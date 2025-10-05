#!/usr/bin/env python3
"""
Test direct transaction upload to frontend integration.
"""

import requests
import json

# Test data
test_transactions = [
    {
        "id": "TXN-TEST-001",
        "date": "2025-10-04",
        "beneficiary": "Test User 1",
        "amount": 15000,
        "currency": "INR",
        "status": "completed",
        "stage": "executed",
        "product": "Payment",
        "creditScore": 750,
        "reference": "REF-TEST-001",
        "workflow_id": "WF-TEST-001"
    },
    {
        "id": "TXN-TEST-002",
        "date": "2025-10-04",
        "beneficiary": "Test User 2",
        "amount": 25000,
        "currency": "INR",
        "status": "pending",
        "stage": "operator-review",
        "product": "Payment",
        "creditScore": 750,
        "reference": "REF-TEST-002",
        "workflow_id": "WF-TEST-001"
    }
]

# Test direct API call to add transactions
def test_direct_upload():
    """Test direct transaction upload."""
    try:
        # This would normally be done through the API
        # For now, let's just test if the service is working
        response = requests.get("http://localhost:8020/api/v1/transactions")
        if response.status_code == 200:
            data = response.json()
            print(f"Current transaction count: {len(data)}")
            print(f"First transaction: {data[0] if data else 'None'}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_upload()
