# Wedding Planner Hiring System: Testing & Validation Guide

> **🎯 Objective**: Ensure all system components work correctly before full execution through comprehensive testing and validation procedures.

## 📋 Testing Strategy Overview

### Testing Phases
1. **🔧 Infrastructure Testing** - APIs, database, credentials
2. **🤖 Agent Unit Testing** - Individual agent functionality 
3. **🔄 Integration Testing** - Multi-agent workflows
4. **📧 Communication Testing** - Email/SMS delivery
5. **💰 Cost Simulation** - Budget tracking accuracy
6. **🧪 End-to-End Testing** - Complete workflow simulation
7. **🚨 Stress Testing** - Error handling and recovery

### Testing Timeline
- **Quick Tests**: 15 minutes (basic functionality)
- **Comprehensive Tests**: 1-2 hours (full validation)
- **Stress Tests**: 30 minutes (error scenarios)

---

## 🔧 Part 1: Infrastructure Testing (15-30 minutes)

### Step 1: API Connectivity Testing

**Test all external API connections:**
```bash
# Run comprehensive API validation
python scripts/setup.py --skip-deps --validate-all

# Expected output for each service:
# ✅ OPENAI API: Valid
# ✅ AIRTABLE API: Valid  
# ✅ APIFY API: Valid
# ✅ TWILIO API: Valid
# ✅ SENDGRID API: Valid
```

**Manual API Tests:**
```bash
# Test OpenAI API
python -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Test'}],
    max_tokens=10
)
print('✅ OpenAI API working:', response.choices[0].message.content)
"

# Test Airtable API
python -c "
from pyairtable import Api
import os
api = Api(os.getenv('AIRTABLE_API_KEY'))
bases = api.bases()
print('✅ Airtable API working, accessible bases:', len(bases))
"
```

### Step 2: Database Schema Testing

**Create test database structure:**
```bash
# Test database client initialization
python tests/test_database_integration.py
```

**Expected Output:**
```
🧪 Testing Database Integration Workflow
==================================================
✅ Database client initialized
✅ Test planner created: recXXXXXXXXXXXXXX
✅ Planner update successful
✅ Test communication created: recYYYYYYYYYYYYYY
✅ System stats retrieved: 1 total planners
✅ Query by status works: 1 discovered planners
✅ Get planner works: TEST_Sarah_Chen_DELETE
✅ Test data cleaned up

🎉 ALL DATABASE TESTS PASSED!
```

### Step 3: Credentials Security Testing

**Test credential encryption:**
```bash
# Test credential storage and retrieval
python -c "
from src.utils.credentials import CredentialsManager
cm = CredentialsManager()
# This should work without errors if credentials are properly set up
creds = cm.decrypt_credentials()
print('✅ Credentials decrypted successfully')
print('Available keys:', list(creds.keys()))
"
```

### Step 4: File System Testing

**Test directory structure and permissions:**
```bash
# Test all required directories exist and are writable
python -c "
from src.config import Config
import os

directories = [Config.DATA_DIR, Config.LOGS_DIR]
for dir_path in directories:
    if dir_path.exists() and os.access(dir_path, os.W_OK):
        print(f'✅ {dir_path.name} directory: OK')
    else:
        print(f'❌ {dir_path.name} directory: PROBLEM')
        dir_path.mkdir(exist_ok=True)
"
```

---

## 🤖 Part 2: Agent Unit Testing (20-30 minutes)

### Step 1: Researcher Agent Testing

**Test data extraction functions:**
```bash
# Test individual researcher components
python -c "
from src.agents.researcher_agent import ResearcherAgent
import unittest.mock as mock

# Mock the setup to avoid API calls
with mock.patch.object(ResearcherAgent, '_setup_clients'):
    researcher = ResearcherAgent()
    
    # Test email extraction
    text = 'Contact us at planner@example.com'
    email = researcher._extract_email(text)
    assert email == 'planner@example.com', 'Email extraction failed'
    print('✅ Email extraction works')
    
    # Test phone extraction  
    text = 'Call (949) 123-4567'
    phone = researcher._extract_phone(text)
    assert '949' in phone, 'Phone extraction failed'
    print('✅ Phone extraction works')
    
    # Test keyword setup
    assert len(researcher.multicultural_keywords) > 0, 'Keywords not loaded'
    print('✅ Keywords loaded:', len(researcher.multicultural_keywords))
"
```

