"""
Test cases for Intent Manager Bank API Integration
"""

import pytest
import json
from unittest.mock import Mock, patch
from layers.intent_router.intent_manager_bank_api import IntentManagerBankAPI


class TestIntentManagerBankAPI:
    """Test Intent Manager Bank API functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.intent_manager = IntentManagerBankAPI()
        self.sample_bank_data = {
            "batch_id": "B-2025-10-04-01",
            "tenant_id": "ICICI",
            "source": "BANK_API",
            "policy_version": "intent-2.0.0",
            "upload_ts": "2025-10-04T13:06:00Z",
            "lines": [
                {
                    "line_id": "L-1",
                    "transaction_type": "IMPS_P2P",
                    "amount": 25000.0,
                    "currency": "INR",
                    "purpose": "VENDOR_PAYMENT",
                    "DebitAccountDetails": {
                        "DebitAccountInformation": {
                            "debitAccountNumber": "9180190****0605",
                            "debitAccountHolderName": "Company ABC"
                        }
                    },
                    "CreditAccountDetails": {
                        "CreditAccountInformation": {
                            "creditAccountNumber": "2001110****011",
                            "creditMMID": "9229154",
                            "ifscCode": "SIMB0002233",
                            "creditAccountHolderName": "Vendor XYZ"
                        }
                    },
                    "sourceReferenceNumber": "123132128834",
                    "remarks": "Payment for services rendered",
                    "transaction_date": "20251004130600",
                    "service_charge": 50.0,
                    "gst": 4.0,
                    "status": "SUCCESS",
                    "bank_rrn": "52658615",
                    "evidence_ref": "s3://bucket/transactions/B-2025-10-04-01/L-1.json",
                    "bcid": "IBCFli00044"
                }
            ]
        }
    
    def test_process_bank_transactions_success(self):
        """Test successful processing of bank transactions"""
        result = self.intent_manager.process_bank_transactions(self.sample_bank_data)
        
        assert "batch_id" in result
        assert "intents" in result
        assert "workflow_id" in result
        assert result["batch_id"] == "B-2025-10-04-01"
        assert len(result["intents"]) == 1
        
        intent = result["intents"][0]
        assert intent["line_id"] == "L-1"
        assert "intent" in intent
        assert "risk_score" in intent
        assert "confidence" in intent
        assert 0.0 <= intent["risk_score"] <= 1.0
        assert 0.0 <= intent["confidence"] <= 1.0
    
    def test_process_bank_transactions_error(self):
        """Test error handling in bank transaction processing"""
        invalid_data = {"invalid": "data"}
        
        result = self.intent_manager.process_bank_transactions(invalid_data)
        
        assert "error" in result
        assert "timestamp" in result
    
    def test_classify_transaction_intent(self):
        """Test intent classification for single transaction"""
        line = self.sample_bank_data["lines"][0]
        
        result = self.intent_manager._classify_transaction_intent(line, "ICICI")
        
        assert result["line_id"] == "L-1"
        assert result["intent"] in ["VENDOR_PAYMENTS", "UNKNOWN"]
        assert 0.0 <= result["risk_score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0
        assert "axis_validation" in result
        assert "remarks_summary" in result
    
    def test_determine_intent(self):
        """Test intent determination logic"""
        # Test vendor payment
        intent = self.intent_manager._determine_intent("VENDOR_PAYMENT", "Payment to supplier", 50000)
        assert intent == "VENDOR_PAYMENTS"
        
        # Test payroll
        intent = self.intent_manager._determine_intent("SALARY", "Monthly salary", 25000)
        assert intent == "PAYROLL"
        
        # Test amount-based classification
        intent = self.intent_manager._determine_intent("", "", 100000)
        assert intent == "VENDOR_PAYMENTS"  # Large amount
        
        intent = self.intent_manager._determine_intent("", "", 5000)
        assert intent == "UTILITY_PAYMENTS"  # Small amount
    
    def test_calculate_risk_score(self):
        """Test risk score calculation"""
        line = self.sample_bank_data["lines"][0]
        
        # Test normal transaction
        risk_score = self.intent_manager._calculate_risk_score(line, "VENDOR_PAYMENTS", 25000)
        assert 0.0 <= risk_score <= 1.0
        
        # Test high-value transaction
        risk_score = self.intent_manager._calculate_risk_score(line, "VENDOR_PAYMENTS", 2000000)
        assert risk_score > 0.3  # Should be higher risk
        
        # Test unknown intent
        risk_score = self.intent_manager._calculate_risk_score(line, "UNKNOWN", 25000)
        assert risk_score > 0.2  # Unknown intents are risky
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        line = self.sample_bank_data["lines"][0]
        
        # Test with good purpose and remarks
        confidence = self.intent_manager._calculate_confidence(
            line, "VENDOR_PAYMENTS", "VENDOR_PAYMENT", "Payment for services"
        )
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident
        
        # Test with poor purpose and remarks
        confidence = self.intent_manager._calculate_confidence(
            line, "UNKNOWN", "", ""
        )
        assert confidence < 0.5  # Should be less confident
    
    def test_extract_account_info(self):
        """Test account information extraction"""
        line = self.sample_bank_data["lines"][0]
        
        # Test debit account extraction
        debit_info = self.intent_manager._extract_account_info(line, "debit")
        assert debit_info["account_number"] == "9180190****0605"
        assert debit_info["account_holder"] == "Company ABC"
        
        # Test credit account extraction
        credit_info = self.intent_manager._extract_account_info(line, "credit")
        assert credit_info["account_number"] == "2001110****011"
        assert credit_info["account_holder"] == "Vendor XYZ"
        assert credit_info["ifsc_code"] == "SIMB0002233"
        assert credit_info["mmid"] == "9229154"
    
    def test_validate_kyc_completeness(self):
        """Test KYC completeness validation"""
        line = self.sample_bank_data["lines"][0]
        
        result = self.intent_manager.validate_kyc_completeness(line)
        
        assert "debit_kyc_verified" in result
        assert "credit_kyc_verified" in result
        assert "debit_kyc_score" in result
        assert "credit_kyc_score" in result
        assert "evidence_refs" in result
        assert isinstance(result["evidence_refs"], list)
    
    def test_check_sanctions_watchlist(self):
        """Test sanctions and watchlist checking"""
        line = self.sample_bank_data["lines"][0]
        
        result = self.intent_manager.check_sanctions_watchlist(line)
        
        assert "sanctions_clear" in result
        assert "sanctions_score" in result
        assert "matched_entities" in result
        assert "evidence_refs" in result
        assert isinstance(result["matched_entities"], list)
    
    def test_validate_transaction_limits(self):
        """Test transaction limits validation"""
        line = self.sample_bank_data["lines"][0]
        
        result = self.intent_manager.validate_transaction_limits(line, "ICICI")
        
        assert "within_limits" in result
        assert "limit_amount" in result
        assert "transaction_amount" in result
        assert "limit_utilization" in result
        assert 0.0 <= result["limit_utilization"] <= 1.0
    
    def test_validate_ifsc_account(self):
        """Test IFSC and account validation"""
        line = self.sample_bank_data["lines"][0]
        
        result = self.intent_manager.validate_ifsc_account(line)
        
        assert "ifsc_valid" in result
        assert "account_valid" in result
        assert "ifsc_code" in result
        assert "account_number" in result
        assert "bank_code" in result
    
    def test_validate_purpose_code(self):
        """Test purpose code validation"""
        line = self.sample_bank_data["lines"][0]
        
        result = self.intent_manager.validate_purpose_code(line, "VENDOR_PAYMENTS")
        
        assert "purpose_valid" in result
        assert "purpose_code" in result
        assert "allowed_codes" in result
        assert "intent" in result
        assert isinstance(result["allowed_codes"], list)
    
    def test_determine_workflow(self):
        """Test workflow determination"""
        intents = [
            {"intent": "VENDOR_PAYMENTS"},
            {"intent": "VENDOR_PAYMENTS"},
            {"intent": "PAYROLL"}
        ]
        
        workflow = self.intent_manager._determine_workflow(intents)
        assert workflow == "WF-VENDOR-DOMESTIC"  # Most common intent
        
        # Test empty intents
        workflow = self.intent_manager._determine_workflow([])
        assert workflow == "WF-DEFAULT"
    
    def test_is_amount_reasonable_for_intent(self):
        """Test amount reasonableness for different intents"""
        # Test vendor payment
        assert self.intent_manager._is_amount_reasonable_for_intent("VENDOR_PAYMENTS", 50000)
        assert not self.intent_manager._is_amount_reasonable_for_intent("VENDOR_PAYMENTS", 50)  # Too small
        
        # Test payroll
        assert self.intent_manager._is_amount_reasonable_for_intent("PAYROLL", 25000)
        assert not self.intent_manager._is_amount_reasonable_for_intent("PAYROLL", 1000000)  # Too large
        
        # Test utility payments
        assert self.intent_manager._is_amount_reasonable_for_intent("UTILITY_PAYMENTS", 5000)
        assert not self.intent_manager._is_amount_reasonable_for_intent("UTILITY_PAYMENTS", 100000)  # Too large
    
    def test_create_remarks_summary(self):
        """Test remarks summary creation"""
        summary = self.intent_manager._create_remarks_summary(
            "VENDOR_PAYMENT", "Payment for services rendered", "VENDOR_PAYMENTS"
        )
        assert "VENDOR_PAYMENT" in summary
        assert "Payment for services" in summary
        
        # Test with only purpose
        summary = self.intent_manager._create_remarks_summary("SALARY", "", "PAYROLL")
        assert summary == "SALARY"
        
        # Test with only remarks
        summary = self.intent_manager._create_remarks_summary("", "Monthly salary payment", "PAYROLL")
        assert "Monthly salary payment" in summary
    
    def test_extract_bank_validation(self):
        """Test bank validation extraction"""
        line = {
            "line_id": "L-1",
            "code": "00",
            "result": "Success",
            "utrNumber": "25-1905****18-1",
            "bank_rrn": "52658615"
        }
        
        validation = self.intent_manager._extract_bank_validation(line)
        
        assert "code" in validation
        assert "result" in validation
        assert "utrNumber" in validation
        assert "bank_rrn" in validation


if __name__ == "__main__":
    pytest.main([__file__])
