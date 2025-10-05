"""
RCA Agent (Root Cause Analysis) Service
Analyzes the root cause of transaction failures or holds to inform corrective actions or audits.
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
    title="RCA Agent Service",
    description="Root Cause Analysis for transaction failures",
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


class RCARequest(BaseModel):
    """Input for RCA analysis"""
    task_type: str = "rca"
    batch_id: str
    line_id: str
    status: str  # FAILED, HOLD
    issues: List[str] = Field(default_factory=list)
    evidence_ref: str


class RootCause(BaseModel):
    """Root cause analysis result"""
    issue: str
    source: str  # PDR_VALIDATION, ACC_COMPLIANCE, BANK_API, etc.
    recommendation: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float = Field(ge=0.0, le=1.0)


class RCAResult(BaseModel):
    """RCA analysis output"""
    task_type: str = "rca_result"
    batch_id: str
    line_id: str
    status: str = "COMPLETED"
    root_cause: Optional[RootCause] = None
    evidence_ref: str
    timestamp: str
    analysis_details: Dict[str, Any] = Field(default_factory=dict)


class RCAAgent:
    """Main RCA agent for analyzing transaction failures"""
    
    def __init__(self):
        self.s3_client = s3_client
        self.s3_bucket = S3_BUCKET
    
    async def analyze_failure(self, request: RCARequest) -> RCAResult:
        """
        Analyze the root cause of a transaction failure
        """
        start_time = time.time()
        
        try:
            # Fetch failure data from S3 and database
            failure_data = await self._fetch_failure_data(request)
            
            # Analyze the root cause
            root_cause = await self._analyze_root_cause(request, failure_data)
            
            # Generate evidence reference
            evidence_ref = f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/rca.json"
            
            # Store RCA result in S3
            await self._store_rca_result(request, root_cause, evidence_ref)
            
            processing_time = (time.time() - start_time) * 1000
            
            return RCAResult(
                task_type="rca_result",
                batch_id=request.batch_id,
                line_id=request.line_id,
                status="COMPLETED",
                root_cause=root_cause,
                evidence_ref=evidence_ref,
                timestamp=datetime.now().isoformat(),
                analysis_details={
                    "processing_time_ms": processing_time,
                    "issues_analyzed": request.issues,
                    "data_sources": list(failure_data.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"RCA analysis failed for {request.batch_id}/{request.line_id}: {e}")
            
            # Return error result
            return RCAResult(
                task_type="rca_result",
                batch_id=request.batch_id,
                line_id=request.line_id,
                status="FAILED",
                evidence_ref=f"s3://{self.s3_bucket}/invoices/processed/{request.batch_id}/{request.line_id}/rca.json",
                timestamp=datetime.now().isoformat(),
                analysis_details={"error": str(e)}
            )
    
    async def _fetch_failure_data(self, request: RCARequest) -> Dict[str, Any]:
        """Fetch relevant data for RCA analysis"""
        failure_data = {}
        
        try:
            # Fetch PDR result from S3
            pdr_key = f"invoices/processed/{request.batch_id}/{request.line_id}/pdr.json"
            try:
                pdr_response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=pdr_key)
                failure_data['pdr_result'] = json.loads(pdr_response['Body'].read().decode('utf-8'))
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    logger.warning(f"Could not fetch PDR result: {e}")
            
            # Fetch ACC decision from S3
            acc_key = f"invoices/processed/{request.batch_id}/{request.line_id}/acc.json"
            try:
                acc_response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=acc_key)
                failure_data['acc_decision'] = json.loads(acc_response['Body'].read().decode('utf-8'))
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    logger.warning(f"Could not fetch ACC decision: {e}")
            
            # Fetch invoice data from database
            failure_data['invoice_data'] = await self._fetch_invoice_data(request.batch_id, request.line_id)
            
            # Fetch rail performance data
            failure_data['rail_performance'] = await self._fetch_rail_performance(request.batch_id, request.line_id)
            
        except Exception as e:
            logger.error(f"Error fetching failure data: {e}")
        
        return failure_data
    
    async def _analyze_root_cause(self, request: RCARequest, failure_data: Dict[str, Any]) -> Optional[RootCause]:
        """Analyze the root cause based on available data"""
        
        # Map common issues to root causes
        issue_mapping = {
            "INVALID_IFSC": {
                "source": "PDR_VALIDATION",
                "recommendation": "Verify IFSC code with bank or use correct IFSC",
                "severity": "HIGH"
            },
            "SANCTIONED": {
                "source": "ACC_COMPLIANCE",
                "recommendation": "Review sanctions list and update compliance rules",
                "severity": "CRITICAL"
            },
            "INSUFFICIENT_FUNDS": {
                "source": "BANK_API",
                "recommendation": "Check account balance and retry transaction",
                "severity": "MEDIUM"
            },
            "ACCOUNT_BLOCKED": {
                "source": "BANK_API",
                "recommendation": "Contact bank to unblock account",
                "severity": "HIGH"
            },
            "DAILY_LIMIT_EXCEEDED": {
                "source": "PDR_VALIDATION",
                "recommendation": "Check daily limits or use different rail",
                "severity": "MEDIUM"
            },
            "BANK_UNAVAILABLE": {
                "source": "BANK_API",
                "recommendation": "Retry transaction or use alternative rail",
                "severity": "LOW"
            },
            "INVALID_ACCOUNT": {
                "source": "BANK_API",
                "recommendation": "Verify account number and IFSC",
                "severity": "HIGH"
            }
        }
        
        # Analyze each issue
        for issue in request.issues:
            if issue in issue_mapping:
                mapping = issue_mapping[issue]
                
                # Additional analysis based on failure data
                confidence = self._calculate_confidence(issue, failure_data)
                
                return RootCause(
                    issue=issue,
                    source=mapping["source"],
                    recommendation=mapping["recommendation"],
                    severity=mapping["severity"],
                    confidence=confidence
                )
        
        # If no specific issue mapping, analyze based on available data
        return self._analyze_generic_failure(request, failure_data)
    
    def _calculate_confidence(self, issue: str, failure_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the root cause analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on available evidence
        if 'pdr_result' in failure_data:
            confidence += 0.2
        
        if 'acc_decision' in failure_data:
            confidence += 0.2
        
        if 'invoice_data' in failure_data:
            confidence += 0.1
        
        # Specific confidence adjustments based on issue type
        if issue == "INVALID_IFSC" and 'pdr_result' in failure_data:
            pdr_data = failure_data['pdr_result']
            if 'issues' in pdr_data and issue in pdr_data['issues']:
                confidence = 0.9
        
        return min(1.0, confidence)
    
    def _analyze_generic_failure(self, request: RCARequest, failure_data: Dict[str, Any]) -> Optional[RootCause]:
        """Analyze generic failure when no specific issue mapping exists"""
        
        # Check if it's a rail-specific failure
        if 'pdr_result' in failure_data:
            pdr_data = failure_data['pdr_result']
            if 'routing_plan' in pdr_data and 'primary_route' in pdr_data['routing_plan']:
                primary_route = pdr_data['routing_plan']['primary_route']
                channel = primary_route.get('channel', 'UNKNOWN')
                
                return RootCause(
                    issue="RAIL_FAILURE",
                    source="PDR_EXECUTION",
                    recommendation=f"Try alternative rail or contact {channel} support",
                    severity="MEDIUM",
                    confidence=0.6
                )
        
        # Default generic analysis
        return RootCause(
            issue="UNKNOWN_FAILURE",
            source="SYSTEM",
            recommendation="Review transaction logs and contact support",
            severity="LOW",
            confidence=0.3
        )
    
    async def _fetch_invoice_data(self, batch_id: str, line_id: str) -> Optional[Dict[str, Any]]:
        """Fetch invoice data from database"""
        # Mock implementation - in production, this would query PostgreSQL
        return {
            "batch_id": batch_id,
            "line_id": line_id,
            "amount": 250000,
            "currency": "INR",
            "status": "FAILED"
        }
    
    async def _fetch_rail_performance(self, batch_id: str, line_id: str) -> Optional[Dict[str, Any]]:
        """Fetch rail performance data"""
        # Mock implementation - in production, this would query rail_performance table
        return {
            "rail_name": "NEFT",
            "success_rate": 0.95,
            "avg_eta_ms": 7200000,
            "recent_failures": 2
        }
    
    async def _store_rca_result(self, request: RCARequest, root_cause: Optional[RootCause], evidence_ref: str):
        """Store RCA result in S3"""
        try:
            result_data = {
                "task_type": "rca_result",
                "batch_id": request.batch_id,
                "line_id": request.line_id,
                "status": "COMPLETED",
                "root_cause": root_cause.dict() if root_cause else None,
                "evidence_ref": evidence_ref,
                "timestamp": datetime.now().isoformat()
            }
            
            # Extract S3 key from evidence_ref
            s3_key = evidence_ref.replace(f"s3://{self.s3_bucket}/", "")
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=json.dumps(result_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Stored RCA result at {evidence_ref}")
            
        except Exception as e:
            logger.error(f"Failed to store RCA result: {e}")


# Initialize agent
rca_agent = RCAAgent()


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "RCA Agent",
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

@app.post("/rca/analyze", response_model=RCAResult)
async def analyze_failure(request: RCARequest):
    """Analyze root cause of transaction failure"""
    return await rca_agent.analyze_failure(request)

@app.get("/rca/evidence/{batch_id}/{line_id}")
async def get_rca_evidence(batch_id: str, line_id: str):
    """Get RCA evidence for a transaction"""
    try:
        s3_key = f"invoices/processed/{batch_id}/{line_id}/rca.json"
        response = rca_agent.s3_client.get_object(Bucket=rca_agent.s3_bucket, Key=s3_key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="RCA evidence not found")
        raise HTTPException(status_code=500, detail=f"Error fetching evidence: {str(e)}")

@app.get("/rca/patterns")
async def get_failure_patterns(days: int = 30):
    """Get common failure patterns for analysis"""
    # Mock implementation - in production, this would analyze historical data
    return {
        "common_issues": [
            {"issue": "INVALID_IFSC", "count": 45, "percentage": 35.2},
            {"issue": "INSUFFICIENT_FUNDS", "count": 28, "percentage": 21.9},
            {"issue": "SANCTIONED", "count": 15, "percentage": 11.7},
            {"issue": "ACCOUNT_BLOCKED", "count": 12, "percentage": 9.4}
        ],
        "analysis_period_days": days,
        "total_failures": 128
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
