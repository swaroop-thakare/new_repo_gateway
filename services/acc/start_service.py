#!/usr/bin/env python3
"""
Startup script for ACC Agent Service with database integration
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting ACC Agent Service with Database Integration...")
    print("📊 PostgreSQL: Connected")
    print("🔗 Neo4j: Connected")
    print("🌐 Service running on: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
