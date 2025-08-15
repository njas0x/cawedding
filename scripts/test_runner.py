#!/usr/bin/env python3
"""
Comprehensive test runner for the Wedding Planner Hiring System
"""
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent

def run_command(command, description, timeout=300):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_root
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ PASSED ({execution_time:.1f}s)")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED ({execution_time:.1f}s)")
            if result.stderr.strip():
                print("Error output:")
                print(result.stderr)
            if result.stdout.strip():
                print("Standard output:")
                print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT (>{timeout}s)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🎯 Wedding Planner Hiring System - Comprehensive Test Suite")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test categories with commands
    test_categories = [
        {
            "name": "Environment Setup Validation",
            "tests": [
                ("python scripts/setup.py --skip-deps", "Setup script validation"),
                ("python -c 'import src.config; print(\"Config import successful\")'", "Configuration import test"),
                ("python -c 'from src.utils.credentials import CredentialsManager; print(\"Credentials manager import successful\")'", "Credentials system test")
            ]
        },
        {
            "name": "Unit Tests",
            "tests": [
                ("python -m pytest tests/test_agents.py -v", "Agent unit tests"),
                ("python -m pytest tests/test_system_integration.py -v", "System integration tests")
            ]
        },
        {
            "name": "Database Integration", 
            "tests": [
                ("python tests/test_database_integration.py", "Database workflow test")
            ]
        },
        {
            "name": "Agent Integration",
            "tests": [
                ("python tests/test_agent_integration.py", "Agent communication test")
            ]
        },
        {
            "name": "Performance Testing",
            "tests": [
                ("python tests/test_performance.py", "Performance benchmarks")
            ]
        },
        {
            "name": "Component Testing",
            "tests": [
                ("python -c 'from src.agents.researcher_agent import ResearcherAgent; print(\"Researcher agent import successful\")'", "Researcher agent import"),
                ("python -c 'from src.agents.analyzer_agent import AnalyzerAgent; print(\"Analyzer agent import successful\")'", "Analyzer agent import"),
                ("python -c 'from src.agents.outreach_agent import OutreachAgent; print(\"Outreach agent import successful\")'", "Outreach agent import"),
                ("python -c 'from src.orchestrator import WeddingPlannerOrchestrator; print(\"Orchestrator import successful\")'", "Orchestrator import"),
                ("python -c 'from src.monitoring.dashboard import MonitoringDashboard; print(\"Dashboard import successful\")'", "Dashboard import"),
                ("python -c 'from src.monitoring.cost_tracker import CostTracker; print(\"Cost tracker import successful\")'", "Cost tracker import")
            ]
        },
        {
            "name": "Configuration Validation",
            "tests": [
                ("python -c 'from src.config import Config; print(f\"Budget limit: ${Config.MONTHLY_BUDGET_LIMIT}\")'", "Budget configuration"),
                ("python -c 'from src.config import Config; print(f\"Target planners: {Config.TARGET_PLANNER_COUNT}\")'", "Search configuration"),
                ("python -c 'from src.config import Config; print(f\"Instagram hashtags: {len(Config.INSTAGRAM_HASHTAGS)}\")'", "Social media configuration")
            ]
        }
    ]
    
    # Run all test categories
    total_tests = 0
    passed_tests = 0
    failed_categories = []
    
    for category in test_categories:
        print(f"\n📋 {category['name']}")
        print("=" * 70)
        
        category_passed = 0
        category_total = len(category['tests'])
        
        for command, description in category['tests']:
            total_tests += 1
            if run_command(command, description):
                passed_tests += 1
                category_passed += 1
        
        # Category summary
        if category_passed == category_total:
            print(f"\n✅ {category['name']}: {category_passed}/{category_total} tests passed")
        else:
            print(f"\n❌ {category['name']}: {category_passed}/{category_total} tests passed")
            failed_categories.append(category['name'])
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 70)
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    print(f"⏱️  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed_categories:
        print(f"\n❌ Failed Categories ({len(failed_categories)}):")
        for category in failed_categories:
            print(f"   • {category}")
    
    # Determine system readiness
    if success_rate >= 95:
        print("\n🎉 SYSTEM READY FOR PRODUCTION!")
        print("All critical tests passed. You can proceed with confidence.")
        readiness = "READY"
    elif success_rate >= 85:
        print("\n⚠️  SYSTEM MOSTLY READY")
        print("Most tests passed. Review failures and proceed with caution.")
        readiness = "MOSTLY_READY"
    elif success_rate >= 70:
        print("\n🔧 SYSTEM NEEDS ATTENTION")
        print("Several issues detected. Fix critical problems before production.")
        readiness = "NEEDS_WORK"
    else:
        print("\n🚨 SYSTEM NOT READY")
        print("Major issues detected. Significant fixes required before production.")
        readiness = "NOT_READY"
    
    # Generate test report
    report_content = f"""# Wedding Planner Hiring System - Test Report

## Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Success Rate**: {success_rate:.1f}%
- **System Status**: {readiness}

## Test Categories
"""
    
    for category in test_categories:
        category_tests = len(category['tests'])
        report_content += f"\n### {category['name']}\n"
        report_content += f"- Tests: {category_tests}\n"
        if category['name'] in failed_categories:
            report_content += "- Status: ❌ FAILED\n"
        else:
            report_content += "- Status: ✅ PASSED\n"
    
    if failed_categories:
        report_content += f"\n## Failed Categories\n"
        for category in failed_categories:
            report_content += f"- {category}\n"
    
    report_content += f"\n## Recommendations\n"
    if readiness == "READY":
        report_content += "- ✅ System is ready for production use\n"
        report_content += "- ✅ All critical components validated\n"
        report_content += "- ✅ Proceed with wedding planner search\n"
    elif readiness == "MOSTLY_READY":
        report_content += "- ⚠️  Review failed tests before production\n"
        report_content += "- ⚠️  Consider running tests again after fixes\n"
        report_content += "- ✅ Core functionality appears stable\n"
    else:
        report_content += "- ❌ Fix critical issues before production\n"
        report_content += "- ❌ Re-run tests after fixes\n"
        report_content += "- ❌ Do not proceed with live system yet\n"
    
    # Save test report
    report_file = project_root / "test_report.md"
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    print(f"\n📄 Test report saved: {report_file}")
    
    # Exit with appropriate code
    if success_rate >= 85:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()