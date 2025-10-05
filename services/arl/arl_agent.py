"""
ARL Agent (Account Reconciliation Ledger) Service
Reconciles ledger entries with transaction outcomes to ensure financial accuracy and audit readiness.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ARL Agent Service",
    description="Account Reconciliation Ledger for financial accuracy",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 client
s3_client = boto3.client('s3')
S3_BUCKET = os.getenv('S3_BUCKET', 'arealis-gateway-data')

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/arealis_gateway')


class ARLRequest(BaseModel):
    """Input for ARL reconciliation"""
    task_type: str = "arl"
    batch_id: str
    line_id: str
    status: str  # COMPLETED, FAILED, HOLD
    amount: float
    evidence_ref: str


class LedgerEntry(BaseModel):
    """Ledger entry structure"""
    entry_id: str
    account_number: str
    transaction_type: str  # DEBIT, CREDIT
    amount: Decimal
    currency: str
    reference: str
    timestamp: datetime
    status: str  # PENDING, POSTED, RECONCILED


class Discrepancy(BaseModel):
    """Discrepancy found during reconciliation"""
    type: str  # AMOUNT_MISMATCH, TIMESTAMP_MISMATCH, MISSING_ENTRY, DUPLICATE_ENTRY
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    recommendation: str


class ReconciliationResult(BaseModel):
    """Reconciliation result"""
    status: str  # RECONCILED, PARTIAL, FAILED
    total_entries: int
    matched_entries: int
    discrepancies: List[Discrepancy] = Field(default_factory=list)
    reconciliation_score: float = Field(ge=0.0, le=100.0)
    last_reconciled_at: Optional[datetime] = None


class ARLResult(BaseModel):
    """ARL reconciliation output"""
    task_type: str = "arl_result"
    batch_id: str
    line_id: str
    status: str  # RECONCILED, PARTIAL, FAILED
    discrepancies: List[Discrepancy] = Field(default_factory=list)
    evidence_ref: str
    timestamp: str
    reconciliation_details: Dict[str, Any] = Field(default_factory=dict)


class ARLAgent:
    """Main ARL agent for ledger reconciliation"""
    
    def __init__(self):
        self.s3_client = s3_client
        self.s3_bucket = S3_BUCKET
    
    async def reconcile_transaction(self, request: ARLRequest) -> ARLResult:
        """
        Reconcile ledger entries for a transaction
        """
        start_time = time.time()
        
        try:
            # Fetch transaction data
            transaction_data = await self._fetch_transaction_data(request)
            
            # Fetch ledger entries
            ledger_entries = await self._fetch_ledger_entries(request)
            
            # Perform reconciliation
            reconciliation_result = await self._perform_reconciliation(
                request, transaction_data, ledger_entries
            )
            
            # Update ledger if reconciliation is successful
            if reconciliation_result.status == "RECONCILED":
                await self._update_ledger_status(ledger_entries, "RECONCILED")
            
            # Generate evidence reference
            evidence_ref = f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/arl.json"
            
            # Store ARL result
            await self._store_arl_result(request, reconciliation_result, evidence_ref)
            
            processing_time = (time.time() - start_time) * 1000
            
            return ARLResult(
                task_type="arl_result",
                batch_id=request.batch_id,
                line_id=request.line_id,
                status=reconciliation_result.status,
                discrepancies=reconciliation_result.discrepancies,
                evidence_ref=evidence_ref,
                timestamp=datetime.now().isoformat(),
                reconciliation_details={
                    "processing_time_ms": processing_time,
                    "total_entries": reconciliation_result.total_entries,
                    "matched_entries": reconciliation_result.matched_entries,
                    "reconciliation_score": reconciliation_result.reconciliation_score
                }
            )
            
        except Exception as e:
            logger.error(f"ARL reconciliation failed for {request.batch_id}/{request.line_id}: {e}")
            
            return ARLResult(
                task_type="arl_result",
                batch_id=request.batch_id,
                line_id=request.line_id,
                status="FAILED",
                evidence_ref=f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/arl.json",
                timestamp=datetime.now().isoformat(),
                reconciliation_details={"error": str(e)}
            )
    
    async def _fetch_transaction_data(self, request: ARLRequest) -> Dict[str, Any]:
        """Fetch transaction data for reconciliation"""
        transaction_data = {}
        
        try:
            # Fetch PDR result
            pdr_key = f"invoices/processed/{request.batch_id}/{request.line_id}/pdr.json"
            try:
                pdr_response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=pdr_key)
                transaction_data['pdr_result'] = json.loads(pdr_response['Body'].read().decode('utf-8'))
            except ClientError:
                logger.warning("PDR result not found")
            
            # Fetch invoice data
            transaction_data['invoice_data'] = await self._fetch_invoice_data(request.batch_id, request.line_id)
            
            # Fetch bank transaction data if available
            transaction_data['bank_transaction'] = await self._fetch_bank_transaction_data(request)
            
        except Exception as e:
            logger.error(f"Error fetching transaction data: {e}")
        
        return transaction_data
    
    async def _fetch_ledger_entries(self, request: ARLRequest) -> List[LedgerEntry]:
        """Fetch ledger entries for the transaction"""
        ledger_entries = []
        
        try:
            # Mock implementation - in production, this would query the ledger database
            # Create debit entry
            debit_entry = LedgerEntry(
                entry_id=f"DEBIT_{request.batch_id}_{request.line_id}",
                account_number="91402004****3081",
                transaction_type="DEBIT",
                amount=Decimal(str(request.amount)),
                currency="INR",
                reference=f"{request.batch_id}_{request.line_id}",
                timestamp=datetime.now(),
                status="PENDING"
            )
            ledger_entries.append(debit_entry)
            
            # Create credit entry
            credit_entry = LedgerEntry(
                entry_id=f"CREDIT_{request.batch_id}_{request.line_id}",
                account_number="0052050****597",
                transaction_type="CREDIT",
                amount=Decimal(str(request.amount)),
                currency="INR",
                reference=f"{request.batch_id}_{request.line_id}",
                timestamp=datetime.now(),
                status="PENDING"
            )
            ledger_entries.append(credit_entry)
            
        except Exception as e:
            logger.error(f"Error fetching ledger entries: {e}")
        
        return ledger_entries
    
    async def _perform_reconciliation(
        self, 
        request: ARLRequest, 
        transaction_data: Dict[str, Any], 
        ledger_entries: List[LedgerEntry]
    ) -> ReconciliationResult:
        """Perform the actual reconciliation"""
        
        discrepancies = []
        matched_entries = 0
        total_entries = len(ledger_entries)
        
        # Check amount reconciliation
        expected_amount = Decimal(str(request.amount))
        for entry in ledger_entries:
            if abs(entry.amount - expected_amount) > Decimal('0.01'):  # Allow for small rounding differences
                discrepancies.append(Discrepancy(
                    type="AMOUNT_MISMATCH",
                    description=f"Amount mismatch for entry {entry.entry_id}",
                    severity="HIGH",
                    expected_value=str(expected_amount),
                    actual_value=str(entry.amount),
                    recommendation="Verify transaction amount and ledger entry"
                ))
            else:
                matched_entries += 1
        
        # Check for missing entries
        expected_debit_count = 1
        expected_credit_count = 1
        actual_debit_count = sum(1 for entry in ledger_entries if entry.transaction_type == "DEBIT")
        actual_credit_count = sum(1 for entry in ledger_entries if entry.transaction_type == "CREDIT")
        
        if actual_debit_count != expected_debit_count:
            discrepancies.append(Discrepancy(
                type="MISSING_ENTRY",
                description=f"Missing debit entries. Expected: {expected_debit_count}, Found: {actual_debit_count}",
                severity="CRITICAL",
                recommendation="Create missing debit entry"
            ))
        
        if actual_credit_count != expected_credit_count:
            discrepancies.append(Discrepancy(
                type="MISSING_ENTRY",
                description=f"Missing credit entries. Expected: {expected_credit_count}, Found: {actual_credit_count}",
                severity="CRITICAL",
                recommendation="Create missing credit entry"
            ))
        
        # Check timestamp reconciliation (allow 5 minute tolerance)
        if transaction_data.get('pdr_result'):
            pdr_timestamp = datetime.fromisoformat(
                transaction_data['pdr_result'].get('timestamp', datetime.now().isoformat())
            )
            for entry in ledger_entries:
                time_diff = abs((entry.timestamp - pdr_timestamp).total_seconds())
                if time_diff > 300:  # 5 minutes
                    discrepancies.append(Discrepancy(
                        type="TIMESTAMP_MISMATCH",
                        description=f"Timestamp mismatch for entry {entry.entry_id}",
                        severity="MEDIUM",
                        expected_value=pdr_timestamp.isoformat(),
                        actual_value=entry.timestamp.isoformat(),
                        recommendation="Verify transaction timestamp"
                    ))
        
        # Calculate reconciliation score
        if total_entries == 0:
            reconciliation_score = 0.0
        else:
            reconciliation_score = (matched_entries / total_entries) * 100.0
        
        # Determine reconciliation status
        if len(discrepancies) == 0:
            status = "RECONCILED"
        elif len([d for d in discrepancies if d.severity in ["CRITICAL", "HIGH"]]) == 0:
            status = "PARTIAL"
        else:
            status = "FAILED"
        
        return ReconciliationResult(
            status=status,
            total_entries=total_entries,
            matched_entries=matched_entries,
            discrepancies=discrepancies,
            reconciliation_score=reconciliation_score,
            last_reconciled_at=datetime.now() if status == "RECONCILED" else None
        )
    
    async def _update_ledger_status(self, ledger_entries: List[LedgerEntry], status: str):
        """Update ledger entry status"""
        try:
            # Mock implementation - in production, this would update the ledger database
            for entry in ledger_entries:
                entry.status = status
                logger.info(f"Updated ledger entry {entry.entry_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating ledger status: {e}")
    
    async def _fetch_invoice_data(self, batch_id: str, line_id: str) -> Dict[str, Any]:
        """Fetch invoice data from database"""
        # Mock implementation - in production, this would query PostgreSQL
        return {
            "batch_id": batch_id,
            "line_id": line_id,
            "amount": 250000,
            "currency": "INR",
            "debit_account": "91402004****3081",
            "credit_account": "0052050****597",
            "created_at": datetime.now().isoformat()
        }
    
    async def _fetch_bank_transaction_data(self, request: ARLRequest) -> Optional[Dict[str, Any]]:
        """Fetch bank transaction data"""
        # Mock implementation - in production, this would query bank APIs or database
        return {
            "utr_number": f"UTR{request.batch_id}{request.line_id}",
            "bank_reference": f"BANK_REF_{request.batch_id}_{request.line_id}",
            "transaction_status": "SUCCESS",
            "processed_at": datetime.now().isoformat()
        }
    
    async def _store_arl_result(self, request: ARLRequest, reconciliation_result: ReconciliationResult, evidence_ref: str):
        """Store ARL result in S3"""
        try:
            result_data = {
                "task_type": "arl_result",
                "batch_id": request.batch_id,
                "line_id": request.line_id,
                "status": reconciliation_result.status,
                "discrepancies": [d.dict() for d in reconciliation_result.discrepancies],
                "evidence_ref": evidence_ref,
                "timestamp": datetime.now().isoformat(),
                "reconciliation_details": {
                    "total_entries": reconciliation_result.total_entries,
                    "matched_entries": reconciliation_result.matched_entries,
                    "reconciliation_score": reconciliation_result.reconciliation_score
                }
            }
            
            # Extract S3 key from evidence_ref
            s3_key = evidence_ref.replace(f"s3://{self.s3_bucket}/", "")
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(result_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Stored ARL result at {evidence_ref}")
            
        except Exception as e:
            logger.error(f"Failed to store ARL result: {e}")


# Initialize agent
arl_agent = ARLAgent()


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ARL Agent",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/arl/reconcile", response_model=ARLResult)
async def reconcile_transaction(request: ARLRequest):
    """Reconcile ledger entries for a transaction"""
    return await arl_agent.reconcile_transaction(request)

@app.get("/arl/evidence/{batch_id}/{line_id}")
async def get_arl_evidence(batch_id: str, line_id: str):
    """Get ARL evidence for a transaction"""
    try:
        s3_key = f"invoices/processed/{batch_id}/{line_id}/arl.json"
        response = arl_agent.s3_client.get_object(Bucket=arl_agent.s3_bucket, Key=s3_key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="ARL evidence not found")
        raise HTTPException(status_code=500, detail=f"Error fetching evidence: {str(e)}")

@app.get("/arl/ledger-entries/{batch_id}/{line_id}")
async def get_ledger_entries(batch_id: str, line_id: str):
    """Get ledger entries for a transaction"""
    # Mock implementation - in production, this would query the ledger database
    return {
        "batch_id": batch_id,
        "line_id": line_id,
        "entries": [
            {
                "entry_id": f"DEBIT_{batch_id}_{line_id}",
                "account_number": "91402004****3081",
                "transaction_type": "DEBIT",
                "amount": "250000.00",
                "currency": "INR",
                "status": "RECONCILED"
            },
            {
                "entry_id": f"CREDIT_{batch_id}_{line_id}",
                "account_number": "0052050****597",
                "transaction_type": "CREDIT",
                "amount": "250000.00",
                "currency": "INR",
                "status": "RECONCILED"
            }
        ]
    }

@app.get("/arl/reconciliation-summary")
async def get_reconciliation_summary(days: int = 30):
    """Get reconciliation summary for the period"""
    # Mock implementation - in production, this would analyze historical data
    return {
        "period_days": days,
        "total_transactions": 1250,
        "reconciled_transactions": 1200,
        "partial_transactions": 35,
        "failed_transactions": 15,
        "reconciliation_rate": 96.0,
        "common_discrepancies": [
            {"type": "AMOUNT_MISMATCH", "count": 20},
            {"type": "TIMESTAMP_MISMATCH", "count": 10},
            {"type": "MISSING_ENTRY", "count": 5}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
