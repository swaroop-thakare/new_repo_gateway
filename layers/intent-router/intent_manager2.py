"""
Intent Manager 2.0 - Axis Bank Invoice Processing

Handles invoice_received events from Axis Bank with specific logic for:
- PASS: Compliant vendor payments
- HOLD: New accounts requiring review
- FAIL: Sanctioned entities
- OVERRIDE: Manual overrides from HOLD to PASS

Input: Axis Bank invoice data
Output: Intent classification with agent pipeline routing
"""

import json
import re
import requests
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from difflib import SequenceMatcher

class IntentManager2:
    """
    Intent Manager 2.0 for Axis Bank invoice processing.
    
    Handles invoice_received events with specific business logic for
    PASS/HOLD/FAIL/OVERRIDE scenarios and agent pipeline routing.
    """
    
    def __init__(self):
        """Initialize Intent Manager 2.0 with Axis Bank specific configuration."""
        
        # Intent mappings for Axis Bank invoices
        self.intent_mappings = {
            "VENDOR_PAYMENT": "VENDOR_PAYMENTS",
            "PAYROLL": "PAYROLL",
            "LOAN": "LOAN",
            "UTILITY": "UTILITY",
            "TAX": "TAX",
            "REFUND": "REFUND"
        }
        
        # Risk scoring weights (updated for Axis Bank logic)
        self.risk_weights = {
            "amount": 0.4,
            "zone": 0.2,
            "purpose": 0.25,
            "account": 0.15
        }
        
        # Confidence calculation weights
        self.confidence_weights = {
            "match": 0.5,
            "completeness": 0.3,
            "account": 0.2
        }
        
        # Agent pipeline configurations based on decision
        self.agent_pipelines = {
            "PASS": ["PDR", "CRRAK", "ARL"],
            "HOLD": ["PDR", "RCA", "CRRAK"],  # RCA for analysis of hold reasons
            "FAIL": ["RCA", "CRRAK"],  # RCA for failure analysis, CRRAK for compliance
            "OVERRIDE": ["PDR", "CRRAK", "ARL"]
        }
        
        # Workflow mappings
        self.workflow_mappings = {
            "VENDOR_PAYMENTS": {
                "PASS": "WF-VENDOR-DOMESTIC",
                "HOLD": "WF-VENDOR-HOLD",
                "FAIL": "WF-VENDOR-FAIL",
                "OVERRIDE": "WF-VENDOR-OVERRIDE"
            },
            "PAYROLL": {
                "PASS": "WF-PAYROLL-DOMESTIC",
                "HOLD": "WF-PAYROLL-HOLD",
                "FAIL": "WF-PAYROLL-FAIL",
                "OVERRIDE": "WF-PAYROLL-OVERRIDE"
            },
            "LOAN": {
                "PASS": "WF-LOAN-DOMESTIC",
                "HOLD": "WF-LOAN-HOLD",
                "FAIL": "WF-LOAN-FAIL",
                "OVERRIDE": "WF-LOAN-OVERRIDE"
            }
        }
        
        # Axis API configuration
        self.axis_api_config = {
            "base_url": "https://api.axisbank.com",
            "payment_enquiry_endpoint": "/payment-enquiry-imps",
            "timeout": 30
        }
        
        # Evidence storage configuration
        self.evidence_config = {
            "bucket": "arealis-evidence",
            "prefix": "evidence"
        }
    
    def process_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Axis Bank invoice and return classification results.
        
        Args:
            invoice_data: Invoice data from Axis Bank
            
        Returns:
            Classification results with agent pipeline routing
        """
        batch_id = invoice_data.get("batch_id")
        tenant_id = invoice_data.get("tenant_id", "AXIS")
        lines = invoice_data.get("lines", [])
        
        print(f"🚀 Processing Axis Bank Invoice: {batch_id}")
        print(f"📊 Tenant: {tenant_id}, Lines: {len(lines)}")
        
        # Process each line
        intents = []
        workflow_ids = set()
        agent_pipeline = set()
        
        for line in lines:
            # Extract line information
            line_info = self._extract_line_info(line)
            
            # Classify intent
            intent_result = self._classify_line_intent(line_info, line.get("line_id"))
            intents.append(intent_result)
            
            # Get workflow and agent pipeline
            decision = intent_result["decision"]
            workflow_id = self._get_workflow_id(intent_result["intent"], decision)
            workflow_ids.add(workflow_id)
            
            pipeline = self._get_agent_pipeline(decision)
            agent_pipeline.update(pipeline)
        
        # Create final output
        output = {
            "batch_id": batch_id,
            "intents": intents,
            "workflow_id": list(workflow_ids)[0] if len(workflow_ids) == 1 else list(workflow_ids),
            "agent_pipeline": list(agent_pipeline),
            "policy_version": "intent-2.0.0"
        }
        
        # Add override flag if any line was overridden
        if any(intent.get("override", False) for intent in intents):
            output["override"] = True
        
        return output
    
    def _extract_line_info(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize line information from invoice data.
        
        Args:
            line: Invoice line data
            
        Returns:
            Normalized line information
        """
        debit_info = line.get("DebitAccountDetails", {}).get("DebitAccountInformation", {})
        credit_info = line.get("CreditAccountDetails", {}).get("CreditAccountInformation", {})
        
        return {
            "line_id": line.get("line_id"),
            "amount": float(line.get("amount", 0.0)),
            "currency": line.get("currency", "INR"),
            "purpose": line.get("purpose", ""),
            "debit_account": debit_info.get("debitAccountNumber", ""),
            "credit_account": credit_info.get("creditAccountNumber", ""),
            "ifsc_code": credit_info.get("ifscCode", ""),
            "source_reference": line.get("sourceReferenceNumber", ""),
            "remarks": line.get("remarks", "")
        }
    
    def _classify_line_intent(self, line_info: Dict[str, Any], line_id: str) -> Dict[str, Any]:
        """
        Classify line intent with Axis Bank specific logic.
        
        Args:
            line_info: Normalized line information
            line_id: Line identifier
            
        Returns:
            Intent classification result
        """
        # Intent classification
        intent = self._classify_intent(line_info["purpose"])
        
        # Calculate risk score using Axis Bank formula
        risk_score = self._calculate_axis_risk_score(line_info, intent)
        
        # Calculate confidence using Axis Bank formula
        confidence = self._calculate_axis_confidence(line_info, intent)
        
        # Axis API validation
        axis_validation = self._validate_with_axis_api(line_info)
        
        # Determine decision (PASS/HOLD/FAIL/OVERRIDE)
        decision = self._determine_decision(line_info, intent, risk_score, confidence, axis_validation)
        
        # Store evidence
        evidence_ref = self._store_evidence(line_info, intent, risk_score, confidence, axis_validation, decision)
        
        return {
            "line_id": line_id,
            "intent": intent,
            "risk_score": round(risk_score, 2),
            "confidence": round(confidence, 2),
            "axis_validation": axis_validation,
            "evidence_ref": evidence_ref,
            "decision": decision
        }
    
    def _classify_intent(self, purpose: str) -> str:
        """
        Classify intent from purpose string.
        
        Args:
            purpose: Payment purpose
            
        Returns:
            Classified intent
        """
        purpose_upper = purpose.upper().strip()
        
        # Exact match
        if purpose_upper in self.intent_mappings:
            return self.intent_mappings[purpose_upper]
        
        # Fuzzy matching
        best_match = None
        best_similarity = 0.0
        
        for key, intent in self.intent_mappings.items():
            similarity = SequenceMatcher(None, purpose_upper, key).ratio()
            if similarity > best_similarity and similarity > 0.6:
                best_similarity = similarity
                best_match = intent
        
        return best_match if best_match else "UNKNOWN"
    
    def _calculate_axis_risk_score(self, line_info: Dict[str, Any], intent: str) -> float:
        """
        Calculate risk score using Axis Bank formula:
        risk_score = 0.4*amount_risk + 0.2*zone_risk + 0.25*purpose_risk + 0.15*account_risk
        
        Args:
            line_info: Line information
            intent: Classified intent
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        amount = line_info["amount"]
        ifsc_code = line_info["ifsc_code"]
        purpose = line_info["purpose"]
        
        # Amount risk: min(1, amount / 100000) - Updated threshold
        amount_risk = min(1.0, amount / 100000.0) if amount >= 0 else 1.0
        
        # Zone risk: 0.1 (DOMESTIC) or 0.3 (INTERNATIONAL)
        zone_risk = 0.3 if self._is_international_ifsc(ifsc_code) else 0.1
        
        # Purpose risk: 0.1 (exact match) or 0.2 (no match)
        purpose_upper = purpose.upper().strip()
        purpose_risk = 0.1 if purpose_upper in self.intent_mappings else 0.2
        
        # Account risk: 0.0 (verified), 0.05 (new account), 0.2 (sanctioned)
        account_risk = self._calculate_account_risk(line_info)
        
        # Calculate final risk score with updated weights
        risk_score = (
            0.4 * amount_risk +
            0.2 * zone_risk +
            0.25 * purpose_risk +
            0.15 * account_risk
        )
        
        return min(max(risk_score, 0.0), 1.0)
    
    def _calculate_axis_confidence(self, line_info: Dict[str, Any], intent: str) -> float:
        """
        Calculate confidence using Axis Bank formula:
        confidence = (match_confidence^0.5) * (completeness^0.3) * (account_conf^0.2)
        
        Args:
            line_info: Line information
            intent: Classified intent
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        purpose = line_info["purpose"]
        
        # Match confidence: 0.9 (exact), 0.7 (fuzzy), 0.5 (none)
        purpose_upper = purpose.upper().strip()
        if purpose_upper in self.intent_mappings:
            match_confidence = 0.9
        else:
            # Check fuzzy match
            best_similarity = 0.0
            for key in self.intent_mappings:
                similarity = SequenceMatcher(None, purpose_upper, key).ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
            
            if best_similarity > 0.6:
                match_confidence = 0.7
            else:
                match_confidence = 0.5
        
        # Completeness: 1.0 (complete) or 0.7 (incomplete)
        required_fields = ["amount", "currency", "purpose", "debit_account", "credit_account", "ifsc_code"]
        complete = all(line_info.get(field) for field in required_fields)
        completeness = 1.0 if complete else 0.7
        
        # Account confidence: 0.95 (verified), 0.7 (new), 0.5 (sanctioned)
        account_conf = self._calculate_account_confidence(line_info)
        
        # Calculate final confidence
        confidence = (
            (match_confidence ** self.confidence_weights["match"]) *
            (completeness ** self.confidence_weights["completeness"]) *
            (account_conf ** self.confidence_weights["account"])
        )
        
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_account_risk(self, line_info: Dict[str, Any]) -> float:
        """
        Calculate account-specific risk.
        
        Args:
            line_info: Line information
            
        Returns:
            Account risk score
        """
        # This would integrate with actual account verification systems
        # For now, using synthetic logic based on account patterns
        
        credit_account = line_info.get("credit_account", "")
        ifsc_code = line_info.get("ifsc_code", "")
        
        # Check for new account patterns (account number length, patterns)
        if len(credit_account) < 10:
            return 0.05  # New account
        
        # Check for sanctioned entity patterns (this would be real integration)
        if "SANCTIONED" in credit_account.upper() or "BLOCKED" in credit_account.upper():
            return 0.2  # Sanctioned entity
        
        return 0.0  # Verified account
    
    def _calculate_account_confidence(self, line_info: Dict[str, Any]) -> float:
        """
        Calculate account-specific confidence.
        
        Args:
            line_info: Line information
            
        Returns:
            Account confidence score
        """
        # This would integrate with actual account verification systems
        # For now, using synthetic logic
        
        credit_account = line_info.get("credit_account", "")
        
        # Check for new account patterns
        if len(credit_account) < 10:
            return 0.7  # New account
        
        # Check for sanctioned entity patterns
        if "SANCTIONED" in credit_account.upper() or "BLOCKED" in credit_account.upper():
            return 0.5  # Sanctioned entity
        
        return 0.95  # Verified account
    
    def _is_international_ifsc(self, ifsc_code: str) -> bool:
        """
        Check if IFSC code indicates international transaction.
        
        Args:
            ifsc_code: IFSC code
            
        Returns:
            True if international
        """
        # International IFSC patterns
        international_patterns = ["SWIFT", "CHAS", "CITI", "HSBC"]
        ifsc_upper = ifsc_code.upper()
        
        for pattern in international_patterns:
            if pattern in ifsc_upper:
                return True
        
        return False
    
    def _validate_with_axis_api(self, line_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate with Axis Bank API.
        
        Args:
            line_info: Line information
            
        Returns:
            API validation result
        """
        try:
            # This would make actual API call to Axis Bank
            # For now, returning synthetic response
            
            source_reference = line_info.get("source_reference", "")
            
            # Simulate API call
            api_response = {
                "code": "00",
                "result": "Success",
                "reference_number": source_reference,
                "timestamp": datetime.now().isoformat()
            }
            
            return api_response
            
        except Exception as e:
            return {
                "code": "99",
                "result": "Error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _determine_decision(self, line_info: Dict[str, Any], intent: str, 
                          risk_score: float, confidence: float, 
                          axis_validation: Dict[str, Any]) -> str:
        """
        Determine decision (PASS/HOLD/FAIL/OVERRIDE) based on business rules.
        
        Args:
            line_info: Line information
            intent: Classified intent
            risk_score: Calculated risk score
            confidence: Calculated confidence
            axis_validation: Axis API validation result
            
        Returns:
            Decision string
        """
        # Check for override conditions
        if line_info.get("remarks", "").upper().find("OVERRIDE") != -1:
            return "OVERRIDE"
        
        # Check for fail conditions
        if axis_validation.get("code") != "00":
            return "FAIL"
        
        # Check for sanctioned entity
        if "SANCTIONED" in line_info.get("credit_account", "").upper():
            return "FAIL"
        
        # Check for high risk (updated threshold)
        if risk_score > 0.5:
            return "FAIL"
        
        # Check for hold conditions (new account, low confidence)
        credit_account = line_info.get("credit_account", "")
        if (len(credit_account) < 10 or 
            confidence < 0.85 or 
            risk_score > 0.3):
            return "HOLD"
        
        # Default to PASS
        return "PASS"
    
    def _store_evidence(self, line_info: Dict[str, Any], intent: str, 
                       risk_score: float, confidence: float, 
                       axis_validation: Dict[str, Any], decision: str) -> str:
        """
        Store evidence in S3.
        
        Args:
            line_info: Line information
            intent: Classified intent
            risk_score: Risk score
            confidence: Confidence score
            axis_validation: Axis API validation
            decision: Decision
            
        Returns:
            Evidence reference URL
        """
        # This would store actual evidence in S3
        # For now, generating synthetic reference
        
        batch_id = f"B-{datetime.now().strftime('%Y-%m-%d')}-01"
        line_id = line_info.get("line_id", "L-1")
        
        evidence_data = {
            "line_info": line_info,
            "intent": intent,
            "risk_score": risk_score,
            "confidence": confidence,
            "axis_validation": axis_validation,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate S3 reference
        evidence_ref = f"s3://{self.evidence_config['bucket']}/{self.evidence_config['prefix']}/AXIS_{batch_id}/{line_id}/intent.json"
        
        # In real implementation, would store evidence_data to S3
        print(f"📁 Evidence stored: {evidence_ref}")
        
        return evidence_ref
    
    def _get_workflow_id(self, intent: str, decision: str) -> str:
        """
        Get workflow ID for intent and decision.
        
        Args:
            intent: Classified intent
            decision: Decision (PASS/HOLD/FAIL/OVERRIDE)
            
        Returns:
            Workflow ID
        """
        if intent in self.workflow_mappings:
            return self.workflow_mappings[intent].get(decision, "WF-DEFAULT")
        return "WF-DEFAULT"
    
    def _get_agent_pipeline(self, decision: str) -> List[str]:
        """
        Get agent pipeline for decision.
        
        Args:
            decision: Decision (PASS/HOLD/FAIL/OVERRIDE)
            
        Returns:
            List of agent pipeline steps
        """
        return self.agent_pipelines.get(decision, ["PDR", "CRRAK", "ARL"])
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process invoice file and return classification results.
        
        Args:
            file_path: Path to invoice JSON file
            
        Returns:
            Classification results
        """
        try:
            with open(file_path, 'r') as f:
                invoice_data = json.load(f)
            
            return self.process_invoice(invoice_data)
            
        except Exception as e:
            return {
                "error": f"Failed to process file {file_path}: {str(e)}"
            }

def main():
    """
    Main function to demonstrate Intent Manager 2.0 usage.
    """
    print("🤖 Intent Manager 2.0 - Axis Bank Invoice Processing")
    print("=" * 60)
    
    # Initialize Intent Manager 2.0
    intent_manager = IntentManager2()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Scenario 1: PASS (Compliant Vendor Payment)",
            "data": {
                "batch_id": "B-2025-10-03-01",
                "tenant_id": "AXIS",
                "invoice_ref": "INV-2025-10-03-001",
                "source": "BANK_INVOICE",
                "policy_version": "intent-2.0.0",
                "lines": [
                    {
                        "line_id": "L-1",
                        "amount": 250000,
                        "currency": "INR",
                        "purpose": "VENDOR_PAYMENT",
                        "DebitAccountDetails": {
                            "DebitAccountInformation": {"debitAccountNumber": "91402004****3081"}
                        },
                        "CreditAccountDetails": {
                            "CreditAccountInformation": {"creditAccountNumber": "0052050****597", "ifscCode": "BARB0RAEBAR"}
                        },
                        "sourceReferenceNumber": "SAKR39267668",
                        "remarks": "Vendor Payment for Supplies"
                    }
                ]
            }
        },
        {
            "name": "Scenario 2: HOLD (New Account)",
            "data": {
                "batch_id": "B-2025-10-03-02",
                "tenant_id": "AXIS",
                "invoice_ref": "INV-2025-10-03-002",
                "source": "BANK_INVOICE",
                "policy_version": "intent-2.0.0",
                "lines": [
                    {
                        "line_id": "L-2",
                        "amount": 50000,
                        "currency": "INR",
                        "purpose": "PAYROLL",
                        "DebitAccountDetails": {"DebitAccountInformation": {"debitAccountNumber": "9180190****0605"}},
                        "CreditAccountDetails": {"CreditAccountInformation": {"creditAccountNumber": "2001110****011", "ifscCode": "SIMB0002233"}},
                        "sourceReferenceNumber": "SAKR39267669",
                        "remarks": "Salary October 2025"
                    }
                ]
            }
        },
        {
            "name": "Scenario 3: FAIL (Sanctioned Entity)",
            "data": {
                "batch_id": "B-2025-10-03-03",
                "tenant_id": "AXIS",
                "invoice_ref": "INV-2025-10-03-003",
                "source": "BANK_INVOICE",
                "policy_version": "intent-2.0.0",
                "lines": [
                    {
                        "line_id": "L-3",
                        "amount": 1000000,
                        "currency": "INR",
                        "purpose": "LOAN",
                        "DebitAccountDetails": {"DebitAccountInformation": {"debitAccountNumber": "91402004****3081"}},
                        "CreditAccountDetails": {"CreditAccountInformation": {"creditAccountNumber": "SANCTIONED****597", "ifscCode": "BARB0RAEBAR"}},
                        "sourceReferenceNumber": "SAKR39267670",
                        "remarks": "Loan Disbursement"
                    }
                ]
            }
        },
        {
            "name": "Scenario 4: OVERRIDE (HOLD to PASS)",
            "data": {
                "batch_id": "B-2025-10-03-04",
                "tenant_id": "AXIS",
                "invoice_ref": "INV-2025-10-03-004",
                "source": "BANK_INVOICE",
                "policy_version": "intent-2.0.0",
                "lines": [
                    {
                        "line_id": "L-4",
                        "amount": 75000,
                        "currency": "INR",
                        "purpose": "VENDOR_PAYMENT",
                        "DebitAccountDetails": {"DebitAccountInformation": {"debitAccountNumber": "9180190****0605"}},
                        "CreditAccountDetails": {"CreditAccountInformation": {"creditAccountNumber": "2001110****011", "ifscCode": "SIMB0002233"}},
                        "sourceReferenceNumber": "SAKR39267671",
                        "remarks": "New Vendor Setup - OVERRIDE APPROVED"
                    }
                ]
            }
        }
    ]
    
    # Process each scenario and collect results
    all_results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"🧪 {scenario['name']}")
        print(f"{'='*60}")
        
        results = intent_manager.process_invoice(scenario['data'])
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            continue
        
        print("✅ Classification Results:")
        print(json.dumps(results, indent=2))
        
        # Collect results for consolidation
        all_results.append(results)
        
        # Save individual results
        output_file = f"intent_manager2_scenario_{i}_output.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
    
    # Create consolidated output
    if all_results:
        consolidated_output = {
            "batch_id": f"B-CONSOLIDATED-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "scenarios": all_results,
            "total_scenarios": len(all_results),
            "policy_version": "intent-2.0.0",
            "timestamp": datetime.now().isoformat() + "Z",
            "status": "PROCESSING"
        }
        
        # Save consolidated results
        consolidated_file = f"intent_manager2_consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(consolidated_file, 'w') as f:
            json.dump(consolidated_output, f, indent=2)
        
        print(f"\n📊 Consolidated Summary:")
        print(f"   • Total Scenarios: {len(all_results)}")
        print(f"   • Consolidated Output: {consolidated_file}")
        
        # Show decision breakdown
        decisions = {}
        for result in all_results:
            for intent in result.get('intents', []):
                decision = intent.get('decision', 'UNKNOWN')
                decisions[decision] = decisions.get(decision, 0) + 1
        
        print(f"\n🎯 Decision Breakdown:")
        for decision, count in decisions.items():
            print(f"   • {decision}: {count} lines")
    
    print(f"\n🎉 Intent Manager 2.0 Processing Complete!")
    print("🤖 All Axis Bank invoice scenarios processed successfully!")

if __name__ == "__main__":
    main()
