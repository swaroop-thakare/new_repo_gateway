"""
PDR Agent (Payment Decision Router) Service
FastAPI service implementing the sophisticated rail selection and execution logic.
"""

import os
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import requests

from models import (
    Intent, PDRRequest, PDRResponse, PDRDecision, RailExecutionRequest,
    RailExecutionResponse, ACCDecision, ExecutionStatus, IntentStatus,
    FallbackRail, ScoringWeights
)
from database import db_manager
from scoring_engine import RailScoringEngine
from mock_rail_apis import MockRailAPIs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PDR Agent",
    description="Payment Decision Router with sophisticated rail selection",
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

# Initialize components
scoring_engine = RailScoringEngine()
mock_rail_apis = MockRailAPIs()

# ACC service configuration
ACC_SERVICE_URL = os.getenv('ACC_SERVICE_URL', 'http://localhost:8000')


class PDRService:
    """Main PDR service orchestrating the rail selection and execution"""
    
    def __init__(self):
        self.scoring_engine = RailScoringEngine()
        self.mock_rail_apis = MockRailAPIs()
    
    async def process_intents(self, request: PDRRequest) -> PDRResponse:
        """Process payment intents and generate PDR decisions"""
        start_time = time.time()
        decisions = []
        successful_count = 0
        failed_count = 0
        
        for intent in request.intents:
            try:
                # Update intent status to processing
                db_manager.update_intent_status(intent.transaction_id, IntentStatus.PROCESSING)
                
                # Get or create ACC decision
                acc_decision = await self._get_acc_decision(intent)
                
                # Generate PDR decision
                pdr_decision = await self._generate_pdr_decision(
                    intent, acc_decision, request.scoring_weights
                )
                
                # Save PDR decision
                db_manager.save_pdr_decision(pdr_decision)
                
                decisions.append(pdr_decision)
                successful_count += 1
                
                logger.info(f"Generated PDR decision for {intent.transaction_id}: {pdr_decision.primary_rail}")
                
            except Exception as e:
                logger.error(f"Failed to process intent {intent.transaction_id}: {e}")
                failed_count += 1
                
                # Create error decision
                error_decision = PDRDecision(
                    transaction_id=intent.transaction_id,
                    primary_rail="ERROR",
                    primary_rail_score=0.0,
                    execution_status=ExecutionStatus.FAILED
                )
                decisions.append(error_decision)
        
        processing_time = (time.time() - start_time) * 1000
        
        return PDRResponse(
            decisions=decisions,
            total_processed=len(request.intents),
            total_successful=successful_count,
            total_failed=failed_count,
            processing_time_ms=processing_time
        )
    
    async def execute_rail_decision(self, transaction_id: str) -> RailExecutionResponse:
        """Execute the rail decision for a transaction"""
        # Get PDR decision
        pdr_decision = db_manager.get_pdr_decision(transaction_id)
        if not pdr_decision:
            raise HTTPException(status_code=404, detail="PDR decision not found")
        
        # Get intent
        intent = db_manager.get_intent_by_transaction_id(transaction_id)
        if not intent:
            raise HTTPException(status_code=404, detail="Intent not found")
        
        # Update execution status
        db_manager.update_pdr_execution_status(
            transaction_id, ExecutionStatus.EXECUTING
        )
        
        # Try primary rail first, then fallbacks
        rails_to_try = [pdr_decision.primary_rail] + [fb.rail_name for fb in pdr_decision.fallback_rails]
        
        for attempt, rail_name in enumerate(rails_to_try):
            try:
                logger.info(f"Attempting {rail_name} for {transaction_id} (attempt {attempt + 1})")
                
                # Update current attempt
                db_manager.update_pdr_execution_status(
                    transaction_id, ExecutionStatus.EXECUTING,
                    current_rail_attempt=rail_name,
                    attempt_count=attempt + 1
                )
                
                # Execute rail
                rail_request = RailExecutionRequest(
                    transaction_id=transaction_id,
                    rail_name=rail_name,
                    intent=intent,
                    retry_attempt=attempt
                )
                
                result = self.mock_rail_apis.execute_rail(rail_request)
                
                # Save performance data
                self._save_rail_performance(rail_request, result)
                
                if result.success:
                    # Success! Update final status
                    db_manager.update_pdr_execution_status(
                        transaction_id, ExecutionStatus.SUCCESS,
                        final_rail_used=rail_name,
                        final_utr_number=result.utr_number,
                        final_status=ExecutionStatus.SUCCESS
                    )
                    
                    # Update intent status
                    db_manager.update_intent_status(transaction_id, IntentStatus.COMPLETED)
                    
                    logger.info(f"Successfully executed {rail_name} for {transaction_id}: {result.utr_number}")
                    return result
                else:
                    logger.warning(f"Rail {rail_name} failed for {transaction_id}: {result.error_message}")
                    # Continue to next rail
                    
            except Exception as e:
                logger.error(f"Error executing {rail_name} for {transaction_id}: {e}")
                # Continue to next rail
        
        # All rails failed
        db_manager.update_pdr_execution_status(
            transaction_id, ExecutionStatus.FAILED,
            final_status=ExecutionStatus.FAILED
        )
        
        db_manager.update_intent_status(transaction_id, IntentStatus.FAILED)
        
        raise HTTPException(
            status_code=500, 
            detail="All rails failed for this transaction"
        )
    
    async def _get_acc_decision(self, intent: Intent) -> ACCDecision:
        """Get ACC decision for an intent"""
        # First check if we already have an ACC decision
        existing_decision = db_manager.get_acc_decision(intent.transaction_id)
        if existing_decision:
            return existing_decision
        
        # Call ACC service
        try:
            acc_response = requests.post(
                f"{ACC_SERVICE_URL}/acc/decide",
                json=[intent.dict()],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if acc_response.status_code == 200:
                acc_data = acc_response.json()
                if acc_data.get('decisions') and len(acc_data['decisions']) > 0:
                    decision_data = acc_data['decisions'][0]
                    
                    acc_decision = ACCDecision(
                        transaction_id=intent.transaction_id,
                        line_id=decision_data.get('line_id', intent.transaction_id),
                        decision=decision_data['decision'],
                        policy_version=decision_data.get('policy_version', 'unknown'),
                        reasons=decision_data.get('reasons', []),
                        evidence_refs=decision_data.get('evidence_refs', []),
                        compliance_penalty=decision_data.get('compliance_penalty', 0.0),
                        risk_score=decision_data.get('risk_score', 0.0)
                    )
                    
                    # Save ACC decision
                    db_manager.save_acc_decision(acc_decision)
                    return acc_decision
            
            # ACC service failed, create default PASS decision
            logger.warning(f"ACC service failed for {intent.transaction_id}, using default PASS")
            
        except Exception as e:
            logger.error(f"Error calling ACC service for {intent.transaction_id}: {e}")
        
        # Create default ACC decision
        default_decision = ACCDecision(
            transaction_id=intent.transaction_id,
            line_id=intent.transaction_id,
            decision="PASS",
            policy_version="default",
            compliance_penalty=10.0,  # Small penalty for missing ACC
            risk_score=5.0
        )
        
        db_manager.save_acc_decision(default_decision)
        return default_decision
    
    async def _generate_pdr_decision(
        self, 
        intent: Intent, 
        acc_decision: ACCDecision,
        custom_weights: Optional[ScoringWeights] = None
    ) -> PDRDecision:
        """Generate PDR decision using scoring engine"""
        
        # Use custom weights if provided
        if custom_weights:
            self.scoring_engine.weights = custom_weights
        
        # Get available rails
        available_rails = db_manager.get_active_rails()
        
        # Run scoring engine
        scored_rails, filter_reasons = self.scoring_engine.select_rails(
            intent, available_rails, acc_decision
        )
        
        if not scored_rails:
            raise Exception(f"No eligible rails found. Reasons: {filter_reasons}")
        
        # Create PDR decision
        primary_rail = scored_rails[0]
        fallback_rails = [
            FallbackRail(rail_name=rail.rail_name, score=rail.score)
            for rail in scored_rails[1:]
        ]
        
        # Get explainability report
        explainability = self.scoring_engine.get_explainability_report(scored_rails)
        
        pdr_decision = PDRDecision(
            transaction_id=intent.transaction_id,
            primary_rail=primary_rail.rail_name,
            primary_rail_score=primary_rail.score,
            fallback_rails=fallback_rails,
            scoring_features=explainability,
            scoring_weights=self.scoring_engine.weights,
            execution_status=ExecutionStatus.PENDING
        )
        
        return pdr_decision
    
    def _save_rail_performance(self, request: RailExecutionRequest, result: RailExecutionResponse):
        """Save rail performance data"""
        from models import RailPerformance
        
        performance = RailPerformance(
            rail_name=request.rail_name,
            transaction_id=request.transaction_id,
            actual_eta_ms=result.execution_time_ms,
            success=result.success,
            error_code=result.error_code,
            error_message=result.error_message,
            initiated_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        db_manager.save_rail_performance(performance)


# Initialize service
pdr_service = PDRService()


# ========================================
# API Endpoints
# ========================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "PDR Agent",
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    db_healthy = db_manager.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/pdr/decide", response_model=PDRResponse)
async def decide_rails(request: PDRRequest):
    """Generate PDR decisions for payment intents"""
    return await pdr_service.process_intents(request)

@app.post("/pdr/execute/{transaction_id}", response_model=RailExecutionResponse)
async def execute_transaction(transaction_id: str):
    """Execute a transaction using PDR decision"""
    return await pdr_service.execute_rail_decision(transaction_id)

@app.get("/pdr/decision/{transaction_id}")
async def get_pdr_decision(transaction_id: str):
    """Get PDR decision for a transaction"""
    decision = db_manager.get_pdr_decision(transaction_id)
    if not decision:
        raise HTTPException(status_code=404, detail="PDR decision not found")
    return decision

@app.get("/pdr/intent/{transaction_id}")
async def get_intent(transaction_id: str):
    """Get intent for a transaction"""
    intent = db_manager.get_intent_by_transaction_id(transaction_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent

@app.get("/pdr/rails")
async def get_rails():
    """Get all active rail configurations"""
    return db_manager.get_active_rails()

@app.get("/pdr/rails/{rail_name}/stats")
async def get_rail_stats(rail_name: str, days: int = 30):
    """Get performance statistics for a rail"""
    stats = db_manager.get_rail_performance_stats(rail_name, days)
    return stats

@app.get("/pdr/pending")
async def get_pending_intents(limit: int = 100):
    """Get pending intents for processing"""
    return db_manager.get_pending_intents(limit)

@app.post("/pdr/process-pending")
async def process_pending_intents(background_tasks: BackgroundTasks, limit: int = 100):
    """Process pending intents in background"""
    
    async def process_background():
        pending_intents = db_manager.get_pending_intents(limit)
        if pending_intents:
            request = PDRRequest(intents=pending_intents)
            result = await pdr_service.process_intents(request)
            logger.info(f"Processed {result.total_processed} pending intents")
    
    background_tasks.add_task(process_background)
    return {"message": f"Processing up to {limit} pending intents in background"}

@app.get("/pdr/mock-stats")
async def get_mock_rail_stats():
    """Get mock rail API statistics"""
    return mock_rail_apis.get_statistics()

@app.post("/pdr/setup-database")
async def setup_database():
    """Setup database schema (development only)"""
    try:
        schema_file = "/workspace/services/pdr/database_schema.sql"
        db_manager.execute_schema_file(schema_file)
        return {"message": "Database schema setup completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database setup failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)