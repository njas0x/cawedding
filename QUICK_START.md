# 🚀 Quick Start Guide - AI Wedding Planner System

You're **30 minutes away** from having an AI system find your perfect wedding planner!

## Current Status: 95% Complete ✅

The system is fully built and tested. You just need to add API keys and run it.

---

## Step 1: Get Your API Keys (15 minutes)

### Required APIs (for full functionality):

#### 1. OpenAI API Key (Required)
- Go to: https://platform.openai.com/api-keys
- Create new key
- Cost: ~$10-20 for complete run

#### 2. Airtable (Required)
- Sign up free: https://airtable.com/signup
- Create new base called "Wedding Planners"
- Get API key: https://airtable.com/create/tokens
- Get Base ID: In Airtable, go to Help → API Documentation → find your base ID

#### 3. Optional APIs (can skip for dry-run):
- **Apify**: For web scraping (can use mock data instead)
- **Twilio/SendGrid**: For email/SMS (can simulate instead)

### Add Keys to .env File:

```bash
# Edit the .env file
nano .env

# Add your keys:
OPENAI_API_KEY=sk-...your-key-here...
AIRTABLE_API_KEY=pat...your-key-here...
AIRTABLE_BASE_ID=app...your-base-id...

# Optional (leave as-is for dry run):
APIFY_API_TOKEN=your_apify_api_token_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

---

## Step 2: Install & Test (10 minutes)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Test your setup
python scripts/setup.py --validate-all

# 3. Run a dry-run test (no API costs)
python scripts/run_system.py --dry-run
```

If the dry-run works, you're ready!

---

## Step 3: Run the System (5 minutes to start)

### Option A: Full Automated Run
```bash
# Run the complete system
python scripts/run_system.py

# The system will:
# 1. Search for 20-50 planners
# 2. Score and rank them
# 3. Request your approval for shortlist
# 4. Send outreach emails (with your approval)
# 5. Track responses and schedule calls
```

### Option B: Test with Limited Scope
```bash
# Run with just research phase (no emails)
python scripts/simple_dry_run.py

# This will:
# - Find planners
# - Score them
# - Generate report
# - No actual outreach
```

### Option C: Monitor Progress
```bash
# In a separate terminal, watch the dashboard
python scripts/run_system.py --mode dashboard
```

---

## 🎯 What Happens Next?

### Phase 1 (Days 1-4): Research
- AI searches Instagram, WeddingWire, The Knot
- Finds 20-50 potential planners
- Scores based on Chinese wedding experience
- Generates shortlist of top 10

**Your involvement**: Approve shortlist (15 min)

### Phase 2 (Days 5-12): Outreach
- AI drafts personalized emails
- Sends with your approval
- Tracks responses
- Schedules calls via Calendly

**Your involvement**: Approve email batches (15 min)

### Phase 3 (Days 13-14): Decision
- You conduct calls (2-3 hours)
- AI helps track notes
- AI generates comparison matrix
- You make final decision

**Your involvement**: Calls + decision (3 hours)

---

## 💰 Cost Breakdown

- **OpenAI API**: $10-20 (analysis and personalization)
- **Airtable**: Free (under 1,200 records)
- **Apify**: $0-49 (can skip with manual search)
- **Twilio/SendGrid**: $10-20 (50-100 emails)
- **Total**: $20-100 depending on usage

---

## 🚨 Troubleshooting

### If you get API errors:
```bash
# Check your credentials
python scripts/setup.py --validate-all

# Look for which API is failing
# You can run without some APIs:
export DRY_RUN=true  # Skips all external APIs
python scripts/run_system.py
```

### If you want to stop:
- Press Ctrl+C anytime to gracefully stop
- Data is saved continuously
- Can resume with: `python scripts/run_system.py`

### If unsure about the system:
```bash
# Run the safe test version first
python scripts/simple_dry_run.py

# This shows what would happen without doing anything
```

---

## 📊 Monitoring Your Results

Check progress anytime:
```bash
# View system status
python scripts/run_system.py --mode health-check

# See cost tracking
python scripts/run_system.py --mode cost-report

# Check database
python scripts/manage_system.py status
```

---

## 🎉 Success Metrics

You'll know it's working when:
- ✅ Found 20+ planners with Chinese wedding experience
- ✅ Shortlist has 5-10 strong candidates
- ✅ Getting responses to outreach
- ✅ Calls scheduled with 3-5 planners
- ✅ Total human time: <3 hours

---

## 🤝 Hybrid Approach (Recommended)

While the AI system runs, you can also:
1. Use the manual search templates in `/manual_search/`
2. Cross-reference AI findings with your own research
3. Add manually found planners to the AI system for scoring

Best of both worlds!

---

## Next Step:

```bash
# Right now, just run:
python scripts/setup.py --validate-all

# If all green, you're ready to go!
```

Questions? The system has extensive logging and will guide you through each step.

Good luck finding your perfect wedding planner! 🎊