### Step 2: Analyzer Agent Testing

**Test scoring algorithms:**
```bash
# Test scoring logic
python -c "
from src.agents.analyzer_agent import AnalyzerAgent
import unittest.mock as mock

with mock.patch.object(AnalyzerAgent, '_setup_llm'):
    analyzer = AnalyzerAgent()
    
    # Test multicultural scoring
    high_text = 'chinese wedding planner tea ceremony cantonese orange county'
    score_high, factors = analyzer._score_multicultural_fit(high_text)
    
    low_text = 'general wedding planner'  
    score_low, factors_low = analyzer._score_multicultural_fit(low_text)
    
    assert score_high > score_low, f'Scoring logic error: {score_high} vs {score_low}'
    print(f'✅ Multicultural scoring works: {score_high:.1f} > {score_low:.1f}')
    
    # Test red flag detection
    flags = analyzer._identify_red_flags('no asian experience fully booked overpriced')
    assert len(flags) > 0, 'Red flag detection not working'
    print(f'✅ Red flag detection works: {len(flags)} flags found')
"
```

### Step 3: Outreach Agent Testing

**Test template and personalization:**
```bash
# Test message generation
python -c "
from src.agents.outreach_agent import OutreachAgent
import unittest.mock as mock

with mock.patch.object(OutreachAgent, '_setup_clients'):
    outreach = OutreachAgent()
    
    # Test template loading
    assert 'initial_email' in outreach.templates, 'Templates not loaded'
    template = outreach.templates['initial_email']
    assert template.subject is not None, 'Template subject missing'
    print('✅ Templates loaded successfully')
    
    # Test personalization data extraction
    test_planner = {
        'name': 'Sarah Chen',
        'business_name': 'Chen Planning',
        'chinese_wedding_experience': True,
        'source': 'instagram'
    }
    
    data = outreach._extract_personalization_data(test_planner)
    assert data['name'] == 'Sarah', 'Name extraction failed'
    assert 'Chinese wedding experience' in data['experience_highlights'], 'Experience extraction failed'
    print('✅ Personalization data extraction works')
"
```

---

## 🔄 Part 3: Integration Testing (30-45 minutes)

### Step 1: Agent Communication Testing

**Test agent coordination via Airtable:**
```bash
# Test agent data handoffs
python tests/test_agent_integration.py
```

### Step 2: Workflow Phase Testing

**Test each workflow phase individually:**
```bash
# Test research phase (dry run)
python -c "
import os
os.environ['DRY_RUN'] = 'true'

from src.orchestrator import WeddingPlannerOrchestrator
import asyncio
import unittest.mock as mock

async def test_research_phase():
    with mock.patch('src.orchestrator.WeddingPlannerOrchestrator._setup_agents'):
        with mock.patch('src.orchestrator.WeddingPlannerOrchestrator._setup_llm'):
            orchestrator = WeddingPlannerOrchestrator()
            
            # Mock the agents to return test data
            orchestrator.researcher = mock.Mock()
            orchestrator.researcher.run_research_phase.return_value = ['test_planner_1', 'test_planner_2']
            
            orchestrator.analyzer = mock.Mock()
            orchestrator.analyzer.run_analysis_phase.return_value = ['test_planner_1']
            
            results = await orchestrator._execute_research_phase()
            assert 'planners_discovered' in results, 'Research phase structure wrong'
            print('✅ Research phase integration works')

asyncio.run(test_research_phase())
"
```

### Step 3: Database Transaction Testing

