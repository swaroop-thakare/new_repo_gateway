# Arealis Gateway v2 - Ingest Layer

The Ingest Layer handles frontend-uploaded invoices and prepares them for intent classification. This layer bridges the gap between frontend file uploads and the IntentManager processing system.

## 🏗️ Architecture

```
Frontend Upload → FrontendIngestor → InvoiceValidator → IntentManager
                     ↓                    ↓                    ↓
                   S3 Raw            PostgreSQL + S3      Intent Results
```

## 📁 Components

### 1. **FrontendIngestor** (`frontend_ingestor.py`)
- **Purpose**: Receives and ingests invoices uploaded via frontend
- **Input**: HTTP requests with CSV/JSON files
- **Output**: Raw file storage in S3 + metadata
- **API Endpoint**: `POST /api/v1/upload-invoice`

### 2. **InvoiceValidator** (`invoice_validator.py`)
- **Purpose**: Validates and transforms uploaded invoices
- **Input**: Raw file from FrontendIngestor
- **Output**: Standardized schema for IntentManager
- **Storage**: PostgreSQL + S3 processed files

### 3. **IntentManagerIntegration** (`intent_manager_integration.py`)
- **Purpose**: Updated IntentManager that fetches from storage
- **Input**: Batch ID from validated invoices
- **Output**: Intent classification results
- **Storage**: Reads from PostgreSQL + S3

## 🗄️ Storage Systems

### **S3 Bucket Structure**
```
s3://arealis-invoices/
├── invoices/raw/{tenant_id}/{batch_id}/{filename}           # Raw uploaded files
├── invoices/processed/{tenant_id}/{batch_id}/{line_id}.json # Processed line data
└── evidence/{tenant_id}/{batch_id}/{line_id}/intent.json   # Intent results
```

### **PostgreSQL Schema**
- **`invoices`**: Batch-level metadata
- **`invoice_lines`**: Individual transaction lines
- **`intent_results`**: Classification results
- **`audit_log`**: RBI compliance logging

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
cd layers/ingest
pip install -r requirements.txt
```

### 2. **Setup Database**
```bash
# Create database
createdb arealis_gateway

# Run schema
psql arealis_gateway < schema.sql
```

### 3. **Configure Environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

### 4. **Start Services**
```bash
# Start FrontendIngestor API
python frontend_ingestor.py

# In another terminal, run validation
python invoice_validator.py

# Run intent classification
python intent_manager_integration.py
```

## 📊 API Usage

### **Upload Invoice**
```bash
curl -X POST "http://localhost:8001/api/v1/upload-invoice" \
  -F "tenant_id=AXIS" \
  -F "batch_id=B-2025-10-03-01" \
  -F "file=@invoice.csv"
```

### **Response**
```json
{
  "batch_id": "B-2025-10-03-01",
  "tenant_id": "AXIS",
  "source": "FRONTEND_UPLOAD",
  "upload_ts": "2025-10-03T23:06:00Z",
  "raw_file_key": "s3://arealis-invoices/invoices/raw/AXIS/B-2025-10-03-01/invoice_20251003_230600.csv",
  "metadata": {
    "file_type": "csv",
    "size": 1024,
    "structure": {
      "headers": ["batch_id", "line_id", "amount", "currency", "purpose"],
      "row_count": 5
    }
  }
}
```

## 🔄 Workflow

### **1. Frontend Upload**
1. User uploads CSV/JSON file via frontend
2. FrontendIngestor receives file via REST API
3. File stored in S3 with unique key
4. Metadata extracted and returned

### **2. Validation Process**
1. InvoiceValidator downloads raw file from S3
2. Validates required fields and data formats
3. Transforms to standardized schema
4. Stores in PostgreSQL and S3 processed files

### **3. Intent Classification**
1. IntentManagerIntegration fetches validated data
2. Processes through intent classification
3. Stores results in PostgreSQL
4. Returns classification results

## 📋 Data Schema

### **Input Schema (Frontend Upload)**
```csv
batch_id,line_id,amount,currency,purpose,debit_account,credit_account,ifsc,remarks
B-2025-10-03-01,L-1,250000,INR,VENDOR_PAYMENT,91402004****3081,0052050****597,BARB0RAEBAR,Supplier Payment
```

### **Output Schema (Intent Classification)**
```json
{
  "batch_id": "B-2025-10-03-01",
  "intents": [
    {
      "line_id": "L-1",
      "intent": "VENDOR_PAYMENTS",
      "risk_score": 0.45,
      "confidence": 0.94,
      "decision": "PASS",
      "reasons": ["KYC_OK", "LIMITS_OK"],
      "workflow_id": "WF-VENDOR-DOMESTIC",
      "agent_pipeline": ["ACC", "PDR", "Execution", "ARL", "CRRAK"]
    }
  ],
  "workflow_id": "WF-VENDOR-DOMESTIC",
  "agent_pipeline": ["ACC", "PDR", "Execution", "ARL", "CRRAK"],
  "policy_version": "intent-2.0.0",
  "timestamp": "2025-10-03T23:06:00Z",
  "status": "PROCESSING"
}
```

## 🔒 Security & Compliance

### **RBI Compliance**
- **Audit Logging**: All actions logged in `audit_log` table
- **Data Retention**: 3 years for processed data, 1 year for audit logs
- **Encryption**: S3 files encrypted with SSE-KMS
- **Access Control**: Role-based access to PostgreSQL

### **Security Features**
- **JWT Authentication**: Secure API access
- **Rate Limiting**: Prevents abuse
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses

## 📈 Monitoring

### **Metrics**
- Upload success/failure rates
- Validation processing times
- Intent classification accuracy
- Storage utilization

### **Logging**
- Structured JSON logging
- Request/response tracking
- Error monitoring
- Performance metrics

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test
pytest tests/test_frontend_ingestor.py
```

## 🚀 Deployment

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "frontend_ingestor.py"]
```

### **Environment Variables**
- `S3_BUCKET_NAME`: S3 bucket for file storage
- `DB_HOST`: PostgreSQL host
- `DB_PASSWORD`: Database password
- `JWT_SECRET`: JWT signing secret

## 📚 API Documentation

### **Endpoints**
- `POST /api/v1/upload-invoice`: Upload invoice file
- `GET /api/v1/health`: Health check
- `GET /api/v1/batch/{batch_id}`: Get batch status
- `GET /api/v1/batch/{batch_id}/results`: Get classification results

### **Error Codes**
- `400`: Bad Request (invalid file format)
- `413`: Payload Too Large (file too big)
- `422`: Validation Error (missing required fields)
- `500`: Internal Server Error

## 🔧 Configuration

See `config.py` for all configuration options. Key settings:

- **File Size Limit**: 10MB default
- **Validation Timeout**: 5 minutes
- **Database Pool**: 10 connections
- **Rate Limiting**: 100 requests/hour

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify database connectivity
3. Check S3 permissions
4. Review configuration settings
