"""
Cost tracking and budget monitoring for the wedding planner hiring system
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.utils.logger import setup_logger

logger = setup_logger("cost_tracker")

@dataclass
class CostEntry:
    """Individual cost entry"""
    timestamp: datetime
    service: str
    operation: str
    cost: float
    details: Optional[str] = None
    agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "service": self.service,
            "operation": self.operation,
            "cost": self.cost,
            "details": self.details,
            "agent": self.agent
        }

@dataclass
class BudgetStatus:
    """Current budget status"""
    total_spent: float
    monthly_limit: float
    percentage_used: float
    remaining_budget: float
    daily_burn_rate: float
    projected_monthly_spend: float
    alerts: List[str]
    
    def is_over_budget(self) -> bool:
        return self.total_spent > self.monthly_limit
    
    def is_approaching_limit(self, threshold: float = 0.8) -> bool:
        return self.percentage_used > threshold

class CostTracker:
    """Tracks and monitors API costs and system spending"""
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.cost_file = Config.DATA_DIR / "costs.json"
        self._ensure_data_dir()
        self._load_costs()
        
        # API cost rates (per unit)
        self.cost_rates = {
            "openai": {
                "gpt-4o": {"input": 0.0025, "output": 0.010},  # per 1K tokens
                "gpt-4o-mini": {"input": 0.00015, "output": 0.0006}
            },
            "apify": {
                "instagram_scraper": 0.001,  # per result
                "general_scraper": 0.0005
            },
            "twilio": {
                "sms": 0.0075,  # per SMS
                "phone": 0.013   # per minute
            },
            "sendgrid": {
                "email": 0.0006  # per email
            },
            "airtable": {
                "api_call": 0.0001  # minimal cost per API call
            }
        }
        
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        Config.DATA_DIR.mkdir(exist_ok=True)
        
    def _load_costs(self):
        """Load existing cost data"""
        self.costs = []
        if self.cost_file.exists():
            try:
                with open(self.cost_file, 'r') as f:
                    cost_data = json.load(f)
                    for entry in cost_data:
                        entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
                        self.costs.append(CostEntry(**entry))
            except Exception as e:
                logger.error(f"Failed to load cost data: {e}")
                self.costs = []
    
    def _save_costs(self):
        """Save cost data to file"""
        try:
            cost_data = [entry.to_dict() for entry in self.costs]
            with open(self.cost_file, 'w') as f:
                json.dump(cost_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cost data: {e}")
    
    def record_cost(self, service: str, operation: str, cost: float, 
                   details: str = None, agent: str = None) -> None:
        """Record a cost entry"""
        entry = CostEntry(
            timestamp=datetime.now(),
            service=service,
            operation=operation,
            cost=cost,
            details=details,
            agent=agent
        )
        
        self.costs.append(entry)
        self._save_costs()
        
        # Log to Airtable
        try:
            self.airtable.log_action(
                agent_name=agent or "system",
                action=f"{service}_{operation}",
                details=details,
                cost=cost
            )
        except Exception as e:
            logger.error(f"Failed to log cost to Airtable: {e}")
        
        logger.info(f"Cost recorded: {service}.{operation} = ${cost:.4f}")
        
        # Check for budget alerts
        self._check_budget_alerts()
    
    def record_openai_cost(self, model: str, input_tokens: int, output_tokens: int, agent: str = None) -> float:
        """Record OpenAI API cost"""
        rates = self.cost_rates["openai"].get(model, self.cost_rates["openai"]["gpt-4o"])
        
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        total_cost = input_cost + output_cost
        
        self.record_cost(
            service="openai",
            operation=f"completion_{model}",
            cost=total_cost,
            details=f"Input: {input_tokens}, Output: {output_tokens}",
            agent=agent
        )
        
        return total_cost
    
    def record_apify_cost(self, scraper_type: str, results_count: int, agent: str = None) -> float:
        """Record Apify scraping cost"""
        rate = self.cost_rates["apify"].get(scraper_type, self.cost_rates["apify"]["general_scraper"])
        total_cost = results_count * rate
        
        self.record_cost(
            service="apify",
            operation=scraper_type,
            cost=total_cost,
            details=f"Results: {results_count}",
            agent=agent
        )
        
        return total_cost
    
    def record_communication_cost(self, comm_type: str, count: int, agent: str = None) -> float:
        """Record communication cost (SMS/Email)"""
        if comm_type == "sms":
            rate = self.cost_rates["twilio"]["sms"]
            service = "twilio"
        elif comm_type == "email":
            rate = self.cost_rates["sendgrid"]["email"]
            service = "sendgrid"
        else:
            logger.warning(f"Unknown communication type: {comm_type}")
            return 0.0
        
        total_cost = count * rate
        
        self.record_cost(
            service=service,
            operation=comm_type,
            cost=total_cost,
            details=f"Count: {count}",
            agent=agent
        )
        
        return total_cost
    
    def get_budget_status(self) -> BudgetStatus:
        """Get current budget status"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate monthly spending
        monthly_costs = [
            cost for cost in self.costs 
            if cost.timestamp >= month_start
        ]
        
        total_spent = sum(cost.cost for cost in monthly_costs)
        monthly_limit = Config.MONTHLY_BUDGET_LIMIT
        percentage_used = (total_spent / monthly_limit) * 100 if monthly_limit > 0 else 0
        remaining_budget = max(0, monthly_limit - total_spent)
        
        # Calculate daily burn rate
        days_in_month = (now - month_start).days + 1
        daily_burn_rate = total_spent / days_in_month if days_in_month > 0 else 0
        
        # Project monthly spend
        days_remaining = 30 - days_in_month
        projected_monthly_spend = total_spent + (daily_burn_rate * days_remaining)
        
        # Generate alerts
        alerts = []
        if total_spent > monthly_limit:
            alerts.append("CRITICAL: Monthly budget exceeded!")
        elif percentage_used > 90:
            alerts.append("WARNING: Over 90% of monthly budget used")
        elif percentage_used > 75:
            alerts.append("CAUTION: Over 75% of monthly budget used")
        
        if projected_monthly_spend > monthly_limit:
            alerts.append(f"PROJECTION: Current burn rate will exceed budget by ${projected_monthly_spend - monthly_limit:.2f}")
        
        return BudgetStatus(
            total_spent=total_spent,
            monthly_limit=monthly_limit,
            percentage_used=percentage_used,
            remaining_budget=remaining_budget,
            daily_burn_rate=daily_burn_rate,
            projected_monthly_spend=projected_monthly_spend,
            alerts=alerts
        )
    
    def get_cost_breakdown(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed cost breakdown for the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_costs = [cost for cost in self.costs if cost.timestamp >= cutoff]
        
        # Group by service
        service_totals = {}
        operation_totals = {}
        agent_totals = {}
        daily_totals = {}
        
        for cost in recent_costs:
            # Service totals
            service_totals[cost.service] = service_totals.get(cost.service, 0) + cost.cost
            
            # Operation totals
            op_key = f"{cost.service}.{cost.operation}"
            operation_totals[op_key] = operation_totals.get(op_key, 0) + cost.cost
            
            # Agent totals
            if cost.agent:
                agent_totals[cost.agent] = agent_totals.get(cost.agent, 0) + cost.cost
            
            # Daily totals
            day_key = cost.timestamp.strftime("%Y-%m-%d")
            daily_totals[day_key] = daily_totals.get(day_key, 0) + cost.cost
        
        return {
            "period_days": days,
            "total_costs": sum(cost.cost for cost in recent_costs),
            "service_breakdown": dict(sorted(service_totals.items(), key=lambda x: x[1], reverse=True)),
            "operation_breakdown": dict(sorted(operation_totals.items(), key=lambda x: x[1], reverse=True)),
            "agent_breakdown": dict(sorted(agent_totals.items(), key=lambda x: x[1], reverse=True)),
            "daily_breakdown": dict(sorted(daily_totals.items())),
            "cost_entries": len(recent_costs)
        }
    
    def get_cost_report(self) -> str:
        """Generate a formatted cost report"""
        budget_status = self.get_budget_status()
        breakdown = self.get_cost_breakdown(30)
        
        report_lines = [
            "=== WEDDING PLANNER HIRING SYSTEM - COST REPORT ===",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "BUDGET STATUS:",
            f"  Monthly Limit: ${budget_status.monthly_limit:.2f}",
            f"  Total Spent: ${budget_status.total_spent:.2f} ({budget_status.percentage_used:.1f}%)",
            f"  Remaining: ${budget_status.remaining_budget:.2f}",
            f"  Daily Burn Rate: ${budget_status.daily_burn_rate:.2f}",
            f"  Projected Monthly: ${budget_status.projected_monthly_spend:.2f}",
            ""
        ]
        
        # Alerts
        if budget_status.alerts:
            report_lines.append("ALERTS:")
            for alert in budget_status.alerts:
                report_lines.append(f"  🚨 {alert}")
            report_lines.append("")
        
        # Service breakdown
        report_lines.append("SERVICE BREAKDOWN (Last 30 days):")
        for service, cost in breakdown["service_breakdown"].items():
            percentage = (cost / breakdown["total_costs"]) * 100 if breakdown["total_costs"] > 0 else 0
            report_lines.append(f"  {service.upper()}: ${cost:.2f} ({percentage:.1f}%)")
        
        report_lines.append("")
        
        # Top operations
        report_lines.append("TOP OPERATIONS (Last 30 days):")
        for i, (operation, cost) in enumerate(list(breakdown["operation_breakdown"].items())[:5]):
            report_lines.append(f"  {i+1}. {operation}: ${cost:.2f}")
        
        return "\n".join(report_lines)
    
    def _check_budget_alerts(self):
        """Check for budget alerts and log warnings"""
        budget_status = self.get_budget_status()
        
        for alert in budget_status.alerts:
            if "CRITICAL" in alert:
                logger.error(alert)
            elif "WARNING" in alert:
                logger.warning(alert)
            elif "CAUTION" in alert:
                logger.warning(alert)
            elif "PROJECTION" in alert:
                logger.info(alert)
    
    def export_costs(self, filepath: Optional[Path] = None) -> Path:
        """Export costs to CSV file"""
        import csv
        
        if filepath is None:
            filepath = Config.DATA_DIR / f"costs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ["timestamp", "service", "operation", "cost", "details", "agent"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for cost in self.costs:
                row = cost.to_dict()
                writer.writerow(row)
        
        logger.info(f"Costs exported to {filepath}")
        return filepath