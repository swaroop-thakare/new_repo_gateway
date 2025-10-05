"""
Test cases for RCA Service
"""

import pytest
import json
from unittest.mock import Mock, patch
from services.rca.main import RCAService, RCATaskRequest, RCAResult


class TestRCAService:
    """Test RCA service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.rca_service = RCAService()
        self.sample_request = RCATaskRequest(
            task_type="rca",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            status="FAILED",
            issues=["INVALID_IFSC"],
            evidence_ref="s3://bucket/invoices/B-2025-10-04-01/L-1/pdr.json"
        )
    
    @pytest.mark.asyncio
    async def test_analyze_failure_success(self):
        """Test successful failure analysis"""
        with patch.object(self.rca_service, '_fetch_failure_data') as mock_fetch, \
             patch.object(self.rca_service, '_store_rca_result') as mock_store:
            
            mock_fetch.return_value = {
                'pdr_result': {'status': 'FAILED', 'issues': ['INVALID_IFSC']},
                'acc_decision': {'decision': 'PASS', 'risk_score': 10.0}
            }
            
            result = await self.rca_service.analyze_failure(self.sample_request)
            
            assert result.task_type == "rca_result"
            assert result.batch_id == "B-2025-10-04-01"
            assert result.line_id == "L-1"
            assert result.status == "COMPLETED"
            assert result.root_cause is not None
            assert result.root_cause.issue == "INVALID_IFSC"
            assert result.root_cause.source == "PDR_VALIDATION"
    
    @pytest.mark.asyncio
    async def test_analyze_failure_error(self):
        """Test failure analysis with error"""
        with patch.object(self.rca_service, '_fetch_failure_data') as mock_fetch:
            mock_fetch.side_effect = Exception("Database error")
            
            result = await self.rca_service.analyze_failure(self.sample_request)
            
            assert result.status == "FAILED"
            assert "error" in result.analysis_details
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        failure_data = {
            'pdr_result': {'status': 'FAILED'},
            'acc_decision': {'decision': 'PASS'},
            'invoice_data': {'amount': 250000}
        }
        
        confidence = self.rca_service._calculate_confidence("INVALID_IFSC", failure_data)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be high with good evidence
    
    def test_analyze_generic_failure(self):
        """Test generic failure analysis"""
        failure_data = {
            'pdr_result': {
                'routing_plan': {
                    'primary_route': {'channel': 'NEFT'}
                }
            }
        }
        
        root_cause = self.rca_service._analyze_generic_failure(
            self.sample_request, failure_data
        )
        
        assert root_cause is not None
        assert root_cause.issue == "RAIL_FAILURE"
        assert root_cause.source == "PDR_EXECUTION"


if __name__ == "__main__":
    pytest.main([__file__])
