# AI-Powered Wedding Planner Hiring System

> **Built with**: Node.js/TypeScript  
> **Purpose**: System to find and hire a wedding planner for an authentic 80s/90s Asian banquet wedding in Orange County, CA  
> **Philosophy**: Built on 80-20 principle—3 AI agents handle research and outreach with minimal human involvement

---

## 1. Wedding Vision

### Core Concept

- **Authentic 80s/90s Asian wedding banquet** - pragmatic, how it was actually done then for lower mid-class immigrant families
- **Modern comfort & relaxed energy** - especially second half with lounge area for mingling and subtle retro city pop vibes
- **Memorable for first-timers** - accessible traditions without over-choreography, evoking nostalgic warmth like family reunions in Hong Kong, Taipei, or Singapore

### Non-Negotiable Requirements

#### Venue Layout

| Area | Description |
|------|-------------|
| **Main Dining Area** | 200-220 guests at round tables with lazy Susans, stage for ceremonies; practical linoleum or worn tiled floors, plain white or pastel walls |
| **Lounge/Arcade** | Secondary space opening mid-evening for games (mahjong tables, card games, boombox with cassette tapes of Teresa Teng or Tatsuro Yamashita) and mingling; subtle city pop accents like string lights in teal/pink/purple, basic posters of sunset gradients |
| **Entrance Hall** | Welcome area with red envelope station, guestbook; simple signage |
| **Window Side** | Overlooking hazy night view of residential urban neighborhood (glowing apartments, street stalls); used for VIP seating or casual photo moments |

#### Program Anchors (Must Have)

- ✅ **Grand entrance** (2 min, to applause; light door games if family-led)
- ✅ **Tea ceremony** for parents/elders on stage (10-12 min; serve tea for blessings, exchange red envelopes)
- ✅ **Family toast + friend toast** (6-8 min total, keep short and heartfelt)
- ✅ **Cake/champagne moment** (3-4 min; simple cutting)
- ✅ **Group photo on stage** (5-7 min; quick and inclusive)
- ✅ **Table-to-table greetings** during dinner (organic, family-style)

#### Flow Structure

**6:00-7:45pm**: Everyone in main room for ceremonies and early courses; family chatter over symbolic dishes  
**7:45pm onward**: Lounge opens, free flow between zones with snacks (haw flakes, White Rabbit candy, prawn crackers)  
**MC recalls guests** from lounge for key moments (group photo, final thanks); karaoke with 80s/90s Cantonese hits

#### Atmosphere Goals

| Element | Description |
|---------|-------------|
| **Feel** | Warm, bustling, lived-in banquet - not overproduced; lively family conversations, kids playing, clinking glasses |
| **Look** | Venue's existing red/gold décor + minimal additions (paper 囍 cutouts, inexpensive market flowers in reds/golds); subtle city pop through faint neon-like accents in lounge |
| **Sound** | Nostalgic Cantopop or city pop (Teresa Teng, Tatsuro Yamashita), chatter, clinking dishes, eventual karaoke; low hum of conversation |
| **Taste** | Traditional 8-10 course Cantonese banquet (roast pig for prosperity, seafood/lobster for happiness, whole fish for abundance, longevity noodles) |
| **Memory** | Sensory details, candid moments, genuine cultural experience; as if captured on 35mm Kodak Gold film with warm tones and grain |

### What We Need From a Planner

#### Must Have Experience

- ✅ Chinese restaurant banquet weddings in Orange County (e.g., Capital Seafood, Sea Harbour)
- ✅ Managing dual-zone venues (dining + lounge with modest games)
- ✅ Working WITH restaurant's existing setup and package (no transformations)
- ✅ Coordinating traditional tea ceremonies and red envelope systems

#### Must Understand

- ✅ This is restaurant-run, not planner-produced; embrace their proven system
- ✅ Authenticity over Instagram aesthetics (no styling or modern twists)
- ✅ Natural flow over rigid timeline (let courses and conversations guide)
- ✅ Lower mid-class vibe: Practical, humble, family-focused without excess

#### Key Tasks

- ✅ Find right Chinese restaurant with wedding experience (e.g., Cantonese seafood spots in Irvine/Westminster)
- ✅ Book their standard wedding package (8-10 courses, basic setup)
- ✅ Coordinate photographer (documentary style: candid family interactions)
- ✅ Arrange bilingual MC if needed (Cantonese/English for announcements)
- ✅ Manage simple additions (red envelope station, signage, minimal flowers)
- ✅ Day-of: Let restaurant run their proven program; ensure smooth handoffs

---

## 2. Project Specifics

