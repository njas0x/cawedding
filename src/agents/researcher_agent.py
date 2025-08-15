"""
Researcher Agent - Scrapes wedding planner data from Instagram and wedding sites
"""
import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from apify_client import ApifyClient
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

from src.config import Config
from src.database.airtable_client import AirtableClient
from src.database.airtable_schema import PlannerRecord, PlannerStatus
from src.utils.credentials import CredentialsManager
from src.utils.logger import setup_logger, log_agent_action, log_api_call

logger = setup_logger("researcher_agent")

@dataclass
class ScrapedPlannerData:
    """Raw scraped data for a wedding planner"""
    name: str
    source: str
    profile_url: str
    
    # Contact Info
    email: Optional[str] = None
    phone: Optional[str] = None
    instagram_handle: Optional[str] = None
    website: Optional[str] = None
    business_name: Optional[str] = None
    location: Optional[str] = None
    
    # Content Analysis
    bio_text: Optional[str] = None
    posts_analyzed: int = 0
    hashtags_found: List[str] = None
    keywords_matched: List[str] = None
    
    # Portfolio Indicators
    portfolio_links: List[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    
    # Reviews (if available)
    reviews_count: Optional[int] = None
    average_rating: Optional[float] = None
    review_source: Optional[str] = None
    
    def __post_init__(self):
        if self.hashtags_found is None:
            self.hashtags_found = []
        if self.keywords_matched is None:
            self.keywords_matched = []
        if self.portfolio_links is None:
            self.portfolio_links = []

class ResearcherAgent:
    """Agent responsible for discovering and scraping wedding planner data"""
    
    def __init__(self):
        self.creds_manager = CredentialsManager()
        self.airtable = AirtableClient()
        self._setup_clients()
        self._setup_keywords()
        
    def _setup_clients(self):
        """Setup API clients"""
        credentials = self.creds_manager.decrypt_credentials()
        
        # Apify client for Instagram scraping
        self.apify_client = ApifyClient(credentials.get("APIFY_API_TOKEN"))
        
        # OpenAI for content analysis
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=credentials.get("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        logger.info("Researcher agent clients initialized")
    
    def _setup_keywords(self):
        """Setup search keywords and patterns"""
        self.multicultural_keywords = [
            "chinese wedding", "asian wedding", "multicultural", "tea ceremony",
            "fusion wedding", "bilingual", "cantonese", "mandarin", "taiwanese",
            "hong kong", "dim sum", "lazy susan", "red envelope", "double happiness",
            "city pop", "neon", "retro", "80s", "90s", "authentic", "traditional"
        ]
        
        self.location_keywords = [
            "orange county", "oc", "irvine", "newport", "huntington beach",
            "anaheim", "garden grove", "westminster", "costa mesa", "santa ana"
        ]
        
        self.experience_keywords = [
            "wedding planner", "event planner", "full service", "day of coordination",
            "chinese restaurant", "banquet", "seafood restaurant", "capital seafood"
        ]
        
        self.red_flag_keywords = [
            "modern only", "no traditional", "instagram focused", "styled shoot only",
            "overpriced", "unavailable", "booked", "too busy"
        ]
    
    def run_research_phase(self, target_count: int = 50) -> List[str]:
        """Main research phase - discover and process planners"""
        logger.info(f"Starting research phase - target: {target_count} planners")
        
        discovered_planners = []
        
        try:
            # Instagram research
            instagram_planners = self._scrape_instagram_planners()
            discovered_planners.extend(instagram_planners)
            
            # Wedding site research
            weddingwire_planners = self._scrape_weddingwire_planners()
            discovered_planners.extend(weddingwire_planners)
            
            theknot_planners = self._scrape_theknot_planners()
            discovered_planners.extend(theknot_planners)
            
            # Process and store discovered planners
            stored_planner_ids = []
            for scraped_data in discovered_planners[:target_count]:
                planner_id = self._process_scraped_planner(scraped_data)
                if planner_id:
                    stored_planner_ids.append(planner_id)
            
            log_agent_action(
                logger, "researcher_agent", "research_phase_completed",
                {"discovered": len(discovered_planners), "stored": len(stored_planner_ids)}
            )
            
            return stored_planner_ids
            
        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            raise
    
    def _scrape_instagram_planners(self) -> List[ScrapedPlannerData]:
        """Scrape Instagram for wedding planners"""
        logger.info("Starting Instagram scraping")
        planners = []
        
        try:
            for hashtag in Config.INSTAGRAM_HASHTAGS:
                logger.info(f"Scraping hashtag: {hashtag}")
                
                # Run Apify Instagram hashtag scraper
                run_input = {
                    "hashtags": [hashtag.replace("#", "")],
                    "resultsLimit": 20,
                    "searchLimit": 100,
                    "addParentData": False
                }
                
                run = self.apify_client.actor("apify/instagram-hashtag-scraper").call(
                    run_input=run_input
                )
                
                log_api_call(logger, "apify", f"instagram-hashtag-{hashtag}")
                
                # Process results
                for item in self.apify_client.dataset(run["defaultDatasetId"]).iterate_items():
                    planner_data = self._process_instagram_post(item, hashtag)
                    if planner_data:
                        planners.append(planner_data)
                
                # Rate limiting
                time.sleep(2)
            
            # Deduplicate by Instagram handle
            unique_planners = {}
            for planner in planners:
                if planner.instagram_handle not in unique_planners:
                    unique_planners[planner.instagram_handle] = planner
            
            logger.info(f"Instagram scraping completed: {len(unique_planners)} unique planners")
            return list(unique_planners.values())
            
        except Exception as e:
            logger.error(f"Instagram scraping failed: {e}")
            return []
    
    def _process_instagram_post(self, post_data: Dict, hashtag: str) -> Optional[ScrapedPlannerData]:
        """Process individual Instagram post data"""
        try:
            # Extract basic info
            username = post_data.get("ownerUsername", "")
            if not username:
                return None
            
            # Skip non-business accounts
            caption = post_data.get("caption", "").lower()
            if not any(keyword in caption for keyword in self.experience_keywords):
                return None
            
            # Check for location relevance
            location_relevant = any(keyword in caption for keyword in self.location_keywords)
            
            # Extract matched keywords
            matched_keywords = []
            for keyword in self.multicultural_keywords:
                if keyword in caption:
                    matched_keywords.append(keyword)
            
            # Skip if no multicultural relevance
            if not matched_keywords and not location_relevant:
                return None
            
            # Extract contact info from bio/caption
            email = self._extract_email(caption)
            website = self._extract_website(caption)
            phone = self._extract_phone(caption)
            
            planner_data = ScrapedPlannerData(
                name=username.replace("_", " ").title(),
                source="instagram",
                profile_url=f"https://instagram.com/{username}",
                instagram_handle=username,
                email=email,
                website=website,
                phone=phone,
                bio_text=caption[:500],  # Truncate for storage
                keywords_matched=matched_keywords,
                hashtags_found=[hashtag],
                follower_count=post_data.get("ownerFollowersCount"),
                posts_analyzed=1
            )
            
            return planner_data
            
        except Exception as e:
            logger.error(f"Failed to process Instagram post: {e}")
            return None
    
    def _scrape_weddingwire_planners(self) -> List[ScrapedPlannerData]:
        """Scrape WeddingWire for Orange County planners"""
        logger.info("Starting WeddingWire scraping")
        planners = []
        
        try:
            # WeddingWire search URL for Orange County wedding planners
            base_url = "https://www.weddingwire.com/c/ca/orange-county/wedding-planners"
            params = {
                "page": 1,
                "sort": "rating",
                "filter": "asian,multicultural"
            }
            
            for page in range(1, 6):  # Scrape first 5 pages
                params["page"] = page
                url = f"{base_url}?page={page}"
                
                logger.info(f"Scraping WeddingWire page {page}")
                
                response = requests.get(url, headers=self._get_headers())
                if response.status_code != 200:
                    logger.warning(f"WeddingWire request failed: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract planner listings
                planner_cards = soup.find_all('div', class_='vendor-card')
                
                for card in planner_cards:
                    planner_data = self._process_weddingwire_card(card)
                    if planner_data:
                        planners.append(planner_data)
                
                time.sleep(3)  # Rate limiting
            
            logger.info(f"WeddingWire scraping completed: {len(planners)} planners")
            return planners
            
        except Exception as e:
            logger.error(f"WeddingWire scraping failed: {e}")
            return []
    
    def _process_weddingwire_card(self, card) -> Optional[ScrapedPlannerData]:
        """Process WeddingWire vendor card"""
        try:
            # Extract name
            name_elem = card.find('h3') or card.find('h2')
            if not name_elem:
                return None
            name = name_elem.text.strip()
            
            # Extract URL
            link_elem = card.find('a')
            profile_url = link_elem.get('href') if link_elem else ""
            if profile_url and not profile_url.startswith('http'):
                profile_url = f"https://www.weddingwire.com{profile_url}"
            
            # Extract location
            location_elem = card.find('span', class_='location')
            location = location_elem.text.strip() if location_elem else ""
            
            # Extract rating
            rating_elem = card.find('span', class_='rating')
            rating = None
            if rating_elem:
                rating_text = rating_elem.text.strip()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract review count
            reviews_elem = card.find('span', class_='review-count')
            reviews_count = None
            if reviews_elem:
                reviews_text = reviews_elem.text.strip()
                count_match = re.search(r'(\d+)', reviews_text)
                if count_match:
                    reviews_count = int(count_match.group(1))
            
            # Extract description/bio
            desc_elem = card.find('p', class_='description')
            bio_text = desc_elem.text.strip() if desc_elem else ""
            
            # Check for multicultural keywords
            text_to_check = f"{name} {location} {bio_text}".lower()
            matched_keywords = []
            for keyword in self.multicultural_keywords:
                if keyword in text_to_check:
                    matched_keywords.append(keyword)
            
            # Skip if no relevant keywords
            if not matched_keywords:
                return None
            
            planner_data = ScrapedPlannerData(
                name=name,
                source="weddingwire",
                profile_url=profile_url,
                location=location,
                bio_text=bio_text,
                keywords_matched=matched_keywords,
                average_rating=rating,
                reviews_count=reviews_count,
                review_source="weddingwire"
            )
            
            return planner_data
            
        except Exception as e:
            logger.error(f"Failed to process WeddingWire card: {e}")
            return None
    
    def _scrape_theknot_planners(self) -> List[ScrapedPlannerData]:
        """Scrape The Knot for Orange County planners"""
        logger.info("Starting The Knot scraping")
        planners = []
        
        try:
            base_url = "https://www.theknot.com/marketplace/wedding-planners-orange-county-ca"
            
            for page in range(1, 4):  # Scrape first 3 pages
                url = f"{base_url}?page={page}"
                logger.info(f"Scraping The Knot page {page}")
                
                response = requests.get(url, headers=self._get_headers())
                if response.status_code != 200:
                    logger.warning(f"The Knot request failed: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract planner listings
                planner_cards = soup.find_all('div', class_='vendor-search-result')
                
                for card in planner_cards:
                    planner_data = self._process_theknot_card(card)
                    if planner_data:
                        planners.append(planner_data)
                
                time.sleep(3)  # Rate limiting
            
            logger.info(f"The Knot scraping completed: {len(planners)} planners")
            return planners
            
        except Exception as e:
            logger.error(f"The Knot scraping failed: {e}")
            return []
    
    def _process_theknot_card(self, card) -> Optional[ScrapedPlannerData]:
        """Process The Knot vendor card"""
        try:
            # Extract name
            name_elem = card.find('h3') or card.find('h2') or card.find('a')
            if not name_elem:
                return None
            name = name_elem.text.strip()
            
            # Extract URL
            link_elem = card.find('a')
            profile_url = link_elem.get('href') if link_elem else ""
            if profile_url and not profile_url.startswith('http'):
                profile_url = f"https://www.theknot.com{profile_url}"
            
            # Extract description
            desc_elem = card.find('p') or card.find('div', class_='description')
            bio_text = desc_elem.text.strip() if desc_elem else ""
            
            # Check for multicultural keywords
            text_to_check = f"{name} {bio_text}".lower()
            matched_keywords = []
            for keyword in self.multicultural_keywords:
                if keyword in text_to_check:
                    matched_keywords.append(keyword)
            
            # Skip if no relevant keywords
            if not matched_keywords:
                return None
            
            planner_data = ScrapedPlannerData(
                name=name,
                source="theknot",
                profile_url=profile_url,
                bio_text=bio_text,
                keywords_matched=matched_keywords,
                review_source="theknot"
            )
            
            return planner_data
            
        except Exception as e:
            logger.error(f"Failed to process The Knot card: {e}")
            return None
    
    def _process_scraped_planner(self, scraped_data: ScrapedPlannerData) -> Optional[str]:
        """Process scraped data and store in Airtable"""
        try:
            # Enhanced analysis using OpenAI
            enhanced_data = self._enhance_with_ai_analysis(scraped_data)
            
            # Convert to PlannerRecord
            planner_record = PlannerRecord(
                name=enhanced_data.name,
                email=enhanced_data.email,
                phone=enhanced_data.phone,
                instagram_handle=enhanced_data.instagram_handle,
                website=enhanced_data.website,
                business_name=enhanced_data.business_name or enhanced_data.name,
                location=enhanced_data.location or "Orange County, CA",
                portfolio_links=enhanced_data.portfolio_links,
                specializations=enhanced_data.keywords_matched,
                total_reviews=enhanced_data.reviews_count,
                average_rating=enhanced_data.average_rating,
                review_sources=[enhanced_data.review_source] if enhanced_data.review_source else [],
                source=enhanced_data.source,
                status=PlannerStatus.DISCOVERED
            )
            
            # Store in Airtable
            planner_id = self.airtable.create_planner(planner_record)
            
            log_agent_action(
                logger, "researcher_agent", "planner_processed",
                {"name": enhanced_data.name, "source": enhanced_data.source, "keywords": len(enhanced_data.keywords_matched)}
            )
            
            return planner_id
            
        except Exception as e:
            logger.error(f"Failed to process scraped planner: {e}")
            return None
    
    def _enhance_with_ai_analysis(self, scraped_data: ScrapedPlannerData) -> ScrapedPlannerData:
        """Use AI to enhance scraped data with additional insights"""
        try:
            if not scraped_data.bio_text:
                return scraped_data
            
            prompt = f"""
            Analyze this wedding planner's profile and extract relevant information:
            
            Name: {scraped_data.name}
            Bio: {scraped_data.bio_text}
            Source: {scraped_data.source}
            
            Please identify:
            1. Business name (if different from personal name)
            2. Years of experience (estimate from text)
            3. Specialization in Asian/Chinese weddings (yes/no with confidence)
            4. Tea ceremony experience (yes/no)
            5. Bilingual services mentioned (yes/no)
            6. Orange County venue familiarity (yes/no)
            7. Any red flags (overpriced, unavailable, style mismatch)
            8. Contact information (email, phone, website if mentioned)
            
            Respond in this format:
            Business Name: [name or "same as personal"]
            Experience Years: [number or "unknown"]
            Chinese Wedding Experience: [yes/no] ([confidence 1-10])
            Tea Ceremony: [yes/no]
            Bilingual Services: [yes/no]  
            OC Venue Familiarity: [yes/no]
            Red Flags: [list or "none"]
            Contact Info: [any found or "none"]
            """
            
            response = self.llm.invoke(prompt)
            log_api_call(logger, "openai", "planner_analysis")
            
            # Parse AI response and update scraped_data
            analysis = response.content
            
            # Extract business name
            if "Business Name:" in analysis:
                business_line = [line for line in analysis.split('\n') if 'Business Name:' in line][0]
                business_name = business_line.split('Business Name:')[1].strip()
                if business_name != "same as personal" and business_name != scraped_data.name:
                    scraped_data.business_name = business_name
            
            # Extract experience indicators
            if "Chinese Wedding Experience: yes" in analysis:
                scraped_data.keywords_matched.append("chinese_wedding_confirmed")
            
            if "Tea Ceremony: yes" in analysis:
                scraped_data.keywords_matched.append("tea_ceremony_experience")
            
            if "Bilingual Services: yes" in analysis:
                scraped_data.keywords_matched.append("bilingual_services")
            
            if "OC Venue Familiarity: yes" in analysis:
                scraped_data.keywords_matched.append("oc_venue_experience")
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return scraped_data
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        phone_pattern = r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        matches = re.findall(phone_pattern, text)
        return matches[0] if matches else None
    
    def _extract_website(self, text: str) -> Optional[str]:
        """Extract website URL from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        matches = re.findall(url_pattern, text)
        return matches[0] if matches else None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for web scraping"""
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }