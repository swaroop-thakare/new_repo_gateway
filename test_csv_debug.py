#!/usr/bin/env python3
"""
Debug CSV upload to see what's happening.
"""

import requests
import json

def test_csv_upload():
    """Test CSV upload and check results."""
    try:
        # First, check current transaction count
        response = requests.get("http://localhost:8020/api/v1/transactions")
        if response.status_code == 200:
            data = response.json()
            print(f"Current transaction count: {len(data)}")
        else:
            print(f"Error getting transactions: {response.status_code}")
            return
        
        # Test CSV upload
        with open("test_upload.csv", "rb") as f:
            files = {"file": f}
            data = {"tenant_id": "TEST"}
            response = requests.post("http://localhost:8020/api/v1/batches/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Upload successful: {result}")
            else:
                print(f"Upload failed: {response.status_code} - {response.text}")
                return
        
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
    test_csv_upload()
