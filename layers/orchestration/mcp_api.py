"""
MCP API Server - Arealis Gateway v2

FastAPI server for Master Control Process providing REST endpoints
for workflow management, agent monitoring, and system health.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from master_control import MasterControlProcess, WorkflowStatus, AgentStatus
from mcp_config import mcp_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Arealis Gateway v2 MCP API",
    description="Master Control Process API for workflow management and agent coordination",
    version="2.0.0"
)

# Initialize MCP
mcp = MasterControlProcess()

# Pydantic models for API
class WorkflowTrigger(BaseModel):
    """Workflow trigger request model."""
    batch_id: str
    tenant_id: str
    source: str
    upload_ts: Optional[str] = None
    raw_file_key: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class WorkflowStatusResponse(BaseModel):
    """Workflow status response model."""
    workflow_id: str
    batch_id: str
    tenant_id: str
    status: str
    current_layer: Optional[str]
    current_agent: Optional[str]
    start_time: str
    last_update: str
    errors: List[str]

class AgentStatusResponse(BaseModel):
    """Agent status response model."""
    name: str
    layer: str
    status: str
    dependencies: List[str]
    last_run: Optional[str]
    error_count: int

class SystemHealthResponse(BaseModel):
    """System health response model."""
    overall_status: str
    components: Dict[str, str]
    health_score: float
    timestamp: str

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize MCP on startup."""
    try:
        await mcp.initialize()
        logger.info("MCP API server started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown MCP on shutdown."""
    try:
        await mcp.shutdown()
        logger.info("MCP API server shutdown completed")
    except Exception as e:
        logger.error(f"Failed to shutdown MCP: {str(e)}")

# API Endpoints

@app.post("/api/v1/workflows/start", response_model=Dict[str, str])
async def start_workflow(trigger: WorkflowTrigger):
    """
    Start a new workflow.
    
    Args:
        trigger: Workflow trigger data
        
    Returns:
        Workflow ID and status
    """
    try:
        # Convert to dict for MCP
        trigger_data = trigger.dict()
        
        # Start workflow
        workflow_id = await mcp.start_workflow(trigger_data)
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": f"Workflow {workflow_id} started successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to start workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get workflow status.
    
    Args:
        workflow_id: Workflow identifier
        
    Returns:
        Workflow status information
    """
    try:
        status = await mcp.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """
    Cancel a workflow.
    
    Args:
        workflow_id: Workflow identifier
        
    Returns:
        Cancellation status
    """
    try:
        # Get current status
        status = await mcp.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Mark as failed
        context = mcp.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.FAILED
            context.errors.append("Workflow cancelled by user")
            context.last_update = datetime.now()
        
        return {
            "workflow_id": workflow_id,
            "status": "cancelled",
            "message": f"Workflow {workflow_id} cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents", response_model=List[AgentStatusResponse])
async def get_all_agents():
    """
    Get status of all agents.
    
    Returns:
        List of agent statuses
    """
    try:
        agents = []
        for agent_name in mcp.agents.keys():
            status = await mcp.get_agent_status(agent_name)
            if status:
                agents.append(AgentStatusResponse(**status))
        
        return agents
        
    except Exception as e:
        logger.error(f"Failed to get agent statuses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/{agent_name}", response_model=AgentStatusResponse)
async def get_agent_status(agent_name: str):
    """
    Get status of a specific agent.
    
    Args:
        agent_name: Agent name
        
    Returns:
        Agent status information
    """
    try:
        status = await mcp.get_agent_status(agent_name)
        
        if not status:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/{agent_name}/restart")
async def restart_agent(agent_name: str):
    """
    Restart a specific agent.
    
    Args:
        agent_name: Agent name
        
    Returns:
        Restart status
    """
    try:
        agent = mcp.agents.get(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Reset agent status
        agent.status = AgentStatus.IDLE
        agent.error_count = 0
        agent.last_run = None
        
        return {
            "agent_name": agent_name,
            "status": "restarted",
            "message": f"Agent {agent_name} restarted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/health", response_model=SystemHealthResponse)
async def get_system_health():
    """
    Get system health status.
    
    Returns:
        System health information
    """
    try:
        # Check MCP status
        mcp_status = "healthy" if mcp.workflows else "degraded"
        
        # Check agent statuses
        agent_statuses = {}
        healthy_agents = 0
        total_agents = len(mcp.agents)
        
        for agent_name, agent in mcp.agents.items():
            if agent.status in [AgentStatus.IDLE, AgentStatus.SUCCESS]:
                agent_statuses[agent_name] = "healthy"
                healthy_agents += 1
            elif agent.status == AgentStatus.RUNNING:
                agent_statuses[agent_name] = "running"
                healthy_agents += 1
            else:
                agent_statuses[agent_name] = "unhealthy"
        
        # Calculate health score
        health_score = (healthy_agents / total_agents) * 100 if total_agents > 0 else 0
        
        # Determine overall status
        if health_score >= 90:
            overall_status = "healthy"
        elif health_score >= 70:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return SystemHealthResponse(
            overall_status=overall_status,
            components=agent_statuses,
            health_score=health_score,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/metrics")
async def get_system_metrics():
    """
    Get system metrics.
    
    Returns:
        System metrics information
    """
    try:
        # Active workflows
        active_workflows = len([w for w in mcp.workflows.values() 
                              if w.status not in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]])
        
        # Agent metrics
        agent_metrics = {}
        for agent_name, agent in mcp.agents.items():
            agent_metrics[agent_name] = {
                "status": agent.status.value,
                "error_count": agent.error_count,
                "last_run": agent.last_run.isoformat() if agent.last_run else None
            }
        
        # Workflow metrics
        workflow_metrics = {}
        for workflow_id, context in mcp.workflows.items():
            workflow_metrics[workflow_id] = {
                "status": context.status.value,
                "current_layer": context.current_layer,
                "current_agent": context.current_agent,
                "duration_seconds": (context.last_update - context.start_time).total_seconds(),
                "error_count": len(context.errors)
            }
        
        return {
            "active_workflows": active_workflows,
            "total_workflows": len(mcp.workflows),
            "agent_metrics": agent_metrics,
            "workflow_metrics": workflow_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/config")
async def get_system_config():
    """
    Get system configuration.
    
    Returns:
        System configuration information
    """
    try:
        return {
            "app_name": mcp_config.app_name,
            "app_version": mcp_config.app_version,
            "max_concurrent_workflows": mcp_config.max_concurrent_workflows,
            "agent_timeout": mcp_config.agent_timeout,
            "workflow_timeout": mcp_config.workflow_timeout,
            "layers": list(mcp_config.LAYER_AGENTS.keys()),
            "agents": list(mcp.agents.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "mcp_api",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=mcp_config.mcp_host,
        port=mcp_config.mcp_port,
        log_level=mcp_config.log_level.lower()
    )
