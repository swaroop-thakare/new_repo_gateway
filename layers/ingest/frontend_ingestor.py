"""
FrontendIngestor - Arealis Gateway v2 Ingest Layer

Handles frontend-uploaded invoices and stores them in S3 for processing.
Part of the ingest layer that bridges frontend uploads with the intent classification system.

Input: HTTP requests with invoice files (CSV/JSON)
Output: Raw file storage in S3 + metadata for InvoiceValidator
"""

import json
import csv
import boto3
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendIngestor:
    """
    Frontend Ingestor Agent for Arealis Gateway v2
    
    Handles invoice uploads from frontend, performs initial parsing,
    and stores raw files in S3 for downstream processing.
    """
    
    def __init__(self):
        """Initialize FrontendIngestor with S3 and configuration."""
        self.s3_client = boto3.client('s3')
        self.bucket_name = "arealis-invoices"
        self.raw_prefix = "invoices/raw"
        
        # Supported file types
        self.supported_types = {
            'text/csv': 'csv',
            'application/json': 'json',
            'text/plain': 'csv'  # Assume CSV for plain text
        }
    
    async def ingest_invoice(
        self, 
        tenant_id: str,
        batch_id: str,
        file: UploadFile,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Ingest invoice file from frontend upload.
        
        Args:
            tenant_id: Tenant identifier (e.g., "AXIS", "ICICI")
            batch_id: Batch identifier (e.g., "B-2025-10-03-01")
            file: Uploaded file object
            metadata: Additional metadata
            
        Returns:
            Dict with ingestion results and S3 key
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = self._get_file_extension(file.content_type)
            filename = f"invoice_{timestamp}.{file_extension}"
            
            # Create S3 key
            s3_key = f"{self.raw_prefix}/{tenant_id}/{batch_id}/{filename}"
            
            # Read file content
            content = await file.read()
            
            # Store in S3
            await self._store_raw_file(s3_key, content, file.content_type)
            
            # Parse file structure for metadata
            file_metadata = await self._parse_file_structure(content, file.content_type)
            
            # Create ingestion result
            result = {
                "batch_id": batch_id,
                "tenant_id": tenant_id,
                "source": "FRONTEND_UPLOAD",
                "upload_ts": datetime.now().isoformat() + "Z",
                "raw_file_key": f"s3://{self.bucket_name}/{s3_key}",
                "metadata": {
                    "file_type": file_extension,
                    "size": len(content),
                    "original_filename": file.filename,
                    "content_type": file.content_type,
                    "structure": file_metadata
                }
            }
            
            # Add custom metadata if provided
            if metadata:
                result["metadata"].update(metadata)
            
            logger.info(f"Successfully ingested invoice for batch {batch_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error ingesting invoice: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to ingest invoice: {str(e)}")
    
    def _get_file_extension(self, content_type: str) -> str:
        """Get file extension from content type."""
        return self.supported_types.get(content_type, 'txt')
    
    async def _store_raw_file(self, s3_key: str, content: bytes, content_type: str) -> None:
        """Store raw file in S3 bucket."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=content_type,
                ServerSideEncryption='aws:kms'
            )
            logger.info(f"Stored raw file at s3://{self.bucket_name}/{s3_key}")
        except Exception as e:
            logger.error(f"Failed to store file in S3: {str(e)}")
            raise
    
    async def _parse_file_structure(self, content: bytes, content_type: str) -> Dict[str, Any]:
        """Parse file structure to extract metadata."""
        try:
            if content_type == 'text/csv':
                return await self._parse_csv_structure(content)
            elif content_type == 'application/json':
                return await self._parse_json_structure(content)
            else:
                return {"type": "unknown", "size": len(content)}
        except Exception as e:
            logger.warning(f"Failed to parse file structure: {str(e)}")
            return {"type": "parse_error", "size": len(content)}
    
    async def _parse_csv_structure(self, content: bytes) -> Dict[str, Any]:
        """Parse CSV structure to extract headers and row count."""
        try:
            text_content = content.decode('utf-8')
            lines = text_content.split('\n')
            
            if lines:
                headers = lines[0].split(',')
                row_count = len([line for line in lines[1:] if line.strip()])
                
                return {
                    "type": "csv",
                    "headers": headers,
                    "row_count": row_count,
                    "columns": len(headers)
                }
        except Exception as e:
            logger.warning(f"Failed to parse CSV: {str(e)}")
            return {"type": "csv", "parse_error": str(e)}
    
    async def _parse_json_structure(self, content: bytes) -> Dict[str, Any]:
        """Parse JSON structure to extract metadata."""
        try:
            data = json.loads(content.decode('utf-8'))
            
            if isinstance(data, list):
                return {
                    "type": "json",
                    "structure": "array",
                    "item_count": len(data),
                    "sample_keys": list(data[0].keys()) if data else []
                }
            elif isinstance(data, dict):
                return {
                    "type": "json",
                    "structure": "object",
                    "keys": list(data.keys())
                }
        except Exception as e:
            logger.warning(f"Failed to parse JSON: {str(e)}")
            return {"type": "json", "parse_error": str(e)}

# FastAPI Application for Frontend Ingestor
app = FastAPI(title="Frontend Ingestor API", version="2.0.0")

# Initialize ingestor
ingestor = FrontendIngestor()

@app.post("/api/v1/upload-invoice")
async def upload_invoice(
    tenant_id: str = Form(...),
    batch_id: str = Form(...),
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload invoice file from frontend.
    
    Args:
        tenant_id: Tenant identifier
        batch_id: Batch identifier  
        file: Invoice file (CSV/JSON)
        metadata: Optional JSON metadata
    """
    try:
        # Parse metadata if provided
        parsed_metadata = None
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning("Invalid metadata JSON, ignoring")
        
        # Ingest the file
        result = await ingestor.ingest_invoice(
            tenant_id=tenant_id,
            batch_id=batch_id,
            file=file,
            metadata=parsed_metadata
        )
        
        return JSONResponse(content=result, status_code=200)
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "frontend_ingestor", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
