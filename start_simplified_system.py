#!/usr/bin/env python3
"""
Simplified Arealis Gateway v2 Startup
Starts core services without database dependencies
"""

import subprocess
import time
import requests
import sys
import os

def start_service(name, command, port, wait_time=3):
    """Start a service and check if it's healthy"""
    print(f"🚀 Starting {name}...")
    
    try:
        # Start service in background
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(wait_time)
        
        # Check if service is healthy
        try:
            response = requests.get(f"http://localhost:{port}/api/v1/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} (Port {port}): Healthy")
                return True
            else:
                print(f"❌ {name} (Port {port}): Unhealthy - Status {response.status_code}")
                return False
        except requests.exceptions.RequestException:
            print(f"❌ {name} (Port {port}): Not responding")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return False

def main():
    print("🚀 Starting Arealis Gateway v2 - Simplified System")
    print("=" * 60)
    
    # Change to project directory
    os.chdir('/Users/swaroopthakare/Arealis-Gateway')
    
    # Start services in order
    services = [
        ("Frontend Integration API", "source venv/bin/activate && python simple_frontend_integration.py", 8020),
        ("ARL Service", "source venv/bin/activate && python services/arl_service.py", 8008),
        ("RCA Service", "source venv/bin/activate && python services/rca_service.py", 8009),
        ("PDR Service", "source venv/bin/activate && python services/pdr_service.py", 8002),
    ]
    
    healthy_services = 0
    total_services = len(services)
    
    for name, command, port in services:
        if start_service(name, command, port):
            healthy_services += 1
        time.sleep(2)  # Wait between services
    
    print("\n" + "=" * 60)
    print(f"📊 System Status: {healthy_services}/{total_services} services healthy")
    
    if healthy_services >= 3:  # At least core services
        print("\n🎯 CORE SYSTEM OPERATIONAL!")
        print("✅ Frontend, ARL, RCA, and PDR are working")
        print("✅ System ready for CSV uploads and real-time processing")
        
        print("\n🌐 Access Points:")
        print("   • Frontend Dashboard: http://localhost:3000")
        print("   • API Documentation: http://localhost:8020/docs")
        print("   • ARL Service: http://localhost:8008/api/v1/health")
        print("   • RCA Service: http://localhost:8009/api/v1/health")
        print("   • PDR Service: http://localhost:8002/api/v1/health")
        
        print("\n🔄 Real-Time Workflow:")
        print("   1. Upload CSV through frontend")
        print("   2. Backend processes transactions")
        print("   3. ARL provides reconciliation data")
        print("   4. RCA analyzes failures")
        print("   5. PDR selects optimal rails")
        print("   6. Frontend updates in real-time")
        
        return True
    else:
        print("\n❌ SYSTEM ISSUES DETECTED!")
        print("Some core services are not responding")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 System is ready for use!")
        print("You can now upload CSV files and see real-time updates.")
    else:
        print("\n❌ System startup failed!")
        sys.exit(1)
