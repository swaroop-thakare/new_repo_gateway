# Master Control Process (MCP) - Arealis Gateway v2

The Master Control Process serves as the central coordinator for all agents across layers in the Arealis Gateway v2 system. It manages the complete workflow lifecycle from ingestion to audit while ensuring RBI compliance and system resilience.

## 🏗️ Architecture

```
MCP (Master Control Process)
├── Agent Registry (All Layers)
├── Workflow Management
├── Event Coordination
├── Error Handling
└── System Monitoring
```

## 📁 Components

### **1. Master Control Process** (`master_control.py`)
- **Purpose**: Central coordinator for all agents across layers
- **Features**: Agent registration, workflow management, event coordination, error handling
- **Layers Coordinated**: ingest, intent-router, orchestration, audit, memory, observability, prompt, security

### **2. MCP API Server** (`mcp_api.py`)
- **Purpose**: REST API for workflow management and monitoring
- **Endpoints**: Workflow control, agent monitoring, system health
- **Features**: Real-time status, metrics, configuration management

### **3. Configuration Management** (`mcp_config.py`)
- **Purpose**: Centralized configuration for all MCP components
- **Features**: Agent settings, workflow parameters, monitoring configuration
- **Layers**: All layer-specific configurations

### **4. Database Schema** (`mcp_schema.sql`)
- **Purpose**: PostgreSQL schema for MCP data persistence
- **Tables**: Workflow states, agent registry, event log, metrics
- **Features**: Audit trails, performance monitoring, system health

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
cd layers/orchestration
pip install -r requirements.txt
```

### **2. Setup Database**
```bash
# Create database
createdb arealis_gateway

# Run MCP schema
psql arealis_gateway < mcp_schema.sql
```

### **3. Configure Environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

### **4. Start MCP**
```bash
# Start MCP API server
python mcp_api.py

# Or start MCP directly
python master_control.py
```

## 📊 API Usage

### **Start Workflow**
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/start" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "B-2025-10-04-01",
    "tenant_id": "AXIS",
    "source": "FRONTEND_UPLOAD",
    "upload_ts": "2025-10-04T13:06:00Z",
    "raw_file_key": "s3://arealis-invoices/invoices/raw/AXIS/B-2025-10-04-01/invoice_2025-10-04.csv"
  }'
```

### **Get Workflow Status**
```bash
curl "http://localhost:8000/api/v1/workflows/WF-B-2025-10-04-01-abc123/status"
```

### **Get System Health**
```bash
curl "http://localhost:8000/api/v1/system/health"
```

## 🔄 Workflow Management

### **Workflow Lifecycle**
1. **INITIALIZED** → **INGESTING** → **VALIDATING** → **CLASSIFYING** → **ROUTING** → **EXECUTING** → **AUDITING** → **COMPLETED**

### **Agent Coordination**
- **Ingest Layer**: FrontendIngestor → InvoiceValidator
- **Intent-Router Layer**: IntentClassifier → WorkflowSelector  
- **Orchestration Layer**: Orchestrator → PDR → Execution → ARL → CRRAK
- **Audit Layer**: AuditLogger → ComplianceChecker
- **Supporting Layers**: Memory, Observability, Prompt, Security

### **Event Flow**
```
invoice_received → validated_invoice → workflow_selected → 
pdr_result → execution_result → workflow_complete_v2 → 
audit_report_generated → system_workflow_complete
```

## 📋 Agent Registry

### **Ingest Layer Agents**
- **FrontendIngestor**: File upload handling
- **InvoiceValidator**: Data validation and transformation

### **Intent-Router Layer Agents**
- **IntentClassifier**: Intent classification and scoring
- **WorkflowSelector**: Workflow selection based on intents

### **Orchestration Layer Agents**
- **Orchestrator**: Pipeline orchestration
- **PDR**: Payment route optimization
- **Execution**: Transaction execution
- **ARL**: Account reconciliation
- **CRRAK**: Compliance and risk assessment

### **Audit Layer Agents**
- **AuditLogger**: Audit trail management
- **ComplianceChecker**: RBI compliance verification

