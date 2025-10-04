import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, or_
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
