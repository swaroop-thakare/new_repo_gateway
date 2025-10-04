#!/usr/bin/env python3
"""
Test script for ACC Agent database integration
"""

import requests
import json

# Test data
test_transaction = [
    {
        "payment_type": "payroll",
        "transaction_id": "TEST001",
        "sender": {
            "name": "Test Corp",
            "account_number": "98765432100",
            "ifsc_code": "HDFC0001234",
            "bank_name": "HDFC Bank",
            "kyc_verified": True,
            "credit_score": 750
        },
        "receiver": {
            "name": "John Doe",
            "account_number": "1718543210",
            "ifsc_code": "YESB0000001",
            "bank_name": "YES Bank",
            "kyc_verified": True,
            "credit_score": 720
        },
        "amount": 50000,
        "currency": "INR",
        "method": "NEFT",
        "purpose": "Salary Payment",
        "schedule_datetime": "2025-10-02T10:00:00Z",
        "location": {
            "city": "Mumbai",
            "gps_coordinates": {
                "latitude": 19.076,
                "longitude": 72.8777
            }
        },
        "additional_fields": {
            "employee_id": "EMP123",
            "department": "Engineering",
            "payment_frequency": "Monthly",
            "invoice_number": None,
            "invoice_date": None,
            "gst_number": None,
            "pan_number": "ABCDE1234A",
            "vendor_code": None,
            "loan_account_number": None,
            "loan_type": None,
            "sanction_date": None,
            "interest_rate": None,
            "tenure_months": None,
            "borrower_verification_status": None
        }
    }
]

def test_acc_decide():
    """Test the ACC decide endpoint with database integration"""
    try:
        print("🧪 Testing ACC Agent with database integration...")
        
        response = requests.post(
            "http://localhost:8000/acc/decide",
            json=test_transaction,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ACC Agent response received:")
            print(json.dumps(result, indent=2))
            
            # Check if database IDs are present
            for decision in result.get("decisions", []):
                if decision.get("postgres_id"):
                    print(f"✅ PostgreSQL record created with ID: {decision['postgres_id']}")
                else:
                    print("❌ PostgreSQL record creation failed")
                    
                if decision.get("neo4j_success"):
                    print("✅ Neo4j record created successfully")
                else:
                    print("❌ Neo4j record creation failed")
                    
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_get_decisions():
    """Test retrieving decisions from database"""
    try:
        print("\n📊 Testing decision retrieval...")
        
        response = requests.get("http://localhost:8000/acc/decisions")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Decisions retrieved successfully:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to retrieve decisions: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Decision retrieval failed: {e}")

def test_payment_file():
    """Test saving payment file"""
    try:
        print("\n💾 Testing payment file save...")
        
        test_file_data = {
            "filename": "test_payment.csv",
            "data": {
                "transactions": test_transaction,
                "metadata": {
                    "created_at": "2025-10-03T10:00:00Z",
                    "total_amount": 50000
                }
            }
        }
        
        response = requests.post(
            "http://localhost:8000/acc/payment-file",
            json=test_file_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment file saved successfully:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to save payment file: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Payment file test failed: {e}")

def test_get_payment_files():
    """Test retrieving payment files"""
    try:
        print("\n📁 Testing payment file retrieval...")
        
        response = requests.get("http://localhost:8000/acc/payment-files")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment files retrieved successfully:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to retrieve payment files: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Payment file retrieval failed: {e}")

def main():
    """Run all tests"""
    print("🚀 ACC Agent Database Integration Test")
    print("=" * 50)
    
    # Test ACC decide endpoint
    test_acc_decide()
    
    # Test decision retrieval
    test_get_decisions()
    
    # Test payment file save
    test_payment_file()
    
    # Test payment file retrieval
    test_get_payment_files()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
