"""
Analyzer Agent - Scores and ranks wedding planners based on multicultural fit, availability, and reviews
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from langchain_openai import ChatOpenAI

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.database.airtable_schema import PlannerStatus
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger, log_agent_action, log_api_call, log_human_gate

logger = setup_logger("analyzer_agent")

@dataclass
class PlannerAnalysis:
    """Comprehensive analysis results for a planner"""
    planner_id: str
    name: str
    
    # Scoring Components
    multicultural_score: float  # 0-10
    availability_score: float   # 0-10  
    reviews_score: float       # 0-10
    total_score: float         # 0-10
    
    # Detailed Analysis
    multicultural_factors: Dict[str, Any]
    availability_factors: Dict[str, Any] 
    reviews_factors: Dict[str, Any]
    
    # Ranking
    rank: Optional[int] = None
    shortlist_eligible: bool = False
    
    # Flags and Notes
    red_flags: List[str] = None
    green_flags: List[str] = None
    analysis_notes: str = ""
    confidence_level: float = 0.0  # 0-1
    
    def __post_init__(self):
        if self.red_flags is None:
            self.red_flags = []
        if self.green_flags is None:
            self.green_flags = []

class AnalyzerAgent:
    """Agent responsible for analyzing and ranking discovered planners"""
    
    def __init__(self):
        self.creds_manager = CredentialsManager()
        self.airtable = AirtableClient()
        self._setup_llm()
        self._setup_scoring_criteria()
        
    def _setup_llm(self):
        """Setup OpenAI client for analysis"""
        credentials = self.creds_manager.decrypt_credentials()
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=credentials.get("OPENAI_API_KEY"),
            temperature=0.2
        )
        logger.info("Analyzer agent LLM initialized")
    
    def _setup_scoring_criteria(self):
        """Setup detailed scoring criteria"""
        self.multicultural_criteria = {
            "chinese_wedding_experience": {
                "weight": 0.4,
                "indicators": [
                    "chinese wedding", "asian wedding", "tea ceremony", "cantonese",
                    "mandarin", "dim sum", "lazy susan", "red envelope", "double happiness",
                    "capital seafood", "chinese restaurant", "banquet hall"
                ]
            },
            "fusion_capability": {
                "weight": 0.3,
                "indicators": [
                    "fusion", "modern twist", "city pop", "neon", "retro", "80s", "90s",
                    "authentic with modern", "traditional meets contemporary"
                ]
            },
            "cultural_sensitivity": {
                "weight": 0.2,
                "indicators": [
                    "bilingual", "cultural traditions", "family focused", "respectful",
                    "understanding", "heritage", "authentic"
                ]
            },
            "oc_venue_experience": {
                "weight": 0.1,
                "indicators": [
                    "orange county", "oc", "irvine", "newport", "westminster",
                    "capital seafood", "sea harbour", "chinese restaurant"
                ]
            }
        }
        
        self.availability_criteria = {
            "timeline_comfort": {
                "weight": 0.4,
                "positive_indicators": [
                    "rush timeline", "short notice", "quick turnaround", "3 month",
                    "available", "flexible", "can accommodate"
                ],
                "negative_indicators": [
                    "booked", "unavailable", "6 month minimum", "fully booked",
                    "waitlist", "next year", "too busy"
                ]
            },
            "january_2026_availability": {
                "weight": 0.3,
                "positive_indicators": [
                    "january available", "winter weddings", "2026", "accepting bookings"
                ],
                "negative_indicators": [
                    "january booked", "winter break", "not available january"
                ]
            },
            "responsiveness": {
                "weight": 0.2,
                "positive_indicators": [
                    "quick response", "prompt", "same day", "24 hours", "responsive"
                ],
                "negative_indicators": [
                    "slow response", "weeks to respond", "hard to reach", "unresponsive"
                ]
            },
            "capacity": {
                "weight": 0.1,
                "positive_indicators": [
                    "taking new clients", "available", "capacity", "open calendar"
                ],
                "negative_indicators": [
                    "fully booked", "waitlist only", "not taking new", "overbooked"
                ]
            }
        }
        
        self.reviews_criteria = {
            "overall_rating": {"weight": 0.4, "min_reviews": 5},
            "cultural_wedding_reviews": {"weight": 0.3, "keywords": ["asian", "chinese", "multicultural"]},
            "timeline_reviews": {"weight": 0.2, "keywords": ["timeline", "organized", "efficient"]},
            "communication_reviews": {"weight": 0.1, "keywords": ["communication", "responsive", "helpful"]}
        }
        
        self.red_flag_patterns = [
            "no asian experience", "modern only", "no traditional",
            "overpriced", "hidden fees", "unprofessional", "unresponsive",
            "fully booked", "not available", "too busy", "instagram focused only",
            "styled shoots only", "no real weddings", "inexperienced"
        ]
        
        self.green_flag_patterns = [
            "authentic chinese weddings", "tea ceremony expert", "bilingual mc",
            "capital seafood experience", "fusion weddings", "cultural sensitivity",
            "family focused", "available rush timeline", "reasonable pricing",
            "excellent reviews", "multicultural specialist", "orange county expert"
        ]
    
    def run_analysis_phase(self) -> List[str]:
        """Main analysis phase - score and rank all discovered planners"""
        logger.info("Starting analysis phase")
        
        try:
            # Get all discovered planners
            discovered_planners = self.airtable.get_planners_by_status("discovered")
            
            if not discovered_planners:
                logger.warning("No discovered planners to analyze")
                return []
            
            logger.info(f"Analyzing {len(discovered_planners)} planners")
            
            # Analyze each planner
            analyses = []
            for planner in discovered_planners:
                analysis = self._analyze_single_planner(planner)
                if analysis:
                    analyses.append(analysis)
            
            # Rank planners by total score
            ranked_analyses = self._rank_analyses(analyses)
            
            # Generate shortlist
            shortlist_ids = self._generate_shortlist(ranked_analyses)
            
            # Update database with scores and rankings
            self._update_database_with_analyses(ranked_analyses)
            
            log_agent_action(
                logger, "analyzer_agent", "analysis_phase_completed",
                {"analyzed": len(analyses), "shortlisted": len(shortlist_ids)}
            )
            
            # Trigger human approval gate
            self._trigger_human_approval(shortlist_ids)
            
            return shortlist_ids
            
        except Exception as e:
            logger.error(f"Analysis phase failed: {e}")
            raise
    
    def _analyze_single_planner(self, planner: Dict[str, Any]) -> Optional[PlannerAnalysis]:
        """Analyze a single planner and generate scores"""
        try:
            planner_id = planner["id"]
            name = planner.get("name", "Unknown")
            
            logger.info(f"Analyzing planner: {name}")
            
            # Gather all available text data
            text_data = self._gather_planner_text_data(planner)
            
            # Score each component
            multicultural_score, multicultural_factors = self._score_multicultural_fit(text_data)
            availability_score, availability_factors = self._score_availability(text_data)
            reviews_score, reviews_factors = self._score_reviews(planner)
            
            # Calculate weighted total score
            weights = Config.SCORING_WEIGHTS
            total_score = (
                multicultural_score * weights["multicultural_fit"] +
                availability_score * weights["timeline_availability"] +
                reviews_score * weights["reviews_sentiment"]
            )
            
            # Identify flags
            red_flags = self._identify_red_flags(text_data)
            green_flags = self._identify_green_flags(text_data)
            
            # Generate AI-powered analysis notes
            analysis_notes = self._generate_ai_analysis(planner, text_data, {
                "multicultural": multicultural_score,
                "availability": availability_score, 
                "reviews": reviews_score,
                "total": total_score
            })
            
            # Calculate confidence level
            confidence = self._calculate_confidence(multicultural_factors, availability_factors, reviews_factors)
            
            analysis = PlannerAnalysis(
                planner_id=planner_id,
                name=name,
                multicultural_score=multicultural_score,
                availability_score=availability_score,
                reviews_score=reviews_score,
                total_score=total_score,
                multicultural_factors=multicultural_factors,
                availability_factors=availability_factors,
                reviews_factors=reviews_factors,
                red_flags=red_flags,
                green_flags=green_flags,
                analysis_notes=analysis_notes,
                confidence_level=confidence
            )
            
            log_agent_action(
                logger, "analyzer_agent", "planner_analyzed",
                {"name": name, "total_score": total_score, "confidence": confidence}
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze planner {planner.get('name', 'Unknown')}: {e}")
            return None
    
    def _gather_planner_text_data(self, planner: Dict[str, Any]) -> str:
        """Gather all text data for analysis"""
        text_parts = []
        
        # Basic info
        text_parts.append(planner.get("name", ""))
        text_parts.append(planner.get("business_name", ""))
        text_parts.append(planner.get("location", ""))
        
        # Bio and descriptions
        if planner.get("bio_text"):
            text_parts.append(planner["bio_text"])
        
        # Portfolio and specializations
        if planner.get("specializations"):
            if isinstance(planner["specializations"], list):
                text_parts.extend(planner["specializations"])
            else:
                text_parts.append(str(planner["specializations"]))
        
        # Previous venues
        if planner.get("previous_venues"):
            text_parts.append(planner["previous_venues"])
        
        # Review summary
        if planner.get("review_summary"):
            text_parts.append(planner["review_summary"])
        
        # Notes
        if planner.get("notes"):
            text_parts.append(planner["notes"])
        
        return " ".join(filter(None, text_parts)).lower()
    
    def _score_multicultural_fit(self, text_data: str) -> Tuple[float, Dict[str, Any]]:
        """Score multicultural wedding fit (0-10)"""
        total_score = 0.0
        factors = {}
        
        for category, criteria in self.multicultural_criteria.items():
            category_score = 0.0
            matches = []
            
            for indicator in criteria["indicators"]:
                if indicator in text_data:
                    matches.append(indicator)
                    category_score += 1.0
            
            # Normalize to 0-10 scale  
            max_possible = len(criteria["indicators"])
            normalized_score = min(10.0, (category_score / max_possible) * 10.0)
            
            # Apply weight
            weighted_score = normalized_score * criteria["weight"]
            total_score += weighted_score
            
            factors[category] = {
                "score": normalized_score,
                "weight": criteria["weight"],
                "weighted_score": weighted_score,
                "matches": matches
            }
        
        return min(10.0, total_score), factors
    
    def _score_availability(self, text_data: str) -> Tuple[float, Dict[str, Any]]:
        """Score timeline availability (0-10)"""
        total_score = 0.0
        factors = {}
        
        for category, criteria in self.availability_criteria.items():
            positive_score = 0.0
            negative_score = 0.0
            
            # Count positive indicators
            positive_matches = []
            for indicator in criteria.get("positive_indicators", []):
                if indicator in text_data:
                    positive_matches.append(indicator)
                    positive_score += 1.0
            
            # Count negative indicators  
            negative_matches = []
            for indicator in criteria.get("negative_indicators", []):
                if indicator in text_data:
                    negative_matches.append(indicator)
                    negative_score += 1.0
            
            # Calculate net score (positive - negative)
            net_score = positive_score - negative_score
            
            # Normalize to 0-10 scale
            max_positive = len(criteria.get("positive_indicators", []))
            if max_positive > 0:
                normalized_score = max(0.0, min(10.0, (net_score / max_positive) * 10.0))
            else:
                normalized_score = 5.0  # Neutral if no criteria
            
            # Apply weight
            weighted_score = normalized_score * criteria["weight"]
            total_score += weighted_score
            
            factors[category] = {
                "score": normalized_score,
                "weight": criteria["weight"],
                "weighted_score": weighted_score,
                "positive_matches": positive_matches,
                "negative_matches": negative_matches
            }
        
        return min(10.0, total_score), factors
    
    def _score_reviews(self, planner: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Score based on reviews and ratings (0-10)"""
        factors = {}
        total_score = 0.0
        
        # Overall rating score
        rating = planner.get("average_rating", 0)
        review_count = planner.get("total_reviews", 0)
        
        if rating and review_count >= self.reviews_criteria["overall_rating"]["min_reviews"]:
            # Convert rating to 0-10 scale (assuming 5-star max)
            rating_score = (rating / 5.0) * 10.0
            total_score += rating_score * self.reviews_criteria["overall_rating"]["weight"]
            
            factors["overall_rating"] = {
                "score": rating_score,
                "weight": self.reviews_criteria["overall_rating"]["weight"],
                "rating": rating,
                "review_count": review_count
            }
        else:
            # Penalty for insufficient reviews
            penalty_score = 3.0 if review_count > 0 else 0.0
            total_score += penalty_score * self.reviews_criteria["overall_rating"]["weight"]
            
            factors["overall_rating"] = {
                "score": penalty_score,
                "weight": self.reviews_criteria["overall_rating"]["weight"],
                "rating": rating,
                "review_count": review_count,
                "penalty": "Insufficient reviews"
            }
        
        # Review content analysis
        review_text = planner.get("review_summary", "").lower()
        
        for category in ["cultural_wedding_reviews", "timeline_reviews", "communication_reviews"]:
            criteria = self.reviews_criteria[category]
            category_score = 0.0
            matches = []
            
            for keyword in criteria["keywords"]:
                if keyword in review_text:
                    matches.append(keyword)
                    category_score += 1.0
            
            # Normalize and weight
            max_keywords = len(criteria["keywords"])
            if max_keywords > 0:
                normalized_score = min(10.0, (category_score / max_keywords) * 10.0)
            else:
                normalized_score = 5.0
            
            weighted_score = normalized_score * criteria["weight"]
            total_score += weighted_score
            
            factors[category] = {
                "score": normalized_score,
                "weight": criteria["weight"],
                "weighted_score": weighted_score,
                "matches": matches
            }
        
        return min(10.0, total_score), factors
    
    def _identify_red_flags(self, text_data: str) -> List[str]:
        """Identify red flags in planner data"""
        red_flags = []
        
        for pattern in self.red_flag_patterns:
            if pattern in text_data:
                red_flags.append(pattern)
        
        return red_flags
    
    def _identify_green_flags(self, text_data: str) -> List[str]:
        """Identify green flags in planner data"""
        green_flags = []
        
        for pattern in self.green_flag_patterns:
            if pattern in text_data:
                green_flags.append(pattern)
        
        return green_flags
    
    def _generate_ai_analysis(self, planner: Dict[str, Any], text_data: str, scores: Dict[str, float]) -> str:
        """Generate AI-powered analysis summary"""
        try:
            prompt = f"""
            Analyze this wedding planner for a Chinese banquet wedding with city pop fusion elements:
            
            Planner: {planner.get('name', 'Unknown')}
            Source: {planner.get('source', 'Unknown')}
            Location: {planner.get('location', 'Unknown')}
            
            Available Data: {text_data[:1000]}...
            
            Scores:
            - Multicultural Fit: {scores['multicultural']:.1f}/10
            - Availability: {scores['availability']:.1f}/10  
            - Reviews: {scores['reviews']:.1f}/10
            - Total: {scores['total']:.1f}/10
            
            Wedding Requirements:
            - Authentic 80s/90s Chinese banquet style
            - Tea ceremony coordination
            - Bilingual MC needed
            - City pop fusion elements (neon, retro)
            - 3-4 month timeline (urgent)
            - Orange County location
            - 200-220 guests at Chinese restaurant
            
            Provide a 2-3 sentence analysis focusing on:
            1. Key strengths for this specific wedding style
            2. Main concerns or gaps
            3. Overall fit recommendation
            
            Be specific about cultural experience and timeline fit.
            """
            
            response = self.llm.invoke(prompt)
            log_api_call(logger, "openai", "planner_analysis_summary")
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return f"Analysis failed. Scores: Multicultural {scores['multicultural']:.1f}, Availability {scores['availability']:.1f}, Reviews {scores['reviews']:.1f}"
    
    def _calculate_confidence(self, multicultural_factors: Dict, availability_factors: Dict, reviews_factors: Dict) -> float:
        """Calculate confidence level in the analysis (0-1)"""
        confidence_factors = []
        
        # Multicultural confidence based on match quality
        multicultural_matches = sum(len(factor.get("matches", [])) for factor in multicultural_factors.values())
        multicultural_confidence = min(1.0, multicultural_matches / 10.0)
        confidence_factors.append(multicultural_confidence)
        
        # Availability confidence based on data quality
        availability_indicators = sum(
            len(factor.get("positive_matches", [])) + len(factor.get("negative_matches", []))
            for factor in availability_factors.values()
        )
        availability_confidence = min(1.0, availability_indicators / 5.0)
        confidence_factors.append(availability_confidence)
        
        # Reviews confidence based on review count
        review_count = reviews_factors.get("overall_rating", {}).get("review_count", 0)
        reviews_confidence = min(1.0, review_count / 20.0)  # Full confidence at 20+ reviews
        confidence_factors.append(reviews_confidence)
        
        return np.mean(confidence_factors)
    
    def _rank_analyses(self, analyses: List[PlannerAnalysis]) -> List[PlannerAnalysis]:
        """Rank analyses by total score"""
        # Sort by total score (descending) then by confidence (descending)
        ranked = sorted(
            analyses, 
            key=lambda x: (x.total_score, x.confidence_level), 
            reverse=True
        )
        
        # Assign ranks
        for i, analysis in enumerate(ranked):
            analysis.rank = i + 1
        
        return ranked
    
    def _generate_shortlist(self, ranked_analyses: List[PlannerAnalysis]) -> List[str]:
        """Generate shortlist of top planners"""
        shortlist_ids = []
        
        # Shortlist criteria
        min_score = 6.0  # Minimum total score
        min_confidence = 0.3  # Minimum confidence level
        max_red_flags = 2  # Maximum allowed red flags
        target_size = Config.SHORTLIST_SIZE
        
        for analysis in ranked_analyses:
            # Check if eligible for shortlist
            if (analysis.total_score >= min_score and 
                analysis.confidence_level >= min_confidence and
                len(analysis.red_flags) <= max_red_flags):
                
                analysis.shortlist_eligible = True
                shortlist_ids.append(analysis.planner_id)
                
                if len(shortlist_ids) >= target_size:
                    break
        
        logger.info(f"Generated shortlist of {len(shortlist_ids)} planners")
        return shortlist_ids
    
    def _update_database_with_analyses(self, analyses: List[PlannerAnalysis]) -> None:
        """Update Airtable with analysis results"""
        for analysis in analyses:
            try:
                updates = {
                    "multicultural_score": analysis.multicultural_score,
                    "availability_score": analysis.availability_score,
                    "reviews_score": analysis.reviews_score,
                    "total_score": analysis.total_score,
                    "flags": analysis.red_flags + analysis.green_flags,
                    "notes": analysis.analysis_notes,
                    "status": "shortlisted" if analysis.shortlist_eligible else "analyzed"
                }
                
                self.airtable.update_planner(analysis.planner_id, updates)
                
            except Exception as e:
                logger.error(f"Failed to update planner {analysis.planner_id}: {e}")
    
    def _trigger_human_approval(self, shortlist_ids: List[str]) -> None:
        """Trigger human approval gate for shortlist"""
        if not shortlist_ids:
            log_human_gate(logger, "shortlist_approval", "No planners met shortlist criteria")
            return
        
        # Get shortlist details for human review
        shortlist_details = []
        for planner_id in shortlist_ids:
            planner = self.airtable.get_planner(planner_id)
            if planner:
                shortlist_details.append({
                    "name": planner.get("name"),
                    "score": planner.get("total_score"),
                    "source": planner.get("source"),
                    "location": planner.get("location")
                })
        
        summary = f"Generated shortlist of {len(shortlist_ids)} planners: " + \
                 ", ".join([f"{p['name']} ({p['score']:.1f})" for p in shortlist_details])
        
        log_human_gate(logger, "shortlist_approval", summary)