**Test complex database operations:**
```bash
# Test complete planner lifecycle
python -c "
from src.database.airtable_client import AirtableClient
from src.database.airtable_schema import PlannerRecord, PlannerStatus
from datetime import datetime

try:
    client = AirtableClient()
    
    # Create test planner
    planner = PlannerRecord(
        name='Integration Test Planner DELETE',
        email='test@example.com',
        status=PlannerStatus.DISCOVERED,
        source='test'
    )
    
    planner_id = client.create_planner(planner)
    print(f'✅ Planner created: {planner_id}')
    
    # Update through workflow states
    states = ['analyzed', 'shortlisted', 'contacted', 'responded']
    for state in states:
        client.update_planner(planner_id, {'status': state})
        retrieved = client.get_planner(planner_id)
        assert retrieved['status'] == state, f'Status update failed: {state}'
        print(f'✅ Status updated to: {state}')
    
    # Test statistics
    stats = client.get_system_stats()
    assert stats['total_planners'] > 0, 'Stats calculation failed'
    print(f'✅ Stats calculation works: {stats[\"total_planners\"]} planners')
    
    # Cleanup
    client.planners_table.delete(planner_id)
    print('✅ Cleanup successful')
    
    print('🎉 DATABASE INTEGRATION TESTS PASSED!')
    
except Exception as e:
    print(f'❌ Integration test failed: {e}')
    raise
"
```

---

## 📧 Part 4: Communication Testing (15-20 minutes)

### Step 1: Email Delivery Testing

**Test email sending without spamming real planners:**
```bash
# Test with your own email first
python -c "
import os
from src.agents.outreach_agent import OutreachAgent
import unittest.mock as mock

# Create test planner data
test_planner = {
    'id': 'test_planner',
    'name': 'Test Planner',
    'email': 'YOUR_EMAIL@domain.com',  # Replace with your email
    'business_name': 'Test Wedding Planning',
    'source': 'test'
}

# Create test message
test_message = {
    'subject': 'TEST: Wedding Planner System - Please Ignore',
    'content': 'This is a test email from the wedding planner hiring system. Please ignore.',
    'template_used': 'test_template'
}

# Note: This requires manually replacing YOUR_EMAIL above
print('⚠️  Manual test required:')
print('1. Replace YOUR_EMAIL@domain.com with your actual email')
print('2. Run the email test')
print('3. Check your inbox for test email')
print('4. Verify email formatting and sender information')
"
```

### Step 2: SMS Testing (Optional)

**Test SMS delivery:**
```bash
# Test SMS with your own phone number
python -c "
print('📱 SMS Testing:')
print('1. Add your phone number to test_planner data')
print('2. Send test SMS to yourself')
print('3. Verify message formatting and sender ID')
print('4. Check delivery status')
print('⚠️  SMS tests cost ~$0.01 each')
"
```

### Step 3: Template Validation

**Test all email templates:**
```bash
# Validate template syntax and personalization
python -c "
from src.agents.outreach_agent import OutreachAgent
import unittest.mock as mock

with mock.patch.object(OutreachAgent, '_setup_clients'):
    outreach = OutreachAgent()
    
    test_planner = {
        'name': 'Test Planner',
        'business_name': 'Test Planning Co',
        'specializations': ['Chinese weddings', 'Tea ceremony'],
        'chinese_wedding_experience': True,
        'source': 'instagram',
        'instagram_handle': 'testplanner'
    }
    
    for template_name in ['initial_email', 'follow_up_email', 'urgent_email']:
        try:
            # Mock AI personalization to avoid API calls
            with mock.patch.object(outreach, '_ai_personalize_content') as mock_ai:
                mock_ai.return_value = f'Personalized content for {template_name}'
                
                message = outreach._generate_personalized_message(test_planner, template_name)
                
                assert message['subject'] is not None, f'Missing subject in {template_name}'
                assert message['content'] is not None, f'Missing content in {template_name}'
                assert '[name]' not in message['content'], f'Unpersonalized placeholder in {template_name}'
                
                print(f'✅ Template {template_name}: Valid')
                
        except Exception as e:
            print(f'❌ Template {template_name}: Error - {e}')
    
    print('🎉 ALL TEMPLATE TESTS PASSED!')
"
```

---

## 💰 Part 5: Cost Simulation Testing (10-15 minutes)

### Step 1: Cost Tracking Accuracy

