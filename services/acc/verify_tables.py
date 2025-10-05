#!/usr/bin/env python3

"""
Script to verify that the new tables were created and populated correctly
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
POSTGRES_URL = "postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway"

# PostgreSQL setup
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_tables():
    """Verify that all tables exist and have data"""
    db = SessionLocal()
    try:
        print("🔍 Verifying tables...")
        
        # Check redis_table
        result = db.execute(text("SELECT COUNT(*) FROM redis_table"))
        redis_count = result.scalar()
        print(f"✅ redis_table: {redis_count} records")
        
        # Check pdr_table
        result = db.execute(text("SELECT COUNT(*) FROM pdr_table"))
        pdr_count = result.scalar()
        print(f"✅ pdr_table: {pdr_count} records")
        
        # Check arl_table
        result = db.execute(text("SELECT COUNT(*) FROM arl_table"))
        arl_count = result.scalar()
        print(f"✅ arl_table: {arl_count} records")
        
        # Show sample data from each table
        print("\n📊 Sample data from redis_table:")
        result = db.execute(text("SELECT line_id, execution_timeline, system_health FROM redis_table LIMIT 2"))
        for row in result:
            print(f"  Line ID: {row[0]}")
            print(f"  Execution Timeline: {row[1]}")
            print(f"  System Health: {row[2]}")
            print()
        
        print("📊 Sample data from pdr_table:")
        result = db.execute(text("SELECT line_id, batch_id, rail_selected, status FROM pdr_table LIMIT 2"))
        for row in result:
            print(f"  Line ID: {row[0]}, Batch: {row[1]}, Rail: {row[2]}, Status: {row[3]}")
        
        print("\n📊 Sample data from arl_table:")
        result = db.execute(text("SELECT recon_id, line_id, match_status, match_reason FROM arl_table LIMIT 2"))
        for row in result:
            print(f"  Recon ID: {row[0]}, Line ID: {row[1]}, Status: {row[2]}, Reason: {row[3]}")
        
        print(f"\n✅ All tables verified successfully!")
        print(f"📋 Summary:")
        print(f"  - redis_table: {redis_count} records")
        print(f"  - pdr_table: {pdr_count} records")
        print(f"  - arl_table: {arl_count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    verify_tables()
