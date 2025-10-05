"""
Frontend Integration for Arealis Gateway v2

This module provides API endpoints to integrate the Next.js frontend
with the Python backend services.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Arealis Gateway v2 Frontend Integration",
    description="API endpoints for frontend-backend integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend service URLs
BACKEND_SERVICES = {
    "mcp": "http://localhost:8000",
    "frontend_ingestor": "http://localhost:8001",
    "invoice_validator": "http://localhost:8002",
    "intent_classifier": "http://localhost:8003",
    "pdr": "http://localhost:8006",
    "arl": "http://localhost:8008",
    "rca": "http://localhost:8009",
    "crrak": "http://localhost:8010"
}

# Pydantic models for API
class TransactionData(BaseModel):
    """Transaction data model."""
    transactionId: str
    date: str
    beneficiary: str
    amount: float
    currency: str = "INR"
    purpose: str
    transactionType: str = "NEFT"
    creditScore: Optional[int] = None
    reference: Optional[str] = None

class BatchData(BaseModel):
    """Batch data model."""
    batch_id: str
    tenant_id: str
    source: str
    upload_ts: str
    transactions: List[TransactionData]

class WorkflowStatus(BaseModel):
    """Workflow status model."""
    workflow_id: str
    batch_id: str
    status: str
    current_layer: Optional[str]
    current_agent: Optional[str]
    start_time: str
    last_update: str
    errors: List[str] = []

class DashboardMetrics(BaseModel):
    """Dashboard metrics model."""
    total_disbursed: float
    loans_processed: int
    success_rate: float
    batches_awaiting: int

class FrontendIntegration:
    """Frontend integration service."""
    
    def __init__(self):
        """Initialize integration service."""
        self.active_workflows = {}
        self.transaction_cache = {}
        self.transactions = []  # Store actual transactions
        self._initialize_default_transactions()
    
    def _initialize_default_transactions(self):
        """Initialize with default transaction data."""
        self.transactions = [
            {
                "id": "12345678",
                "date": "2025-09-29",
                "beneficiary": "Rajesh Kumar",
                "amount": 45000,
                "currency": "INR",
                "status": "completed",
                "stage": "reconciled",
                "product": "Personal Loan",
                "creditScore": 720,
                "reference": "UTR2025092912345",
                "workflow_id": "WF-B-2025-09-29-01-abc12345"
            },
            {
                "id": "12345679",
                "date": "2025-09-29",
                "beneficiary": "Priya Sharma",
                "amount": 32500,
                "currency": "INR",
                "status": "pending",
                "stage": "operator-review",
                "product": "Business Loan",
                "creditScore": 680,
                "reference": "UTR2025092912346",
                "workflow_id": "WF-B-2025-09-29-02-def67890"
            },
            {
                "id": "12345680",
                "date": "2025-09-29",
                "beneficiary": "Amit Patel",
                "amount": 75000,
                "currency": "INR",
                "status": "completed",
                "stage": "executed",
                "product": "Home Loan",
                "creditScore": 800,
                "reference": "UTR2025092912347",
                "workflow_id": "WF-B-2025-09-29-03-ghi11111"
            },
            {
                "id": "12345681",
                "date": "2025-09-29",
                "beneficiary": "Sneha Gupta",
                "amount": 25000,
                "currency": "INR",
                "status": "failed",
                "stage": "compliance",
                "product": "Personal Loan",
                "creditScore": 650,
                "reference": "UTR2025092912348",
                "workflow_id": "WF-B-2025-09-29-04-jkl22222"
            }
        ]
    
    async def _process_csv_transactions(self, batch_data: BatchData, workflow_id: str):
        """Process transactions and add to transaction store."""
        try:
            new_transactions = []
            for i, tx in enumerate(batch_data.transactions):
                # Get transaction data from TransactionData object
                transaction_type = tx.transactionType if hasattr(tx, 'transactionType') else 'NEFT'
                amount = float(tx.amount)
                
                # Map transaction status based on type and amount
                if transaction_type == 'IMPS':
                    status = "completed"
                    stage = "executed"
                elif transaction_type == 'RTGS':
                    status = "completed" if amount > 1000000 else "pending"
                    stage = "reconciled" if amount > 1000000 else "operator-review"
                elif transaction_type == 'NEFT':
                    status = "completed" if amount < 500000 else "pending"
                    stage = "executed" if amount < 500000 else "operator-review"
                else:  # IFT or other
                    status = "completed"
                    stage = "executed"
                
                # Create transaction with proper format for dashboard
                transaction = {
                    "id": tx.transactionId if hasattr(tx, 'transactionId') else f"TXN-{batch_data.batch_id}-{i+1:03d}",
                    "date": tx.date if hasattr(tx, 'date') else datetime.now().strftime("%Y-%m-%d"),
                    "beneficiary": tx.beneficiary,
                    "amount": amount,
                    "currency": tx.currency if hasattr(tx, 'currency') else 'INR',
                    "status": status,
                    "stage": stage,
                    "product": "Payment",
                    "creditScore": tx.creditScore if hasattr(tx, 'creditScore') else 750,
                    "reference": tx.reference if hasattr(tx, 'reference') else f"REF-{batch_data.batch_id}-{i+1:03d}",
                    "workflow_id": workflow_id
                }
                new_transactions.append(transaction)
                logger.info(f"Processed transaction: {transaction['beneficiary']} - {transaction['amount']}")
            
            # Add new transactions to the store
            self.transactions.extend(new_transactions)
            logger.info(f"Added {len(new_transactions)} new transactions from batch {batch_data.batch_id}")
            
        except Exception as e:
            logger.error(f"Failed to process transactions: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
    async def upload_batch(self, batch_data: BatchData) -> Dict[str, Any]:
        """Upload a new batch for processing."""
        try:
            # Generate workflow ID
            workflow_id = f"WF-{batch_data.batch_id}-{uuid.uuid4().hex[:8]}"
            
            # Prepare data for MCP
            mcp_data = {
                "batch_id": batch_data.batch_id,
                "tenant_id": batch_data.tenant_id,
                "source": batch_data.source,
                "upload_ts": batch_data.upload_ts,
                "raw_file_key": f"s3://arealis-invoices/raw/{batch_data.tenant_id}/{batch_data.batch_id}/batch.json",
                "data": {
                    "transactions": [tx.dict() for tx in batch_data.transactions]
                }
            }
            
            # Start workflow via MCP with correct format
            mcp_request = {
                "workflow_id": workflow_id,
                "event_type": "batch_upload",
                "data": mcp_data
            }
            
            response = requests.post(
                f"{BACKEND_SERVICES['mcp']}/api/v1/workflows/start",
                json=mcp_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result.get("workflow_id", workflow_id)
                
                # Store workflow info
                self.active_workflows[workflow_id] = {
                    "batch_id": batch_data.batch_id,
                    "tenant_id": batch_data.tenant_id,
                    "start_time": datetime.now().isoformat(),
                    "status": "STARTED"
                }
                
                logger.info(f"Started workflow {workflow_id} for batch {batch_data.batch_id}")
                
                # Process CSV transactions and add to transaction store
                logger.info(f"Processing {len(batch_data.transactions)} transactions from batch {batch_data.batch_id}")
                await self._process_csv_transactions(batch_data, workflow_id)
                logger.info(f"Transaction store now has {len(self.transactions)} transactions")
                
                return {
                    "workflow_id": workflow_id,
                    "batch_id": batch_data.batch_id,
                    "status": "STARTED",
                    "message": f"Batch {batch_data.batch_id} processing started"
                }
            else:
                raise HTTPException(status_code=500, detail=f"MCP error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to upload batch: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_workflow_status(self, workflow_id: str) -> WorkflowStatus:
        """Get workflow status."""
        try:
            response = requests.get(
                f"{BACKEND_SERVICES['mcp']}/api/v1/workflows/{workflow_id}/status",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return WorkflowStatus(**data)
            else:
                raise HTTPException(status_code=404, detail="Workflow not found")
                
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics."""
        try:
            # Mock metrics for now - in production, this would query the database
            metrics = {
                "total_disbursed": 8250400.0,
                "loans_processed": 210,
                "success_rate": 98.0,
                "batches_awaiting": 3
            }
            
            return DashboardMetrics(**metrics)
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_transactions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get transaction list."""
        try:
            # Return transactions from the store
            return self.transactions[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to get transactions: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """Get detailed transaction information."""
        try:
            # Mock detailed transaction data
            details = {
                "id": transaction_id,
                "date": "2025-09-29",
                "beneficiary": "Rajesh Kumar",
                "amount": 45000,
                "currency": "INR",
                "status": "completed",
                "stage": "reconciled",
                "product": "Personal Loan",
                "creditScore": 720,
                "reference": "UTR2025092912345",
                "workflow_id": "WF-B-2025-09-29-01-abc12345",
                "processing_steps": [
                    {
                        "step": "File Upload",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:00:00Z",
                        "agent": "FrontendIngestor"
                    },
                    {
                        "step": "Data Validation",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:01:00Z",
                        "agent": "InvoiceValidator"
                    },
                    {
                        "step": "Intent Classification",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:02:00Z",
                        "agent": "IntentClassifier"
                    },
                    {
                        "step": "Payment Routing",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:03:00Z",
                        "agent": "PDR"
                    },
                    {
                        "step": "Transaction Execution",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:04:00Z",
                        "agent": "Execution"
                    },
                    {
                        "step": "Account Reconciliation",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:05:00Z",
                        "agent": "ARL"
                    },
                    {
                        "step": "Compliance Report",
                        "status": "completed",
                        "timestamp": "2025-09-29T10:06:00Z",
                        "agent": "CRRAK"
                    }
                ],
                "audit_trail": [
                    {
                        "action": "Transaction Created",
                        "timestamp": "2025-09-29T10:00:00Z",
                        "actor": "System"
                    },
                    {
                        "action": "Validation Passed",
                        "timestamp": "2025-09-29T10:01:00Z",
                        "actor": "InvoiceValidator"
                    },
                    {
                        "action": "Intent Classified as PERSONAL_LOAN",
                        "timestamp": "2025-09-29T10:02:00Z",
                        "actor": "IntentClassifier"
                    },
                    {
                        "action": "Route Selected: NEFT",
                        "timestamp": "2025-09-29T10:03:00Z",
                        "actor": "PDR"
                    },
                    {
                        "action": "Transaction Executed Successfully",
                        "timestamp": "2025-09-29T10:04:00Z",
                        "actor": "Execution"
                    },
                    {
                        "action": "Account Reconciled",
                        "timestamp": "2025-09-29T10:05:00Z",
                        "actor": "ARL"
                    },
                    {
                        "action": "Compliance Report Generated",
                        "timestamp": "2025-09-29T10:06:00Z",
                        "actor": "CRRAK"
                    }
                ]
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Failed to get transaction details: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        try:
            response = requests.get(
                f"{BACKEND_SERVICES['mcp']}/api/v1/agents",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=500, detail="Failed to get agent status")
                
        except Exception as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize integration service
integration = FrontendIntegration()

# API Endpoints
@app.post("/api/v1/batches/upload")
async def upload_batch_file(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    batch_id: str = Form(None)
):
    """Upload a CSV file for batch processing."""
    try:
        # Read and parse CSV file
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV data
        lines = csv_content.strip().split('\n')
        headers = lines[0].split(',')
        transactions = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split(',')
                if len(values) >= len(headers):
                    tx_dict = dict(zip(headers, values))
                    try:
                        # Map CSV fields to TransactionData model
                        tx_data = TransactionData(
                            transactionId=f"TXN-{batch_id}-{len(transactions)+1:03d}",
                            date=datetime.now().strftime("%Y-%m-%d"),
                            beneficiary=tx_dict.get('beneficiary', 'Unknown'),
                            amount=float(tx_dict.get('amount', 0)),
                            currency="INR",
                            purpose=tx_dict.get('purpose', 'P0101'),
                            transactionType="NEFT",
                            creditScore=750,
                            reference=tx_dict.get('reference', f"REF-{len(transactions)+1:03d}")
                        )
                        transactions.append(tx_data)
                        logger.info(f"Successfully parsed transaction: {tx_data.beneficiary}")
                    except Exception as e:
                        logger.error(f"Failed to parse transaction: {e}, data: {tx_dict}")
                        # Create a simple transaction object for debugging
                        simple_tx = {
                            "transactionId": f"TXN-{batch_id}-{len(transactions)+1:03d}",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "beneficiary": tx_dict.get('beneficiary', 'Unknown'),
                            "amount": float(tx_dict.get('amount', 0)),
                            "currency": "INR",
                            "purpose": tx_dict.get('purpose', 'P0101'),
                            "transactionType": "NEFT",
                            "creditScore": 750,
                            "reference": tx_dict.get('reference', f"REF-{len(transactions)+1:03d}")
                        }
                        transactions.append(simple_tx)
                        logger.info(f"Added simple transaction: {simple_tx['beneficiary']}")
        
        # Generate batch ID if not provided
        if not batch_id:
            batch_id = f"B-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        
        # Create batch data
        batch_data = BatchData(
            batch_id=batch_id,
            tenant_id=tenant_id,
            source="frontend",
            upload_ts=datetime.now().isoformat(),
            transactions=transactions
        )
        
        # Process the batch
        result = await integration.upload_batch(batch_data)
        
        return JSONResponse(content={
            "message": "Batch upload received and workflow initiated",
            "batch_id": batch_id,
            "ingestion_result": {
                "batch_id": batch_id,
                "tenant_id": tenant_id,
                "file_name": file.filename,
                "file_size": len(content),
                "status": "success",
                "records_processed": len(transactions),
                "timestamp": datetime.now().isoformat()
            }
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"Batch upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/batches/upload-json")
async def upload_json_batch(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    batch_id: str = Form(None)
):
    """Upload a JSON file with transaction data."""
    try:
        # Read and parse JSON file
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))
        
        # Extract transactions from JSON
        transactions = []
        json_transactions = json_data.get('transactions', [])
        
        for i, tx in enumerate(json_transactions):
            # Map JSON transaction to our TransactionData model
            tx_data = TransactionData(
                transactionId=tx.get('transactionId', f"TXN-{batch_id}-{i+1:03d}"),
                date=tx.get('timestamp', datetime.now().isoformat())[:10],  # Extract date from timestamp
                beneficiary=tx.get('beneficiary', {}).get('accountHolderName', 'Unknown'),
                amount=float(tx.get('amount', 0)),
                currency=tx.get('currency', 'INR'),
                purpose=tx.get('additionalDetails', {}).get('remarks', 'P0101'),
                transactionType=tx.get('transactionType', 'NEFT'),
                creditScore=750,  # Default credit score
                reference=tx.get('response', {}).get('utrNumber', f"REF-{i+1:03d}")
            )
            transactions.append(tx_data)
        
        # Generate batch ID if not provided
        if not batch_id:
            batch_id = f"B-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        
        # Create batch data
        batch_data = BatchData(
            batch_id=batch_id,
            tenant_id=tenant_id,
            source="frontend",
            upload_ts=datetime.now().isoformat(),
            transactions=transactions
        )
        
        # Process the batch
        result = await integration.upload_batch(batch_data)
        
        return JSONResponse(content={
            "message": "JSON batch upload received and workflow initiated",
            "batch_id": batch_id,
            "ingestion_result": {
                "batch_id": batch_id,
                "tenant_id": tenant_id,
                "file_name": file.filename,
                "file_size": len(content),
                "status": "success",
                "records_processed": len(transactions),
                "metadata": json_data.get('metadata', {}),
                "timestamp": datetime.now().isoformat()
            }
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"JSON batch upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/batches/upload-data")
async def upload_batch_data(batch_data: BatchData):
    """Upload batch data directly."""
    try:
        result = await integration.upload_batch(batch_data)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        logger.error(f"Batch upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get workflow status."""
    try:
        status = await integration.get_workflow_status(workflow_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """Get dashboard metrics."""
    try:
        metrics = await integration.get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/transactions")
async def get_transactions(limit: int = 50, offset: int = 0):
    """Get transaction list."""
    try:
        transactions = await integration.get_transactions(limit, offset)
        return JSONResponse(content=transactions, status_code=200)
    except Exception as e:
        logger.error(f"Failed to get transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction_details(transaction_id: str):
    """Get detailed transaction information."""
    try:
        details = await integration.get_transaction_details(transaction_id)
        return JSONResponse(content=details, status_code=200)
    except Exception as e:
        logger.error(f"Failed to get transaction details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents")
async def get_agent_status():
    """Get status of all agents."""
    try:
        agents = await integration.get_agent_status()
        return JSONResponse(content=agents, status_code=200)
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/transactions/add")
async def add_transactions(transactions: List[Dict[str, Any]]):
    """Add transactions directly to the store."""
    try:
        # Add transactions to the store
        integration.transactions.extend(transactions)
        logger.info(f"Added {len(transactions)} transactions to store")
        
        return JSONResponse(content={
            "message": f"Added {len(transactions)} transactions",
            "total_transactions": len(integration.transactions)
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"Failed to add transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/transactions/add-simple")
async def add_simple_transactions():
    """Add simple test transactions to the store."""
    try:
        # Add simple test transactions
        test_transactions = [
            {
                "id": "TXN-TEST-001",
                "date": "2025-10-04",
                "beneficiary": "Test User 1",
                "amount": 15000,
                "currency": "INR",
                "status": "completed",
                "stage": "executed",
                "product": "Payment",
                "creditScore": 750,
                "reference": "REF-TEST-001",
                "workflow_id": "WF-TEST-001"
            },
            {
                "id": "TXN-TEST-002",
                "date": "2025-10-04",
                "beneficiary": "Test User 2",
                "amount": 25000,
                "currency": "INR",
                "status": "pending",
                "stage": "operator-review",
                "product": "Payment",
                "creditScore": 750,
                "reference": "REF-TEST-002",
                "workflow_id": "WF-TEST-001"
            }
        ]
        
        integration.transactions.extend(test_transactions)
        logger.info(f"Added {len(test_transactions)} test transactions to store")
        
        return JSONResponse(content={
            "message": f"Added {len(test_transactions)} test transactions",
            "total_transactions": len(integration.transactions)
        }, status_code=200)
        
    except Exception as e:
        logger.error(f"Failed to add test transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "frontend_integration",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