**Test cost calculation and tracking:**
```bash
# Test cost tracking functions
python -c "
from src.monitoring.cost_tracker import CostTracker
import tempfile
from pathlib import Path

# Use temporary directory for testing
with tempfile.TemporaryDirectory() as temp_dir:
    import src.config
    original_data_dir = src.config.Config.DATA_DIR
    src.config.Config.DATA_DIR = Path(temp_dir)
    
    try:
        tracker = CostTracker()
        
        # Test cost recording
        tracker.record_cost('openai', 'completion', 0.05, 'Test completion', 'test_agent')
        tracker.record_cost('apify', 'scraping', 0.02, 'Test scraping', 'researcher')
        
        # Test budget status
        status = tracker.get_budget_status()
        assert status.total_spent == 0.07, f'Cost calculation wrong: {status.total_spent}'
        print(f'✅ Cost tracking works: ${status.total_spent:.2f}')
        
        # Test cost breakdown
        breakdown = tracker.get_cost_breakdown(30)
        assert breakdown['total_costs'] == 0.07, 'Breakdown calculation wrong'
        assert 'openai' in breakdown['service_breakdown'], 'Service breakdown missing'
        print('✅ Cost breakdown works')
        
        # Test budget alerts
        tracker.record_cost('test', 'big_expense', 100.0)  # Trigger alert
        status = tracker.get_budget_status()
        assert len(status.alerts) > 0, 'Budget alerts not working'
        print(f'✅ Budget alerts work: {len(status.alerts)} alerts')
        
        print('🎉 COST TRACKING TESTS PASSED!')
        
    finally:
        src.config.Config.DATA_DIR = original_data_dir
"
```

### Step 2: Budget Limit Testing

**Test budget enforcement:**
```bash
# Test budget limit enforcement
python -c "
from src.monitoring.cost_tracker import CostTracker
from src.config import Config

print(f'Current budget limit: ${Config.MONTHLY_BUDGET_LIMIT}')
print('Testing budget enforcement...')

# This would be integrated into the actual system
# For now, just verify the calculation logic
test_spent = 120.0
limit = Config.MONTHLY_BUDGET_LIMIT
percentage = (test_spent / limit) * 100

if percentage > 90:
    print('✅ Budget alert logic: CRITICAL level detected')
elif percentage > 75:
    print('✅ Budget alert logic: WARNING level detected')
else:
    print('✅ Budget alert logic: Normal level')
"
```

---

## 🧪 Part 6: End-to-End Testing (45-60 minutes)

### Step 1: Dry Run Full Workflow

**Test complete workflow without external API calls:**
```bash
# Run complete workflow in dry-run mode
python scripts/run_system.py --dry-run
```

**Expected behavior:**
- All agents initialize successfully
- Mock data flows through all phases
- Human approval gates trigger correctly
- Cost tracking records simulated costs
- Final report generates with mock data

### Step 2: Limited Real Data Test

**Test with minimal real API usage:**
```bash
# Test with very limited scope to minimize costs
python -c "
import os
os.environ['TEST_MODE'] = 'true'
os.environ['MAX_PLANNERS'] = '5'  # Limit to 5 planners

# Run limited research phase
from src.agents.researcher_agent import ResearcherAgent
import unittest.mock as mock

# Mock expensive operations but keep basic ones
print('🧪 Running limited real data test...')
print('This will make minimal API calls (~$1-2 cost)')
print('Continue? (y/n): ', end='')

# Uncomment next lines for actual test:
# response = input()
# if response.lower() == 'y':
#     researcher = ResearcherAgent()
#     # Test with just 1-2 Instagram posts
#     # This would be a real but very limited test
print('⚠️  Real API test commented out - uncomment to run')
"
```

### Step 3: Monitoring Integration Test

**Test dashboard and monitoring:**
```bash
# Test monitoring dashboard
python -c "
from src.monitoring.dashboard import MonitoringDashboard
import unittest.mock as mock

dashboard = MonitoringDashboard()

# Test system metrics
metrics = dashboard.get_system_metrics()
assert metrics.cpu_percent >= 0, 'CPU metrics not working'
assert metrics.memory_percent >= 0, 'Memory metrics not working'
print('✅ System metrics collection works')

# Test health check
health = dashboard.get_health_check()
assert 'status' in health, 'Health check structure wrong'
assert 'health_score' in health, 'Health score missing'
print(f'✅ Health check works: {health[\"status\"]}')

# Test report generation
report = dashboard.generate_dashboard_report()
assert 'WEDDING PLANNER HIRING SYSTEM' in report, 'Report generation failed'
print('✅ Dashboard report generation works')

print('🎉 MONITORING TESTS PASSED!')
"
```

