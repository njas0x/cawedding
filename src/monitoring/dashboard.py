"""
Monitoring dashboard for the wedding planner hiring system
"""
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import psutil
from pathlib import Path

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.monitoring.cost_tracker import CostTracker
from src.orchestrator import WeddingPlannerOrchestrator
from src.utils.logger import setup_logger

logger = setup_logger("dashboard")

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    active_processes: int
    uptime_seconds: float

@dataclass
class AgentMetrics:
    """Individual agent performance metrics"""
    agent_name: str
    tasks_completed: int
    success_rate: float
    average_execution_time: float
    errors_count: int
    last_activity: Optional[datetime]
    status: str  # active, idle, error, completed

@dataclass
class WorkflowMetrics:
    """Overall workflow progress metrics"""
    current_phase: str
    phase_progress: float  # 0-100%
    total_progress: float  # 0-100%
    estimated_completion: Optional[datetime]
    planners_discovered: int
    planners_shortlisted: int
    planners_contacted: int
    planners_responding: int
    calls_scheduled: int
    calls_completed: int
    planners_hired: int

class MonitoringDashboard:
    """Real-time monitoring dashboard for the wedding planner hiring system"""
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.cost_tracker = CostTracker()
        self.start_time = datetime.now()
        self.metrics_file = Config.DATA_DIR / "metrics.json"
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        Config.DATA_DIR.mkdir(exist_ok=True)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage_percent=psutil.disk_usage('/').percent,
            active_processes=len(psutil.pids()),
            uptime_seconds=(datetime.now() - self.start_time).total_seconds()
        )
    
    def get_agent_metrics(self) -> List[AgentMetrics]:
        """Get metrics for all agents"""
        metrics = []
        
        # Get agent activity from logs
        try:
            # Query Airtable logs for agent activity
            logs = self.airtable.logs_table.all(
                max_records=1000,
                sort=["-timestamp"]
            )
            
            agent_data = {}
            
            for log in logs:
                fields = log["fields"]
                agent_name = fields.get("agent_name", "unknown")
                
                if agent_name not in agent_data:
                    agent_data[agent_name] = {
                        "tasks_completed": 0,
                        "errors": 0,
                        "execution_times": [],
                        "last_activity": None,
                        "total_actions": 0
                    }
                
                agent_data[agent_name]["total_actions"] += 1
                
                if fields.get("success", True):
                    agent_data[agent_name]["tasks_completed"] += 1
                else:
                    agent_data[agent_name]["errors"] += 1
                
                exec_time = fields.get("execution_time_seconds")
                if exec_time:
                    agent_data[agent_name]["execution_times"].append(exec_time)
                
                # Update last activity
                timestamp_str = fields.get("timestamp")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if (not agent_data[agent_name]["last_activity"] or 
                        timestamp > agent_data[agent_name]["last_activity"]):
                        agent_data[agent_name]["last_activity"] = timestamp
            
            # Convert to AgentMetrics
            for agent_name, data in agent_data.items():
                success_rate = (data["tasks_completed"] / data["total_actions"] * 100) if data["total_actions"] > 0 else 0
                avg_exec_time = sum(data["execution_times"]) / len(data["execution_times"]) if data["execution_times"] else 0
                
                # Determine status
                if data["last_activity"]:
                    time_since_activity = (datetime.now() - data["last_activity"]).total_seconds()
                    if time_since_activity < 300:  # 5 minutes
                        status = "active"
                    elif time_since_activity < 3600:  # 1 hour
                        status = "idle"
                    else:
                        status = "inactive"
                else:
                    status = "unknown"
                
                if data["errors"] > data["tasks_completed"]:
                    status = "error"
                
                metrics.append(AgentMetrics(
                    agent_name=agent_name,
                    tasks_completed=data["tasks_completed"],
                    success_rate=success_rate,
                    average_execution_time=avg_exec_time,
                    errors_count=data["errors"],
                    last_activity=data["last_activity"],
                    status=status
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get agent metrics: {e}")
            return []
    
    def get_workflow_metrics(self) -> WorkflowMetrics:
        """Get workflow progress metrics"""
        try:
            # Get planner counts by status
            stats = self.airtable.get_system_stats()
            status_counts = stats.get("planner_status_counts", {})
            
            # Calculate phase progress
            discovered = status_counts.get("discovered", 0) + status_counts.get("analyzed", 0) + status_counts.get("shortlisted", 0)
            shortlisted = status_counts.get("shortlisted", 0)
            contacted = status_counts.get("contacted", 0)
            responding = status_counts.get("responded", 0)
            calls_scheduled = status_counts.get("call_scheduled", 0)
            calls_completed = status_counts.get("call_completed", 0)
            hired = status_counts.get("hired", 0)
            
            # Determine current phase and progress
            current_phase = "research"
            phase_progress = 0.0
            total_progress = 0.0
            
            if discovered >= 20:
                if shortlisted >= 5:
                    if contacted >= shortlisted:
                        if responding >= 3:
                            if calls_completed >= 3:
                                if hired >= 1:
                                    current_phase = "completed"
                                    phase_progress = 100.0
                                    total_progress = 100.0
                                else:
                                    current_phase = "decision"
                                    phase_progress = (calls_completed / 3) * 100
                                    total_progress = 85 + (phase_progress * 0.15)
                            else:
                                current_phase = "calls"
                                phase_progress = (calls_completed / 3) * 100
                                total_progress = 60 + (phase_progress * 0.25)
                        else:
                            current_phase = "outreach"
                            phase_progress = (responding / 3) * 100
                            total_progress = 30 + (phase_progress * 0.30)
                    else:
                        current_phase = "outreach"
                        phase_progress = (contacted / shortlisted) * 100
                        total_progress = 30 + (phase_progress * 0.30)
                else:
                    current_phase = "research"
                    phase_progress = 50 + (shortlisted / 5) * 50
                    total_progress = phase_progress * 0.30
            else:
                current_phase = "research"
                phase_progress = (discovered / 20) * 50
                total_progress = phase_progress * 0.30
            
            # Estimate completion time
            estimated_completion = None
            if total_progress > 0:
                time_elapsed = (datetime.now() - self.start_time).total_seconds()
                estimated_total_time = time_elapsed / (total_progress / 100)
                estimated_completion = self.start_time + timedelta(seconds=estimated_total_time)
            
            return WorkflowMetrics(
                current_phase=current_phase,
                phase_progress=phase_progress,
                total_progress=total_progress,
                estimated_completion=estimated_completion,
                planners_discovered=discovered,
                planners_shortlisted=shortlisted,
                planners_contacted=contacted,
                planners_responding=responding,
                calls_scheduled=calls_scheduled,
                calls_completed=calls_completed,
                planners_hired=hired
            )
            
        except Exception as e:
            logger.error(f"Failed to get workflow metrics: {e}")
            return WorkflowMetrics(
                current_phase="unknown",
                phase_progress=0.0,
                total_progress=0.0,
                estimated_completion=None,
                planners_discovered=0,
                planners_shortlisted=0,
                planners_contacted=0,
                planners_responding=0,
                calls_scheduled=0,
                calls_completed=0,
                planners_hired=0
            )
    
    def generate_dashboard_report(self) -> str:
        """Generate a comprehensive dashboard report"""
        system_metrics = self.get_system_metrics()
        agent_metrics = self.get_agent_metrics()
        workflow_metrics = self.get_workflow_metrics()
        budget_status = self.cost_tracker.get_budget_status()
        
        # Build report
        report_lines = [
            "🎯 WEDDING PLANNER HIRING SYSTEM - DASHBOARD",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"⏱️ Uptime: {system_metrics.uptime_seconds / 3600:.1f} hours",
            "=" * 60,
            "",
            "📊 WORKFLOW PROGRESS:",
            f"  Current Phase: {workflow_metrics.current_phase.upper()}",
            f"  Phase Progress: {workflow_metrics.phase_progress:.1f}%",
            f"  Total Progress: {workflow_metrics.total_progress:.1f}%",
        ]
        
        if workflow_metrics.estimated_completion:
            report_lines.append(f"  Est. Completion: {workflow_metrics.estimated_completion.strftime('%Y-%m-%d %H:%M')}")
        
        report_lines.extend([
            "",
            "👥 PLANNER PIPELINE:",
            f"  📊 Discovered: {workflow_metrics.planners_discovered}",
            f"  ⭐ Shortlisted: {workflow_metrics.planners_shortlisted}",
            f"  📞 Contacted: {workflow_metrics.planners_contacted}",
            f"  💬 Responding: {workflow_metrics.planners_responding}",
            f"  📅 Calls Scheduled: {workflow_metrics.calls_scheduled}",
            f"  ✅ Calls Completed: {workflow_metrics.calls_completed}",
            f"  🎉 Hired: {workflow_metrics.planners_hired}",
            "",
            "💰 BUDGET STATUS:",
            f"  Spent: ${budget_status.total_spent:.2f} / ${budget_status.monthly_limit:.2f} ({budget_status.percentage_used:.1f}%)",
            f"  Remaining: ${budget_status.remaining_budget:.2f}",
            f"  Daily Burn: ${budget_status.daily_burn_rate:.2f}",
        ])
        
        # Budget alerts
        if budget_status.alerts:
            report_lines.append("  🚨 ALERTS:")
            for alert in budget_status.alerts:
                report_lines.append(f"    • {alert}")
        
        report_lines.extend([
            "",
            "🤖 AGENT STATUS:"
        ])
        
        # Agent status
        if agent_metrics:
            for agent in agent_metrics:
                status_emoji = {
                    "active": "🟢",
                    "idle": "🟡", 
                    "inactive": "⚪",
                    "error": "🔴",
                    "unknown": "⚫"
                }.get(agent.status, "⚫")
                
                report_lines.append(f"  {status_emoji} {agent.agent_name.upper()}:")
                report_lines.append(f"    Tasks: {agent.tasks_completed} | Success: {agent.success_rate:.1f}% | Errors: {agent.errors_count}")
                if agent.last_activity:
                    time_ago = (datetime.now() - agent.last_activity).total_seconds() / 60
                    report_lines.append(f"    Last Active: {time_ago:.0f}m ago")
        else:
            report_lines.append("  No agent activity detected")
        
        report_lines.extend([
            "",
            "💻 SYSTEM PERFORMANCE:",
            f"  CPU: {system_metrics.cpu_percent:.1f}% | Memory: {system_metrics.memory_percent:.1f}% | Disk: {system_metrics.disk_usage_percent:.1f}%",
            f"  Processes: {system_metrics.active_processes}",
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def save_metrics_snapshot(self) -> None:
        """Save current metrics snapshot to file"""
        try:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": asdict(self.get_system_metrics()),
                "agent_metrics": [asdict(agent) for agent in self.get_agent_metrics()],
                "workflow_metrics": asdict(self.get_workflow_metrics()),
                "budget_status": asdict(self.cost_tracker.get_budget_status())
            }
            
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            def clean_dict(d):
                if isinstance(d, dict):
                    return {k: clean_dict(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [clean_dict(item) for item in d]
                else:
                    return convert_datetime(d)
            
            cleaned_snapshot = clean_dict(snapshot)
            
            with open(self.metrics_file, 'w') as f:
                json.dump(cleaned_snapshot, f, indent=2)
                
            logger.info("Metrics snapshot saved")
            
        except Exception as e:
            logger.error(f"Failed to save metrics snapshot: {e}")
    
    def start_monitoring(self, interval_seconds: int = 60) -> None:
        """Start continuous monitoring with specified interval"""
        logger.info(f"Starting dashboard monitoring (interval: {interval_seconds}s)")
        
        try:
            while True:
                # Generate and log dashboard report
                report = self.generate_dashboard_report()
                print("\n" + report + "\n")
                
                # Save metrics snapshot
                self.save_metrics_snapshot()
                
                # Check for critical alerts
                budget_status = self.cost_tracker.get_budget_status()
                for alert in budget_status.alerts:
                    if "CRITICAL" in alert:
                        logger.critical(alert)
                        # In production, this might trigger notifications
                
                # Wait for next interval
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
    
    def get_health_check(self) -> Dict[str, Any]:
        """Get system health check status"""
        try:
            system_metrics = self.get_system_metrics()
            workflow_metrics = self.get_workflow_metrics()
            budget_status = self.cost_tracker.get_budget_status()
            
            # Determine overall health
            health_score = 100.0
            issues = []
            
            # System performance checks
            if system_metrics.cpu_percent > 80:
                health_score -= 20
                issues.append("High CPU usage")
            
            if system_metrics.memory_percent > 80:
                health_score -= 20
                issues.append("High memory usage")
            
            # Budget checks
            if budget_status.is_over_budget():
                health_score -= 30
                issues.append("Budget exceeded")
            elif budget_status.is_approaching_limit(0.9):
                health_score -= 15
                issues.append("Approaching budget limit")
            
            # Workflow checks
            if workflow_metrics.total_progress == 0:
                health_score -= 25
                issues.append("No workflow progress")
            
            # Determine status
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "status": status,
                "health_score": health_score,
                "issues": issues,
                "timestamp": datetime.now().isoformat(),
                "uptime_hours": system_metrics.uptime_seconds / 3600,
                "total_progress": workflow_metrics.total_progress,
                "budget_used_percent": budget_status.percentage_used
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "health_score": 0.0,
                "issues": [f"Health check failed: {str(e)}"],
                "timestamp": datetime.now().isoformat()
            }