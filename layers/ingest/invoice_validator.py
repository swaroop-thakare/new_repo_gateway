"""
InvoiceValidator - Arealis Gateway v2 Ingest Layer

Validates frontend-uploaded invoices and transforms them into standardized schema.
Stores validated data in PostgreSQL and S3 for IntentManager processing.

Input: Raw invoice data from FrontendIngestor
Output: Validated schema for IntentManager
"""

import json
import csv
import boto3
import psycopg2
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import re
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of invoice validation."""
    is_valid: bool
    issues: List[str]
    transformed_data: Optional[Dict] = None

class InvoiceValidator:
    """
    Invoice Validator Agent for Arealis Gateway v2
    
    Validates frontend-uploaded invoices and transforms them into
    standardized schema for IntentManager processing.
    """
    
    def __init__(self):
        """Initialize InvoiceValidator with S3 and PostgreSQL connections."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = "arealis-invoices"
        self.raw_prefix = "invoices/raw"
        self.processed_prefix = "invoices/processed"
        
        # PostgreSQL connection (configure via environment)
        self.db_config = {
            'host': 'localhost',  # Configure via environment
            'database': 'arealis_gateway',
            'user': 'postgres',
            'password': 'password'  # Configure via environment
        }
        
        # Required fields for validation
        self.required_fields = [
            'amount', 'debit_account', 'credit_account', 'currency'
        ]
        
        # Field validation patterns
        self.validation_patterns = {
            'ifsc': r'^[A-Z]{4}0[A-Z0-9]{6}$',
            'account_number': r'^\d{10,18}$',
            'currency': r'^[A-Z]{3}$'
        }
    
    async def validate_invoice(self, ingestion_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate invoice from FrontendIngestor output.
        
        Args:
            ingestion_result: Output from FrontendIngestor
            
        Returns:
            Validated invoice data in standardized schema
        """
        try:
            batch_id = ingestion_result['batch_id']
            tenant_id = ingestion_result['tenant_id']
            raw_file_key = ingestion_result['raw_file_key']
            
            logger.info(f"Validating invoice for batch {batch_id}")
            
            # Download raw file from S3
            raw_data = await self._download_raw_file(raw_file_key)
            
            # Parse file based on type
            parsed_data = await self._parse_uploaded_file(raw_data, ingestion_result['metadata'])
            
            # Validate data
            validation_result = await self._validate_data(parsed_data)
            
            if not validation_result.is_valid:
                logger.error(f"Validation failed for batch {batch_id}: {validation_result.issues}")
                return {
                    "batch_id": batch_id,
                    "tenant_id": tenant_id,
                    "validation_status": "FAILED",
                    "issues": validation_result.issues,
                    "error": "Validation failed"
                }
            
            # Transform to standardized schema
            transformed_data = await self._transform_to_schema(
                parsed_data, batch_id, tenant_id, ingestion_result
            )
            
            # Store in PostgreSQL
            await self._store_in_postgresql(transformed_data)
            
            # Store processed files in S3
            await self._store_processed_files(transformed_data)
            
            logger.info(f"Successfully validated and stored batch {batch_id}")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error validating invoice: {str(e)}")
            return {
                "batch_id": ingestion_result.get('batch_id', 'unknown'),
                "tenant_id": ingestion_result.get('tenant_id', 'unknown'),
                "validation_status": "ERROR",
                "error": str(e)
            }
    
    async def _download_raw_file(self, s3_key: str) -> bytes:
        """Download raw file from S3."""
        try:
            # Extract key from s3://bucket/key format
            key = s3_key.replace(f"s3://{self.bucket_name}/", "")
            
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Failed to download file from S3: {str(e)}")
            raise
    
    async def _parse_uploaded_file(self, content: bytes, metadata: Dict) -> List[Dict]:
        """Parse uploaded file based on type."""
        file_type = metadata.get('file_type', 'csv')
        
        if file_type == 'csv':
            return await self._parse_csv_content(content)
        elif file_type == 'json':
            return await self._parse_json_content(content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    async def _parse_csv_content(self, content: bytes) -> List[Dict]:
        """Parse CSV content into list of dictionaries."""
        try:
            text_content = content.decode('utf-8')
            lines = text_content.strip().split('\n')
            
            if not lines:
                return []
            
            # Parse headers
            headers = [h.strip() for h in lines[0].split(',')]
            
            # Parse data rows
            data = []
            for i, line in enumerate(lines[1:], 1):
                if line.strip():
                    values = [v.strip() for v in line.split(',')]
                    if len(values) == len(headers):
                        row_dict = dict(zip(headers, values))
                        row_dict['_line_number'] = i
                        data.append(row_dict)
            
            return data
        except Exception as e:
            logger.error(f"Failed to parse CSV: {str(e)}")
            raise
    
    async def _parse_json_content(self, content: bytes) -> List[Dict]:
        """Parse JSON content into list of dictionaries."""
        try:
            data = json.loads(content.decode('utf-8'))
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                raise ValueError("Invalid JSON structure")
        except Exception as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            raise
    
    async def _validate_data(self, parsed_data: List[Dict]) -> ValidationResult:
        """Validate parsed data for required fields and formats."""
        issues = []
        
        if not parsed_data:
            issues.append("No data found in file")
            return ValidationResult(is_valid=False, issues=issues)
        
        for i, row in enumerate(parsed_data):
            line_num = row.get('_line_number', i + 1)
            
            # Check required fields
            for field in self.required_fields:
                if field not in row or not row[field]:
                    issues.append(f"Line {line_num}: Missing required field '{field}'")
            
            # Validate amount
            if 'amount' in row:
                try:
                    amount = float(row['amount'])
                    if amount <= 0:
                        issues.append(f"Line {line_num}: Amount must be positive")
                except ValueError:
                    issues.append(f"Line {line_num}: Invalid amount format")
            
            # Validate IFSC code
            if 'ifsc' in row and row['ifsc']:
                if not re.match(self.validation_patterns['ifsc'], row['ifsc']):
                    issues.append(f"Line {line_num}: Invalid IFSC code format")
            
            # Validate currency
            if 'currency' in row and row['currency']:
                if not re.match(self.validation_patterns['currency'], row['currency']):
                    issues.append(f"Line {line_num}: Invalid currency code")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues
        )
    
    async def _transform_to_schema(
        self, 
        parsed_data: List[Dict], 
        batch_id: str, 
        tenant_id: str, 
        ingestion_result: Dict
    ) -> Dict[str, Any]:
        """Transform validated data to standardized schema."""
        
        # Generate invoice reference
        invoice_ref = f"INV-{datetime.now().strftime('%Y-%m-%d')}-{batch_id.split('-')[-1]}"
        
        # Transform lines
        lines = []
        for i, row in enumerate(parsed_data):
            line_id = row.get('line_id', f"L-{i+1}")
            
            # Generate source reference number if not provided
            source_ref = row.get('source_reference_number')
            if not source_ref:
                source_ref = f"SRC{datetime.now().strftime('%Y%m%d%H%M%S')}{i+1:03d}"
            
            line_data = {
                "line_id": line_id,
                "transaction_type": "MANUAL_INVOICE",
                "amount": float(row['amount']),
                "currency": row.get('currency', 'INR'),
                "purpose": row.get('purpose', 'UNKNOWN'),
                "DebitAccountDetails": {
                    "DebitAccountInformation": {
                        "debitAccountNumber": row['debit_account'],
                        "debitAccountHolderName": row.get('debit_account_holder_name')
                    }
                },
                "CreditAccountDetails": {
                    "CreditAccountInformation": {
                        "creditAccountNumber": row['credit_account'],
                        "creditIFSC": row.get('ifsc'),
                        "creditAccountHolderName": row.get('credit_account_holder_name')
                    }
                },
                "sourceReferenceNumber": source_ref,
                "remarks": row.get('remarks', ''),
                "transaction_date": row.get('transaction_date', datetime.now().isoformat() + "Z"),
                "evidence_ref": f"s3://{self.bucket_name}/{self.processed_prefix}/{tenant_id}/{batch_id}/{line_id}.json",
                "status": "PENDING",
                "validation_status": "VALID",
                "issues": []
            }
            lines.append(line_data)
        
        # Create standardized schema
        transformed_data = {
            "batch_id": batch_id,
            "tenant_id": tenant_id,
            "invoice_ref": invoice_ref,
            "source": "FRONTEND_UPLOAD",
            "policy_version": "intent-2.0.0",
            "upload_ts": ingestion_result['upload_ts'],
            "lines": lines
        }
        
        return transformed_data
    
    async def _store_in_postgresql(self, transformed_data: Dict[str, Any]) -> None:
        """Store validated data in PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Insert invoice record
            cursor.execute("""
                INSERT INTO invoices (batch_id, tenant_id, invoice_ref, source, policy_version, upload_ts, validation_status, issues)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (batch_id) DO UPDATE SET
                    validation_status = EXCLUDED.validation_status,
                    issues = EXCLUDED.issues
            """, (
                transformed_data['batch_id'],
                transformed_data['tenant_id'],
                transformed_data['invoice_ref'],
                transformed_data['source'],
                transformed_data['policy_version'],
                transformed_data['upload_ts'],
                'VALID',
                json.dumps([])
            ))
            
            # Insert invoice lines
            for line in transformed_data['lines']:
                cursor.execute("""
                    INSERT INTO invoice_lines (
                        batch_id, line_id, transaction_type, amount, currency, purpose,
                        debit_account_number, credit_account_number, credit_ifsc,
                        source_reference_number, remarks, transaction_date, evidence_ref, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    transformed_data['batch_id'],
                    line['line_id'],
                    line['transaction_type'],
                    line['amount'],
                    line['currency'],
                    line['purpose'],
                    line['DebitAccountDetails']['DebitAccountInformation']['debitAccountNumber'],
                    line['CreditAccountDetails']['CreditAccountInformation']['creditAccountNumber'],
                    line['CreditAccountDetails']['CreditAccountInformation']['creditIFSC'],
                    line['sourceReferenceNumber'],
                    line['remarks'],
                    line['transaction_date'],
                    line['evidence_ref'],
                    line['status']
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Stored batch {transformed_data['batch_id']} in PostgreSQL")
            
        except Exception as e:
            logger.error(f"Failed to store in PostgreSQL: {str(e)}")
            raise
    
    async def _store_processed_files(self, transformed_data: Dict[str, Any]) -> None:
        """Store processed files in S3."""
        try:
            batch_id = transformed_data['batch_id']
            tenant_id = transformed_data['tenant_id']
            
            for line in transformed_data['lines']:
                line_id = line['line_id']
                s3_key = f"{self.processed_prefix}/{tenant_id}/{batch_id}/{line_id}.json"
                
                # Store individual line as JSON
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=json.dumps(line, indent=2),
                    ContentType='application/json',
                    ServerSideEncryption='aws:kms'
                )
            
            # Store complete batch
            batch_key = f"{self.processed_prefix}/{tenant_id}/{batch_id}/batch.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=batch_key,
                Body=json.dumps(transformed_data, indent=2),
                ContentType='application/json',
                ServerSideEncryption='aws:kms'
            )
            
            logger.info(f"Stored processed files for batch {batch_id} in S3")
            
        except Exception as e:
            logger.error(f"Failed to store processed files: {str(e)}")
            raise

# Example usage
async def main():
    """Example usage of InvoiceValidator."""
    validator = InvoiceValidator()
    
    # Example ingestion result from FrontendIngestor
    ingestion_result = {
        "batch_id": "B-2025-10-03-01",
        "tenant_id": "AXIS",
        "source": "FRONTEND_UPLOAD",
        "upload_ts": "2025-10-03T23:06:00Z",
        "raw_file_key": "s3://arealis-invoices/invoices/raw/AXIS/B-2025-10-03-01/invoice_20251003_230600.csv",
        "metadata": {
            "file_type": "csv",
            "size": 1024
        }
    }
    
    # Validate invoice
    result = await validator.validate_invoice(ingestion_result)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
