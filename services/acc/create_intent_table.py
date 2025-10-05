#!/usr/bin/env python3
"""
Create intent_table in the database
"""

from database import create_tables, IntentTable, get_db
from sqlalchemy.orm import Session

def create_intent_table():
    """Create the intent_table in the database"""
    try:
        print("🗄️  Creating intent_table...")
        
        # Create all tables (including intent_table)
        create_tables()
        
        print("✅ intent_table created successfully!")
        print("\n📋 Table Schema:")
        print("   - id (Primary Key)")
        print("   - payment_type")
        print("   - transaction_id")
        print("   - sender_name, sender_account_number, sender_ifsc_code, sender_bank_name")
        print("   - receiver_name, receiver_account_number, receiver_ifsc_code, receiver_bank_name")
        print("   - amount, currency, method, purpose, schedule_datetime")
        print("   - city, latitude, longitude")
        print("   - employee_id, department, payment_frequency")
        print("   - created_at, updated_at")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating intent_table: {e}")
        return False

def verify_table_exists():
    """Verify that intent_table exists and is accessible"""
    try:
        print("\n🔍 Verifying intent_table...")
        db = next(get_db())
        
        # Try to query the table (should return empty result)
        result = db.query(IntentTable).first()
        print("✅ intent_table is accessible and ready for data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying intent_table: {e}")
        return False

def main():
    """Create intent_table and verify it works"""
    print("🚀 Creating Intent Table")
    print("=" * 50)
    
    # Create the table
    table_created = create_intent_table()
    
    if table_created:
        # Verify it works
        verification_ok = verify_table_exists()
        
        if verification_ok:
            print("\n🎉 intent_table created and verified successfully!")
            print("📝 Ready to store transaction data")
        else:
            print("\n⚠️  Table created but verification failed")
    else:
        print("\n❌ Failed to create intent_table")

if __name__ == "__main__":
    main()
