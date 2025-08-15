#!/usr/bin/env python3
"""
Performance test script
"""
import sys
import time
import psutil
import gc
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.agents.researcher_agent import ResearcherAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.outreach_agent import OutreachAgent
from src.monitoring.cost_tracker import CostTracker
from src.monitoring.dashboard import MonitoringDashboard

def get_memory_usage():
    """Get current memory usage in MB"""
    return psutil.Process().memory_info().rss / 1024 / 1024

def test_agent_initialization_performance():
    """Test agent initialization times and memory usage"""
    print("🧪 Testing Agent Initialization Performance")
    print("=" * 50)
    
    baseline_memory = get_memory_usage()
    print(f"Baseline memory: {baseline_memory:.1f} MB")
    
    results = {}
    
    try:
        # Test Researcher Agent
        start_time = time.time()
        with patch.object(ResearcherAgent, '_setup_clients'):
            researcher = ResearcherAgent()
        researcher_time = time.time() - start_time
        researcher_memory = get_memory_usage()
        
        results['researcher'] = {
            'init_time': researcher_time,
            'memory_usage': researcher_memory - baseline_memory
        }
        
        print(f"✅ Researcher: {researcher_time:.3f}s, +{researcher_memory - baseline_memory:.1f} MB")
        
        # Test Analyzer Agent
        start_time = time.time()
        with patch.object(AnalyzerAgent, '_setup_llm'):
            analyzer = AnalyzerAgent()
        analyzer_time = time.time() - start_time
        analyzer_memory = get_memory_usage()
        
        results['analyzer'] = {
            'init_time': analyzer_time,
            'memory_usage': analyzer_memory - researcher_memory
        }
        
        print(f"✅ Analyzer: {analyzer_time:.3f}s, +{analyzer_memory - researcher_memory:.1f} MB")
        
        # Test Outreach Agent
        start_time = time.time()
        with patch.object(OutreachAgent, '_setup_clients'):
            outreach = OutreachAgent()
        outreach_time = time.time() - start_time
        outreach_memory = get_memory_usage()
        
        results['outreach'] = {
            'init_time': outreach_time,
            'memory_usage': outreach_memory - analyzer_memory
        }
        
        print(f"✅ Outreach: {outreach_time:.3f}s, +{outreach_memory - analyzer_memory:.1f} MB")
        
        # Overall results
        total_time = researcher_time + analyzer_time + outreach_time
        total_memory = outreach_memory - baseline_memory
        
        print(f"\nTotal initialization: {total_time:.3f}s, {total_memory:.1f} MB")
        
        # Performance criteria
        if total_time < 5.0:
            print("✅ Initialization performance: Excellent")
        elif total_time < 10.0:
            print("✅ Initialization performance: Good")
        else:
            print("⚠️  Initialization performance: Slow")
        
        if total_memory < 100:
            print("✅ Memory efficiency: Excellent")
        elif total_memory < 200:
            print("✅ Memory efficiency: Good")
        else:
            print("⚠️  Memory efficiency: High usage")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_scoring_performance():
    """Test scoring algorithm performance"""
    print("\n🧪 Testing Scoring Performance")
    print("=" * 30)
    
    try:
        with patch.object(AnalyzerAgent, '_setup_llm'):
            analyzer = AnalyzerAgent()
            
            # Test data
            test_cases = [
                "Chinese wedding planner with tea ceremony experience in Orange County",
                "General wedding planner",
                "Multicultural wedding specialist with Asian ceremony coordination and bilingual services",
                "Modern fusion wedding planner specializing in traditional Chinese banquets and city pop elements"
            ]
            
            total_time = 0
            for i, test_text in enumerate(test_cases, 1):
                start_time = time.time()
                score, factors = analyzer._score_multicultural_fit(test_text)
                execution_time = time.time() - start_time
                total_time += execution_time
                
                print(f"Test {i}: {execution_time:.3f}s (Score: {score:.1f})")
            
            avg_time = total_time / len(test_cases)
            print(f"\nAverage scoring time: {avg_time:.3f}s")
            
            if avg_time < 0.1:
                print("✅ Scoring performance: Excellent")
            elif avg_time < 0.5:
                print("✅ Scoring performance: Good")
            else:
                print("⚠️  Scoring performance: Slow")
        
        return True
        
    except Exception as e:
        print(f"❌ Scoring performance test failed: {e}")
        return False

def test_large_dataset_handling():
    """Test handling of large datasets"""
    print("\n🧪 Testing Large Dataset Handling")
    print("=" * 35)
    
    try:
        baseline_memory = get_memory_usage()
        
        # Create large dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'id': f'planner_{i}',
                'name': f'Planner {i}',
                'bio_text': 'Chinese wedding planner with tea ceremony experience ' * 50,
                'status': 'discovered',
                'total_reviews': i % 100,
                'average_rating': 3.0 + (i % 20) / 10.0
            })
        
        memory_after_creation = get_memory_usage()
        print(f"Created 1000 planners: +{memory_after_creation - baseline_memory:.1f} MB")
        
        # Test processing performance
        with patch.object(AnalyzerAgent, '_setup_llm'):
            analyzer = AnalyzerAgent()
            
            start_time = time.time()
            processed_count = 0
            
            # Process subset to test performance
            for planner in large_dataset[:100]:  # Process 100 planners
                text_data = analyzer._gather_planner_text_data(planner)
                score, factors = analyzer._score_multicultural_fit(text_data)
                processed_count += 1
                
                # Break if taking too long
                if time.time() - start_time > 10.0:
                    break
            
            processing_time = time.time() - start_time
            rate = processed_count / processing_time if processing_time > 0 else 0
            
            print(f"Processed {processed_count} planners in {processing_time:.2f}s")
            print(f"Processing rate: {rate:.1f} planners/second")
            
            if rate > 10:
                print("✅ Large dataset performance: Excellent")
            elif rate > 5:
                print("✅ Large dataset performance: Good")
            else:
                print("⚠️  Large dataset performance: Slow")
        
        # Cleanup
        del large_dataset
        gc.collect()
        
        final_memory = get_memory_usage()
        print(f"Memory after cleanup: {final_memory - baseline_memory:.1f} MB difference")
        
        return True
        
    except Exception as e:
        print(f"❌ Large dataset test failed: {e}")
        return False