| Category | Details |
|----------|---------|
| **Date** | January 2026 (mid-month for auspicious timing) |
| **Location** | Orange County, CA (Chinese restaurant with banquet facilities, e.g., Irvine or Westminster) |
| **Guest Count** | 200-220 (20-22 round tables of 10) |
| **Budget** | $25-30K total wedding (venue/food $15-20K; planner fee $3-5K; photography $2-3K; other $2-3K) |
| **Timeline** | Hire planner by September 1, 2025 (3-4 month execution) |
| **Urgency** | Need to start within weeks - emphasize in all outreach |

### Success Criteria

- ✅ Shortlist 5-10 planners
- ✅ Secure 3-5 intro calls
- ✅ Hire by September 1, 2025
- ✅ Provide handoff brief with all specs

### Timeline: ~2 weeks (August 13-27, 2025)

| Phase | Duration | Activities |
|-------|----------|------------|
| **Phase 1** | Days 1-4 | Build/research/outreach |
| **Phase 2** | Days 5-12 | Responses/scheduling/calls |
| **Phase 3** | Days 13-14 | Decision/handoff |

### Human & AI Roles

**Human Role**: Minimal—provide initial specs JSON (10 min), approve shortlist/outreach batches (15-30 min), attend calls (1-2 hours), make final decision (30 min)

**AI Role**: Delegate 80% to automation—handle data gathering, analysis, communications, logging

---

## 3. Agent Specifications (Node.js Implementation)

### Agent Overview

