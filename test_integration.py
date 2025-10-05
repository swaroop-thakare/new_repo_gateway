"""
Test Frontend-Backend Integration

This script tests the integration between the Next.js frontend
and Python backend services.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

def test_backend_services():
    """Test backend services."""
    print("🧪 Testing Backend Services...")
    
    services = [
        ("MCP", "http://localhost:8000/api/v1/health"),
        ("Frontend Integration", "http://localhost:8020/api/v1/health"),
        ("FrontendIngestor", "http://localhost:8001/api/v1/health"),
        ("InvoiceValidator", "http://localhost:8002/api/v1/health"),
        ("IntentClassifier", "http://localhost:8003/api/v1/health"),
        ("PDR", "http://localhost:8006/api/v1/health"),
        ("ARL", "http://localhost:8008/api/v1/health"),
        ("RCA", "http://localhost:8009/api/v1/health"),
        ("CRRAK", "http://localhost:8010/api/v1/health"),
        ("ACC", "http://localhost:8011/api/v1/health")
    ]
    
    healthy_services = 0
    total_services = len(services)
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: HEALTHY")
                healthy_services += 1
            else:
                print(f"❌ {service_name}: UNHEALTHY ({response.status_code})")
        except Exception as e:
            print(f"❌ {service_name}: OFFLINE ({str(e)})")
    
    print(f"\n📊 Backend Health: {healthy_services}/{total_services} services healthy")
    return healthy_services >= total_services * 0.7

def test_frontend_integration():
    """Test frontend integration API."""
    print("\n🧪 Testing Frontend Integration API...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8020/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend Integration API: HEALTHY")
        else:
            print(f"❌ Frontend Integration API: UNHEALTHY ({response.status_code})")
            return False
        
        # Test dashboard metrics
        response = requests.get("http://localhost:8020/api/v1/dashboard/metrics", timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            print(f"✅ Dashboard Metrics: {metrics}")
        else:
            print(f"❌ Dashboard Metrics: FAILED ({response.status_code})")
            return False
        
        # Test transactions endpoint
        response = requests.get("http://localhost:8020/api/v1/transactions", timeout=10)
        if response.status_code == 200:
            transactions = response.json()
            print(f"✅ Transactions: {len(transactions)} transactions loaded")
        else:
            print(f"❌ Transactions: FAILED ({response.status_code})")
            return False
        
        # Test agent status
        response = requests.get("http://localhost:8020/api/v1/agents", timeout=10)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Agent Status: {len(agents)} agents loaded")
        else:
            print(f"❌ Agent Status: FAILED ({response.status_code})")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend Integration API: ERROR ({str(e)})")
        return False

def test_batch_upload():
    """Test batch upload functionality."""
    print("\n🧪 Testing Batch Upload...")
    
    try:
        # Create test batch data
        batch_data = {
            "batch_id": f"B-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "tenant_id": "TEST",
            "source": "TEST_UPLOAD",
            "upload_ts": datetime.now().isoformat() + "Z",
            "transactions": [
                {
                    "transactionId": "TXN-TEST-001",
                    "date": "2025-10-04",
                    "beneficiary": "Test User",
                    "amount": 100000,
                    "currency": "INR",
                    "purpose": "VENDOR_PAYMENT",
                    "transactionType": "NEFT",
                    "creditScore": 750,
                    "reference": "TEST-REF-001"
                }
            ]
        }
        
        # Upload batch
        response = requests.post(
            "http://localhost:8020/api/v1/batches/upload",
            json=batch_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch Upload: SUCCESS - {result}")
            
            # Test workflow status
            workflow_id = result.get("workflow_id")
            if workflow_id:
                time.sleep(2)  # Wait for processing
                
                status_response = requests.get(
                    f"http://localhost:8020/api/v1/workflows/{workflow_id}/status",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"✅ Workflow Status: {status}")
                    return True
                else:
                    print(f"❌ Workflow Status: FAILED ({status_response.status_code})")
                    return False
            else:
                print("❌ No workflow ID returned")
                return False
        else:
            print(f"❌ Batch Upload: FAILED ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Batch Upload: ERROR ({str(e)})")
        return False

def test_frontend_connectivity():
    """Test frontend connectivity."""
    print("\n🧪 Testing Frontend Connectivity...")
    
    try:
        # Test if Next.js is running
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Next.js Frontend: RUNNING")
            return True
        else:
            print(f"❌ Next.js Frontend: NOT RUNNING ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Next.js Frontend: OFFLINE ({str(e)})")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Arealis Gateway v2 - Integration Test")
    print("=" * 60)
    
    tests = [
        ("Backend Services", test_backend_services),
        ("Frontend Integration API", test_frontend_integration),
        ("Batch Upload", test_batch_upload),
        ("Frontend Connectivity", test_frontend_connectivity)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASS")
            else:
                print(f"❌ {test_name}: FAIL")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    print(f"\n📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All integration tests passed! System is fully integrated.")
        print("💡 Access the system at:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8020")
        print("   MCP: http://localhost:8000")
        return True
    else:
        print(f"\n⚠️ {total - passed} integration tests failed.")
        print("💡 Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
