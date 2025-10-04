#!/usr/bin/env python3
"""
Simple Neo4j connection test with detailed error reporting
"""

from neo4j import GraphDatabase
import time

# Neo4j credentials
NEO4J_URI = "neo4j+s://6933b562.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Yavi0NJTNDApnMb-InD3pCVwdgT7Hzd2-6vb-tYshZo"
NEO4J_DATABASE = "neo4j"

def test_basic_connection():
    """Test basic Neo4j connection"""
    print("🔗 Testing basic Neo4j connection...")
    print(f"URI: {NEO4J_URI}")
    print(f"User: {NEO4J_USER}")
    print(f"Database: {NEO4J_DATABASE}")
    print("=" * 50)
    
    try:
        # Create driver with minimal configuration
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        
        print("✅ Driver created successfully")
        
        # Test basic connectivity
        print("🔄 Testing connectivity...")
        driver.verify_connectivity()
        print("✅ Connectivity verified")
        
        # Test simple query
        print("🔄 Testing simple query...")
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Simple query successful: {record['test']}")
        
        # Test with database parameter
        print("🔄 Testing with database parameter...")
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("RETURN 'Hello from Neo4j Aura!' as message")
            record = result.single()
            print(f"✅ Database query successful: {record['message']}")
        
        # Test node creation
        print("🔄 Testing node creation...")
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                CREATE (t:TestNode {
                    name: 'Connection Test',
                    timestamp: datetime(),
                    test_id: 'simple_test_001'
                })
                RETURN t.name as name, t.test_id as test_id
            """)
            record = result.single()
            if record:
                print(f"✅ Node created: {record['name']} (ID: {record['test_id']})")
            else:
                print("❌ Node creation failed - no result")
        
        # Clean up
        print("🔄 Cleaning up test node...")
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("MATCH (t:TestNode {test_id: 'simple_test_001'}) DELETE t RETURN count(t) as deleted")
            record = result.single()
            print(f"✅ Cleanup completed: {record['deleted']} nodes deleted")
        
        driver.close()
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Additional debugging
        if "routing" in str(e).lower():
            print("💡 This appears to be a routing issue. Possible causes:")
            print("   - Network connectivity problems")
            print("   - Firewall blocking the connection")
            print("   - Neo4j Aura instance not ready")
            print("   - Incorrect URI format")
        elif "auth" in str(e).lower():
            print("💡 This appears to be an authentication issue. Check:")
            print("   - Username and password are correct")
            print("   - Database name is correct")
        elif "timeout" in str(e).lower():
            print("💡 This appears to be a timeout issue. Try:")
            print("   - Waiting a bit longer for the connection")
            print("   - Checking network stability")
        
        return False

def test_with_retry():
    """Test connection with retry logic"""
    print("\n🔄 Testing with retry logic...")
    
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries}")
        
        try:
            driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
                max_connection_lifetime=30 * 60,
                connection_acquisition_timeout=60
            )
            
            driver.verify_connectivity()
            print("✅ Connection successful with retry!")
            driver.close()
            return True
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("⏳ Waiting 5 seconds before retry...")
                time.sleep(5)
            else:
                print("❌ All retry attempts failed")
                return False

def main():
    """Run Neo4j connection tests"""
    print("🚀 Simple Neo4j Connection Test")
    print("=" * 50)
    
    # Test basic connection
    basic_ok = test_basic_connection()
    
    if not basic_ok:
        # Try with retry logic
        retry_ok = test_with_retry()
        
        if retry_ok:
            print("\n✅ Connection successful with retry!")
        else:
            print("\n❌ All connection attempts failed")
            print("\n💡 Troubleshooting suggestions:")
            print("1. Check if Neo4j Aura instance is running")
            print("2. Verify network connectivity")
            print("3. Try connecting from Neo4j Browser")
            print("4. Check firewall settings")
    else:
        print("\n🎉 Neo4j connection working perfectly!")

if __name__ == "__main__":
    main()
