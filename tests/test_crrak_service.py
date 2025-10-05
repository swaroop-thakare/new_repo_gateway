"""
Test cases for CRRAK Service
"""

import pytest
import json
from unittest.mock import Mock, patch
from services.crrak.main import CRRAKService, CRRAKTaskRequest, CRRAKResult


class TestCRRAKService:
    """Test CRRAK service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.crrak_service = CRRAKService()
        self.sample_request = CRRAKTaskRequest(
            task_type="crrak",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            status="COMPLETED",
            evidence_ref="s3://bucket/invoices/B-2025-10-04-01/L-1/completed.json"
        )
    
    @pytest.mark.asyncio
    async def test_generate_crrak_success(self):
        """Test successful CRRAK generation"""
        with patch.object(self.crrak_service, '_fetch_transaction_data') as mock_fetch, \
             patch.object(self.crrak_service, '_store_crrak_report') as mock_store:
            
            mock_fetch.return_value = {
                'pdr_result': {'status': 'SUCCESS', 'routing_plan': {'primary_route': {'channel': 'NEFT'}}},
                'acc_decision': {'decision': 'PASS', 'risk_score': 10.0},
                'invoice_data': {'amount': 250000, 'currency': 'INR'}
            }
            
            result = await self.crrak_service.generate_crrak(self.sample_request)
            
            assert result.task_type == "crrak_generated"
            assert result.batch_id == "B-2025-10-04-01"
            assert result.line_id == "L-1"
            assert result.status == "SUCCESS"
            assert result.report is not None
            assert result.report.compliance_status is not None
            assert result.report.risk_assessment is not None
    
    @pytest.mark.asyncio
    async def test_generate_crrak_error(self):
        """Test CRRAK generation with error"""
        with patch.object(self.crrak_service, '_fetch_transaction_data') as mock_fetch:
            mock_fetch.side_effect = Exception("S3 error")
            
            result = await self.crrak_service.generate_crrak(self.sample_request)
            
            assert result.status == "FAILED"
            assert "error" in result.generation_details
    
    @pytest.mark.asyncio
    async def test_assess_compliance(self):
        """Test compliance assessment"""
        transaction_data = {
            'acc_decision': {'decision': 'PASS', 'risk_score': 10.0},
            'counterparty_data': {'kyc_verified': True, 'credit_score': 750},
            'invoice_data': {'amount': 250000}
        }
        
        compliance = await self.crrak_service._assess_compliance(transaction_data)
        
        assert compliance.status == "COMPLIANT"
        assert compliance.sanctions_check is True
        assert compliance.kyc_verified is True
        assert compliance.compliance_score > 80.0
    
    @pytest.mark.asyncio
    async def test_assess_risk(self):
        """Test risk assessment"""
        transaction_data = {
            'invoice_data': {'amount': 250000},
            'counterparty_data': {'kyc_verified': True, 'credit_score': 750},
            'pdr_result': {'status': 'SUCCESS'}
        }
        
        risk = await self.crrak_service._assess_risk(transaction_data)
        
        assert 0.0 <= risk.overall_risk_score <= 100.0
        assert 0.0 <= risk.transaction_risk <= 100.0
        assert 0.0 <= risk.counterparty_risk <= 100.0
        assert 0.0 <= risk.operational_risk <= 100.0
    
    @pytest.mark.asyncio
    async def test_build_audit_trail(self):
        """Test audit trail building"""
        transaction_data = {
            'pdr_result': {'timestamp': '2025-10-04T13:14:00Z', 'status': 'SUCCESS'},
            'acc_decision': {'timestamp': '2025-10-04T13:13:00Z', 'decision': 'PASS'}
        }
        
        audit_trail = await self.crrak_service._build_audit_trail(
            self.sample_request, transaction_data
        )
        
        assert len(audit_trail) > 0
        assert any(entry['action'] == 'INVOICE_CREATED' for entry in audit_trail)
        assert any(entry['action'] == 'PDR_DECISION' for entry in audit_trail)
        assert any(entry['action'] == 'ACC_DECISION' for entry in audit_trail)


if __name__ == "__main__":
    pytest.main([__file__])
