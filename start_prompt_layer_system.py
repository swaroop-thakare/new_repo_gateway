#!/usr/bin/env python3
"""
Start all services including the new Prompt Layer (xAI) service
"""

import subprocess
import time
import requests
import json
from pathlib import Path

def start_service(name, command, port, max_retries=3):
    """Start a service and wait for it to be healthy"""
    print(f"🚀 Starting {name}...")
    
    for attempt in range(max_retries):
        try:
            # Start the service
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for service to start
            time.sleep(3)
            
            # Check if service is healthy
            try:
                response = requests.get(f"http://localhost:{port}/api/v1/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} is healthy on port {port}")
                    return process
            except requests.exceptions.RequestException:
                pass
            
            # If not healthy, kill and retry
            process.terminate()
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Failed to start {name} (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    print(f"❌ Failed to start {name} after {max_retries} attempts")
    return None

def main():
    """Start all services"""
    print("🎯 Starting Arealis Gateway v2 with Prompt Layer (xAI)")
    print("=" * 60)
    
    services = [
        {
            "name": "Frontend Integration API",
            "command": "source venv/bin/activate && python simple_frontend_integration.py",
            "port": 8020
        },
        {
            "name": "ACC Service",
            "command": "source venv/bin/activate && python services/acc_service.py",
            "port": 8002
        },
        {
            "name": "ARL Service", 
            "command": "source venv/bin/activate && python services/arl_service.py",
            "port": 8008
        },
        {
            "name": "RCA Service",
            "command": "source venv/bin/activate && python services/rca_service.py", 
            "port": 8009
        },
        {
            "name": "CRRAK Service",
            "command": "source venv/bin/activate && python services/crrak_service.py",
            "port": 8010
        },
        {
            "name": "Prompt Layer (xAI) Service",
            "command": "source venv/bin/activate && python services/prompt_layer_service.py",
            "port": 8011
        }
    ]
    
    processes = []
    
    # Start all services
    for service in services:
        process = start_service(service["name"], service["command"], service["port"])
        if process:
            processes.append((service["name"], process))
        else:
            print(f"⚠️  {service['name']} failed to start, continuing with other services...")
    
    print("\n" + "=" * 60)
    print("🎉 System Status:")
    
    # Check all services
    for service in services:
        try:
            response = requests.get(f"http://localhost:{service['port']}/api/v1/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ {service['name']}: http://localhost:{service['port']}")
            else:
                print(f"❌ {service['name']}: Not responding")
        except:
            print(f"❌ {service['name']}: Not responding")
    
    print("\n🌐 Frontend: http://localhost:3001")
    print("📚 API Documentation: http://localhost:8020/docs")
    print("🤖 Prompt Layer: http://localhost:8011/docs")
    
    print("\n" + "=" * 60)
    print("🎯 Prompt Layer (xAI) Integration:")
    print("• ACC Service: http://localhost:8002")
    print("• ARL Service: http://localhost:8008") 
    print("• RCA Service: http://localhost:8009")
    print("• CRRAK Service: http://localhost:8010")
    print("• Prompt Layer: http://localhost:8011")
    
    print("\n🔗 Test the integration:")
    print("1. Navigate to http://localhost:3001")
    print("2. Click 'Prompt Layer (xAI)' in the sidebar")
    print("3. Try query: 'Why did line L-2 fail and what should we do about it?'")
    
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"✅ Stopped {name}")
            except:
                print(f"❌ Failed to stop {name}")
        print("👋 All services stopped")

if __name__ == "__main__":
    main()
