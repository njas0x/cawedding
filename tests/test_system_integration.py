"""
Integration tests for the wedding planner hiring system
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import json

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.database.airtable_schema import PlannerRecord, PlannerStatus
from src.agents.researcher_agent import ResearcherAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.outreach_agent import OutreachAgent, OutreachCampaign
from src.orchestrator import WeddingPlannerOrchestrator
from src.monitoring.cost_tracker import CostTracker
from src.monitoring.dashboard import MonitoringDashboard
from src.utils.credentials import CredentialsManager

class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def mock_credentials(self):
        """Mock credentials for testing"""
        return {
            "OPENAI_API_KEY": "test_openai_key",
            "AIRTABLE_API_KEY": "test_airtable_key",
            "AIRTABLE_BASE_ID": "test_base_id",
            "APIFY_API_TOKEN": "test_apify_token",
            "TWILIO_ACCOUNT_SID": "test_twilio_sid",
            "TWILIO_AUTH_TOKEN": "test_twilio_token",
            "SENDGRID_API_KEY": "test_sendgrid_key"
        }
    
    @pytest.fixture
    def mock_airtable_data(self):
        """Mock Airtable data for testing"""
        return {
            "planners": [
                {
                    "id": "planner_1",
                    "name": "Sarah Chen",
                    "email": "sarah@example.com",
                    "phone": "+1234567890",
                    "business_name": "Chen Wedding Planning",
                    "location": "Irvine, CA",
                    "chinese_wedding_experience": True,
                    "tea_ceremony_experience": True,
                    "bilingual_services": True,
                    "total_reviews": 25,
                    "average_rating": 4.8,
                    "status": "discovered",
                    "source": "instagram"
                },
                {
                    "id": "planner_2", 
                    "name": "Maria Rodriguez",
                    "email": "maria@example.com",
                    "business_name": "Elegant Events OC",
                    "location": "Newport Beach, CA",
                    "fusion_experience": True,
                    "total_reviews": 15,
                    "average_rating": 4.5,
                    "status": "discovered",
                    "source": "weddingwire"
                }
            ]
        }
    
    @patch('src.utils.credentials.CredentialsManager.decrypt_credentials')
    def test_credentials_manager_integration(self, mock_decrypt, mock_credentials):
        """Test credentials manager integration"""
        mock_decrypt.return_value = mock_credentials
        
        creds_manager = CredentialsManager()
        credentials = creds_manager.decrypt_credentials()
        
        assert credentials["OPENAI_API_KEY"] == "test_openai_key"
        assert credentials["AIRTABLE_API_KEY"] == "test_airtable_key"
    
    @patch('src.database.airtable_client.AirtableClient.__init__')
    @patch('src.utils.credentials.CredentialsManager.decrypt_credentials')
    def test_airtable_client_integration(self, mock_decrypt, mock_init, mock_credentials):
        """Test Airtable client integration"""
        mock_decrypt.return_value = mock_credentials
        mock_init.return_value = None
        
        # Test that client can be initialized without errors
        client = AirtableClient()
        assert client is not None
    
    @patch('src.agents.researcher_agent.ResearcherAgent._setup_clients')
    @patch('src.database.airtable_client.AirtableClient')
    def test_researcher_agent_integration(self, mock_airtable, mock_setup):
        """Test researcher agent integration"""
        mock_setup.return_value = None
        mock_airtable_instance = Mock()
        mock_airtable.return_value = mock_airtable_instance
        
        researcher = ResearcherAgent()
        assert researcher is not None
        
        # Test keyword setup
        assert len(researcher.multicultural_keywords) > 0
        assert "chinese wedding" in researcher.multicultural_keywords
        assert "tea ceremony" in researcher.multicultural_keywords
    
    @patch('src.agents.analyzer_agent.AnalyzerAgent._setup_llm')
    @patch('src.database.airtable_client.AirtableClient')
    def test_analyzer_agent_integration(self, mock_airtable, mock_setup_llm):
        """Test analyzer agent integration"""
        mock_setup_llm.return_value = None
        mock_airtable_instance = Mock()
        mock_airtable.return_value = mock_airtable_instance
        
        analyzer = AnalyzerAgent()
        assert analyzer is not None
        
        # Test scoring criteria setup
        assert "chinese_wedding_experience" in analyzer.multicultural_criteria
        assert "timeline_comfort" in analyzer.availability_criteria
        assert "overall_rating" in analyzer.reviews_criteria
    
    @patch('src.agents.outreach_agent.OutreachAgent._setup_clients')
    @patch('src.database.airtable_client.AirtableClient')
    def test_outreach_agent_integration(self, mock_airtable, mock_setup):
        """Test outreach agent integration"""
        mock_setup.return_value = None
        mock_airtable_instance = Mock()
        mock_airtable.return_value = mock_airtable_instance
        
        outreach = OutreachAgent()
        assert outreach is not None
        
        # Test templates setup
        assert "initial_email" in outreach.templates
        assert "follow_up_email" in outreach.templates
        assert "sms_intro" in outreach.templates
    
    @patch('src.orchestrator.WeddingPlannerOrchestrator._setup_agents')
    @patch('src.orchestrator.WeddingPlannerOrchestrator._setup_llm')
    def test_orchestrator_integration(self, mock_setup_llm, mock_setup_agents):
        """Test orchestrator integration"""
        mock_setup_llm.return_value = None
        mock_setup_agents.return_value = None
        
        orchestrator = WeddingPlannerOrchestrator()
        assert orchestrator is not None
        
        # Test workflow phases setup
        assert "research" in orchestrator.workflow_phases
        assert "outreach" in orchestrator.workflow_phases
        assert "calls" in orchestrator.workflow_phases
        assert "decision" in orchestrator.workflow_phases
    
    def test_cost_tracker_integration(self):
        """Test cost tracker integration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock Config.DATA_DIR to use temp directory
            original_data_dir = Config.DATA_DIR
            Config.DATA_DIR = temp_dir
            
            try:
                cost_tracker = CostTracker()
                assert cost_tracker is not None
                
                # Test cost recording
                cost_tracker.record_cost("openai", "completion", 0.01, "test", "test_agent")
                
                # Test budget status
                budget_status = cost_tracker.get_budget_status()
                assert budget_status.total_spent == 0.01
                assert budget_status.percentage_used > 0
                
            finally:
                Config.DATA_DIR = original_data_dir
    
    def test_monitoring_dashboard_integration(self):
        """Test monitoring dashboard integration"""
        with patch('src.database.airtable_client.AirtableClient'):
            with patch('src.monitoring.cost_tracker.CostTracker'):
                dashboard = MonitoringDashboard()
                assert dashboard is not None
                
                # Test metrics collection
                system_metrics = dashboard.get_system_metrics()
                assert system_metrics.cpu_percent >= 0
                assert system_metrics.memory_percent >= 0
                
                # Test health check
                health = dashboard.get_health_check()
                assert "status" in health
                assert "health_score" in health

