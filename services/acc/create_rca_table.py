#!/usr/bin/env python3

"""
Script to create the rca_table (blank table)
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
POSTGRES_URL = "postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway"

# PostgreSQL setup
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

def create_rca_table():
    """Create the rca_table"""
    Base.metadata.create_all(bind=engine)
    print("✅ RCA table created successfully!")

def verify_rca_table():
    """Verify that the rca_table was created"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT COUNT(*) FROM rca_table"))
        count = result.scalar()
        print(f"✅ rca_table: {count} records (blank table as requested)")
        return True
    except Exception as e:
        print(f"❌ Error verifying rca_table: {e}")
        return False
    finally:
        db.close()

def main():
    print("🚀 Creating RCA table...")
    
    # Create the table
    create_rca_table()
    
    # Verify the table was created
    verify_rca_table()
    
    print("✅ RCA table setup complete!")

if __name__ == "__main__":
    main()
