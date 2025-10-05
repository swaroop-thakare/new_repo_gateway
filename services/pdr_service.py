#!/usr/bin/env python3
"""
Payment Decision Router (PDR) Service
Handles rail selection and execution logic
"""

import asyncio
import logging
import boto3
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="PDR Service",
    description="Payment Decision Router Service for Arealis Gateway v2",
    version="1.0.0"
)

class PDRRequest(BaseModel):
    """PDR processing request model"""
    transaction_id: str
    amount: float
    beneficiary: str
    rail_preferences: List[str] = ["IMPS", "NEFT", "RTGS", "UPI"]
    priority: str = "normal"  # normal, high, urgent

class PDRResponse(BaseModel):
    """PDR processing response model"""
    transaction_id: str
    selected_rail: str
    confidence_score: float
    estimated_time: str
    cost: float
    status: str
    reasoning: str

class PDRService:
    """Payment Decision Router Service."""

    def __init__(self):
        """Initialize PDR service."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = "arealis-invoices"
        
        # Rail performance data (mock)
        self.rail_performance = {
            "IMPS": {"success_rate": 0.95, "avg_time": "2-5 min", "cost": 5.0},
            "NEFT": {"success_rate": 0.98, "avg_time": "30 min - 2 hours", "cost": 2.0},
            "RTGS": {"success_rate": 0.99, "avg_time": "30 min - 2 hours", "cost": 25.0},
            "UPI": {"success_rate": 0.97, "avg_time": "1-3 min", "cost": 0.0}
        }

    async def select_rail(self, request: PDRRequest) -> PDRResponse:
        """Select optimal rail for transaction."""
        try:
            logger.info(f"PDR: Processing rail selection for transaction {request.transaction_id}")
            
            # Rail selection logic
            selected_rail = self._select_optimal_rail(request)
            rail_data = self.rail_performance[selected_rail]
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(request, selected_rail)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(request, selected_rail, confidence_score)
            
            result = PDRResponse(
                transaction_id=request.transaction_id,
                selected_rail=selected_rail,
                confidence_score=confidence_score,
                estimated_time=rail_data["avg_time"],
                cost=rail_data["cost"],
                status="SELECTED",
                reasoning=reasoning
            )
            
            logger.info(f"PDR: Selected rail {selected_rail} for transaction {request.transaction_id}")
            return result

        except Exception as e:
            logger.error(f"PDR rail selection failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _select_optimal_rail(self, request: PDRRequest) -> str:
        """Select optimal rail based on transaction characteristics."""
        amount = request.amount
        
        # Rail selection logic based on amount and preferences
        if amount <= 2000:
            # Small amounts - prefer UPI or IMPS
            if "UPI" in request.rail_preferences:
                return "UPI"
            elif "IMPS" in request.rail_preferences:
                return "IMPS"
        elif amount <= 200000:
            # Medium amounts - prefer IMPS or NEFT
            if "IMPS" in request.rail_preferences:
                return "IMPS"
            elif "NEFT" in request.rail_preferences:
                return "NEFT"
        else:
            # Large amounts - prefer RTGS or NEFT
            if "RTGS" in request.rail_preferences:
                return "RTGS"
            elif "NEFT" in request.rail_preferences:
                return "NEFT"
        
        # Fallback to first preference
        return request.rail_preferences[0] if request.rail_preferences else "IMPS"

    def _calculate_confidence(self, request: PDRRequest, selected_rail: str) -> float:
        """Calculate confidence score for rail selection."""
        base_confidence = self.rail_performance[selected_rail]["success_rate"]
        
        # Adjust based on amount
        if request.amount <= 2000:
            confidence_boost = 0.05  # Higher confidence for small amounts
        elif request.amount <= 200000:
            confidence_boost = 0.0
        else:
            confidence_boost = -0.02  # Slightly lower for large amounts
        
        # Adjust based on priority
        if request.priority == "urgent":
            confidence_boost += 0.03
        elif request.priority == "high":
            confidence_boost += 0.01
        
        return min(1.0, max(0.0, base_confidence + confidence_boost))

    def _generate_reasoning(self, request: PDRRequest, selected_rail: str, confidence: float) -> str:
        """Generate reasoning for rail selection."""
        rail_data = self.rail_performance[selected_rail]
        
        reasoning_parts = [
            f"Selected {selected_rail} based on transaction amount of ₹{request.amount:,.2f}",
            f"Success rate: {rail_data['success_rate']*100:.1f}%",
            f"Estimated time: {rail_data['avg_time']}",
            f"Cost: ₹{rail_data['cost']:.2f}",
            f"Confidence: {confidence*100:.1f}%"
        ]
        
        if request.priority == "urgent":
            reasoning_parts.append("Priority: Urgent - fastest rail selected")
        elif request.priority == "high":
            reasoning_parts.append("Priority: High - reliable rail selected")
        
        return " | ".join(reasoning_parts)

# Initialize service
pdr_service = PDRService()

@app.post("/api/v1/process", response_model=PDRResponse)
async def process_rail_selection(request: PDRRequest):
    """Process rail selection for a transaction."""
    try:
        result = await pdr_service.select_rail(request)
        return result
    except Exception as e:
        logger.error(f"PDR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pdr_service",
        "version": "1.0.0",
        "rails_available": list(pdr_service.rail_performance.keys())
    }

@app.get("/api/v1/rails")
async def get_rail_info():
    """Get available rails and their performance data."""
    return {
        "rails": pdr_service.rail_performance,
        "selection_criteria": {
            "amount_based": {
                "small": "≤ ₹2,000 - UPI/IMPS preferred",
                "medium": "₹2,000 - ₹2,00,000 - IMPS/NEFT preferred", 
                "large": "> ₹2,00,000 - RTGS/NEFT preferred"
            },
            "priority_based": {
                "urgent": "Fastest rail selected",
                "high": "Reliable rail selected",
                "normal": "Cost-optimized rail selected"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
