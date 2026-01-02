# Meridian

> Where macro currents and crypto narratives converge.

**Version:** 0.3.0 (Unified Spec: SCQA + Revised Spec)  
**Last Updated:** January 2026  
**Status:** Pre-Development

**Canonical doc:** This file is the single source of truth and merges `SCQA_Trading_System.md` + prior drafts into one spec.
**Implementation map:** See `CODEMAP.md` for repo layout, code map, and build scopes derived from this spec.

---

## Table of Contents

0. [Origin & Motivation (SCQA)](#0-origin--motivation-scqa)
1. [Vision & Problem Statement](#1-vision--problem-statement)
2. [User Persona](#2-user-persona)
3. [Core Thesis](#3-core-thesis)
4. [System Architecture](#4-system-architecture)
5. [Data Sources & Ingestion](#5-data-sources--ingestion)
6. [Metals Intelligence Module](#6-metals-intelligence-module)
7. [Scoring Frameworks](#7-scoring-frameworks)
8. [Feature Breakdown by Phase](#8-feature-breakdown-by-phase)
9. [Technical Stack](#9-technical-stack)
10. [Cold Start Strategy](#10-cold-start-strategy)
11. [UX & Interaction Model](#11-ux--interaction-model)
12. [Success Metrics & Failure Modes](#12-success-metrics--failure-modes)
13. [Open Questions](#13-open-questions)
14. [Appendix A: Glossary](#appendix-a-glossary)
15. [Appendix B: Historical Case Template](#appendix-b-historical-case-template)
16. [Appendix C: Thesis Template](#appendix-c-thesis-template)
17. [Appendix D: Reference - Missed Trades Analysis](#appendix-d-reference---missed-trades-analysis)
18. [Appendix E: Key Trade History (Context)](#appendix-e-key-trade-history-context)
19. [Appendix F: Database Schema (Draft)](#appendix-f-database-schema-draft)
20. [Appendix G: LLM Prompt Templates](#appendix-g-llm-prompt-templates)
21. [Appendix H: Build Plan Checklists](#appendix-h-build-plan-checklists)

---

## 0. Origin & Motivation (SCQA)

Meridian exists to turn macro “inputs” into actionable, thesis-driven trades—without devolving into noisy buy/sell signals.

### 0.1 Situation

- Trading identity: narrative trader (macro themes → concentrated positions).
- Key scars that shaped Meridian:
  - Terra/LUNA (2022): thesis without invalidation criteria + leverage + ignoring macro = catastrophic loss.
  - Soulgraph / NOMAI (2024-2025): good entries, poor exits; ecosystem dependency; narrative decay.
  - Gold/Silver (2024-2025): saw drivers, but couldn’t synthesize into a thesis fast enough.

### 0.2 Complication

- Information overload without structure (feeds everywhere, no prioritization).
- No consistent thesis process (entries/exits not tied to explicit invalidation).
- “Connecting dots” problem (facts observed but not translated into trades).
- Confidence erosion (losses reduce conviction and increase hesitation).
- Markets evolved (macro regime + metals matter; crypto is downstream, not isolated).

### 0.3 Question

How do we build a lightweight system that:
- Centralizes modular data sources (news, central banks, calendar, prices, crypto).
- Extracts structured facts first, then interpretation (clear separation).
- Scores significance to filter noise and surface “kingmaker” setups.
- Generates/maintains theses with mandatory counter-case + invalidation criteria.
- Supports both macro-first and crypto-native opportunities depending on regime.
- Tracks outcomes and learns (what works for you, not generic alpha).

### 0.4 Answer (Meridian)

Meridian is a macro-first dashboard + Telegram check-in that:
- Detects events, scores significance (0-100), and elevates ⚡ PRIORITY events (≥65).
- Uses a metals knowledge base + historical case library to synthesize impacts.
- Seeds theses (with counter-case + invalidation) and tracks them over time.
- Evaluates macro → crypto transmission paths; runs crypto-native radar as gap-fill.
- Closes the loop with performance tracking and a counter-thesis engine.

#### Problem → Solution Map

| Problem | Meridian Solution |
|---------|-------------------|
| Missed kingmaker trades (silver, gold) | Macro Intelligence Layer + significance scoring |
| No systematic macro monitoring | Automated ingestion + calendar + central bank tracking |
| Fragmented information | Single dashboard with Macro Radar + Thesis Workspace |
| Couldn’t connect dots | Metals KB + historical matching + LLM synthesis |
| Overwhelming noise | Significance scoring + “⚡ PRIORITY” gating |
| No memory | Case base + thesis history + outcome tracking |
| No exit discipline | Thesis invalidation criteria + counter-case mandatory |
| Echo chamber thinking | Counter-thesis engine challenges active theses |

(Trade history reference lives in Appendix E.)

## 1. Vision & Problem Statement

### The Problem

Information asymmetry in markets isn't about *access* anymore—everyone has access. The alpha is in **synthesis**: connecting dots faster than the crowd and recognizing when macro events will translate into asset opportunities.

The current reality:
- **Missed kingmaker trades**: Major macro events (Russia/Ukraine → silver, COVID → gold) are visible but not connected to actionable positions
- **No systematic macro monitoring**: Events happen, but without a framework to evaluate significance
- **Fragmented information**: News, Fed communications, economic data, and commodity signals live in separate silos
- **Overwhelming noise**: By the time an opportunity is obvious, it's crowded
- **No memory**: Past theses, learnings, and patterns aren't systematically captured

The result: **Kingmaker trades are missed not from lack of information, but from lack of synthesis.** Research feels overwhelming, so it doesn't happen.

### The Vision

Meridian is an **externalized macro intelligence brain** that:

1. **Monitors macro events** continuously and scores them for significance
2. **Surfaces kingmaker opportunities** - a few high-conviction trades per year in metals and crypto
3. **Provides historical context** - "this rhymes with X, here's what happened, here's why this time might differ"
4. **Builds and tracks theses** over days/weeks, not reactive trading
5. **Translates macro to crypto** when transmission paths exist
6. **Fills gaps with crypto-native signals** when macro is quiet

This is not a screener. Not a signal bot. Not reactive trading.  
It's a **system for kingmaker trades with deep research and conviction**.

---

## 2. User Persona

**Primary User:** Solo trader/investor with:
- **Edge**: Information asymmetry, pattern recognition, macro-to-asset translation
- **Style**: Thesis-driven, high-conviction, patient
- **Time horizon**: Days to weeks (thesis building, not reactive)
- **Markets**: Metals (gold, silver, copper) + Crypto
- **Trade frequency**: Kingmaker trades a few times per year, crypto-native fills the gaps
- **Technical ability**: Can code, comfortable with CLI, willing to maintain with AI assistance
- **Pain point**: Missed macro opportunities (silver, gold) due to lack of systematic synthesis

**User Context:**
- Wants raw facts first, then AI interpretation with clear separation
- Prefers scheduled check-ins over constant alerts
- Values forming own conviction—doesn't want "buy/sell" signals
- Trades metals via physical or stocks (miners)
- Trades crypto directly

---

## 3. Core Thesis

### What Makes Meridian Different

1. **Macro-first, not crypto-first**
   - Starts with global events, policy signals, and commodity intelligence
   - Crypto opportunities derived downstream OR run as parallel track
   - Most "crypto tools" ignore macro entirely

2. **Kingmaker framing, not constant signals**
   - Optimized for a few high-conviction trades per year
   - Quality over quantity
   - Deep research and thesis-building, not reactive noise

3. **Pre-built macro knowledge + real-time synthesis**
   - System *understands* metals (supply chains, use cases, correlations, actors)
   - Synthesizes implications of new events against this knowledge
   - Not just news aggregation—actual intelligence

4. **Raw → Interpreted presentation**
   - Raw facts from primary sources first
   - AI interpretation clearly separated
   - User forms own conviction, system provides scaffolding

5. **Historical grounding with counter-cases**
   - Every opportunity comes with precedent AND why this time might differ
   - Prevents false confidence

6. **Hybrid attention model**
   - Macro radar for kingmaker opportunities
   - Crypto-native radar for gap-filling
   - System tells you where to look based on regime

---

## 4. System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         MERIDIAN                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MACRO INTELLIGENCE LAYER                    │   │
│  │                                                          │   │
│  │  News Wires ──► Event Detection ──► Significance Score  │   │
│  │       +                                                  │   │
│  │  Fed/ECB/BOJ ──► Policy Signals                         │   │
│  │       +                                                  │   │
│  │  Economic Calendar ──► Data Releases                    │   │
│  │       +                                                  │   │
│  │  Metals Intelligence (Gold, Silver, Copper)             │   │
│  │       │                                                  │   │
│  │       ▼                                                  │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  MACRO OPPORTUNITIES                             │    │   │
│  │  │  • Metals plays (physical, miners)              │    │   │
│  │  │  • Historical precedent + counter-case          │    │   │
│  │  │  • Thesis workspace                             │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              TRANSMISSION LAYER                          │   │
│  │                                                          │   │
│  │  Macro Event ──► Crypto Transmission Path?              │   │
│  │       │                                                  │   │
│  │       ├── YES ──► Crypto opportunity (macro-derived)    │   │
│  │       └── NO ───► Pure macro play, no crypto angle      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         +                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         CRYPTO-NATIVE LAYER (Parallel Track)             │   │
│  │                                                          │   │
│  │  CryptoPanic ──► Narrative Detection                    │   │
│  │  Twitter/Telegram ──► Sentiment/Crowding                │   │
│  │       │                                                  │   │
│  │       ▼                                                  │   │
│  │  CRYPTO-NATIVE OPPORTUNITIES                            │   │
│  │  • Memecoins, upgrades, unlocks                         │   │
│  │  • Narrative rotation                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              INTERFACE LAYER                             │   │
│  │                                                          │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌────────────┐  │   │
│  │  │ MACRO RADAR │    │CRYPTO RADAR │    │ DAILY      │  │   │
│  │  │ (Tab 1)     │    │(Tab 2)      │    │ CHECK-IN   │  │   │
│  │  └─────────────┘    └─────────────┘    └────────────┘  │   │
│  │                                                          │   │
│  │  Telegram Bot  │  Thesis Workspace  │  DD Reports       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Attention Model (Hybrid)

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY MODE                               │
│                                                             │
│  Default State:                                             │
│  • Crypto-native radar: ACTIVE (gap-filling)               │
│  • Macro radar: MONITORING (thesis-building)               │
│                                                             │
│  When Macro Event Detected (significance ≥ 65):            │
│  • "⚡ PRIORITY" flag surfaces                              │
│  • Macro radar: ACTIVE (primary focus)                     │
│  • Days/weeks to build thesis, not reactive                │
│                                                             │
│  Cross-Pollination:                                         │
│  • Macro events checked for crypto transmission            │
│  • Crypto narratives checked for macro drivers             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
External Sources                    Meridian Core                     User Interface
─────────────────                   ─────────────                     ──────────────

News Wires ──────┐
(Reuters, AP)    │
                 │
Fed/ECB/BOJ ─────┼──► Event ──► Significance ──► Historical ──► MACRO RADAR
                 │    Detection    Scoring        Matching
Economic ────────┤                                    │
Calendar         │                                    │
                 │                                    ▼
Metals ──────────┘                              Transmission ──► CRYPTO RADAR
Knowledge                                       Check              (if path exists)
                                                    │
                                                    ▼
CryptoPanic ─────┐                              CRYPTO-NATIVE
                 ├──► Narrative ──► Crowding ──► RADAR
Twitter/TG ──────┘    Detection      Scoring
                                        │
                                        ▼
                                   DAILY CHECK-IN
                                   "⚡ Priority" or "Nothing urgent"
                                        │
                                        ▼
                                   THESIS WORKSPACE
                                   (Notes, DD, Export)
```

---

## 5. Data Sources & Ingestion

### 5.1 News Wires (Primary - Macro Events)

**Sources (Free RSS/API):**
- Reuters RSS feeds
- AP News RSS
- Google News (aggregation backup)

**Purpose:** Breaking macro event detection

**Data Captured:**
- Headline, summary, full text
- Timestamp
- Category/region tags
- Entity extraction (countries, leaders, institutions)

**Processing:**
- Real-time ingestion
- Significance scoring trigger
- Entity linking to knowledge base

### 5.2 Central Bank Communications

**Sources (Official - Free):**
- Federal Reserve: FOMC statements, minutes, speeches, press conferences
- ECB: Monetary policy decisions, press conferences
- BOJ: Policy statements
- BOE: MPC decisions

**Data Captured:**
- Full text of communications
- Key phrase extraction
- Hawkish/dovish sentiment scoring
- Forward guidance signals

**Processing:**
- Scheduled ingestion (around known meeting dates)
- Change detection vs. previous communications
- Historical comparison

### 5.3 Economic Calendar

**Sources (Free):**
- Investing.com economic calendar
- TradingEconomics (free tier)
- ForexFactory (backup)

**Data Captured:**
- Event name, date/time
- Expected vs. actual vs. previous values
- Impact rating (high/medium/low)
- Currency/region affected

**Processing:**
- Daily sync of upcoming events
- Alert on high-impact events
- Surprise detection (actual vs. expected)

### 5.4 Price Data

**Metals (Free):**
- Yahoo Finance: Gold (GC=F), Silver (SI=F), Copper (HG=F)
- GLD, SLV, COPX ETF prices
- Major miners (NEM, GOLD, FCX)

**Crypto (Free):**
- CoinGecko free tier
- Delayed acceptable (not for execution)

**Data Captured:**
- OHLCV (daily sufficient for thesis-building)
- Key levels, moving averages
- Ratio calculations (gold/silver ratio)

**Constraints:**
- Rate limits respected
- Caching layer
- Directionality > precision

### 5.5 Crypto-Native Sources (Phase 2+)

**CryptoPanic:**
- News aggregation with sentiment voting
- Free API tier
- Good for crypto-specific news

**Twitter/Telegram:**
- Deferred to Phase 2
- Will use selective scraping
- Focus on sentiment/crowding, not primary source

---

## 6. Metals Intelligence Module

### 6.1 Scope: MVP Metals

| Metal | Ticker | Why Included | Complexity |
|-------|--------|--------------|------------|
| **Gold** | GC=F, GLD | Safe haven, most liquid, clearest macro signals | Low |
| **Silver** | SI=F, SLV | Monetary + industrial hybrid, higher beta to gold | Medium |
| **Copper** | HG=F, COPX | Economic bellwether, "Dr. Copper", electrification | Medium |

### 6.2 Pre-Built Knowledge Base (Per Metal)

Each metal has structured knowledge covering:

#### A. Supply Chain
```yaml
gold:
  top_producers:
    - country: China
      share: 11%
      notes: "Domestic consumption high, limited export"
    - country: Australia
      share: 10%
      notes: "Major exporter, stable supply"
    - country: Russia
      share: 9%
      notes: "Sanctions risk, potential supply disruption"
  top_consumers:
    - sector: Jewelry
      share: 50%
      regions: [India, China]
    - sector: Investment
      share: 25%
      vehicles: [ETFs, bars, coins]
    - sector: Central Banks
      share: 15%
      trend: "Net buyers since 2010"
    - sector: Technology
      share: 10%
  chokepoints:
    - "Swiss refineries process 70% of world's gold"
    - "London/Zurich/NYC primary trading hubs"
```

#### B. Use Cases & Demand Drivers
```yaml
gold:
  monetary:
    - "Store of value during uncertainty"
    - "Inflation hedge (historically)"
    - "Currency debasement hedge"
  investment:
    - "Portfolio diversification"
    - "Negative real rates → gold positive"
    - "ETF flows drive short-term price"
  industrial:
    - "Electronics (small %)"
    - "Dentistry (declining)"
```

#### C. Historical Patterns
```yaml
gold:
  patterns:
    - trigger: "Fed rate cut cycle begins"
      typical_response: "+15-25% over 12 months"
      examples: [2001, 2007, 2019]
      counter_examples: ["1994 - rate cuts but gold flat due to strong USD"]
    
    - trigger: "Geopolitical conflict escalation"
      typical_response: "+5-10% initial spike, fade if contained"
      examples: ["Gulf War 1990", "Russia/Ukraine 2022"]
      counter_examples: ["Syria 2013 - limited market impact"]
    
    - trigger: "Banking/financial crisis"
      typical_response: "+20-50% over 12-24 months"
      examples: ["2008 GFC", "2023 SVB"]
```

#### D. Correlations
```yaml
gold:
  correlations:
    - asset: "USD (DXY)"
      relationship: "Inverse (-0.4 to -0.6)"
      notes: "Strong dollar = gold headwind"
    
    - asset: "Real rates (10Y TIPS)"
      relationship: "Inverse (-0.7 to -0.9)"
      notes: "Most reliable driver. Negative real rates = gold bullish"
    
    - asset: "Silver"
      relationship: "Positive (0.8+)"
      notes: "Silver typically higher beta"
    
    - asset: "S&P 500"
      relationship: "Low/Variable"
      notes: "Not reliable correlation, depends on regime"
  
  ratios:
    - name: "Gold/Silver Ratio"
      current_context: "Historical mean ~60, range 40-100"
      signal: "Above 80 = silver undervalued, mean reversion thesis"
```

#### E. Key Actors
```yaml
gold:
  actors:
    central_banks:
      - "China PBOC - consistent buyer, reserves diversification"
      - "Russia CBR - heavy buyer, sanctions hedge"
      - "Turkey - volatile buyer/seller"
      - "Fed - not direct buyer but policy drives price"
    
    etf_flows:
      - "GLD (SPDR) - largest gold ETF, flows signal sentiment"
      - "IAU (iShares) - secondary indicator"
    
    miners:
      - "Newmont (NEM) - largest gold miner"
      - "Barrick (GOLD) - major producer"
      - "Note: Miners = leveraged gold bet"
    
    speculators:
      - "COMEX positioning (COT report)"
      - "Extreme long/short = contrarian signal"
```

### 6.3 Synthesis Logic

When a macro event is detected, the system:

1. **Matches event to metal drivers**
   - "War in major producer region" → supply disruption risk
   - "Fed signals rate cuts" → real rates falling → bullish
   - "USD weakening" → gold tailwind

2. **Pulls historical precedent**
   - "Similar events in the past led to X% move over Y timeframe"
   - Cites specific examples

3. **Generates counter-case**
   - "However, in [counter-example], the expected move didn't happen because..."

4. **Outputs structured opportunity card**
   - Raw facts
   - Interpretation
   - Historical precedent
   - Counter-case
   - Transmission to crypto (if any)

---

## 7. Scoring Frameworks

### 7.1 Macro Event Significance Score (0-100)

Determines whether a macro event warrants deep analysis.

| Component | Weight | Description |
|-----------|--------|-------------|
| **Structural Impact** | 35% | GDP/economic weight, commodity exposure, financial system stress |
| **Asset Transmission Path** | 30% | Direct metal implications, clear causation chain |
| **Historical Market Reaction** | 20% | Similar events' impact on metals, directional consistency |
| **Attention & Reflexivity** | 15% | Media saturation, policymaker signaling, narrative spread speed |

**Trigger Rules:**
- Score ≥ 65 → ⚡ PRIORITY - Full analysis, thesis workspace activated
- Score 50-64 → MONITORING - Light tracking, added to watchlist
- Score < 50 → LOGGED - Recorded but no action

**Key Principle:** Uses structural similarity, not keyword matching.  
"Energy shock + sanctions + inflation" > "war"

### 7.2 Narrative Crowding Score (0-100) - Phase 2

For crypto-native opportunities. Indicates how "late" a narrative is.

| Signal Category | Indicators |
|-----------------|------------|
| **Price Exhaustion** | % move from emergence, speed vs. historical |
| **Social Reflexivity** | Volume peaked/flattening, engagement declining |
| **Quality Degradation** | Derivative content > original, retail dominance |
| **Dilution** | New token explosion, forks/clones |
| **Mainstream Validation** | CNBC/Bloomberg coverage |

### 7.3 Narrative Lifecycle States - Phase 2

| State | Description |
|-------|-------------|
| **Emerging** | Few mentions, builder-led |
| **Early Momentum** | Price + smart money chatter |
| **Mainstream Acceleration** | Broad awareness, retail entry |
| **Crowded/Reflexive** | Overextended, quality degradation |
| **Distribution/Rotation** | Capital exiting, new narratives emerging |

---

## 8. Feature Breakdown by Phase

### Phase 1: MVP - Macro Intelligence (Target: 6-8 weeks)

**Focus:** Macro event detection, metals intelligence, thesis building

#### Core Features

1. **Macro Event Detection**
   - News wire ingestion (Reuters, AP RSS)
   - Event extraction and classification
   - Significance scoring (0-100)
   - ⚡ PRIORITY flagging for high-significance events

2. **Metals Intelligence Dashboard**
   - Gold, Silver, Copper coverage
   - Pre-built knowledge base (supply chains, patterns, correlations)
   - Current price + key levels
   - Gold/Silver ratio tracking

3. **Macro Radar (Tab)**
   - List of detected events with significance scores
   - Per-event detail view:
     ```
     ┌─────────────────────────────────────────────────────────┐
     │ EVENT: [Headline]                                       │
     │ Source: Reuters | 2 hours ago                           │
     │ Significance Score: 72/100 ⚡ PRIORITY                  │
     ├─────────────────────────────────────────────────────────┤
     │ RAW FACTS                                               │
     │ • [Fact 1]                                              │
     │ • [Fact 2]                                              │
     │ • [Fact 3]                                              │
     ├─────────────────────────────────────────────────────────┤
     │ INTERPRETATION                                          │
     │                                                         │
     │ Metal Impact:                                           │
     │ • Gold: [Analysis]                                      │
     │ • Silver: [Analysis]                                    │
     │ • Copper: [Analysis]                                    │
     │                                                         │
     │ Historical Precedent:                                   │
     │ "[Similar event] in [year] led to [outcome]"           │
     │                                                         │
     │ Counter-Case:                                           │
     │ "However, [reason this time might differ]"             │
     │                                                         │
     │ Crypto Transmission: [Yes/No + path if yes]            │
     ├─────────────────────────────────────────────────────────┤
     │ YOUR NOTES: [Add notes]                                 │
     └─────────────────────────────────────────────────────────┘
     ```

4. **Central Bank Monitor**
   - Fed, ECB, BOJ communication tracking
   - Next meeting countdown
   - Hawkish/dovish trend indicator
   - Key phrase extraction

5. **Economic Calendar Integration**
   - Upcoming high-impact events
   - Surprise detection (actual vs. expected)
   - Historical impact on metals

6. **Historical Case Base**
   - 25-40 curated macro events
   - Searchable by event type, metal impact
   - Linked to current event analysis

7. **Basic Thesis Workspace**
   - Create thesis for an opportunity
   - Add notes over time
   - Track price since thesis creation
   - Export as markdown

8. **Daily Check-in**
   - Morning summary (Dashboard or Telegram)
   - "⚡ PRIORITY: [Event] detected" OR "Nothing urgent - monitoring mode"
   - Upcoming economic calendar highlights
   - Thesis updates needed

9. **Telegram Bot (Basic)**
   - `/today` - Daily summary
   - `/gold` `/silver` `/copper` - Quick metal status
   - `/note [thesis] [text]` - Add note to thesis
   - `/events` - Recent high-significance events

#### Technical Deliverables (Phase 1)

- PostgreSQL database schema
- News ingestion pipeline (RSS parsing)
- Event extraction and significance scoring (LLM-based)
- Metals knowledge base (structured YAML → DB)
- Historical case base (structured data)
- Web dashboard (Next.js, mobile-responsive)
  - Macro Radar tab
  - Metals Intelligence view
  - Thesis Workspace
- Central bank communication parser
- Economic calendar sync
- Daily digest generator
- Telegram bot (basic commands)
- Price data pipeline (Yahoo Finance)

---

### Phase 2: V1 - Crypto Layer + Full DD (Target: 4-6 weeks post-MVP)

**Focus:** Add crypto-native radar, transmission paths, full due diligence workflow

#### Core Features

1. **Crypto Radar (Tab)**
   - Narrative detection from CryptoPanic
   - Crowding score per narrative
   - Lifecycle state tracking
   - Rotation suggestions

2. **Macro-to-Crypto Transmission**
   - When macro event detected, check for crypto angles
   - "Banking crisis → BTC 'digital gold' narrative"
   - "Inflation → stablecoin demand in emerging markets"

3. **Source Ingestion (Twitter/Telegram)**
   - Tier 1/2/3 account seeding
   - Selective Telegram group ingestion
   - Sentiment/crowding signals

4. **Full Due Diligence Workflow**
   - Structured DD template
   - AI synthesis of notes
   - Bull/bear case generation
   - Historical analogy matching
   - Export to Markdown/HTML/PDF

5. **Enhanced Telegram Bot**
   - `/crypto` - Crypto radar summary (narratives + top signals)
   - `/crowded` - List crowded narratives
   - `/emerging` - List emerging narratives
   - `/signal [token]` - Quick analysis of a token
   - `/macro2crypto` - Current macro-to-crypto transmission paths
   - `/dd [project]` - Start DD workflow
   - Voice note → text input

6. **Watchlist with Alerts**
   - Track metals + crypto opportunities
   - Price alerts
   - Thesis update reminders

---

### Phase 3: V2 - Learning & Advanced (Target: 8-12 weeks post-V1)

**Focus:** Performance tracking, learning loops, advanced visualization

#### Core Features

1. **Thesis Outcome Tracking**
   - Link thesis to actual trades
   - "This thesis led to +X% / -Y%"
   - Pattern recognition on your own decisions

2. **Source Performance Tracking**
   - Per-account accuracy metrics (for crypto sources)
   - Automatic tier adjustments

3. **Narrative Timeline Visualization**
   - Historical view of narratives and lifecycles
   - "Show me every commodity narrative since 2020"

4. **On-Chain Data Integration**
   - Whale tracking
   - Smart money flows

5. **Adaptive Check-in Cadence**
   - Quiet periods → less frequent
   - High-activity → more touchpoints

6. **Counter-Thesis Engine**
   - Proactive devil's advocate
   - "You've held this thesis for 30 days with no price movement. Here's what might be wrong."

---

## 9. Technical Stack

### Backend

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Runtime** | Python 3.11+ | ML/AI ecosystem, scraping libraries |
| **API Framework** | FastAPI | Async, modern, good for real-time |
| **Database** | PostgreSQL | Reliable, JSON support, full-text search |
| **Vector DB** | pgvector (PostgreSQL extension) | Semantic search for analogies |
| **Task Queue** | Celery + Redis | Background jobs, scheduled tasks |
| **Cache** | Redis | Rate limiting, session, quick lookups |

### Frontend

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | Next.js 14+ (App Router) | SSR, good DX, React ecosystem |
| **Styling** | Tailwind CSS | Fast iteration, consistent design |
| **Charts** | Recharts or Tremor | Simple, React-native |
| **State** | Zustand or React Query | Lightweight, server-state friendly |

### Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Hosting** | VPS (Hetzner, DigitalOcean) | Cost-effective, full control |
| **LLM - Heavy** | OpenAI GPT-4o / Claude | Event analysis, synthesis |
| **LLM - Light** | Local Llama/Mistral (Ollama) | Classification, extraction |

### Estimated Costs (Monthly)

| Item | Cost |
|------|------|
| VPS (4GB RAM, 2 vCPU) | $12-20 |
| OpenAI API | $20-50 (depending on usage) |
| All data sources | Free |
| **Total** | ~$30-70/month |

**By Phase (rough):**

| Phase | Monthly Cost | What It Covers |
|-------|--------------|----------------|
| Phase 1 (MVP) | ~$30-50 | LLM event analysis + thesis seeding |
| Phase 2 (V1) | ~$40-60 | + Crypto narrative/signal analysis |
| Phase 3 (V2) | ~$50-70 | + Counter-thesis engine + learning loops |

**Cost optimization tips:**
- Use a cheaper model for classification tasks (event type, sentiment, entity extraction).
- Cache AI responses for similar patterns and batch events (daily synthesis vs. real-time).
- Prefer local models (Ollama) for extraction/filtering; reserve heavier models for synthesis.

---

## 10. Cold Start Strategy

### 10.1 Historical Macro Case Base

**Day 1 Requirement:** 25-40 curated case studies

**Per-Case Structure:**
```yaml
event_name: "Russia/Ukraine Invasion"
date_range: "Feb 2022 - ongoing"
event_type: "geopolitical_conflict"
significance_score: 85

structural_drivers:
  - "Energy supply shock (Russia = major oil/gas)"
  - "Sanctions regime (financial system stress)"
  - "Inflation acceleration"
  - "Safe haven demand spike"

metal_impacts:
  gold:
    direction: "up"
    magnitude: "+8% initial, +15% over 6 months"
    driver: "Safe haven demand"
  silver:
    direction: "up"
    magnitude: "+12% over 6 months"
    driver: "Following gold + industrial concerns"
  copper:
    direction: "volatile"
    magnitude: "+5% then -10%"
    driver: "Demand concerns vs. supply disruption"

traditional_market_reaction:
  - "Oil +60% in 3 months"
  - "EUR/USD -12%"
  - "European equities -15%"

crypto_reaction:
  - "BTC -15% initial (risk-off)"
  - "Stablecoin demand spike in Russia/Ukraine"
  - "No sustained safe haven bid for BTC"

crypto_transmission:
  exists: true
  path: "Capital controls → stablecoin demand (but not BTC)"
  strength: "weak"

time_delays:
  - "Gold: Immediate spike, sustained over months"
  - "Commodity inflation: 3-6 month feed-through"

lessons:
  - "War ≠ automatic BTC pump"
  - "Traditional safe havens (gold) outperformed"
  - "Stablecoin > BTC for capital flight"

counter_examples:
  - "Unlike smaller conflicts, this had direct energy/commodity implications"
  - "Sanctions made this more impactful than typical regional war"
```

**Mandatory Inclusions:**

| Event | Year | Primary Metal Impact |
|-------|------|---------------------|
| Global Financial Crisis | 2008 | Gold +25% |
| Eurozone Debt Crisis | 2010-12 | Gold +50% |
| Cyprus Bail-in | 2013 | Gold spike, BTC first noticed |
| Brexit Vote | 2016 | Gold +8% immediate |
| Trump Election | 2016 | Gold -5% (surprise) |
| COVID Crash | Mar 2020 | Gold -10% then +30% |
| COVID QE Era | 2020-21 | Gold +25%, Silver +50% |
| Inflation Spike | 2021-22 | Gold flat (real rates rising) |
| Fed Hiking Cycle | 2022-23 | Gold -15% |
| Russia/Ukraine | 2022 | Gold +15%, Silver +12% |
| SVB Banking Crisis | 2023 | Gold +10% |
| Fed Pivot Signal | 2023-24 | Gold +20% |
| ETF Approvals | 2024 | BTC +100%+ |

### 10.2 Metals Knowledge Base

Pre-built on Day 1 for Gold, Silver, Copper:
- Supply chain data (producers, consumers, chokepoints)
- Use case breakdown
- Historical pattern library (10+ patterns per metal)
- Correlation matrix
- Key actor profiles

### 10.3 Economic Calendar Seed

Pre-loaded with:
- All Fed meeting dates (current year + 1)
- ECB, BOJ, BOE meeting dates
- Major data releases (CPI, NFP, GDP)
- Historical impact ratings

---

## 11. UX & Interaction Model

### 11.1 Web Dashboard

**Tab 1: Macro Radar (Primary in Phase 1)**
- Event list with significance scores
- ⚡ PRIORITY badges for high-significance
- Expandable event cards (raw → interpretation)
- Quick filters: By metal impact, by recency, by significance

**Tab 2: Crypto Radar (Phase 2+)**
- Narrative list with crowding scores
- Lifecycle state indicators
- Rotation suggestions

**Tab 3: Metals**
- Gold, Silver, Copper dashboards
- Current price, key levels, ratios
- Supply chain visualization (simple)
- Recent relevant events

**Tab 4: Calendar**
- Upcoming economic events
- Central bank meetings
- Significance highlighting

**Tab 5: Theses**
- Active theses list
- Per-thesis: notes, price since entry, linked events
- Archive of completed theses

**Tab 6: History**
- Historical case base browser
- Searchable by event type, metal, year
- Compare current event to historical

**Design Principles:**
- Clean, information-dense
- Mobile-responsive (phone usable)
- Fast (feels instant)
- Raw facts visually separated from interpretation

### 11.2 Event Card Format (Critical UX)

```
┌─────────────────────────────────────────────────────────────┐
│ ⚡ PRIORITY                                    72/100       │
├─────────────────────────────────────────────────────────────┤
│ Russia announces expanded military operations               │
│ Reuters • 2 hours ago                                       │
├─────────────────────────────────────────────────────────────┤
│ 📰 RAW FACTS                                                │
│                                                             │
│ • Russia announced X in region Y                           │
│ • NATO responded with statement Z                          │
│ • Oil +3.2%, Gold +1.1% since announcement                 │
├─────────────────────────────────────────────────────────────┤
│ 🔍 INTERPRETATION                                           │
│                                                             │
│ Metal Implications:                                         │
│ • Gold: Likely beneficiary. Safe haven demand + inflation  │
│   concern. Watching for sustained bid above $2,050.        │
│ • Silver: Follows gold. Industrial demand concern minor.   │
│ • Copper: Neutral. Not directly affected by this region.   │
│                                                             │
│ Historical Precedent:                                       │
│ "Escalation events in this conflict have preceded gold     │
│ moves of 5-8% over 2-4 weeks. See: Feb 2022, Sep 2022."   │
│                                                             │
│ Counter-Case:                                               │
│ "Markets may be desensitized. Oct 2023 escalation saw      │
│ muted 2% gold response, faded within days. Watch if        │
│ sustained bid develops or quick fade."                     │
│                                                             │
│ Crypto Transmission:                                        │
│ "Weak. Prior escalations showed stablecoin demand in       │
│ region but no BTC safe haven bid. Monitor USDT premium."   │
├─────────────────────────────────────────────────────────────┤
│ 📝 YOUR NOTES                                               │
│ [Click to add notes...]                                     │
│                                                             │
│ [Create Thesis] [Add to Watchlist] [Dismiss]               │
└─────────────────────────────────────────────────────────────┘
```

### 11.3 Telegram Bot

**Phase 1 Commands:**
```
/today          - Daily briefing (priority events + calendar)
/events         - Recent events with significance scores
/gold           - Gold status (price, recent events, key levels)
/silver         - Silver status
/copper         - Copper status
/ratio          - Gold/Silver ratio with historical context
/calendar       - Upcoming high-impact events
/thesis list    - Your active theses (alias: /thesis)
/note [thesis] [text] - Add note to a thesis
/help           - Command list
```

**Phase 2 Additions:**
```
/crypto         - Crypto radar summary (narratives + top signals)
/crowded        - List crowded narratives to avoid
/emerging       - List emerging narratives to watch
/signal [token] - Quick analysis of a token
/macro2crypto   - Current macro-to-crypto transmission paths
/dd [project]   - Start DD workflow
```

**Daily Check-in Message Format:**
```
☀️ MERIDIAN DAILY BRIEFING
Thursday, Jan 2, 2026

⚡ PRIORITY EVENTS (1)
━━━━━━━━━━━━━━━━━━━━━
• Russia military escalation (72/100)
  Gold +1.1% | Analysis ready →

📊 METALS STATUS
━━━━━━━━━━━━━━━━━━━━━
Gold: $2,048 (+0.5%)
Silver: $24.12 (+0.8%)
Copper: $3.82 (-0.2%)
G/S Ratio: 84.9 (elevated)

📅 TODAY'S CALENDAR
━━━━━━━━━━━━━━━━━━━━━
• 10:00 - ISM Manufacturing (HIGH)
• 14:00 - FOMC Minutes (HIGH)

📋 THESIS UPDATES
━━━━━━━━━━━━━━━━━━━━━
• "Silver mean reversion" - Day 12, Silver +3.2%
  
[View Dashboard →]
```

### 11.4 Check-in Cadence

**Default:** Once daily, morning (configurable time)

**Content:**
- Priority events (if any)
- Metals status snapshot
- Today's economic calendar
- Active thesis updates

**Adaptive (Phase 3):**
- High-significance event → additional alert
- Quiet periods → can reduce to every-other-day

---

## 12. Success Metrics & Failure Modes

### 12.1 Success Definition (6 Months)

**Primary (in order):**
1. "I have a system instead of chaos"
2. "I caught 1-2 kingmaker macro plays I would have missed" (e.g., silver)
3. "I caught 2-3 crypto plays I would have missed"
4. "Research feels lighter, not heavier"

**Secondary:**
- Daily check-in becomes habitual
- Theses are documented and trackable
- Historical knowledge is accessible and useful

### 12.2 Failure Modes

| Failure Mode | Mitigation |
|--------------|------------|
| **False confidence** | Counter-cases mandatory, raw/interpretation separation |
| **Too many alerts** | Significance scoring, ⚡ PRIORITY only for ≥65 |
| **Ignored dashboard** | Daily Telegram check-in, habit formation |
| **Stale knowledge** | Regular knowledge base updates, clear versioning |
| **Missed events** | Multiple news sources, manual input fallback |
| **Echo chamber (again)** | Counter-thesis engine challenges active theses |

### 12.3 Kingmaker Trade Criteria

A "kingmaker trade" is:
- High conviction (thesis documented with evidence)
- Significant size relative to portfolio
- Held for days/weeks, not reactive
- Based on macro analysis, not noise
- Outcome tracked for learning

---

## 13. Open Questions

### Technical

1. **News ingestion reliability**: RSS feeds can be delayed. Is this acceptable, or need real-time alternatives?

2. **LLM for event analysis**: How much context needed per event? Token costs could add up.

3. **Knowledge base maintenance**: How to keep supply chain data, actor profiles current?

4. **Price data granularity**: Daily sufficient for thesis-building, or need intraday for entry timing?

### Product

1. **Event deduplication**: Same story from Reuters and AP - how to merge?

2. **Significance score calibration**: How to tune without historical data on our own scoring?

3. **Thesis lifecycle**: When is a thesis "complete"? After trade? After target hit?

4. **Multi-metal events**: Event affects gold AND copper differently - one card or two?

### Data

1. **Central bank parsing**: FOMC statements are dense. How deep to parse vs. summarize?

2. **Economic surprise calculation**: Need reliable expected values - source quality varies.

3. **Metals knowledge freshness**: Supply chain data changes. Annual refresh? Event-triggered?

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Kingmaker trade** | High-conviction macro trade, few per year, thesis-driven |
| **Significance score** | 0-100 rating of macro event importance |
| **Transmission path** | How a macro event translates to asset opportunity |
| **Counter-case** | Reasons why the obvious trade might not work |
| **Thesis** | Documented investment idea with evidence and tracking |
| **Priority event** | Significance ≥ 65, requires attention |

---

## Appendix B: Historical Case Template

```yaml
event_name: ""
date_range: ""
event_type: ""  # geopolitical_conflict, monetary_policy, financial_crisis, etc.
significance_score: 0

structural_drivers:
  - ""

metal_impacts:
  gold:
    direction: ""  # up, down, volatile, flat
    magnitude: ""
    driver: ""
  silver:
    direction: ""
    magnitude: ""
    driver: ""
  copper:
    direction: ""
    magnitude: ""
    driver: ""

traditional_market_reaction:
  - ""

crypto_reaction:
  - ""

crypto_transmission:
  exists: false
  path: ""
  strength: ""  # strong, moderate, weak, none

time_delays:
  - ""

lessons:
  - ""

counter_examples:
  - ""
```

---

## Appendix C: Thesis Template

```markdown
# Thesis: [Name]

**Created:** [Date]
**Status:** Active / Watching / Closed
**Metal/Asset:** Gold / Silver / Copper / [Crypto]

## Core Thesis
*One paragraph: Why this opportunity exists and why now*

## Trigger Event
*What macro event or signal initiated this thesis*

## Historical Precedent
*Similar past events and outcomes*

## Bull Case
- 
- 
- 

## Bear Case / Counter-Case
- 
- 
- 

## Key Levels
- Entry consideration: 
- Target: 
- Invalidation: 

## Position
- Vehicle: (GLD, physical, miners, etc.)
- Size: 
- Entry date: 
- Entry price: 

## Updates Log
| Date | Note | Price |
|------|------|-------|
| | | |

## Outcome
*Filled when thesis closed*
- Exit date: 
- Exit price: 
- Result: 
- Lessons: 
```

---

## Appendix D: Reference - Missed Trades Analysis

### Silver (2024-2025)

**What happened:** Silver rose ~5x during period
**Signal location:** Russia/Ukraine war → commodity supercycle narrative, industrial demand + monetary demand convergence
**Why missed:** No systematic macro monitoring, no metals knowledge base, no historical pattern matching
**Meridian fix:** Event detection → historical precedent (war → commodities) → silver thesis workspace

### Russia/Ukraine Opportunities (2022)

**What happened:** Multiple assets moved (gold, oil, defense stocks, stablecoins)
**Signal location:** News was everywhere, but transmission paths weren't clear
**Why missed:** Saw news but didn't connect to actionable positions
**Meridian fix:** Transmission path analysis (event → which assets → historical magnitude)

---

## Appendix E: Key Trade History (Context)

| Trade | Period | Entry Thesis | Result | Key Lesson |
|-------|--------|--------------|--------|------------|
| Terra/LUNA | 2021-May 2022 | Algorithmic stablecoin adoption drives burn mechanism | -80% net worth | No invalidation thesis, ignored macro, leverage killed |
| Soulgraph | Oct 2024-Q2 2025 | AI + crypto convergence, Y Combinator hints, strong community | $20k → $200k → $5k | No exit plan, held through narrative cooldown |
| NOMAI | Late 2024-2025 | Alphanomics data layer + AI agent, strong team | $110k → $5k | Didn’t account for ecosystem dependency (Virtuals) |
| Gold/Silver | 2024-2025 | (Missed) | N/A | Saw inputs but couldn’t synthesize thesis; silver required connecting safe-haven + industrial + supply dynamics |

---

## Appendix F: Database Schema (Draft)

Starting-point PostgreSQL schema (Phase 1 MVP). Expect evolution, but keep the core entities stable: events, theses, knowledge, historical cases.

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- Theses: investment ideas you're building conviction on
CREATE TABLE IF NOT EXISTS theses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Core
  title TEXT NOT NULL,               -- "Silver: Safe-haven + Industrial Convergence"
  asset_type TEXT NOT NULL,          -- 'gold', 'silver', 'copper', 'btc', 'eth', 'altcoin'
  asset_symbol TEXT,                 -- 'SI=F', 'SLV', 'BTC'

  -- Thesis content
  trigger_event TEXT,                -- What initiated this thesis
  core_thesis TEXT NOT NULL,         -- One paragraph: why this, why now
  bull_case TEXT[],                  -- Array of bull points
  bear_case TEXT[],                  -- Array of bear/counter points (MANDATORY)
  historical_precedent TEXT,         -- Similar past events

  -- Levels
  entry_consideration TEXT,          -- Price zone for entry consideration
  target TEXT,                       -- Price target with reasoning
  invalidation TEXT,                 -- What kills this thesis (CRITICAL)

  -- Position (if taken)
  vehicle TEXT,                      -- 'GLD', 'physical', 'NEM', 'SLV', 'direct'
  position_size TEXT,
  entry_date TIMESTAMPTZ,
  entry_price NUMERIC,

  -- Status
  status TEXT DEFAULT 'watching',    -- 'watching', 'active', 'closed'

  -- Tracking
  price_at_creation NUMERIC,
  current_price NUMERIC,
  price_change_percent NUMERIC,

  -- Notes over time
  updates JSONB                      -- [{ date: '...', note: '...', price: ... }]
);

-- Macro Events: detected from news wires / comms / manual input
CREATE TABLE IF NOT EXISTS macro_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Source data
  source TEXT NOT NULL,              -- 'reuters', 'ap', 'fed', 'ecb', 'manual'
  headline TEXT NOT NULL,
  full_text TEXT,
  url TEXT,
  published_at TIMESTAMPTZ,

  -- Classification
  event_type TEXT,                   -- 'geopolitical', 'monetary_policy', 'economic_data', etc.
  regions TEXT[],                    -- ['US', 'EU', 'China']
  entities TEXT[],                   -- ['Federal Reserve', 'PBOC', 'Russia']

  -- Scoring
  significance_score INTEGER,        -- 0-100
  score_components JSONB,            -- { structural: 35, transmission: 28, historical: 18, attention: 12 }
  priority_flag BOOLEAN DEFAULT FALSE,  -- TRUE if score >= 65

  -- Analysis
  raw_facts TEXT[],                  -- Extracted facts, uninterpreted
  metal_impacts JSONB,               -- { gold: { direction: 'bullish', reasoning: '...' }, ... }
  historical_precedent TEXT,         -- "Similar to X in Y year..."
  counter_case TEXT,                 -- "However, this time might differ because..."
  crypto_transmission JSONB,         -- { exists: true, path: 'BTC digital gold narrative', strength: 'moderate' }

  -- Status
  status TEXT DEFAULT 'new',         -- 'new', 'analyzed', 'thesis_created', 'dismissed'
  thesis_id UUID REFERENCES theses(id)
);

-- Metals Knowledge Base: pre-built understanding
CREATE TABLE IF NOT EXISTS metals_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metal TEXT NOT NULL,               -- 'gold', 'silver', 'copper'
  category TEXT NOT NULL,            -- 'supply_chain', 'use_cases', 'patterns', 'correlations', 'actors'
  content JSONB NOT NULL,            -- Structured knowledge (see section 6.2)
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Historical Cases: past macro events for pattern matching
CREATE TABLE IF NOT EXISTS historical_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_name TEXT NOT NULL,
  date_range TEXT,
  event_type TEXT,
  significance_score INTEGER,

  -- Impacts
  structural_drivers TEXT[],
  metal_impacts JSONB,               -- { gold: { direction: 'up', magnitude: '+25%', driver: '...' }, ... }
  traditional_market_reaction TEXT[],
  crypto_reaction TEXT[],

  -- Transmission
  crypto_transmission JSONB,         -- { exists: true, path: '...', strength: 'strong' }

  -- Learning
  time_delays TEXT[],
  lessons TEXT[],
  counter_examples TEXT[],

  -- Embeddings for semantic search (dimension matches embedding model)
  embedding vector(1536)
);

-- Central Bank Communications
CREATE TABLE IF NOT EXISTS central_bank_comms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bank TEXT NOT NULL,                -- 'fed', 'ecb', 'boj', 'boe'
  comm_type TEXT,                    -- 'statement', 'minutes', 'speech', 'press_conference'
  published_at TIMESTAMPTZ,
  full_text TEXT,

  -- Analysis
  key_phrases TEXT[],
  sentiment TEXT,                    -- 'hawkish', 'dovish', 'neutral'
  sentiment_score NUMERIC,           -- -1 to +1
  change_vs_previous TEXT,           -- What changed from last communication
  forward_guidance TEXT
);

-- Economic Calendar Events
CREATE TABLE IF NOT EXISTS economic_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_name TEXT NOT NULL,
  event_date TIMESTAMPTZ NOT NULL,
  region TEXT,
  impact_level TEXT,                 -- 'high', 'medium', 'low'

  -- Values
  expected_value TEXT,
  actual_value TEXT,
  previous_value TEXT,

  -- Surprise
  surprise_direction TEXT,           -- 'beat', 'miss', 'inline'
  surprise_magnitude NUMERIC,

  -- Historical impact on metals
  historical_metal_impact JSONB
);

-- Daily Digests (cached for Telegram bot)
CREATE TABLE IF NOT EXISTS daily_digests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  digest_date DATE NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  priority_events JSONB,             -- Events with significance >= 65
  metals_snapshot JSONB,             -- { gold: { price: ..., change: ... }, ... }
  economic_calendar JSONB,           -- Today's high-impact events
  active_theses JSONB,               -- Updates on active theses
  full_digest TEXT                   -- Rendered markdown for Telegram
);
```

---

## Appendix G: LLM Prompt Templates

### Macro Event Analysis Prompt

```text
You are a macro intelligence analyst helping identify kingmaker trades.

## Your Role
Analyze macro events for their potential to generate high-conviction, thesis-driven trades in metals (gold, silver, copper) and their potential transmission to crypto.

## Metals Knowledge Context
{metals_knowledge_json}

## Historical Cases Context
{relevant_historical_cases_json}

## Event to Analyze
Source: {source}
Headline: {headline}
Full Text: {full_text}
Published: {published_at}

## Required Output

### 1. RAW FACTS (Uninterpreted)
Extract 3-5 key facts from the event. No interpretation yet.
• [Fact 1]
• [Fact 2]
• [Fact 3]

### 2. SIGNIFICANCE SCORE (0-100)
Rate the event's significance for metals/macro trading:

| Component | Weight | Score | Reasoning |
|-----------|--------|-------|-----------|
| Structural Impact | 35% | [X] | [One sentence] |
| Asset Transmission Path | 30% | [X] | [One sentence] |
| Historical Market Reaction | 20% | [X] | [One sentence] |
| Attention & Reflexivity | 15% | [X] | [One sentence] |
| TOTAL | 100% | [X] | |

If score >= 65, flag as ⚡ PRIORITY

### 3. METAL IMPACTS (If relevant)

Gold:
- Direction: [Bullish/Bearish/Neutral]
- Reasoning: [Why this event affects gold]
- Magnitude estimate: [If applicable]

Silver:
- Direction: [Bullish/Bearish/Neutral]
- Reasoning: [Why - note both monetary AND industrial angles]
- Magnitude estimate: [If applicable]

Copper:
- Direction: [Bullish/Bearish/Neutral]
- Reasoning: [Economic bellwether angle]
- Magnitude estimate: [If applicable]

### 4. HISTORICAL PRECEDENT
Identify the most relevant historical parallel:
- Event: "[Name]" ([Year])
- What happened: [Outcome for metals]
- Similarity to current: [Why this rhymes]

### 5. COUNTER-CASE (MANDATORY)
Why might the obvious trade NOT work?
- [Reason 1]
- [Reason 2]
- [Counter-example from history if available]

### 6. CRYPTO TRANSMISSION PATH
Does this macro event have a path to crypto?

- Transmission exists: [Yes/No]
- If yes, path: [e.g., "Banking crisis → BTC digital gold narrative"]
- Strength: [Strong/Moderate/Weak/None]
- Relevant assets: [BTC, stablecoins, specific altcoins]

### 7. THESIS SEED (If score >= 65)
If this is a priority event, seed a potential thesis:
- Thesis title: [Name]
- Core idea: [One paragraph]
- Vehicle options: [GLD, SLV, miners, physical, etc.]
- What to watch: [Confirming/disconfirming signals]

## Guidelines
- Be direct and specific, not vague
- Prioritize structural analysis over news cycle noise
- Always include counter-case - prevents false confidence
- If event doesn't warrant metal analysis, say so and score low
- Remember: kingmaker trades, not noise trading
```

### Counter-Thesis Engine Prompt

```text
You are a devil's advocate challenging an active investment thesis.

## Active Thesis
Title: {thesis_title}
Asset: {asset}
Created: {created_date}
Core Thesis: {core_thesis}
Bull Case: {bull_case}
Current Bear Case: {bear_case}

## Current Status
Price at creation: {price_at_creation}
Current price: {current_price}
Change: {change_percent}%
Days held: {days_held}
User notes: {recent_notes}

## Your Task
Proactively challenge this thesis. Be constructive but rigorous.

### 1. THESIS HEALTH CHECK
- Is the original thesis still intact?
- Have any bull case points been invalidated?
- Have any bear case points materialized?

### 2. NEW COUNTER-ARGUMENTS
What new information or perspectives should challenge this thesis?
- Market developments since thesis creation
- Competing narratives
- Technical/price action concerns
- Timing concerns

### 3. INVALIDATION PROXIMITY
How close are we to invalidation triggers?
- Price-based: [Distance to stop/invalidation]
- Time-based: [Expected duration vs. actual]
- Fundamental: [Any triggering events]

### 4. RECOMMENDATION
- HOLD: Thesis intact, stay the course
- REASSESS: Material concerns, needs attention
- CLOSE: Invalidation triggered or imminent

### 5. QUESTIONS FOR THE USER
What should the user be monitoring or researching to maintain conviction?
```

---

## Appendix H: Build Plan Checklists

### Phase 1 (Weeks 1-8): MVP Macro Intelligence

**Week 1-2: Foundation**
- [ ] PostgreSQL database with full schema
- [ ] News ingestion pipeline (Reuters, AP RSS)
- [ ] Basic event classification

**Week 3-4: Intelligence Layer**
- [ ] Metals knowledge base loaded (gold, silver, copper)
- [ ] Historical case base (25-40 events)
- [ ] LLM integration for event analysis
- [ ] Significance scoring

**Week 5-6: Dashboard**
- [ ] Next.js app with Macro Radar tab
- [ ] Event deep dive view
- [ ] Metals Intelligence view
- [ ] Basic thesis workspace

**Week 7-8: Check-in & Polish**
- [ ] Telegram bot with basic commands
- [ ] Daily digest generation
- [ ] Central bank communication tracking
- [ ] Economic calendar integration

### Phase 2 (Weeks 9-14): Crypto Layer + Transmission

**Week 9-10: Telegram Integration**
- [ ] Telegram bot receives forwarded signals
- [ ] Parsers for “Hawk AI”, “From The Trenches” formats
- [ ] Signal storage and enrichment (CoinGecko data)

**Week 11-12: Crypto Intelligence**
- [ ] Narrative detection from CryptoPanic
- [ ] Crowding score algorithm
- [ ] Lifecycle state tracking
- [ ] Crypto Radar tab in dashboard

**Week 13-14: Transmission Layer**
- [ ] Macro-to-crypto transmission logic
- [ ] Signal scoring with macro alignment
- [ ] Watchlist with Telegram alerts
- [ ] Enhanced Telegram bot commands

### Phase 3 (Weeks 15-24): Learning & Advanced

**Week 15-17: Performance Tracking**
- [ ] Thesis-to-trade linking
- [ ] Win/loss tracking and statistics
- [ ] Source performance metrics

**Week 18-20: Counter-Thesis Engine**
- [ ] Scheduled thesis challenges
- [ ] AI counter-argument generation
- [ ] Invalidation proximity alerts

**Week 21-22: Historical & Visualization**
- [ ] Semantic search for historical cases
- [ ] Narrative timeline visualization
- [ ] Cycle pattern analysis

**Week 23-24: Behavioral Learning**
- [ ] Behavioral pattern detection
- [ ] Adaptive check-in cadence
- [ ] Personalized recommendations

### Quick Start: Week 1-2 Sprint (Fastest path to value)

**Days 1-3: Foundation**
1. Set up PostgreSQL database with core schema (events, theses, knowledge base)
2. Create Next.js app with basic routing
3. Set up LLM API integration

**Days 4-7: Metals Knowledge Base**
1. Load gold, silver, copper knowledge (from section 6.2)
2. Load 10-15 historical cases (start with major ones: 2008 GFC, 2020 COVID, 2022 Russia/Ukraine)
3. Build basic Metals Intelligence view

**Days 8-10: Event Detection**
1. Set up RSS ingestion (Reuters, AP)
2. Basic event extraction and classification
3. Connect to LLM for significance scoring

**Days 11-14: Daily Check-in**
1. Build Telegram bot with `/today` command
2. Daily digest generation
3. Basic thesis workspace

---

*End of Specification*
