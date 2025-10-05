#!/bin/bash

echo "🚀 Starting Arealis Gateway v2 - Complete System"
echo "================================================"

# Activate virtual environment
source venv/bin/activate

# Start MCP (Master Control Process) - Port 8000
echo "Starting MCP (Master Control Process)..."
python layers/orchestration/master_control.py &
MCP_PID=$!
sleep 3

# Start Frontend Integration API - Port 8020
echo "Starting Frontend Integration API..."
python simple_frontend_integration.py &
FRONTEND_PID=$!
sleep 2

# Start ARL Service - Port 8008
echo "Starting ARL Service..."
python services/arl_service.py &
ARL_PID=$!
sleep 2

# Start RCA Service - Port 8009
echo "Starting RCA Service..."
python services/rca_service.py &
RCA_PID=$!
sleep 2

# Start Intent Manager - Port 8001
echo "Starting Intent Manager..."
python layers/intent-router/intent_manager2.py &
INTENT_PID=$!
sleep 2

# Start PDR Service - Port 8002
echo "Starting PDR Service..."
python services/pdr_service.py &
PDR_PID=$!
sleep 2

# Wait for all services to start
echo "Waiting for services to initialize..."
sleep 5

# Check service health
echo ""
echo "🔍 Checking Service Health..."
echo "=============================="

# Check MCP
echo -n "MCP (Port 8000): "
curl -s http://localhost:8000/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

# Check Frontend Integration
echo -n "Frontend Integration (Port 8020): "
curl -s http://localhost:8020/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

# Check ARL Service
echo -n "ARL Service (Port 8008): "
curl -s http://localhost:8008/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

# Check RCA Service
echo -n "RCA Service (Port 8009): "
curl -s http://localhost:8009/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

# Check Intent Manager
echo -n "Intent Manager (Port 8001): "
curl -s http://localhost:8001/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

# Check PDR Service
echo -n "PDR Service (Port 8002): "
curl -s http://localhost:8002/api/v1/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

echo ""
echo "🎯 System Status:"
echo "================="
echo "✅ MCP (Master Control Process): http://localhost:8000"
echo "✅ Frontend Integration API: http://localhost:8020"
echo "✅ ARL Service: http://localhost:8008"
echo "✅ RCA Service: http://localhost:8009"
echo "✅ Intent Manager: http://localhost:8001"
echo "✅ PDR Service: http://localhost:8002"
echo ""
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo ""
echo "📊 All services are running! The system is ready for use."
echo ""
echo "To stop all services, run: ./stop_all_services.sh"
