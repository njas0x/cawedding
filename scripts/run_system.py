#!/usr/bin/env python3
"""
Main execution script for the Wedding Planner Hiring System
"""
import os
import sys
import asyncio
import argparse
import signal
import json
from datetime import datetime
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.orchestrator import WeddingPlannerOrchestrator, run_wedding_planner_hiring_system
from src.monitoring.dashboard import MonitoringDashboard
from src.monitoring.cost_tracker import CostTracker
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger
from src.config import Config

logger = setup_logger("main")

class SystemRunner:
    """Main system runner with graceful shutdown handling"""
    
    def __init__(self):
        self.orchestrator = None
        self.dashboard = None
        self.running = False
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    async def run_complete_workflow(self, monitoring: bool = True):
        """Run the complete wedding planner hiring workflow"""
        logger.info("🎯 Starting Wedding Planner Hiring System")
        logger.info("=" * 60)
        
        self.running = True
        
        try:
            # Initialize components
            self.orchestrator = WeddingPlannerOrchestrator()
            
            if monitoring:
                self.dashboard = MonitoringDashboard()
                logger.info("📊 Monitoring dashboard enabled")
            
            # Start monitoring in background if enabled
            monitoring_task = None
            if monitoring and self.dashboard:
                monitoring_task = asyncio.create_task(self._run_monitoring())
            
            # Run the main workflow
            logger.info("🚀 Starting workflow execution...")
            workflow_results = await self.orchestrator.run_complete_workflow()
            
            # Stop monitoring
            if monitoring_task:
                monitoring_task.cancel()
                try:
                    await monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Save final results
            await self._save_results(workflow_results)
            
            # Generate final report
            self._generate_final_report(workflow_results)
            
            logger.info("✅ Workflow completed successfully!")
            return workflow_results
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            raise
        finally:
            self.running = False
    
    async def _run_monitoring(self):
        """Run monitoring dashboard in background"""
        try:
            while self.running:
                # Generate dashboard report
                report = self.dashboard.generate_dashboard_report()
                logger.info(f"\n{report}")
                
                # Save metrics snapshot
                self.dashboard.save_metrics_snapshot()
                
                # Wait before next update
                await asyncio.sleep(60)  # Update every minute
                
        except asyncio.CancelledError:
            logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
    
    async def _save_results(self, results: dict):
        """Save workflow results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = Config.DATA_DIR / f"workflow_results_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def _generate_final_report(self, results: dict):
        """Generate final system report"""
        try:
            # Generate comprehensive report
            report_lines = [
                "🎯 WEDDING PLANNER HIRING SYSTEM - FINAL REPORT",
                f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 70,
                "",
                "📊 WORKFLOW SUMMARY:",
            ]
            
            # Add phase results
            if "phases_completed" in results:
                for phase_result in results["phases_completed"]:
                    phase_name = phase_result["phase"]
                    phase_data = phase_result["results"]
                    
                    report_lines.append(f"  📋 {phase_name.upper()} PHASE:")
                    
                    if phase_name == "research":
                        discovered = phase_data.get("planners_discovered", 0)
                        shortlisted = phase_data.get("shortlist_generated", 0)
                        report_lines.append(f"    • Planners Discovered: {discovered}")
                        report_lines.append(f"    • Shortlisted: {shortlisted}")
                    
                    elif phase_name == "outreach":
                        contacted = phase_data.get("total_contacted", 0)
                        responses = phase_data.get("responses_received", 0)
                        report_lines.append(f"    • Planners Contacted: {contacted}")
                        report_lines.append(f"    • Responses Received: {responses}")
                    
                    elif phase_name == "calls":
                        calls = phase_data.get("calls_completed", 0)
                        viable = phase_data.get("viable_candidates", 0)
                        report_lines.append(f"    • Calls Completed: {calls}")
                        report_lines.append(f"    • Viable Candidates: {viable}")
                    
                    elif phase_name == "decision":
                        hired = len(phase_data.get("hired_planners", []))
                        report_lines.append(f"    • Planners Hired: {hired}")
                    
                    report_lines.append("")
            
            # Add final status
            if "final_status" in results:
                status = results["final_status"]
                report_lines.extend([
                    "🎯 FINAL STATUS:",
                    f"  Total Planners: {status.total_planners}",
                    f"  Shortlisted: {status.shortlisted_planners}",
                    f"  Contacted: {status.contacted_planners}",
                    f"  Responding: {status.responding_planners}",
                    f"  Calls Completed: {status.calls_completed}",
                    f"  Planners Hired: {status.hired_planners}",
                    ""
                ])
            
            # Add cost summary
            cost_tracker = CostTracker()
            budget_status = cost_tracker.get_budget_status()
            
            report_lines.extend([
                "💰 COST SUMMARY:",
                f"  Total Spent: ${budget_status.total_spent:.2f}",
                f"  Budget Used: {budget_status.percentage_used:.1f}%",
                f"  Remaining Budget: ${budget_status.remaining_budget:.2f}",
                ""
            ])
            
            # Add timing
            if "total_duration" in results:
                duration_hours = results["total_duration"] / 3600
                report_lines.extend([
                    "⏱️ EXECUTION TIME:",
                    f"  Total Duration: {duration_hours:.1f} hours",
                    f"  Started: {results.get('start_time', 'Unknown')}",
                    f"  Completed: {results.get('end_time', 'Unknown')}",
                    ""
                ])
            
            # Success/failure status
            if results.get("hired_planners"):
                report_lines.extend([
                    "🎉 SUCCESS:",
                    f"  Successfully hired {len(results['hired_planners'])} wedding planner(s)!",
                    "  System achieved its primary objective.",
                    ""
                ])
            else:
                report_lines.extend([
                    "⚠️ INCOMPLETE:",
                    "  No planners were hired during this execution.",
                    "  Consider adjusting search criteria or extending timeline.",
                    ""
                ])
            
            report_lines.extend([
                "=" * 70,
                "Thank you for using the Wedding Planner Hiring System!"
            ])
            
            # Print and save report
            final_report = "\n".join(report_lines)
            print(f"\n{final_report}\n")
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = Config.DATA_DIR / f"final_report_{timestamp}.txt"
            with open(report_file, 'w') as f:
                f.write(final_report)
            
            logger.info(f"Final report saved to: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")

async def run_dashboard_only():
    """Run only the monitoring dashboard"""
    logger.info("📊 Starting Monitoring Dashboard")
    
    dashboard = MonitoringDashboard()
    
    try:
        # Generate initial report
        report = dashboard.generate_dashboard_report()
        print(f"\n{report}\n")
        
        # Start continuous monitoring
        dashboard.start_monitoring(interval_seconds=30)
        
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Dashboard failed: {e}")

async def run_cost_report():
    """Generate and display cost report"""
    logger.info("💰 Generating Cost Report")
    
    cost_tracker = CostTracker()
    report = cost_tracker.get_cost_report()
    
    print(f"\n{report}\n")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Config.DATA_DIR / f"cost_report_{timestamp}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Cost report saved to: {report_file}")

async def run_health_check():
    """Run system health check"""
    logger.info("🏥 Running System Health Check")
    
    dashboard = MonitoringDashboard()
    health = dashboard.get_health_check()
    
    status_emoji = {
        "healthy": "✅",
        "warning": "⚠️", 
        "critical": "❌",
        "error": "💥"
    }.get(health["status"], "❓")
    
    print(f"\n{status_emoji} SYSTEM HEALTH: {health['status'].upper()}")
    print(f"Health Score: {health['health_score']:.1f}/100")
    
    if health.get("issues"):
        print("\nIssues Found:")
        for issue in health["issues"]:
            print(f"  • {issue}")
    
    print(f"\nUptime: {health.get('uptime_hours', 0):.1f} hours")
    print(f"Progress: {health.get('total_progress', 0):.1f}%")
    print(f"Budget Used: {health.get('budget_used_percent', 0):.1f}%")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Wedding Planner Hiring System")
    parser.add_argument("--mode", choices=["full", "dashboard", "cost-report", "health-check"], 
                       default="full", help="Execution mode")
    parser.add_argument("--no-monitoring", action="store_true", 
                       help="Disable monitoring dashboard during full execution")
    parser.add_argument("--dry-run", action="store_true",
                       help="Perform a dry run without making actual API calls")
    
    args = parser.parse_args()
    
    # Check credentials
    try:
        creds_manager = CredentialsManager()
        credentials = creds_manager.decrypt_credentials()
        if not credentials:
            logger.error("No credentials found. Please run: python scripts/setup.py")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Credential check failed: {e}")
        logger.error("Please run: python scripts/setup.py")
        sys.exit(1)
    
    # Set dry run mode
    if args.dry_run:
        os.environ["DRY_RUN"] = "true"
        logger.info("🧪 Running in DRY RUN mode - no actual API calls will be made")
    
    # Execute based on mode
    try:
        if args.mode == "full":
            runner = SystemRunner()
            monitoring = not args.no_monitoring
            asyncio.run(runner.run_complete_workflow(monitoring=monitoring))
        
        elif args.mode == "dashboard":
            asyncio.run(run_dashboard_only())
        
        elif args.mode == "cost-report":
            asyncio.run(run_cost_report())
        
        elif args.mode == "health-check":
            asyncio.run(run_health_check())
    
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()