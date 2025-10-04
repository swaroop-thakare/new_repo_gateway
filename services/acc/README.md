# ACC Agent Service with Database Integration

This service provides ACC (Anti-Corruption Compliance) decision-making capabilities with integrated PostgreSQL and Neo4j database storage.

## 🗄️ Database Schema

### PostgreSQL Tables

#### `acc_agent` Table
```sql
CREATE TABLE acc_agent (
    id SERIAL PRIMARY KEY,
    line_id VARCHAR(100),
    beneficiary VARCHAR(255),
    ifsc VARCHAR(20),
    amount NUMERIC,
    policy_version VARCHAR(50),
    status VARCHAR(20),
    decision_reason TEXT,
    evidence_ref TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `payment_files` Table
```sql
CREATE TABLE payment_files (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    data JSONB
);
```

### Neo4j Schema
- **Node Type**: `AccAgent`
- **Properties**: `line_id`, `beneficiary`, `ifsc`, `amount`, `status`, `decision_reason`, `evidence_ref`, `created_at`

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Databases

#### PostgreSQL
- **URL**: `postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway`
- **Status**: ✅ Configured

#### Neo4j
- **URI**: `neo4j+s://6933b562.databases.neo4j.io`
- **Username**: `neo4j`
- **Password**: `Yavi0NJTNDApnMb-InD3pCVwdgT7Hzd2-6vb-tYshZo`
- **Database**: `neo4j`
- **Status**: ✅ Configured (Neo4j Aura Cloud)

### 3. Create Tables
```bash
python setup_database.py
```

### 4. Start Service
```bash
python start_service.py
```

## 📡 API Endpoints

### POST `/acc/decide`
Process transactions and save results to both databases.

**Request:**
```json
[
  {
    "payment_type": "payroll",
    "transaction_id": "TXN001",
    "sender": {...},
    "receiver": {...},
    "amount": 50000,
    "currency": "INR",
    "method": "NEFT",
    "purpose": "Salary Payment",
    "schedule_datetime": "2025-10-02T10:00:00Z",
    "location": {...},
    "additional_fields": {...}
  }
]
```

**Response:**
```json
{
  "decisions": [
    {
      "line_id": "TXN001",
      "decision": "PASS",
      "policy_version": "acc-1.4.2",
      "reasons": [],
      "evidence_refs": ["pan", "bank"],
      "postgres_id": 123,
      "neo4j_success": true
    }
  ]
}
```

### POST `/acc/payment-file`
Save payment file data to PostgreSQL.

### GET `/acc/decisions`
Retrieve all ACC agent decisions from PostgreSQL.

## 🧪 Testing

### Run Integration Tests
```bash
python test_integration.py
```

### Test Database Connection
```bash
python setup_database.py
```

## 📊 Database Features

### PostgreSQL
- ✅ **ACID Compliance**: Reliable transaction storage
- ✅ **JSON Support**: Flexible data storage with JSONB
- ✅ **Indexing**: Optimized queries with primary keys
- ✅ **Scalability**: Handles high-volume transactions

### Neo4j
- ✅ **Graph Relationships**: Complex data relationships
- ✅ **Real-time Analytics**: Pattern detection and analysis
- ✅ **Flexible Schema**: Dynamic property addition
- ✅ **Performance**: Optimized for graph traversals

## 🔧 Configuration

### Environment Variables
```bash
# PostgreSQL (already configured)
POSTGRES_URL=postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway

# Neo4j (Neo4j Aura Cloud)
NEO4J_URI=neo4j+s://6933b562.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=Yavi0NJTNDApnMb-InD3pCVwdgT7Hzd2-6vb-tYshZo
NEO4J_DATABASE=neo4j
```

## 📈 Monitoring

### Database Health Checks
- **PostgreSQL**: Connection status and table creation
- **Neo4j**: Node creation and relationship mapping
- **Performance**: Query execution times and success rates

### Logging
- **Transaction Processing**: Each decision logged with timestamps
- **Database Operations**: Success/failure status for each operation
- **Error Handling**: Detailed error messages for troubleshooting

## 🚨 Troubleshooting

### Common Issues

1. **PostgreSQL Connection Failed**
   - Check network connectivity
   - Verify credentials
   - Ensure database exists

2. **Neo4j Connection Failed**
   - Update credentials in `database.py`
   - Check Neo4j server status
   - Verify bolt protocol support

3. **Table Creation Failed**
   - Check database permissions
   - Verify schema conflicts
   - Review error logs

### Debug Commands
```bash
# Test PostgreSQL connection
python -c "from database import create_tables; create_tables()"

# Test Neo4j connection
python -c "from database import save_to_neo4j; print(save_to_neo4j('test', 'test', 'test', 100, 'PASS', '{}', '{}'))"
```

## 📝 Notes

- **Data Persistence**: All decisions are stored in both databases
- **Error Handling**: Graceful fallback if one database fails
- **Performance**: Optimized for high-throughput scenarios
- **Security**: Credentials should be stored in environment variables

## 🔄 Next Steps

1. **Update Neo4j credentials** in `database.py`
2. **Run setup script** to create tables
3. **Test integration** with sample data
4. **Monitor performance** in production
5. **Scale databases** as needed
