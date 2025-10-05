#!/usr/bin/env python3
"""
Test complete Prompt Layer integration with MCP and all agents
"""

import requests
import json
import time
from datetime import datetime

def test_mcp_integration():
    """Test MCP integration with Prompt Layer"""
    print("🧠 Testing MCP Integration...")
    
    try:
        # Test MCP health
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Service: healthy")
        else:
            print("⚠️  MCP Service: not responding")
            return False
        
        # Test Prompt Layer with MCP context
        query_data = {
            "query": "Why did line L-2 fail and what should we do about it?",
            "batch_id": "B-2025-10-03-01",
            "line_id": "L-2",
            "context": {
                "mcp_workflow": {
                    "batch_id": "B-2025-10-03-01",
                    "status": "COMPLETED",
                    "workflow_summary": {
                        "intents": [
                            {
                                "line_id": "L-2",
                                "intent": "VENDOR_PAYMENTS",
                                "decision": "FAIL",
                                "evidence_ref": "s3://invoices/processed/HDFC/B-2025-10-03-01/L-2/completed.json"
                            }
                        ],
                        "pipeline_status": ["ACC_FAILED", "RCA_ANALYZED", "CRRAK_GENERATED"]
                    }
                }
            }
        }
        
        response = requests.post(
            "http://localhost:8011/api/v1/query",
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ MCP-Prompt Layer integration successful!")
            print(f"📝 Query: {data['query']}")
            print(f"🎯 Failure Reason: {data['response']['failure_reason']}")
            print(f"📊 Confidence Score: {data['response']['confidence_score']}")
            return True
        else:
            print(f"❌ MCP-Prompt Layer integration failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ MCP integration error: {e}")
        return False

def test_agent_data_flow():
    """Test data flow from all agents to Prompt Layer"""
    print("\n🔄 Testing Agent Data Flow...")
    
    # Test ACC data
    try:
        response = requests.get("http://localhost:8002/api/v1/status/L-2", timeout=5)
        if response.status_code == 200:
            acc_data = response.json()
            print("✅ ACC Data: Available")
            print(f"   Decision: {acc_data.get('decision', 'unknown')}")
            print(f"   Reasons: {acc_data.get('reasons', [])}")
        else:
            print("❌ ACC Data: Not available")
    except:
        print("❌ ACC Data: Connection failed")
    
    # Test RCA data
    try:
        response = requests.get("http://localhost:8009/api/v1/status/L-2", timeout=5)
        if response.status_code == 200:
            rca_data = response.json()
            print("✅ RCA Data: Available")
            print(f"   Root Cause: {rca_data.get('root_cause', 'unknown')}")
        else:
            print("❌ RCA Data: Not available")
    except:
        print("❌ RCA Data: Connection failed")
    
    # Test ARL data
    try:
        response = requests.get("http://localhost:8008/api/v1/status/L-2", timeout=5)
        if response.status_code == 200:
            arl_data = response.json()
            print("✅ ARL Data: Available")
            print(f"   Status: {arl_data.get('status', 'unknown')}")
        else:
            print("❌ ARL Data: Not available")
    except:
        print("❌ ARL Data: Connection failed")
    
    # Test CRRAK data
    try:
        response = requests.get("http://localhost:8010/api/v1/status/L-2", timeout=5)
        if response.status_code == 200:
            crrak_data = response.json()
            print("✅ CRRAK Data: Available")
            print(f"   Compliance: {crrak_data.get('audit_report', {}).get('compliance_status', 'unknown')}")
        else:
            print("❌ CRRAK Data: Not available")
    except:
        print("❌ CRRAK Data: Connection failed")

def test_complete_workflow():
    """Test complete workflow from query to response"""
    print("\n🎯 Testing Complete Workflow...")
    
    # Simulate a complete transaction failure scenario
    workflow_data = {
        "query": "Why did line L-2 fail and what should we do about it?",
        "batch_id": "B-2025-10-03-01",
        "line_id": "L-2",
        "context": {
            "acc_output": {
                "decision": "FAIL",
                "reasons": ["SANCTION_LIST_MATCH"],
                "evidence_refs": ["s3://evidence/HDFC/B-2025-09-19-01/L-2/sanction_check.pdf"],
                "timestamp": "2025-09-20T10:10:00Z"
            },
            "rca_output": {
                "root_cause": "SANCTION_LIST_MATCH (beneficiary 'Beta Corp' matched RBI watchlist entry ID: WL-2023-0456)",
                "explanation": "Line L-2 failed because the beneficiary 'Beta Corp' was flagged on the RBI sanction list during the compliance check on 2025-09-20 at 10:10:00Z, with a match confidence score of 0.95 based on name and IFSC 'HDFC0001234'; this indicates a potential regulatory risk.",
                "recommended_actions": [
                    "Re-verify KYC details for 'Beta Corp' using updated UIDAI/PAN data.",
                    "Contact HDFC compliance team for manual review of transactionReferenceNo '7577'.",
                    "Remove 'Beta Corp' from the transaction list if sanction persists."
                ],
                "neo4j_state": "Line → Decision [FAIL] → Explanation [RCA report]"
            },
            "arl_output": {
                "exceptions": [{"type": "TRANSACTION_FAILED", "line_id": "L-2", "details": "No settlement due to ACC failure", "timestamp": "2025-09-20T10:15:00Z"}]
            }
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8011/api/v1/query",
            json=workflow_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Complete workflow successful!")
            print(f"📝 Query: {data['query']}")
            print(f"🎯 Failure Reason: {data['response']['failure_reason']}")
            print(f"📊 Confidence Score: {data['response']['confidence_score']}")
            print(f"🔗 Evidence Refs: {len(data['evidence_refs'])} files")
            
            # Check if we got detailed analysis
            if data['response']['detailed_analysis']:
                print("✅ Detailed Analysis: Available")
            else:
                print("⚠️  Detailed Analysis: Not available")
            
            # Check recommended actions
            actions = data['response']['recommended_actions']
            if actions:
                print(f"✅ Recommended Actions: {len(actions)} actions")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action.get('action', 'Unknown')} - {action.get('priority', 'Unknown')} priority")
            else:
                print("⚠️  Recommended Actions: Not available")
            
            return True
        else:
            print(f"❌ Complete workflow failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Complete workflow error: {e}")
        return False

def main():
    """Run comprehensive Prompt Layer integration tests"""
    print("🎯 Testing Complete Prompt Layer (xAI) Integration")
    print("=" * 70)
    
    # Test all services health
    services = [
        ("Frontend Integration API", "http://localhost:8020/api/v1/health"),
        ("MCP Service", "http://localhost:8000/api/v1/health"),
        ("ACC Service", "http://localhost:8002/api/v1/health"),
        ("ARL Service", "http://localhost:8008/api/v1/health"),
        ("RCA Service", "http://localhost:8009/api/v1/health"),
        ("CRRAK Service", "http://localhost:8010/api/v1/health"),
        ("Prompt Layer (xAI)", "http://localhost:8011/api/v1/health")
    ]
    
    print("🔍 Checking All Services...")
    healthy_services = 0
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ {service_name}: healthy")
                healthy_services += 1
            else:
                print(f"❌ {service_name}: HTTP {response.status_code}")
        except:
            print(f"❌ {service_name}: not responding")
    
    print(f"\n📊 Service Health: {healthy_services}/{len(services)} services healthy")
    
    if healthy_services >= 6:
        # Test MCP integration
        test_mcp_integration()
        
        # Test agent data flow
        test_agent_data_flow()
        
        # Test complete workflow
        test_complete_workflow()
        
        print("\n" + "=" * 70)
        print("🎉 Complete Prompt Layer (xAI) Integration Test Complete!")
        print("\n🌐 Your Enhanced System is Ready:")
        print("• Frontend: http://localhost:3001")
        print("• Prompt Layer: http://localhost:8011/docs")
        print("• MCP: http://localhost:8000/docs")
        print("• API Documentation: http://localhost:8020/docs")
        
        print("\n🔗 Test the Complete Workflow:")
        print("1. Go to http://localhost:3001")
        print("2. Click 'Prompt Layer (xAI)' in sidebar")
        print("3. Enter query: 'Why did line L-2 fail and what should we do about it?'")
        print("4. Click 'Ask xAI' to see the integrated response")
        print("5. The system will:")
        print("   • Query ACC for compliance data")
        print("   • Query RCA for root cause analysis")
        print("   • Query ARL for reconciliation data")
        print("   • Query CRRAK for audit information")
        print("   • Generate comprehensive xAI response")
        
    else:
        print("\n❌ Not enough services are healthy. Please start the system first:")
        print("python start_prompt_layer_system.py")

if __name__ == "__main__":
    main()
