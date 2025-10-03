#!/usr/bin/env python3
"""
Direct test of OPA integration from ACC agent
"""

import requests
import json

def test_opa_integration():
    """Test direct OPA call with ACC agent data format"""
    
    # Sample data in ACC agent format
    acc_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
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
        },
        "verifications": {
            "pan": {
                "data": {
                    "aadhaar_seeding_status": "LINKED",
                    "category": "Individual",
                    "full_name": "John Doe",
                    "first_name": "John",
                    "middle_name": "Hartwell",
                    "last_name": "Doe"
                },
                "message": "PAN is valid",
                "verification": "success",
                "traceId": "trace-123"
            },
            "bank": {
                "reference_id": 34,
                "name_at_bank": "BHARATHTEST GKUMARUT",
                "bank_name": "YES BANK",
                "branch": "SANTACRUZ, MUMBAI",
                "name_match_score": "90.00",
                "name_match_result": "GOOD_PARTIAL_MATCH",
                "account_status": "VALID",
                "account_status_code": "ACCOUNT_IS_VALID"
            }
        }
    }
    
    # Test OPA directly
    opa_url = "http://localhost:8181/v1/data/arealis/compliance/routing/v1"
    
    try:
        print("🚀 Testing OPA Integration...")
        print(f"📤 Sending request to: {opa_url}")
        
        # Wrap in input as required by OPA
        opa_payload = {"input": acc_payload}
        
        response = requests.post(
            opa_url,
            json=opa_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ OPA Response:")
            print(json.dumps(result, indent=2))
            
            # Check result
            if "result" in result:
                allow = result["result"].get("allow", False)
                violations = result["result"].get("violations", [])
                
                print(f"\n🎯 Decision: {'PASS' if allow else 'FAIL'}")
                if violations:
                    print(f"📝 Violations: {violations}")
                else:
                    print("✅ No violations found")
                    
                print("\n🎉 OPA Integration successful!")
            else:
                print("❌ Unexpected response format")
        else:
            print(f"❌ OPA error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ OPA server is not running. Please start it with Docker.")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_opa_integration()
