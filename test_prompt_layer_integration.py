#!/usr/bin/env python3
"""
Test Prompt Layer (xAI) integration with all agents
"""

import requests
import json
import time
from datetime import datetime

def test_service_health(service_name, url):
    """Test if a service is healthy"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {service_name}: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ {service_name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: {e}")
        return False

def test_prompt_layer_query():
    """Test Prompt Layer query processing"""
    print("\n🧪 Testing Prompt Layer Query Processing...")
    
    query_data = {
        "query": "Why did line L-2 fail and what should we do about it?",
        "batch_id": "B-2025-10-03-01",
        "line_id": "L-2"
    }
    
    try:
        response = requests.post(
            "http://localhost:8011/api/v1/query",
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Prompt Layer query successful!")
            print(f"📝 Query: {data['query']}")
            print(f"🎯 Failure Reason: {data['response']['failure_reason']}")
            print(f"📊 Confidence Score: {data['response']['confidence_score']}")
            print(f"🔗 Evidence Refs: {len(data['evidence_refs'])} files")
            print(f"⏰ Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Prompt Layer query failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Prompt Layer query error: {e}")
        return False

def test_agent_integration():
    """Test integration with all agents"""
    print("\n🔗 Testing Agent Integration...")
    
    try:
        response = requests.get("http://localhost:8011/api/v1/agents/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent integration status retrieved!")
            
            agents = data.get('agents', {})
            for agent, status in agents.items():
                if status == "healthy":
                    print(f"✅ {agent}: {status}")
                else:
                    print(f"⚠️  {agent}: {status}")
            
            return True
        else:
            print(f"❌ Agent integration check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent integration error: {e}")
        return False

def test_frontend_integration():
    """Test frontend API integration"""
    print("\n🌐 Testing Frontend Integration...")
    
    try:
        response = requests.post(
            "http://localhost:3001/api/prompt/query",
            json={
                "query": "Why did line L-2 fail?",
                "batch_id": "B-2025-001",
                "line_id": "L-2"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Frontend API integration successful!")
            print(f"📝 Query: {data['query']}")
            print(f"🎯 Response ID: {data['id']}")
            print(f"⏰ Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Frontend API integration failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend API integration error: {e}")
        return False

def main():
    """Run comprehensive Prompt Layer integration tests"""
    print("🎯 Testing Prompt Layer (xAI) Integration")
    print("=" * 60)
    
    # Test all services
    services = [
        ("Frontend Integration API", "http://localhost:8020/api/v1/health"),
        ("ACC Service", "http://localhost:8002/api/v1/health"),
        ("ARL Service", "http://localhost:8008/api/v1/health"),
        ("RCA Service", "http://localhost:8009/api/v1/health"),
        ("CRRAK Service", "http://localhost:8010/api/v1/health"),
        ("Prompt Layer (xAI)", "http://localhost:8011/api/v1/health")
    ]
    
    print("🔍 Checking Service Health...")
    healthy_services = 0
    
    for service_name, url in services:
        if test_service_health(service_name, url):
            healthy_services += 1
    
    print(f"\n📊 Service Health: {healthy_services}/{len(services)} services healthy")
    
    # Test Prompt Layer functionality
    if healthy_services >= 4:  # At least core services should be running
        print("\n🧪 Testing Prompt Layer Functionality...")
        
        # Test agent integration
        test_agent_integration()
        
        # Test query processing
        test_prompt_layer_query()
        
        # Test frontend integration
        test_frontend_integration()
        
        print("\n" + "=" * 60)
        print("🎉 Prompt Layer (xAI) Integration Test Complete!")
        print("\n🌐 Access your system:")
        print("• Frontend: http://localhost:3001")
        print("• Prompt Layer: http://localhost:8011/docs")
        print("• API Documentation: http://localhost:8020/docs")
        
        print("\n🔗 Test the complete workflow:")
        print("1. Go to http://localhost:3001")
        print("2. Click 'Prompt Layer (xAI)' in sidebar")
        print("3. Enter query: 'Why did line L-2 fail and what should we do about it?'")
        print("4. Click 'Ask xAI' to see the integrated response")
        
    else:
        print("\n❌ Not enough services are healthy. Please start the system first:")
        print("python start_prompt_layer_system.py")

if __name__ == "__main__":
    main()
