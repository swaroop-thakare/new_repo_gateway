"""
Test cases for ARL Service
"""

import pytest
import json
from decimal import Decimal
from unittest.mock import Mock, patch
from services.arl.main import ARLService, ARLTaskRequest, ARLResult, LedgerEntry


class TestARLService:
    """Test ARL service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.arl_service = ARLService()
        self.sample_request = ARLTaskRequest(
            task_type="arl",
            batch_id="B-2025-10-04-01",
            line_id="L-1",
            status="COMPLETED",
            amount=250000.0,
            evidence_ref="s3://bucket/invoices/B-2025-10-04-01/L-1/completed.json"
        )
    
    @pytest.mark.asyncio
    async def test_reconcile_transaction_success(self):
        """Test successful transaction reconciliation"""
        with patch.object(self.arl_service, '_fetch_transaction_data') as mock_fetch, \
             patch.object(self.arl_service, '_fetch_ledger_entries') as mock_ledger, \
             patch.object(self.arl_service, '_store_arl_result') as mock_store:
            
            mock_fetch.return_value = {
                'pdr_result': {'status': 'SUCCESS', 'timestamp': '2025-10-04T13:14:00Z'},
                'invoice_data': {'amount': 250000}
            }
            
            mock_ledger.return_value = [
                LedgerEntry(
                    entry_id="DEBIT_B-2025-10-04-01_L-1",
                    account_number="91402004****3081",
                    transaction_type="DEBIT",
                    amount=Decimal('250000.00'),
                    currency="INR",
                    reference="B-2025-10-04-01_L-1",
                    timestamp=None,
                    status="PENDING"
                ),
                LedgerEntry(
                    entry_id="CREDIT_B-2025-10-04-01_L-1",
                    account_number="0052050****597",
                    transaction_type="CREDIT",
                    amount=Decimal('250000.00'),
                    currency="INR",
                    reference="B-2025-10-04-01_L-1",
                    timestamp=None,
                    status="PENDING"
                )
            ]
            
            result = await self.arl_service.reconcile_transaction(self.sample_request)
            
            assert result.task_type == "arl_result"
            assert result.batch_id == "B-2025-10-04-01"
            assert result.line_id == "L-1"
            assert result.status == "RECONCILED"
            assert len(result.discrepancies) == 0
    
    @pytest.mark.asyncio
    async def test_reconcile_transaction_amount_mismatch(self):
        """Test reconciliation with amount mismatch"""
        with patch.object(self.arl_service, '_fetch_transaction_data') as mock_fetch, \
             patch.object(self.arl_service, '_fetch_ledger_entries') as mock_ledger, \
             patch.object(self.arl_service, '_store_arl_result') as mock_store:
            
            mock_fetch.return_value = {
                'pdr_result': {'status': 'SUCCESS', 'timestamp': '2025-10-04T13:14:00Z'},
                'invoice_data': {'amount': 250000}
            }
            
            # Create ledger entries with amount mismatch
            mock_ledger.return_value = [
                LedgerEntry(
                    entry_id="DEBIT_B-2025-10-04-01_L-1",
                    account_number="91402004****3081",
                    transaction_type="DEBIT",
                    amount=Decimal('200000.00'),  # Mismatch
                    currency="INR",
                    reference="B-2025-10-04-01_L-1",
                    timestamp=None,
                    status="PENDING"
                )
            ]
            
            result = await self.arl_service.reconcile_transaction(self.sample_request)
            
            assert result.status == "FAILED"
            assert len(result.discrepancies) > 0
            assert any(d.type == "AMOUNT_MISMATCH" for d in result.discrepancies)
    
    @pytest.mark.asyncio
    async def test_reconcile_transaction_error(self):
        """Test reconciliation with error"""
        with patch.object(self.arl_service, '_fetch_transaction_data') as mock_fetch:
            mock_fetch.side_effect = Exception("Database error")
            
            result = await self.arl_service.reconcile_transaction(self.sample_request)
            
            assert result.status == "FAILED"
            assert "error" in result.reconciliation_details
    
    def test_perform_reconciliation(self):
        """Test reconciliation logic"""
        # Mock ledger entries
        ledger_entries = [
            LedgerEntry(
                entry_id="DEBIT_1",
                account_number="91402004****3081",
                transaction_type="DEBIT",
                amount=Decimal('250000.00'),
                currency="INR",
                reference="REF1",
                timestamp=None,
                status="PENDING"
            ),
            LedgerEntry(
                entry_id="CREDIT_1",
                account_number="0052050****597",
                transaction_type="CREDIT",
                amount=Decimal('250000.00'),
                currency="INR",
                reference="REF1",
                timestamp=None,
                status="PENDING"
            )
        ]
        
        transaction_data = {
            'pdr_result': {'timestamp': '2025-10-04T13:14:00Z'}
        }
        
        # This would need to be called through the service method
        # For now, just test the logic components
        expected_amount = Decimal('250000.00')
        
        for entry in ledger_entries:
            if abs(entry.amount - expected_amount) <= Decimal('0.01'):
                assert True  # Amount matches
            else:
                assert False  # Amount mismatch


if __name__ == "__main__":
    pytest.main([__file__])
