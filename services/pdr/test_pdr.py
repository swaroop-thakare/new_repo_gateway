"""
PDR System Test Suite
Tests the complete PDR pipeline with sample data.
"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal

from models import *
from database import db_manager
from main import pdr_service

# Test data
test_intents = [
    Intent(
        transaction_id="TEST001",
        payment_type=PaymentType.PAYROLL,
        sender=Party(
            name="Arealis Corp",
            account_number="1234567890",
            ifsc_code="UTIB0000123",
            bank_name="Axis Bank"
        ),
        receiver=Party(
            name="John Doe",
            account_number="9876543210", 
            ifsc_code="HDFC0001234",
            bank_name="HDFC Bank"
        ),
        amount=Decimal("50000.00"),
        purpose="Salary payment for December 2024",
        schedule_datetime=datetime.now() + timedelta(hours=1),
        location=Location(
            city="Mumbai",
            gps_coordinates=GPSCoordinates(latitude=19.0760, longitude=72.8777)
        ),
        additional_fields=AdditionalFields(
            employee_id="EMP001",
            department="Engineering"
        )
    ),
    Intent(
        transaction_id="TEST002",
        payment_type=PaymentType.VENDOR_PAYMENT,
        sender=Party(
            name="Arealis Corp",
            account_number="1234567890",
            ifsc_code="UTIB0000123", 
            bank_name="Axis Bank"
        ),
        receiver=Party(
            name="Tech Supplies Ltd",
            account_number="5555666677",
            ifsc_code="ICIC0001111",
            bank_name="ICICI Bank"
        ),
        amount=Decimal("250000.00"),
        purpose="Payment for software licenses",
        schedule_datetime=datetime.now() + timedelta(hours=2),
        additional_fields=AdditionalFields(
            invoice_number="INV-2024-001",
            gst_number="29ABCDE1234A1Z5"
        )
    ),
    Intent(
        transaction_id="TEST003",
        payment_type=PaymentType.LOAN_DISBURSEMENT,
        sender=Party(
            name="Arealis Bank",
            account_number="9999888877",
            ifsc_code="UTIB0000456",
            bank_name="Axis Bank"
        ),
        receiver=Party(
            name="Small Business Owner", 
            account_number="1111222233",
            ifsc_code="SBIN0001234",
            bank_name="State Bank of India"
        ),
        amount=Decimal("500000.00"),
        purpose="Business loan disbursement",
        schedule_datetime=datetime.now() + timedelta(hours=3),
        additional_fields=AdditionalFields(
            loan_account_number="LOAN123456",
            loan_type="business_loan"
        )
    )
]

async def test_complete_pipeline():
    """Test the complete PDR pipeline"""
    print("🚀 Starting PDR Pipeline Test")
    
    # 1. Test database setup
    print("\n1. Setting up database...")
    try:
        db_manager.execute_schema_file("/workspace/services/pdr/database_schema.sql")
        print("✅ Database schema setup completed")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return
    
    # 2. Test PDR decision generation
    print("\n2. Testing PDR decision generation...")
    request = PDRRequest(intents=test_intents)
    
    try:
        response = await pdr_service.process_intents(request)
        print(f"✅ Generated {response.total_successful} PDR decisions")
        print(f"   Processing time: {response.processing_time_ms:.2f}ms")
        
        for decision in response.decisions:
            print(f"   {decision.transaction_id}: {decision.primary_rail} (score: {decision.primary_rail_score:.3f})")
            
    except Exception as e:
        print(f"❌ PDR decision generation failed: {e}")
        return
    
    # 3. Test rail execution
    print("\n3. Testing rail execution...")
    for decision in response.decisions:
        if decision.execution_status == ExecutionStatus.PENDING:
            try:
                result = await pdr_service.execute_rail_decision(decision.transaction_id)
                if result.success:
                    print(f"✅ {decision.transaction_id}: {result.rail_name} succeeded - UTR: {result.utr_number}")
                else:
                    print(f"❌ {decision.transaction_id}: {result.rail_name} failed - {result.error_message}")
            except Exception as e:
                print(f"❌ {decision.transaction_id}: Execution failed - {e}")
    
    # 4. Test performance stats
    print("\n4. Testing performance statistics...")
    rails = ["UPI", "IMPS", "NEFT", "RTGS", "IFT"]
    for rail in rails:
        stats = db_manager.get_rail_performance_stats(rail)
        if stats['total_transactions'] > 0:
            print(f"   {rail}: {stats['total_transactions']} txns, {stats['success_rate']:.1%} success")
    
    print("\n🎉 PDR Pipeline Test Completed!")

def test_scoring_engine():
    """Test the scoring engine with sample data"""
    print("\n🧮 Testing Scoring Engine")
    
    from scoring_engine import RailScoringEngine
    
    # Get sample data
    intent = test_intents[0]  # 50K payroll payment
    rails = db_manager.get_active_rails()
    
    # Mock ACC decision
    acc_decision = ACCDecision(
        transaction_id=intent.transaction_id,
        line_id=intent.transaction_id,
        decision=DecisionStatus.PASS,
        policy_version="test",
        compliance_penalty=5.0,
        risk_score=10.0
    )
    
    # Run scoring
    engine = RailScoringEngine()
    scored_rails, filter_reasons = engine.select_rails(intent, rails, acc_decision)
    
    print(f"Eligible rails: {len(scored_rails)}")
    print(f"Filtered out: {len(filter_reasons)} reasons")
    
    if scored_rails:
        print("\nRail Rankings:")
        for i, rail in enumerate(scored_rails[:5]):  # Top 5
            print(f"  {i+1}. {rail.rail_name}: {rail.score:.3f}")
        
        # Explainability
        explainability = engine.get_explainability_report(scored_rails)
        print(f"\nTop factors for {explainability['primary_rail']}:")
        for factor, contribution in explainability['top_contributing_factors']:
            print(f"  - {factor}: {contribution:.3f}")
    
    if filter_reasons:
        print(f"\nFiltered reasons: {filter_reasons[:3]}")  # First 3

def test_mock_apis():
    """Test mock rail APIs"""
    print("\n🔌 Testing Mock Rail APIs")
    
    from mock_rail_apis import MockRailAPIs
    
    apis = MockRailAPIs()
    intent = test_intents[0]
    
    rails_to_test = ["UPI", "IMPS", "NEFT", "RTGS", "IFT"]
    
    for rail in rails_to_test:
        request = RailExecutionRequest(
            transaction_id=f"MOCK_{rail}",
            rail_name=rail,
            intent=intent,
            retry_attempt=0
        )
        
        result = apis.execute_rail(request)
        status = "✅" if result.success else "❌"
        print(f"  {status} {rail}: {result.execution_time_ms}ms - {result.utr_number or result.error_message}")
    
    # Show statistics
    stats = apis.get_statistics()
    print(f"\nAPI Statistics: {stats['total_calls']} total calls")

if __name__ == "__main__":
    print("🧪 PDR System Test Suite")
    print("=" * 50)
    
    # Test individual components
    test_scoring_engine()
    test_mock_apis()
    
    # Test complete pipeline
    asyncio.run(test_complete_pipeline())