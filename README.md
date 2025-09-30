# Arealis Gateway

A multi-agent autonomous payment processing system with explainable AI and comprehensive audit capabilities.

## Architecture Overview

The Arealis Gateway is a sophisticated payment processing platform that leverages multiple specialized agents to handle complex financial workflows with full transparency and compliance.

### Core Agents

- **ACC (Autonomous Compliance Agent)**: Handles regulatory compliance and risk assessment
- **PDR (Payment Decision & Routing Agent)**: Manages payment routing and decision logic
- **ARL (Reconciliation & Ledger Agent)**: Handles transaction reconciliation and ledger management
- **RCA (Root Cause Analysis Agent)**: Performs failure analysis and diagnostics
- **CRRAK (Explainability & Audit Pack Agent)**: Provides explainable AI and audit capabilities

### Cross-Cutting Layers

- **Ingest**: Batch processing and data normalization
- **Security**: RBAC, encryption, and secure key management
- **Intent Router**: Workflow classification and routing
- **Prompt**: LLM interface and RAG capabilities
- **Orchestration**: Ray DAGs and workflow management
- **Memory**: Redis and vector database integration
- **Audit**: Evidence graph and signed pack storage
- **Observability**: Metrics, tracing, and monitoring

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+
- Terraform (for infrastructure)

### Local Development

1. Clone the repository
2. Start the development environment:
   ```bash
   make dev
   ```
3. Access services:
   - ACC: http://localhost:8001
   - PDR: http://localhost:8002
   - ARL: http://localhost:8003
   - RCA: http://localhost:8004
   - CRRAK: http://localhost:8005
   - Grafana: http://localhost:3000

### Available Commands

- `make lint` - Run linting checks
- `make test` - Run all tests
- `make build` - Build all services
- `make deploy` - Deploy to target environment
- `make clean` - Clean build artifacts

## Project Structure

```
arealis-gateway/
├── services/          # Core agents (ACC, PDR, ARL, RCA, CRRAK)
├── layers/            # Cross-cutting infrastructure
├── libs/              # Shared libraries
├── policies/          # GitOps-managed policy packs
├── infra/             # Infrastructure-as-code
├── docs/              # Architecture documentation
├── tests/             # Test suites
├── scripts/           # DevOps scripts
├── Makefile           # Developer entrypoints
└── docker-compose.yml # Local development environment
```

## Contributing

Please refer to the documentation in the `docs/` directory for detailed architecture information and development guidelines.

## License

[License information to be added]
