"""
IntentManager Integration - Arealis Gateway v2 Ingest Layer

Updated IntentManager that fetches data from S3 and PostgreSQL
as part of the complete ingest-to-intent workflow.

Input: Batch ID from validated invoices
Output: Intent classification results
"""

import json
import boto3
import psycopg2
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentManagerIntegration:
    """
    Updated IntentManager that integrates with S3 and PostgreSQL storage.
    
    Fetches validated invoice data from storage systems and processes
    through intent classification workflow.
    """
    
    def __init__(self):
        """Initialize IntentManagerIntegration with storage connections."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = "arealis-invoices"
        self.processed_prefix = "invoices/processed"
        
        # Master Control Service URL
        self.master_control_url = "http://localhost:8000"
        
        # PostgreSQL connection
        self.db_config = {
            'host': 'localhost',
            'database': 'arealis_gateway',
            'user': 'postgres',
            'password': 'password'
        }
        
        # Intent mappings (from original IntentManager)
        self.intent_mappings = {
            "VENDOR_PAYMENT": "VENDOR_PAYMENTS",
            "PAYROLL": "PAYROLL",
            "SALARY": "PAYROLL",
            "TAX_PAYMENT": "TAX_PAYMENTS",
            "UTILITY_PAYMENT": "UTILITY_PAYMENTS",
            "LOAN_DISBURSEMENT": "LOAN_DISBURSEMENTS"
        }
        
        # Workflow mappings
        self.workflow_mappings = {
            "VENDOR_PAYMENTS": "WF-VENDOR-DOMESTIC",
            "PAYROLL": "WF-PAYROLL-DOMESTIC",
            "TAX_PAYMENTS": "WF-TAX-DOMESTIC",
            "UTILITY_PAYMENTS": "WF-UTILITY-DOMESTIC",
            "LOAN_DISBURSEMENTS": "WF-LOAN-DOMESTIC"
        }
        
        # Agent pipeline mappings (updated for new service architecture)
        self.pipeline_mappings = {
            "VENDOR_PAYMENTS": ["PDR", "CRRAK", "ARL"],
            "PAYROLL": ["PDR", "CRRAK", "ARL"],
            "TAX_PAYMENTS": ["PDR", "CRRAK", "ARL"],
            "UTILITY_PAYMENTS": ["PDR", "CRRAK", "ARL"],
            "LOAN_DISBURSEMENTS": ["PDR", "CRRAK", "ARL"]
        }
    
    async def process_batch_from_storage(self, batch_id: str) -> Dict[str, Any]:
        """
        Process batch from S3 and PostgreSQL storage.
        
        Args:
            batch_id: Batch identifier to process
            
        Returns:
            Intent classification results
        """
        try:
            logger.info(f"Processing batch {batch_id} from storage")
            
            # Fetch batch metadata from PostgreSQL
            batch_metadata = await self._fetch_batch_metadata(batch_id)
            if not batch_metadata:
                return {"error": f"Batch {batch_id} not found"}
            
            # Fetch invoice lines from PostgreSQL
            invoice_lines = await self._fetch_invoice_lines(batch_id)
            if not invoice_lines:
                return {"error": f"No lines found for batch {batch_id}"}
            
            # Process each line through intent classification
            intents = []
            all_workflows = set()
            all_pipelines = set()
            
            for line in invoice_lines:
                # Fetch additional data from S3 if needed
                s3_data = await self._fetch_s3_line_data(line.get('evidence_ref'))
                
                # Classify intent
                intent_result = await self._classify_intent(line, s3_data)
                intents.append(intent_result)
                
                # Collect workflows and pipelines
                all_workflows.add(intent_result.get('workflow_id'))
                all_pipelines.update(intent_result.get('agent_pipeline', []))
            
            # Create consolidated result
            result = {
                "batch_id": batch_id,
                "intents": intents,
                "workflow_id": list(all_workflows)[0] if all_workflows else "WF-DEFAULT",
                "agent_pipeline": list(all_pipelines),
                "policy_version": batch_metadata.get('policy_version', 'intent-2.0.0'),
                "timestamp": datetime.now().isoformat() + "Z",
                "status": "PROCESSING"
            }
            
            # Store results in PostgreSQL
            await self._store_intent_results(result)
            
            # Trigger Master Control workflow for each intent
            workflow_results = []
            for intent in intents:
                try:
                    workflow_result = await self._trigger_master_control_workflow(
                        batch_id, intent, list(all_pipelines)
                    )
                    workflow_results.append(workflow_result)
                except Exception as e:
                    logger.error(f"Failed to trigger workflow for {intent['line_id']}: {e}")
                    workflow_results.append({
                        "line_id": intent['line_id'],
                        "status": "ERROR",
                        "error": str(e)
                    })
            
            result["workflow_results"] = workflow_results
            
            logger.info(f"Successfully processed batch {batch_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_batch_metadata(self, batch_id: str) -> Optional[Dict]:
        """Fetch batch metadata from PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT batch_id, tenant_id, invoice_ref, source, policy_version, 
                       upload_ts, validation_status, issues
                FROM invoices 
                WHERE batch_id = %s
            """, (batch_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    "batch_id": row[0],
                    "tenant_id": row[1],
                    "invoice_ref": row[2],
                    "source": row[3],
                    "policy_version": row[4],
                    "upload_ts": row[5].isoformat() + "Z" if row[5] else None,
                    "validation_status": row[6],
                    "issues": json.loads(row[7]) if row[7] else []
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch batch metadata: {str(e)}")
            return None
    
    async def _fetch_invoice_lines(self, batch_id: str) -> List[Dict]:
        """Fetch invoice lines from PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT line_id, transaction_type, amount, currency, purpose,
                       debit_account_number, credit_account_number, credit_ifsc,
                       source_reference_number, remarks, transaction_date, evidence_ref, status
                FROM invoice_lines 
                WHERE batch_id = %s
                ORDER BY line_id
            """, (batch_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            lines = []
            for row in rows:
                lines.append({
                    "line_id": row[0],
                    "transaction_type": row[1],
                    "amount": float(row[2]) if row[2] else 0,
                    "currency": row[3],
                    "purpose": row[4],
                    "debit_account_number": row[5],
                    "credit_account_number": row[6],
                    "credit_ifsc": row[7],
                    "source_reference_number": row[8],
                    "remarks": row[9],
                    "transaction_date": row[10].isoformat() + "Z" if row[10] else None,
                    "evidence_ref": row[11],
                    "status": row[12]
                })
            
            return lines
            
        except Exception as e:
            logger.error(f"Failed to fetch invoice lines: {str(e)}")
            return []
    
    async def _fetch_s3_line_data(self, evidence_ref: Optional[str]) -> Dict:
        """Fetch additional line data from S3 if available."""
        if not evidence_ref:
            return {}
        
        try:
            # Extract S3 key from evidence_ref
            if evidence_ref.startswith('s3://'):
                key = evidence_ref.replace(f's3://{self.bucket_name}/', '')
            else:
                return {}
            
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(response['Body'].read())
            
        except Exception as e:
            logger.warning(f"Failed to fetch S3 data: {str(e)}")
            return {}
    
    async def _classify_intent(self, line: Dict, s3_data: Dict) -> Dict:
        """Classify intent for a single line."""
        try:
            # Extract line information
            line_id = line['line_id']
            amount = line['amount']
            purpose = line['purpose'].upper()
            currency = line['currency']
            
            # Classify intent
            intent = self.intent_mappings.get(purpose, "UNKNOWN")
            
            # Calculate risk score (simplified version)
            risk_score = self._calculate_risk_score(line, s3_data)
            
            # Calculate confidence
            confidence = self._calculate_confidence(line, s3_data)
            
            # Determine decision
            decision = self._determine_decision(risk_score, confidence)
            
            # Get workflow and pipeline
            workflow_id = self._get_workflow_id(intent, decision)
            pipeline = self._get_agent_pipeline(intent, decision)
            
            # Mock Axis API validation
            axis_validation = {
                "code": "00",
                "result": "Success",
                "utrNumber": f"25-{datetime.now().strftime('%d%m%H%M')}-{line_id.split('-')[1]}"
            }
            
            # Determine reasons
            reasons = self._get_decision_reasons(risk_score, confidence, decision)
            
            return {
                "line_id": line_id,
                "intent": intent,
                "risk_score": round(risk_score, 2),
                "confidence": round(confidence, 2),
                "axis_validation": axis_validation,
                "evidence_ref": line.get('evidence_ref'),
                "decision": decision,
                "reasons": reasons,
                "override": False,
                "workflow_id": workflow_id,
                "agent_pipeline": pipeline
            }
            
        except Exception as e:
            logger.error(f"Failed to classify intent for line {line.get('line_id')}: {str(e)}")
            return {
                "line_id": line.get('line_id', 'unknown'),
                "intent": "UNKNOWN",
                "risk_score": 1.0,
                "confidence": 0.0,
                "decision": "FAIL",
                "reasons": ["CLASSIFICATION_ERROR"],
                "error": str(e)
            }
    
    def _calculate_risk_score(self, line: Dict, s3_data: Dict) -> float:
        """Calculate risk score for a line."""
        amount = line['amount']
        
        # Amount-based risk (threshold: 100,000)
        amount_risk = min(1.0, amount / 100000.0)
        
        # Zone risk (simplified)
        zone_risk = 0.1  # Assume domestic
        
        # Purpose risk
        purpose = line['purpose'].upper()
        purpose_risk = 0.1 if purpose in self.intent_mappings else 0.2
        
        # Account risk (simplified)
        account_risk = 0.0
        
        # Calculate final risk score
        risk_score = (
            0.4 * amount_risk +
            0.2 * zone_risk +
            0.25 * purpose_risk +
            0.15 * account_risk
        )
        
        return min(1.0, risk_score)
    
    def _calculate_confidence(self, line: Dict, s3_data: Dict) -> float:
        """Calculate confidence score for a line."""
        purpose = line['purpose'].upper()
        
        # Match confidence
        match_confidence = 0.9 if purpose in self.intent_mappings else 0.7
        
        # Completeness
        completeness = 1.0
        
        # Account confidence
        account_conf = 0.95
        
        # Calculate final confidence
        confidence = (
            (match_confidence ** 0.5) *
            (completeness ** 0.3) *
            (account_conf ** 0.2)
        )
        
        return min(1.0, confidence)
    
    def _determine_decision(self, risk_score: float, confidence: float) -> str:
        """Determine decision based on risk and confidence."""
        if risk_score > 0.5:
            return "FAIL"
        elif risk_score > 0.3 or confidence < 0.85:
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
        base_pipeline = self.pipeline_mappings.get(intent, ["PDR", "CRRAK", "ARL"])
        
        if decision == "HOLD":
            return ["PDR", "RCA", "CRRAK"]  # RCA for analysis of hold reasons
        elif decision == "FAIL":
            return ["RCA", "CRRAK"]  # RCA for failure analysis, CRRAK for compliance
        
        return base_pipeline
    
    def _get_decision_reasons(self, risk_score: float, confidence: float, decision: str) -> List[str]:
        """Get reasons for the decision."""
        reasons = []
        
        if decision == "PASS":
            reasons.extend(["KYC_OK", "LIMITS_OK"])
        elif decision == "HOLD":
            if confidence < 0.85:
                reasons.append("LOW_CONFIDENCE")
            if risk_score > 0.3:
                reasons.append("HIGH_RISK")
        elif decision == "FAIL":
            if risk_score > 0.5:
                reasons.append("LIMIT_EXCEEDED")
        
        return reasons
    
    async def _trigger_master_control_workflow(self, batch_id: str, intent: Dict, agent_pipeline: List[str]) -> Dict[str, Any]:
        """
        Trigger Master Control workflow for a single intent.
        
        Args:
            batch_id: Batch identifier
            intent: Intent classification result
            agent_pipeline: List of agents to execute
            
        Returns:
            Workflow execution result
        """
        try:
            # Create task request for Master Control
            task_request = {
                "task_type": "pdr",
                "batch_id": batch_id,
                "line_id": intent['line_id'],
                "amount": intent.get('amount', 250000),
                "currency": "INR",
                "status": intent.get('decision', 'PASS'),
                "evidence_ref": intent.get('evidence_ref')
            }
            
            # Create workflow event
            workflow_event = {
                "type": "workflow_selected",
                "batch_id": batch_id,
                "line_id": intent['line_id'],
                "agent_pipeline": agent_pipeline,
                "task_request": task_request,
                "timestamp": datetime.now().isoformat()
            }
            
            # Call Master Control service
            response = requests.post(
                f"{self.master_control_url}/orchestrate/event",
                json=workflow_event,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully triggered workflow for {intent['line_id']}")
                return {
                    "line_id": intent['line_id'],
                    "status": "SUCCESS",
                    "workflow_result": result
                }
            else:
                logger.error(f"Master Control returned status {response.status_code}")
                return {
                    "line_id": intent['line_id'],
                    "status": "ERROR",
                    "error": f"Master Control error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to trigger Master Control workflow: {e}")
            return {
                "line_id": intent['line_id'],
                "status": "ERROR",
                "error": str(e)
            }
    
    async def _store_intent_results(self, result: Dict[str, Any]) -> None:
        """Store intent classification results in PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
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
                    json.dumps(intent.get('axis_validation', {})),
                    intent.get('evidence_ref'),
                    json.dumps(intent.get('reasons', [])),
                    intent.get('override', False)
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Stored intent results for batch {result['batch_id']}")
            
        except Exception as e:
            logger.error(f"Failed to store intent results: {str(e)}")
            raise

# Example usage
async def main():
    """Example usage of IntentManagerIntegration."""
    integration = IntentManagerIntegration()
    
    # Process a batch
    result = await integration.process_batch_from_storage("B-2025-10-03-01")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
