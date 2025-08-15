# Wedding Planner Hiring System: Complete Setup & Execution Guide

> **🎯 Goal**: Successfully hire 1-3 qualified wedding planners for an authentic Chinese banquet wedding with city pop fusion elements by September 1, 2025.

## 📋 Pre-Execution Checklist

### ✅ Prerequisites (Complete First)
- [ ] Python 3.8+ installed
- [ ] Git installed and configured
- [ ] Access to all required API services
- [ ] Airtable account created
- [ ] Email account for wedding communications
- [ ] Phone number for SMS communications
- [ ] ~2-3 hours available over 2 weeks for human oversight

### ✅ Required API Accounts & Keys
Before starting, ensure you have accounts and API keys for:

1. **OpenAI** (Required)
   - Sign up at: https://platform.openai.com/
   - Get API key from: https://platform.openai.com/api-keys
   - Add $20 minimum credit balance
   - **Estimated Cost**: $10-20/month

2. **Airtable** (Required)
   - Sign up at: https://airtable.com/
   - Create new base (we'll configure schema)
   - Get API key from: https://airtable.com/developers/web/api/introduction
   - **Cost**: Free (up to 1,200 records)

3. **Apify** (Required)
   - Sign up at: https://apify.com/
   - Get API token from: https://console.apify.com/account#/integrations
   - Add $49 starter credit
   - **Estimated Cost**: $49 + $20-30 usage

4. **Twilio** (Required)
   - Sign up at: https://www.twilio.com/
   - Get Account SID and Auth Token
   - Verify phone number for SMS
   - **Estimated Cost**: $20-30/month

5. **SendGrid** (Required)
   - Sign up at: https://sendgrid.com/
   - Get API key from dashboard
   - Verify sender email domain
   - **Cost**: Included with Twilio or free tier

6. **Calendly** (Optional but Recommended)
   - Sign up at: https://calendly.com/
   - Get API token for automated scheduling
   - **Cost**: $10/month

---

## 🚀 Part 1: System Setup (30-45 minutes)

### Step 1: Environment Setup

```bash
# Navigate to project directory
cd cawedding

# Run setup script
python scripts/setup.py

# If setup script finds issues, fix them before proceeding
```

**Expected Output:**
```
🎯 Starting Wedding Planner Hiring System Setup
✅ Python 3.9.0 detected
✅ Creating directories completed
✅ Creating .env template completed
✅ Installing dependencies completed
✅ Setting up credentials completed
✅ Validating API connections completed
✅ Setup completed successfully!
```

### Step 2: Configure API Keys

```bash
# Edit .env file with your actual API keys
nano .env  # or use your preferred editor
```

**Required Configuration:**
```bash
# OpenAI (Required)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Airtable (Required)
AIRTABLE_API_KEY=your-airtable-api-key
AIRTABLE_BASE_ID=your-airtable-base-id

# Apify (Required)
APIFY_API_TOKEN=your-apify-token

# Twilio (Required)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token

# SendGrid (Required)
SENDGRID_API_KEY=your-sendgrid-key

# Optional but recommended
CALENDLY_ACCESS_TOKEN=your-calendly-token
```

### Step 3: Airtable Database Setup

1. **Create New Airtable Base:**
   - Go to https://airtable.com/
   - Click "Create a base" → "Start from scratch"
   - Name it: "Wedding Planner Hiring System"

2. **Configure Tables:**
   The system will auto-create the following tables:
   - **Planners**: Main planner data and scores
   - **Communications**: Email/SMS tracking
   - **Calls**: Call scheduling and notes
   - **Logs**: System audit trail

3. **Get Base ID:**
   - In Airtable, go to Help → API Documentation
   - Copy the Base ID (starts with "app...")
   - Add to your .env file

### Step 4: Email Configuration

**Update Sender Information:**
```bash
# Edit the outreach agent configuration
nano src/agents/outreach_agent.py
```

**Find and update these lines (~line 150):**
```python
self.sender_info = {
    "from_email": "your-email@domain.com",  # Your actual email
    "from_name": "Your Name",               # Your actual name
    "reply_to": "your-email@domain.com",    # Your actual email
    "phone_number": "+1234567890"           # Your actual phone
}
```

### Step 5: Validation Test

```bash
# Validate setup
python scripts/setup.py --skip-deps --skip-validation=false

# Expected output should show all APIs as "Valid"
```

---

## 🎯 Part 2: Pre-Execution Configuration (15-30 minutes)

### Step 1: Review Wedding Specifications

```bash
# Review current specifications
cat wedding_specs.json
```

**Verify these match your requirements:**
- Wedding date (currently: January 2026)
- Location (currently: Orange County, CA)
- Guest count (currently: 200-220)
- Budget (currently: $25-30K total, $3-5K planner fee)

**To modify specifications:**
```bash
nano wedding_specs.json
```

### Step 2: Customize Search Keywords

**Review and adjust cultural keywords:**
```bash
nano src/agents/researcher_agent.py
```

**Look for these keyword lists (~line 50-80) and adjust if needed:**
```python
self.multicultural_keywords = [
    "chinese wedding", "asian wedding", "multicultural", "tea ceremony",
    "fusion wedding", "bilingual", "cantonese", "mandarin", "taiwanese",
    # Add any specific terms important to your family
]
```

### Step 3: Customize Outreach Templates

**Review email templates:**
```bash
cat templates/planner_outreach.txt
```

**Customize if needed:**
```bash
nano templates/planner_outreach.txt
```

**Key customization points:**
- Personal names (currently "Jason & Suzie")
- Contact information
- Specific wedding date
- Family background details

---

## 🚀 Part 3: System Execution (2 weeks, ~3 hours human time)

### Phase 1: Research & Analysis (Days 1-4)

**Start the system:**
```bash
# Full workflow with monitoring
python scripts/run_system.py

# Alternative: Dry run first to test
python scripts/run_system.py --dry-run
```

**What Happens Automatically:**
1. **Researcher Agent** scrapes 20-50 planners from:
   - Instagram (hashtags: #OCWeddingPlanner, #AsianWeddingOC, etc.)
   - WeddingWire (Orange County multicultural planners)
   - The Knot (Asian wedding specialists)

2. **Analyzer Agent** scores each planner on:
   - **40%** Multicultural fit (Chinese wedding experience)
   - **30%** Timeline availability (can handle 3-4 month planning)
   - **30%** Reviews and reputation

3. **System generates shortlist** of top 5-10 planners

**🚨 HUMAN ACTION REQUIRED:**
```
HUMAN APPROVAL REQUIRED: shortlist_approval | Generated shortlist of 8 planners: 
Sarah Chen (8.5), Maria Rodriguez (8.2), David Kim (7.9), Lisa Wong (7.7), ...
```

**Your Response Options:**
- **Approve**: Continue with current shortlist
- **Modify**: Remove specific planners or request different criteria
- **Reject**: Restart research with adjusted parameters

**Monitor Progress:**
```bash
# Check status in separate terminal
python scripts/run_system.py --mode dashboard

# Or check cost usage
python scripts/run_system.py --mode cost-report
```

### Phase 2: Outreach Campaign (Days 5-12)

**What Happens Automatically:**
1. **Outreach Agent** sends personalized emails to shortlisted planners
2. **Follow-up system** sends reminders after 48 hours
3. **Response tracking** monitors replies and engagement

**🚨 HUMAN ACTION REQUIRED:**
```
HUMAN APPROVAL REQUIRED: outreach_batch_approval | 
Campaign: initial_outreach
Batch size: 5
Planners to contact:
- Sarah Chen (instagram)
- Maria Rodriguez (weddingwire)
- David Kim (theknot)
...
```

**Email Preview Example:**
```
Subject: Wedding Planner Needed - Authentic Chinese Banquet with Modern Twists (January 2026)

Dear Sarah,

We're seeking a wedding planner for an authentic 80s/90s-style Chinese restaurant 
wedding in Orange County, scheduled for January 2026. Your Chinese wedding experience 
and tea ceremony coordination caught our attention through your Instagram profile 
@sarahchenplanning.

Timeline is urgent - we need to begin planning within weeks for our 3-4 month 
execution window.

Available for a 15-20 minute call this week?

Best regards,
Jason & Suzie
```

**Your Response Options:**
- **Approve Batch**: Send emails to this group
- **Edit Templates**: Modify message content
- **Skip Planners**: Remove specific planners from batch
- **Delay**: Postpone this batch

**Monitor Responses:**
```bash
# Check response status
python scripts/manage_system.py status
```

### Phase 3: Response Management & Call Scheduling (Days 8-12)

**What Happens Automatically:**
1. **System processes responses** from planners
2. **Calendly integration** (if configured) helps schedule calls
3. **Follow-up management** for non-responders

**🚨 HUMAN ACTION REQUIRED - Call Coordination:**
```
HUMAN APPROVAL REQUIRED: call_coordination | 
Ready to coordinate calls with 4 responding planners:
- Sarah Chen: Interested, available this week
- David Kim: Very interested, sent portfolio
- Lisa Wong: Available for quick call
- Jennifer Liu: Interested but timeline concern
```

**Your Tasks:**
1. **Schedule intro calls** (15-20 minutes each)
2. **Prepare questions** (system provides suggested list)
3. **Conduct calls** and take notes
4. **Update system** with call results

**Suggested Call Questions:**
- How many Chinese banquet weddings have you planned?
- Experience with venues like Capital Seafood?
- Comfort with 3-4 month timeline?
- Availability for January 2026?
- Approach to authentic traditions + modern elements?
- Previous tea ceremony coordination?
- Bilingual MC connections?
- Portfolio examples of fusion elements?

**After Each Call:**
```bash
# Update call results (system will provide interface)
python scripts/manage_system.py update-call [planner-id]
```

### Phase 4: Final Decision (Days 13-14)

**What Happens Automatically:**
1. **Analyzer compiles** all call data and scores
2. **System generates** final recommendations with rationale
3. **Cost summary** and timeline analysis provided

**🚨 HUMAN ACTION REQUIRED - Final Decision:**
```
HUMAN APPROVAL REQUIRED: final_decision | 
Final recommendation among 3 interviewed planners:

RANK 1: Sarah Chen - Score: 9.2/10
✅ 15+ Chinese banquet weddings
✅ Capital Seafood experience  
✅ Available January 2026
✅ Excellent tea ceremony coordination
✅ Bilingual MC network
⚠️  Slightly over budget ($5.5K vs $5K target)

RANK 2: David Kim - Score: 8.8/10
✅ 8 multicultural weddings including Chinese
✅ Available timeline
✅ Modern fusion experience
✅ Within budget ($4.5K)
⚠️  Less traditional tea ceremony experience

RANK 3: Lisa Wong - Score: 8.1/10
✅ Strong cultural background
✅ Available January 2026  
✅ Within budget ($4K)
⚠️  Only 3 previous Chinese weddings
⚠️  No Orange County venue experience
```

**Your Decision Options:**
1. **Hire Primary Choice**: Proceed with top-ranked planner
2. **Hire Multiple**: Hire 2-3 planners for different roles
3. **Request More Calls**: Interview additional candidates
4. **Restart Process**: Adjust criteria and find new candidates

---

## 📊 Part 4: Monitoring & Management

### Real-Time Monitoring

**Dashboard View:**
```bash
# Live system status
python scripts/run_system.py --mode dashboard
```

**Sample Dashboard Output:**
```
🎯 WEDDING PLANNER HIRING SYSTEM - DASHBOARD
📅 2025-08-15 14:30:25
⏱️ Uptime: 24.5 hours

📊 WORKFLOW PROGRESS:
  Current Phase: OUTREACH
  Phase Progress: 75.0%
  Total Progress: 45.0%
  Est. Completion: 2025-08-27 18:00

👥 PLANNER PIPELINE:
  📊 Discovered: 32
  ⭐ Shortlisted: 8
  📞 Contacted: 8
  💬 Responding: 4
  📅 Calls Scheduled: 3
  ✅ Calls Completed: 1
  🎉 Hired: 0

💰 BUDGET STATUS:
  Spent: $78.50 / $150.00 (52.3%)
  Remaining: $71.50
  Daily Burn: $3.25

🤖 AGENT STATUS:
  🟢 RESEARCHER: Tasks: 15 | Success: 95.0% | Errors: 1
  🟢 ANALYZER: Tasks: 8 | Success: 100.0% | Errors: 0  
  🟡 OUTREACH: Tasks: 12 | Success: 85.0% | Errors: 2
```

### Cost Monitoring

**Check Budget Status:**
```bash
python scripts/run_system.py --mode cost-report
```

**Budget Alert Example:**
```
⚠️ WARNING: Over 75% of monthly budget used
🚨 PROJECTION: Current burn rate will exceed budget by $23.50
```

### System Health Checks

**Regular Health Monitoring:**
```bash
python scripts/run_system.py --mode health-check
```

**Health Check Output:**
```
✅ SYSTEM HEALTH: HEALTHY
Health Score: 87.5/100

Uptime: 36.2 hours
Progress: 65.0%
Budget Used: 62.3%
```

### Data Management

**Create Backups:**
```bash
# Regular backup (recommended daily)
python scripts/manage_system.py backup

# Export current results
python scripts/manage_system.py export --format csv
```

**System Status:**
```bash
# Quick status check
python scripts/manage_system.py status
```

---

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: API Authentication Errors
**Symptoms:** 
- Setup validation shows "Invalid" APIs
- System crashes with 401/403 errors

**Solutions:**
```bash
# Re-validate API keys
python scripts/setup.py --skip-deps

# Check .env file formatting
cat .env | grep -v "^#"

# Test individual API
python -c "
from src.utils.credentials import CredentialsManager
cm = CredentialsManager()
print(cm.validate_api_keys())
"
```

#### Issue 2: No Planners Discovered
**Symptoms:**
- Research phase completes with 0 planners
- All scraped data is filtered out

**Solutions:**
```bash
# Check search keywords
grep -n "multicultural_keywords" src/agents/researcher_agent.py

# Relax filtering criteria temporarily
# Edit researcher_agent.py, line ~200, change:
# if not matched_keywords:
#     return None
# TO:
# if len(matched_keywords) < 1:  # Allow some matches
#     return None

# Re-run research phase
python scripts/run_system.py --mode research-only
```

#### Issue 3: Budget Exceeded
**Symptoms:**
- Cost alerts showing over budget
- System stops with budget error

**Solutions:**
```bash
# Check detailed cost breakdown
python scripts/run_system.py --mode cost-report

# Common expensive operations:
# - OpenAI API calls (reduce analysis detail)
# - Apify scraping (reduce result count)

# Adjust budget limits in src/config.py:
nano src/config.py
# Change: MONTHLY_BUDGET_LIMIT = 150.0
# To: MONTHLY_BUDGET_LIMIT = 200.0
```

#### Issue 4: No Email Responses
**Symptoms:**
- All emails sent but 0% response rate
- Emails going to spam

**Solutions:**
```bash
# Check email template quality
cat templates/planner_outreach.txt

# Common issues:
# - Too generic/automated sounding
# - Missing personalization
# - Spam trigger words

# Test with single email first
# Edit outreach campaign batch_size to 1

# Verify sender reputation
# Check SendGrid sender verification
```

#### Issue 5: Airtable Connection Issues
**Symptoms:**
- Database errors during planner storage
- "Table not found" errors

**Solutions:**
```bash
# Verify Airtable base ID
echo $AIRTABLE_BASE_ID

# Check table creation
python -c "
from src.database.airtable_client import AirtableClient
client = AirtableClient()
print('Connection successful')
"

# Manually create tables if needed
# Go to Airtable → Your Base → Add Table
# Name: Planners, Communications, Calls, Logs
```

### Emergency Procedures

#### System Recovery After Crash
```bash
# Check last successful state
tail -100 logs/orchestrator_$(date +%Y%m%d).log

# Resume from checkpoint (if implemented)
python scripts/run_system.py --resume

# Otherwise, restart with existing data
python scripts/run_system.py --skip-research
```

#### Data Corruption Recovery
```bash
# Restore from backup
python scripts/manage_system.py backup  # Create current backup first
ls backups/  # Find latest good backup
# Manually restore from backup_YYYYMMDD_HHMMSS/

# Validate data integrity
python scripts/manage_system.py status
```

#### Budget Emergency Stop
```bash
# Immediate system halt
kill -TERM $(pgrep -f "run_system.py")

# Check final costs
python scripts/run_system.py --mode cost-report

# Export current data
python scripts/manage_system.py export --format json
```

---

## 📈 Success Metrics & Expected Outcomes

### Quantitative Success Metrics
- **Planners Discovered**: 20-50 (Target: 30+)
- **Shortlist Quality**: 5-10 planners scoring 6.0+ (Target: 8+)
- **Response Rate**: 30-60% (Target: 40%+)
- **Call Conversion**: 3-5 scheduled calls (Target: 4+)
- **Hiring Success**: 1-3 planners hired (Target: 2)
- **Budget Adherence**: <$150/month (Target: <$120)
- **Human Time**: <3 hours total (Target: <2.5 hours)

### Qualitative Success Indicators
- **Cultural Fit**: Planners demonstrate understanding of Chinese traditions
- **Timeline Comfort**: Planners confident with 3-4 month execution
- **Communication Quality**: Responsive, professional, detail-oriented
- **Portfolio Relevance**: Previous work shows multicultural expertise
- **Vendor Network**: Connections to bilingual MCs, Asian florists, etc.

### Timeline Expectations
```
Day 1-2:   Setup and initial research      (30 min human time)
Day 3-4:   Analysis and shortlist approval (45 min human time) 
Day 5-8:   Outreach campaign launch       (30 min human time)
Day 9-12:  Response management and calls  (90 min human time)
Day 13-14: Final decision and hiring      (30 min human time)

Total Human Time: ~3.5 hours over 2 weeks
Total System Cost: $80-120
Success Rate: 85% (hire 1+ qualified planners)
```

---

## 🎯 Final Pre-Launch Checklist

### ✅ Technical Readiness
- [ ] All API keys validated and working
- [ ] Airtable base created with correct permissions
- [ ] Email/SMS sender information configured
- [ ] Backup and monitoring systems tested
- [ ] Cost tracking and alerts configured

### ✅ Content Readiness  
- [ ] Wedding specifications reviewed and accurate
- [ ] Email templates personalized with your information
- [ ] Search keywords adjusted for your preferences
- [ ] Cultural requirements clearly defined
- [ ] Budget limits set appropriately

### ✅ Process Readiness
- [ ] Calendar cleared for approval gates and calls
- [ ] Phone/email accessible for urgent notifications
- [ ] Decision criteria established for final selection
- [ ] Backup plans prepared for low response scenarios
- [ ] Success metrics and timeline expectations set

### ✅ Human Readiness
- [ ] Understanding of 4-phase workflow process
- [ ] Comfort with AI-generated communications
- [ ] Prepared questions for planner interviews
- [ ] Budget authorization for selected planners
- [ ] Timeline alignment with January 2026 wedding

---

## 🚀 Launch Command

Once all checklists are complete:

```bash
# Final system validation
python scripts/run_system.py --mode health-check

# Launch complete workflow
python scripts/run_system.py

# Monitor in separate terminal
python scripts/run_system.py --mode dashboard
```

**Expected First Output:**
```
🎯 Starting Wedding Planner Hiring System
🚀 Starting workflow execution...
📊 Monitoring dashboard enabled

=== RESEARCH PHASE ===
[14:30:25] Starting Instagram scraping for #OCWeddingPlanner...
[14:31:15] Found 12 potential planners from Instagram
[14:32:30] Starting WeddingWire scraping...
[14:34:45] Found 8 potential planners from WeddingWire
[14:35:00] Starting analysis of 20 discovered planners...
```

Your AI-powered wedding planner hiring system is now operational! 🎉

---

## 📞 Support & Next Steps

### If You Need Help
1. **Check logs**: `tail -f logs/orchestrator_$(date +%Y%m%d).log`
2. **Review this guide**: Most issues covered in troubleshooting
3. **System status**: `python scripts/manage_system.py status`
4. **Create backup**: `python scripts/manage_system.py backup`

### After Hiring Success
1. **Export final results**: `python scripts/manage_system.py export`
2. **Create complete backup**: `python scripts/manage_system.py backup`
3. **Generate final report**: System will auto-generate upon completion
4. **Share feedback**: Document lessons learned for future improvements

The system is designed to be largely autonomous while keeping you in control of all critical decisions. Trust the AI for research and analysis, but rely on your human judgment for final planner selection.

**Good luck with your wedding planner search!** 🎉💒