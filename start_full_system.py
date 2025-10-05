"""
Start Full Arealis Gateway v2 System

This script starts both the Python backend services and the Next.js frontend
for a complete integrated system.
"""

import subprocess
import time
import signal
import sys
import os
import threading
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FullSystemManager:
    """Manages the complete Arealis Gateway v2 system."""
    
    def __init__(self):
        """Initialize system manager."""
        self.processes = []
        self.running = False
        
    def start_python_services(self):
        """Start Python backend services."""
        logger.info("🚀 Starting Python backend services...")
        
        # Start MCP (Master Control Process)
        mcp_process = subprocess.Popen(
            ["python", "layers/orchestration/master_control.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.processes.append(("MCP", mcp_process))
        logger.info("✅ MCP started on port 8000")
        
        # Start Frontend Integration API
        integration_process = subprocess.Popen(
            ["python", "frontend_integration.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.processes.append(("Frontend Integration", integration_process))
        logger.info("✅ Frontend Integration API started on port 8020")
        
        # Start core services
        services = [
            ("FrontendIngestor", "layers/ingest/frontend_ingestor.py", 8001),
            ("InvoiceValidator", "layers/ingest/invoice_validator.py", 8002),
            ("IntentClassifier", "layers/intent-router/intent_manager_frontend.py", 8003),
            ("PDR", "services/pdr/pdr_agent.py", 8006),
            ("ARL", "services/arl_service.py", 8008),
            ("RCA", "services/rca_service.py", 8009),
            ("CRRAK", "services/crrak_service.py", 8010),
            ("ACC", "services/acc/acc_agent.py", 8011)
        ]
        
        for service_name, script_path, port in services:
            try:
                process = subprocess.Popen(
                    ["python", script_path],
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes.append((service_name, process))
                logger.info(f"✅ {service_name} started on port {port}")
                time.sleep(1)  # Small delay between services
            except Exception as e:
                logger.warning(f"⚠️ Failed to start {service_name}: {str(e)}")
    
    def start_nextjs_frontend(self):
        """Start Next.js frontend."""
        logger.info("🚀 Starting Next.js frontend...")
        
        frontend_dir = "arealisgatewaylanding1 (2)"
        
        if not os.path.exists(frontend_dir):
            logger.error(f"❌ Frontend directory not found: {frontend_dir}")
            return
        
        try:
            # Change to frontend directory and start Next.js
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("Next.js Frontend", frontend_process))
            logger.info("✅ Next.js frontend started on port 3000")
        except Exception as e:
            logger.error(f"❌ Failed to start Next.js frontend: {str(e)}")
    
    def check_service_health(self):
        """Check health of all services."""
        import requests
        
        services_to_check = [
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
        total_services = len(services_to_check)
        
        logger.info("🏥 Checking service health...")
        
        for service_name, url in services_to_check:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name}: HEALTHY")
                    healthy_services += 1
                else:
                    logger.warning(f"⚠️ {service_name}: UNHEALTHY ({response.status_code})")
            except Exception as e:
                logger.warning(f"❌ {service_name}: OFFLINE ({str(e)})")
        
        logger.info(f"📊 Health Summary: {healthy_services}/{total_services} services healthy")
        return healthy_services >= total_services * 0.7  # At least 70% healthy
    
    def start_system(self):
        """Start the complete system."""
        try:
            logger.info("🚀 Starting Arealis Gateway v2 Full System")
            logger.info("=" * 60)
            
            # Start Python services
            self.start_python_services()
            
            # Wait for Python services to start
            logger.info("⏳ Waiting for Python services to initialize...")
            time.sleep(10)
            
            # Check Python services health
            if self.check_service_health():
                logger.info("✅ Python backend services are healthy")
            else:
                logger.warning("⚠️ Some Python services may not be healthy")
            
            # Start Next.js frontend
            self.start_nextjs_frontend()
            
            # Wait for frontend to start
            logger.info("⏳ Waiting for Next.js frontend to initialize...")
            time.sleep(5)
            
            self.running = True
            
            logger.info("🎉 Arealis Gateway v2 Full System Started!")
            logger.info("=" * 60)
            logger.info("📱 Frontend: http://localhost:3000")
            logger.info("🔧 Backend API: http://localhost:8020")
            logger.info("🧠 MCP: http://localhost:8000")
            logger.info("=" * 60)
            logger.info("Press Ctrl+C to stop all services")
            
            # Keep running until interrupted
            while self.running:
                time.sleep(10)
                # Optional: Check service health periodically
                # self.check_service_health()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Received interrupt signal, stopping all services...")
            self.stop_system()
        except Exception as e:
            logger.error(f"❌ System startup failed: {str(e)}")
            self.stop_system()
    
    def stop_system(self):
        """Stop all services."""
        logger.info("🛑 Stopping all services...")
        
        for service_name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {service_name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️ {service_name} killed")
            except Exception as e:
                logger.error(f"❌ Failed to stop {service_name}: {str(e)}")
        
        self.processes.clear()
        self.running = False
        logger.info("✅ All services stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("\n🛑 Received interrupt signal, stopping all services...")
    system_manager.stop_system()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create system manager
    system_manager = FullSystemManager()
    
    try:
        # Start the complete system
        system_manager.start_system()
    except Exception as e:
        logger.error(f"❌ System startup failed: {str(e)}")
        system_manager.stop_system()
        sys.exit(1)
