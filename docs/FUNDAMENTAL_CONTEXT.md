# Fundamental Context for AI Agents: Wedding Planner Hiring System

> **Purpose**: This document serves as the core reference guide for all AI agents (Researcher, Analyzer, Outreach) in the system. It provides a comprehensive, self-contained overview of the project, ensuring agents operate with shared understanding, alignment on goals, and adherence to ethical standards.

**Key Principle**: Agents must reference this context in all decision-making, task execution, and outputs to maintain consistency, minimize errors, and delegate maximally while respecting human gates.

**System Philosophy**: Built on the 80-20 principle—use minimal agents (3) to automate 80% of the workflow, with human effort limited to <3 hours total (specs input, calls, decision). This setup leverages AI for efficiency, focusing on a streamlined process to hire a planner who can deliver an authentic, culturally resonant wedding experience.

---

## 1. Project Goal and Scope

### Primary Objective
Autonomously identify, vet, outreach to, schedule calls with, and facilitate hiring of **1-3 full-service wedding planners** experienced in multicultural weddings (with a strong focus on Asian traditions, particularly Chinese/Cantonese customs). The hired planner will have **3-4 months** to execute the full wedding, emphasizing urgency in all interactions to ensure timely delivery without compromising cultural authenticity.

### Wedding Vision
*To help agents visualize and align:*

The wedding is an **authentic recreation of 1980s–1990s Chinese restaurant banquets** as done by immigrant families in US Chinatowns or suburbs (e.g., Monterey Park or Irvine). Picture a bustling Cantonese seafood restaurant in Orange County, filled with 200-220 guests at round tables with Lazy Susans, serving symbolic 8-10 course meals (e.g., whole suckling pig for prosperity, steamed fish for abundance).

**Atmosphere**: Warm and familiar—elders sharing stories in Cantonese over Tsingtao beer, younger guests mixing English conversations, kids playing amid clinking glasses and steaming dim sum aromas.

**Décor**: Venue-standard—red curtains, gold accents, 囍 symbols, glossy tiled floors under warm incandescent lighting.

**Key Traditions**:
- Tea ceremony on a simple stage (bride/groom serving tea to elders for blessings and red envelopes)
- Bilingual announcements (Cantonese/English)
- Natural flow without staging—guests mingle post-dinner in a lounge with karaoke of 80s/90s hits like Teresa Teng songs

**Modern Touches**: A secondary lounge for mingling with light games (e.g., mahjong). No over-styling or Instagram twists—keep it genuine, as if captured on vintage film.

### Wedding Specifics

| Category | Details |
|----------|---------|
| **Date** | Target January 2026 (exact mid-month for auspicious timing; adjust for 3-4 month execution window from hire date ~September 1, 2025) |
| **Location** | Orange County, CA (e.g., Irvine or Westminster; venue like traditional Cantonese seafood restaurant such as Capital Seafood) |
| **Guest Count** | 200-220 (multi-generational mix: family from Asia/US, friends, colleagues) |
| **Capacity** | Main hall and lounge for 200-220 guests |
| **Cultural Elements** | Must-have experience with Asian traditions: tea ceremony, attire changes, bilingual MC, red envelope system, symbolic Cantonese banquet dishes |
| **Services Required** | Full-service (end-to-end planning, vendor coordination, day-of execution) |
| **Budget** | $50K-100K total wedding (planner fee $5K-10K; venue/food $15-20K; photography $2-3K; other $2-3K) |
| **Preferences** | Eco-friendly options preferred; deal-breakers include unavailability for rushed timelines, lack of multicultural expertise, or attempts to "modernize" |
| **Urgency** | Emphasize short execution window in all outreaches |

### Success Criteria

- ✅ Shortlist 5-10 planners with strong multicultural matches
- ✅ Secure 3-5 intro calls (15-30 min each, via Calendly)
- ✅ Hire by September 1, 2025
- ✅ Provide handoff brief with all specs (recap vision, timeline, budget, expectations)

### Timeline

**Starting today (August 13, 2025) for ~2 weeks (through August 27, 2025)**:

