#!/usr/bin/env python3
"""
Management utilities for the Wedding Planner Hiring System
"""
import os
import sys
import argparse
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.monitoring.cost_tracker import CostTracker
from src.monitoring.dashboard import MonitoringDashboard
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger

logger = setup_logger("management")

class SystemManager:
    """System management utilities"""
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.cost_tracker = CostTracker()
        self.dashboard = MonitoringDashboard()
    
    def backup_data(self, backup_dir: Path = None) -> Path:
        """Create backup of all system data"""
        if backup_dir is None:
            backup_dir = project_root / "backups"
        
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        logger.info(f"Creating backup at: {backup_path}")
        
        try:
            # Export Airtable data
            self._export_airtable_data(backup_path)
            
            # Export cost data
            self._export_cost_data(backup_path)
            
            # Export metrics data
            self._export_metrics_data(backup_path)
            
            # Export logs
            self._export_logs(backup_path)
            
            # Create backup manifest
            self._create_backup_manifest(backup_path)
            
            logger.info(f"✅ Backup completed: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def _export_airtable_data(self, backup_path: Path):
        """Export Airtable data to CSV files"""
        airtable_dir = backup_path / "airtable"
        airtable_dir.mkdir(exist_ok=True)
        
        tables = ["planners", "communications", "calls", "logs"]
        
        for table_name in tables:
            try:
                table = getattr(self.airtable, f"{table_name}_table")
                records = table.all()
                
                csv_file = airtable_dir / f"{table_name}.csv"
                
                if records:
                    fieldnames = set()
                    for record in records:
                        fieldnames.update(record["fields"].keys())
                    
                    with open(csv_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                        writer.writeheader()
                        
                        for record in records:
                            row = record["fields"]
                            row["airtable_id"] = record["id"]
                            writer.writerow(row)
                    
                    logger.info(f"Exported {len(records)} {table_name} records")
                
            except Exception as e:
                logger.error(f"Failed to export {table_name}: {e}")
    
    def _export_cost_data(self, backup_path: Path):
        """Export cost tracking data"""
        try:
            cost_file = backup_path / "costs.csv"
            self.cost_tracker.export_costs(cost_file)
            logger.info("Cost data exported")
        except Exception as e:
            logger.error(f"Failed to export cost data: {e}")
    
    def _export_metrics_data(self, backup_path: Path):
        """Export metrics snapshots"""
        try:
            metrics_file = Config.DATA_DIR / "metrics.json"
            if metrics_file.exists():
                backup_metrics = backup_path / "metrics.json"
                backup_metrics.write_text(metrics_file.read_text())
                logger.info("Metrics data exported")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def _export_logs(self, backup_path: Path):
        """Export log files"""
        try:
            logs_dir = backup_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            for log_file in Config.LOGS_DIR.glob("*.log"):
                backup_log = logs_dir / log_file.name
                backup_log.write_text(log_file.read_text())
            
            logger.info("Log files exported")
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
    
    def _create_backup_manifest(self, backup_path: Path):
        """Create backup manifest with metadata"""
        manifest = {
            "backup_timestamp": datetime.now().isoformat(),
            "system_version": "1.0.0",
            "backup_type": "full",
            "files_included": [],
            "table_counts": {}
        }
        
        # Count files
        for file_path in backup_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(backup_path)
                manifest["files_included"].append(str(rel_path))
        
        # Get table counts
        try:
            stats = self.airtable.get_system_stats()
            manifest["table_counts"] = stats.get("planner_status_counts", {})
            manifest["total_planners"] = stats.get("total_planners", 0)
        except Exception as e:
            logger.warning(f"Could not get table counts: {e}")
        
        # Save manifest
        manifest_file = backup_path / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        logger.info(f"Cleaning up data older than {cutoff_date.strftime('%Y-%m-%d')}")
        
        cleaned_items = 0
        
        try:
            # Clean old log files
            for log_file in Config.LOGS_DIR.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    cleaned_items += 1
                    logger.info(f"Deleted old log: {log_file.name}")
            
            # Clean old backup files
            backup_dir = project_root / "backups"
            if backup_dir.exists():
                for backup_item in backup_dir.iterdir():
                    if backup_item.stat().st_mtime < cutoff_date.timestamp():
                        if backup_item.is_dir():
                            import shutil
                            shutil.rmtree(backup_item)
                        else:
                            backup_item.unlink()
                        cleaned_items += 1
                        logger.info(f"Deleted old backup: {backup_item.name}")
            
            # Clean old export files
            data_dir = Config.DATA_DIR
            for data_file in data_dir.glob("*_export_*.csv"):
                if data_file.stat().st_mtime < cutoff_date.timestamp():
                    data_file.unlink()
                    cleaned_items += 1
                    logger.info(f"Deleted old export: {data_file.name}")
            
            logger.info(f"✅ Cleanup completed: {cleaned_items} items removed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise
    
    def reset_system(self, confirm: bool = False):
        """Reset the system to initial state (WARNING: Deletes all data)"""
        if not confirm:
            logger.error("System reset requires confirmation. Use --confirm flag.")
            return False
        
        logger.warning("🚨 RESETTING SYSTEM - ALL DATA WILL BE DELETED")
        
        try:
            # Create final backup before reset
            logger.info("Creating final backup before reset...")
            backup_path = self.backup_data()
            
            # Clear Airtable data (would need to be implemented based on requirements)
            logger.info("Clearing database data...")
            # Note: Actual Airtable deletion would need specific implementation
            
            # Clear local data
            logger.info("Clearing local data...")
            
            # Clear cost data
            cost_file = Config.DATA_DIR / "costs.json"
            if cost_file.exists():
                cost_file.unlink()
            
            # Clear metrics data
            metrics_file = Config.DATA_DIR / "metrics.json"
            if metrics_file.exists():
                metrics_file.unlink()
            
            # Clear logs
            for log_file in Config.LOGS_DIR.glob("*.log"):
                log_file.unlink()
            
            logger.info(f"✅ System reset completed. Final backup saved at: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"System reset failed: {e}")
            return False
    
    def export_results(self, format: str = "json", output_file: Path = None):
        """Export system results in specified format"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = project_root / "exports" / f"results_{timestamp}.{format}"
        
        output_file.parent.mkdir(exist_ok=True)
        
        logger.info(f"Exporting results to: {output_file}")
        
        try:
            # Gather all system data
            stats = self.airtable.get_system_stats()
            budget_status = self.cost_tracker.get_budget_status()
            
            # Get shortlisted and hired planners
            shortlisted = self.airtable.get_shortlisted_planners()
            hired = self.airtable.get_planners_by_status("hired")
            
            results = {
                "export_timestamp": datetime.now().isoformat(),
                "system_stats": stats,
                "budget_status": {
                    "total_spent": budget_status.total_spent,
                    "monthly_limit": budget_status.monthly_limit,
                    "percentage_used": budget_status.percentage_used,
                    "remaining_budget": budget_status.remaining_budget
                },
                "shortlisted_planners": shortlisted,
                "hired_planners": hired,
                "success_metrics": {
                    "planners_discovered": stats.get("total_planners", 0),
                    "shortlist_size": len(shortlisted),
                    "hired_count": len(hired),
                    "success_rate": len(hired) / len(shortlisted) * 100 if shortlisted else 0
                }
            }
            
            if format == "json":
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            
            elif format == "csv":
                # Export planners data as CSV
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write summary
                    writer.writerow(["Wedding Planner Hiring System Results"])
                    writer.writerow([f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow([])
                    
                    # Write metrics
                    writer.writerow(["SUMMARY METRICS"])
                    writer.writerow(["Metric", "Value"])
                    writer.writerow(["Total Planners Discovered", stats.get("total_planners", 0)])
                    writer.writerow(["Shortlisted", len(shortlisted)])
                    writer.writerow(["Hired", len(hired)])
                    writer.writerow(["Budget Spent", f"${budget_status.total_spent:.2f}"])
                    writer.writerow([])
                    
                    # Write planner details
                    if shortlisted:
                        writer.writerow(["SHORTLISTED PLANNERS"])
                        headers = ["Name", "Business", "Location", "Score", "Source", "Contact"]
                        writer.writerow(headers)
                        
                        for planner in shortlisted:
                            row = [
                                planner.get("name", ""),
                                planner.get("business_name", ""),
                                planner.get("location", ""),
                                planner.get("total_score", ""),
                                planner.get("source", ""),
                                planner.get("email", "")
                            ]
                            writer.writerow(row)
            
            logger.info(f"✅ Results exported to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

def main():
    """Main management interface"""
    parser = argparse.ArgumentParser(description="Wedding Planner Hiring System Management")
    subparsers = parser.add_subparsers(dest="command", help="Management commands")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create system backup")
    backup_parser.add_argument("--output", type=Path, help="Backup output directory")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old data")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Delete data older than N days")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset system (DANGEROUS)")
    reset_parser.add_argument("--confirm", action="store_true", help="Confirm system reset")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export system results")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    export_parser.add_argument("--output", type=Path, help="Output file path")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = SystemManager()
        
        if args.command == "backup":
            backup_path = manager.backup_data(args.output)
            print(f"✅ Backup created: {backup_path}")
        
        elif args.command == "cleanup":
            manager.cleanup_old_data(args.days)
            print(f"✅ Cleanup completed (older than {args.days} days)")
        
        elif args.command == "reset":
            success = manager.reset_system(args.confirm)
            if success:
                print("✅ System reset completed")
            else:
                print("❌ System reset failed or cancelled")
        
        elif args.command == "export":
            output_file = manager.export_results(args.format, args.output)
            print(f"✅ Results exported: {output_file}")
        
        elif args.command == "status":
            stats = manager.airtable.get_system_stats()
            budget = manager.cost_tracker.get_budget_status()
            
            print("📊 SYSTEM STATUS")
            print("=" * 40)
            print(f"Total Planners: {stats.get('total_planners', 0)}")
            print(f"Shortlisted: {stats.get('planner_status_counts', {}).get('shortlisted', 0)}")
            print(f"Contacted: {stats.get('planner_status_counts', {}).get('contacted', 0)}")
            print(f"Hired: {stats.get('planner_status_counts', {}).get('hired', 0)}")
            print(f"Budget Used: ${budget.total_spent:.2f} / ${budget.monthly_limit:.2f} ({budget.percentage_used:.1f}%)")
    
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()