# Quick Start Guide

> **Purpose**: Get the AI-powered wedding planner hiring system up and running quickly  
> **Time to Complete**: ~30 minutes  
> **Prerequisites**: Node.js v18+, npm, git

---

## Prerequisites Checklist

Run these commands to verify your environment:

```bash
# Check Node.js version (v18+ recommended)
node --version

# Check npm (comes with Node.js)
npm --version

# Verify git installed
git --version
```

---

## 1. Environment Setup

### Clone and Install

```bash
# Clone repository (if applicable)
cd /Users/caffeinated/creator/cawedding

# Install dependencies
npm install

# Install TypeScript and ts-node globally if needed (for running .ts files directly)
npm install -g typescript ts-node
```

---

## 2. API Keys Configuration

### Create Environment File

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

### Required API Keys

| Service | Purpose | Where to Get |
|---------|---------|--------------|
| **Anthropic** | Claude AI orchestration | [Anthropic Console](https://console.anthropic.com/) |
| **OpenAI** | GPT-4o analysis | [OpenAI Platform](https://platform.openai.com/) |
| **Airtable** | Database storage | [Airtable API](https://airtable.com/api) |
| **Apify** | Web scraping | [Apify Console](https://console.apify.com/) |
| **Twilio** | Email/SMS communications | [Twilio Console](https://console.twilio.com/) |
| **Calendly** | Call scheduling | [Calendly API](https://developer.calendly.com/) |

---

## 3. Database Setup

### Initialize Airtable

```bash
# Initialize Airtable bases (run the setup script)
ts-node scripts/setup_airtable.ts

# Verify connection
ts-node -e 'const { Airtable } = require("@airtable/airtable.js"); console.log("Airtable connected");'
```

---

## 4. Run Commands

### Start Full Pipeline

```bash
# Run all agents in sequence
ts-node src/orchestrator/index.ts --specs wedding_specs.json --mode full

# Run with human gates (recommended)
ts-node src/orchestrator/index.ts --specs wedding_specs.json --mode supervised
```

### Run Individual Agents

```bash
# Research only
ts-node src/agents/researcher.ts --hashtags "OCWeddingPlanner,AsianWeddingOC" --limit 50

# Analyze only (requires existing data)
ts-node src/agents/analyzer.ts --input airtable --output shortlist.csv

# Outreach only (requires approved shortlist)
ts-node src/agents/outreach.ts --list shortlist.csv --template templates/initial_contact.txt
```

### Monitor Progress

```bash
# Check agent status
ts-node src/monitor.ts --status

# View logs
tail -f logs/agents.log

# Check Airtable data
ts-node scripts/check_data.ts --table planners
```

---

## 5. Test Commands

### System Verification

```bash
# Test scraper (dry run)
ts-node src/agents/researcher.ts --test --limit 5

# Test email template
ts-node src/agents/outreach.ts --test-email your-email@example.com

# Validate data quality
ts-node scripts/validate.ts --check-scores

# API quota check
ts-node scripts/check_quotas.ts
```

---

## 6. Common Operations

### Update Wedding Specs

```bash
# Edit JSON file
nano wedding_specs.json

# Validate JSON (using Node.js)
node -e 'require("fs").readFileSync("wedding_specs.json", "utf8"); console.log("JSON valid");'
```

### Manual Overrides

```bash
# Skip a planner
ts-node scripts/manual.ts --skip-planner "Planner Name"

# Add planner manually
ts-node scripts/manual.ts --add-planner --data planner_info.json

# Force retry failed outreach
ts-node src/agents/outreach.ts --retry-failed
```

### Export Results

```bash
# Export shortlist to CSV
ts-node scripts/export.ts --format csv --output results/shortlist.csv

# Generate PDF report (assuming pdf generation lib installed)
ts-node scripts/export.ts --format pdf --output results/report.pdf
```

---

## 7. Troubleshooting

### Common Issues

```bash
# Check API connectivity
ts-node scripts/test_apis.ts

# Clear cache (if applicable)
rm -rf node_modules/.cache/*

# Reset failed jobs
ts-node scripts/reset.ts --failed-only

# Debug mode (verbose logging)
ts-node src/orchestrator/index.ts --debug --specs wedding_specs.json

# Check rate limits
ts-node scripts/check_limits.ts --service all
```

### Troubleshooting Checklist

| Issue | Solution |
|-------|----------|
| **API connection errors** | Check `.env` file and API keys |
| **Rate limit exceeded** | Wait and retry, or upgrade plan |
| **Airtable sync issues** | Verify base ID and permissions |
| **Agent stuck** | Check logs and restart process |
| **Memory issues** | Reduce batch sizes or upgrade resources |

---

## 8. Emergency Stops

### Stop Operations

```bash
# Stop all agents
pkill -f "node.*agents"

# Pause outreach
touch .pause_outreach

# Resume outreach
rm .pause_outreach
```

---

## 9. Cost Monitoring

### Usage Tracking

```bash
# Check current usage
ts-node scripts/costs.ts --current-month

# Set alerts
ts-node scripts/costs.ts --set-alert 100
```

### Cost Breakdown

| Service | Typical Monthly Cost | Alert Threshold |
|---------|---------------------|-----------------|
| **Anthropic** | $10-20 | $25 |
| **OpenAI** | $10-20 | $25 |
| **Apify** | $49 | $75 |
| **Twilio** | $20-30 | $50 |
| **Calendly** | $10 | $15 |
| **Total** | **<$150** | **$200** |

---

## 10. Quick Verification

### Run System Check

```bash
ts-node verify_setup.ts
```

### Expected Output

```
✓ Node.js v18+ installed
✓ All packages installed
✓ API keys configured
✓ Airtable connected
✓ Apify ready
✓ Twilio configured
✓ System ready to run
```

---

## 11. Support & Resources

### File Locations

| Type | Location |
|------|----------|
| **Logs** | `logs/agents.log` |
| **Config** | `.env`, `wedding_specs.json` |
| **Data** | Airtable (check base URL in `.env`) |
| **Documentation** | `docs/README.md` |

### Getting Help

- ✅ **Issues**: Check `docs/README.md` for context
- ✅ **API Limits**: Monitor usage with cost scripts
- ✅ **Agent Behavior**: Run in supervised mode first
- ✅ **Data Issues**: Validate with check scripts

---

## ⚠️ Important Reminders

> **Always run in supervised mode first** to verify agent behavior before full automation.

### Best Practices

- ✅ Test with small datasets before full runs
- ✅ Monitor costs regularly
- ✅ Keep API keys secure
- ✅ Backup important data
- ✅ Review agent outputs before proceeding

### Safety Checks

- ✅ Verify email templates before sending
- ✅ Check planner data quality
- ✅ Validate cultural fit scores
- ✅ Confirm timeline availability
- ✅ Review compliance with ethics guidelines