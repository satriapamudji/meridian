# Meridian Trader Guide

> How to use Meridian as your macro intelligence brain for kingmaker trades.

**Last Updated:** January 2026  
**System Version:** Phase 1 MVP

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Daily Workflow](#2-daily-workflow)
3. [Macro Radar: Finding Opportunities](#3-macro-radar-finding-opportunities)
4. [Event Analysis: Understanding Significance](#4-event-analysis-understanding-significance)
5. [Thesis Workspace: Building Conviction](#5-thesis-workspace-building-conviction)
6. [Metals Intelligence](#6-metals-intelligence)
7. [The Thesis Lifecycle](#7-the-thesis-lifecycle)
8. [Best Practices](#8-best-practices)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Quick Start

### Starting the System

```bash
# 1. Start infrastructure (Postgres + Redis)
cd ops && docker compose up -d

# 2. Start backend API
cd backend
source .venv/bin/activate  # or create venv first
uvicorn app.main:app --reload

# 3. Start frontend
cd frontend
npm run dev

# 4. Open in browser
open http://localhost:3000
```

### First-Time Setup

1. **Verify health**: Home page should show "Backend status: ok"
2. **Check data**: Navigate to `/macro-radar` — you should see events
3. **Review a thesis**: Go to `/theses` to see the sample "Silver mean reversion" thesis

### Key URLs

| Page | URL | Purpose |
|------|-----|---------|
| Home | `/` | System status overview |
| Macro Radar | `/macro-radar` | Event list with significance scores |
| Event Detail | `/macro-radar/{id}` | Deep-dive into a single event |
| Thesis Workspace | `/theses` | Manage your trading theses |
| Metals | `/metals` | Metals intelligence (coming soon) |

---

## 2. Daily Workflow

Meridian is designed for a **once-daily check-in** with occasional deep dives. Here's the recommended workflow:

### Morning Routine (5-10 minutes)

1. **Check the Macro Radar** (`/macro-radar`)
   - Look for ⚡ PRIORITY badges (score ≥ 65)
   - These are events that warrant your attention
   
2. **Review Priority Events**
   - Click into any priority event
   - Read the **Raw Facts** first (uninterpreted)
   - Then review the **Interpretation** (metal impacts, historical precedent)
   
3. **Update Active Theses** (`/theses`)
   - Check if any thesis needs updating based on new events
   - Add notes to track your thinking

### When to Go Deeper

- **⚡ PRIORITY event detected**: Take 15-30 minutes to analyze
- **Thesis approaching invalidation**: Reassess your position
- **Major central bank meeting**: Review communications

### When to Do Nothing

- **No priority events**: The system is doing its job — filtering noise
- **Score < 50**: These are logged but not actionable
- **Thesis unchanged**: No news is sometimes good news

---

## 3. Macro Radar: Finding Opportunities

### Understanding the Event List

The Macro Radar (`/macro-radar`) shows all detected events with:

| Column | Meaning |
|--------|---------|
| **Headline** | Event title from source |
| **Score** | Significance score (0-100) |
| **Source** | Reuters, AP, Bloomberg, etc. |
| **Status** | New, Analyzed, Thesis Created, Dismissed |
| **Published** | When the event occurred |

### Significance Tiers

| Score | Tier | Badge | Action |
|-------|------|-------|--------|
| 65-100 | ⚡ PRIORITY | Red/Orange | **Requires analysis** — potential kingmaker |
| 50-64 | MONITORING | Yellow | Track but don't act yet |
| 0-49 | LOGGED | Gray | Recorded for reference |

### Using Filters

- **Score filter**: Focus on Priority only when time-constrained
- **Source filter**: Trust some sources more than others
- **Status filter**: Hide dismissed events, show only "new"
- **Date filter**: Focus on recent (24h, 7d)

### Pro Tips

1. **Don't read everything**: Let the significance score do its job
2. **Priority events are rare**: 1-3 per week is normal
3. **If nothing is priority, that's fine**: The market isn't always moving

---

## 4. Event Analysis: Understanding Significance

### The Event Detail Page

When you click into an event (`/macro-radar/{id}`), you see:

#### Raw Facts Section
- **Uninterpreted facts** extracted from the source
- Read these first to form your own view
- Example: "Fed Chair Powell stated rates will remain elevated"

#### Interpretation Section

1. **Significance Scoring**
   - Total score (0-100)
   - Band (Priority/Monitoring/Logged)
   - Priority flag (Yes/No)

2. **Metal Impacts**
   - Per-metal analysis (Gold, Silver, Copper)
   - Direction: Bullish / Bearish / Neutral
   - Magnitude estimate
   - Driver explanation

3. **Historical Precedent**
   - Similar events from the past
   - What happened to metals
   - Link to historical case if available

4. **Counter-Case** (CRITICAL)
   - Why the obvious trade might NOT work
   - Prevents false confidence
   - Always read this section

5. **Crypto Transmission**
   - Does this macro event affect crypto?
   - Transmission path (if any)
   - Strength: Strong / Moderate / Weak / None

### Triggering Analysis

- For priority events, click **"Analyze"** to run LLM analysis
- Analysis populates all interpretation fields
- Analysis is only available for priority events (score ≥ 65)

### Making a Decision

After reading an event:

| Decision | When | Action |
|----------|------|--------|
| **Create Thesis** | High conviction opportunity | Start formal tracking |
| **Keep Watching** | Interesting but uncertain | Check back in 1-2 days |
| **Dismiss** | Not relevant to metals | Remove from radar |

---

## 5. Thesis Workspace: Building Conviction

### The Thesis Workflow

The Thesis Workspace (`/theses`) is where you formalize your trading ideas.

```
Watching → Active → Closed
```

| Status | Meaning | Requirements |
|--------|---------|--------------|
| **Watching** | Idea worth tracking | Title, Asset, Core Thesis |
| **Active** | Position taken or imminent | Bear Case + Invalidation REQUIRED |
| **Closed** | Trade completed or abandoned | Exit reasoning documented |

### Creating a Thesis

1. Click **"+ New Thesis"**
2. Fill in required fields:
   - **Title**: Short, descriptive (e.g., "Gold: Fed Pivot Play")
   - **Asset Type**: Gold, Silver, Copper, etc.
   - **Core Thesis**: One paragraph — why this, why now
3. Optional but recommended:
   - **Trigger Event**: What macro event sparked this idea
   - **Historical Precedent**: Similar past situations
   - **Bull Case**: Reasons this works (bullets)

### Activating a Thesis (IMPORTANT)

Before going Active, you MUST fill in:

1. **Bear Case / Counter-Case**
   - List 2-3 reasons this could fail
   - Be honest with yourself
   - If you can't think of any, you haven't done enough research

2. **Invalidation**
   - Specific conditions that kill the thesis
   - Price level, time constraint, or fundamental change
   - Example: "Thesis invalidated if gold breaks below $1,950"

### Adding Updates

As the trade develops:

1. Select your thesis from the sidebar
2. Scroll to **"Add Update"** section
3. Add a note and optional price
4. Updates are timestamped and logged

### Exporting a Thesis

Click **"Export Markdown"** to download a full thesis document. Useful for:
- Sharing with others
- Archiving for future reference
- Reviewing your own reasoning later

---

## 6. Metals Intelligence

> Note: Full UI coming in task-25. Currently placeholder.

### What's Available Now

- **Price data** is ingested daily (Gold, Silver, Copper)
- **Knowledge base** is seeded with supply chain, patterns, correlations
- **Event analysis** includes metal impacts

### Coming Soon

- `/metals` dashboard with prices and ratios
- Per-metal detail pages
- Gold/Silver ratio analysis
- Supply chain visualization

### Key Concepts

**Gold/Silver Ratio**
- Historical mean: ~60
- Range: 40-100
- Above 80: Silver potentially undervalued
- Below 50: Silver potentially overvalued

**Price Drivers**
- Gold: Real rates (inverse), USD (inverse), safe haven demand
- Silver: Gold correlation + industrial demand
- Copper: Economic growth, China demand, electrification

---

## 7. The Thesis Lifecycle

### Phase 1: Watching

**Duration**: Days to weeks

**Activities**:
- Monitor related events
- Build understanding of the setup
- Refine entry levels
- Identify invalidation criteria

**Exit Watching**:
- Promote to Active (conviction reached)
- Dismiss (thesis no longer valid)

### Phase 2: Active

**Duration**: Days to months

**Requirements**:
- Clear invalidation criteria
- Documented bear case
- Regular updates (at least weekly)

**Activities**:
- Track price vs. entry/target/invalidation
- Add notes on new developments
- Watch for confirming/disconfirming signals

**Exit Active**:
- Close (target reached or invalidation triggered)
- Back to Watching (uncertainty increased)

### Phase 3: Closed

**When closing, document**:
- Exit reasoning
- Actual outcome vs. expected
- Lessons learned

**Review closed theses monthly** to improve your process.

---

## 8. Best Practices

### Do

✅ **Read raw facts before interpretation** — form your own view first

✅ **Always read the counter-case** — prevents overconfidence

✅ **Require bear case for active theses** — if you can't articulate what could go wrong, you don't understand the trade

✅ **Update theses regularly** — stale theses are dangerous

✅ **Use invalidation levels** — know when you're wrong before you're wrong

✅ **Trust the significance score** — it's filtering noise for you

### Don't

❌ **Don't chase every event** — kingmaker trades are rare

❌ **Don't ignore counter-cases** — they exist for a reason

❌ **Don't activate without invalidation** — you need an exit plan

❌ **Don't forget to close theses** — completed trades need documentation

❌ **Don't manually refresh constantly** — once daily is enough

### Kingmaker Trade Criteria

A true "kingmaker" trade meets ALL of these:

1. **Macro-driven**: Based on structural macro shift
2. **High conviction**: Thesis documented with evidence
3. **Clear invalidation**: You know when you're wrong
4. **Patient timeframe**: Days to weeks, not hours
5. **Meaningful size**: Worth the research effort

---

## 9. Troubleshooting

### Common Issues

**"No events showing"**
- Check backend is running: `curl http://localhost:8000/health`
- Run RSS ingestion: `cd backend && python -m app.ingestion.rss_poller`

**"Analysis button doesn't work"**
- Only works for priority events (score ≥ 65)
- Check you have an OpenRouter API key configured

**"Thesis won't save"**
- Title, Asset Type, and Core Thesis are required
- Bear Case and Invalidation required for Active status

**"Prices not updating"**
- Run price poller: `cd backend && python -m app.ingestion.prices_poller`
- Check Yahoo Finance is accessible

### Manual Data Refresh

```bash
# Refresh macro events
cd backend
python -m app.ingestion.rss_poller

# Refresh prices
python -m app.ingestion.prices_poller

# Refresh economic calendar
python -m app.ingestion.economic_calendar
```

### Getting Help

- Check `AGENTS.md` for technical documentation
- Review `spec.md` for system design intent
- Check `CODEMAP.md` for code organization

---

## Appendix: Keyboard Shortcuts (Future)

| Shortcut | Action |
|----------|--------|
| `g` `r` | Go to Macro Radar |
| `g` `t` | Go to Theses |
| `g` `m` | Go to Metals |
| `n` | New thesis |
| `?` | Help |

---

## Appendix: Significance Scoring Breakdown

The 0-100 score is calculated from four components:

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| Structural Impact | 35% | GDP/economic weight, commodity exposure |
| Transmission Path | 30% | Clear causation to metals |
| Historical Reaction | 20% | How similar events moved markets |
| Attention | 15% | Media saturation, narrative velocity |

**Score ≥ 65 = Priority**: The event has strong structural implications with clear asset transmission and historical precedent.

---

*This guide will be updated as new features are added. For the latest, check the task files in `tasks/`.*
