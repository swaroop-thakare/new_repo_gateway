#!/usr/bin/env python3
"""
Test Neo4j connection with the provided credentials
"""

from database import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE, save_to_neo4j
from neo4j import GraphDatabase
import json

def test_neo4j_connection():
    """Test Neo4j connection with provided credentials"""
    try:
        print("🔗 Testing Neo4j connection...")
        print(f"URI: {NEO4J_URI}")
        print(f"User: {NEO4J_USER}")
        print(f"Database: {NEO4J_DATABASE}")
        print("=" * 50)
        
        # Test direct connection
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Test basic connection
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"✅ Connection successful: {record['message']}")
            
            # Test creating a test node
            session.run("""
                CREATE (t:TestNode {
                    name: 'Connection Test',
                    timestamp: datetime(),
                    status: 'active'
                })
            """)
            print("✅ Test node created successfully")
            
            # Test querying the test node
            result = session.run("MATCH (t:TestNode) RETURN t.name as name, t.timestamp as timestamp")
            record = result.single()
            if record:
                print(f"✅ Test node found: {record['name']} at {record['timestamp']}")
            
            # Clean up test node
            session.run("MATCH (t:TestNode) DELETE t")
            print("✅ Test node cleaned up")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def test_save_function():
    """Test the save_to_neo4j function"""
    try:
        print("\n💾 Testing save_to_neo4j function...")
        
        success = save_to_neo4j(
            line_id="TEST_CONNECTION_001",
            beneficiary="Test Beneficiary",
            ifsc="TEST0001234",
            amount=1000.00,
            status="PASS",
            decision_reason=json.dumps(["Connection test successful"]),
            evidence_ref=json.dumps(["test"])
        )
        
        if success:
            print("✅ save_to_neo4j function works correctly")
        else:
            print("❌ save_to_neo4j function failed")
            
        return success
        
    except Exception as e:
        print(f"❌ save_to_neo4j test failed: {e}")
        return False

def main():
    """Run Neo4j connection tests"""
    print("🚀 Neo4j Connection Test")
    print("=" * 50)
    
    # Test direct connection
    connection_ok = test_neo4j_connection()
    print()
    
    # Test save function
    save_ok = test_save_function()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Neo4j Test Summary:")
    print(f"Direct Connection: {'✅ Success' if connection_ok else '❌ Failed'}")
    print(f"Save Function: {'✅ Success' if save_ok else '❌ Failed'}")
    
    if connection_ok and save_ok:
        print("🎉 Neo4j integration working perfectly!")
    else:
        print("⚠️  Neo4j integration has issues. Check credentials and network.")

if __name__ == "__main__":
    main()
