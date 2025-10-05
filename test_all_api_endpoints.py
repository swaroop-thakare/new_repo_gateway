#!/usr/bin/env python3
"""
Test all API endpoints for frontend integration
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(name, url, method="GET", data=None):
    """Test a single API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: {response.status_code}")
            return True, data
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {e}")
        return False, None

def test_all_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing All API Endpoints")
    print("=" * 60)
    
    endpoints = [
        ("Overview Metrics", "http://localhost:3001/api/overview/metrics"),
        ("Pending Approvals", "http://localhost:3001/api/approvals/pending"),
        ("Live Funnel Status", "http://localhost:3001/api/livefunnel/status"),
        ("Payments Report", "http://localhost:3001/api/payments/report"),
        ("SLA Breaches", "http://localhost:3001/api/sla/breaches"),
        ("Recent Events", "http://localhost:3001/api/events/recent"),
        ("Open Tasks", "http://localhost:3001/api/tasks/open"),
        ("Ledger Reconciled", "http://localhost:3001/api/ledger/reconciled"),
        ("Audit Reports", "http://localhost:3001/api/audit/reports"),
        ("Prompt Query", "http://localhost:3001/api/prompt/query", "POST", {
            "query": "Why did line L-2 fail?",
            "batch_id": "B-2025-001",
            "line_id": "L-2"
        }),
        ("Prompt History", "http://localhost:3001/api/prompt/history"),
        ("Search Query", "http://localhost:3001/api/search/query", "POST", {
            "query": "TXN-2025-001"
        })
    ]
    
    results = []
    
    for endpoint in endpoints:
        if len(endpoint) == 2:
            name, url = endpoint
            success, data = test_endpoint(name, url)
        elif len(endpoint) == 4:
            name, url, method, data = endpoint
            success, data = test_endpoint(name, url, method, data)
        
        results.append((name, success))
        
        if success and data:
            # Show sample data for key endpoints
            if name in ["Overview Metrics", "Prompt Query"]:
                print(f"   📊 Sample data: {json.dumps(data, indent=2)[:200]}...")
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n🎯 Overall: {successful}/{total} endpoints working")
    
    if successful == total:
        print("🎉 All API endpoints are working!")
        print("\n🌐 Your complete system is ready:")
        print("• Frontend: http://localhost:3001")
        print("• All API endpoints: ✅ Working")
        print("• Prompt Layer: ✅ Connected")
        print("• Agent Integration: ✅ Complete")
    else:
        print(f"⚠️  {total - successful} endpoints need attention")
    
    return successful == total

def test_prompt_layer_integration():
    """Test Prompt Layer integration specifically"""
    print("\n🤖 Testing Prompt Layer Integration...")
    
    # Test with comprehensive data
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
                "amount": 300000
            },
            "rca_output": {
                "root_cause": "SANCTION_LIST_MATCH (beneficiary 'Beta Corp' matched RBI watchlist entry ID: WL-2023-0456)",
                "explanation": "Line L-2 failed because the beneficiary 'Beta Corp' was flagged on the RBI sanction list during the compliance check on 2025-09-20 at 10:10:00Z, with a match confidence score of 0.95 based on name and IFSC 'HDFC0001234'; this indicates a potential regulatory risk.",
                "recommended_actions": [
                    "Re-verify KYC details for 'Beta Corp' using updated UIDAI/PAN data.",
                    "Contact HDFC compliance team for manual review of transactionReferenceNo '7577'.",
                    "Remove 'Beta Corp' from the transaction list if sanction persists."
                ],
                "fault_party": "Remitter Bank",
                "priority_score": 100
            },
            "arl_output": {
                "status": "FAILED",
                "exceptions": [
                    {
                        "type": "TRANSACTION_FAILED",
                        "line_id": "L-2",
                        "details": "No settlement due to ACC failure",
                        "timestamp": "2025-09-20T10:15:00Z"
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8011/api/v1/query",
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prompt Layer integration successful!")
            print(f"📝 Query: {data['query']}")
            print(f"🎯 Failure Reason: {data['response']['failure_reason']}")
            print(f"📊 Confidence Score: {data['response']['confidence_score']}")
            print(f"🔗 Evidence Refs: {len(data['evidence_refs'])} files")
            
            # Check if we got detailed analysis
            if data['response']['detailed_analysis'] and data['response']['detailed_analysis'] != "No detailed analysis available":
                print("✅ Detailed Analysis: Available")
            else:
                print("⚠️  Detailed Analysis: Not available")
            
            return True
        else:
            print(f"❌ Prompt Layer integration failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Prompt Layer integration error: {e}")
        return False

def main():
    """Run comprehensive API endpoint tests"""
    print("🎯 Testing Complete API Integration")
    print("=" * 60)
    
    # Test all frontend API endpoints
    all_endpoints_working = test_all_endpoints()
    
    # Test Prompt Layer integration
    prompt_layer_working = test_prompt_layer_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Final System Status:")
    print(f"• Frontend API Endpoints: {'✅ Working' if all_endpoints_working else '❌ Issues'}")
    print(f"• Prompt Layer Integration: {'✅ Working' if prompt_layer_working else '❌ Issues'}")
    
    if all_endpoints_working and prompt_layer_working:
        print("\n🚀 Your Arealis Gateway v2 system is fully operational!")
        print("🌐 Access: http://localhost:3001")
        print("🤖 Prompt Layer: Click 'Prompt Layer (xAI)' in sidebar")
        print("📊 All dashboards: Real-time data from all agents")
    else:
        print("\n⚠️  Some components need attention")
        if not all_endpoints_working:
            print("• Check frontend API endpoints")
        if not prompt_layer_working:
            print("• Check Prompt Layer service connection")

if __name__ == "__main__":
    main()
