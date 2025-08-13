# Quick Start Guide

## Prerequisites Checklist

```bash
# Check Python version (3.8+ required)
python --version

# Check Node.js (for Calendly/Twilio integrations)
node --version

# Verify git installed
git --version
```

## 1. Environment Setup

```bash
# Clone repository (if applicable)
cd /Users/caffeinated/creator/cawedding

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install crewai openai airtable-python-wrapper twilio apify-client
pip install python-dotenv requests pandas
```

## 2. API Keys Configuration

Create `.env` file in project root:

```bash
# Create .env file
cat > .env << 'EOF'
# AI APIs
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Data Storage
AIRTABLE_API_KEY=your_airtable_key_here
AIRTABLE_BASE_ID=your_base_id_here

# Scraping
APIFY_API_TOKEN=your_apify_token_here

# Communications
TWILIO_ACCOUNT_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_token_here
TWILIO_PHONE_NUMBER=+1234567890
CALENDLY_API_TOKEN=your_calendly_token_here

# Email Config
SENDER_EMAIL=wedding-ai@yourdomain.com
EOF
```

## 3. Database Setup

```bash
# Initialize Airtable bases
python scripts/setup_airtable.py

# Verify connection
python -c "from airtable import Airtable; print('Airtable connected')"
```

## 4. Run Commands

### Start Full Pipeline
```bash
# Run all agents in sequence
python main.py --specs wedding_specs.json --mode full

# Run with human gates (recommended)
python main.py --specs wedding_specs.json --mode supervised
```

### Run Individual Agents
```bash
# Research only
python agents/researcher.py --hashtags "OCWeddingPlanner,AsianWeddingOC" --limit 50

# Analyze only (requires existing data)
python agents/analyzer.py --input airtable --output shortlist.csv

# Outreach only (requires approved shortlist)
python agents/outreach.py --list shortlist.csv --template templates/initial_contact.txt
```

### Monitor Progress
```bash
# Check agent status
python monitor.py --status

# View logs
tail -f logs/agents.log

# Check Airtable data
python scripts/check_data.py --table planners
```

## 5. Test Commands

```bash
# Test scraper (dry run)
python agents/researcher.py --test --limit 5

# Test email template
python agents/outreach.py --test-email your-email@example.com

# Validate data quality
python scripts/validate.py --check-scores

# API quota check
python scripts/check_quotas.py
```

## 6. Common Operations

### Update Wedding Specs
```bash
# Edit JSON file
nano wedding_specs.json

# Validate JSON
python -m json.tool wedding_specs.json
```

### Manual Overrides
```bash
# Skip a planner
python scripts/manual.py --skip-planner "Planner Name"

# Add planner manually
python scripts/manual.py --add-planner --data planner_info.json

# Force retry failed outreach
python agents/outreach.py --retry-failed
```

### Export Results
```bash
# Export shortlist to CSV
python scripts/export.py --format csv --output results/shortlist.csv

# Generate PDF report
python scripts/export.py --format pdf --output results/report.pdf
```

## 7. Troubleshooting

```bash
# Check API connectivity
python scripts/test_apis.py

# Clear cache
rm -rf .cache/*

# Reset failed jobs
python scripts/reset.py --failed-only

# Debug mode (verbose logging)
python main.py --debug --specs wedding_specs.json

# Check rate limits
python scripts/check_limits.py --service all
```

## 8. Emergency Stops

```bash
# Stop all agents
pkill -f "python.*agents"

# Pause outreach
touch .pause_outreach

# Resume outreach
rm .pause_outreach
```

## 9. Cost Monitoring

```bash
# Check current usage
python scripts/costs.py --current-month

# Set alerts
python scripts/costs.py --set-alert 100
```

## Quick Verification

Run this to verify everything is working:

```bash
python verify_setup.py
```

Expected output:
```
✓ Python 3.8+ installed
✓ All packages installed
✓ API keys configured
✓ Airtable connected
✓ Apify ready
✓ Twilio configured
✓ System ready to run
```

## Support

- Logs location: `logs/agents.log`
- Config location: `.env`, `wedding_specs.json`
- Data location: Airtable (check base URL in .env)
- Issues: Check `docs/README.md` for context

---

**Remember**: Always run in supervised mode first to verify agent behavior before full automation.