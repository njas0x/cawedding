#!/usr/bin/env python3
"""
Database integration test script
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.database.airtable_client import AirtableClient
from src.database.airtable_schema import PlannerRecord, PlannerStatus, CommunicationRecord, CommunicationStatus
from datetime import datetime

def test_full_database_workflow():
    """Test complete database workflow"""
    print("🧪 Testing Database Integration Workflow")
    print("=" * 50)
    
    try:
        # Initialize client
        client = AirtableClient()
        print("✅ Database client initialized")
        
        # Test 1: Create planner
        test_planner = PlannerRecord(
            name="TEST_Sarah_Chen_DELETE",
            email="test.sarah@example.com",
            phone="+19491234567",
            business_name="TEST Chen Wedding Planning",
            location="Irvine, CA",
            chinese_wedding_experience=True,
            tea_ceremony_experience=True,
            bilingual_services=True,
            total_reviews=25,
            average_rating=4.8,
            multicultural_score=8.5,
            availability_score=7.2,
            reviews_score=9.1,
            total_score=8.3,
            status=PlannerStatus.DISCOVERED,
            source="test"
        )
        
        planner_id = client.create_planner(test_planner)
        print(f"✅ Test planner created: {planner_id}")
        
        # Test 2: Update planner
        client.update_planner(planner_id, {
            "status": "analyzed",
            "notes": "Test planner - excellent multicultural experience"
        })
        print("✅ Planner update successful")
        
        # Test 3: Create communication
        test_comm = CommunicationRecord(
            planner_id=planner_id,
            communication_type="email",
            subject="Wedding Planner Inquiry - Test",
            message_content="This is a test email for the wedding planner hiring system.",
            status=CommunicationStatus.SENT,
            sent_date=datetime.now(),
            template_used="test_template",
            cost=0.01
        )
        
        comm_id = client.create_communication(test_comm)
        print(f"✅ Test communication created: {comm_id}")
        
        # Test 4: Get system stats
        stats = client.get_system_stats()
        print(f"✅ System stats retrieved: {stats['total_planners']} total planners")
        
        # Test 5: Query functions
        discovered = client.get_planners_by_status("discovered")
        print(f"✅ Query by status works: {len(discovered)} discovered planners")
        
        # Test 6: Get specific planner
        planner_data = client.get_planner(planner_id)
        print(f"✅ Get planner works: {planner_data['name']}")
        
        # Cleanup
        client.planners_table.delete(planner_id)
        client.communications_table.delete(comm_id)
        print("✅ Test data cleaned up")
        
        print("\n🎉 ALL DATABASE TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        print("Please check your Airtable configuration and API keys")
        return False

if __name__ == "__main__":
    success = test_full_database_workflow()
    sys.exit(0 if success else 1)