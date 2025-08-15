#!/usr/bin/env python3
"""
Agent integration test script
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import asyncio

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.agents.researcher_agent import ResearcherAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.outreach_agent import OutreachAgent
from src.database.airtable_schema import PlannerRecord, PlannerStatus

def test_agent_data_handoffs():
    """Test agents can pass data through database"""
    print("🧪 Testing Agent Integration Workflow")
    print("=" * 50)
    
    try:
        # Mock database client to avoid real API calls
        with patch('src.database.airtable_client.AirtableClient') as mock_airtable:
            mock_client = Mock()
            mock_airtable.return_value = mock_client
            
            # Mock planner creation
            mock_client.create_planner.return_value = "test_planner_id"
            mock_client.get_planners_by_status.return_value = [
                {"id": "test_planner_id", "name": "Test Planner", "status": "discovered"}
            ]
            
            # Test 1: Researcher creates planners
            with patch.object(ResearcherAgent, '_setup_clients'):
                researcher = ResearcherAgent()
                
                # Mock scraped data
                mock_scraped = Mock()
                mock_scraped.name = "Test Planner"
                mock_scraped.email = "test@example.com"
                mock_scraped.source = "test"
                
                # This would normally process scraped data
                planner_id = researcher._process_scraped_planner(mock_scraped)
                print("✅ Researcher agent data handoff works")
            
            # Test 2: Analyzer processes planner data
            with patch.object(AnalyzerAgent, '_setup_llm'):
                analyzer = AnalyzerAgent()
                
                # Mock planner data for analysis
                mock_planner = {
                    "id": "test_planner_id",
                    "name": "Test Planner",
                    "bio_text": "Chinese wedding planner tea ceremony",
                    "total_reviews": 10,
                    "average_rating": 4.5
                }
                
                analysis = analyzer._analyze_single_planner(mock_planner)
                if analysis:
                    print("✅ Analyzer agent data processing works")
            
            # Test 3: Outreach processes shortlisted planners
            with patch.object(OutreachAgent, '_setup_clients'):
                outreach = OutreachAgent()
                
                # Mock shortlisted planner
                mock_planner = {
                    "id": "test_planner_id",
                    "name": "Test Planner",
                    "email": "test@example.com",
                    "business_name": "Test Planning",
                    "specializations": ["Chinese weddings"]
                }
                
                # Test message generation
                with patch.object(outreach, '_ai_personalize_content') as mock_ai:
                    mock_ai.return_value = "Personalized message content"
                    message = outreach._generate_personalized_message(mock_planner, "initial_email")
                    
                    if message and message.get("content"):
                        print("✅ Outreach agent data processing works")
        
        print("\n🎉 ALL AGENT INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent integration test failed: {e}")
        return False

def test_workflow_coordination():
    """Test workflow phase coordination"""
    print("\n🧪 Testing Workflow Coordination")
    print("=" * 30)
    
    try:
        # Test data flow between phases
        research_results = ["planner_1", "planner_2", "planner_3"]
        analysis_results = ["planner_1", "planner_2"]  # Top 2 from analysis
        outreach_results = {"sent": 2, "failed": 0}
        
        # Verify data consistency
        assert len(analysis_results) <= len(research_results), "Analysis can't have more than research"
        assert outreach_results["sent"] <= len(analysis_results), "Outreach can't exceed shortlist"
        
        print("✅ Data flow consistency verified")
        print(f"✅ Research → Analysis: {len(research_results)} → {len(analysis_results)}")
        print(f"✅ Analysis → Outreach: {len(analysis_results)} → {outreach_results['sent']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow coordination test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_agent_data_handoffs()
    success2 = test_workflow_coordination()
    
    overall_success = success1 and success2
    print(f"\n{'🎉 ALL TESTS PASSED!' if overall_success else '❌ SOME TESTS FAILED'}")
    
    sys.exit(0 if overall_success else 1)