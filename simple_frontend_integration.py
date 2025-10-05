#!/usr/bin/env python3
"""
Simplified Frontend Integration API for Arealis Gateway v2
This version works without database dependency for local testing.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
class DashboardMetrics(BaseModel):
    total_disbursed: float
    loans_processed: int
    success_rate: float
    batches_awaiting: int
    last_updated: datetime

class Transaction(BaseModel):
    id: str
    date: str
    beneficiary: str
    amount: float
    status: str
    stage: str
    product: str
    creditScore: int
    reference: str

class AgentStatus(BaseModel):
    name: str
    layer: str
    status: str
    last_heartbeat: datetime
    metrics: Dict[str, Any]

class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: str
    current_layer: str
    current_agent: str
    last_update: datetime
    events: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    errors: List[str]

# Transaction store (mutable list to allow adding new transactions)
TRANSACTIONS_STORE = [
    Transaction(
        id="12345678",
        date="2025-09-29",
        beneficiary="Rajesh Kumar",
        amount=45000.0,
        status="completed",
        stage="reconciled",
        product="Personal Loan",
        creditScore=720,
        reference="UTR2025092912345"
    ),
    Transaction(
        id="12345679",
        date="2025-09-29",
        beneficiary="Priya Sharma",
        amount=32500.0,
        status="pending",
        stage="operator-review",
        product="MSME Loan",
        creditScore=680,
        reference="L-108"
    ),
    Transaction(
        id="12345680",
        date="2025-09-29",
        beneficiary="Amit Patel",
        amount=75000.0,
        status="completed",
        stage="executed",
        product="Business Loan",
        creditScore=750,
        reference="UTR2025092912346"
    ),
    Transaction(
        id="12345681",
        date="2025-09-29",
        beneficiary="Sneha Gupta",
        amount=25000.0,
        status="failed",
        stage="compliance",
        product="Personal Loan",
        creditScore=650,
        reference="L-109"
    )
]

MOCK_METRICS = DashboardMetrics(
    total_disbursed=8250400.0,
    loans_processed=210,
    success_rate=98.0,
    batches_awaiting=3,
    last_updated=datetime.now()
)

# FastAPI App
app = FastAPI(
    title="Arealis Gateway Frontend Integration API (Simplified)",
    description="API to bridge Next.js frontend with Python backend services (Simplified Version)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/api/v1/health")
async def health_check():
    """Health check for the integration API."""
    return {"status": "healthy", "service": "frontend_integration_api", "version": "1.0.0"}

@app.get("/api/v1/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """Fetches aggregated metrics for the dashboard."""
    return MOCK_METRICS

@app.get("/api/v1/transactions", response_model=List[Transaction])
async def get_transactions():
    """Fetches a list of recent transactions."""
    return TRANSACTIONS_STORE

@app.get("/api/v1/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction_details(transaction_id: str):
    """Fetches details for a specific transaction."""
    for transaction in TRANSACTIONS_STORE:
        if transaction.id == transaction_id:
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.get("/api/v1/agents", response_model=List[AgentStatus])
async def get_agent_status():
    """Fetches the status of all registered agents."""
    agents = [
        AgentStatus(
            name="FrontendIngestor",
            layer="ingest",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.1, "memory_usage": 0.2}
        ),
        AgentStatus(
            name="InvoiceValidator",
            layer="ingest",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.15, "memory_usage": 0.25}
        ),
        AgentStatus(
            name="IntentClassifier",
            layer="intent-router",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.2, "memory_usage": 0.3}
        ),
        AgentStatus(
            name="PDR",
            layer="orchestration",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.12, "memory_usage": 0.22}
        ),
        AgentStatus(
            name="ARL",
            layer="orchestration",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.18, "memory_usage": 0.28}
        ),
        AgentStatus(
            name="RCA",
            layer="orchestration",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.14, "memory_usage": 0.24}
        ),
        AgentStatus(
            name="CRRAK",
            layer="audit",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.16, "memory_usage": 0.26}
        ),
        AgentStatus(
            name="ACC",
            layer="security",
            status="active",
            last_heartbeat=datetime.now(),
            metrics={"cpu_usage": 0.13, "memory_usage": 0.23}
        )
    ]
    return agents

@app.post("/api/v1/batches/upload")
async def upload_batch(
    file: UploadFile = File(...),
    tenant_id: str = Form("AXIS"),
    batch_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Uploads a batch file (e.g., CSV) and initiates the ingestion workflow.
    """
    if not batch_id:
        batch_id = f"B-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.urandom(2).hex()}"

    logger.info(f"Frontend Integration: Received file upload for batch {batch_id}, tenant {tenant_id}")

    # Process file and add transactions
    file_content = await file.read()
    file_size = len(file_content)
    
    # Parse CSV and add transactions to store
    new_transactions = []
    try:
        csv_content = file_content.decode('utf-8')
        lines = csv_content.strip().split('\n')
        headers = lines[0].split(',')
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                values = line.split(',')
                if len(values) >= len(headers):
                    tx_dict = dict(zip(headers, values))
                    
                    # Create transaction
                    transaction = Transaction(
                        id=f"TXN-{batch_id}-{i:03d}",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        beneficiary=tx_dict.get('beneficiary', 'Unknown'),
                        amount=float(tx_dict.get('amount', 0)),
                        status="completed" if float(tx_dict.get('amount', 0)) < 50000 else "pending",
                        stage="executed" if float(tx_dict.get('amount', 0)) < 50000 else "operator-review",
                        product="Payment",
                        creditScore=750,
                        reference=tx_dict.get('reference', f"REF-{batch_id}-{i:03d}")
                    )
                    new_transactions.append(transaction)
                    logger.info(f"Processed transaction: {transaction.beneficiary} - {transaction.amount}")
        
        # Add new transactions to the store
        TRANSACTIONS_STORE.extend(new_transactions)
        logger.info(f"Added {len(new_transactions)} new transactions to store. Total: {len(TRANSACTIONS_STORE)}")
        
    except Exception as e:
        logger.error(f"Failed to process CSV: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Ingestion result
    ingestion_result = {
        "batch_id": batch_id,
        "tenant_id": tenant_id,
        "file_name": file.filename,
        "file_size": file_size,
        "status": "success",
        "records_processed": len(new_transactions),
        "timestamp": datetime.now().isoformat()
    }

    # Simulate triggering MCP workflow
    async def trigger_mcp_workflow():
        try:
            logger.info(f"Frontend Integration: Triggering MCP for batch {batch_id}")
            logger.info(f"Frontend Integration: MCP workflow started for batch {batch_id}")
        except Exception as e:
            logger.error(f"Frontend Integration: Failed to trigger MCP for batch {batch_id}: {e}")
    
    background_tasks.add_task(trigger_mcp_workflow)

    return {
        "message": "Batch upload received and workflow initiated", 
        "batch_id": batch_id, 
        "ingestion_result": ingestion_result
    }

@app.get("/api/v1/workflows/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """Get the current status of a workflow."""
    # Mock workflow status
    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status="INGESTING",
        current_layer="ingest",
        current_agent="FrontendIngestor",
        last_update=datetime.now(),
        events=[
            {
                "type": "invoice_received",
                "timestamp": datetime.now().isoformat(),
                "data": {"batch_id": workflow_id}
            }
        ],
        metadata={"batch_id": workflow_id, "tenant_id": "AXIS"},
        errors=[]
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Simplified Frontend Integration API on port 8020...")
    uvicorn.run(app, host="0.0.0.0", port=8020)
