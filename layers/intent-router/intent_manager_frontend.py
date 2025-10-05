"""
Intent Manager Frontend - Arealis Gateway v2

Updated Intent Manager to process frontend transaction data with new schema.
Integrates with bank API context and aligns with MCP orchestration system.

Purpose: Analyze frontend-provided transaction data to classify intents and set workflows.
Focus: Intent classification for downstream agents, not full compliance or routing.
"""

import json
import re
import boto3
import psycopg2
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TransactionData:
    """Transaction data structure from frontend."""
    transaction_id: str
    request_uuid: str
    source_reference_number: str
    transaction_type: str
    timestamp: str
    amount: float
    currency: str
    remitter: Dict[str, Any]
    beneficiary: Dict[str, Any]
    response: Dict[str, Any]
    additional_details: Dict[str, Any]
    processing_time_ms: int

class IntentManagerFrontend:
    """
    Intent Manager for Frontend Transaction Data
    
    Processes frontend-uploaded transaction data to classify intents
    and set workflows for downstream agent orchestration.
    """
    
    def __init__(self):
        """Initialize Intent Manager with storage and configuration."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = "arealis-invoices"
        self.processed_prefix = "invoices/processed"
        
        # PostgreSQL connection
        self.db_config = {
            'host': 'localhost',
            'database': 'arealis_gateway',
            'user': 'postgres',
            'password': 'password'
        }
        
        # Intent classification mappings
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
            "CREDIT": "LOAN_DISBURSEMENTS"
        }
        
        # Workflow mappings
        self.workflow_mappings = {
            "VENDOR_PAYMENTS": "WF-VENDOR-DOMESTIC",
            "PAYROLL": "WF-PAYROLL-DOMESTIC",
            "TAX_PAYMENTS": "WF-TAX-DOMESTIC",
            "UTILITY_PAYMENTS": "WF-UTILITY-DOMESTIC",
            "LOAN_DISBURSEMENTS": "WF-LOAN-DOMESTIC"
        }
        
        # Agent pipeline mappings
        self.pipeline_mappings = {
            "VENDOR_PAYMENTS": ["PDR", "Execution", "ARL", "CRRAK"],
            "PAYROLL": ["PDR", "Execution", "ARL", "CRRAK"],
            "TAX_PAYMENTS": ["PDR", "Execution", "ARL", "CRRAK"],
            "UTILITY_PAYMENTS": ["PDR", "Execution", "ARL", "CRRAK"],
            "LOAN_DISBURSEMENTS": ["PDR", "Execution", "ARL", "CRRAK"]
        }
        
        # Risk scoring thresholds
        self.risk_thresholds = {
            "high_amount": 1000000,  # 10 lakhs
            "medium_amount": 100000,  # 1 lakh
            "low_amount": 10000      # 10k
        }
        
        # Confidence scoring factors
        self.confidence_factors = {
            "bank_validation": 0.3,
            "amount_consistency": 0.2,
            "transaction_type": 0.2,
            "remarks_analysis": 0.3
        }
    
    async def process_frontend_data(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process frontend transaction data to classify intents.
        
        Args:
            frontend_data: Frontend transaction data with metadata and transactions
            
        Returns:
            Intent classification results
        """
        try:
            logger.info("Processing frontend transaction data")
            
            # Extract metadata
            metadata = frontend_data.get('metadata', {})
            transactions = frontend_data.get('transactions', [])
            policy_version = frontend_data.get('policy_version', 'intent-2.0.0')
            
            # Generate batch ID from metadata
            batch_id = self._generate_batch_id(metadata)
            tenant_id = self._extract_tenant_id(transactions)
            
            # Process each transaction
            intents = []
            for transaction in transactions:
                try:
                    intent_result = await self._classify_transaction(transaction, batch_id, tenant_id)
                    intents.append(intent_result)
                except Exception as e:
                    logger.error(f"Failed to classify transaction {transaction.get('transactionId', 'unknown')}: {str(e)}")
                    intents.append({
                        "line_id": transaction.get('transactionId', 'unknown'),
                        "intent": "UNKNOWN",
                        "risk_score": 1.0,
                        "confidence": 0.0,
                        "decision": "FAIL",
                        "reasons": ["CLASSIFICATION_ERROR"],
                        "error": str(e)
                    })
            
            # Determine primary workflow
            primary_workflow = self._determine_primary_workflow(intents)
            
            # Create consolidated result
            result = {
                "batch_id": batch_id,
                "tenant_id": tenant_id,
                "source": "FRONTEND_UPLOAD",
                "policy_version": policy_version,
                "upload_ts": datetime.now().isoformat() + "Z",
                "intents": intents,
                "workflow_id": primary_workflow,
                "timestamp": datetime.now().isoformat() + "Z"
            }
            
            # Store results
            await self._store_results(result)
            
            logger.info(f"Successfully processed {len(transactions)} transactions")
            return result
            
        except Exception as e:
            logger.error(f"Error processing frontend data: {str(e)}")
            return {"error": str(e)}
    
    async def _classify_transaction(self, transaction: Dict[str, Any], batch_id: str, tenant_id: str) -> Dict[str, Any]:
        """Classify intent for a single transaction."""
        try:
            # Extract transaction data
            transaction_id = transaction.get('transactionId', 'unknown')
            amount = float(transaction.get('amount', 0))
            transaction_type = transaction.get('transactionType', '')
            remarks = transaction.get('additionalDetails', {}).get('remarks', '')
            response = transaction.get('response', {})
            
            # Parse transaction data
            tx_data = TransactionData(
                transaction_id=transaction_id,
                request_uuid=transaction.get('requestUUID', ''),
                source_reference_number=transaction.get('sourceReferenceNumber', ''),
                transaction_type=transaction_type,
                timestamp=transaction.get('timestamp', ''),
                amount=amount,
                currency=transaction.get('currency', 'INR'),
                remitter=transaction.get('remitter', {}),
                beneficiary=transaction.get('beneficiary', {}),
                response=response,
                additional_details=transaction.get('additionalDetails', {}),
                processing_time_ms=transaction.get('processingTimeMs', 0)
            )
            
            # Classify intent
            intent = self._classify_intent(tx_data)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(tx_data)
            
            # Calculate confidence
            confidence = self._calculate_confidence(tx_data)
            
            # Determine decision
            decision = self._determine_decision(risk_score, confidence)
            
            # Get workflow and pipeline
            workflow_id = self._get_workflow_id(intent, decision)
            pipeline = self._get_agent_pipeline(intent, decision)
            
            # Bank validation
            bank_validation = self._extract_bank_validation(response)
            
            # Generate evidence reference
            evidence_ref = f"s3://{self.bucket_name}/{self.processed_prefix}/{tenant_id}/{batch_id}/{transaction_id}.json"
            
            # Summarize remarks
            remarks_summary = self._summarize_remarks(remarks)
            
            return {
                "line_id": transaction_id,
                "intent": intent,
                "risk_score": round(risk_score, 2),
                "confidence": round(confidence, 2),
                "validation": bank_validation,
                "evidence_ref": evidence_ref,
                "remarks_summary": remarks_summary,
                "workflow_id": workflow_id,
                "agent_pipeline": pipeline,
                "decision": decision,
                "reasons": self._get_decision_reasons(risk_score, confidence, decision)
            }
            
        except Exception as e:
            logger.error(f"Failed to classify transaction: {str(e)}")
            raise
    
    def _classify_intent(self, tx_data: TransactionData) -> str:
        """Classify intent based on transaction data."""
        try:
            # Analyze remarks for intent keywords
            remarks = tx_data.additional_details.get('remarks', '').upper()
            narration = tx_data.additional_details.get('narration', '').upper()
            
            # Check for explicit intent keywords
            for keyword, intent in self.intent_mappings.items():
                if keyword in remarks or keyword in narration:
                    return intent
            
            # Analyze amount patterns
            amount = tx_data.amount
            
            # Large amounts (>10 lakhs) likely vendor payments
            if amount > self.risk_thresholds['high_amount']:
                return "VENDOR_PAYMENTS"
            
            # Medium amounts (1-10 lakhs) with specific patterns
            elif amount > self.risk_thresholds['medium_amount']:
                # Check for payroll patterns (round numbers, specific amounts)
                if self._is_payroll_pattern(amount, remarks):
                    return "PAYROLL"
                else:
                    return "VENDOR_PAYMENTS"
            
            # Small amounts (<1 lakh) with utility patterns
            elif amount < self.risk_thresholds['medium_amount']:
                if self._is_utility_pattern(remarks, narration):
                    return "UTILITY_PAYMENTS"
                elif self._is_payroll_pattern(amount, remarks):
                    return "PAYROLL"
                else:
                    return "VENDOR_PAYMENTS"
            
            # Default to vendor payments
            return "VENDOR_PAYMENTS"
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return "UNKNOWN"
    
    def _is_payroll_pattern(self, amount: float, remarks: str) -> bool:
        """Check if transaction matches payroll patterns."""
        # Round number amounts (no decimals)
        if amount == int(amount):
            # Check for salary-related keywords
            salary_keywords = ['SALARY', 'PAYROLL', 'WAGES', 'EMPLOYEE', 'STAFF']
            return any(keyword in remarks.upper() for keyword in salary_keywords)
        return False
    
    def _is_utility_pattern(self, remarks: str, narration: str) -> bool:
        """Check if transaction matches utility payment patterns."""
        utility_keywords = ['ELECTRICITY', 'WATER', 'GAS', 'INTERNET', 'UTILITY', 'BILL']
        combined_text = f"{remarks} {narration}".upper()
        return any(keyword in combined_text for keyword in utility_keywords)
    
    def _calculate_risk_score(self, tx_data: TransactionData) -> float:
        """Calculate risk score for transaction."""
        try:
            amount = tx_data.amount
            response = tx_data.response
            
            # Amount-based risk
            if amount > self.risk_thresholds['high_amount']:
                amount_risk = 0.8
            elif amount > self.risk_thresholds['medium_amount']:
                amount_risk = 0.5
            else:
                amount_risk = 0.2
            
            # Transaction type risk
            tx_type = tx_data.transaction_type
            if tx_type in ['RTGS', 'NEFT']:
                tx_risk = 0.1  # Lower risk for formal channels
            elif tx_type in ['IMPS', 'IFT']:
                tx_risk = 0.3  # Medium risk for instant transfers
            else:
                tx_risk = 0.5  # Higher risk for unknown types
            
            # Bank response risk
            is_success = response.get('isSuccess', False)
            response_code = response.get('responseCode', '')
            
            if not is_success or response_code != '00':
                bank_risk = 0.8  # High risk for failed transactions
            else:
                bank_risk = 0.1  # Low risk for successful transactions
            
            # Calculate weighted risk score
            risk_score = (
                0.4 * amount_risk +
                0.3 * tx_risk +
                0.3 * bank_risk
            )
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Risk calculation failed: {str(e)}")
            return 0.5  # Default medium risk
    
    def _calculate_confidence(self, tx_data: TransactionData) -> float:
        """Calculate confidence score for transaction."""
        try:
            response = tx_data.response
            remarks = tx_data.additional_details.get('remarks', '')
            
            # Bank validation confidence
            is_success = response.get('isSuccess', False)
            response_code = response.get('responseCode', '')
            utr_number = response.get('utrNumber', '')
            
            if is_success and response_code == '00' and utr_number:
                bank_confidence = 0.95
            elif is_success and response_code == '00':
                bank_confidence = 0.85
            else:
                bank_confidence = 0.5
            
            # Amount consistency confidence
            amount = tx_data.amount
            if amount > 0 and amount < 10000000:  # Reasonable amount range
                amount_confidence = 0.9
            else:
                amount_confidence = 0.6
            
            # Transaction type confidence
            tx_type = tx_data.transaction_type
            if tx_type in ['RTGS', 'NEFT', 'IMPS', 'IFT']:
                tx_confidence = 0.9
            else:
                tx_confidence = 0.7
            
            # Remarks analysis confidence
            if remarks and len(remarks) > 10:
                remarks_confidence = 0.8
            else:
                remarks_confidence = 0.6
            
            # Calculate weighted confidence
            confidence = (
                self.confidence_factors['bank_validation'] * bank_confidence +
                self.confidence_factors['amount_consistency'] * amount_confidence +
                self.confidence_factors['transaction_type'] * tx_confidence +
                self.confidence_factors['remarks_analysis'] * remarks_confidence
            )
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {str(e)}")
            return 0.5  # Default medium confidence
    
    def _determine_decision(self, risk_score: float, confidence: float) -> str:
        """Determine decision based on risk and confidence."""
        if risk_score > 0.7:
            return "FAIL"
        elif risk_score > 0.4 or confidence < 0.7:
            return "HOLD"
        else:
            return "PASS"
    
    def _get_workflow_id(self, intent: str, decision: str) -> str:
        """Get workflow ID based on intent and decision."""
        base_workflow = self.workflow_mappings.get(intent, "WF-DEFAULT")
        
        if decision == "HOLD":
            return base_workflow.replace("DOMESTIC", "HOLD")
        elif decision == "FAIL":
            return base_workflow.replace("DOMESTIC", "FAIL")
        
        return base_workflow
    
    def _get_agent_pipeline(self, intent: str, decision: str) -> List[str]:
        """Get agent pipeline based on intent and decision."""
        base_pipeline = self.pipeline_mappings.get(intent, ["PDR", "Execution", "ARL", "CRRAK"])
        
        if decision == "HOLD":
            return ["PDR", "RCA", "CRRAK"]  # RCA for hold analysis
        elif decision == "FAIL":
            return ["RCA", "CRRAK"]  # RCA for failure analysis
        
        return base_pipeline
    
    def _extract_bank_validation(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract bank validation information."""
        return {
            "responseCode": response.get('responseCode', ''),
            "isSuccess": response.get('isSuccess', False),
            "utrNumber": response.get('utrNumber', ''),
            "message": response.get('message', ''),
            "retrievalReferenceNo": response.get('retrievalReferenceNo', '')
        }
    
    def _summarize_remarks(self, remarks: str) -> str:
        """Summarize remarks for intent classification."""
        if not remarks:
            return "NO_REMARKS"
        
        # Extract key intent keywords
        remarks_upper = remarks.upper()
        for keyword, intent in self.intent_mappings.items():
            if keyword in remarks_upper:
                return intent
        
        # Default summary
        if len(remarks) > 50:
            return remarks[:50] + "..."
        return remarks
    
    def _get_decision_reasons(self, risk_score: float, confidence: float, decision: str) -> List[str]:
        """Get reasons for the decision."""
        reasons = []
        
        if decision == "PASS":
            reasons.extend(["BANK_VALIDATION_OK", "AMOUNT_WITHIN_LIMITS"])
        elif decision == "HOLD":
            if confidence < 0.7:
                reasons.append("LOW_CONFIDENCE")
            if risk_score > 0.4:
                reasons.append("ELEVATED_RISK")
        elif decision == "FAIL":
            if risk_score > 0.7:
                reasons.append("HIGH_RISK")
            if confidence < 0.5:
                reasons.append("LOW_CONFIDENCE")
        
        return reasons
    
    def _generate_batch_id(self, metadata: Dict[str, Any]) -> str:
        """Generate batch ID from metadata."""
        start_date = metadata.get('startDate', '')
        if start_date:
            date_part = start_date.split('T')[0].replace('-', '')
            return f"B-{date_part}-01"
        return f"B-{datetime.now().strftime('%Y-%m-%d')}-01"
    
    def _extract_tenant_id(self, transactions: List[Dict[str, Any]]) -> str:
        """Extract tenant ID from transactions."""
        if transactions:
            # Try to extract from remitter bank
            first_tx = transactions[0]
            remitter = first_tx.get('remitter', {})
            bank_name = remitter.get('bankName', '')
            
            # Map bank names to tenant IDs
            bank_mapping = {
                'AXIS': 'AXIS',
                'ICICI': 'ICICI',
                'HDFC': 'HDFC',
                'SBI': 'SBI',
                'BOI': 'BOI'
            }
            
            for bank, tenant in bank_mapping.items():
                if bank in bank_name.upper():
                    return tenant
        
        return "UNKNOWN"
    
    async def _store_results(self, result: Dict[str, Any]) -> None:
        """Store intent classification results."""
        try:
            # Store in PostgreSQL
            await self._store_in_postgresql(result)
            
            # Store in S3
            await self._store_in_s3(result)
            
            logger.info(f"Stored results for batch {result['batch_id']}")
            
        except Exception as e:
            logger.error(f"Failed to store results: {str(e)}")
            raise
    
    async def _store_in_postgresql(self, result: Dict[str, Any]) -> None:
        """Store results in PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Store batch metadata
            cursor.execute("""
                INSERT INTO invoices (batch_id, tenant_id, invoice_ref, source, policy_version, upload_ts, validation_status, issues)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (batch_id) DO UPDATE SET
                    validation_status = EXCLUDED.validation_status,
                    issues = EXCLUDED.issues
            """, (
                result['batch_id'],
                result['tenant_id'],
                f"INV-{result['batch_id']}",
                result['source'],
                result['policy_version'],
                result['upload_ts'],
                'VALID',
                json.dumps([])
            ))
            
            # Store intent results
            for intent in result['intents']:
                cursor.execute("""
                    INSERT INTO intent_results (
                        batch_id, line_id, intent, risk_score, confidence, decision,
                        workflow_id, agent_pipeline, axis_validation, evidence_ref, reasons, override
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (batch_id, line_id) DO UPDATE SET
                        intent = EXCLUDED.intent,
                        risk_score = EXCLUDED.risk_score,
                        confidence = EXCLUDED.confidence,
                        decision = EXCLUDED.decision,
                        workflow_id = EXCLUDED.workflow_id,
                        agent_pipeline = EXCLUDED.agent_pipeline,
                        axis_validation = EXCLUDED.axis_validation,
                        evidence_ref = EXCLUDED.evidence_ref,
                        reasons = EXCLUDED.reasons,
                        override = EXCLUDED.override
                """, (
                    result['batch_id'],
                    intent['line_id'],
                    intent['intent'],
                    intent['risk_score'],
                    intent['confidence'],
                    intent['decision'],
                    intent.get('workflow_id'),
                    json.dumps(intent.get('agent_pipeline', [])),
                    json.dumps(intent.get('validation', {})),
                    intent.get('evidence_ref'),
                    json.dumps(intent.get('reasons', [])),
                    False
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store in PostgreSQL: {str(e)}")
            raise
    
    async def _store_in_s3(self, result: Dict[str, Any]) -> None:
        """Store results in S3."""
        try:
            batch_id = result['batch_id']
            tenant_id = result['tenant_id']
            
            # Store individual intent results
            for intent in result['intents']:
                line_id = intent['line_id']
                s3_key = f"{self.processed_prefix}/{tenant_id}/{batch_id}/{line_id}.json"
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=json.dumps(intent, indent=2),
                    ContentType='application/json',
                    ServerSideEncryption='aws:kms'
                )
            
            # Store complete batch result
            batch_key = f"{self.processed_prefix}/{tenant_id}/{batch_id}/batch.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=batch_key,
                Body=json.dumps(result, indent=2),
                ContentType='application/json',
                ServerSideEncryption='aws:kms'
            )
            
        except Exception as e:
            logger.error(f"Failed to store in S3: {str(e)}")
            raise

# Example usage
async def main():
    """Example usage of IntentManagerFrontend."""
    intent_manager = IntentManagerFrontend()
    
    # Example frontend data
    frontend_data = {
        "metadata": {
            "generatedAt": "2025-10-04T14:25:00.247363",
            "startDate": "2024-10-01T00:00:00",
            "endDate": "2024-10-30T00:00:00",
            "totalDays": 30,
            "totalTransactions": 30381,
            "averageTransactionsPerDay": 1012.7,
            "transactionTypes": {
                "IMPS": 7549,
                "NEFT": 7443,
                "RTGS": 7675,
                "IFT": 7714
            },
            "successRate": 94.95079161317929,
            "totalVolume": 235464634375
        },
        "transactions": [
            {
                "transactionId": "TXN20241001000001",
                "requestUUID": "111b3f60-c34a-43f0-8f28-e9b6a68e76ae",
                "sourceReferenceNumber": "SRN119549372",
                "transactionType": "IFT",
                "timestamp": "2024-10-01T16:34:36",
                "transactionDate": "01102024163436",
                "amount": 922288,
                "currency": "INR",
                "channelId": "BRANCH",
                "txnInitChannel": "API",
                "remitter": {
                    "accountNumber": "62908824712",
                    "accountHolderName": "Zashil Rajan",
                    "mobileNumber": "919886328298",
                    "email": "asur@example.org",
                    "bankName": "Bank of India",
                    "ifscCode": "BKID0909973"
                },
                "beneficiary": {
                    "accountNumber": "939070055817085",
                    "accountHolderName": "Yagnesh Murthy",
                    "bankName": "Union Bank of India",
                    "ifscCode": "UBIN0806977"
                },
                "response": {
                    "responseCode": "00",
                    "isSuccess": True,
                    "message": "The Transaction is Successfully Completed",
                    "utrNumber": "IFT20241001822314",
                    "retrievalReferenceNo": "723721653729"
                },
                "additionalDetails": {
                    "remarks": "Vendor Payment for Services",
                    "narration": "Payment to supplier",
                    "serviceRequestId": "NB.GEN.SVC.ENQ",
                    "serviceRequestVersion": "1.0",
                    "checksum": "4704801997"
                },
                "processingTimeMs": 1619
            }
        ],
        "policy_version": "intent-2.0.0"
    }
    
    # Process frontend data
    result = await intent_manager.process_frontend_data(frontend_data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
