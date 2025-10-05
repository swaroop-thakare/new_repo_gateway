#!/usr/bin/env python3
"""
Simplified Master Control Process for Arealis Gateway v2
This version works without PostgreSQL dependency for local testing.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class WorkflowStatus(Enum):
    INITIALIZED = "INITIALIZED"
    INGESTING = "INGESTING"
    VALIDATING = "VALIDATING"
    CLASSIFYING = "CLASSIFYING"
    ROUTING = "ROUTING"
    EXECUTING = "EXECUTING"
    AUDITING = "AUDITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    HOLD = "HOLD"

# Data Models
@dataclass
class WorkflowContext:
    workflow_id: str
    status: WorkflowStatus
    current_layer: str
    current_agent: str
    created_at: datetime
    last_update: datetime
    events: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    errors: List[str]

class WorkflowRequest(BaseModel):
    workflow_id: Optional[str] = None
    event_type: str
    data: Dict[str, Any] = Field(default_factory=dict)

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    current_layer: str
    current_agent: str
    timestamp: str
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    workflows: int
    agents: int

# Simplified MCP Class
class SimpleMCP:
    def __init__(self):
        self.workflows: Dict[str, WorkflowContext] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {
            "FrontendIngestor": {"layer": "ingest", "status": "active"},
            "InvoiceValidator": {"layer": "ingest", "status": "active"},
            "IntentClassifier": {"layer": "intent-router", "status": "active"},
            "PDR": {"layer": "orchestration", "status": "active"},
            "ARL": {"layer": "orchestration", "status": "active"},
            "RCA": {"layer": "orchestration", "status": "active"},
            "CRRAK": {"layer": "audit", "status": "active"},
            "ACC": {"layer": "security", "status": "active"},
        }
        self.metrics = {
            "total_disbursed": 8250400.0,
            "loans_processed": 210,
            "success_rate": 98.0,
            "batches_awaiting": 3
        }

    async def start_workflow(self, event_data: Dict[str, Any]) -> WorkflowContext:
        """Start a new workflow."""
        workflow_id = event_data.get('workflow_id', f"WF-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.urandom(2).hex()}")
        
        context = WorkflowContext(
            workflow_id=workflow_id,
            status=WorkflowStatus.INITIALIZED,
            current_layer="ingest",
            current_agent="FrontendIngestor",
            created_at=datetime.now(),
            last_update=datetime.now(),
            events=[event_data],
            metadata=event_data.get('data', {}),
            errors=[]
        )
        
        self.workflows[workflow_id] = context
        logger.info(f"Started workflow {workflow_id}")
        return context

    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle events in the workflow."""
        try:
            workflow_id = event_data.get('workflow_id')
            event_type = event_data.get('type', event_data.get('event_type'))
            
            if not workflow_id:
                raise ValueError("workflow_id is required")
            
            if workflow_id not in self.workflows:
                logger.warning(f"Workflow {workflow_id} not found, creating new one")
                return await self.start_workflow(event_data)
            
            context = self.workflows[workflow_id]
            context.last_update = datetime.now()
            context.events.append(event_data)
            
            logger.info(f"Handling event '{event_type}' for workflow {workflow_id}")
            
            # Process event based on type
            if event_type == "invoice_received":
                context.status = WorkflowStatus.INGESTING
                context.current_layer = "ingest"
                context.current_agent = "FrontendIngestor"
                
            elif event_type == "validated_invoice":
                context.status = WorkflowStatus.VALIDATING
                context.current_layer = "intent-router"
                context.current_agent = "IntentClassifier"
                
            elif event_type == "workflow_selected":
                context.status = WorkflowStatus.CLASSIFYING
                context.current_layer = "orchestration"
                context.current_agent = "Orchestrator"
                
            elif event_type == "pdr_result":
                context.status = WorkflowStatus.ROUTING
                context.current_layer = "orchestration"
                context.current_agent = "PDR"
                
            elif event_type == "execution_result":
                context.status = WorkflowStatus.EXECUTING
                context.current_layer = "orchestration"
                context.current_agent = "Execution"
                
            elif event_type == "arl_result":
                context.status = WorkflowStatus.EXECUTING
                context.current_layer = "orchestration"
                context.current_agent = "ARL"
                
            elif event_type == "rca_result":
                context.status = WorkflowStatus.EXECUTING
                context.current_layer = "orchestration"
                context.current_agent = "RCA"
                
            elif event_type == "crrak_generated":
                context.status = WorkflowStatus.AUDITING
                context.current_layer = "audit"
                context.current_agent = "CRRAK"
                
            elif event_type == "audit_report_generated":
                context.status = WorkflowStatus.COMPLETED
                context.current_layer = "audit"
                context.current_agent = "AuditLogger"
                
            else:
                logger.warning(f"Unknown event type: {event_type}")
                context.status = WorkflowStatus.FAILED
                context.errors.append(f"Unknown event type: {event_type}")
            
            return {
                "workflow_id": workflow_id,
                "status": context.status.value,
                "current_layer": context.current_layer,
                "current_agent": context.current_agent,
                "timestamp": context.last_update.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to handle event: {str(e)}")
            raise

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status."""
        if workflow_id not in self.workflows:
            return None
        
        context = self.workflows[workflow_id]
        return {
            "workflow_id": context.workflow_id,
            "status": context.status.value,
            "current_layer": context.current_layer,
            "current_agent": context.current_agent,
            "last_update": context.last_update.isoformat(),
            "events": context.events,
            "metadata": context.metadata,
            "errors": context.errors
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return self.metrics.copy()

    def get_agents(self) -> List[Dict[str, Any]]:
        """Get agent status."""
        return [
            {
                "name": name,
                "layer": details["layer"],
                "status": details["status"],
                "last_heartbeat": datetime.now().isoformat(),
                "metrics": {"cpu_usage": 0.1, "memory_usage": 0.2}
            }
            for name, details in self.agent_registry.items()
        ]

# Initialize MCP
mcp = SimpleMCP()

# FastAPI App
app = FastAPI(
    title="Arealis Gateway v2 - Simplified MCP",
    description="Master Control Process for Arealis Gateway v2 (Simplified Version)",
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
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="simplified_mcp",
        version="1.0.0",
        workflows=len(mcp.workflows),
        agents=len(mcp.agent_registry)
    )

@app.post("/api/v1/workflows/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest):
    """Start a new workflow."""
    try:
        event_data = {
            "workflow_id": request.workflow_id,
            "type": request.event_type,
            "data": request.data
        }
        context = await mcp.start_workflow(event_data)
        
        return WorkflowResponse(
            workflow_id=context.workflow_id,
            status=context.status.value,
            current_layer=context.current_layer,
            current_agent=context.current_agent,
            timestamp=context.last_update.isoformat(),
            message="Workflow started successfully"
        )
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/workflows/{workflow_id}/events")
async def handle_workflow_event(workflow_id: str, event_data: Dict[str, Any]):
    """Handle workflow events."""
    try:
        event_data["workflow_id"] = workflow_id
        result = await mcp.handle_event(event_data)
        return result
    except Exception as e:
        logger.error(f"Failed to handle event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get workflow status."""
    status = mcp.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get system metrics."""
    return mcp.get_metrics()

@app.get("/api/v1/agents")
async def get_agents():
    """Get agent status."""
    return mcp.get_agents()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Simplified MCP on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
