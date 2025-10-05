"""
Intent Manager - Agentic AI for Payment Intent Classification

A single, comprehensive system that processes payment data and classifies intents
for the Arealis Gateway system. This is the complete agentic AI solution.

Input: JSON payment data (from S3 or local file)
Output: Intent classification with risk scores and workflow routing
"""

import json
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from difflib import SequenceMatcher

class IntentManager:
    """
    Agentic AI Intent Manager for the Arealis Gateway system.
    
    This single file contains all functionality:
    - Payment data processing
    - Intent classification using rule-based + AI logic
    - Risk scoring and assessment
    - Workflow routing
    - Agent pipeline generation
    """
    
    def __init__(self):
        """Initialize the Intent Manager with comprehensive configuration."""
        
        # Intent classification mappings
        self.intent_mappings = {
            # Payroll intents
            "SALARY": "PAYROLL",
            "PAYROLL": "PAYROLL", 
            "EMP_WAGES": "PAYROLL",
            "EMPLOYEE_PAYMENT": "PAYROLL",
            "STAFF_SALARY": "PAYROLL",
            "WAGES": "PAYROLL",
            
            # Vendor payment intents
            "VENDOR_TO_VENDOR": "VENDOR_TO_VENDOR",
            "VENDOR_PAYMENT": "VENDOR_PAYMENT",
            "SUPPLIER_PAYMENT": "VENDOR_PAYMENT",
            "SERVICES": "VENDOR_PAYMENT",
            "SUP": "VENDOR_PAYMENT", 
            "GOODS": "VENDOR_PAYMENT",
            "SUPPLIER": "VENDOR_PAYMENT",
            "VENDOR": "VENDOR_PAYMENT",
            "CONTRACTOR": "VENDOR_PAYMENT",
            "CONSULTING": "VENDOR_PAYMENT",
            
            # Loan intents
            "LOAN_DISBURSEMENT": "LOAN",
            "LOAN_DISB": "LOAN",
            "LOAN_PAYMENT": "LOAN",
            "DISBURSEMENT": "LOAN",
            
            # Other intents
            "UTILITY_PAYMENT": "UTILITY",
            "TAX_PAYMENT": "TAX",
            "REFUND": "REFUND",
            "INVESTMENT": "INVESTMENT",
            "TRANSFER": "TRANSFER"
        }
        
        # Risk scoring parameters
        self.risk_factors = {
            "amount_high": 0.3,      # Amount > ₹100k
            "amount_very_high": 0.5,  # Amount > ₹500k
            "amount_critical": 0.7,   # Amount > ₹1M
            "international": 0.4,    # International payments
            "vendor_to_vendor": 0.2,  # Vendor-to-vendor payments
            "unusual_purpose": 0.3,   # Unusual purpose codes
            "low_confidence": 0.2,    # Low confidence classification
            "unknown_intent": 0.4,    # Unknown intent classification
            "cash_payment": 0.3,      # Cash payments
            "high_frequency": 0.2     # High frequency payments
        }
        
        # Risk level thresholds
        self.risk_thresholds = {
            "LOW": 0.0,
            "MEDIUM": 0.3,
            "HIGH": 0.5,
            "CRITICAL": 0.8
        }
        
        # Workflow mappings based on intent and risk level
        self.workflow_mappings = {
            "PAYROLL": {
                "LOW": "WF-PAYROLL-DOMESTIC",
                "MEDIUM": "WF-PAYROLL-ENHANCED",
                "HIGH": "WF-PAYROLL-REVIEW",
                "CRITICAL": "WF-PAYROLL-CRITICAL"
            },
            "VENDOR_PAYMENT": {
                "LOW": "WF-VENDOR-PAYMENT-DOMESTIC",
                "MEDIUM": "WF-VENDOR-PAYMENT-ENHANCED", 
                "HIGH": "WF-VENDOR-PAYMENT-REVIEW",
                "CRITICAL": "WF-VENDOR-PAYMENT-CRITICAL"
            },
            "VENDOR_TO_VENDOR": {
                "LOW": "WF-VENDOR-TO-VENDOR-DOMESTIC",
                "MEDIUM": "WF-VENDOR-TO-VENDOR-ENHANCED",
                "HIGH": "WF-VENDOR-TO-VENDOR-REVIEW",
                "CRITICAL": "WF-VENDOR-TO-VENDOR-CRITICAL"
            },
            "LOAN": {
                "LOW": "WF-LOAN-DOMESTIC",
                "MEDIUM": "WF-LOAN-ENHANCED",
                "HIGH": "WF-LOAN-REVIEW",
                "CRITICAL": "WF-LOAN-CRITICAL"
            },
            "UTILITY": {
                "LOW": "WF-UTILITY-DOMESTIC",
                "MEDIUM": "WF-UTILITY-ENHANCED",
                "HIGH": "WF-UTILITY-REVIEW",
                "CRITICAL": "WF-UTILITY-CRITICAL"
            },
            "TAX": {
                "LOW": "WF-TAX-DOMESTIC",
                "MEDIUM": "WF-TAX-ENHANCED",
                "HIGH": "WF-TAX-REVIEW",
                "CRITICAL": "WF-TAX-CRITICAL"
            },
            "REFUND": {
                "LOW": "WF-REFUND-DOMESTIC",
                "MEDIUM": "WF-REFUND-ENHANCED",
                "HIGH": "WF-REFUND-REVIEW",
                "CRITICAL": "WF-REFUND-CRITICAL"
            },
            "INVESTMENT": {
                "LOW": "WF-INVESTMENT-DOMESTIC",
                "MEDIUM": "WF-INVESTMENT-ENHANCED",
                "HIGH": "WF-INVESTMENT-REVIEW",
                "CRITICAL": "WF-INVESTMENT-CRITICAL"
            },
            "TRANSFER": {
                "LOW": "WF-TRANSFER-DOMESTIC",
                "MEDIUM": "WF-TRANSFER-ENHANCED",
                "HIGH": "WF-TRANSFER-REVIEW",
                "CRITICAL": "WF-TRANSFER-CRITICAL"
            },
            "UNKNOWN": {
                "LOW": "WF-UNKNOWN-DOMESTIC",
                "MEDIUM": "WF-UNKNOWN-ENHANCED",
                "HIGH": "WF-UNKNOWN-REVIEW",
                "CRITICAL": "WF-UNKNOWN-CRITICAL"
            }
        }
        
        # Agent pipeline mappings
        self.agent_pipelines = {
            "PAYROLL": ["PDR", "CRRAK", "ARL"],
            "VENDOR_PAYMENT": ["PDR", "CRRAK", "ARL"],
            "VENDOR_TO_VENDOR": ["PDR", "CRRAK", "ARL"],
            "LOAN": ["PDR", "CRRAK", "ARL"],
            "UTILITY": ["PDR", "CRRAK", "ARL"],
            "TAX": ["PDR", "CRRAK", "ARL"],
            "REFUND": ["PDR", "CRRAK", "ARL"],
            "INVESTMENT": ["PDR", "RCA", "CRRAK", "ARL"],  # RCA for investment analysis
            "TRANSFER": ["PDR", "CRRAK", "ARL"],
            "UNKNOWN": ["PDR", "RCA", "CRRAK", "ARL"]  # RCA for unknown payment analysis
        }

        # Synthetic tenant history for development/testing
        self.tenants = {
            "T-123": {
                "failure_rate": 0.05  # Synthetic default failure rate for risk history
            }
        }
    
    def process_payments(self, payments_data: List[Dict[str, Any]], batch_id: str = None) -> Dict[str, Any]:
        """
        Main processing function - processes payment data and returns classification results.
        
        Args:
            payments_data: List of payment dictionaries from S3 or local file
            batch_id: Optional batch ID, will generate if not provided
            
        Returns:
            Classification results in the exact required format
        """
        if not batch_id:
            batch_id = f"B-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
        
        print(f"🚀 Intent Manager Processing {len(payments_data)} payments for batch {batch_id}")
        
        # Process each payment
        intents = []
        workflow_ids = set()
        agent_pipeline = set()
        
        for i, payment_data in enumerate(payments_data):
            # Extract payment information
            payment_info = self._extract_payment_info(payment_data)
            
            # Classify intent
            intent_result = self._classify_intent(payment_info, f"L-{i+1}")
            intents.append(intent_result)
            
            # Get workflow and agent pipeline
            risk_level = self._determine_risk_level(intent_result["risk_score"])
            workflow_id = self._get_workflow_id(intent_result["intent"], risk_level)
            workflow_ids.add(workflow_id)
            
            pipeline = self._get_agent_pipeline(intent_result["intent"])
            agent_pipeline.update(pipeline)
        
        # Create final output in exact required format
        output = {
            "batch_id": batch_id,
            "intents": intents,
            "workflow_ids": list(workflow_ids),
            "agent_pipeline": list(agent_pipeline),
            "policy_version": "intent-1.0.1"
        }
        
        return output
    
    def _extract_payment_info(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize payment information from input data.
        
        Args:
            payment_data: Raw payment data dictionary
            
        Returns:
            Normalized payment information
        """
        return {
            "payment_type": payment_data.get("payment_type", ""),
            "transaction_id": payment_data.get("transaction_id", ""),
            "amount": float(payment_data.get("amount", 0.0)),
            "currency": payment_data.get("currency", "INR"),
            "method": payment_data.get("method", "UPI"),
            "purpose": payment_data.get("purpose", ""),
            "sender": payment_data.get("sender", {}),
            "receiver": payment_data.get("receiver", {}),
            "location": payment_data.get("location", {}),
            "schedule_datetime": payment_data.get("schedule_datetime", ""),
            "additional_fields": payment_data.get("additional_fields", {})
        }
    
    def _classify_intent(self, payment_info: Dict[str, Any], line_id: str) -> Dict[str, Any]:
        """
        Classify payment intent using rule-based and AI-enhanced logic.
        
        Args:
            payment_info: Normalized payment information
            line_id: Line identifier
            
        Returns:
            Intent classification result
        """
        # Rule-based classification
        intent, match_kind = self._rule_based_classification(
            payment_info["purpose"], 
            payment_info["payment_type"]
        )

        # Compute confidence using synthetic formula
        confidence = self._compute_confidence(payment_info, match_kind)

        # Calculate risk score using synthetic formula
        risk_score = self._calculate_risk_score(payment_info, intent)

        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        return {
            "line_id": line_id,
            "intent": intent,
            "risk_score": round(risk_score, 2),
            "confidence": round(confidence, 2)
        }
    
    def _rule_based_classification(self, purpose: str, payment_type: str) -> Tuple[str, str]:
        """
        Rule-based intent classification using exact and fuzzy matching.
        
        Args:
            purpose: Payment purpose string
            payment_type: Payment type from input data
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        purpose_upper = purpose.upper().strip()
        payment_type_upper = payment_type.upper().strip()
        
        # Check payment type first (highest confidence)
        if payment_type_upper in ["PAYROLL", "SALARY", "WAGES"]:
            return "PAYROLL", "exact"
        
        # Exact match on purpose (high confidence)
        if purpose_upper in self.intent_mappings:
            return self.intent_mappings[purpose_upper], "exact"
        
        # Fuzzy matching for similar purposes (medium confidence)
        best_match = None
        best_similarity = 0.0
        
        for key, intent in self.intent_mappings.items():
            similarity = SequenceMatcher(None, purpose_upper, key).ratio()
            if similarity > best_similarity and similarity > 0.6:  # 60% similarity threshold
                best_similarity = similarity
                best_match = intent
        
        if best_match:
            return best_match, "fuzzy"
        
        # Default to UNKNOWN if no match found (low confidence)
        return "UNKNOWN", "none"
    
    def _calculate_risk_score(self, payment_info: Dict[str, Any], intent: str) -> float:
        """
        Calculate synthetic risk score as specified:
        amount_risk = min(1, amount / 100000)
        zone_risk = 0.1 (DOMESTIC) or 0.3 (INTERNATIONAL)
        purpose_risk = 0.2 default; 0.1 if purpose matches mock patterns (exact)
        history_risk = tenants["T-123"]["failure_rate"]
        risk_score = 0.4*amount_risk + 0.2*zone_risk + 0.3*purpose_risk + 0.1*history_risk
        """
        amount = float(payment_info.get("amount", 0.0))
        purpose = str(payment_info.get("purpose", ""))
        sender = payment_info.get("sender", {})
        receiver = payment_info.get("receiver", {})
        location = payment_info.get("location", {})

        # Amount-based risk
        amount_risk = min(1.0, amount / 100000.0) if amount >= 0 else 1.0

        # Zone risk using international detection
        is_international = self._is_international_payment(location, sender, receiver)
        zone_risk = 0.3 if is_international else 0.1

        # Purpose ambiguity risk
        purpose_upper = purpose.upper().strip()
        purpose_risk = 0.1 if purpose_upper in self.intent_mappings else 0.2

        # Tenant history risk (synthetic)
        history_risk = float(self.tenants.get("T-123", {}).get("failure_rate", 0.05))

        risk_score = (
            0.4 * amount_risk +
            0.2 * zone_risk +
            0.3 * purpose_risk +
            0.1 * history_risk
        )

        return round(min(max(risk_score, 0.0), 1.0), 2)

    def _compute_confidence(self, payment_info: Dict[str, Any], match_kind: str) -> float:
        """
        Calculate synthetic confidence as specified:
        match_confidence = 0.9 (exact), 0.7 (fuzzy), 0.5 (none)
        completeness = 1.0 (assume complete), 0.7 if required fields missing
        history_conf = 0.8 default, 0.9 if purpose matches patterns (exact)
        confidence = (match_confidence^0.5) * (completeness^0.3) * (history_conf^0.2)
        """
        purpose_upper = str(payment_info.get("purpose", "")).upper().strip()

        # Match confidence
        if match_kind == "exact":
            match_confidence = 0.9
        elif match_kind == "fuzzy":
            match_confidence = 0.7
        else:
            match_confidence = 0.5

        # Data completeness check
        required_fields = [
            "payment_type", "transaction_id", "amount", "currency",
            "method", "purpose", "sender", "receiver"
        ]
        complete = all(payment_info.get(k) not in (None, "", {}) for k in required_fields)
        completeness = 1.0 if complete else 0.7

        # History consistency
        history_conf = 0.9 if purpose_upper in self.intent_mappings else 0.8

        confidence = (
            (match_confidence ** 0.5) *
            (completeness ** 0.3) *
            (history_conf ** 0.2)
        )

        return round(min(max(confidence, 0.0), 1.0), 2)
    
    def _is_unusual_purpose(self, purpose: str, intent: str) -> bool:
        """
        Check if the purpose string contains unusual or suspicious patterns.
        
        Args:
            purpose: Payment purpose string
            intent: Classified intent
            
        Returns:
            True if purpose is unusual
        """
        unusual_patterns = [
            r"urgent", r"emergency", r"asap", r"immediate",
            r"cash", r"cash advance", r"personal",
            r"gift", r"donation", r"charity",
            r"offshore", r"tax haven", r"shell",
            r"consulting", r"advisory", r"management fee"
        ]
        
        purpose_lower = purpose.lower()
        for pattern in unusual_patterns:
            if re.search(pattern, purpose_lower):
                return True
        
        return False
    
    def _is_international_payment(self, location: Dict, sender: Dict, receiver: Dict) -> bool:
        """
        Check if payment is international based on location and bank data.
        
        Args:
            location: Location information
            sender: Sender information
            receiver: Receiver information
            
        Returns:
            True if payment appears international
        """
        # Check location
        city = location.get("city", "").upper()
        international_cities = ["LONDON", "NEW YORK", "SINGAPORE", "DUBAI", "HONG KONG", "TOKYO"]
        if city in international_cities:
            return True
        
        # Check bank names for international indicators
        sender_bank = sender.get("bank_name", "").upper()
        receiver_bank = receiver.get("bank_name", "").upper()
        
        international_banks = ["SWIFT", "CHASE", "CITIBANK", "HSBC", "DEUTSCHE", "BARCLAYS"]
        for bank in international_banks:
            if bank in sender_bank or bank in receiver_bank:
                return True
        
        return False
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """
        Determine risk level based on risk score.
        
        Args:
            risk_score: Calculated risk score
            
        Returns:
            Risk level classification
        """
        if risk_score >= self.risk_thresholds["CRITICAL"]:
            return "CRITICAL"
        elif risk_score >= self.risk_thresholds["HIGH"]:
            return "HIGH"
        elif risk_score >= self.risk_thresholds["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_workflow_id(self, intent: str, risk_level: str) -> str:
        """
        Get workflow ID for intent and risk level.
        
        Args:
            intent: Classified intent
            risk_level: Risk level
            
        Returns:
            Workflow ID
        """
        if intent in self.workflow_mappings:
            return self.workflow_mappings[intent].get(risk_level, "WF-DEFAULT")
        return "WF-DEFAULT"
    
    def _get_agent_pipeline(self, intent: str) -> List[str]:
        """
        Get agent pipeline for intent.
        
        Args:
            intent: Classified intent
            
        Returns:
            List of agent pipeline steps
        """
        return self.agent_pipelines.get(intent, ["PDR", "RCA", "CRRAK", "ARL"])
    
    def process_file(self, file_path: str, batch_id: str = None) -> Dict[str, Any]:
        """
        Process a JSON file and return classification results.
        
        Args:
            file_path: Path to the JSON file
            batch_id: Optional batch ID
            
        Returns:
            Classification results
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different data formats
            if isinstance(data, list):
                payments_data = data
            elif isinstance(data, dict) and "payments" in data:
                payments_data = data["payments"]
            else:
                payments_data = [data]  # Single payment object
            
            return self.process_payments(payments_data, batch_id)
            
        except Exception as e:
            return {
                "error": f"Failed to process file {file_path}: {str(e)}"
            }
    
    def get_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of classification results.
        
        Args:
            results: Classification results
            
        Returns:
            Summary statistics and insights
        """
        if "error" in results:
            return results
        
        intents = results.get("intents", [])
        intent_counts = {}
        risk_distribution = {}
        high_risk_payments = []
        
        for intent in intents:
            intent_type = intent["intent"]
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
            
            # Determine risk level from risk score
            risk_score = intent["risk_score"]
            if risk_score >= 0.8:
                risk_level = "CRITICAL"
            elif risk_score >= 0.5:
                risk_level = "HIGH"
            elif risk_score >= 0.3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # Collect high-risk payments for review
            if risk_level in ["HIGH", "CRITICAL"]:
                high_risk_payments.append({
                    "line_id": intent["line_id"],
                    "intent": intent_type,
                    "risk_score": risk_score,
                    "confidence": intent["confidence"]
                })
        
        return {
            "total_payments": len(intents),
            "intent_distribution": intent_counts,
            "risk_distribution": risk_distribution,
            "high_risk_payments": high_risk_payments,
            "workflow_count": len(results.get("workflow_ids", [])),
            "agent_pipeline_steps": len(results.get("agent_pipeline", [])),
            "batch_id": results.get("batch_id"),
            "policy_version": results.get("policy_version"),
            "requires_manual_review": len(high_risk_payments) > 0,
            "manual_review_count": len(high_risk_payments)
        }

def main():
    """
    Main function to demonstrate Intent Manager usage.
    This is the single entry point for the agentic AI system.
    """
    print("🤖 Intent Manager - Agentic AI for Payment Classification")
    print("=" * 60)
    
    # Initialize Intent Manager
    intent_manager = IntentManager()
    
    # Process the sample JSON file
    print("📁 Processing arealis_payment_samples_for_intent_manger_1.json...")
    results = intent_manager.process_file("arealis_payment_samples_for_intent_manger_1.json", "B-2025-09-30-01")
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Get and display comprehensive summary
    summary = intent_manager.get_summary(results)
    
    print(f"\n📊 Classification Summary:")
    print("=" * 60)
    print(f"✅ Total Payments: {summary['total_payments']}")
    print(f"📈 Intent Distribution: {summary['intent_distribution']}")
    print(f"⚠️  Risk Distribution: {summary['risk_distribution']}")
    print(f"🔄 Workflow IDs: {summary['workflow_count']}")
    print(f"🤖 Agent Pipeline Steps: {summary['agent_pipeline_steps']}")
    print(f"👤 Requires Manual Review: {summary['requires_manual_review']}")
    print(f"📋 Manual Review Count: {summary['manual_review_count']}")
    
    # Show high-risk payments if any
    if summary['high_risk_payments']:
        print(f"\n⚠️  High Risk Payments Requiring Review:")
        print("-" * 60)
        for payment in summary['high_risk_payments'][:5]:  # Show first 5
            print(f"  {payment['line_id']}: {payment['intent']} | Risk: {payment['risk_score']} | Confidence: {payment['confidence']}")
        if len(summary['high_risk_payments']) > 5:
            print(f"  ... and {len(summary['high_risk_payments']) - 5} more high-risk payments")
    
    # Save results to file
    output_file = f"intent_manager_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {output_file}")
    
    print("\n🎉 Intent Manager Processing Complete!")
    print("🤖 Agentic AI has successfully classified all payments and routed them to appropriate workflows!")

if __name__ == "__main__":
    main()