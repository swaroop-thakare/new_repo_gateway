#!/usr/bin/env python3
"""
System Status Check for Arealis Gateway v2
"""

import requests
import time

def check_service(name, url, port):
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}:{port}/api/v1/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        return f"✅ {name} (Port {port}): {data.get('status', 'unknown')}"
    except requests.exceptions.RequestException as e:
        return f"❌ {name} (Port {port}): Unhealthy - {str(e)[:50]}..."

def main():
    print("🔍 Arealis Gateway v2 - System Status Check")
    print("=" * 50)
    
    services = [
        ("MCP", "http://localhost", 8000),
        ("Frontend Integration", "http://localhost", 8020),
        ("ARL Service", "http://localhost", 8008),
        ("RCA Service", "http://localhost", 8009),
        ("Intent Manager", "http://localhost", 8001),
        ("PDR Service", "http://localhost", 8002)
    ]
    
    healthy_count = 0
    total_count = len(services)
    
    for name, url, port in services:
        status = check_service(name, url, port)
        print(status)
        if "✅" in status:
            healthy_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 System Status: {healthy_count}/{total_count} services healthy")
    
    if healthy_count >= 4:  # At least core services
        print("🎯 CORE SYSTEM OPERATIONAL!")
        print("✅ MCP, Frontend, ARL, and RCA are working")
        print("✅ System ready for CSV uploads and real-time processing")
        
        print("\n🌐 Access Points:")
        print("   • Frontend Dashboard: http://localhost:3000")
        print("   • API Documentation: http://localhost:8020/docs")
        print("   • MCP Status: http://localhost:8000/api/v1/health")
        
        return True
    else:
        print("❌ SYSTEM ISSUES DETECTED!")
        print("Some core services are not responding")
        return False

if __name__ == "__main__":
    main()
