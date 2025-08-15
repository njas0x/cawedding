"""
Wedding Planner Hiring System Orchestrator
Coordinates all agents using CrewAI framework
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time
import asyncio
from dataclasses import dataclass
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from src.config import Config
from src.agents.researcher_agent import ResearcherAgent
from src.agents.analyzer_agent import AnalyzerAgent  
from src.agents.outreach_agent import OutreachAgent, OutreachCampaign
from src.database.airtable_client import AirtableClient
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger, log_agent_action, log_human_gate

logger = setup_logger("orchestrator")

@dataclass
class WorkflowPhase:
    """Configuration for a workflow phase"""
    name: str
    duration_days: int
    agents: List[str]
    tasks: List[str]
    human_gates: List[str]
    success_criteria: Dict[str, Any]

@dataclass
class SystemStatus:
    """Current system status"""
    phase: str
    day: int
    total_planners: int
    shortlisted_planners: int
    contacted_planners: int
    responding_planners: int
    calls_scheduled: int
    calls_completed: int
    hired_planners: int
    cost_to_date: float
    next_action: str
    
class WeddingPlannerOrchestrator:
    """Main orchestrator for the wedding planner hiring system"""
    
    def __init__(self):
        self.creds_manager = CredentialsManager()
        self.airtable = AirtableClient()
        self._setup_llm()
        self._setup_agents()
        self._setup_workflow()
        self.start_time = datetime.now()
        
    def _setup_llm(self):
        """Setup OpenAI client for orchestration"""
        credentials = self.creds_manager.decrypt_credentials()
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=credentials.get("OPENAI_API_KEY"),
            temperature=0.1
        )
        logger.info("Orchestrator LLM initialized")
    
    def _setup_agents(self):
        """Initialize all agents"""
        self.researcher = ResearcherAgent()
        self.analyzer = AnalyzerAgent()
        self.outreach = OutreachAgent()
        
        # CrewAI agent definitions
        self.crew_researcher = Agent(
            role="Wedding Planner Researcher",
            goal="Discover and scrape data for 20-50 wedding planners specializing in multicultural Asian weddings",
            backstory="You are an expert at finding wedding vendors through social media and wedding directories, with deep knowledge of multicultural wedding requirements.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.crew_analyzer = Agent(
            role="Wedding Planner Analyst", 
            goal="Score and rank discovered planners based on multicultural fit, availability, and reviews to create a shortlist of 5-10 candidates",
            backstory="You are a wedding industry analyst who specializes in evaluating vendor suitability for cultural weddings and tight timelines.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        self.crew_outreach = Agent(
            role="Wedding Planner Outreach Coordinator",
            goal="Execute personalized outreach campaigns and coordinate responses to schedule intro calls with shortlisted planners",
            backstory="You are a communication expert who excels at professional vendor outreach and relationship building in the wedding industry.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        logger.info("All agents initialized")
    
    def _setup_workflow(self):
        """Setup workflow phases"""
        self.workflow_phases = {
            "research": WorkflowPhase(
                name="research",
                duration_days=4,
                agents=["researcher", "analyzer"],
                tasks=["scrape_planners", "analyze_planners", "generate_shortlist"],
                human_gates=["shortlist_approval"],
                success_criteria={
                    "min_planners_discovered": 20,
                    "min_shortlisted": 5,
                    "min_avg_score": 6.0
                }
            ),
            "outreach": WorkflowPhase(
                name="outreach", 
                duration_days=8,
                agents=["outreach"],
                tasks=["initial_outreach", "follow_up_cycle", "response_processing"],
                human_gates=["outreach_approval"],
                success_criteria={
                    "min_responses": 3,
                    "min_calls_scheduled": 3
                }
            ),
            "calls": WorkflowPhase(
                name="calls",
                duration_days=4,
                agents=["outreach"],
                tasks=["coordinate_calls", "process_call_results"],
                human_gates=["call_coordination"],
                success_criteria={
                    "min_calls_completed": 3,
                    "min_viable_candidates": 2
                }
            ),
            "decision": WorkflowPhase(
                name="decision",
                duration_days=2,
                agents=["analyzer", "outreach"],
                tasks=["final_analysis", "generate_recommendations", "coordinate_hiring"],
                human_gates=["final_decision"],
                success_criteria={
                    "hired_planners": 1
                }
            )
        }
        
        self.current_phase = "research"
    
    async def run_complete_workflow(self) -> Dict[str, Any]:
        """Run the complete wedding planner hiring workflow"""
        logger.info("Starting complete wedding planner hiring workflow")
        
        workflow_results = {
            "start_time": self.start_time.isoformat(),
            "phases_completed": [],
            "total_cost": 0.0,
            "final_status": {},
            "hired_planners": []
        }
        
        try:
            for phase_name in ["research", "outreach", "calls", "decision"]:
                phase = self.workflow_phases[phase_name]
                self.current_phase = phase_name
                
                logger.info(f"Starting phase: {phase_name}")
                
                phase_results = await self._execute_phase(phase)
                workflow_results["phases_completed"].append({
                    "phase": phase_name,
                    "results": phase_results,
                    "completed_at": datetime.now().isoformat()
                })
                
                # Check if phase met success criteria
                if not self._validate_phase_success(phase, phase_results):
                    logger.error(f"Phase {phase_name} failed to meet success criteria")
                    workflow_results["failed_phase"] = phase_name
                    break
                
                # Update workflow results
                workflow_results["total_cost"] += phase_results.get("cost", 0.0)
                
                # Check cost limits
                if workflow_results["total_cost"] > Config.MONTHLY_BUDGET_LIMIT:
                    logger.error("Monthly budget limit exceeded")
                    workflow_results["budget_exceeded"] = True
                    break
            
            # Final status
            workflow_results["final_status"] = self.get_system_status()
            workflow_results["end_time"] = datetime.now().isoformat()
            workflow_results["total_duration"] = (datetime.now() - self.start_time).total_seconds()
            
            log_agent_action(
                logger, "orchestrator", "workflow_completed",
                {"phases": len(workflow_results["phases_completed"]), "cost": workflow_results["total_cost"]}
            )
            
            return workflow_results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            workflow_results["error"] = str(e)
            workflow_results["failed_at"] = datetime.now().isoformat()
            return workflow_results
    
    async def _execute_phase(self, phase: WorkflowPhase) -> Dict[str, Any]:
        """Execute a single workflow phase"""
        logger.info(f"Executing phase: {phase.name}")
        
        phase_results = {
            "start_time": datetime.now().isoformat(),
            "tasks_completed": [],
            "cost": 0.0,
            "errors": []
        }
        
        try:
            if phase.name == "research":
                results = await self._execute_research_phase()
            elif phase.name == "outreach":
                results = await self._execute_outreach_phase()
            elif phase.name == "calls":
                results = await self._execute_calls_phase()
            elif phase.name == "decision":
                results = await self._execute_decision_phase()
            else:
                raise ValueError(f"Unknown phase: {phase.name}")
            
            phase_results.update(results)
            phase_results["end_time"] = datetime.now().isoformat()
            
            return phase_results
            
        except Exception as e:
            logger.error(f"Phase {phase.name} execution failed: {e}")
            phase_results["error"] = str(e)
            phase_results["errors"].append(str(e))
            return phase_results
    
    async def _execute_research_phase(self) -> Dict[str, Any]:
        """Execute research phase"""
        logger.info("Executing research phase")
        
        results = {"tasks_completed": [], "cost": 0.0}
        
        try:
            # Task 1: Scrape planners
            logger.info("Task 1: Scraping wedding planners")
            planner_ids = self.researcher.run_research_phase(Config.TARGET_PLANNER_COUNT)
            
            results["tasks_completed"].append({
                "task": "scrape_planners",
                "status": "completed",
                "planners_discovered": len(planner_ids)
            })
            
            # Task 2: Analyze planners
            logger.info("Task 2: Analyzing and scoring planners")
            shortlist_ids = self.analyzer.run_analysis_phase()
            
            results["tasks_completed"].append({
                "task": "analyze_planners",
                "status": "completed", 
                "planners_analyzed": len(planner_ids),
                "shortlist_generated": len(shortlist_ids)
            })
            
            # Store results
            results["planners_discovered"] = len(planner_ids)
            results["shortlist_generated"] = len(shortlist_ids)
            results["shortlist_ids"] = shortlist_ids
            
            return results
            
        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            results["error"] = str(e)
            return results
    
    async def _execute_outreach_phase(self) -> Dict[str, Any]:
        """Execute outreach phase"""
        logger.info("Executing outreach phase")
        
        results = {"tasks_completed": [], "cost": 0.0}
        
        try:
            # Initial outreach campaign
            initial_campaign = OutreachCampaign(
                name="initial_outreach",
                template_name="initial_email",
                target_status="shortlisted",
                communication_type="email",
                batch_size=5,
                delay_between_batches=300,
                follow_up_delay_hours=48,
                max_follow_ups=2
            )
            
            outreach_results = self.outreach.run_outreach_campaign(initial_campaign)
            
            results["tasks_completed"].append({
                "task": "initial_outreach",
                "status": "completed",
                "messages_sent": outreach_results["sent"],
                "failures": outreach_results["failed"]
            })
            
            # Wait for responses (48 hours simulation)
            logger.info("Waiting for initial responses...")
            await asyncio.sleep(10)  # Simulated wait
            
            # Follow-up cycle
            follow_up_results = self.outreach.run_follow_up_cycle()
            
            results["tasks_completed"].append({
                "task": "follow_up_cycle",
                "status": "completed",
                "follow_ups_sent": follow_up_results["sent"]
            })
            
            # Process responses
            response_results = self.outreach.process_responses()
            
            results["tasks_completed"].append({
                "task": "process_responses",
                "status": "completed",
                "responses_processed": response_results["processed"]
            })
            
            # Store results
            results["total_contacted"] = outreach_results["sent"]
            results["total_follow_ups"] = follow_up_results["sent"]
            results["responses_received"] = response_results["processed"]
            
            return results
            
        except Exception as e:
            logger.error(f"Outreach phase failed: {e}")
            results["error"] = str(e)
            return results
    
    async def _execute_calls_phase(self) -> Dict[str, Any]:
        """Execute calls phase"""
        logger.info("Executing calls phase")
        
        results = {"tasks_completed": [], "cost": 0.0}
        
        try:
            # This phase is primarily human-driven
            # The system coordinates but humans conduct calls
            
            # Get responding planners
            responding_planners = self.airtable.get_planners_by_status("responded")
            
            log_human_gate(
                logger, "call_coordination",
                f"Ready to coordinate calls with {len(responding_planners)} responding planners"
            )
            
            results["tasks_completed"].append({
                "task": "coordinate_calls", 
                "status": "completed",
                "planners_for_calls": len(responding_planners)
            })
            
            # Simulate call completion
            results["calls_completed"] = min(len(responding_planners), 5)
            results["viable_candidates"] = min(results["calls_completed"], 3)
            
            return results
            
        except Exception as e:
            logger.error(f"Calls phase failed: {e}")
            results["error"] = str(e)
            return results
    
    async def _execute_decision_phase(self) -> Dict[str, Any]:
        """Execute decision phase"""
        logger.info("Executing decision phase")
        
        results = {"tasks_completed": [], "cost": 0.0}
        
        try:
            # Get call-completed planners
            call_completed = self.airtable.get_planners_by_status("call_completed")
            
            # Generate final recommendations
            log_human_gate(
                logger, "final_decision",
                f"Ready for final decision among {len(call_completed)} interviewed planners"
            )
            
            results["tasks_completed"].append({
                "task": "final_analysis",
                "status": "completed",
                "candidates_analyzed": len(call_completed)
            })
            
            # Simulate hiring decision
            if call_completed:
                # In production, this would be human-driven
                results["hired_planners"] = ["planner_1"]  # Simulated
                results["hiring_completed"] = True
            else:
                results["hired_planners"] = []
                results["hiring_completed"] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Decision phase failed: {e}")
            results["error"] = str(e)
            return results
    
    def _validate_phase_success(self, phase: WorkflowPhase, results: Dict[str, Any]) -> bool:
        """Validate that phase met success criteria"""
        if "error" in results:
            return False
        
        criteria = phase.success_criteria
        
        for criterion, threshold in criteria.items():
            if criterion == "min_planners_discovered":
                if results.get("planners_discovered", 0) < threshold:
                    logger.error(f"Failed criterion: {criterion} ({results.get('planners_discovered', 0)} < {threshold})")
                    return False
            elif criterion == "min_shortlisted":
                if results.get("shortlist_generated", 0) < threshold:
                    logger.error(f"Failed criterion: {criterion} ({results.get('shortlist_generated', 0)} < {threshold})")
                    return False
            elif criterion == "min_responses":
                if results.get("responses_received", 0) < threshold:
                    logger.error(f"Failed criterion: {criterion} ({results.get('responses_received', 0)} < {threshold})")
                    return False
            elif criterion == "min_calls_completed":
                if results.get("calls_completed", 0) < threshold:
                    logger.error(f"Failed criterion: {criterion} ({results.get('calls_completed', 0)} < {threshold})")
                    return False
            elif criterion == "hired_planners":
                if len(results.get("hired_planners", [])) < threshold:
                    logger.error(f"Failed criterion: {criterion} ({len(results.get('hired_planners', []))} < {threshold})")
                    return False
        
        return True
    
    def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        try:
            stats = self.airtable.get_system_stats()
            
            days_elapsed = (datetime.now() - self.start_time).days
            
            status = SystemStatus(
                phase=self.current_phase,
                day=days_elapsed,
                total_planners=stats.get("total_planners", 0),
                shortlisted_planners=stats.get("planner_status_counts", {}).get("shortlisted", 0),
                contacted_planners=stats.get("planner_status_counts", {}).get("contacted", 0),
                responding_planners=stats.get("planner_status_counts", {}).get("responded", 0),
                calls_scheduled=stats.get("planner_status_counts", {}).get("call_scheduled", 0),
                calls_completed=stats.get("planner_status_counts", {}).get("call_completed", 0),
                hired_planners=stats.get("planner_status_counts", {}).get("hired", 0),
                cost_to_date=self._calculate_cost_to_date(),
                next_action=self._determine_next_action(stats)
            )
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return SystemStatus(
                phase=self.current_phase,
                day=0,
                total_planners=0,
                shortlisted_planners=0,
                contacted_planners=0,
                responding_planners=0,
                calls_scheduled=0,
                calls_completed=0,
                hired_planners=0,
                cost_to_date=0.0,
                next_action="Check system status"
            )
    
    def _calculate_cost_to_date(self) -> float:
        """Calculate total cost incurred so far"""
        # This would pull from actual API usage logs
        # For now, return estimated cost
        days_elapsed = (datetime.now() - self.start_time).days
        estimated_daily_cost = Config.MONTHLY_BUDGET_LIMIT / 30
        return min(days_elapsed * estimated_daily_cost, Config.MONTHLY_BUDGET_LIMIT)
    
    def _determine_next_action(self, stats: Dict[str, Any]) -> str:
        """Determine the next action needed"""
        status_counts = stats.get("planner_status_counts", {})
        
        if self.current_phase == "research":
            if status_counts.get("discovered", 0) < 20:
                return "Continue research to discover more planners"
            elif status_counts.get("shortlisted", 0) < 5:
                return "Complete analysis to generate shortlist"
            else:
                return "Approve shortlist and proceed to outreach"
        
        elif self.current_phase == "outreach":
            if status_counts.get("contacted", 0) < status_counts.get("shortlisted", 0):
                return "Complete initial outreach to all shortlisted planners"
            elif status_counts.get("responded", 0) < 3:
                return "Send follow-ups and wait for responses"
            else:
                return "Schedule calls with responding planners"
        
        elif self.current_phase == "calls":
            if status_counts.get("call_scheduled", 0) < status_counts.get("responded", 0):
                return "Schedule remaining calls"
            elif status_counts.get("call_completed", 0) < status_counts.get("call_scheduled", 0):
                return "Complete scheduled calls"
            else:
                return "Proceed to final decision phase"
        
        elif self.current_phase == "decision":
            if status_counts.get("hired", 0) == 0:
                return "Make final hiring decision"
            else:
                return "Process complete - planner hired"
        
        return "Review system status and continue workflow"

# Convenience function for external usage
async def run_wedding_planner_hiring_system():
    """Run the complete wedding planner hiring system"""
    orchestrator = WeddingPlannerOrchestrator()
    return await orchestrator.run_complete_workflow()