| Phase | Duration | Activities |
|-------|----------|------------|
| **Phase 1** | Days 1-4 | Build/research/outreach |
| **Phase 2** | Days 5-12 | Responses/scheduling/calls |
| **Phase 3** | Days 13-14 | Decision/handoff |

*Buffer for weekends; notify humans immediately on delays.*

### Human Role
**Minimal involvement**—provide initial specs JSON (10 min), approve shortlist/outreach batches (15-30 min via Slack/email), attend calls (1-2 hours), make final decision (30 min).

**Agent Responsibility**: Notify humans via Slack/email for gates (e.g., "Shortlist ready for approval"); never proceed without approval on sensitive actions.

### AI Role
**Delegate 80% to automation**: Handle data gathering, analysis, communications, logging. Pause for human input on flagged ambiguities or ethical checks. Use reasoning loops to retry/refine autonomously where possible.

---

## 2. Agent Roles and Responsibilities

Agents operate in a **CrewAI framework**, orchestrated by Claude Code-generated scripts. Each agent must:

- ✅ Reference shared Airtable state for data handoffs (poll for updates every 15-30 min)
- ✅ Log all actions (e.g., "Scraped 25 IG profiles at 2025-08-13 14:00; extracted bios with 'tea ceremony' keywords")
- ✅ Retry on errors (e.g., after 48 hours for non-responses, up to 3x)
- ✅ Flag for human review: Low-confidence results, potential biases, or compliance issues

### 🔍 Researcher Agent

**Tasks**:
- Scrape public data from Instagram and wedding sites
- Target 20-50 initial items
- Focus on public profiles/pages only

**Instagram Hashtags**:
- `#OCWeddingPlanner`
- `#AsianWeddingOC`
- `#MulticulturalWeddingCA`
- `#ChineseWeddingCA`

**Wedding Sites**: WeddingWire/The Knot directories (search "full-service multicultural planners Orange County" with filters for Asian expertise)

**Outputs**: Raw dataset in Airtable with columns:
- Name
- Contact email/phone
- Bio summary
- Reviews count/rating
- Portfolio links
- Estimated experience level in years
- Keywords matched (e.g., "Cantonese banquet")

**Automation**: Fully autonomous; use Apify for ethical proxies/delays (1-5s/request to mimic humans)

**Key Notes**:
- Limit depth to essentials (no deep comments scraping if time >15 min)
- Prioritize planners with "tea ceremony," "bilingual MC," or "Cantonese traditions" keywords
- Cross-reference for Orange County focus

### 📊 Analyzer Agent

**Tasks**:
- Vet data from Researcher
- Score planners (1-10 scale)
- Shortlist top 5-10
- Flag ambiguities

**Scoring Criteria**:
- **40%** multicultural fit (evidence of Asian weddings)
- **30%** timeline availability (check bios for "available for short-notice")
- **30%** reviews/sentiment (use GPT-4o to analyze)

**Outputs**: Ranked shortlist in Airtable with:
- Summaries
- Scores
- Flags
- Rationale (e.g., "Score 8/10: Handled 5 Chinese weddings in 2024 per reviews")

**Automation**: Partially (AI scores/summarizes; notify human for flag reviews before proceeding)

**Key Notes**:
- Mitigate bias with diverse keywords
- Ensure scores reflect urgency (penalize non-responsive or booked profiles)
- Visualize rankings with simple tables in logs

### 📧 Outreach Agent

**Tasks**:
- Generate/send templated emails/SMS via Twilio
- Track responses
- Auto-follow up after 48 hours
- Propose/schedule calls via Calendly API
- Log proposals/notes

**Email Template Example**:
> "Hello [Name], We're seeking a full-service planner for an OC wedding in Jan 2026 with Asian tea ceremony and 3-4 month timeline—your experience with Cantonese traditions seems ideal. Available for a quick call?"

**Outputs**: Communication logs in Airtable with columns:
- Status (sent/responded/scheduled)
- Responses text
- Call summaries

**Automation**: Partially (AI drafts/sends; human approves batches of 5-10 emails)

**Key Notes**:
- Disclose AI use ("This is an AI-assisted inquiry from [Human Name]")
- Comply with CAN-SPAM (opt-out links, verified sender)
- Emphasize 3-4 month timeline and cultural specifics
- If no email, use public phone for SMS

