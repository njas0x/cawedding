# AI-Powered Wedding Planner Hiring System

## Overview
System to find and hire a wedding planner for an authentic 80s/90s Asian banquet wedding in Orange County, CA. Built on 80-20 principle: 3 AI agents handle research and outreach with minimal human involvement.

---

## Wedding Vision

### Core Concept
- **Authentic 80s/90s Asian wedding banquet** - pragmatic, how it was actually done then
- **Modern comfort & relaxed energy** - especially second half with lounge area
- **Memorable for first-timers** - accessible traditions without over-choreography

### Non-Negotiable Requirements

#### Venue Layout
- **Main Dining Area**: 200~ guests at round tables with lazy Susans, stage for ceremonies
- **Lounge/Arcade**: Secondary space opening mid-evening for games and mingling
- **Entrance Hall**: Welcome area with red envelope station, guestbook
- **Window Side**: VIP seating or photo moment area

#### Program Anchors (Must Have)
1. Grand entrance (2 min)
2. Tea ceremony for parents/elders on stage (10-12 min)
3. Family toast + friend toast (6-8 min total, keep short)
4. Cake/champagne moment (3-4 min)
5. Group photo on stage (5-7 min)
6. Table-to-table greetings during dinner

#### Flow Structure
- 6:00-7:45pm: Everyone in main room for ceremonies and early courses
- 7:45pm onward: Lounge opens, free flow between zones
- MC recalls guests from lounge for key moments (group photo, final thanks)

### Atmosphere Goals
- **Feel**: Warm, bustling, lived-in banquet - not overproduced
- **Look**: Venue's existing red/gold décor + minimal additions (囍 cutouts, silk flowers)
- **Sound**: Nostalgic Cantopop, chatter, clinking dishes, eventual karaoke
- **Taste**: Traditional 8-10 course Chinese banquet (roast pig, seafood, whole fish)
- **Memory**: Sensory details, candid moments, genuine cultural experience

### What We Need From a Planner

#### Must Have Experience
- Chinese restaurant banquet weddings in Orange County
- Managing dual-zone venues (dining + lounge)
- Working WITH restaurant's existing setup and package
- Coordinating traditional tea ceremonies

#### Must Understand
- This is restaurant-run, not planner-produced
- Authenticity over Instagram aesthetics
- Natural flow over rigid timeline
- Restaurant's system works - don't reinvent it

#### Key Tasks
1. Find right Chinese restaurant with wedding experience
2. Book their standard wedding package
3. Coordinate photographer (documentary style)
4. Arrange bilingual MC if needed
5. Manage simple additions (red envelope station, signage)
6. Day-of: Let restaurant run their proven program

---

## Project Specifics
- **Date**: Jan 2026
- **Location**: Orange County, CA (Chinese restaurant with banquet facilities)
- **Guest Count**: 200 (8-10 round tables)
- **Budget**: Open
- **Timeline**: Hire planner by September 1, 2025 (3-4 month execution)
- **Urgency**: Need to start within weeks - emphasize in all outreach
- **Success Criteria**: Shortlist 5-10 planners; secure 3-5 intro calls; hire by September 1, 2025; provide handoff brief with all specs
- **Timeline**: ~2 weeks (August 13-27, 2025)
  - Days 1-4: Build/research/outreach
  - Days 5-12: Responses/scheduling/calls
  - Days 13-14: Decision/handoff
- **Human Role**: Minimal—provide initial specs JSON (10 min), approve shortlist/outreach batches (15-30 min), attend calls (1-2 hours), make final decision (30 min)
- **AI Role**: Delegate 80% to automation: Handle data gathering, analysis, communications, logging

### 2. Agent Specifications

