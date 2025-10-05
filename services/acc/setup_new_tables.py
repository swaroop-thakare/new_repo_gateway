#!/usr/bin/env python3

"""
Script to create and populate the new tables: redis_table, pdr_table, and arl_table
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from database import create_tables, populate_all_tables

def main():
    print("🚀 Setting up new tables...")
    
    # Create all tables
    print("📋 Creating tables...")
    create_tables()
    
    # Populate all tables with data
    print("📊 Populating tables with data...")
    success = populate_all_tables()
    
    if success:
        print("✅ All tables created and populated successfully!")
        print("\n📋 Tables created:")
        print("  - redis_table (5 records)")
        print("  - pdr_table (5 records)")
        print("  - arl_table (5 records)")
    else:
        print("❌ Failed to populate some tables")
        return False
    
    return True

if __name__ == "__main__":
    main()
