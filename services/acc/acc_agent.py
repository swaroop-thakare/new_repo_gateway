"""
ACC Agent (Anti-Compliance Check) Service
Handles compliance checks and anti-fraud validation for payment transactions.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import requests
import boto3
from botocore.exceptions import ClientError

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ACC Agent Service",
    description="Anti-Compliance Check for payment transactions",
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


class ACCRequest(BaseModel):
    """Input for ACC analysis"""
    task_type: str = "acc"
    batch_id: str
    line_id: str
    amount: float
    currency: str = "INR"
    debit_account: str
    credit_account: str
    credit_ifsc: str
    purpose: str
    evidence_ref: Optional[str] = None


class ComplianceCheck(BaseModel):
    """Compliance check result"""
    check_type: str  # KYC, SANCTIONS, LIMITS, IFSC, etc.
    status: str  # PASS, FAIL, WARNING
    score: float = Field(ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)
    evidence_ref: Optional[str] = None


class ACCResult(BaseModel):
    """ACC analysis output"""
    task_type: str = "acc_result"
    batch_id: str
    line_id: str
    decision: str  # PASS, FAIL, HOLD
    policy_version: str
    reasons: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    compliance_penalty: float = Field(default=0.0, ge=0, le=100)
    risk_score: float = Field(default=0.0, ge=0, le=100)
    compliance_checks: List[ComplianceCheck] = Field(default_factory=list)
    timestamp: str


class ACCAgent:
    """Main ACC agent for compliance checking"""
    
    def __init__(self):
        self.s3_client = s3_client
        self.s3_bucket = S3_BUCKET
        self.policy_version = "acc-1.0.0"
    
    async def analyze_compliance(self, request: ACCRequest) -> ACCResult:
        """
        Analyze compliance for a transaction
        """
        start_time = time.time()
        
        try:
            # Run compliance checks
            compliance_checks = await self._run_compliance_checks(request)
            
            # Aggregate results
            decision, reasons, penalty, risk_score = self._aggregate_results(compliance_checks)
            
            # Generate evidence references
            evidence_refs = await self._generate_evidence_refs(request, compliance_checks)
            
            # Create ACC result
            result = ACCResult(
                task_type="acc_result",
                batch_id=request.batch_id,
                line_id=request.line_id,
                decision=decision,
                policy_version=self.policy_version,
                reasons=reasons,
                evidence_refs=evidence_refs,
                compliance_penalty=penalty,
                risk_score=risk_score,
                compliance_checks=compliance_checks,
                timestamp=datetime.now().isoformat()
            )
            
            # Store result in S3
            await self._store_acc_result(request, result)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"ACC analysis completed for {request.batch_id}/{request.line_id} in {processing_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"ACC analysis failed for {request.batch_id}/{request.line_id}: {e}")
            
            return ACCResult(
                task_type="acc_result",
                batch_id=request.batch_id,
                line_id=request.line_id,
                decision="ERROR",
                policy_version=self.policy_version,
                reasons=[f"Analysis error: {str(e)}"],
                evidence_refs=[],
                compliance_penalty=100.0,
                risk_score=100.0,
                timestamp=datetime.now().isoformat()
            )
    
    async def _run_compliance_checks(self, request: ACCRequest) -> List[ComplianceCheck]:
        """Run all compliance checks"""
        checks = []
        
        # KYC verification check
        kyc_check = await self._check_kyc_verification(request)
        checks.append(kyc_check)
        
        # Sanctions check
        sanctions_check = await self._check_sanctions(request)
        checks.append(sanctions_check)
        
        # Transaction limits check
        limits_check = await self._check_transaction_limits(request)
        checks.append(limits_check)
        
        # IFSC validation check
        ifsc_check = await self._check_ifsc_validation(request)
        checks.append(ifsc_check)
        
        # Purpose validation check
        purpose_check = await self._check_purpose_validation(request)
        checks.append(purpose_check)
        
        return checks
    
    async def _check_kyc_verification(self, request: ACCRequest) -> ComplianceCheck:
        """Check KYC verification status"""
        try:
            # Mock implementation - in production, this would check KYC APIs
            kyc_score = 0.9  # High score for verified accounts
            
            return ComplianceCheck(
                check_type="KYC",
                status="PASS" if kyc_score > 0.8 else "FAIL",
                score=kyc_score,
                details={
                    "debit_kyc_verified": True,
                    "credit_kyc_verified": True,
                    "kyc_score": kyc_score
                },
                evidence_ref="s3://bucket/kyc/verification.json"
            )
        except Exception as e:
            logger.error(f"KYC check failed: {e}")
            return ComplianceCheck(
                check_type="KYC",
                status="FAIL",
                score=0.0,
                details={"error": str(e)}
            )
    
    async def _check_sanctions(self, request: ACCRequest) -> ComplianceCheck:
        """Check against sanctions and watchlists"""
        try:
            # Mock implementation - in production, this would check sanctions APIs
            sanctions_score = 0.1  # Low score means no sanctions match
            
            return ComplianceCheck(
                check_type="SANCTIONS",
                status="PASS" if sanctions_score < 0.5 else "FAIL",
                score=1.0 - sanctions_score,  # Invert score (higher is better)
                details={
                    "sanctions_clear": sanctions_score < 0.5,
                    "sanctions_score": sanctions_score,
                    "matched_entities": []
                },
                evidence_ref="s3://bucket/sanctions/check_results.json"
            )
        except Exception as e:
            logger.error(f"Sanctions check failed: {e}")
            return ComplianceCheck(
                check_type="SANCTIONS",
                status="FAIL",
                score=0.0,
                details={"error": str(e)}
            )
    
    async def _check_transaction_limits(self, request: ACCRequest) -> ComplianceCheck:
        """Check transaction against limits"""
        try:
            amount = request.amount
            
            # Mock limits - in production, this would check RBI guidelines
            daily_limit = 1000000  # 10L daily limit
            transaction_limit = 500000  # 5L per transaction
            
            within_daily_limit = amount <= daily_limit
            within_transaction_limit = amount <= transaction_limit
            
            score = 1.0 if within_daily_limit and within_transaction_limit else 0.5
            
            return ComplianceCheck(
                check_type="LIMITS",
                status="PASS" if within_daily_limit and within_transaction_limit else "WARNING",
                score=score,
                details={
                    "daily_limit": daily_limit,
                    "transaction_limit": transaction_limit,
                    "amount": amount,
                    "within_limits": within_daily_limit and within_transaction_limit
                }
            )
        except Exception as e:
            logger.error(f"Limits check failed: {e}")
            return ComplianceCheck(
                check_type="LIMITS",
                status="FAIL",
                score=0.0,
                details={"error": str(e)}
            )
    
    async def _check_ifsc_validation(self, request: ACCRequest) -> ComplianceCheck:
        """Validate IFSC code"""
        try:
            ifsc_code = request.credit_ifsc
            
            # Basic IFSC format validation
            import re
            ifsc_valid = bool(re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code))
            
            # Mock bank validation - in production, this would check bank APIs
            bank_valid = True
            
            score = 1.0 if ifsc_valid and bank_valid else 0.0
            
            return ComplianceCheck(
                check_type="IFSC",
                status="PASS" if ifsc_valid and bank_valid else "FAIL",
                score=score,
                details={
                    "ifsc_code": ifsc_code,
                    "format_valid": ifsc_valid,
                    "bank_valid": bank_valid,
                    "bank_code": ifsc_code[:4] if ifsc_valid else None
                }
            )
        except Exception as e:
            logger.error(f"IFSC check failed: {e}")
            return ComplianceCheck(
                check_type="IFSC",
                status="FAIL",
                score=0.0,
                details={"error": str(e)}
            )
    
    async def _check_purpose_validation(self, request: ACCRequest) -> ComplianceCheck:
        """Validate transaction purpose"""
        try:
            purpose = request.purpose.upper()
            
            # Mock purpose validation - in production, this would check RBI purpose codes
            valid_purposes = ["VENDOR_PAYMENT", "SALARY", "UTILITY", "TAX", "LOAN", "REFUND"]
            purpose_valid = any(valid_purpose in purpose for valid_purpose in valid_purposes)
            
            score = 1.0 if purpose_valid else 0.5
            
            return ComplianceCheck(
                check_type="PURPOSE",
                status="PASS" if purpose_valid else "WARNING",
                score=score,
                details={
                    "purpose": request.purpose,
                    "valid_purpose": purpose_valid,
                    "allowed_purposes": valid_purposes
                }
            )
        except Exception as e:
            logger.error(f"Purpose check failed: {e}")
            return ComplianceCheck(
                check_type="PURPOSE",
                status="FAIL",
                score=0.0,
                details={"error": str(e)}
            )
    
    def _aggregate_results(self, checks: List[ComplianceCheck]) -> Tuple[str, List[str], float, float]:
        """Aggregate compliance check results"""
        reasons = []
        penalty = 0.0
        risk_score = 0.0
        
        # Count check results
        pass_count = sum(1 for check in checks if check.status == "PASS")
        fail_count = sum(1 for check in checks if check.status == "FAIL")
        warning_count = sum(1 for check in checks if check.status == "WARNING")
        
        # Calculate penalty and risk score
        for check in checks:
            if check.status == "FAIL":
                penalty += 20.0
                risk_score += 25.0
                reasons.append(f"{check.check_type} check failed")
            elif check.status == "WARNING":
                penalty += 5.0
                risk_score += 10.0
                reasons.append(f"{check.check_type} check warning")
        
        # Determine decision
        if fail_count > 0:
            decision = "FAIL"
        elif warning_count > 0:
            decision = "HOLD"
        else:
            decision = "PASS"
            reasons.append("All compliance checks passed")
        
        return decision, reasons, penalty, min(100.0, risk_score)
    
    async def _generate_evidence_refs(self, request: ACCRequest, checks: List[ComplianceCheck]) -> List[str]:
        """Generate evidence references"""
        evidence_refs = []
        
        # Add evidence refs from checks
        for check in checks:
            if check.evidence_ref:
                evidence_refs.append(check.evidence_ref)
        
        # Add main evidence ref
        main_evidence_ref = f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/acc.json"
        evidence_refs.append(main_evidence_ref)
        
        return evidence_refs
    
    async def _store_acc_result(self, request: ACCRequest, result: ACCResult):
        """Store ACC result in S3"""
        try:
            result_data = result.dict()
            
            # Extract S3 key from main evidence ref
            s3_key = f"invoices/processed/{request.batch_id}/{request.line_id}/acc.json"
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(result_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Stored ACC result at s3://{self.s3_bucket}/{s3_key}")
            
        except Exception as e:
            logger.error(f"Failed to store ACC result: {e}")


# Initialize agent
acc_agent = ACCAgent()


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ACC Agent",
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

@app.post("/acc/analyze", response_model=ACCResult)
async def analyze_compliance(request: ACCRequest):
    """Analyze compliance for a transaction"""
    return await acc_agent.analyze_compliance(request)

@app.get("/acc/evidence/{batch_id}/{line_id}")
async def get_acc_evidence(batch_id: str, line_id: str):
    """Get ACC evidence for a transaction"""
    try:
        s3_key = f"invoices/processed/{batch_id}/{line_id}/acc.json"
        response = acc_agent.s3_client.get_object(Bucket=acc_agent.s3_bucket, Key=s3_key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="ACC evidence not found")
        raise HTTPException(status_code=500, detail=f"Error fetching evidence: {str(e)}")

@app.get("/acc/compliance-summary")
async def get_compliance_summary(days: int = 30):
    """Get compliance summary for the period"""
    # Mock implementation - in production, this would analyze historical data
    return {
        "period_days": days,
        "total_transactions": 1250,
        "compliant_transactions": 1180,
        "non_compliant_transactions": 45,
        "hold_transactions": 25,
        "compliance_rate": 94.4,
        "common_issues": [
            {"issue": "KYC_NOT_VERIFIED", "count": 20},
            {"issue": "SANCTIONS_MATCH", "count": 15},
            {"issue": "LIMIT_EXCEEDED", "count": 10}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