| Agent | Primary Tasks | Tools Used | Key Outputs |
|-------|--------------|------------|-------------|
| **🔍 Researcher** | • Search WeddingWire/The Knot for multicultural planners<br>• Scrape Instagram (#OCWeddingPlanner, #AsianWeddingOC, #MulticulturalWeddingCA, #ChineseWeddingCA)<br>• Find planners with "tea ceremony," "Cantonese banquet," or "bilingual MC" keywords<br>• Target 20-50 profiles | Apify SDK, TypeScript | Raw dataset in Airtable (name, contact, bio, reviews, portfolio links, estimated experience level) |
| **📊 Analyzer** | • Score planners (1-10 scale)<br>• Weight: 40% multicultural fit, 30% timeline availability, 30% reviews/sentiment<br>• Use OpenAI GPT-4o for bio summarization<br>• Shortlist top 5-10, flag ambiguities | OpenAI SDK, scoring algorithms | Ranked shortlist in Airtable (with summaries, scores, flags) |
| **📧 Outreach** | • Generate personalized emails via Twilio<br>• Track responses & auto-follow up after 48hr<br>• Schedule calls via Calendly API<br>• Log all communications | Twilio SDK, Calendly API | Communication logs in Airtable (status, responses, call summaries) |

### Agent Operating Rules

- ✅ Reference shared Airtable state for data handoffs
- ✅ Log all actions with timestamps (Winston logger)
- ✅ Retry on errors with exponential backoff
- ✅ Flag for human review: Low-confidence results (<70% match), potential biases, or compliance issues
- ✅ Disclose AI use in all outreaches ("This is an AI-assisted inquiry")
- ✅ Comply with CAN-SPAM (opt-out links)

---

## 4. Workflow Steps

### Process Flow

| Step | Timeline | Activities |
|------|----------|------------|
| **Step 1** | Day 1-3 | Human inputs specs → Researcher scrapes → Analyzer vets → Human approves shortlist |
| **Step 2** | Day 4-8 | Outreach sends contacts → Tracks responses → Schedules calls |
| **Step 3** | Day 9-12 | Humans attend calls → Outreach logs summaries |
| **Step 4** | Day 13-14 | Analyzer compiles rankings → Human decides → Outreach drafts handoff brief |

### Human Gates (require approval)

- ✅ Initial specs input
- ✅ Shortlist approval before outreach
- ✅ Batch outreach message approval
- ✅ Final hiring decision

---

## 5. Tech Stack & Budget (Node.js)

### Core Tools

| Tool | Purpose | Cost | Notes |
|------|---------|------|-------|
| **Claude Code** | Orchestrator, script generation | $10-20/mo | Anthropic API, usage-based |
| **Node.js/TypeScript** | Runtime & type safety | Free | Local development |
| **Apify SDK** | Web scraping (ethical) | $49/mo | Starter plan + pay-as-you-go |
| **Airtable** | Central database | Free | API-integrated for real-time updates |
| **OpenAI GPT-4o** | Analysis & summarization | $10-20/mo | <1M tokens target |
| **Twilio SendGrid** | Email outreach | $20-30/mo | Pay-per-use |
| **Calendly** | Call scheduling | $10/mo | Standard plan |
| **Winston** | Logging | Free | NPM package |

**Total Budget**: <$150/month

---

## 6. Node.js Project Structure

```
src/
├── agents/
│   ├── researcher.ts      # Instagram/web scraping agent
│   ├── analyzer.ts        # AI-powered scoring & analysis
│   └── outreach.ts        # Email automation & scheduling
├── orchestrator/
│   ├── index.ts          # Main entry point & CLI
│   └── workflow.ts       # Agent coordination logic
├── lib/
│   ├── airtable.ts       # Database operations
│   ├── openai.ts         # AI integration
│   ├── apify.ts          # Web scraping
│   ├── twilio.ts         # Email/SMS
│   └── calendly.ts       # Scheduling
├── utils/
│   ├── logger.ts         # Winston logging setup
│   ├── costs.ts          # Usage monitoring
│   └── validation.ts     # Input validation
├── types/
│   └── index.ts          # TypeScript definitions
└── config/
    ├── default.json      # Default settings
    └── production.json   # Production overrides
```

---

## 7. Ethics & Compliance Guidelines

### Must Follow

- ✅ **Privacy (CCPA)**: Scrape only public data; anonymize personal info
- ✅ **Platform TOS**: No private data scraping; no Instagram DMs (use email)
- ✅ **CAN-SPAM**: Include opt-out links; verified sender info
- ✅ **Transparency**: Disclose AI use in all outreach ("AI-assisted inquiry")
- ✅ **Bias Mitigation**: Use diverse keywords (e.g., "Cantonese," "Taiwanese"); human review for cultural nuance
- ✅ **Sustainability**: Minimize API calls; batch operations; prefer eco-friendly planners

### Compliance Checklist

- ✅ Public data only (no login-required content)
- ✅ Apify compliant mode enabled
- ✅ Email opt-out links included
- ✅ AI disclosure in first contact
- ✅ Audit logs timestamped in Airtable
- ✅ Human review for flagged items

---

## 8. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| **Low response rate** | Aggressive follow-ups; expand shortlist if <3 replies |
| **Timeline delays** | Buffer for weekends; prioritize responsive planners |
| **Data inaccuracy** | Cross-validate reviews vs. bios; human verification |
| **API/Tech failures** | Monitor usage limits; manual fallback procedures |
| **Cultural misalignment** | Flag non-exact matches; verify in human calls |

---

## 9. Data Schemas

### Airtable: Planners Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | auto | Auto-generated ID |
| `name` | text | Planner name |
| `business_name` | text | Business name |
| `contact_email` | email | Contact email |
| `contact_phone` | phone | Contact phone |
| `instagram_handle` | text | Instagram handle |
| `bio_summary` | long text | Bio summary |
| `multicultural_experience` | long text | Multicultural experience details |
| `review_score` | number 1-5 | Review score |
| `review_count` | number | Number of reviews |
| `portfolio_links` | attachment/URL | Portfolio links |
| `availability_status` | single select | available/busy/unknown |
| `analyzer_score` | number 1-10 | Analyzer score |
| `flags` | multi-select | timeline_concern/experience_unclear/no_response |
| `outreach_status` | single select | pending/contacted/responded/scheduled |
| `call_date` | date | Call date |
| `call_notes` | long text | Call notes |
| `final_rank` | number | Final ranking |

### Airtable: Activity Logs Table

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | date/time | Action timestamp |
| `agent` | single select | researcher/analyzer/outreach |
| `action` | text | Action description |
| `target` | link to Planners | Target planner |
| `result` | text | Action result |
| `error_flag` | checkbox | Error flag |

---

## 10. Key Principles

- ✅ **80-20 Rule**: Minimal agents (3) automate 80% of workflow
- ✅ **Human Gates**: Critical decisions only (specs, approvals, final choice)
- ✅ **Transparency**: Always disclose AI involvement
- ✅ **Urgency**: Emphasize 3-4 month timeline in all communications
- ✅ **Cultural Focus**: Prioritize Asian tradition experience, especially Cantonese banquets
- ✅ **Audit Everything**: Log all actions for accountability

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| **Planners researched** | 20-50 |
| **Shortlisted with scores >7** | 5-10 |
| **Intro calls scheduled** | 3-5 |
| **Planners hired by September 1** | 1-3 |
| **Total human time** | <3 hours |
| **Monthly tool costs** | <$150 |
| **Compliance with ethics guidelines** | 100% |

---

## Summary

**This document serves as the single source of truth for all AI agents in the system.** Agents must reference this context in all decision-making and task execution.