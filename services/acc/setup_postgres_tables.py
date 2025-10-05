#!/usr/bin/env python3

"""
Script to create and populate the new PostgreSQL tables: redis_table, pdr_table, and arl_table
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration
POSTGRES_URL = "postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway"

# PostgreSQL setup
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    print("✅ Tables created successfully!")

def populate_redis_table():
    """Populate redis_table with the provided data"""
    db = SessionLocal()
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
    finally:
        db.close()

def populate_pdr_table():
    """Populate pdr_table with the provided data"""
    db = SessionLocal()
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
    finally:
        db.close()

def populate_arl_table():
    """Populate arl_table with the provided data"""
    db = SessionLocal()
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
    finally:
        db.close()

def main():
    print("🚀 Setting up new PostgreSQL tables...")
    
    # Create all tables
    print("📋 Creating tables...")
    create_tables()
    
    # Populate all tables with data
    print("📊 Populating tables with data...")
    
    redis_success = populate_redis_table()
    pdr_success = populate_pdr_table()
    arl_success = populate_arl_table()
    
    if redis_success and pdr_success and arl_success:
        print("✅ All tables created and populated successfully!")
        print("\n📋 Tables created:")
        print("  - redis_table (5 records)")
        print("  - pdr_table (5 records)")
        print("  - arl_table (5 records)")
    else:
        print("❌ Failed to populate some tables")
        return False
    
    return True

if __name__ == "__main__":
    main()
