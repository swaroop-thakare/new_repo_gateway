import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, or_, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
from datetime import datetime
import json

# Database configurations
POSTGRES_URL = "postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway"

# Neo4j credentials
NEO4J_URI = "neo4j+s://6933b562.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Yavi0NJTNDApnMb-InD3pCVwdgT7Hzd2-6vb-tYshZo"
NEO4J_DATABASE = "neo4j"

# PostgreSQL setup
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Neo4j setup
neo4j_driver = GraphDatabase.driver(
    NEO4J_URI, 
    auth=(NEO4J_USER, NEO4J_PASSWORD),
    max_connection_lifetime=30 * 60,  # 30 minutes
    max_connection_pool_size=5,  # Reduced pool size
    connection_acquisition_timeout=30,  # Reduced timeout
    keep_alive=True
)

class AccAgent(Base):
    __tablename__ = "acc_agent"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String(100))
    beneficiary = Column(String(255))
    ifsc = Column(String(20))
    amount = Column(Numeric)
    policy_version = Column(String(50))
    status = Column(String(20))
    decision_reason = Column(Text)
    evidence_ref = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class PaymentFile(Base):
    __tablename__ = "payment_files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(Text)
    data = Column(Text)  # JSON data as text

class IntentTable(Base):
    __tablename__ = "intent_table"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_type = Column(String(50))
    transaction_id = Column(String(100))
    
    # Sender fields
    sender_name = Column(String(255))
    sender_account_number = Column(String(50))
    sender_ifsc_code = Column(String(20))
    sender_bank_name = Column(String(100))
    
    # Receiver fields
    receiver_name = Column(String(255))
    receiver_account_number = Column(String(50))
    receiver_ifsc_code = Column(String(20))
    receiver_bank_name = Column(String(100))
    
    # Transaction details
    amount = Column(Numeric)
    currency = Column(String(10))
    method = Column(String(20))
    purpose = Column(String(50))
    schedule_datetime = Column(DateTime)
    
    # Location fields
    city = Column(String(100))
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    
    # Additional fields
    employee_id = Column(String(50))
    department = Column(String(100))
    payment_frequency = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RedisTable(Base):
    __tablename__ = "redis_table"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String(50), unique=True)
    execution_timeline = Column(JSON)
    system_health = Column(JSON)
    ttl = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class PdrTable(Base):
    __tablename__ = "pdr_table"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String(50), unique=True)
    batch_id = Column(String(100))
    rail_selected = Column(String(100))
    fallbacks = Column(JSON)
    expected_amount = Column(Numeric)
    expected_currency = Column(String(10))
    expected_utr = Column(String(100))
    status = Column(String(50))
    created_at = Column(DateTime)

class ArlTable(Base):
    __tablename__ = "arl_table"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recon_id = Column(Integer, unique=True)
    line_id = Column(String(50))
    utr = Column(String(100))
    psp_reference = Column(String(100))
    match_status = Column(String(50))
    match_reason = Column(String(100))
    journal = Column(JSON)
    metadata_info = Column(JSON)
    created_at = Column(DateTime)

class RcaTable(Base):
    __tablename__ = "rca_table"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rca_id = Column(Integer, unique=True)
    line_id = Column(String(50))
    batch_id = Column(String(100))
    root_cause = Column(Text)
    failure_category = Column(String(100))
    recommended_action = Column(Text)
    evidence_refs = Column(JSON)
    created_at = Column(DateTime)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_acc_agent_result(db, line_id, beneficiary, ifsc, amount, policy_version, status, decision_reason, evidence_ref):
    """Save ACC agent result to PostgreSQL"""
    try:
        acc_record = AccAgent(
            line_id=line_id,
            beneficiary=beneficiary,
            ifsc=ifsc,
            amount=amount,
            policy_version=policy_version,
            status=status,
            decision_reason=decision_reason,
            evidence_ref=evidence_ref
        )
        db.add(acc_record)
        db.commit()
        return acc_record.id
    except Exception as e:
        db.rollback()
        print(f"Error saving to PostgreSQL: {e}")
        return None

