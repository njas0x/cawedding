"""
Unit tests for individual agents
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.agents.researcher_agent import ResearcherAgent, ScrapedPlannerData
from src.agents.analyzer_agent import AnalyzerAgent, PlannerAnalysis
from src.agents.outreach_agent import OutreachAgent, OutreachCampaign, MessageTemplate
from src.database.airtable_schema import PlannerRecord, PlannerStatus

class TestResearcherAgent:
    """Test ResearcherAgent functionality"""
    
    @pytest.fixture
    def mock_researcher(self):
        """Create researcher agent with mocked dependencies"""
        with patch('src.agents.researcher_agent.ResearcherAgent._setup_clients'):
            return ResearcherAgent()
    
    def test_keyword_setup(self, mock_researcher):
        """Test keyword and pattern setup"""
        assert len(mock_researcher.multicultural_keywords) > 0
        assert "chinese wedding" in mock_researcher.multicultural_keywords
        assert "tea ceremony" in mock_researcher.multicultural_keywords
        assert "orange county" in mock_researcher.location_keywords
    
    def test_email_extraction(self, mock_researcher):
        """Test email extraction from text"""
        text = "Contact us at planner@example.com for inquiries"
        email = mock_researcher._extract_email(text)
        assert email == "planner@example.com"
        
        # Test no email
        text_no_email = "No email here"
        email = mock_researcher._extract_email(text_no_email)
        assert email is None
    
    def test_phone_extraction(self, mock_researcher):
        """Test phone number extraction"""
        text = "Call us at (949) 123-4567"
        phone = mock_researcher._extract_phone(text)
        assert "949" in phone
        assert "123" in phone
        assert "4567" in phone
    
    def test_website_extraction(self, mock_researcher):
        """Test website URL extraction"""
        text = "Visit our website at https://example.com"
        website = mock_researcher._extract_website(text)
        assert website == "https://example.com"
    
    def test_instagram_post_processing(self, mock_researcher):
        """Test Instagram post data processing"""
        mock_post = {
            "ownerUsername": "test_planner",
            "caption": "Chinese wedding planner in Orange County. Specializing in tea ceremony and bilingual services.",
            "ownerFollowersCount": 1500
        }
        
        result = mock_researcher._process_instagram_post(mock_post, "#OCWeddingPlanner")
        
        assert result is not None
        assert result.name == "Test Planner"
        assert result.instagram_handle == "test_planner"
        assert "tea ceremony" in result.keywords_matched
        assert result.follower_count == 1500
    
    def test_weddingwire_card_processing(self, mock_researcher):
        """Test WeddingWire card processing"""
        # Mock BeautifulSoup elements
        mock_card = Mock()
        
        # Mock name element
        mock_name_elem = Mock()
        mock_name_elem.text.strip.return_value = "Elegant Events"
        mock_card.find.return_value = mock_name_elem
        
        # Mock link element
        mock_link_elem = Mock()
        mock_link_elem.get.return_value = "/vendor/elegant-events"
        
        # Mock location element
        mock_location_elem = Mock()
        mock_location_elem.text.strip.return_value = "Irvine, CA"
        
        # Mock description element
        mock_desc_elem = Mock()
        mock_desc_elem.text.strip.return_value = "Specializing in Asian weddings and multicultural celebrations"
        
        # Setup side effects for different find calls
        def find_side_effect(tag, class_=None):
            if tag == 'h3' or tag == 'h2':
                return mock_name_elem
            elif tag == 'a':
                return mock_link_elem
            elif class_ == 'location':
                return mock_location_elem
            elif class_ == 'description':
                return mock_desc_elem
            return None
        
        mock_card.find.side_effect = find_side_effect
        
        result = mock_researcher._process_weddingwire_card(mock_card)
        
        assert result is not None
        assert result.name == "Elegant Events"
        assert result.source == "weddingwire"
        assert "asian" in result.keywords_matched

class TestAnalyzerAgent:
    """Test AnalyzerAgent functionality"""
    
    @pytest.fixture
    def mock_analyzer(self):
        """Create analyzer agent with mocked dependencies"""
        with patch('src.agents.analyzer_agent.AnalyzerAgent._setup_llm'):
            return AnalyzerAgent()
    
    def test_scoring_criteria_setup(self, mock_analyzer):
        """Test scoring criteria initialization"""
        assert "chinese_wedding_experience" in mock_analyzer.multicultural_criteria
        assert "timeline_comfort" in mock_analyzer.availability_criteria
        assert "overall_rating" in mock_analyzer.reviews_criteria
        
        # Test weights sum to expected values
        multicultural_weights = sum(
            criteria["weight"] for criteria in mock_analyzer.multicultural_criteria.values()
        )
        assert abs(multicultural_weights - 1.0) < 0.01  # Should sum to ~1.0
    
    def test_multicultural_scoring(self, mock_analyzer):
        """Test multicultural fit scoring"""
        # Text with high multicultural relevance
        text_high = "Experienced chinese wedding planner specializing in tea ceremony and cantonese traditions in orange county"
        score_high, factors_high = mock_analyzer._score_multicultural_fit(text_high)
        
        # Text with low multicultural relevance
        text_low = "General wedding planner"
        score_low, factors_low = mock_analyzer._score_multicultural_fit(text_low)
        
        assert score_high > score_low
        assert score_high > 5.0  # Should score well
        assert score_low < 3.0   # Should score poorly
    
    def test_availability_scoring(self, mock_analyzer):
        """Test availability scoring"""
        # Text indicating good availability
        text_available = "Available for rush timeline weddings, can accommodate 3 month planning, flexible schedule"
        score_available, factors_available = mock_analyzer._score_availability(text_available)
        
        # Text indicating poor availability
        text_unavailable = "Fully booked, 6 month minimum timeline, not available january"
        score_unavailable, factors_unavailable = mock_analyzer._score_availability(text_unavailable)
        
        assert score_available > score_unavailable
    
    def test_reviews_scoring(self, mock_analyzer):
        """Test reviews scoring"""
        # Planner with good reviews
        planner_good_reviews = {
            "average_rating": 4.8,
            "total_reviews": 25,
            "review_summary": "Excellent cultural wedding experience, great communication, organized timeline"
        }
        
        score_good, factors_good = mock_analyzer._score_reviews(planner_good_reviews)
        
        # Planner with poor reviews
        planner_poor_reviews = {
            "average_rating": 2.5,
            "total_reviews": 3,
            "review_summary": "Poor communication, disorganized"
        }
        
        score_poor, factors_poor = mock_analyzer._score_reviews(planner_poor_reviews)
        
        assert score_good > score_poor
        assert score_good > 7.0  # Should score well
    
    def test_red_flag_identification(self, mock_analyzer):
        """Test red flag identification"""
        text_with_flags = "No asian experience, modern only weddings, fully booked, overpriced packages"
        red_flags = mock_analyzer._identify_red_flags(text_with_flags)
        
        assert len(red_flags) > 0
        assert any("no asian experience" in flag for flag in red_flags)
    
    def test_green_flag_identification(self, mock_analyzer):
        """Test green flag identification"""
        text_with_flags = "Authentic chinese weddings, tea ceremony expert, bilingual mc available, capital seafood experience"
        green_flags = mock_analyzer._identify_green_flags(text_with_flags)
        
        assert len(green_flags) > 0
        assert any("authentic chinese weddings" in flag for flag in green_flags)
    
    def test_confidence_calculation(self, mock_analyzer):
        """Test confidence level calculation"""
        # High confidence factors
        multicultural_factors = {
            "chinese_wedding_experience": {"matches": ["chinese wedding", "tea ceremony", "cantonese"]},
            "fusion_capability": {"matches": ["fusion", "modern twist"]}
        }
        
        availability_factors = {
            "timeline_comfort": {"positive_matches": ["rush timeline", "3 month"], "negative_matches": []}
        }
        
        reviews_factors = {
            "overall_rating": {"review_count": 25}
        }
        
        confidence = mock_analyzer._calculate_confidence(
            multicultural_factors, availability_factors, reviews_factors
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident

class TestOutreachAgent:
    """Test OutreachAgent functionality"""
    
    @pytest.fixture
    def mock_outreach(self):
        """Create outreach agent with mocked dependencies"""
        with patch('src.agents.outreach_agent.OutreachAgent._setup_clients'):
            return OutreachAgent()
    
    def test_templates_setup(self, mock_outreach):
        """Test message templates setup"""
        assert "initial_email" in mock_outreach.templates
        assert "follow_up_email" in mock_outreach.templates
        assert "sms_intro" in mock_outreach.templates
        
        # Test template structure
        initial_template = mock_outreach.templates["initial_email"]
        assert initial_template.subject is not None
        assert "[name]" in initial_template.content
        assert "personalization_fields" in initial_template.__dict__
    
    def test_personalization_data_extraction(self, mock_outreach):
        """Test personalization data extraction"""
        planner = {
            "name": "Sarah Chen",
            "business_name": "Chen Wedding Planning",
            "location": "Irvine, CA",
            "specializations": ["Chinese weddings", "Tea ceremony"],
            "chinese_wedding_experience": True,
            "bilingual_services": True,
            "source": "instagram",
            "instagram_handle": "sarahchenplanning"
        }
        
        data = mock_outreach._extract_personalization_data(planner)
        
        assert data["name"] == "Sarah"
        assert data["full_name"] == "Sarah Chen"
        assert data["business_name"] == "Chen Wedding Planning"
        assert "Chinese weddings" in data["specializations"]
        assert "Chinese wedding experience" in data["experience_highlights"]
        assert "instagram" in data["source_mention"]
    
    def test_message_generation(self, mock_outreach):
        """Test personalized message generation"""
        planner = {
            "id": "planner_1",
            "name": "Sarah Chen",
            "business_name": "Chen Wedding Planning",
            "location": "Irvine, CA",
            "specializations": ["Chinese weddings"],
            "chinese_wedding_experience": True,
            "source": "instagram"
        }
        
        with patch.object(mock_outreach, '_ai_personalize_content') as mock_ai:
            mock_ai.return_value = "Personalized email content"
            
            message = mock_outreach._generate_personalized_message(planner, "initial_email")
            
            assert message["subject"] is not None
            assert message["content"] == "Personalized email content" + mock_outreach.compliance_footer
            assert message["template_used"] == "initial_email"
    
    def test_outreach_campaign_configuration(self, mock_outreach):
        """Test outreach campaign configuration"""
        campaign = OutreachCampaign(
            name="test_campaign",
            template_name="initial_email",
            target_status="shortlisted",
            communication_type="email",
            batch_size=3,
            follow_up_delay_hours=24
        )
        
        assert campaign.name == "test_campaign"
        assert campaign.batch_size == 3
        assert campaign.follow_up_delay_hours == 24
        assert campaign.communication_type == "email"
    
    def test_batch_message_generation(self, mock_outreach):
        """Test batch message generation"""
        planners = [
            {"id": "p1", "name": "Planner 1", "source": "instagram"},
            {"id": "p2", "name": "Planner 2", "source": "weddingwire"}
        ]
        
        campaign = OutreachCampaign(
            name="test",
            template_name="initial_email",
            target_status="shortlisted",
            communication_type="email"
        )
        
        with patch.object(mock_outreach, '_generate_personalized_message') as mock_generate:
            mock_generate.return_value = {"subject": "Test", "content": "Test content"}
            
            messages = mock_outreach._generate_batch_messages(planners, campaign)
            
            assert len(messages) == 2
            assert all("planner" in msg for msg in messages)
            assert all("message" in msg for msg in messages)

class TestDataProcessing:
    """Test data processing and transformation"""
    
    def test_scraped_planner_data_creation(self):
        """Test ScrapedPlannerData creation and defaults"""
        data = ScrapedPlannerData(
            name="Test Planner",
            source="instagram",
            profile_url="https://instagram.com/test"
        )
        
        assert data.name == "Test Planner"
        assert data.source == "instagram"
        assert len(data.hashtags_found) == 0  # Default empty list
        assert len(data.keywords_matched) == 0  # Default empty list
        assert len(data.portfolio_links) == 0  # Default empty list
    
    def test_planner_analysis_creation(self):
        """Test PlannerAnalysis creation and calculations"""
        analysis = PlannerAnalysis(
            planner_id="test_id",
            name="Test Planner",
            multicultural_score=8.5,
            availability_score=7.0,
            reviews_score=9.0,
            total_score=8.2,
            multicultural_factors={},
            availability_factors={},
            reviews_factors={}
        )
        
        assert analysis.planner_id == "test_id"
        assert analysis.multicultural_score == 8.5
        assert analysis.total_score == 8.2
        assert len(analysis.red_flags) == 0  # Default empty list
        assert len(analysis.green_flags) == 0  # Default empty list
    
    def test_message_template_creation(self):
        """Test MessageTemplate creation"""
        template = MessageTemplate(
            name="test_template",
            subject="Test Subject",
            content="Dear [name], this is a test message about [topic].",
            personalization_fields=["name", "topic"],
            communication_type="email"
        )
        
        assert template.name == "test_template"
        assert template.subject == "Test Subject"
        assert len(template.personalization_fields) == 2
        assert "name" in template.personalization_fields

if __name__ == "__main__":
    pytest.main([__file__, "-v"])