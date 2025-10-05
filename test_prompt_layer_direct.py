#!/usr/bin/env python3
"""
Test Prompt Layer directly with mock data to verify it's working
"""

import requests
import json

def test_prompt_layer_with_mock_data():
    """Test Prompt Layer with comprehensive mock data"""
    print("🧪 Testing Prompt Layer with Mock Data...")
    
    # Test with comprehensive mock data
    query_data = {
        "query": "Why did line L-2 fail and what should we do about it?",
        "batch_id": "B-2025-10-03-01",
        "line_id": "L-2",
        "context": {
            "acc_output": {
                "decision": "FAIL",
                "reasons": ["SANCTION_LIST_MATCH"],
                "evidence_refs": ["s3://evidence/HDFC/B-2025-09-19-01/L-2/sanction_check.pdf"],
                "timestamp": "2025-09-20T10:10:00Z",
                "beneficiary": {
                    "name": "Beta Corp",
                    "ifsc": "HDFC0001234",
                    "account": "XXXXXXXX5678"
                },
                "sender": {
                    "merchant_id": "M124",
                    "kyc_ref": "KYC999"
                },
                "amount": 300000,
                "currency": "INR",
                "purpose": "VENDOR"
            },
            "rca_output": {
                "root_cause": "SANCTION_LIST_MATCH (beneficiary 'Beta Corp' matched RBI watchlist entry ID: WL-2023-0456)",
                "explanation": "Line L-2 failed because the beneficiary 'Beta Corp' was flagged on the RBI sanction list during the compliance check on 2025-09-20 at 10:10:00Z, with a match confidence score of 0.95 based on name and IFSC 'HDFC0001234'; this indicates a potential regulatory risk.",
                "recommended_actions": [
                    "Re-verify KYC details for 'Beta Corp' using updated UIDAI/PAN data.",
                    "Contact HDFC compliance team for manual review of transactionReferenceNo '7577'.",
                    "Remove 'Beta Corp' from the transaction list if sanction persists."
                ],
                "neo4j_state": "Line → Decision [FAIL] → Explanation [RCA report]",
                "fault_party": "Remitter Bank",
                "retry_eligible": False,
                "priority_score": 100,
                "compensation_amount": 0,
                "evidence_refs": ["s3://evidence/HDFC/B-2025-10-03-01/L-2/rca_analysis.json"]
            },
            "arl_output": {
                "status": "FAILED",
                "matched": [],
                "exceptions": [
                    {
                        "type": "TRANSACTION_FAILED",
                        "line_id": "L-2",
                        "details": "No settlement due to ACC failure",
                        "timestamp": "2025-09-20T10:15:00Z"
                    }
                ],
                "journals": [],
                "evidence_refs": ["s3://evidence/HDFC/B-2025-10-03-01/L-2/arl_reconciliation.json"]
            },
            "crrak_output": {
                "audit_report": {
                    "compliance_status": "NON_COMPLIANT",
                    "combined_details": "ARL: Transaction failed with no settlement recorded | RCA: Beneficiary 'Beta Corp' matched RBI watchlist entry ID WL-2023-0456",
                    "neo4j_state": "Line → Journal [FAILED] → Report [CRRAK]",
                    "audit_timestamp": "2025-10-05T09:58:00Z"
                },
                "report_ref": "s3://audit/HDFC/B-2025-10-03-01/L-2/report.pdf",
                "evidence_refs": ["s3://audit/HDFC/B-2025-10-03-01/L-2/audit_pack.pdf"]
            }
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8011/api/v1/query",
            json=query_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prompt Layer with mock data successful!")
            print(f"📝 Query: {data['query']}")
            print(f"🎯 Failure Reason: {data['response']['failure_reason']}")
            print(f"📊 Confidence Score: {data['response']['confidence_score']}")
            print(f"🔗 Evidence Refs: {len(data['evidence_refs'])} files")
            
            # Check detailed analysis
            if data['response']['detailed_analysis'] and data['response']['detailed_analysis'] != "No detailed analysis available":
                print("✅ Detailed Analysis: Available")
                print(f"   Analysis: {data['response']['detailed_analysis'][:100]}...")
            else:
                print("⚠️  Detailed Analysis: Not available")
            
            # Check recommended actions
            actions = data['response']['recommended_actions']
            if actions and len(actions) > 0:
                print(f"✅ Recommended Actions: {len(actions)} actions")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action.get('action', 'Unknown')} - {action.get('priority', 'Unknown')} priority")
            else:
                print("⚠️  Recommended Actions: Not available")
            
            # Check additional notes
            if data['response']['additional_notes'] and data['response']['additional_notes'] != "No additional notes available":
                print("✅ Additional Notes: Available")
                print(f"   Notes: {data['response']['additional_notes'][:100]}...")
            else:
                print("⚠️  Additional Notes: Not available")
            
            return True
        else:
            print(f"❌ Prompt Layer test failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Prompt Layer test error: {e}")
        return False

def main():
    """Run Prompt Layer test with mock data"""
    print("🎯 Testing Prompt Layer (xAI) with Mock Data")
    print("=" * 60)
    
    # Test Prompt Layer with comprehensive mock data
    test_prompt_layer_with_mock_data()
    
    print("\n" + "=" * 60)
    print("🎉 Prompt Layer Test Complete!")
    print("\n🌐 Test the frontend:")
    print("1. Go to http://localhost:3001")
    print("2. Click 'Prompt Layer (xAI)' in sidebar")
    print("3. Enter query: 'Why did line L-2 fail and what should we do about it?'")
    print("4. The system should now show detailed analysis!")

if __name__ == "__main__":
    main()