def save_to_neo4j(line_id, beneficiary, ifsc, amount, status, decision_reason, evidence_ref):
    """Save ACC agent result to Neo4j"""
    try:
        # Test connection first
        neo4j_driver.verify_connectivity()
        
        with neo4j_driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                CREATE (a:AccAgent {
                    line_id: $line_id,
                    beneficiary: $beneficiary,
                    ifsc: $ifsc,
                    amount: $amount,
                    status: $status,
                    decision_reason: $decision_reason,
                    evidence_ref: $evidence_ref,
                    created_at: datetime()
                })
                RETURN a.line_id as created_line_id
            """, 
            line_id=line_id,
            beneficiary=beneficiary,
            ifsc=ifsc,
            amount=amount,
            status=status,
            decision_reason=decision_reason,
            evidence_ref=evidence_ref
            )
            
            # Verify the record was created
            record = result.single()
            if record:
                print(f"✅ Neo4j record created: {record['created_line_id']}")
                return True
            else:
                print("❌ Neo4j record creation failed - no result returned")
                return False
                
    except Exception as e:
        print(f"⚠️  Neo4j connection issue: {e}")
        print(f"   Continuing without Neo4j - data saved to PostgreSQL only")
        print(f"   To fix Neo4j: Check network connectivity and credentials")
        return False

def save_payment_file(db, filename, data):
    """Save payment file data to PostgreSQL"""
    try:
        print(f"💾 Database save attempt:")
        print(f"  - Filename: {filename}")
        print(f"  - Data type: {type(data)}")
        print(f"  - Data preview: {str(data)[:200]}...")
        
        # Ensure data is properly serialized
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = str(data)
        
        payment_record = PaymentFile(
            filename=filename,
            data=data_str
        )
        db.add(payment_record)
        db.flush()  # Flush to get the ID
        db.commit()
        
        print(f"✅ Database save successful, ID: {payment_record.id}")
        print(f"✅ Data length: {len(data_str)} characters")
        return payment_record.id
    except Exception as e:
        db.rollback()
        print(f"❌ Database save error: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_intent_data(db, transaction_data):
    """Save transaction data to intent_table"""
    try:
        # Parse schedule_datetime
        schedule_dt = None
        if 'schedule_datetime' in transaction_data:
            schedule_dt = datetime.fromisoformat(transaction_data['schedule_datetime'].replace('Z', '+00:00'))
        
        intent_record = IntentTable(
            payment_type=transaction_data.get('payment_type'),
            transaction_id=transaction_data.get('transaction_id'),
            
            # Sender data
            sender_name=transaction_data.get('sender', {}).get('name'),
            sender_account_number=transaction_data.get('sender', {}).get('account_number'),
            sender_ifsc_code=transaction_data.get('sender', {}).get('ifsc_code'),
            sender_bank_name=transaction_data.get('sender', {}).get('bank_name'),
            
            # Receiver data
            receiver_name=transaction_data.get('receiver', {}).get('name'),
            receiver_account_number=transaction_data.get('receiver', {}).get('account_number'),
            receiver_ifsc_code=transaction_data.get('receiver', {}).get('ifsc_code'),
            receiver_bank_name=transaction_data.get('receiver', {}).get('bank_name'),
            
            # Transaction details
            amount=transaction_data.get('amount'),
            currency=transaction_data.get('currency'),
            method=transaction_data.get('method'),
            purpose=transaction_data.get('purpose'),
            schedule_datetime=schedule_dt,
            
            # Location data
            city=transaction_data.get('location', {}).get('city'),
            latitude=transaction_data.get('location', {}).get('gps_coordinates', {}).get('latitude'),
            longitude=transaction_data.get('location', {}).get('gps_coordinates', {}).get('longitude'),
            
            # Additional fields
            employee_id=transaction_data.get('additional_fields', {}).get('employee_id'),
            department=transaction_data.get('additional_fields', {}).get('department'),
            payment_frequency=transaction_data.get('additional_fields', {}).get('payment_frequency')
        )
        
        db.add(intent_record)
        db.commit()
        return intent_record.id
    except Exception as e:
        db.rollback()
        print(f"Error saving intent data: {e}")
        return None

def get_payment_files(db, limit=100, offset=0):
    """Fetch payment files from PostgreSQL"""
    try:
        files = db.query(PaymentFile).offset(offset).limit(limit).all()
        return files
    except Exception as e:
        print(f"Error fetching payment files: {e}")
        return []

def get_payment_file_by_id(db, file_id):
    """Fetch a specific payment file by ID"""
    try:
        file = db.query(PaymentFile).filter(PaymentFile.id == file_id).first()
        return file
    except Exception as e:
        print(f"Error fetching payment file {file_id}: {e}")
        return None

def get_payment_files_count(db):
    """Get total count of payment files"""
    try:
        count = db.query(PaymentFile).count()
        return count
    except Exception as e:
        print(f"Error counting payment files: {e}")
        return 0

def search_payment_files(db, search_term=None, limit=100, offset=0):
    """Search payment files by filename or data content"""
    try:
        query = db.query(PaymentFile)
        
        if search_term:
            query = query.filter(
                or_(
                    PaymentFile.filename.contains(search_term),
                    PaymentFile.data.contains(search_term)
                )
            )
        
        files = query.offset(offset).limit(limit).all()
        return files
    except Exception as e:
        print(f"Error searching payment files: {e}")
        return []

def get_latest_payment_files(db, limit=10):
    """Get the latest payment files"""
    try:
        files = db.query(PaymentFile).order_by(PaymentFile.id.desc()).limit(limit).all()
        return files
    except Exception as e:
        print(f"Error fetching latest payment files: {e}")
        return []

def populate_redis_table(db):
    """Populate redis_table with the provided data"""
    try:
        redis_data = [
            {
                "line_id": "L-1",
                "execution_timeline": [
                    {"agent": "ACC", "decision": "PASS"},
                    {"agent": "PDR", "rail": "IMPS@HDFC"},
                    {"agent": "ARL", "status": "MATCHED"},
                    {"agent": "RCA", "root_cause": None}
                ],
                "system_health": {"cpu": 19, "memory": "4GB"},
                "ttl": 3600
            },
            {
                "line_id": "L-2",
                "execution_timeline": [
                    {"agent": "ACC", "decision": "HOLD"},
                    {"agent": "PDR", "rail": "IMPS@HDFC"},
                    {"agent": "ARL", "status": "EXCEPTION"},
                    {"agent": "RCA", "root_cause": "Amount Mismatch"}
                ],
                "system_health": {"cpu": 93, "memory": "2GB"},
                "ttl": 3600
            },
            {
                "line_id": "L-3",
                "execution_timeline": [
                    {"agent": "ACC", "decision": "PASS"},
                    {"agent": "PDR", "rail": "IMPS@HDFC"},
                    {"agent": "ARL", "status": "MATCHED"},
                    {"agent": "RCA", "root_cause": None}
                ],
                "system_health": {"cpu": 85, "memory": "24GB"},
                "ttl": 3600
            },
            {
                "line_id": "L-4",
                "execution_timeline": [
                    {"agent": "ACC", "decision": "PASS"},
                    {"agent": "PDR", "rail": "IMPS@HDFC"},
                    {"agent": "ARL", "status": "MATCHED"},
                    {"agent": "RCA", "root_cause": None}
                ],
                "system_health": {"cpu": 56, "memory": "11GB"},
                "ttl": 3600
            },
            {
                "line_id": "L-5",
                "execution_timeline": [
                    {"agent": "ACC", "decision": "PASS"},
                    {"agent": "PDR", "rail": "IMPS@HDFC"},
                    {"agent": "ARL", "status": "MATCHED"},
                    {"agent": "RCA", "root_cause": None}
                ],
                "system_health": {"cpu": 21, "memory": "20GB"},
                "ttl": 3600
            }
        ]
        
        for data in redis_data:
            redis_record = RedisTable(
                line_id=data["line_id"],
                execution_timeline=data["execution_timeline"],
                system_health=data["system_health"],
                ttl=data["ttl"]
            )
            db.add(redis_record)
        
        db.commit()
        print("✅ Redis table populated successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error populating redis table: {e}")
        return False

def populate_pdr_table(db):
    """Populate pdr_table with the provided data"""
    try:
        pdr_data = [
            {
                "line_id": "L-1",
                "batch_id": "BATCH-1",
                "rail_selected": "IMPS@HDFC",
                "fallbacks": {"alt": "NEFT@HDFC"},
                "expected_amount": 912001.78,
                "expected_currency": "INR",
                "expected_utr": "UTR000000",
                "status": "SUCCESS",
                "created_at": datetime.fromisoformat("2024-10-02T18:11:09")
            },
            {
                "line_id": "L-2",
                "batch_id": "BATCH-1",
                "rail_selected": "NEFT@ICICI",
                "fallbacks": {"alt": "IMPS@ICICI"},
                "expected_amount": 540252.97,
                "expected_currency": "INR",
                "expected_utr": "UTR000001",
                "status": "FAILED",
                "created_at": datetime.fromisoformat("2024-10-03T04:20:05")
            },
            {
                "line_id": "L-3",
                "batch_id": "BATCH-1",
                "rail_selected": "NEFT@ICICI",
                "fallbacks": {"alt": "NEFT@HDFC"},
                "expected_amount": 534772.99,
                "expected_currency": "INR",
                "expected_utr": "UTR000002",
                "status": "SUCCESS",
                "created_at": datetime.fromisoformat("2024-10-02T05:23:18")
            },
            {
                "line_id": "L-4",
                "batch_id": "BATCH-1",
                "rail_selected": "RTGS@SBI",
                "fallbacks": {"alt": "IMPS@ICICI"},
                "expected_amount": 181322.89,
                "expected_currency": "INR",
                "expected_utr": "UTR000003",
                "status": "SUCCESS",
                "created_at": datetime.fromisoformat("2024-10-04T16:55:20")
            },
            {
                "line_id": "L-5",
                "batch_id": "BATCH-1",
                "rail_selected": "NEFT@ICICI",
                "fallbacks": {"alt": "IMPS@ICICI"},
                "expected_amount": 238125.64,
                "expected_currency": "INR",
                "expected_utr": "UTR000004",
                "status": "SUCCESS",
                "created_at": datetime.fromisoformat("2024-10-01T05:21:04")
            }
        ]
        
        for data in pdr_data:
            pdr_record = PdrTable(
                line_id=data["line_id"],
                batch_id=data["batch_id"],
                rail_selected=data["rail_selected"],
                fallbacks=data["fallbacks"],
                expected_amount=data["expected_amount"],
                expected_currency=data["expected_currency"],
                expected_utr=data["expected_utr"],
                status=data["status"],
                created_at=data["created_at"]
            )
            db.add(pdr_record)
        
        db.commit()
        print("✅ PDR table populated successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error populating PDR table: {e}")
        return False

def populate_arl_table(db):
    """Populate arl_table with the provided data"""
    try:
        arl_data = [
            {
                "recon_id": 1,
                "line_id": "L-1",
                "utr": "UTR-000000",
                "psp_reference": "PSP-000000",
                "match_status": "MATCHED",
                "match_reason": "Success",
                "journal": {"debit": "Expense", "credit": "Bank"},
                "metadata": {"remitter": "Alice", "beneficiary": "Bob"},
                "created_at": datetime.fromisoformat("2024-10-02T18:11:09")
            },
            {
                "recon_id": 2,
                "line_id": "L-2",
                "utr": "UTR-000001",
                "psp_reference": "PSP-000001",
                "match_status": "EXCEPTION",
                "match_reason": "Amount Mismatch",
                "journal": {"debit": "Expense", "credit": "Bank"},
                "metadata": {"remitter": "Alice", "beneficiary": "Bob"},
                "created_at": datetime.fromisoformat("2024-10-03T04:20:05")
            },
            {
                "recon_id": 3,
                "line_id": "L-3",
                "utr": "UTR-000002",
                "psp_reference": "PSP-000002",
                "match_status": "MATCHED",
                "match_reason": "Success",
                "journal": {"debit": "Expense", "credit": "Bank"},
                "metadata": {"remitter": "Alice", "beneficiary": "Bob"},
                "created_at": datetime.fromisoformat("2024-10-02T05:23:18")
            },
            {
                "recon_id": 4,
                "line_id": "L-4",
                "utr": "UTR-000003",
                "psp_reference": "PSP-000003",
                "match_status": "MATCHED",
                "match_reason": "Success",
                "journal": {"debit": "Expense", "credit": "Bank"},
                "metadata": {"remitter": "Alice", "beneficiary": "Bob"},
                "created_at": datetime.fromisoformat("2024-10-04T16:55:20")
            },
            {
                "recon_id": 5,
                "line_id": "L-5",
                "utr": "UTR-000004",
                "psp_reference": "PSP-000004",
                "match_status": "MATCHED",
                "match_reason": "Success",
                "journal": {"debit": "Expense", "credit": "Bank"},
                "metadata": {"remitter": "Alice", "beneficiary": "Bob"},
                "created_at": datetime.fromisoformat("2024-10-01T05:21:04")
            }
        ]
        
        for data in arl_data:
            arl_record = ArlTable(
                recon_id=data["recon_id"],
                line_id=data["line_id"],
                utr=data["utr"],
                psp_reference=data["psp_reference"],
                match_status=data["match_status"],
                match_reason=data["match_reason"],
                journal=data["journal"],
                metadata_info=data["metadata"],
                created_at=data["created_at"]
            )
            db.add(arl_record)
        
        db.commit()
        print("✅ ARL table populated successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error populating ARL table: {e}")
        return False

def populate_all_tables():
    """Populate all new tables with data"""
    db = SessionLocal()
    try:
        print("🚀 Starting to populate all tables...")
        
        # Populate each table
        redis_success = populate_redis_table(db)
        pdr_success = populate_pdr_table(db)
        arl_success = populate_arl_table(db)
        
        if redis_success and pdr_success and arl_success:
            print("✅ All tables populated successfully!")
            return True
        else:
            print("❌ Some tables failed to populate")
            return False
    except Exception as e:
        print(f"❌ Error populating tables: {e}")
        return False
    finally:
        db.close()
