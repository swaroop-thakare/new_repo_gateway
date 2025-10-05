#!/usr/bin/env python3
"""
Prompt Layer (xAI) Service for Arealis Gateway v2
Provides detailed responses to user queries about transaction statuses
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Prompt Layer (xAI) Service",
    description="Enhanced Prompt Layer powered by xAI for transaction analysis",
    version="1.0.0"
)

# Database and S3 configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "arealis_gateway",
    "user": "postgres",
    "password": "password"
}

S3_CONFIG = {
    "bucket": "arealis-evidence",
    "region": "us-east-1"
}

# Initialize S3 client
s3_client = boto3.client('s3')

@dataclass
class AgentOutput:
    """Data structure for agent outputs"""
    agent_name: str
    data: Dict[str, Any]
    timestamp: str
    evidence_refs: List[str]

class QueryRequest(BaseModel):
    """Request model for prompt layer queries"""
    query: str
    batch_id: str
    line_id: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    """Response model for prompt layer queries"""
    query: str
    response: Dict[str, Any]
    evidence_refs: List[str]
    timestamp: str

class AgentDataRetriever:
    """Service to retrieve data from various agents"""
    
    def __init__(self):
        self.acc_service_url = "http://localhost:8002"
        self.rca_service_url = "http://localhost:8009"
        self.arl_service_url = "http://localhost:8008"
        self.crrak_service_url = "http://localhost:8010"
        self.mcp_service_url = "http://localhost:8000"
    
    async def get_acc_data(self, line_id: str, batch_id: str) -> Optional[AgentOutput]:
        """Retrieve ACC agent data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.acc_service_url}/api/v1/status/{line_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return AgentOutput(
                            agent_name="ACC",
                            data=data,
                            timestamp=data.get("timestamp", datetime.now().isoformat()),
                            evidence_refs=data.get("evidence_refs", [])
                        )
        except Exception as e:
            logger.error(f"Failed to retrieve ACC data: {e}")
        return None
    
    async def get_rca_data(self, line_id: str, batch_id: str) -> Optional[AgentOutput]:
        """Retrieve RCA agent data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.rca_service_url}/api/v1/status/{line_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return AgentOutput(
                            agent_name="RCA",
                            data=data,
                            timestamp=data.get("timestamp", datetime.now().isoformat()),
                            evidence_refs=data.get("evidence_refs", [])
                        )
        except Exception as e:
            logger.error(f"Failed to retrieve RCA data: {e}")
        return None
    
    async def get_arl_data(self, line_id: str, batch_id: str) -> Optional[AgentOutput]:
        """Retrieve ARL agent data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.arl_service_url}/api/v1/status/{line_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return AgentOutput(
                            agent_name="ARL",
                            data=data,
                            timestamp=data.get("timestamp", datetime.now().isoformat()),
                            evidence_refs=data.get("evidence_refs", [])
                        )
        except Exception as e:
            logger.error(f"Failed to retrieve ARL data: {e}")
        return None
    
    async def get_crrak_data(self, line_id: str, batch_id: str) -> Optional[AgentOutput]:
        """Retrieve CRRAK agent data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.crrak_service_url}/api/v1/status/{line_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return AgentOutput(
                            agent_name="CRRAK",
                            data=data,
                            timestamp=data.get("timestamp", datetime.now().isoformat()),
                            evidence_refs=data.get("evidence_refs", [])
                        )
        except Exception as e:
            logger.error(f"Failed to retrieve CRRAK data: {e}")
        return None
    
    async def get_mcp_workflow_data(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve MCP workflow data"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mcp_service_url}/api/v1/workflows/{batch_id}") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Failed to retrieve MCP workflow data: {e}")
        return None

class XAIAnalyzer:
    """xAI-powered analysis engine"""
    
    def __init__(self):
        self.retriever = AgentDataRetriever()
    
    async def analyze_query(self, request: QueryRequest) -> QueryResponse:
        """Analyze user query using xAI and agent data"""
        
        # Step 1: Query Reception
        logger.info(f"Processing query: {request.query}")
        
        # Step 2: Get Real Transaction Data from Frontend Integration
        real_transaction_data = await self._get_real_transaction_data(request.line_id, request.batch_id)
        
        # Step 3: Data Retrieval - Use context if provided, otherwise fetch from agents
        if request.context:
            # Use provided context data
            acc_data = AgentOutput("ACC", request.context.get("acc_output", {}), datetime.now().isoformat(), [])
            rca_data = AgentOutput("RCA", request.context.get("rca_output", {}), datetime.now().isoformat(), [])
            arl_data = AgentOutput("ARL", request.context.get("arl_output", {}), datetime.now().isoformat(), [])
            crrak_data = AgentOutput("CRRAK", request.context.get("crrak_output", {}), datetime.now().isoformat(), [])
            mcp_data = request.context.get("mcp_workflow", {})
        else:
            # Fetch data from all agents
            acc_data = await self.retriever.get_acc_data(request.line_id, request.batch_id)
            rca_data = await self.retriever.get_rca_data(request.line_id, request.batch_id)
            arl_data = await self.retriever.get_arl_data(request.line_id, request.batch_id)
            crrak_data = await self.retriever.get_crrak_data(request.line_id, request.batch_id)
            mcp_data = await self.retriever.get_mcp_workflow_data(request.batch_id)
        
        # Step 4: Context Analysis with Real Transaction Data
        context = self._build_context(acc_data, rca_data, arl_data, crrak_data, mcp_data)
        context["real_transaction"] = real_transaction_data
        
        # Step 5: Response Generation using xAI with Real Data
        response = await self._generate_xai_response(request.query, context)
        
        # Step 6: Evidence Linking
        evidence_refs = self._collect_evidence_refs(acc_data, rca_data, arl_data, crrak_data)
        
        return QueryResponse(
            query=request.query,
            response=response,
            evidence_refs=evidence_refs,
            timestamp=datetime.now().isoformat()
        )
    
    async def _get_real_transaction_data(self, line_id: str, batch_id: str) -> Dict[str, Any]:
        """Get real transaction data from frontend integration API"""
        try:
            # Try to get transaction data from frontend integration API
            async with aiohttp.ClientSession() as session:
                # First try to get all transactions
                async with session.get("http://localhost:8020/api/v1/transactions") as response:
                    if response.status == 200:
                        transactions = await response.json()
                        
                        # Look for the specific transaction by line_id or batch_id
                        for tx in transactions:
                            if (tx.get("id") == line_id or 
                                tx.get("reference") == line_id or 
                                tx.get("id") == f"TXN-{batch_id}-{line_id}"):
                                logger.info(f"Found real transaction data for {line_id}: {tx}")
                                return tx
                        
                        # If not found by line_id, return the first transaction as example
                        if transactions:
                            logger.info(f"Using first available transaction as example: {transactions[0]}")
                            return transactions[0]
                        
        except Exception as e:
            logger.warning(f"Could not fetch real transaction data: {e}")
        
        # Return None if no real data available - no fallback to mock data
        return None
    
    def _build_context(self, acc_data: Optional[AgentOutput], rca_data: Optional[AgentOutput], 
                      arl_data: Optional[AgentOutput], crrak_data: Optional[AgentOutput], 
                      mcp_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive context from agent data"""
        context = {
            "acc_output": acc_data.data if acc_data else {},
            "rca_output": rca_data.data if rca_data else {},
            "arl_output": arl_data.data if arl_data else {},
            "crrak_output": crrak_data.data if crrak_data else {},
            "mcp_workflow": mcp_data or {}
        }
        return context
    
    async def _generate_xai_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate xAI-powered response"""
        
        # Extract key information from context
        acc_output = context.get("acc_output", {})
        rca_output = context.get("rca_output", {})
        arl_output = context.get("arl_output", {})
        real_transaction = context.get("real_transaction", {})
        
        # Build failure reason with real transaction data
        failure_reason = self._build_failure_reason(acc_output, rca_output, arl_output, real_transaction)
        
        # Build detailed analysis
        detailed_analysis = self._build_detailed_analysis(acc_output, rca_output, arl_output, real_transaction)
        
        # Build recommended actions
        recommended_actions = self._build_recommended_actions(rca_output, acc_output)
        
        # Build additional notes
        additional_notes = self._build_additional_notes(acc_output, rca_output, arl_output, real_transaction)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(acc_output, rca_output, arl_output)
        
        return {
            "failure_reason": failure_reason,
            "detailed_analysis": detailed_analysis,
            "recommended_actions": recommended_actions,
            "additional_notes": additional_notes,
            "confidence_score": confidence_score
        }
    
    def _build_failure_reason(self, acc_output: Dict, rca_output: Dict, arl_output: Dict, real_transaction: Dict = None) -> str:
        """Build comprehensive failure reason using real transaction data"""
        if not acc_output and not real_transaction:
            return "No transaction or agent data available for analysis"
        
        # Use real transaction data if available
        if real_transaction:
            beneficiary_name = real_transaction.get("beneficiary", "Unknown")
            amount = real_transaction.get("amount", 0)
            transaction_id = real_transaction.get("id", "Unknown")
            status = real_transaction.get("status", "unknown")
            stage = real_transaction.get("stage", "unknown")
            
            if acc_output:
                decision = acc_output.get("decision", "UNKNOWN")
                reasons = acc_output.get("reasons", [])
                timestamp = acc_output.get("timestamp", "")
                
                if decision == "FAIL":
                    reason_text = ", ".join(reasons) if reasons else "Unknown reason"
                    return f"Transaction {transaction_id} failed due to {reason_text} during ACC process on {timestamp}. The beneficiary '{beneficiary_name}' was flagged for a transaction amount of ₹{amount:,}. Current status: {status}, Stage: {stage}"
                else:
                    return f"Transaction {transaction_id} status: {decision} as of {timestamp}. Beneficiary: {beneficiary_name}, Amount: ₹{amount:,}, Status: {status}, Stage: {stage}"
            else:
                return f"Transaction {transaction_id}: Beneficiary: {beneficiary_name}, Amount: ₹{amount:,}, Status: {status}, Stage: {stage}"
        
        # Fallback to ACC data only if no real transaction data
        if acc_output:
            decision = acc_output.get("decision", "UNKNOWN")
            reasons = acc_output.get("reasons", [])
            timestamp = acc_output.get("timestamp", "")
            
            if decision == "FAIL":
                reason_text = ", ".join(reasons) if reasons else "Unknown reason"
                beneficiary = acc_output.get("beneficiary", {})
                beneficiary_name = beneficiary.get("name", "Unknown") if beneficiary else "Unknown"
                amount = acc_output.get("amount", 0)
                
                return f"Line failed due to {reason_text} during ACC process on {timestamp}. The beneficiary '{beneficiary_name}' was flagged for a transaction amount of ₹{amount:,}."
            
            return f"Line status: {decision} as of {timestamp}"
        
        return "No analysis data available"
    
    def _build_detailed_analysis(self, acc_output: Dict, rca_output: Dict, arl_output: Dict, real_transaction: Dict = None) -> str:
        """Build detailed technical analysis using real transaction data"""
        analysis_parts = []
        
        # Add real transaction information first
        if real_transaction:
            transaction_id = real_transaction.get("id", "Unknown")
            beneficiary_name = real_transaction.get("beneficiary", "Unknown")
            amount = real_transaction.get("amount", 0)
            status = real_transaction.get("status", "unknown")
            stage = real_transaction.get("stage", "unknown")
            reference = real_transaction.get("reference", "Unknown")
            product = real_transaction.get("product", "Unknown")
            credit_score = real_transaction.get("creditScore", 0)
            
            analysis_parts.append(f"Transaction ID: {transaction_id}")
            analysis_parts.append(f"Beneficiary: {beneficiary_name}")
            analysis_parts.append(f"Amount: ₹{amount:,}")
            analysis_parts.append(f"Status: {status}")
            analysis_parts.append(f"Stage: {stage}")
            analysis_parts.append(f"Reference: {reference}")
            analysis_parts.append(f"Product: {product}")
            if credit_score > 0:
                analysis_parts.append(f"Credit Score: {credit_score}")
        
        # Only add agent data if it's available and not hardcoded
        if acc_output and acc_output.get("timestamp"):
            decision = acc_output.get("decision", "UNKNOWN")
            reasons = acc_output.get("reasons", [])
            timestamp = acc_output.get("timestamp", "")
            
            analysis_parts.append(f"ACC Decision: {decision}")
            if reasons:
                analysis_parts.append(f"ACC Reasons: {', '.join(reasons)}")
            analysis_parts.append(f"ACC Timestamp: {timestamp}")
        
        if rca_output and rca_output.get("timestamp"):
            root_cause = rca_output.get("root_cause", "")
            explanation = rca_output.get("explanation", "")
            fault_party = rca_output.get("fault_party", "")
            confidence = rca_output.get("priority_score", 0)
            timestamp = rca_output.get("timestamp", "")
            
            if root_cause:
                analysis_parts.append(f"Root Cause: {root_cause}")
            if explanation:
                analysis_parts.append(f"Explanation: {explanation}")
            if fault_party:
                analysis_parts.append(f"Fault Party: {fault_party}")
            if confidence:
                analysis_parts.append(f"Priority Score: {confidence}")
            analysis_parts.append(f"RCA Timestamp: {timestamp}")
        
        if arl_output and arl_output.get("timestamp"):
            status = arl_output.get("status", "UNKNOWN")
            exceptions = arl_output.get("exceptions", [])
            journals = arl_output.get("journals", [])
            timestamp = arl_output.get("timestamp", "")
            
            analysis_parts.append(f"ARL Status: {status}")
            if exceptions:
                analysis_parts.append(f"ARL Exceptions: {len(exceptions)} found")
            if journals:
                analysis_parts.append(f"ARL Journals: {len(journals)} generated")
            analysis_parts.append(f"ARL Timestamp: {timestamp}")
        
        return " | ".join(analysis_parts) if analysis_parts else "No detailed analysis available - no real transaction or agent data found"
    
    def _build_recommended_actions(self, rca_output: Dict, acc_output: Dict) -> List[Dict[str, str]]:
        """Build recommended actions from RCA and ACC data"""
        actions = []
        
        if rca_output and "recommended_actions" in rca_output:
            for i, action in enumerate(rca_output["recommended_actions"], 1):
                actions.append({
                    "action": f"Action {i}",
                    "description": action,
                    "priority": "High" if i == 1 else "Medium" if i == 2 else "Low",
                    "estimated_time": "2-3 business days" if i == 1 else "1 business day" if i == 2 else "1 hour",
                    "responsible_party": "Compliance Team" if i == 1 else "Operations Team" if i == 2 else "Merchant Support"
                })
        
        if not actions:
            actions.append({
                "action": "Manual Review",
                "description": "Conduct manual review of transaction details",
                "priority": "High",
                "estimated_time": "2-3 business days",
                "responsible_party": "Operations Team"
            })
        
        return actions
    
    def _build_additional_notes(self, acc_output: Dict, rca_output: Dict, arl_output: Dict, real_transaction: Dict = None) -> str:
        """Build additional compliance and audit notes using real transaction data"""
        notes = []
        
        # Add real transaction notes
        if real_transaction:
            transaction_id = real_transaction.get("id", "Unknown")
            date = real_transaction.get("date", "Unknown")
            notes.append(f"Transaction {transaction_id} processed on {date}")
            
            if real_transaction.get("status") == "failed":
                notes.append("Transaction failed - requires manual intervention")
            elif real_transaction.get("status") == "pending":
                notes.append("Transaction pending - awaiting processing")
            elif real_transaction.get("status") == "completed":
                notes.append("Transaction completed successfully")
            
            # Add product-specific notes
            product = real_transaction.get("product", "")
            if product:
                notes.append(f"Product type: {product}")
            
            # Add credit score notes
            credit_score = real_transaction.get("creditScore", 0)
            if credit_score > 0:
                if credit_score >= 750:
                    notes.append("High credit score - low risk transaction")
                elif credit_score >= 650:
                    notes.append("Medium credit score - moderate risk")
                else:
                    notes.append("Low credit score - high risk transaction")
        
        # Only add agent notes if they have real timestamps (not hardcoded)
        if acc_output and acc_output.get("timestamp"):
            policy_version = acc_output.get("policy_version", "")
            if policy_version:
                notes.append(f"Compliance with policy version: {policy_version}")
            
            decision = acc_output.get("decision", "")
            if decision == "FAIL":
                notes.append("ACC flagged transaction for compliance issues")
            elif decision == "PASS":
                notes.append("ACC cleared transaction for compliance")
        
        if rca_output and rca_output.get("timestamp"):
            fault_party = rca_output.get("fault_party", "")
            if fault_party:
                notes.append(f"Fault party identified: {fault_party}")
            
            retry_eligible = rca_output.get("retry_eligible", False)
            if retry_eligible:
                notes.append("Transaction is eligible for retry")
            else:
                notes.append("Transaction is not eligible for retry")
        
        if arl_output and arl_output.get("timestamp"):
            status = arl_output.get("status", "")
            if status:
                notes.append(f"Reconciliation status: {status}")
            
            exceptions = arl_output.get("exceptions", [])
            if exceptions:
                notes.append(f"Reconciliation exceptions: {len(exceptions)} found")
        
        return " | ".join(notes) if notes else "No additional notes available - no real transaction or agent data found"
    
    def _calculate_confidence_score(self, acc_output: Dict, rca_output: Dict, arl_output: Dict) -> float:
        """Calculate confidence score based on available data"""
        score = 0.0
        
        if acc_output:
            score += 0.3
        if rca_output:
            score += 0.4
        if arl_output:
            score += 0.3
        
        return min(score, 1.0)
    
    def _collect_evidence_refs(self, acc_data: Optional[AgentOutput], rca_data: Optional[AgentOutput], 
                              arl_data: Optional[AgentOutput], crrak_data: Optional[AgentOutput]) -> List[str]:
        """Collect all evidence references"""
        evidence_refs = []
        
        if acc_data:
            evidence_refs.extend(acc_data.evidence_refs)
        if rca_data:
            evidence_refs.extend(rca_data.evidence_refs)
        if arl_data:
            evidence_refs.extend(arl_data.evidence_refs)
        if crrak_data:
            evidence_refs.extend(crrak_data.evidence_refs)
        
        return list(set(evidence_refs))  # Remove duplicates

# Initialize xAI analyzer
xai_analyzer = XAIAnalyzer()

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query and return xAI-powered response"""
    try:
        response = await xai_analyzer.analyze_query(request)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Prompt Layer (xAI)",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/agents/status")