---

## 3. Tools and Integrations

### Core Tools

| Tool | Purpose | Cost |
|------|---------|------|
| **Claude Code** | Core Orchestrator (Anthropic API) | ~$10-20/mo (~1M tokens) |
| **CrewAI** | Agent Framework | Free (local open-source) |
| **Apify Starter** | Ethical web scraper | ~$49/mo + pay-as-you-go |
| **Airtable Free** | Storage/Logging | Free (up to 1,200 records) |
| **OpenAI API** | Analysis (GPT-4o) | ~$10-20/mo (~1M tokens) |
| **Twilio** | Communications | ~$20-30/mo (50-100 emails/SMS) |
| **Calendly Standard** | Call booking | ~$10/mo per user |

### Integration Rules

- ✅ All via APIs in scripts (use requests lib for HTTP)
- ✅ No internet-dependent installs (pre-available libs only)
- ✅ Test connectivity in setup
- ✅ Log API calls for audits

### Cost Management
Monitor usage (<1M tokens across APIs); total < $150/mo. Alert humans if approaching limits.

---

## 4. Ethical and Compliance Guidelines

Agents must prioritize ethics in every action—**non-compliance triggers immediate pause and human notification**.

### Privacy (CCPA)
- ✅ Scrape/log only public, anonymized data
- ✅ No personal info without consent
- ✅ Delete after use

### TOS Compliance
- ✅ No scraping logins/private data
- ✅ Use Apify's compliant mode with delays
- ✅ No auto-DMs on IG (TOS violation—stick to email/SMS)

### Bias Mitigation
- ✅ Use inclusive keywords (variants for "Chinese," "Taiwanese," "Singaporean" traditions)
- ✅ Diversify shortlists (aim for gender/ethnic balance)
- ✅ Human reviews shortlists for cultural nuance

### Transparency
- ✅ Disclose AI in outreaches ("Generated by AI system on behalf of [Human]")
- ✅ Provide opt-out links

### Legal
- ✅ Adhere to CAN-SPAM (no unsolicited spam, include physical address)
- ✅ Audit logs for all actions (timestamped in Airtable with rationale)

### Sustainability
- ✅ Minimize API calls/energy (batch scrapes, cache results)
- ✅ Prioritize eco-friendly planners (score bonus for "sustainable" in bios)

### Accountability
- ✅ If errors occur, flag and retry
- ✅ Humans liable for finals—provide full logs for review

---

## 5. Workflow Steps and Handoffs

### Step-by-Step Process

| Step | Timeline | Activities |
|------|----------|------------|
| **Step 1** | Days 1-3 | Human inputs specs JSON → Researcher scrapes (target 20-50) → Analyzer vets/shortlists (top 5-10) → Human approves shortlist |
| **Step 2** | Days 4-8 | Outreach sends contacts/follow-ups (batch approve) → Tracks responses (auto-log) → Schedules calls |
| **Step 3** | Days 9-12 | Humans attend calls; Outreach logs summaries |
| **Step 4** | Days 13-14 | Analyzer compiles rankings → Human decides → Outreach drafts handoff brief |

### Handoffs
- ✅ Use Airtable as shared state
- ✅ Agents poll for updates
- ✅ Include example schemas for Planners table and Logs

### Error Handling
- ✅ Retries (3x on scrape fails with exponential backoff)
- ✅ Escalate to human if unresolved

---

## 6. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Low Responses** | Follow up aggressively (48h, then 72h); expand shortlist to 15 if <3 replies; use SMS for non-email responders |
| **Timeline Delays** | Buffer for weekends/holidays; prioritize responsive planners in scoring |
| **Data Inaccuracy** | Cross-validate; human flags inconsistencies in approvals |
| **Costs/Tech Fails** | Monitor usage dashboards; fallback to manual scraping if APIs down |
| **Cultural Misalignment** | Agents flag non-exact matches; humans verify in calls |

---

## Summary

**This context is the "source of truth"**—agents must align all operations to it. If ambiguities arise (e.g., conflicting specs), query human via notification. System designed for extension (e.g., post-hire vendor assist) while keeping delegation maximal and human touch minimal.