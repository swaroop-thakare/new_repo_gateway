#!/usr/bin/env python3

import requests
import json

# Test data for vendor payment
vendor_test_data = {
    "input": {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "vendor_payment",
            "transaction_id": "VEN001",
            "sender": {
                "name": "ABC Corp",
                "account_number": "3456789012",
                "ifsc_code": "SBIN0567890",
                "bank_name": "State Bank of India",
                "kyc_verified": True,
                "credit_score": 750
            },
            "receiver": {
                "name": "Bob Wilson",
                "account_number": "7654321098",
                "ifsc_code": "PNBA5678901",
                "bank_name": "Punjab National Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "amount": 25000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Vendor Payment",
            "schedule_datetime": "2025-10-02T12:00:00Z",
            "location": {
                "city": "Bangalore",
                "gps_coordinates": {
                    "latitude": 12.9716,
                    "longitude": 77.5946
                }
            },
            "additional_fields": {
                "invoice_number": "INV001",
                "invoice_date": "2025-10-01",
                "gst_number": "29ABCDE1234F1Z5",
                "pan_number": "ABCDE1234A",
                "vendor_code": "VENDOR001"
            }
        },
        "verifications": {
            "pan": {
                "data": {
                    "aadhaar_seeding_status": "LINKED",
                    "category": "Individual",
                    "full_name": "Verified User",
                    "first_name": "Verified",
                    "middle_name": "",
                    "last_name": "User"
                },
                "message": "PAN is valid",
                "verification": "success",
                "traceId": "trace-12345"
            },
            "gstin": {
                "reference_id": 12345,
                "GSTIN": "29ABCDE1234F1Z5",
                "legal_name_of_business": "VERIFIED BUSINESS",
                "trade_name_of_business": "VERIFIED TRADE",
                "constitution_of_business": "Private Limited Company",
                "gst_in_status": "Active",
                "valid": True,
                "message": "GSTIN Exists"
            },
            "bank": {
                "reference_id": 34,
                "name_at_bank": "BOB WILSON",
                "bank_name": "MOCK BANK",
                "branch": "MOCK BRANCH",
                "name_match_score": "90.00",
                "name_match_result": "GOOD_PARTIAL_MATCH",
                "account_status": "VALID",
                "account_status_code": "ACCOUNT_IS_VALID"
            }
        }
    }
}

# Test data for loan disbursement
loan_test_data = {
    "input": {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "loan_disbursement",
            "transaction_id": "LOAN001",
            "sender": {
                "name": "Loan Bank",
                "account_number": "5678901234",
                "ifsc_code": "PNBA5678901",
                "bank_name": "Punjab National Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "receiver": {
                "name": "Charlie Davis",
                "account_number": "5432109876",
                "ifsc_code": "HDFC0567890",
                "bank_name": "HDFC Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "amount": 80000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Loan Disbursement",
            "schedule_datetime": "2025-10-02T14:00:00Z",
            "location": {
                "city": "Hyderabad",
                "gps_coordinates": {
                    "latitude": 17.385,
                    "longitude": 78.4867
                }
            },
            "additional_fields": {
                "loan_account_number": "LOAN001",
                "loan_type": "Personal Loan",
                "sanction_date": "2025-10-01",
                "interest_rate": 12.5,
                "tenure_months": 24,
                "borrower_verification_status": "APPROVED",
                "pan_number": "ABCDE1234A"
            }
        },
        "verifications": {
            "pan": {
                "data": {
                    "aadhaar_seeding_status": "LINKED",
                    "category": "Individual",
                    "full_name": "Verified User",
                    "first_name": "Verified",
                    "middle_name": "",
                    "last_name": "User"
                },
                "message": "PAN is valid",
                "verification": "success",
                "traceId": "trace-12345"
            },
            "bank": {
                "reference_id": 34,
                "name_at_bank": "CHARLIE DAVIS",
                "bank_name": "MOCK BANK",
                "branch": "MOCK BRANCH",
                "name_match_score": "90.00",
                "name_match_result": "GOOD_PARTIAL_MATCH",
                "account_status": "VALID",
                "account_status_code": "ACCOUNT_IS_VALID"
            },
            "cibil_check_performed": True,
            "cibil_score": 750
        }
    }
}

def test_opa_policy(test_name, test_data):
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            "http://localhost:8181/v1/data/arealis/compliance/routing/v1",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OPA Response:")
            print(f"Allow: {result.get('result', {}).get('allow', 'UNKNOWN')}")
            print(f"Violations: {result.get('result', {}).get('violations', [])}")
            
            if result.get('result', {}).get('allow'):
                print("🎉 TEST PASSED - Transaction should be approved")
            else:
                print("❌ TEST FAILED - Transaction was rejected")
                print("Violations found:")
                for violation in result.get('result', {}).get('violations', []):
                    print(f"  - {violation}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 Testing OPA Policies for Vendor Payment and Loan Disbursement")
    
    # Test vendor payment
    test_opa_policy("Vendor Payment PASS Case", vendor_test_data)
    
    # Test loan disbursement  
    test_opa_policy("Loan Disbursement PASS Case", loan_test_data)
    
    print(f"\n{'='*60}")
    print("Testing Complete")
    print(f"{'='*60}")
