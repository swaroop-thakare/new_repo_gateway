#!/usr/bin/env python3
"""
Test script to verify ACC agent integration with OPA
"""

import requests
import json

def test_acc_agent():
    """Test the ACC agent with sample transaction data"""
    
    # Sample transaction data
    test_transactions = [
        {
            "payment_type": "SALARY",
            "transaction_id": "TXN001",
            "sender": {
                "name": "ABC Corp",
                "account_number": "98765432100",
                "ifsc_code": "HDFC0001234",
                "bank_name": "HDFC Bank",
                "kyc_verified": None,
                "credit_score": None
            },
            "receiver": {
                "name": "John Doe",
                "account_number": "1718543210",
                "ifsc_code": "YESB0000001",
                "bank_name": "YES Bank",
                "kyc_verified": None,
                "credit_score": None
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
                "department": None,
                "payment_frequency": None,
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
    
    # Test ACC agent endpoint
    acc_url = "http://localhost:8000/acc/decide"
    
    try:
        print("🚀 Testing ACC Agent Integration with OPA...")
        print(f"📤 Sending request to: {acc_url}")
        print(f"📋 Transaction data: {json.dumps(test_transactions[0], indent=2)}")
        
        response = requests.post(
            acc_url,
            json=test_transactions,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ ACC Agent Response:")
            print(json.dumps(result, indent=2))
            
            # Check if OPA integration worked
            if "decisions" in result and len(result["decisions"]) > 0:
                decision = result["decisions"][0]
                print(f"\n🎯 Decision: {decision.get('decision', 'UNKNOWN')}")
                print(f"📝 Reasons: {decision.get('reasons', [])}")
                print(f"🔍 Evidence: {decision.get('evidence_refs', [])}")
                
                if decision.get('decision') == 'PASS':
                    print("✅ Integration successful! OPA returned PASS")
                elif decision.get('decision') == 'FAIL':
                    print("⚠️  Integration successful! OPA returned FAIL with violations")
                else:
                    print("❌ Integration issue detected")
            else:
                print("❌ No decisions returned from ACC agent")
        else:
            print(f"❌ ACC Agent error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ACC Agent is not running. Please start it with: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_acc_agent()
