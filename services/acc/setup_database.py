#!/usr/bin/env python3
"""
Database setup script for ACC Agent Service
Creates tables in PostgreSQL and tests Neo4j connection
"""

from database import create_tables, save_acc_agent_result, save_to_neo4j, save_payment_file, get_db
from sqlalchemy.orm import Session
import json

def test_postgres_connection():
    """Test PostgreSQL connection and create tables"""
    try:
        print("Creating PostgreSQL tables...")
        create_tables()
        print("✅ PostgreSQL tables created successfully!")
        
        # Test saving a sample record
        db = next(get_db())
        sample_id = save_acc_agent_result(
            db=db,
            line_id="TEST001",
            beneficiary="Test Beneficiary",
            ifsc="TEST0001234",
            amount=1000.00,
            policy_version="acc-1.4.2",
            status="PASS",
            decision_reason=json.dumps(["Test reason"]),
            evidence_ref=json.dumps(["pan", "bank"])
        )
        
        if sample_id:
            print(f"✅ Test record saved to PostgreSQL with ID: {sample_id}")
        else:
            print("❌ Failed to save test record to PostgreSQL")
            
        # Test saving a sample payment file
        sample_payment_data = {
            "filename": "test_payments_2025_10_03.csv",
            "data": {
                "transactions": [
                    {
                        "payment_type": "payroll",
                        "transaction_id": "TXN001",
                        "amount": 50000,
                        "beneficiary": "John Doe",
                        "ifsc": "YESB0000001",
                        "status": "PASS"
                    },
                    {
                        "payment_type": "vendor_payment",
                        "transaction_id": "TXN002", 
                        "amount": 75000,
                        "beneficiary": "Vendor Corp",
                        "ifsc": "HDFC0001234",
                        "status": "FAIL"
                    }
                ],
                "metadata": {
                    "total_amount": 125000,
                    "total_transactions": 2,
                    "created_at": "2025-10-03T10:00:00Z",
                    "processed_by": "ACC Agent v1.4.2"
                }
            }
        }
        
        payment_file_id = save_payment_file(db, sample_payment_data["filename"], sample_payment_data["data"])
        
        if payment_file_id:
            print(f"✅ Test payment file saved to PostgreSQL with ID: {payment_file_id}")
        else:
            print("❌ Failed to save test payment file to PostgreSQL")
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_neo4j_connection():
    """Test Neo4j connection"""
    try:
        print("Testing Neo4j connection...")
        print("Using Neo4j Aura cloud instance...")
        success = save_to_neo4j(
            line_id="TEST001",
            beneficiary="Test Beneficiary",
            ifsc="TEST0001234",
            amount=1000.00,
            status="PASS",
            decision_reason=json.dumps(["Test reason"]),
            evidence_ref=json.dumps(["pan", "bank"])
        )
        
        if success:
            print("✅ Neo4j connection successful!")
            print("✅ Test node created in Neo4j Aura")
        else:
            print("❌ Neo4j connection failed")
            
        return success
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def test_payment_file_retrieval():
    """Test retrieving payment files from database"""
    try:
        print("📁 Testing payment file retrieval...")
        db = next(get_db())
        
        # Query payment files
        from database import PaymentFile
        payment_files = db.query(PaymentFile).all()
        
        if payment_files:
            print(f"✅ Found {len(payment_files)} payment files in database:")
            for pf in payment_files:
                print(f"   - ID: {pf.id}, Filename: {pf.filename}")
                # Parse and display sample data
                try:
                    data = json.loads(pf.data)
                    if 'transactions' in data:
                        print(f"     Transactions: {len(data['transactions'])}")
                    if 'metadata' in data:
                        print(f"     Total Amount: {data['metadata'].get('total_amount', 'N/A')}")
                except:
                    print(f"     Data: {pf.data[:100]}...")
        else:
            print("❌ No payment files found in database")
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Payment file retrieval failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up ACC Agent Database...")
    print("=" * 50)
    
    # Test PostgreSQL
    postgres_ok = test_postgres_connection()
    print()
    
    # Test Neo4j
    neo4j_ok = test_neo4j_connection()
    print()
    
    # Test payment file retrieval
    payment_files_ok = test_payment_file_retrieval()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Setup Summary:")
    print(f"PostgreSQL: {'✅ Connected' if postgres_ok else '❌ Failed'}")
    print(f"Neo4j: {'✅ Connected' if neo4j_ok else '❌ Failed'}")
    print(f"Payment Files: {'✅ Working' if payment_files_ok else '❌ Failed'}")
    
    if postgres_ok and neo4j_ok and payment_files_ok:
        print("🎉 All databases and features working successfully!")
        print("📋 Sample data created:")
        print("   - ACC Agent records in PostgreSQL")
        print("   - Payment files in PostgreSQL") 
        print("   - Graph nodes in Neo4j")
    else:
        print("⚠️  Some components failed. Check your credentials and connections.")

if __name__ == "__main__":
    main()
