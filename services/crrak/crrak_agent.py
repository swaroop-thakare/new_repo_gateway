"""
CRRAK Agent (Compliance Report & Risk Assessment Kit) Service
Generates compliance reports and risk assessments for RBI compliance and audit readiness.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import boto3
from botocore.exceptions import ClientError
import requests

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CRRAK Agent Service",
    description="Compliance Report & Risk Assessment Kit",
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


class CRRAKRequest(BaseModel):
    """Input for CRRAK generation"""
    task_type: str = "crrak"
    batch_id: str
    line_id: str
    status: str  # COMPLETED, FAILED, HOLD
    evidence_ref: str


class ComplianceStatus(BaseModel):
    """Compliance status details"""
    status: str  # COMPLIANT, NON_COMPLIANT, PENDING
    sanctions_check: bool
    aml_check: bool
    kyc_verified: bool
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_score: float = Field(ge=0.0, le=100.0)


class RiskAssessment(BaseModel):
    """Risk assessment details"""
    overall_risk_score: float = Field(ge=0.0, le=100.0)
    transaction_risk: float = Field(ge=0.0, le=100.0)
    counterparty_risk: float = Field(ge=0.0, le=100.0)
    operational_risk: float = Field(ge=0.0, le=100.0)
    risk_factors: List[str] = Field(default_factory=list)


class CRRAKReport(BaseModel):
    """CRRAK report structure"""
    compliance_status: ComplianceStatus
    risk_assessment: RiskAssessment
    transaction_details: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]
    recommendations: List[str] = Field(default_factory=list)


class CRRAKResult(BaseModel):
    """CRRAK generation output"""
    task_type: str = "crrak_generated"
    batch_id: str
    line_id: str
    status: str = "SUCCESS"
    report: Optional[CRRAKReport] = None
    report_ref: str
    timestamp: str
    generation_details: Dict[str, Any] = Field(default_factory=dict)


class CRRAKAgent:
    """Main CRRAK agent for compliance reporting and risk assessment"""
    
    def __init__(self):
        self.s3_client = s3_client
        self.s3_bucket = S3_BUCKET
    
    async def generate_crrak(self, request: CRRAKRequest) -> CRRAKResult:
        """
        Generate CRRAK report for a transaction
        """
        start_time = time.time()
        
        try:
            # Fetch transaction data
            transaction_data = await self._fetch_transaction_data(request)
            
            # Generate compliance status
            compliance_status = await self._assess_compliance(transaction_data)
            
            # Generate risk assessment
            risk_assessment = await self._assess_risk(transaction_data)
            
            # Build audit trail
            audit_trail = await self._build_audit_trail(request, transaction_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(compliance_status, risk_assessment)
            
            # Create CRRAK report
            crrak_report = CRRAKReport(
                compliance_status=compliance_status,
                risk_assessment=risk_assessment,
                transaction_details=transaction_data,
                audit_trail=audit_trail,
                recommendations=recommendations
            )
            
            # Generate report reference
            report_ref = f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/crrak.pdf"
            
            # Store CRRAK report
            await self._store_crrak_report(request, crrak_report, report_ref)
            
            processing_time = (time.time() - start_time) * 1000
            
            return CRRAKResult(
                task_type="crrak_generated",
                batch_id=request.batch_id,
                line_id=request.line_id,
                status="SUCCESS",
                report=crrak_report,
                report_ref=report_ref,
                timestamp=datetime.now().isoformat(),
                generation_details={
                    "processing_time_ms": processing_time,
                    "compliance_score": compliance_status.compliance_score,
                    "risk_score": risk_assessment.overall_risk_score
                }
            )
            
        except Exception as e:
            logger.error(f"CRRAK generation failed for {request.batch_id}/{request.line_id}: {e}")
            
            return CRRAKResult(
                task_type="crrak_generated",
                batch_id=request.batch_id,
                line_id=request.line_id,
                status="FAILED",
                report_ref=f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/crrak.pdf",
                timestamp=datetime.now().isoformat(),
                generation_details={"error": str(e)}
            )
    
    async def _fetch_transaction_data(self, request: CRRAKRequest) -> Dict[str, Any]:
        """Fetch all relevant transaction data"""
        transaction_data = {}
        
        try:
            # Fetch PDR result
            pdr_key = f"invoices/processed/{request.batch_id}/{request.line_id}/pdr.json"
            try:
                pdr_response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=pdr_key)
                transaction_data['pdr_result'] = json.loads(pdr_response['Body'].read().decode('utf-8'))
            except ClientError:
                logger.warning("PDR result not found")
            
            # Fetch ACC decision
            acc_key = f"invoices/processed/{request.batch_id}/{request.line_id}/acc.json"
            try:
                acc_response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=acc_key)
                transaction_data['acc_decision'] = json.loads(acc_response['Body'].read().decode('utf-8'))
            except ClientError:
                logger.warning("ACC decision not found")
            
            # Fetch RCA result if available
            rca_key = f"invoices/processed/{request.batch_id}/{request.line_id}/rca.json"
            try:
                rca_response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=rca_key)
                transaction_data['rca_result'] = json.loads(rca_response['Body'].read().decode('utf-8'))
            except ClientError:
                logger.warning("RCA result not found")
            
            # Fetch invoice data from database
            transaction_data['invoice_data'] = await self._fetch_invoice_data(request.batch_id, request.line_id)
            
            # Fetch counterparty data
            transaction_data['counterparty_data'] = await self._fetch_counterparty_data(transaction_data)
            
        except Exception as e:
            logger.error(f"Error fetching transaction data: {e}")
        
        return transaction_data
    
    async def _assess_compliance(self, transaction_data: Dict[str, Any]) -> ComplianceStatus:
        """Assess compliance status"""
        
        # Initialize compliance checks
        sanctions_check = True
        aml_check = True
        kyc_verified = True
        compliance_score = 100.0
        risk_level = "LOW"
        
        # Check ACC decision
        if 'acc_decision' in transaction_data:
            acc_data = transaction_data['acc_decision']
            if acc_data.get('decision') == 'FAIL':
                compliance_score -= 30.0
                sanctions_check = False
                risk_level = "HIGH"
        
        # Check for sanctions
        if 'acc_decision' in transaction_data:
            acc_data = transaction_data['acc_decision']
            if 'reasons' in acc_data and any('SANCTION' in reason.upper() for reason in acc_data['reasons']):
                sanctions_check = False
                compliance_score -= 50.0
                risk_level = "CRITICAL"
        
        # Check KYC status
        if 'counterparty_data' in transaction_data:
            counterparty = transaction_data['counterparty_data']
            if not counterparty.get('kyc_verified', True):
                kyc_verified = False
                compliance_score -= 20.0
                if risk_level == "LOW":
                    risk_level = "MEDIUM"
        
        # Check transaction amount for regulatory limits
        if 'invoice_data' in transaction_data:
            invoice = transaction_data['invoice_data']
            amount = invoice.get('amount', 0)
            if amount > 1000000:  # Above 10 lakhs
                compliance_score -= 10.0
                if risk_level == "LOW":
                    risk_level = "MEDIUM"
        
        # Determine compliance status
        if compliance_score >= 80:
            status = "COMPLIANT"
        elif compliance_score >= 60:
            status = "PENDING"
        else:
            status = "NON_COMPLIANT"
        
        return ComplianceStatus(
            status=status,
            sanctions_check=sanctions_check,
            aml_check=aml_check,
            kyc_verified=kyc_verified,
            risk_level=risk_level,
            compliance_score=max(0.0, compliance_score)
        )
    
    async def _assess_risk(self, transaction_data: Dict[str, Any]) -> RiskAssessment:
        """Assess transaction risk"""
        
        # Initialize risk scores
        transaction_risk = 0.0
        counterparty_risk = 0.0
        operational_risk = 0.0
        risk_factors = []
        
        # Transaction risk assessment
        if 'invoice_data' in transaction_data:
            invoice = transaction_data['invoice_data']
            amount = invoice.get('amount', 0)
            
            if amount > 5000000:  # Above 50 lakhs
                transaction_risk += 30.0
                risk_factors.append("High transaction amount")
            elif amount > 1000000:  # Above 10 lakhs
                transaction_risk += 15.0
                risk_factors.append("Medium transaction amount")
        
        # Counterparty risk assessment
        if 'counterparty_data' in transaction_data:
            counterparty = transaction_data['counterparty_data']
            
            if not counterparty.get('kyc_verified', True):
                counterparty_risk += 40.0
                risk_factors.append("Counterparty KYC not verified")
            
            if counterparty.get('credit_score', 0) < 600:
                counterparty_risk += 20.0
                risk_factors.append("Low counterparty credit score")
        
        # Operational risk assessment
        if 'pdr_result' in transaction_data:
            pdr_data = transaction_data['pdr_result']
            if pdr_data.get('status') == 'FAILED':
                operational_risk += 25.0
                risk_factors.append("Payment execution failed")
        
        # ACC compliance risk
        if 'acc_decision' in transaction_data:
            acc_data = transaction_data['acc_decision']
            if acc_data.get('risk_score', 0) > 50:
                operational_risk += acc_data.get('risk_score', 0) * 0.3
                risk_factors.append("High ACC risk score")
        
        # Calculate overall risk score
        overall_risk_score = (transaction_risk + counterparty_risk + operational_risk) / 3
        
        return RiskAssessment(
            overall_risk_score=min(100.0, overall_risk_score),
            transaction_risk=min(100.0, transaction_risk),
            counterparty_risk=min(100.0, counterparty_risk),
            operational_risk=min(100.0, operational_risk),
            risk_factors=risk_factors
        )
    
    async def _build_audit_trail(self, request: CRRAKRequest, transaction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build audit trail for the transaction"""
        audit_trail = []
        
        # Add invoice creation
        audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "action": "INVOICE_CREATED",
            "actor": "SYSTEM",
            "details": f"Invoice {request.line_id} created in batch {request.batch_id}"
        })
        
        # Add ACC decision
        if 'acc_decision' in transaction_data:
            acc_data = transaction_data['acc_decision']
            audit_trail.append({
                "timestamp": acc_data.get('timestamp', datetime.now().isoformat()),
                "action": "ACC_DECISION",
                "actor": "ACC_AGENT",
                "details": f"ACC decision: {acc_data.get('decision', 'UNKNOWN')}",
                "evidence": acc_data.get('evidence_refs', [])
            })
        
        # Add PDR decision
        if 'pdr_result' in transaction_data:
            pdr_data = transaction_data['pdr_result']
            audit_trail.append({
                "timestamp": pdr_data.get('timestamp', datetime.now().isoformat()),
                "action": "PDR_DECISION",
                "actor": "PDR_AGENT",
                "details": f"PDR status: {pdr_data.get('status', 'UNKNOWN')}",
                "routing_plan": pdr_data.get('routing_plan', {})
            })
        
        # Add RCA analysis if available
        if 'rca_result' in transaction_data:
            rca_data = transaction_data['rca_result']
            audit_trail.append({
                "timestamp": rca_data.get('timestamp', datetime.now().isoformat()),
                "action": "RCA_ANALYSIS",
                "actor": "RCA_AGENT",
                "details": f"Root cause: {rca_data.get('root_cause', {}).get('issue', 'UNKNOWN')}"
            })
        
        return audit_trail
    
    async def _generate_recommendations(self, compliance_status: ComplianceStatus, risk_assessment: RiskAssessment) -> List[str]:
        """Generate recommendations based on compliance and risk assessment"""
        recommendations = []
        
        # Compliance recommendations
        if not compliance_status.sanctions_check:
            recommendations.append("Review sanctions list and update compliance rules")
        
        if not compliance_status.kyc_verified:
            recommendations.append("Complete KYC verification for counterparty")
        
        if compliance_status.compliance_score < 80:
            recommendations.append("Review transaction for compliance issues")
        
        # Risk recommendations
        if risk_assessment.overall_risk_score > 70:
            recommendations.append("Consider additional risk mitigation measures")
        
        if risk_assessment.counterparty_risk > 50:
            recommendations.append("Verify counterparty credentials and creditworthiness")
        
        if risk_assessment.operational_risk > 50:
            recommendations.append("Review operational processes and controls")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Transaction appears compliant and low risk")
        
        return recommendations
    
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
            "credit_ifsc": "BARB0RAEBAR",
            "created_at": datetime.now().isoformat()
        }
    
    async def _fetch_counterparty_data(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch counterparty data"""
        # Mock implementation - in production, this would query customer database
        return {
            "kyc_verified": True,
            "credit_score": 750,
            "account_age_days": 365,
            "transaction_history": "GOOD"
        }
    
    async def _store_crrak_report(self, request: CRRAKRequest, report: CRRAKReport, report_ref: str):
        """Store CRRAK report in S3"""
        try:
            # Extract S3 key from report_ref
            s3_key = report_ref.replace(f"s3://{self.s3_bucket}/", "")
            
            # Store JSON version
            json_data = {
                "task_type": "crrak_generated",
                "batch_id": request.batch_id,
                "line_id": request.line_id,
                "status": "SUCCESS",
                "report": report.dict(),
                "report_ref": report_ref,
                "timestamp": datetime.now().isoformat()
            }
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key.replace('.pdf', '.json'),
                Body=json.dumps(json_data, indent=2),
                ContentType='application/json'
            )
            
            # In production, generate PDF report
            # For now, store the JSON as the report
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(json_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Stored CRRAK report at {report_ref}")
            
        except Exception as e:
            logger.error(f"Failed to store CRRAK report: {e}")


# Initialize agent
crrak_agent = CRRAKAgent()


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "CRRAK Agent",
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

@app.post("/crrak/generate", response_model=CRRAKResult)
async def generate_crrak(request: CRRAKRequest):
    """Generate CRRAK report for a transaction"""
    return await crrak_agent.generate_crrak(request)

@app.get("/crrak/report/{batch_id}/{line_id}")
async def get_crrak_report(batch_id: str, line_id: str):
    """Get CRRAK report for a transaction"""
    try:
        s3_key = f"invoices/processed/{batch_id}/{line_id}/crrak.json"
        response = crrak_agent.s3_client.get_object(Bucket=crrak_agent.s3_bucket, Key=s3_key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="CRRAK report not found")
        raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")

@app.get("/crrak/compliance-summary")
async def get_compliance_summary(days: int = 30):
    """Get compliance summary for the period"""
    # Mock implementation - in production, this would analyze historical data
    return {
        "period_days": days,
        "total_transactions": 1250,
        "compliant_transactions": 1180,
        "non_compliant_transactions": 45,
        "pending_transactions": 25,
        "compliance_rate": 94.4,
        "common_issues": [
            {"issue": "KYC_NOT_VERIFIED", "count": 20},
            {"issue": "SANCTIONS_MATCH", "count": 15},
            {"issue": "HIGH_RISK_SCORE", "count": 10}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
