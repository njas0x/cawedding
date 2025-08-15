# Wedding Planner Hiring System 🎯

AI-powered multi-agent system for autonomously discovering, vetting, and hiring wedding planners specialized in authentic Chinese banquet weddings with modern fusion elements.

## Overview

This system automates 80% of the wedding planner hiring process using three specialized AI agents:

- **🔍 Researcher Agent**: Discovers planners via Instagram, WeddingWire, and The Knot
- **📊 Analyzer Agent**: Scores and ranks planners based on multicultural fit, availability, and reviews  
- **📧 Outreach Agent**: Manages personalized communications and scheduling

**Target**: Hire 1-3 qualified planners by September 1, 2025 for a January 2026 authentic Chinese banquet wedding with city pop fusion elements.

## Quick Start

### 1. Setup

```bash
# Clone and setup
cd cawedding
python scripts/setup.py

# Configure API keys in .env file
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Run System

```bash
# Full workflow with monitoring
python scripts/run_system.py

# Dashboard only
python scripts/run_system.py --mode dashboard

# Health check
python scripts/run_system.py --mode health-check
```

### 3. Monitor Progress

The system provides real-time monitoring with:
- Workflow progress tracking
- Cost monitoring and alerts
- Agent performance metrics
- Human approval gates

## System Architecture

```
Wedding Planner Hiring System
├── 🎯 Orchestrator (CrewAI)
├── 🔍 Researcher Agent
├── 📊 Analyzer Agent  
├── 📧 Outreach Agent
├── 💾 Airtable Database
├── 📊 Monitoring Dashboard
└── 💰 Cost Tracker
```

## Workflow Phases

### Phase 1: Research (Days 1-4)
- Scrape 20-50 wedding planners from social media and directories
- Focus on multicultural expertise and Orange County location
- Store raw data in Airtable for analysis

### Phase 2: Analysis (Days 1-4)  
- Score planners on multicultural fit (40%), availability (30%), reviews (30%)
- Generate shortlist of 5-10 top candidates
- Flag red flags and green flags for human review

### Phase 3: Outreach (Days 5-12)
- Send personalized emails to shortlisted planners
- Automated follow-ups after 48 hours
- Track responses and schedule intro calls

### Phase 4: Decision (Days 13-14)
- Coordinate intro calls (human-conducted)
- Final analysis and recommendations
- Facilitate hiring decision and handoff

## Key Features

### 🎯 Cultural Specialization
- Focused on authentic Chinese banquet weddings
- Tea ceremony coordination experience
- Bilingual MC capabilities
- Modern fusion elements (city pop, neon lighting)

### 🤖 Intelligent Automation
- AI-powered content analysis
- Automated scoring and ranking
- Personalized outreach at scale
- Smart follow-up management

### 💰 Cost Control
- Real-time budget monitoring (<$150/month)
- API usage tracking
- Cost alerts and projections
- Detailed expense reporting

### 📊 Comprehensive Monitoring
- Live dashboard with progress tracking
- Agent performance metrics
- System health monitoring
- Audit logs for compliance

## Configuration

### Required API Keys
```bash
OPENAI_API_KEY=your_openai_api_key
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
APIFY_API_TOKEN=your_apify_token
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
SENDGRID_API_KEY=your_sendgrid_key
```

### Wedding Specifications
The system is pre-configured for:
- **Date**: January 2026 (mid-month)
- **Location**: Orange County, CA Chinese restaurants
- **Guests**: 200-220 (20-22 round tables)
- **Style**: Authentic 80s/90s Chinese banquet with city pop fusion
- **Budget**: $25-30K total (planner fee $3-5K)
- **Timeline**: 3-4 months execution window

## Usage Examples

### Complete Workflow
```bash
# Run full system with monitoring
python scripts/run_system.py

# Dry run (no actual API calls)
python scripts/run_system.py --dry-run

# Run without monitoring dashboard
python scripts/run_system.py --no-monitoring
```

### Management Commands
```bash
# Create system backup
python scripts/manage_system.py backup

# Export results  
python scripts/manage_system.py export --format csv

# System status
python scripts/manage_system.py status

# Clean old data
python scripts/manage_system.py cleanup --days 30
```

### Monitoring
```bash
# Live dashboard
python scripts/run_system.py --mode dashboard

# Cost report
python scripts/run_system.py --mode cost-report

# Health check
python scripts/run_system.py --mode health-check
```

## Data Storage

### Airtable Schema
- **Planners**: Core planner data, scores, status
- **Communications**: Email/SMS tracking and responses  
- **Calls**: Call scheduling and summary records
- **Logs**: Audit trail of all agent actions

### Local Storage
- **Costs**: JSON file with detailed cost tracking
- **Metrics**: System performance snapshots
- **Logs**: Detailed execution logs by component
- **Exports**: Generated reports and backups

## Success Criteria

- ✅ Discover 20-50 relevant planners
- ✅ Generate shortlist of 5-10 candidates  
- ✅ Achieve 3+ responses from outreach
- ✅ Complete 3+ intro calls
- ✅ Hire 1-3 qualified planners by September 1
- ✅ Keep human involvement under 3 hours total
- ✅ Stay within $150/month budget

## Safety & Compliance

### Ethical Scraping
- Uses Apify for compliant data collection
- Respects rate limits and robots.txt
- Only scrapes public profile data
- No login or private data access

### Privacy Protection
- Encrypts stored credentials
- Anonymizes personal data in logs
- Provides opt-out mechanisms
- Complies with CAN-SPAM for emails

### Human Oversight
- Approval gates for sensitive actions
- All outreach reviewed before sending
- Final hiring decision remains human-driven
- Complete audit trail maintained

## Technical Requirements

- **Python**: 3.8+
- **APIs**: OpenAI, Airtable, Apify, Twilio, SendGrid
- **Framework**: CrewAI for multi-agent coordination
- **Storage**: Airtable (free tier supports 1,200 records)
- **Monitoring**: Built-in dashboard and cost tracking

## Budget Breakdown

| Service | Monthly Cost | Usage |
|---------|-------------|--------|
| **OpenAI API** | $10-20 | ~1M tokens for analysis |
| **Apify** | $49 + usage | Ethical web scraping |
| **Twilio** | $20-30 | 50-100 emails/SMS |
| **SendGrid** | Included | Email delivery |
| **Airtable** | Free | Database storage |
| **Calendly** | $10 | Call scheduling |
| **Total** | **<$150** | Within budget limits |

## Support

### Documentation
- `/docs/FUNDAMENTAL_CONTEXT.md` - System architecture
- `/docs/PLANNER_BRIEF.md` - Wedding requirements
- `/wedding_specs.json` - Detailed specifications

### Troubleshooting
```bash
# Check system health
python scripts/run_system.py --mode health-check

# Validate API connections
python scripts/setup.py --skip-deps

# View recent logs
tail -f logs/orchestrator_$(date +%Y%m%d).log
```

### Common Issues
1. **API Key Errors**: Verify keys in `.env` file
2. **Budget Exceeded**: Check cost report and adjust limits
3. **No Responses**: Review outreach templates and timing
4. **Scraping Failures**: Check Apify credits and status

## Development

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/test_agents.py -v

# Integration tests
pytest tests/test_system_integration.py -v
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## License

This project is private and confidential. All rights reserved.

## Contact

For questions or support:
- **Project**: Wedding Planner Hiring System
- **Timeline**: August 13 - September 1, 2025
- **Purpose**: Hire planner for January 2026 Chinese banquet wedding

---

*🎯 Built with Claude Code for autonomous wedding planner discovery and hiring*