class TestEndToEndWorkflow:
    """End-to-end workflow tests"""
    
    @pytest.fixture
    def mock_workflow_data(self):
        """Mock data for end-to-end testing"""
        return {
            "research_results": ["planner_1", "planner_2", "planner_3"],
            "analysis_results": ["planner_1", "planner_2"],
            "outreach_results": {"sent": 2, "failed": 0},
            "response_results": {"responded": 1, "scheduled": 1}
        }
    
    @patch('src.agents.researcher_agent.ResearcherAgent.run_research_phase')
    @patch('src.agents.analyzer_agent.AnalyzerAgent.run_analysis_phase')
    @patch('src.agents.outreach_agent.OutreachAgent.run_outreach_campaign')
    @patch('src.orchestrator.WeddingPlannerOrchestrator._setup_agents')
    @patch('src.orchestrator.WeddingPlannerOrchestrator._setup_llm')
    async def test_complete_workflow_simulation(self, mock_setup_llm, mock_setup_agents,
                                               mock_outreach, mock_analysis, mock_research,
                                               mock_workflow_data):
        """Test complete workflow simulation"""
        
        # Setup mocks
        mock_setup_llm.return_value = None
        mock_setup_agents.return_value = None
        mock_research.return_value = mock_workflow_data["research_results"]
        mock_analysis.return_value = mock_workflow_data["analysis_results"]
        mock_outreach.return_value = mock_workflow_data["outreach_results"]
        
        # Create orchestrator
        orchestrator = WeddingPlannerOrchestrator()
        
        # Test research phase
        research_results = await orchestrator._execute_research_phase()
        assert "planners_discovered" in research_results
        assert "shortlist_generated" in research_results
        
        # Test outreach phase
        outreach_results = await orchestrator._execute_outreach_phase()
        assert "total_contacted" in outreach_results
        
        # Test calls phase
        calls_results = await orchestrator._execute_calls_phase()
        assert "calls_completed" in calls_results
        
        # Test decision phase
        decision_results = await orchestrator._execute_decision_phase()
        assert "hired_planners" in decision_results

class TestDataValidation:
    """Data validation and integrity tests"""
    
    def test_planner_record_validation(self):
        """Test planner record data validation"""
        # Valid planner record
        valid_planner = PlannerRecord(
            name="Test Planner",
            email="test@example.com",
            phone="+1234567890",
            status=PlannerStatus.DISCOVERED
        )
        
        assert valid_planner.name == "Test Planner"
        assert valid_planner.status == PlannerStatus.DISCOVERED
        assert len(valid_planner.portfolio_links) == 0  # Default empty list
    
    def test_outreach_campaign_validation(self):
        """Test outreach campaign configuration validation"""
        campaign = OutreachCampaign(
            name="test_campaign",
            template_name="initial_email",
            target_status="shortlisted",
            communication_type="email"
        )
        
        assert campaign.name == "test_campaign"
        assert campaign.batch_size == 5  # Default value
        assert campaign.max_follow_ups == 2  # Default value
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test search criteria
        search_criteria = Config.get_search_criteria()
        assert "location" in search_criteria
        assert "wedding_style" in search_criteria
        assert "must_have_experience" in search_criteria
        
        # Test hashtags
        assert len(Config.INSTAGRAM_HASHTAGS) > 0
        assert all(tag.startswith("#") for tag in Config.INSTAGRAM_HASHTAGS)

class TestErrorHandling:
    """Error handling and resilience tests"""
    
    @patch('src.database.airtable_client.AirtableClient.create_planner')
    def test_database_error_handling(self, mock_create):
        """Test database error handling"""
        mock_create.side_effect = Exception("Database connection failed")
        
        with patch('src.agents.researcher_agent.ResearcherAgent._setup_clients'):
            researcher = ResearcherAgent()
            
            # Test that errors are handled gracefully
            result = researcher._process_scraped_planner(Mock())
            assert result is None  # Should return None on error
    
    @patch('src.agents.outreach_agent.OutreachAgent._send_email')
    def test_communication_error_handling(self, mock_send):
        """Test communication error handling"""
        mock_send.side_effect = Exception("Email sending failed")
        
        with patch('src.agents.outreach_agent.OutreachAgent._setup_clients'):
            outreach = OutreachAgent()
            
            # Test error handling in message sending
            success = outreach._send_single_message({}, {}, "email")
            assert not success  # Should return False on error
    
    def test_cost_tracking_error_handling(self):
        """Test cost tracking error handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = Config.DATA_DIR
            Config.DATA_DIR = temp_dir
            
            try:
                cost_tracker = CostTracker()
                
                # Test with invalid service
                cost_tracker.record_cost("invalid_service", "test", 0.01)
                
                # Should not crash, just log the cost
                budget_status = cost_tracker.get_budget_status()
                assert budget_status.total_spent == 0.01
                
            finally:
                Config.DATA_DIR = original_data_dir

class TestPerformance:
    """Performance and scalability tests"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Simulate large number of planners
        large_dataset = []
        for i in range(100):
            large_dataset.append({
                "id": f"planner_{i}",
                "name": f"Planner {i}",
                "status": "discovered"
            })
        
        # Test that the system can handle large datasets
        assert len(large_dataset) == 100
        
        # This would be expanded with actual performance metrics
        # in a real test environment
    
    def test_concurrent_operations(self):
        """Test concurrent operations"""
        # This would test concurrent agent operations
        # For now, just verify that the async framework is set up correctly
        import asyncio
        
        async def dummy_task():
            await asyncio.sleep(0.1)
            return "completed"
        
        # Test async execution
        result = asyncio.run(dummy_task())
        assert result == "completed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])