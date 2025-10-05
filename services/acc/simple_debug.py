#!/usr/bin/env python3

"""
Simple debug script to check database without neo4j dependency
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
        result = db.execute(text("SELECT COUNT(*) FROM acc_agent"))
        total_count = result.scalar()
        print(f"Total ACC Agent records: {total_count}")
        
        # Get sample records
        result = db.execute(text("SELECT id, line_id, beneficiary, amount, status FROM acc_agent LIMIT 10"))
        records = result.fetchall()
        for record in records:
            print(f"  ID: {record[0]}, Line ID: {record[1]}, Beneficiary: {record[2]}, Amount: {record[3]}, Status: {record[4]}")
        
        # Check vendor payments specifically
        print("\n🏪 Vendor Payments (VEN%):")
        result = db.execute(text("SELECT COUNT(*) FROM acc_agent WHERE line_id LIKE 'VEN%'"))
        ven_count = result.scalar()
        print(f"Vendor payment records: {ven_count}")
        
        result = db.execute(text("SELECT line_id, beneficiary, amount, status FROM acc_agent WHERE line_id LIKE 'VEN%'"))
        ven_records = result.fetchall()
        for record in ven_records:
            print(f"  Line ID: {record[0]}, Beneficiary: {record[1]}, Amount: {record[2]}, Status: {record[3]}")
        
        # Check payment_files table
        print("\n📁 Payment Files Table:")
        result = db.execute(text("SELECT COUNT(*) FROM payment_files"))
        pf_count = result.scalar()
        print(f"Total Payment Files: {pf_count}")
        
        # Get last few files
        result = db.execute(text("SELECT id, filename, data FROM payment_files ORDER BY id DESC LIMIT 3"))
        files = result.fetchall()
        for file_record in files:
            print(f"  ID: {file_record[0]}, Filename: {file_record[1]}")
            if file_record[2]:  # data column
                try:
                    data = json.loads(file_record[2]) if isinstance(file_record[2], str) else file_record[2]
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
        result = db.execute(text("SELECT data FROM payment_files WHERE data IS NOT NULL"))
        all_data = result.fetchall()
        
        for data_record in all_data:
            if data_record[0]:  # data column
                try:
                    data = json.loads(data_record[0]) if isinstance(data_record[0], str) else data_record[0]
                    if 'data' in data and isinstance(data['data'], list):
                        for row in data['data']:
                            if isinstance(row, dict) and 'transaction_id' in row:
                                if row['transaction_id'].startswith('VEN'):
                                    print(f"    Found VEN transaction: {row['transaction_id']}")
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
