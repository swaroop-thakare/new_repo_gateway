#!/usr/bin/env python3
"""
Debug Prompt Layer to see what's happening with context data
"""

import requests
import json

def debug_prompt_layer():
    """Debug the Prompt Layer with detailed logging"""
    print("🔍 Debugging Prompt Layer...")
    
    # Test with minimal context
    query_data = {
        "query": "Why did line L-2 fail?",
        "batch_id": "B-2025-10-03-01",
        "line_id": "L-2",
        "context": {
            "acc_output": {
                "decision": "FAIL",
                "reasons": ["SANCTION_LIST_MATCH"],
                "timestamp": "2025-09-20T10:10:00Z"
            }
        }
    }
    
    print("📤 Sending request with context:")
    print(json.dumps(query_data, indent=2))
    
    try:
        response = requests.post(
            "http://localhost:8011/api/v1/query",
            json=query_data,
            timeout=10
        )
        
        print(f"\n📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received:")
            print(json.dumps(data, indent=2))
            
            # Check if context was processed
            if data['response']['failure_reason'] != "No ACC data available for analysis":
                print("✅ Context data was processed!")
            else:
                print("❌ Context data was NOT processed")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    debug_prompt_layer()
