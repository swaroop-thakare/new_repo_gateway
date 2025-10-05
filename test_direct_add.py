#!/usr/bin/env python3
"""
Test direct transaction addition to frontend integration.
"""

import requests
import json

def test_direct_add():
    """Test adding transactions directly."""
    try:
        # First, check current transaction count
        response = requests.get("http://localhost:8020/api/v1/transactions")
        if response.status_code == 200:
            data = response.json()
            print(f"Current transaction count: {len(data)}")
        else:
            print(f"Error getting transactions: {response.status_code}")
            return
        
        # Try to add transactions using a simple POST request
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
        
        response = requests.post(
            "http://localhost:8020/api/v1/transactions/add",
            json=test_transactions,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"Successfully added transactions: {response.json()}")
        else:
            print(f"Error adding transactions: {response.status_code} - {response.text}")
            
        # Check transaction count again
        response = requests.get("http://localhost:8020/api/v1/transactions")
        if response.status_code == 200:
            data = response.json()
            print(f"New transaction count: {len(data)}")
            if len(data) > 4:
                print(f"New transactions added: {len(data) - 4}")
                print(f"Latest transaction: {data[-1]}")
            else:
                print("No new transactions added")
        else:
            print(f"Error getting transactions: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_add()
