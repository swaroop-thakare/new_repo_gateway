#!/usr/bin/env python3

"""
Debug script to check what's in the database
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import AccAgent, PaymentFile

# Database configuration
POSTGRES_URL = "postgresql://postgres:NmxNfLIKzWQzxwrmQUiKCouDXhcScjcD@switchyard.proxy.rlwy.net:25675/railway"

# PostgreSQL setup
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def debug_database():
    """Debug what's in the database"""
    db = SessionLocal()
    try:
        print("🔍 Debugging database contents...")
        
        # Check acc_agent table
        print("\n📊 ACC Agent Table:")
        acc_records = db.query(AccAgent).all()
        print(f"Total ACC Agent records: {len(acc_records)}")
        
        for record in acc_records:
            print(f"  ID: {record.id}, Line ID: {record.line_id}, Beneficiary: {record.beneficiary}, Amount: {record.amount}, Status: {record.status}")
        
        # Check vendor payments specifically
        print("\n🏪 Vendor Payments (VEN%):")
        vendor_payments = db.query(AccAgent).filter(AccAgent.line_id.like("VEN%")).all()
        print(f"Vendor payment records: {len(vendor_payments)}")
        
        for record in vendor_payments:
            print(f"  Line ID: {record.line_id}, Beneficiary: {record.beneficiary}, Amount: {record.amount}, Status: {record.status}")
        
        # Check payment_files table
        print("\n📁 Payment Files Table:")
        payment_files = db.query(PaymentFile).all()
        print(f"Total Payment Files: {len(payment_files)}")
        
        for pf in payment_files[-3:]:  # Show last 3 files
            print(f"  ID: {pf.id}, Filename: {pf.filename}")
            if pf.data:
                try:
                    import json
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"    Data rows: {len(data['data'])}")
                        # Show first row if available
                        if data['data']:
                            first_row = data['data'][0]
                            if isinstance(first_row, dict):
                                print(f"    First row keys: {list(first_row.keys())}")
                                if 'transaction_id' in first_row:
                                    print(f"    First transaction_id: {first_row['transaction_id']}")
                                if 'method' in first_row:
                                    print(f"    First method: {first_row['method']}")
                except Exception as e:
                    print(f"    Error parsing data: {e}")
        
        # Check for any VEN transactions in payment_files
        print("\n🔍 Searching for VEN transactions in payment_files:")
        ven_found = False
        for pf in payment_files:
            if pf.data:
                try:
                    import json
                    data = json.loads(pf.data) if isinstance(pf.data, str) else pf.data
                    if 'data' in data and isinstance(data['data'], list):
                        for row in data['data']:
                            if isinstance(row, dict) and 'transaction_id' in row:
                                if row['transaction_id'].startswith('VEN'):
                                    print(f"    Found VEN transaction: {row['transaction_id']} in file {pf.filename}")
                                    ven_found = True
                                    if 'method' in row:
                                        print(f"      Method: {row['method']}")
                except Exception as e:
                    continue
        
        if not ven_found:
            print("    No VEN transactions found in payment_files")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_database()
