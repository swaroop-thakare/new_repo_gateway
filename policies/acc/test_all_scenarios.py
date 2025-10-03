#!/usr/bin/env python3
"""
Comprehensive test script for OPA server with all payment types and scenarios
"""

import requests
import json
import time

def test_opa_scenario(scenario_name, payload, expected_result="PASS"):
    """Test a specific scenario and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {scenario_name}")
    print(f"📋 Expected: {expected_result}")
    print(f"{'='*60}")
    
    opa_url = "http://localhost:8181/v1/data/arealis/compliance/routing/v1"
    
    try:
        # Wrap in input as required by OPA
        opa_payload = {"input": payload}
        
        print(f"📤 Sending to: {opa_url}")
        print(f"📋 Payment Type: {payload['transaction']['payment_type']}")
        print(f"💰 Amount: {payload['transaction']['amount']} {payload['transaction']['currency']}")
        print(f"🏦 Method: {payload['transaction']['method']}")
        
        response = requests.post(
            opa_url,
            json=opa_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if "result" in result:
                allow = result["result"].get("allow", False)
                violations = result["result"].get("violations", [])
                
                decision = "PASS" if allow else "FAIL"
                print(f"\n🎯 Result: {decision}")
                
                if violations:
                    print(f"📝 Violations ({len(violations)}):")
                    for i, violation in enumerate(violations, 1):
                        print(f"   {i}. {violation}")
                else:
                    print("✅ No violations found")
                
                # Check if result matches expectation
                if (expected_result == "PASS" and allow) or (expected_result == "FAIL" and not allow):
                    print(f"✅ Test PASSED - Expected {expected_result}, got {decision}")
                    return True
                else:
                    print(f"❌ Test FAILED - Expected {expected_result}, got {decision}")
                    return False
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ OPA error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ OPA server is not running. Please start it with Docker.")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all test scenarios"""
    print("🚀 Starting Comprehensive OPA Server Tests")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: SALARY - PASS Case
    salary_pass_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "SALARY",
            "transaction_id": "TXN001",
            "sender": {
                "name": "ABC Corp",
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
    
    result1 = test_opa_scenario("SALARY - PASS Case", salary_pass_payload, "PASS")
    test_results.append(("SALARY - PASS", result1))
    
    # Test 2: SALARY - FAIL Case (Multiple Violations)
    salary_fail_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "SALARY",
            "transaction_id": "TXN002",
            "sender": {
                "name": "ABC Corp",
                "account_number": "98765432100",
                "ifsc_code": "INVALIDIFSC12",
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
            "currency": "USD",
            "method": "UPI",
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
                "employee_id": "",
                "department": None,
                "payment_frequency": None,
                "invoice_number": None,
                "invoice_date": None,
                "gst_number": None,
                "pan_number": "",
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
                    "aadhaar_seeding_status": "NOT_LINKED",
                    "category": "Individual",
                    "full_name": "John Doe",
                    "first_name": "John",
                    "middle_name": "Hartwell",
                    "last_name": "Doe"
                },
                "message": "PAN verification failed",
                "verification": "failed",
                "traceId": "trace-123"
            },
            "bank": {
                "reference_id": 34,
                "name_at_bank": "BHARATHTEST GKUMARUT",
                "bank_name": "YES BANK",
                "branch": "SANTACRUZ, MUMBAI",
                "name_match_score": "90.00",
                "name_match_result": "GOOD_PARTIAL_MATCH",
                "account_status": "INVALID",
                "account_status_code": "ACCOUNT_IS_INVALID"
            }
        }
    }
    
    result2 = test_opa_scenario("SALARY - FAIL Case (Multiple Violations)", salary_fail_payload, "FAIL")
    test_results.append(("SALARY - FAIL", result2))
    
    # Test 3: LOAN_DISBURSEMENT - PASS Case
    loan_pass_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "LOAN_DISBURSEMENT",
            "transaction_id": "TXN003",
            "sender": {
                "name": "ABC Bank",
                "account_number": "98765432100",
                "ifsc_code": "HDFC0001234",
                "bank_name": "HDFC Bank",
                "kyc_verified": True,
                "credit_score": 800
            },
            "receiver": {
                "name": "Jane Smith",
                "account_number": "1718543210",
                "ifsc_code": "YESB0000001",
                "bank_name": "YES Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "amount": 75000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Personal Loan Disbursement",
            "schedule_datetime": "2025-10-02T10:00:00Z",
            "location": {
                "city": "Delhi",
                "gps_coordinates": {
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
            },
            "additional_fields": {
                "employee_id": None,
                "department": None,
                "payment_frequency": None,
                "invoice_number": None,
                "invoice_date": None,
                "gst_number": None,
                "pan_number": "ABCDE1234A",
                "vendor_code": None,
                "loan_account_number": "LOAN123456",
                "loan_type": "PERSONAL",
                "sanction_date": "2025-09-15",
                "interest_rate": 12.5,
                "tenure_months": 36,
                "borrower_verification_status": "APPROVED"
            }
        },
        "verifications": {
            "cibil_check_performed": True,
            "cibil_score": 720
        }
    }
    
    result3 = test_opa_scenario("LOAN_DISBURSEMENT - PASS Case", loan_pass_payload, "PASS")
    test_results.append(("LOAN_DISBURSEMENT - PASS", result3))
    
    # Test 4: LOAN_DISBURSEMENT - FAIL Case
    loan_fail_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "LOAN_DISBURSEMENT",
            "transaction_id": "TXN004",
            "sender": {
                "name": "ABC Bank",
                "account_number": "98765432100",
                "ifsc_code": "HDFC0001234",
                "bank_name": "HDFC Bank",
                "kyc_verified": True,
                "credit_score": 800
            },
            "receiver": {
                "name": "Jane Smith",
                "account_number": "1718543210",
                "ifsc_code": "YESB0000001",
                "bank_name": "YES Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "amount": 75000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Personal Loan Disbursement",
            "schedule_datetime": "2025-10-02T10:00:00Z",
            "location": {
                "city": "Delhi",
                "gps_coordinates": {
                    "latitude": 28.6139,
                    "longitude": 77.2090
                }
            },
            "additional_fields": {
                "employee_id": None,
                "department": None,
                "payment_frequency": None,
                "invoice_number": None,
                "invoice_date": None,
                "gst_number": None,
                "pan_number": "",
                "vendor_code": None,
                "loan_account_number": "",
                "loan_type": "",
                "sanction_date": "2025-09-15",
                "interest_rate": 0,
                "tenure_months": 36,
                "borrower_verification_status": "PENDING"
            }
        },
        "verifications": {
            "cibil_check_performed": False,
            "cibil_score": 650
        }
    }
    
    result4 = test_opa_scenario("LOAN_DISBURSEMENT - FAIL Case", loan_fail_payload, "FAIL")
    test_results.append(("LOAN_DISBURSEMENT - FAIL", result4))
    
    # Test 5: VENDOR_PAYMENT - PASS Case
    vendor_pass_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "VENDOR_PAYMENT",
            "transaction_id": "TXN005",
            "sender": {
                "name": "ABC Corp",
                "account_number": "98765432100",
                "ifsc_code": "HDFC0001234",
                "bank_name": "HDFC Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "receiver": {
                "name": "Vendor Solutions Pvt Ltd",
                "account_number": "1718543210",
                "ifsc_code": "YESB0000001",
                "bank_name": "YES Bank",
                "kyc_verified": True,
                "credit_score": 720
            },
            "amount": 30000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Vendor Payment for Services",
            "schedule_datetime": "2025-10-02T10:00:00Z",
            "location": {
                "city": "Bangalore",
                "gps_coordinates": {
                    "latitude": 12.9716,
                    "longitude": 77.5946
                }
            },
            "additional_fields": {
                "employee_id": None,
                "department": None,
                "payment_frequency": None,
                "invoice_number": "INV001",
                "invoice_date": "2025-10-01",
                "gst_number": "22AAAAA0000A1Z5",
                "pan_number": "ABCDE1234A",
                "vendor_code": "VENDOR123",
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
                "verification": "success"
            },
            "bank": {
                "account_status": "VALID"
            }
        }
    }
    
    result5 = test_opa_scenario("VENDOR_PAYMENT - PASS Case", vendor_pass_payload, "PASS")
    test_results.append(("VENDOR_PAYMENT - PASS", result5))
    
    # Test 6: VENDOR_PAYMENT - FAIL Case
    vendor_fail_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "VENDOR_PAYMENT",
            "transaction_id": "TXN006",
            "sender": {
                "name": "ABC Corp",
                "account_number": "98765432100",
                "ifsc_code": "HDFC0001234",
                "bank_name": "HDFC Bank",
                "kyc_verified": True,
                "credit_score": 750
            },
            "receiver": {
                "name": "Vendor Solutions Pvt Ltd",
                "account_number": "1718543210",
                "ifsc_code": "YESB0000001",
                "bank_name": "YES Bank",
                "kyc_verified": True,
                "credit_score": 720
            },
            "amount": 100000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Vendor Payment for Services",
            "schedule_datetime": "2025-10-02T10:00:00Z",
            "location": {
                "city": "Bangalore",
                "gps_coordinates": {
                    "latitude": 12.9716,
                    "longitude": 77.5946
                }
            },
            "additional_fields": {
                "employee_id": None,
                "department": None,
                "payment_frequency": None,
                "invoice_number": "",
                "invoice_date": "",
                "gst_number": "",
                "pan_number": "",
                "vendor_code": "",
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
                "verification": "failed"
            },
            "bank": {
                "account_status": "INVALID"
            }
        }
    }
    
    result6 = test_opa_scenario("VENDOR_PAYMENT - FAIL Case", vendor_fail_payload, "FAIL")
    test_results.append(("VENDOR_PAYMENT - FAIL", result6))
    
    # Test 7: UPI Transaction - FAIL Case (Amount Limit)
    upi_fail_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "SALARY",
            "transaction_id": "TXN007",
            "sender": {
                "name": "ABC Corp",
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
            "amount": 600000,
            "currency": "INR",
            "method": "UPI",
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
    
    result7 = test_opa_scenario("UPI Transaction - FAIL Case (Amount Limit)", upi_fail_payload, "FAIL")
    test_results.append(("UPI - FAIL", result7))
    
    # Test 8: PAYROLL - PASS Case (Alternative to SALARY)
    payroll_pass_payload = {
        "policy_version": "acc-1.4.2",
        "transaction": {
            "payment_type": "PAYROLL",
            "transaction_id": "TXN008",
            "sender": {
                "name": "ABC Corp",
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
            "amount": 45000,
            "currency": "INR",
            "method": "NEFT",
            "purpose": "Monthly Payroll",
            "schedule_datetime": "2025-10-02T10:00:00Z",
            "location": {
                "city": "Mumbai",
                "gps_coordinates": {
                    "latitude": 19.076,
                    "longitude": 72.8777
                }
            },
            "additional_fields": {
                "employee_id": "EMP456",
                "department": "HR",
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
    
    result8 = test_opa_scenario("PAYROLL - PASS Case", payroll_pass_payload, "PASS")
    test_results.append(("PAYROLL - PASS", result8))
    
    # Print Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! OPA server is working perfectly!")
    else:
        print(f"\n⚠️  Some tests failed. Check the OPA server configuration.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