| Agent | Primary Tasks | Tools Used | Key Outputs |
|-------|--------------|------------|-------------|
| **Researcher** | • Search WeddingWire/The Knot for "Asian-owned"<br>• Scrape Instagram (#ChineseBanquetWedding #OCChineseWedding)<br>• Find planners mentioning specific venues (Capital Seafood, etc)<br>• Target 20-50 profiles | Apify, Web scrapers | Raw dataset in Airtable (name, contact, Chinese wedding experience, venue relationships) |
| **Analyzer** | • Score planners (1-10 scale)<br>• Weight: 40% Chinese banquet experience, 30% authentic approach, 20% OC venue relationships, 10% availability<br>• Shortlist top 5-10<br>• Flag red flags (over-stylized, no restaurant experience) | OpenAI GPT-4o, Scoring algorithms | Ranked shortlist with experience summaries, scores, compatibility flags |
| **Outreach** | • Generate personalized emails emphasizing authentic approach<br>• Track responses & follow up (48hr)<br>• Schedule calls via Calendly<br>• Log all communications | Twilio, Calendly API | Communication logs, scheduled calls, response tracking |

**Agent Operating Rules**:
- Reference shared Airtable state for data handoffs
- Log all actions with timestamps
- Retry on errors (e.g., after 48 hours for non-responses)
- Flag for human review: Low-confidence results (<70% match), potential biases, or compliance issues

### 3. Workflow Steps

```
Day 1-3:  Human inputs specs → Researcher scrapes → Analyzer vets → Human approves shortlist
Day 4-8:  Outreach sends contacts → Tracks responses → Schedules calls
Day 9-12: Humans attend calls → Outreach logs summaries
Day 13-14: Analyzer compiles rankings → Human decides → Outreach drafts handoff brief
```

**Human Gates** (require approval):
- Initial specs input
- Shortlist approval before outreach
- Batch outreach message approval
- Final hiring decision

### 4. Tech Stack & Budget

| Tool | Purpose | Cost | Notes |
|------|---------|------|-------|
| Claude Code | Orchestrator, script generation | $10-20/mo | Anthropic API, usage-based |
| CrewAI | Multi-agent framework | Free | Local installation |
| Apify | Web scraping (ethical) | $49/mo | Starter plan + pay-as-you-go |
| Airtable | Central database | Free | API-integrated for real-time updates |
| OpenAI GPT-4o | Analysis & summarization | $10-20/mo | <1M tokens target |
| Twilio | Email/SMS outreach | $20-30/mo | Pay-per-use |
| Calendly | Call scheduling | $10/mo | Standard plan |

**Total Budget**: <$150/month

### 5. Ethics & Compliance Guidelines

#### Must Follow:
- **Privacy (CCPA)**: Scrape only public data; anonymize personal info
- **Platform TOS**: No private data scraping; no Instagram DMs (use email)
- **CAN-SPAM**: Include opt-out links; verified sender info
- **Transparency**: Disclose AI use in all outreach ("AI-assisted inquiry")
- **Bias Mitigation**: Use diverse keywords; human review for cultural nuance
- **Sustainability**: Minimize API calls; batch operations; prefer eco-friendly planners

#### Compliance Checklist:
- [ ] Public data only (no login-required content)
- [ ] Apify compliant mode enabled
- [ ] Email opt-out links included
- [ ] AI disclosure in first contact
- [ ] Audit logs timestamped in Airtable
- [ ] Human review for flagged items

### 6. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Low response rate | Aggressive follow-ups; expand shortlist if <3 replies |
| Timeline delays | Buffer for weekends; prioritize responsive planners |
| Data inaccuracy | Cross-validate reviews vs. bios; human verification |
| API/Tech failures | Monitor usage limits; manual fallback procedures |
| Cultural misalignment | Flag non-exact matches; verify in human calls |

### 7. Data Schemas

**Airtable: Planners Table**
```
- id (auto)
- name (text)
- business_name (text)
- contact_email (email)
- contact_phone (phone)
- instagram_handle (text)
- bio_summary (long text)
- multicultural_experience (long text)
- review_score (number 1-5)
- review_count (number)
- portfolio_links (attachment/URL)
- availability_status (single select: available/busy/unknown)
- analyzer_score (number 1-10)
- flags (multi-select: timeline_concern/experience_unclear/no_response)
- outreach_status (single select: pending/contacted/responded/scheduled)
- call_date (date)
- call_notes (long text)
- final_rank (number)
```

**Airtable: Activity Logs Table**
```
- timestamp (date/time)
- agent (single select: researcher/analyzer/outreach)
- action (text)
- target (link to Planners)
- result (text)
- error_flag (checkbox)
```

### 8. Key Principles

1. **80-20 Rule**: Minimal agents (3) automate 80% of workflow
2. **Human Gates**: Critical decisions only (specs, approvals, final choice)
3. **Transparency**: Always disclose AI involvement
4. **Urgency**: Emphasize 3-4 month timeline in all communications
5. **Cultural Focus**: Prioritize Asian tradition experience
6. **Audit Everything**: Log all actions for accountability

---

## Success Metrics

- [ ] 20-50 planners researched
- [ ] 5-10 shortlisted with scores >7
- [ ] 3-5 intro calls scheduled
- [ ] 1-3 planners hired by September 1
- [ ] <3 hours total human time
- [ ] <$150 monthly tool costs
- [ ] 100% compliance with ethics guidelines

---

*This document serves as the single source of truth for all AI agents in the system. Agents must reference this context in all decision-making and task execution.*