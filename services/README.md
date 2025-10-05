# Arealis Gateway Services

This directory contains the core services that make up the Arealis Gateway system. Each service is designed to handle specific aspects of payment processing, compliance, and reconciliation.

## Services Overview

### 1. PDR Service (Payment Decision Router)
**Location**: `services/pdr/`
**Port**: 8001
**Purpose**: Acts as the "smart navigator" to optimize payment routes based on cost, speed, reliability, and account compatibility.

**Key Features**:
- Sophisticated rail selection algorithm
- Cost optimization
- Fallback path management
- Real-time performance tracking

**API Endpoints**:
- `POST /pdr/decide` - Generate PDR decisions
- `POST /pdr/execute/{transaction_id}` - Execute transaction
- `GET /pdr/decision/{transaction_id}` - Get PDR decision
- `GET /pdr/rails` - Get available rails
- `GET /pdr/rails/{rail_name}/stats` - Get rail statistics

### 2. RCA Service (Root Cause Analysis)
**Location**: `services/rca/`
**Port**: 8002
**Purpose**: Analyzes the root cause of transaction failures or holds to inform corrective actions.

**Key Features**:
- Failure pattern analysis
- Issue categorization
- Recommendation generation
- Evidence correlation

**API Endpoints**:
- `POST /rca/analyze` - Analyze failure root cause
- `GET /rca/evidence/{batch_id}/{line_id}` - Get RCA evidence
- `GET /rca/patterns` - Get failure patterns

### 3. CRRAK Service (Compliance Report & Risk Assessment Kit)
**Location**: `services/crrak/`
**Port**: 8003
**Purpose**: Generates compliance reports and risk assessments for RBI compliance and audit readiness.

**Key Features**:
- Compliance status assessment
- Risk scoring
- Audit trail generation
- Regulatory reporting

**API Endpoints**:
- `POST /crrak/generate` - Generate CRRAK report
- `GET /crrak/report/{batch_id}/{line_id}` - Get CRRAK report
- `GET /crrak/compliance-summary` - Get compliance summary

### 4. ARL Service (Account Reconciliation Ledger)
**Location**: `services/arl/`
**Port**: 8004
**Purpose**: Reconciles ledger entries with transaction outcomes to ensure financial accuracy.

**Key Features**:
- Ledger reconciliation
- Discrepancy detection
- Financial accuracy validation
- Audit trail maintenance

**API Endpoints**:
- `POST /arl/reconcile` - Reconcile transaction
- `GET /arl/evidence/{batch_id}/{line_id}` - Get ARL evidence
- `GET /arl/ledger-entries/{batch_id}/{line_id}` - Get ledger entries
- `GET /arl/reconciliation-summary` - Get reconciliation summary

### 5. Master Control Service
**Location**: `services/master_control.py`
**Port**: 8000
**Purpose**: Orchestrates all services and manages workflow execution.

**Key Features**:
- Service orchestration
- Workflow management
- Event processing
- Status tracking

**API Endpoints**:
- `POST /orchestrate/event` - Process workflow events
- `POST /orchestrate/pipeline` - Execute complete pipeline
- `GET /orchestrate/status/{batch_id}/{line_id}` - Get workflow status
- `POST /orchestrate/trigger-rca` - Manually trigger RCA
- `POST /orchestrate/trigger-crrak` - Manually trigger CRRAK
- `POST /orchestrate/trigger-arl` - Manually trigger ARL

## Architecture

The services follow a microservices architecture with the following characteristics:

1. **Independent Services**: Each service can be deployed and scaled independently
2. **Event-Driven**: Services communicate through events and HTTP APIs
3. **Stateless**: Services maintain minimal state, relying on external storage
4. **Fault Tolerant**: Services handle failures gracefully with fallback mechanisms

## Data Flow

```
Invoice → PDR → [Success] → CRRAK → ARL → Completion
         ↓
       [Failure] → RCA → Analysis
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/arealis_gateway

# AWS S3
S3_BUCKET=arealis-gateway-data
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Service URLs
PDR_SERVICE_URL=http://localhost:8001
RCA_SERVICE_URL=http://localhost:8002
CRRAK_SERVICE_URL=http://localhost:8003
ARL_SERVICE_URL=http://localhost:8004
```

## Running the Services

### Development Mode

```bash
# Install dependencies
pip install -r requirements.txt

# Run PDR Service
cd services/pdr
python main.py

# Run RCA Service
cd services/rca
python main.py

# Run CRRAK Service
cd services/crrak
python main.py

# Run ARL Service
cd services/arl
python main.py

# Run Master Control
cd services
python master_control.py
```

### Production Mode

```bash
# Using Docker (recommended)
docker-compose up -d

# Or using systemd services
sudo systemctl start arealis-pdr
sudo systemctl start arealis-rca
sudo systemctl start arealis-crrak
sudo systemctl start arealis-arl
sudo systemctl start arealis-master-control
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run all tests
pytest tests/

# Run specific service tests
pytest tests/test_rca_service.py
pytest tests/test_crrak_service.py
pytest tests/test_arl_service.py
pytest tests/test_master_control.py
```

## Monitoring

Each service provides health check endpoints:

- `GET /health` - Basic health check
- `GET /` - Service information

Monitor service health:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## API Documentation

Each service provides interactive API documentation:

- Master Control: http://localhost:8000/docs
- PDR Service: http://localhost:8001/docs
- RCA Service: http://localhost:8002/docs
- CRRAK Service: http://localhost:8003/docs
- ARL Service: http://localhost:8004/docs

## Security

- All services use HTTPS in production
- API keys are required for external access
- Database connections are encrypted
- S3 buckets have appropriate access controls

## Scaling

Services can be scaled horizontally:

```bash
# Scale PDR service
docker-compose up -d --scale pdr-service=3

# Scale RCA service
docker-compose up -d --scale rca-service=2
```

## Troubleshooting

### Common Issues

1. **Service Unavailable**: Check if all services are running and healthy
2. **Database Connection**: Verify DATABASE_URL and database accessibility
3. **S3 Access**: Verify AWS credentials and S3 bucket permissions
4. **Port Conflicts**: Ensure no other services are using the same ports

### Logs

Check service logs:

```bash
# Docker logs
docker-compose logs pdr-service
docker-compose logs rca-service
docker-compose logs crrak-service
docker-compose logs arl-service
docker-compose logs master-control

# Systemd logs
journalctl -u arealis-pdr
journalctl -u arealis-rca
journalctl -u arealis-crrak
journalctl -u arealis-arl
journalctl -u arealis-master-control
```