### **Supporting Layer Agents**
- **ContextMemory**: Context and state management
- **Monitor**: System monitoring
- **Debugger**: Error debugging
- **PromptGenerator**: Prompt generation
- **PromptValidator**: Prompt validation
- **SanctionScanner**: Sanction list scanning

## 🔧 Configuration

### **Agent Configuration**
```python
# Example agent configuration
agent_config = {
    "FrontendIngestor": {
        "api_port": 8001,
        "timeout": 30,
        "max_file_size": 10485760
    },
    "IntentClassifier": {
        "risk_threshold": 0.5,
        "confidence_threshold": 0.85
    }
}
```

### **Workflow Configuration**
```python
# Example workflow configuration
workflow_config = {
    "timeout": 1800,  # 30 minutes
    "max_retries": 3,
    "cleanup_interval": 3600  # 1 hour
}
```

## 📈 Monitoring and Metrics

### **System Health**
- **Overall Status**: healthy, degraded, unhealthy
- **Component Status**: Individual agent health
- **Health Score**: Percentage of healthy components

### **Workflow Metrics**
- **Active Workflows**: Currently running workflows
- **Completion Rate**: Success/failure rates
- **Average Duration**: Workflow execution times
- **Error Rates**: Agent failure rates

### **Agent Metrics**
- **Execution Count**: Total agent executions
- **Success Rate**: Agent success percentage
- **Average Duration**: Agent execution times
- **Error Count**: Agent error frequency

## 🔒 Security and Compliance

### **RBI Compliance**
- **Audit Trails**: Complete workflow audit logging
- **Data Retention**: 3 years for processed data
- **Compliance Checks**: Automated RBI compliance verification
- **Access Control**: Role-based access to MCP functions

### **Security Features**
- **JWT Authentication**: Secure API access
- **Rate Limiting**: Prevent system abuse
- **Error Handling**: Secure error responses
- **Audit Logging**: All actions logged for compliance

## 🧪 Testing

### **Unit Tests**
```bash
# Run unit tests
pytest tests/test_master_control.py

# Run with coverage
pytest --cov=. tests/
```

### **Integration Tests**
```bash
# Run integration tests
pytest tests/test_integration.py

# Test specific workflow
pytest tests/test_workflow_integration.py
```

### **Load Testing**
```bash
# Run load tests
pytest tests/test_load.py

# Test concurrent workflows
pytest tests/test_concurrent_workflows.py
```

## 🚀 Deployment

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "mcp_api.py"]
```

### **Environment Variables**
- `MCP_HOST`: MCP server host
- `MCP_PORT`: MCP server port
- `DB_HOST`: PostgreSQL host
- `DB_PASSWORD`: Database password
- `S3_BUCKET_NAME`: S3 bucket for storage

### **Production Configuration**
```yaml
# docker-compose.yml
version: '3.8'
services:
  mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - S3_BUCKET_NAME=arealis-invoices
    depends_on:
      - postgres
      - redis
```

## 📚 API Documentation

### **Endpoints**
- `POST /api/v1/workflows/start`: Start new workflow
- `GET /api/v1/workflows/{id}/status`: Get workflow status
- `GET /api/v1/workflows/{id}/cancel`: Cancel workflow
- `GET /api/v1/agents`: Get all agent statuses
- `GET /api/v1/agents/{name}`: Get specific agent status
- `POST /api/v1/agents/{name}/restart`: Restart agent
- `GET /api/v1/system/health`: Get system health
- `GET /api/v1/system/metrics`: Get system metrics
- `GET /api/v1/system/config`: Get system configuration

### **Error Codes**
- `400`: Bad Request (invalid input)
- `404`: Not Found (workflow/agent not found)
- `500`: Internal Server Error (system error)

## 🔧 Troubleshooting

### **Common Issues**
1. **Agent Failures**: Check agent logs and dependencies
2. **Workflow Stuck**: Check workflow status and agent health
3. **Database Connection**: Verify PostgreSQL connectivity
4. **S3 Access**: Check AWS credentials and permissions

### **Debugging**
```bash
# Check MCP logs
tail -f logs/mcp.log

# Check agent status
curl "http://localhost:8000/api/v1/agents"

# Check system health
curl "http://localhost:8000/api/v1/system/health"
```

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify database connectivity
3. Check S3 permissions
4. Review configuration settings
5. Check agent dependencies