def test_monitoring_performance():
    """Test monitoring system performance"""
    print("\n🧪 Testing Monitoring Performance")
    print("=" * 35)
    
    try:
        # Test dashboard performance
        start_time = time.time()
        
        with patch('src.database.airtable_client.AirtableClient'):
            with patch('src.monitoring.cost_tracker.CostTracker'):
                dashboard = MonitoringDashboard()
                
                # Test metrics collection
                metrics = dashboard.get_system_metrics()
                health = dashboard.get_health_check()
                report = dashboard.generate_dashboard_report()
        
        monitoring_time = time.time() - start_time
        print(f"Monitoring operations: {monitoring_time:.3f}s")
        
        if monitoring_time < 1.0:
            print("✅ Monitoring performance: Excellent")
        elif monitoring_time < 3.0:
            print("✅ Monitoring performance: Good")
        else:
            print("⚠️  Monitoring performance: Slow")
        
        # Test cost tracking performance
        start_time = time.time()
        
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            import src.config
            original_data_dir = src.config.Config.DATA_DIR
            src.config.Config.DATA_DIR = Path(temp_dir)
            
            try:
                tracker = CostTracker()
                
                # Add many cost entries
                for i in range(100):
                    tracker.record_cost('test_service', f'operation_{i}', 0.01, f'Test {i}', 'test_agent')
                
                # Test report generation
                budget_status = tracker.get_budget_status()
                cost_breakdown = tracker.get_cost_breakdown(30)
                cost_report = tracker.get_cost_report()
                
            finally:
                src.config.Config.DATA_DIR = original_data_dir
        
        cost_tracking_time = time.time() - start_time
        print(f"Cost tracking (100 entries): {cost_tracking_time:.3f}s")
        
        if cost_tracking_time < 1.0:
            print("✅ Cost tracking performance: Excellent")
        elif cost_tracking_time < 3.0:
            print("✅ Cost tracking performance: Good")
        else:
            print("⚠️  Cost tracking performance: Slow")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring performance test failed: {e}")
        return False

def test_system_resource_usage():
    """Test overall system resource usage"""
    print("\n🧪 Testing System Resource Usage")
    print("=" * 35)
    
    try:
        # Get initial system state
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().percent
        initial_disk = psutil.disk_usage('/').percent
        
        print(f"Initial CPU: {initial_cpu:.1f}%")
        print(f"Initial Memory: {initial_memory:.1f}%")
        print(f"Initial Disk: {initial_disk:.1f}%")
        
        # Simulate system load
        start_time = time.time()
        
        with patch.object(ResearcherAgent, '_setup_clients'):
            with patch.object(AnalyzerAgent, '_setup_llm'):
                with patch.object(OutreachAgent, '_setup_clients'):
                    
                    # Initialize all agents
                    researcher = ResearcherAgent()
                    analyzer = AnalyzerAgent()
                    outreach = OutreachAgent()
                    
                    # Simulate some work
                    for i in range(10):
                        text = f"Test planner {i} with Chinese wedding experience"
                        score, factors = analyzer._score_multicultural_fit(text)
        
        # Get final system state
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = psutil.virtual_memory().percent
        execution_time = time.time() - start_time
        
        print(f"\nAfter execution ({execution_time:.1f}s):")
        print(f"Final CPU: {final_cpu:.1f}%")
        print(f"Final Memory: {final_memory:.1f}%")
        
        # Check resource usage increases
        cpu_increase = final_cpu - initial_cpu
        memory_increase = final_memory - initial_memory
        
        print(f"\nResource changes:")
        print(f"CPU increase: {cpu_increase:.1f}%")
        print(f"Memory increase: {memory_increase:.1f}%")
        
        # Performance criteria
        if cpu_increase < 10 and memory_increase < 5:
            print("✅ Resource usage: Excellent")
        elif cpu_increase < 20 and memory_increase < 10:
            print("✅ Resource usage: Good")
        else:
            print("⚠️  Resource usage: High")
        
        return True
        
    except Exception as e:
        print(f"❌ Resource usage test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Performance Test Suite")
    print("=" * 60)
    
    tests = [
        test_agent_initialization_performance,
        test_scoring_performance,
        test_large_dataset_handling,
        test_monitoring_performance,
        test_system_resource_usage
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🧪 Performance Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL PERFORMANCE TESTS PASSED!")
        performance_grade = "A"
    elif failed <= 2:
        print("⚠️  Most performance tests passed with some warnings")
        performance_grade = "B"
    else:
        print("❌ Multiple performance issues detected")
        performance_grade = "C"
    
    print(f"Overall Performance Grade: {performance_grade}")
    
    sys.exit(0 if failed == 0 else 1)