async def get_agents_status():
    """Get status of all integrated agents"""
    try:
        retriever = AgentDataRetriever()
        
        # Check agent health
        agents_status = {}
        
        # Check ACC
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{retriever.acc_service_url}/api/v1/health") as response:
                    agents_status["ACC"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            agents_status["ACC"] = "unavailable"
        
        # Check RCA
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{retriever.rca_service_url}/api/v1/health") as response:
                    agents_status["RCA"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            agents_status["RCA"] = "unavailable"
        
        # Check ARL
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{retriever.arl_service_url}/api/v1/health") as response:
                    agents_status["ARL"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            agents_status["ARL"] = "unavailable"
        
        # Check CRRAK
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{retriever.crrak_service_url}/api/v1/health") as response:
                    agents_status["CRRAK"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            agents_status["CRRAK"] = "unavailable"
        
        # Check MCP
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{retriever.mcp_service_url}/api/v1/health") as response:
                    agents_status["MCP"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            agents_status["MCP"] = "unavailable"
        
        return {
            "status": "healthy",
            "agents": agents_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking agents status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v1/query/history/{line_id}")
async def get_query_history(line_id: str):
    """Get query history for a specific line"""
    try:
        # In production, this would query the database
        mock_history = [
            {
                "id": "1",
                "query": f"Why did line {line_id} fail?",
                "timestamp": "2025-01-05T10:00:00Z",
                "line_id": line_id,
                "batch_id": "B-2025-001"
            },
            {
                "id": "2",
                "query": f"What is the status of line {line_id}?",
                "timestamp": "2025-01-05T09:30:00Z",
                "line_id": line_id,
                "batch_id": "B-2025-001"
            }
        ]
        return mock_history
    except Exception as e:
        logger.error(f"Error retrieving query history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