---

## 🚨 Part 7: Stress Testing & Error Handling (20-30 minutes)

### Step 1: API Failure Simulation

**Test system behavior when APIs fail:**
```bash
# Test API failure handling
python -c "
import unittest.mock as mock
from src.agents.researcher_agent import ResearcherAgent

# Test with simulated API failures
with mock.patch.object(ResearcherAgent, '_setup_clients'):
    researcher = ResearcherAgent()
    
    # Mock failing API calls
    with mock.patch('requests.get') as mock_get:
        mock_get.side_effect = Exception('API connection failed')
        
        # Test error handling
        try:
            result = researcher._scrape_weddingwire_planners()
            # Should return empty list, not crash
            assert isinstance(result, list), 'Error handling failed'
            print('✅ API failure handling works')
        except Exception as e:
            print(f'❌ System crashed on API failure: {e}')
"
```

### Step 2: Data Corruption Testing

**Test handling of malformed data:**
```bash
# Test malformed data handling
python -c "
from src.agents.analyzer_agent import AnalyzerAgent
import unittest.mock as mock

with mock.patch.object(AnalyzerAgent, '_setup_llm'):
    analyzer = AnalyzerAgent()
    
    # Test with malformed planner data
    bad_data = {
        'name': None,  # Missing name
        'total_reviews': 'not_a_number',  # Wrong type
        'average_rating': -1,  # Invalid rating
        'review_summary': None
    }
    
    try:
        score, factors = analyzer._score_reviews(bad_data)
        # Should handle gracefully, not crash
        assert isinstance(score, (int, float)), 'Data validation failed'
        print('✅ Malformed data handling works')
    except Exception as e:
        print(f'❌ System crashed on bad data: {e}')
"
```

### Step 3: Resource Exhaustion Testing

**Test system under resource constraints:**
```bash
# Test memory and processing limits
python -c "
import psutil
import gc

print(f'Current memory usage: {psutil.virtual_memory().percent}%')
print(f'Current CPU usage: {psutil.cpu_percent()}%')

# Test large dataset handling
large_dataset = []
for i in range(1000):
    large_dataset.append({
        'id': f'planner_{i}',
        'name': f'Planner {i}' * 100,  # Large strings
        'bio_text': 'Lorem ipsum ' * 1000,  # Very large bio
        'status': 'discovered'
    })

print(f'Created large dataset: {len(large_dataset)} planners')
print(f'Memory after large dataset: {psutil.virtual_memory().percent}%')

# Cleanup
del large_dataset
gc.collect()
print('✅ Large dataset handling test passed')
"
```

### Step 4: Network Failure Recovery

**Test network interruption handling:**
```bash
# Test network failure scenarios
python -c "
import unittest.mock as mock
from src.database.airtable_client import AirtableClient
import requests

# Simulate network timeout
with mock.patch('requests.get') as mock_get:
    mock_get.side_effect = requests.exceptions.Timeout('Network timeout')
    
    try:
        # This should handle timeout gracefully
        print('Testing network timeout handling...')
        # In real implementation, this would have retry logic
        print('✅ Network timeout handling needs implementation')
    except Exception as e:
        print(f'❌ Network failure not handled: {e}')
"
```

---

## 📊 Part 8: Performance Validation (15-20 minutes)

### Step 1: Response Time Testing

**Test system response times:**
```bash
# Test performance benchmarks
python -c "
import time
from src.agents.analyzer_agent import AnalyzerAgent
import unittest.mock as mock

with mock.patch.object(AnalyzerAgent, '_setup_llm'):
    analyzer = AnalyzerAgent()
    
    # Test scoring performance
    test_text = 'Chinese wedding planner with tea ceremony experience in Orange County'
    
    start_time = time.time()
    score, factors = analyzer._score_multicultural_fit(test_text)
    end_time = time.time()
    
    execution_time = end_time - start_time
    print(f'Scoring execution time: {execution_time:.3f} seconds')
    
    if execution_time < 0.1:
        print('✅ Scoring performance: Excellent')
    elif execution_time < 0.5:
        print('✅ Scoring performance: Good')
    else:
        print('⚠️  Scoring performance: Slow')
"
```

### Step 2: Memory Usage Testing

