"""
Intent Manager v2 - Bank API Integration (Intent-Only Focus)

Analyzes bank-provided transaction data (e.g., from ICICI IMPS or Axis NEFT responses) 
to classify intents (e.g., "VENDOR_PAYMENTS", "PAYROLL") and set workflows. 

Focus: Intent classification for downstream agents, not full compliance or routing.
"""

import json
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentManagerBankAPI:
    """
    Intent Manager v2 for Bank API Integration.
    
    Focuses on intent classification from bank transaction data without
    full compliance or routing decisions.
    """
    
    def __init__(self):
        """Initialize Intent Manager with bank API configuration."""
        
        # Intent classification mappings for bank transactions
        self.intent_mappings = {
            # Vendor payments
            "VENDOR_PAYMENT": "VENDOR_PAYMENTS",
            "SUPPLIER_PAYMENT": "VENDOR_PAYMENTS", 
            "SERVICE_PAYMENT": "VENDOR_PAYMENTS",
            "CONTRACTOR_PAYMENT": "VENDOR_PAYMENTS",
            "VENDOR": "VENDOR_PAYMENTS",
            "SUPPLIER": "VENDOR_PAYMENTS",
            
            # Payroll
            "PAYROLL": "PAYROLL",
            "SALARY": "PAYROLL",
            "WAGES": "PAYROLL",
            "EMPLOYEE_PAYMENT": "PAYROLL",
            "STAFF_SALARY": "PAYROLL",
            
            # Tax payments
            "TAX_PAYMENT": "TAX_PAYMENTS",
            "GST_PAYMENT": "TAX_PAYMENTS",
            "INCOME_TAX": "TAX_PAYMENTS",
            "TDS_PAYMENT": "TAX_PAYMENTS",
            
            # Utility payments
            "UTILITY_PAYMENT": "UTILITY_PAYMENTS",
            "ELECTRICITY": "UTILITY_PAYMENTS",
            "WATER": "UTILITY_PAYMENTS",
            "GAS": "UTILITY_PAYMENTS",
            "INTERNET": "UTILITY_PAYMENTS",
            
            # Loan disbursements
            "LOAN_DISBURSEMENT": "LOAN_DISBURSEMENTS",
            "LOAN": "LOAN_DISBURSEMENTS",
            "CREDIT": "LOAN_DISBURSEMENTS",
            
            # Refunds
            "REFUND": "REFUNDS",
            "REIMBURSEMENT": "REFUNDS",
            "CASHBACK": "REFUNDS"
        }
        
        # Purpose code mappings for RBI compliance
        self.purpose_codes = {
            "VENDOR_PAYMENTS": ["P0001", "P0002", "P0003"],  # Business payments
            "PAYROLL": ["P0010", "P0011"],  # Salary payments
            "TAX_PAYMENTS": ["P0020", "P0021", "P0022"],  # Tax payments
            "UTILITY_PAYMENTS": ["P0030", "P0031", "P0032"],  # Utility payments
            "LOAN_DISBURSEMENTS": ["P0040", "P0041"],  # Loan disbursements
            "REFUNDS": ["P0050", "P0051"]  # Refunds
        }
        
        # Risk scoring weights
        self.risk_weights = {
            "amount": 0.3,
            "transaction_type": 0.2,
            "purpose_match": 0.2,
            "account_age": 0.15,
            "frequency": 0.15
        }
        
        # Confidence calculation weights
        self.confidence_weights = {
            "purpose_clarity": 0.4,
            "amount_reasonableness": 0.3,
            "account_verification": 0.3
        }
        
        # Bank API endpoints for validation
        self.bank_apis = {
            "ICICI": "https://api.icicibank.com",
            "AXIS": "https://api.axisbank.com", 
            "HDFC": "https://api.hdfcbank.com",
            "SBI": "https://api.sbi.co.in"
        }
        
        # Government API endpoints
        self.gov_apis = {
            "uidai": "https://api.uidai.gov.in",
            "pan": "https://api.incometax.gov.in",
            "gst": "https://api.gst.gov.in"
        }
    
    def process_bank_transactions(self, bank_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process bank transaction data and classify intents.
        
        Args:
            bank_data: Bank transaction data in unified schema
            
        Returns:
            Intent classification results
        """
        try:
            logger.info(f"Processing bank transactions for batch {bank_data.get('batch_id')}")
            
            # Extract batch information
            batch_id = bank_data.get('batch_id')
            tenant_id = bank_data.get('tenant_id', 'UNKNOWN')
            source = bank_data.get('source', 'BANK_API')
            policy_version = bank_data.get('policy_version', 'intent-2.0.0')
            upload_ts = bank_data.get('upload_ts', datetime.now().isoformat() + 'Z')
            
            # Process each transaction line
            intents = []
            for line in bank_data.get('lines', []):
                try:
                    intent_result = self._classify_transaction_intent(line, tenant_id)
                    intents.append(intent_result)
                except Exception as e:
                    logger.error(f"Failed to classify line {line.get('line_id')}: {e}")
                    # Create error intent
                    intents.append({
                        "line_id": line.get('line_id', 'unknown'),
                        "intent": "UNKNOWN",
                        "risk_score": 1.0,
                        "confidence": 0.0,
                        "axis_validation": {},
                        "evidence_ref": line.get('evidence_ref', ''),
                        "remarks_summary": "CLASSIFICATION_ERROR"
                    })
            
            # Determine suggested workflow
            workflow_id = self._determine_workflow(intents)
            
            return {
                "batch_id": batch_id,
                "tenant_id": tenant_id,
                "source": source,
                "policy_version": policy_version,
                "upload_ts": upload_ts,
                "intents": intents,
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat() + 'Z'
            }
            
        except Exception as e:
            logger.error(f"Error processing bank transactions: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat() + 'Z'
            }
    
    def _classify_transaction_intent(self, line: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """
        Classify intent for a single transaction line.
        
        Args:
            line: Transaction line data
            tenant_id: Bank identifier
            
        Returns:
            Intent classification result
        """
        line_id = line.get('line_id', 'unknown')
        amount = float(line.get('amount', 0))
        purpose = line.get('purpose', '').upper()
        remarks = line.get('remarks', '').upper()
        
        # Extract account information
        debit_account = self._extract_account_info(line, 'debit')
        credit_account = self._extract_account_info(line, 'credit')
        
        # Classify intent based on purpose and remarks
        intent = self._determine_intent(purpose, remarks, amount)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(line, intent, amount)
        
        # Calculate confidence
        confidence = self._calculate_confidence(line, intent, purpose, remarks)
        
        # Get bank validation if available
        axis_validation = self._extract_bank_validation(line)
        
        # Create remarks summary
        remarks_summary = self._create_remarks_summary(purpose, remarks, intent)
        
        return {
            "line_id": line_id,
            "intent": intent,
            "risk_score": round(risk_score, 3),
            "confidence": round(confidence, 3),
            "axis_validation": axis_validation,
            "evidence_ref": line.get('evidence_ref', ''),
            "remarks_summary": remarks_summary
        }
    
    def _extract_account_info(self, line: Dict[str, Any], account_type: str) -> Dict[str, Any]:
        """Extract account information from transaction line."""
        account_key = f"{account_type.title()}AccountDetails"
        account_info = line.get(account_key, {}).get(f"{account_type.title()}AccountInformation", {})
        
        return {
            "account_number": account_info.get(f"{account_type}AccountNumber", ""),
            "account_holder": account_info.get(f"{account_type}AccountHolderName", ""),
            "ifsc_code": account_info.get("ifscCode", ""),
            "mmid": account_info.get("creditMMID", "") if account_type == "credit" else ""
        }
    
    def _determine_intent(self, purpose: str, remarks: str, amount: float) -> str:
        """
        Determine intent based on purpose, remarks, and amount.
        
        Args:
            purpose: Transaction purpose
            remarks: Transaction remarks
            amount: Transaction amount
            
        Returns:
            Classified intent
        """
        # Combine purpose and remarks for analysis
        combined_text = f"{purpose} {remarks}".upper()
        
        # Check for specific intent keywords
        for keyword, intent in self.intent_mappings.items():
            if keyword.upper() in combined_text:
                return intent
        
        # Amount-based classification
        if amount >= 50000:  # Large amounts likely vendor payments
            return "VENDOR_PAYMENTS"
        elif 10000 <= amount < 50000:  # Medium amounts could be payroll
            return "PAYROLL"
        elif amount < 10000:  # Small amounts could be utility or refunds
            return "UTILITY_PAYMENTS"
        
        # Default classification
        return "UNKNOWN"
    
    def _calculate_risk_score(self, line: Dict[str, Any], intent: str, amount: float) -> float:
        """
        Calculate risk score for transaction.
        
        Args:
            line: Transaction line data
            intent: Classified intent
            amount: Transaction amount
            
        Returns:
            Risk score (0-1)
        """
        risk_score = 0.0
        
        # Amount-based risk
        if amount > 1000000:  # Above 10 lakhs
            risk_score += 0.4
        elif amount > 500000:  # Above 5 lakhs
            risk_score += 0.2
        elif amount > 100000:  # Above 1 lakh
            risk_score += 0.1
        
        # Transaction type risk
        transaction_type = line.get('transaction_type', '').upper()
        if transaction_type in ['RTGS']:  # RTGS is typically high-value
            risk_score += 0.2
        elif transaction_type in ['IMPS', 'UPI']:  # IMPS/UPI are typically lower risk
            risk_score += 0.05
        
        # Intent-based risk
        if intent == "UNKNOWN":
            risk_score += 0.3
        elif intent in ["VENDOR_PAYMENTS", "LOAN_DISBURSEMENTS"]:
            risk_score += 0.1
        
        # Account age risk (mock implementation)
        # In production, this would check account creation date
        if amount > 100000:  # Large amounts to new accounts are risky
            risk_score += 0.1
        
        return min(1.0, risk_score)
    
    def _calculate_confidence(self, line: Dict[str, Any], intent: str, purpose: str, remarks: str) -> float:
        """
        Calculate confidence score for intent classification.
        
        Args:
            line: Transaction line data
            intent: Classified intent
            purpose: Transaction purpose
            remarks: Transaction remarks
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Purpose clarity
        if purpose and len(purpose) > 5:
            confidence += 0.2
        
        # Remarks clarity
        if remarks and len(remarks) > 10:
            confidence += 0.2
        
        # Intent match quality
        combined_text = f"{purpose} {remarks}".upper()
        if intent in combined_text:
            confidence += 0.3
        
        # Amount reasonableness for intent
        amount = float(line.get('amount', 0))
        if self._is_amount_reasonable_for_intent(intent, amount):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _is_amount_reasonable_for_intent(self, intent: str, amount: float) -> bool:
        """Check if amount is reasonable for the classified intent."""
        amount_ranges = {
            "VENDOR_PAYMENTS": (1000, 10000000),  # 1K to 1Cr
            "PAYROLL": (5000, 500000),  # 5K to 5L
            "TAX_PAYMENTS": (1000, 1000000),  # 1K to 10L
            "UTILITY_PAYMENTS": (100, 50000),  # 100 to 50K
            "LOAN_DISBURSEMENTS": (10000, 5000000),  # 10K to 50L
            "REFUNDS": (100, 100000)  # 100 to 1L
        }
        
        if intent in amount_ranges:
            min_amount, max_amount = amount_ranges[intent]
            return min_amount <= amount <= max_amount
        
        return True  # Unknown intents are always reasonable
    
    def _extract_bank_validation(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """Extract bank validation information if available."""
        # Check for Axis Bank validation
        if 'axis_validation' in line:
            return line['axis_validation']
        
        # Check for other bank validations
        validation_fields = ['code', 'result', 'utrNumber', 'bank_rrn']
        validation = {}
        
        for field in validation_fields:
            if field in line:
                validation[field] = line[field]
        
        return validation
    
    def _create_remarks_summary(self, purpose: str, remarks: str, intent: str) -> str:
        """Create a summary of remarks for the intent."""
        if purpose and remarks:
            return f"{purpose}: {remarks[:50]}..."
        elif purpose:
            return purpose
        elif remarks:
            return remarks[:50] + "..." if len(remarks) > 50 else remarks
        else:
            return intent
    
    def _determine_workflow(self, intents: List[Dict[str, Any]]) -> str:
        """Determine suggested workflow based on intents."""
        if not intents:
            return "WF-DEFAULT"
        
        # Get most common intent
        intent_counts = {}
        for intent in intents:
            intent_type = intent.get('intent', 'UNKNOWN')
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        most_common_intent = max(intent_counts, key=intent_counts.get)
        
        # Map intent to workflow
        workflow_mappings = {
            "VENDOR_PAYMENTS": "WF-VENDOR-DOMESTIC",
            "PAYROLL": "WF-PAYROLL-DOMESTIC", 
            "TAX_PAYMENTS": "WF-TAX-DOMESTIC",
            "UTILITY_PAYMENTS": "WF-UTILITY-DOMESTIC",
            "LOAN_DISBURSEMENTS": "WF-LOAN-DOMESTIC",
            "REFUNDS": "WF-REFUND-DOMESTIC"
        }
        
        return workflow_mappings.get(most_common_intent, "WF-UNKNOWN-DOMESTIC")
    
    def validate_kyc_completeness(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate KYC completeness for sender and beneficiary.
        
        Args:
            line: Transaction line data
            
        Returns:
            KYC validation results
        """
        # Mock implementation - in production, this would call government APIs
        debit_info = self._extract_account_info(line, 'debit')
        credit_info = self._extract_account_info(line, 'credit')
        
        return {
            "debit_kyc_verified": True,  # Would check UIDAI/PAN APIs
            "credit_kyc_verified": True,
            "debit_kyc_score": 0.95,
            "credit_kyc_score": 0.90,
            "evidence_refs": [
                "s3://bucket/kyc/debit_validation.json",
                "s3://bucket/kyc/credit_validation.json"
            ]
        }
    
    def check_sanctions_watchlist(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check against sanctions and watchlists.
        
        Args:
            line: Transaction line data
            
        Returns:
            Sanctions check results
        """
        # Mock implementation - in production, this would check global watchlists
        credit_info = self._extract_account_info(line, 'credit')
        beneficiary_name = credit_info.get('account_holder', '').upper()
        
        # Simple fuzzy matching (in production, use proper fuzzy matching)
        sanctions_score = 0.0
        if any(keyword in beneficiary_name for keyword in ['SANCTIONED', 'BLOCKED', 'WATCHLIST']):
            sanctions_score = 0.8
        
        return {
            "sanctions_clear": sanctions_score < 0.5,
            "sanctions_score": sanctions_score,
            "matched_entities": [],
            "evidence_refs": ["s3://bucket/sanctions/check_results.json"]
        }
    
    def validate_transaction_limits(self, line: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """
        Validate transaction against RBI limits.
        
        Args:
            line: Transaction line data
            tenant_id: Bank identifier
            
        Returns:
            Limits validation results
        """
        amount = float(line.get('amount', 0))
        transaction_type = line.get('transaction_type', '').upper()
        
        # RBI limits (mock implementation)
        limits = {
            "IMPS": 200000,  # 2L per transaction
            "NEFT": 10000000,  # 10L per transaction
            "RTGS": 2000000,  # 2L minimum
            "UPI": 100000  # 1L per transaction
        }
        
        limit = limits.get(transaction_type, 1000000)  # Default 10L
        
        return {
            "within_limits": amount <= limit,
            "limit_amount": limit,
            "transaction_amount": amount,
            "limit_utilization": min(1.0, amount / limit)
        }
    
    def validate_ifsc_account(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate IFSC code and account number.
        
        Args:
            line: Transaction line data
            
        Returns:
            IFSC/Account validation results
        """
        credit_info = self._extract_account_info(line, 'credit')
        ifsc_code = credit_info.get('ifsc_code', '')
        account_number = credit_info.get('account_number', '')
        
        # IFSC format validation
        ifsc_valid = bool(re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code))
        
        # Account number validation (basic)
        account_valid = len(account_number) >= 9 and account_number.isdigit()
        
        return {
            "ifsc_valid": ifsc_valid,
            "account_valid": account_valid,
            "ifsc_code": ifsc_code,
            "account_number": account_number,
            "bank_code": ifsc_code[:4] if ifsc_valid else None
        }
    
    def validate_purpose_code(self, line: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Validate purpose code against RBI guidelines.
        
        Args:
            line: Transaction line data
            intent: Classified intent
            
        Returns:
            Purpose code validation results
        """
        purpose = line.get('purpose', '')
        
        # Check if purpose aligns with intent
        allowed_codes = self.purpose_codes.get(intent, [])
        purpose_valid = any(code in purpose for code in allowed_codes) if allowed_codes else True
        
        return {
            "purpose_valid": purpose_valid,
            "purpose_code": purpose,
            "allowed_codes": allowed_codes,
            "intent": intent
        }


# Example usage and testing
def main():
    """Example usage of IntentManagerBankAPI."""
    
    # Sample bank transaction data
    sample_data = {
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
    
    # Process the data
    intent_manager = IntentManagerBankAPI()
    result = intent_manager.process_bank_transactions(sample_data)
    
    # Print results
    print("Intent Classification Results:")
    print(json.dumps(result, indent=2))
    
    # Show summary
    if 'intents' in result:
        print(f"\nSummary:")
        print(f"Batch ID: {result['batch_id']}")
        print(f"Total Transactions: {len(result['intents'])}")
        print(f"Suggested Workflow: {result['workflow_id']}")
        
        for intent in result['intents']:
            print(f"Line {intent['line_id']}: {intent['intent']} (Risk: {intent['risk_score']}, Confidence: {intent['confidence']})")


if __name__ == "__main__":
    main()
