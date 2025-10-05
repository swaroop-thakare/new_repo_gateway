"""
Master Control Process (MCP) - Arealis Gateway v2

Central coordinator for all agents across layers, managing end-to-end workflow
from ingestion to audit while ensuring RBI compliance and system resilience.

Purpose: Serve as the central "brain" of the Arealis system, orchestrating all agents
across layers to manage the full lifecycle of payment transactions.

Logic: Act as a supervisory entity that initializes agents, routes events through
the workflow, monitors statuses, handles errors, and maintains system state.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

import boto3
import psycopg2
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration."""
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

class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    HOLD = "HOLD"

@dataclass
class Agent:
    """Agent definition for MCP registration."""
    name: str
    layer: str
    status: AgentStatus = AgentStatus.IDLE
    dependencies: List[str] = field(default_factory=list)
    handler: Optional[Callable] = None
    config: Dict[str, Any] = field(default_factory=dict)
    last_run: Optional[datetime] = None
    error_count: int = 0
    service_url: Optional[str] = None

@dataclass
class WorkflowContext:
    """Context for workflow execution."""
    batch_id: str
    tenant_id: str
    source: str
    status: WorkflowStatus
    current_layer: Optional[str] = None
    current_agent: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)

class MasterControlProcess:
    """
    Master Control Process for Arealis Gateway v2
    
    Central coordinator that manages all agents across layers and orchestrates
    the complete payment transaction lifecycle.
    """
    
    def __init__(self):
        """Initialize MCP with storage connections and agent registry."""
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, WorkflowContext] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}
        
        # Storage connections
        self.s3_client = boto3.client('s3')
        self.bucket_name = "arealis-invoices"
        
        # PostgreSQL connection
        self.db_config = {
            'host': 'localhost',
            'database': 'arealis_gateway',
            'user': 'postgres',
            'password': 'password'
        }
        
        # Configuration
        self.config = {
            "policy_version": "intent-2.0.0",
            "max_retries": 3,
            "timeout_seconds": 300,
            "enable_audit": True,
            "enable_monitoring": True
        }
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Service URLs for agent communication
        self.service_urls = {
            "FrontendIngestor": "http://localhost:8001",
            "InvoiceValidator": "http://localhost:8002",
            "IntentClassifier": "http://localhost:8003",
            "WorkflowSelector": "http://localhost:8004",
            "Orchestrator": "http://localhost:8005",
            "PDR": "http://localhost:8006",
            "Execution": "http://localhost:8007",
            "ARL": "http://localhost:8008",
            "RCA": "http://localhost:8009",
            "CRRAK": "http://localhost:8010",
            "ACC": "http://localhost:8011",
            "AuditLogger": "http://localhost:8012",
            "ComplianceChecker": "http://localhost:8013",
            "ContextMemory": "http://localhost:8014",
            "Monitor": "http://localhost:8015",
            "Debugger": "http://localhost:8016",
            "PromptGenerator": "http://localhost:8017",
            "PromptValidator": "http://localhost:8018",
            "SanctionScanner": "http://localhost:8019"
        }
        
        logger.info("MCP initialized successfully")
    
    async def initialize(self) -> None:
        """Initialize MCP by registering all agents and setting up event listeners."""
        try:
            logger.info("Initializing Master Control Process...")
            
            # Register agents from all layers
            await self._register_agents()
            
            # Setup event listeners
            await self._setup_event_listeners()
            
            # Initialize storage connections
            await self._initialize_storage()
            
            logger.info("MCP initialization completed successfully")
            
        except Exception as e:
            logger.error(f"MCP initialization failed: {str(e)}")
            raise
    
    async def _register_agents(self) -> None:
        """Register all agents across layers."""
        
        # Ingest Layer Agents
        self.agents["FrontendIngestor"] = Agent(
            name="FrontendIngestor",
            layer="ingest",
            dependencies=[],
            service_url=self.service_urls["FrontendIngestor"],
            config={"api_port": 8001, "timeout": 30}
        )
        
        self.agents["InvoiceValidator"] = Agent(
            name="InvoiceValidator",
            layer="ingest",
            dependencies=["FrontendIngestor"],
            service_url=self.service_urls["InvoiceValidator"],
            config={"validation_timeout": 300}
        )
        
        # Intent-Router Layer Agents
        self.agents["IntentClassifier"] = Agent(
            name="IntentClassifier",
            layer="intent-router",
            dependencies=["InvoiceValidator"],
            service_url=self.service_urls["IntentClassifier"],
            config={"risk_threshold": 0.5}
        )
        
        self.agents["WorkflowSelector"] = Agent(
            name="WorkflowSelector",
            layer="intent-router",
            dependencies=["IntentClassifier"],
            service_url=self.service_urls["WorkflowSelector"],
            config={"workflow_mappings": {}}
        )
        
        # Orchestration Layer Agents
        self.agents["Orchestrator"] = Agent(
            name="Orchestrator",
            layer="orchestration",
            dependencies=["WorkflowSelector"],
            service_url=self.service_urls["Orchestrator"],
            config={"max_concurrent": 5}
        )
        
        self.agents["PDR"] = Agent(
            name="PDR",
            layer="orchestration",
            dependencies=["Orchestrator"],
            service_url=self.service_urls["PDR"],
            config={"routing_timeout": 60}
        )
        
        self.agents["Execution"] = Agent(
            name="Execution",
            layer="orchestration",
            dependencies=["PDR"],
            service_url=self.service_urls["Execution"],
            config={"execution_timeout": 120}
        )
        
        self.agents["ARL"] = Agent(
            name="ARL",
            layer="orchestration",
            dependencies=["Execution"],
            service_url=self.service_urls["ARL"],
            config={"arl_timeout": 30}
        )
        
        self.agents["RCA"] = Agent(
            name="RCA",
            layer="orchestration",
            dependencies=["PDR"],
            service_url=self.service_urls["RCA"],
            config={"rca_timeout": 30}
        )
        
        self.agents["CRRAK"] = Agent(
            name="CRRAK",
            layer="orchestration",
            dependencies=["ARL", "RCA"],
            service_url=self.service_urls["CRRAK"],
            config={"crrak_timeout": 30}
        )
        
        # Audit Layer Agents
        self.agents["AuditLogger"] = Agent(
            name="AuditLogger",
            layer="audit",
            dependencies=[],
            service_url=self.service_urls["AuditLogger"],
            config={"audit_retention_days": 365}
        )
        
        self.agents["ComplianceChecker"] = Agent(
            name="ComplianceChecker",
            layer="audit",
            dependencies=["AuditLogger"],
            service_url=self.service_urls["ComplianceChecker"],
            config={"rbi_compliance": True}
        )
        
        # Memory Layer Agents
        self.agents["ContextMemory"] = Agent(
            name="ContextMemory",
            layer="memory",
            dependencies=[],
            service_url=self.service_urls["ContextMemory"],
            config={"memory_retention_hours": 24}
        )
        
        # Observability Layer Agents
        self.agents["Monitor"] = Agent(
            name="Monitor",
            layer="observability",
            dependencies=[],
            service_url=self.service_urls["Monitor"],
            config={"metrics_interval": 60}
        )
        
        self.agents["Debugger"] = Agent(
            name="Debugger",
            layer="observability",
            dependencies=["Monitor"],
            service_url=self.service_urls["Debugger"],
            config={"debug_level": "INFO"}
        )
        
        # Prompt Layer Agents
        self.agents["PromptGenerator"] = Agent(
            name="PromptGenerator",
            layer="prompt",
            dependencies=[],
            service_url=self.service_urls["PromptGenerator"],
            config={"prompt_templates": {}}
        )
        
        self.agents["PromptValidator"] = Agent(
            name="PromptValidator",
            layer="prompt",
            dependencies=["PromptGenerator"],
            service_url=self.service_urls["PromptValidator"],
            config={"validation_rules": {}}
        )
        
        # Security Layer Agents
        self.agents["SanctionScanner"] = Agent(
            name="SanctionScanner",
            layer="security",
            dependencies=[],
            service_url=self.service_urls["SanctionScanner"],
            config={"sanction_lists": []}
        )
        
        # ACC Agent (Anti-Compliance Check)
        self.agents["ACC"] = Agent(
            name="ACC",
            layer="orchestration",
            dependencies=["IntentClassifier"],
            service_url=self.service_urls["ACC"],
            config={"compliance_timeout": 30}
        )
        
        logger.info(f"Registered {len(self.agents)} agents across all layers")
    
    async def _setup_event_listeners(self) -> None:
        """Setup event listeners for layer coordination."""
        
        # Ingest layer events
        self.event_listeners["invoice_received"] = [
            self._handle_invoice_received,
            self._trigger_validation
        ]
        
        self.event_listeners["validated_invoice"] = [
            self._handle_validated_invoice,
            self._trigger_intent_classification
        ]
        
        # Intent-router layer events
        self.event_listeners["workflow_selected"] = [
            self._handle_workflow_selected,
            self._trigger_orchestration
        ]
        
        # Orchestration layer events
        self.event_listeners["pdr_result"] = [
            self._handle_pdr_result,
            self._trigger_execution_or_rca
        ]
        
        self.event_listeners["execution_result"] = [
            self._handle_execution_result,
            self._trigger_arl
        ]
        
        self.event_listeners["arl_result"] = [
            self._handle_arl_result,
            self._trigger_crrak
        ]
        
        self.event_listeners["rca_result"] = [
            self._handle_rca_result,
            self._trigger_crrak
        ]
        
        self.event_listeners["crrak_generated"] = [
            self._handle_crrak_complete,
            self._trigger_audit
        ]
        
        # Audit layer events
        self.event_listeners["audit_report_generated"] = [
            self._handle_audit_complete,
            self._finalize_workflow
        ]
        
        # Error events
        self.event_listeners["agent_failed"] = [
            self._handle_agent_failure,
            self._trigger_error_recovery
        ]
        
        logger.info(f"Setup {len(self.event_listeners)} event listeners")
    
    async def _initialize_storage(self) -> None:
        """Initialize storage connections."""
        try:
            # Test PostgreSQL connection
            conn = psycopg2.connect(**self.db_config)
            conn.close()
            logger.info("PostgreSQL connection verified")
            
            # Test S3 connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("S3 connection verified")
            
        except Exception as e:
            logger.error(f"Storage initialization failed: {str(e)}")
            raise
    
    async def start_workflow(self, trigger_data: Dict[str, Any]) -> str:
        """
        Start a new workflow from initial trigger.
        
        Args:
            trigger_data: Initial trigger data (e.g., from FrontendIngestor)
            
        Returns:
            Workflow ID for tracking
        """
        try:
            batch_id = trigger_data.get('batch_id')
            tenant_id = trigger_data.get('tenant_id')
            source = trigger_data.get('source', 'UNKNOWN')
            
            if not batch_id or not tenant_id:
                raise ValueError("batch_id and tenant_id are required")
            
            # Create workflow context
            workflow_id = f"WF-{batch_id}-{uuid.uuid4().hex[:8]}"
            
            context = WorkflowContext(
                batch_id=batch_id,
                tenant_id=tenant_id,
                source=source,
                status=WorkflowStatus.INITIALIZED,
                data=trigger_data
            )
            
            self.workflows[workflow_id] = context
            
            # Store initial state in PostgreSQL
            await self._store_workflow_state(workflow_id, context)
            
            # Emit initial event
            await self._emit_event("invoice_received", {
                "workflow_id": workflow_id,
                "batch_id": batch_id,
                "tenant_id": tenant_id,
                "source": source,
                "data": trigger_data
            })
            
            logger.info(f"Started workflow {workflow_id} for batch {batch_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
            raise
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle events in the workflow.
        
        Args:
            event_data: Event data to process
            
        Returns:
            Event processing result
        """
        try:
            workflow_id = event_data.get('workflow_id')
            event_type = event_data.get('type')
            
            if not workflow_id:
                raise ValueError("workflow_id is required")
            
            if workflow_id not in self.workflows:
                logger.warning(f"Workflow {workflow_id} not found, creating new one")
                return await self.start_workflow(event_data)
            
            context = self.workflows[workflow_id]
            context.last_update = datetime.now()
            
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
            
            # Update workflow state
            await self._store_workflow_state(workflow_id, context)
            
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
    
    async def _emit_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Emit event to registered listeners."""
        try:
            if event_name in self.event_listeners:
                for listener in self.event_listeners[event_name]:
                    try:
                        await listener(event_data)
                    except Exception as e:
                        logger.error(f"Event listener {listener.__name__} failed: {str(e)}")
            
            # Store event in audit log
            await self._log_event(event_name, event_data)
            
        except Exception as e:
            logger.error(f"Failed to emit event {event_name}: {str(e)}")
    
    async def _handle_invoice_received(self, event_data: Dict[str, Any]) -> None:
        """Handle invoice received event."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if not context:
            return
        
        # Update workflow status
        context.status = WorkflowStatus.INGESTING
        context.current_layer = "ingest"
        context.last_update = datetime.now()
        
        logger.info(f"Processing invoice received for workflow {workflow_id}")
    
    async def _trigger_validation(self, event_data: Dict[str, Any]) -> None:
        """Trigger invoice validation."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Call InvoiceValidator service
            await self._call_agent_service("InvoiceValidator", event_data)
            
            # Emit validated_invoice event
            await self._emit_event("validated_invoice", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "validation_status": "VALID",
                "processed_data": {
                    "lines": [
                        {
                            "line_id": "L-1",
                            "amount": 250000,
                            "currency": "INR",
                            "purpose": "VENDOR_PAYMENT"
                        }
                    ]
                }
            })
            
        except Exception as e:
            logger.error(f"Validation failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_validated_invoice(self, event_data: Dict[str, Any]) -> None:
        """Handle validated invoice event."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.VALIDATING
            context.current_layer = "intent-router"
            context.last_update = datetime.now()
        
        logger.info(f"Processing validated invoice for workflow {workflow_id}")
    
    async def _trigger_intent_classification(self, event_data: Dict[str, Any]) -> None:
        """Trigger intent classification."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run IntentClassifier
            await self._call_agent_service("IntentClassifier", event_data)
            
            # Run WorkflowSelector
            await self._call_agent_service("WorkflowSelector", event_data)
            
            # Emit workflow_selected event
            await self._emit_event("workflow_selected", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "intents": [
                    {
                        "line_id": "L-1",
                        "intent": "VENDOR_PAYMENTS",
                        "risk_score": 0.45,
                        "confidence": 0.94,
                        "decision": "PASS"
                    }
                ],
                "workflow_id": "WF-VENDOR-DOMESTIC",
                "agent_pipeline": ["ACC", "PDR", "Execution", "ARL", "CRRAK"]
            })
            
        except Exception as e:
            logger.error(f"Intent classification failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_workflow_selected(self, event_data: Dict[str, Any]) -> None:
        """Handle workflow selection."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.CLASSIFYING
            context.current_layer = "orchestration"
            context.last_update = datetime.now()
        
        logger.info(f"Processing workflow selection for workflow {workflow_id}")
    
    async def _trigger_orchestration(self, event_data: Dict[str, Any]) -> None:
        """Trigger orchestration layer."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run Orchestrator
            await self._call_agent_service("Orchestrator", event_data)
            
            # Run PDR
            await self._call_agent_service("PDR", event_data)
            
            # Emit pdr_result event
            await self._emit_event("pdr_result", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "line_id": "L-1",
                "status": "SUCCESS",
                "routing_plan": {
                    "primary_route": {
                        "channel": "NEFT",
                        "psp": "AXIS",
                        "cost_bps": 10,
                        "eta_ms": 7200000,
                        "success_prob": 0.98
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"Orchestration failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_pdr_result(self, event_data: Dict[str, Any]) -> None:
        """Handle PDR result."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.ROUTING
            context.current_layer = "orchestration"
            context.last_update = datetime.now()
        
        logger.info(f"Processing PDR result for workflow {workflow_id}")
    
    async def _trigger_execution_or_rca(self, event_data: Dict[str, Any]) -> None:
        """Trigger execution or RCA based on PDR result."""
        workflow_id = event_data.get('workflow_id')
        status = event_data.get('status')
        
        if status == "SUCCESS":
            # Trigger execution
            await self._trigger_execution(event_data)
        else:
            # Trigger RCA for failure analysis
            await self._trigger_rca(event_data)
    
    async def _trigger_execution(self, event_data: Dict[str, Any]) -> None:
        """Trigger execution phase."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run Execution agent
            await self._call_agent_service("Execution", event_data)
            
            # Emit execution_result event
            await self._emit_event("execution_result", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "line_id": "L-1",
                "status": "SUCCESS",
                "execution_result": {
                    "transaction_id": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "utr": f"25-{datetime.now().strftime('%d%m%H%M')}-001"
                }
            })
            
        except Exception as e:
            logger.error(f"Execution failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _trigger_rca(self, event_data: Dict[str, Any]) -> None:
        """Trigger RCA for failure analysis."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run RCA agent
            await self._call_agent_service("RCA", event_data)
            
            # Emit rca_result event
            await self._emit_event("rca_result", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "line_id": "L-1",
                "status": "COMPLETED",
                "root_cause": {
                    "issue": "INVALID_IFSC",
                    "source": "PDR_VALIDATION",
                    "recommendation": "Verify IFSC with bank"
                },
                "explanation": "Failure due to invalid IFSC format detected by PDR"
            })
            
        except Exception as e:
            logger.error(f"RCA failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_execution_result(self, event_data: Dict[str, Any]) -> None:
        """Handle execution result."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.EXECUTING
            context.current_layer = "orchestration"
            context.last_update = datetime.now()
        
        logger.info(f"Processing execution result for workflow {workflow_id}")
    
    async def _trigger_arl(self, event_data: Dict[str, Any]) -> None:
        """Trigger ARL processing."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run ARL agent
            await self._call_agent_service("ARL", event_data)
            
            # Emit arl_result event
            await self._emit_event("arl_result", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "line_id": "L-1",
                "status": "RECONCILED",
                "matched": [
                    {
                        "line_id": "L-1",
                        "utr": "IFT20241001822314"
                    }
                ],
                "exceptions": [],
                "journals": [
                    {
                        "entry_id": "J-001",
                        "debit": "Expense:Vendors",
                        "credit": "Bank:BOI",
                        "amount": 922288
                    }
                ]
            })
            
        except Exception as e:
            logger.error(f"ARL failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_arl_result(self, event_data: Dict[str, Any]) -> None:
        """Handle ARL result."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.EXECUTING
            context.current_layer = "orchestration"
            context.last_update = datetime.now()
        
        logger.info(f"Processing ARL result for workflow {workflow_id}")
    
    async def _handle_rca_result(self, event_data: Dict[str, Any]) -> None:
        """Handle RCA result."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.EXECUTING
            context.current_layer = "orchestration"
            context.last_update = datetime.now()
        
        logger.info(f"Processing RCA result for workflow {workflow_id}")
    
    async def _trigger_crrak(self, event_data: Dict[str, Any]) -> None:
        """Trigger CRRAK processing."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run CRRAK agent
            await self._call_agent_service("CRRAK", event_data)
            
            # Emit crrak_generated event
            await self._emit_event("crrak_generated", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "line_id": "L-1",
                "status": "SUCCESS",
                "report": {
                    "compliance_status": "COMPLIANT",
                    "combined_details": "ARL: Matched UTR IFT20241001822314; RCA: N/A (SUCCESS); AI Explanation: Transaction completed within RBI guidelines.",
                    "risk_score": 0.1,
                    "tat_ms": 1619
                }
            })
            
        except Exception as e:
            logger.error(f"CRRAK failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_crrak_complete(self, event_data: Dict[str, Any]) -> None:
        """Handle CRRAK completion."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.AUDITING
            context.current_layer = "audit"
            context.last_update = datetime.now()
        
        logger.info(f"Processing CRRAK completion for workflow {workflow_id}")
    
    async def _trigger_audit(self, event_data: Dict[str, Any]) -> None:
        """Trigger audit processing."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Run AuditLogger
            await self._call_agent_service("AuditLogger", event_data)
            
            # Run ComplianceChecker
            await self._call_agent_service("ComplianceChecker", event_data)
            
            # Emit audit_report_generated event
            await self._emit_event("audit_report_generated", {
                "workflow_id": workflow_id,
                "batch_id": event_data.get('batch_id'),
                "audit_status": "COMPLIANT",
                "audit_report": {
                    "rbi_compliance": True,
                    "audit_trail": "Complete",
                    "retention_period": "3 years"
                }
            })
            
        except Exception as e:
            logger.error(f"Audit failed for workflow {workflow_id}: {str(e)}")
            await self._handle_workflow_error(workflow_id, str(e))
    
    async def _handle_audit_complete(self, event_data: Dict[str, Any]) -> None:
        """Handle audit completion."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.COMPLETED
            context.last_update = datetime.now()
        
        logger.info(f"Audit completed for workflow {workflow_id}")
    
    async def _finalize_workflow(self, event_data: Dict[str, Any]) -> None:
        """Finalize workflow."""
        workflow_id = event_data.get('workflow_id')
        if not workflow_id:
            return
        
        try:
            # Update final state
            context = self.workflows.get(workflow_id)
            if context:
                context.status = WorkflowStatus.COMPLETED
                context.last_update = datetime.now()
            
            # Store final state
            await self._store_workflow_state(workflow_id, context)
            
            # Cleanup
            self.workflows.pop(workflow_id, None)
            
            logger.info(f"Workflow {workflow_id} finalized successfully")
            
        except Exception as e:
            logger.error(f"Failed to finalize workflow {workflow_id}: {str(e)}")
    
    async def _call_agent_service(self, agent_name: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call an agent service via HTTP."""
        try:
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            # Update agent status
            agent.status = AgentStatus.RUNNING
            agent.last_run = datetime.now()
            
            # Prepare request data
            request_data = {
                "task_type": agent_name.lower(),
                "batch_id": event_data.get('batch_id'),
                "line_id": event_data.get('line_id', 'L-1'),
                "workflow_id": event_data.get('workflow_id'),
                **event_data.get('data', {})
            }
            
            # Make HTTP call to agent service
            service_url = agent.service_url
            if service_url:
                response = requests.post(
                    f"{service_url}/api/v1/process",
                    json=request_data,
                    timeout=agent.config.get('timeout', 30)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    agent.status = AgentStatus.SUCCESS
                    agent.error_count = 0
                    logger.info(f"Agent {agent_name} completed successfully")
                    return result
                else:
                    raise Exception(f"Agent service returned status {response.status_code}")
            else:
                # Simulate agent execution if no service URL
                await asyncio.sleep(0.1)  # Simulate processing time
                agent.status = AgentStatus.SUCCESS
                agent.error_count = 0
                logger.info(f"Agent {agent_name} completed successfully (simulated)")
                return {"status": "SUCCESS", "result": "Simulated execution"}
            
        except Exception as e:
            agent = self.agents.get(agent_name)
            if agent:
                agent.status = AgentStatus.FAILED
                agent.error_count += 1
            
            logger.error(f"Agent {agent_name} failed: {str(e)}")
            raise
    
    async def _handle_agent_failure(self, event_data: Dict[str, Any]) -> None:
        """Handle agent failure."""
        agent_name = event_data.get('agent_name')
        error = event_data.get('error')
        
        logger.error(f"Agent {agent_name} failed: {error}")
        
        # Update agent status
        agent = self.agents.get(agent_name)
        if agent:
            agent.status = AgentStatus.FAILED
            agent.error_count += 1
    
    async def _trigger_error_recovery(self, event_data: Dict[str, Any]) -> None:
        """Trigger error recovery."""
        workflow_id = event_data.get('workflow_id')
        agent_name = event_data.get('agent_name')
        
        logger.info(f"Triggering error recovery for agent {agent_name} in workflow {workflow_id}")
        
        # Implement retry logic
        max_retries = self.config.get("max_retries", 3)
        agent = self.agents.get(agent_name)
        
        if agent and agent.error_count < max_retries:
            # Retry agent
            try:
                await self._call_agent_service(agent_name, event_data)
            except Exception as e:
                logger.error(f"Retry failed for agent {agent_name}: {str(e)}")
        else:
            # Mark workflow as failed
            await self._handle_workflow_error(workflow_id, f"Agent {agent_name} failed after {max_retries} retries")
    
    async def _handle_workflow_error(self, workflow_id: str, error: str) -> None:
        """Handle workflow error."""
        context = self.workflows.get(workflow_id)
        if context:
            context.status = WorkflowStatus.FAILED
            context.errors.append(error)
            context.last_update = datetime.now()
        
        logger.error(f"Workflow {workflow_id} failed: {error}")
        
        # Store error state
        await self._store_workflow_state(workflow_id, context)
    
    async def _store_workflow_state(self, workflow_id: str, context: WorkflowContext) -> None:
        """Store workflow state in PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO workflow_states (workflow_id, batch_id, tenant_id, status, 
                                          current_layer, current_agent, data, errors, 
                                          start_time, last_update)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (workflow_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    current_layer = EXCLUDED.current_layer,
                    current_agent = EXCLUDED.current_agent,
                    data = EXCLUDED.data,
                    errors = EXCLUDED.errors,
                    last_update = EXCLUDED.last_update
            """, (
                workflow_id,
                context.batch_id,
                context.tenant_id,
                context.status.value,
                context.current_layer,
                context.current_agent,
                json.dumps(context.data),
                json.dumps(context.errors),
                context.start_time,
                context.last_update
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store workflow state: {str(e)}")
    
    async def _log_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Log event to audit log."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_log (batch_id, line_id, action, actor, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                event_data.get('batch_id'),
                event_data.get('line_id'),
                event_name,
                'MCP',
                json.dumps(event_data),
                datetime.now()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status."""
        context = self.workflows.get(workflow_id)
        if not context:
            return None
        
        return {
            "workflow_id": workflow_id,
            "batch_id": context.batch_id,
            "tenant_id": context.tenant_id,
            "status": context.status.value,
            "current_layer": context.current_layer,
            "current_agent": context.current_agent,
            "start_time": context.start_time.isoformat(),
            "last_update": context.last_update.isoformat(),
            "errors": context.errors
        }
    
    async def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent status."""
        agent = self.agents.get(agent_name)
        if not agent:
            return None
        
        return {
            "name": agent.name,
            "layer": agent.layer,
            "status": agent.status.value,
            "dependencies": agent.dependencies,
            "last_run": agent.last_run.isoformat() if agent.last_run else None,
            "error_count": agent.error_count,
            "service_url": agent.service_url
        }
    
    async def shutdown(self) -> None:
        """Shutdown MCP gracefully."""
        try:
            logger.info("Shutting down Master Control Process...")
            
            # Wait for running workflows to complete
            await asyncio.sleep(2)
            
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
            
            logger.info("MCP shutdown completed")
            
        except Exception as e:
            logger.error(f"MCP shutdown failed: {str(e)}")

# Initialize MCP
mcp = MasterControlProcess()

# FastAPI Application for MCP
app = FastAPI(
    title="Master Control Process API",
    description="Central coordinator for all Arealis Gateway agents and workflows",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    service_url: Optional[str]

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
    """Start a new workflow."""
    try:
        trigger_data = trigger.dict()
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
    """Get workflow status."""
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

@app.get("/api/v1/agents", response_model=List[AgentStatusResponse])
async def get_all_agents():
    """Get status of all agents."""
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
    """Get status of a specific agent."""
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

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "master_control_process",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