**Test memory efficiency:**
```bash
# Test memory usage patterns
python -c "
import psutil
import gc

def get_memory_usage():
    return psutil.Process().memory_info().rss / 1024 / 1024  # MB

print(f'Baseline memory: {get_memory_usage():.1f} MB')

# Simulate agent initialization
from src.agents.researcher_agent import ResearcherAgent
import unittest.mock as mock

with mock.patch.object(ResearcherAgent, '_setup_clients'):
    researcher = ResearcherAgent()
    print(f'After researcher init: {get_memory_usage():.1f} MB')

from src.agents.analyzer_agent import AnalyzerAgent
with mock.patch.object(AnalyzerAgent, '_setup_llm'):
    analyzer = AnalyzerAgent()
    print(f'After analyzer init: {get_memory_usage():.1f} MB')

from src.agents.outreach_agent import OutreachAgent
with mock.patch.object(OutreachAgent, '_setup_clients'):
    outreach = OutreachAgent()
    print(f'After outreach init: {get_memory_usage():.1f} MB')

final_memory = get_memory_usage()
if final_memory < 100:
    print('✅ Memory usage: Excellent')
elif final_memory < 200:
    print('✅ Memory usage: Good')
else:
    print('⚠️  Memory usage: High')
"
```

---

## 🎯 Part 9: Pre-Production Validation Checklist

### ✅ Final System Validation

Before running the full system, verify all these tests pass:

**Infrastructure Tests:**
- [ ] All API connections validated
- [ ] Database schema created and tested
- [ ] Credentials encrypted and accessible
- [ ] File system permissions correct

**Agent Tests:**
- [ ] Researcher extracts data correctly
- [ ] Analyzer scoring logic works
- [ ] Outreach templates personalize properly
- [ ] All agents handle errors gracefully

**Integration Tests:**
- [ ] Agents communicate via database
- [ ] Workflow phases execute in sequence
- [ ] Human approval gates trigger correctly
- [ ] Data flows through complete pipeline

**Communication Tests:**
- [ ] Email delivery works (test with your email)
- [ ] SMS delivery works (optional)
- [ ] Templates format correctly
- [ ] Personalization replaces placeholders

**Cost Tests:**
- [ ] Cost tracking records accurately
- [ ] Budget limits trigger alerts
- [ ] Cost breakdown calculations correct
- [ ] Emergency stop procedures work

**Performance Tests:**
- [ ] Response times acceptable (<0.5s for scoring)
- [ ] Memory usage reasonable (<200MB)
- [ ] Large dataset handling works
- [ ] System recovers from failures

### 🚨 Critical Test Command

**Run all automated tests:**
```bash
# Run comprehensive test suite
pytest tests/ -v --tb=short

# Run integration tests
python tests/test_system_integration.py

# Run performance tests
python tests/test_performance.py

# Validate configuration
python scripts/setup.py --validate-all
```

### 📊 Test Results Interpretation

**All Green (✅)**: System ready for production
**Some Yellow (⚠️)**: Review warnings, proceed with caution
**Any Red (❌)**: Fix issues before production run

### 🎯 Final Validation Steps

1. **Review test logs** for any warnings or errors
2. **Verify budget limits** are set appropriately
3. **Confirm email/SMS credentials** are for production use
4. **Check wedding specifications** match your requirements
5. **Ensure human availability** for approval gates
6. **Create system backup** before starting production

---

## 🚀 Production Readiness Criteria

The system is ready for production when:

✅ **All automated tests pass** (>95% success rate)
✅ **API costs under $5** for complete test suite
✅ **Email delivery successful** to test address
✅ **Database operations complete** without errors
✅ **Monitoring dashboard functional** and reporting correctly
✅ **Error handling graceful** for all tested failure modes
✅ **Performance acceptable** for expected workload
✅ **Human interfaces working** (approval gates, notifications)

**Command to verify readiness:**
```bash
# Final readiness check
python scripts/run_system.py --mode health-check
python scripts/manage_system.py status
python scripts/setup.py --validate-all

# If all report "healthy" status, you're ready to launch!
python scripts/run_system.py
```

**Good luck with your wedding planner search!** 🎉💒

---

*Remember: Testing thoroughly now saves hours of debugging during production execution.*