#!/usr/bin/env python3
"""
Test script to demonstrate fetching payment files from PostgreSQL
"""

import requests
import json
from database import get_db, get_payment_files, get_payment_files_count, get_latest_payment_files

def test_database_functions():
    """Test database functions directly"""
    print("=== Testing Database Functions ===")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test getting payment files count
        count = get_payment_files_count(db)
        print(f"Total payment files in database: {count}")
        
        # Test getting latest payment files
        latest_files = get_latest_payment_files(db, limit=5)
        print(f"\nLatest 5 payment files:")
        for file in latest_files:
            print(f"  ID: {file.id}, Filename: {file.filename}")
        
        # Test getting all payment files with pagination
        all_files = get_payment_files(db, limit=10, offset=0)
        print(f"\nFirst 10 payment files:")
        for file in all_files:
            print(f"  ID: {file.id}, Filename: {file.filename}")
            
    except Exception as e:
        print(f"Error testing database functions: {e}")
    finally:
        db.close()

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test getting payment files count
        print("1. Testing payment files count...")
        response = requests.get(f"{base_url}/acc/payment-files/count")
        if response.status_code == 200:
            data = response.json()
            print(f"   Count: {data.get('total_count', 'N/A')}")
        else:
            print(f"   Error: {response.status_code}")
        
        # Test getting latest payment files
        print("\n2. Testing latest payment files...")
        response = requests.get(f"{base_url}/acc/payment-files/latest?limit=3")
        if response.status_code == 200:
            data = response.json()
            files = data.get('payment_files', [])
            print(f"   Latest 3 files:")
            for file in files:
                print(f"     ID: {file.get('id')}, Filename: {file.get('filename')}")
        else:
            print(f"   Error: {response.status_code}")
        
        # Test getting payment files with pagination
        print("\n3. Testing payment files with pagination...")
        response = requests.get(f"{base_url}/acc/payment-files?limit=5&offset=0")
        if response.status_code == 200:
            data = response.json()
            files = data.get('payment_files', [])
            pagination = data.get('pagination', {})
            print(f"   Files: {len(files)}")
            print(f"   Total: {pagination.get('total', 'N/A')}")
            print(f"   Has more: {pagination.get('has_more', 'N/A')}")
        else:
            print(f"   Error: {response.status_code}")
        
        # Test getting specific payment file by ID
        print("\n4. Testing specific payment file by ID...")
        response = requests.get(f"{base_url}/acc/payment-files/1")
        if response.status_code == 200:
            data = response.json()
            file = data.get('payment_file', {})
            print(f"   File ID: {file.get('id')}")
            print(f"   Filename: {file.get('filename')}")
        else:
            print(f"   Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   Error: Could not connect to API server. Make sure the ACC service is running on port 8000")
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Main test function"""
    print("Payment Files Fetch Test")
    print("=" * 50)
    
    # Test database functions
    test_database_functions()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
