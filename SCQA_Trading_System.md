# (Archived) SCQA: Building a Personal Trading Intelligence System

> NOTE: This document has been merged into `spec.md` (Meridian unified spec) and is kept only for historical reference. Please use `spec.md` as the canonical source of truth.

---

## Situation

I've been actively trading in crypto markets since 2020, progressing from early-stage altcoins to larger-cap ecosystem plays to narrative-driven trades. Over five years, I've developed a trading identity as a **narrative trader**: someone who identifies macro themes early and takes concentrated positions based on conviction in the underlying thesis.

### The Early Years (2020-2021): Learning the Game

My first foray was into the BNB chain during the 2020/2021 cycle, trading what were then called "shitcoins." My initial successful trade was $CUMMIES, a token aiming to "decentralize OnlyFans." The thesis was simple: the adult industry was growing, and decentralization was novel. While profitable, I quickly realized that low-cap memecoin trading demanded constant attention and wasn't sustainable for my style.

### The Terra Luna Era (2021-2022): Conviction and Catastrophe

In 2021, I shifted to larger-cap ecosystem plays. My first major conviction trade was Terra ($LUNA), built on a thesis I deeply believed in: **algorithmic stablecoins were the future of decentralized finance**. The elegant mechanism (where $UST and $LUNA maintained a burn/mint relationship) meant that increased stablecoin adoption would structurally drive $LUNA's value higher.

I went all-in. Not just financially, but mentally. I was building, making connections in the ecosystem, and actively working to help Terra succeed. I even constructed a leveraged yield strategy:

- Converted liquid assets to staked derivatives (bLUNA, wasAVAX)
- Deposited into Anchor Protocol as collateral
- Borrowed ~30k UST against ~100k in collateral
- Deployed borrowed UST into yield-generating NFT plays (Crabada/TUS farming)
- Target: perpetual passive income with ~120-day loan payback period

Then, on May 7-9, 2022, UST de-pegged. Within days, LUNA collapsed from $80+ to effectively zero, wiping out ~$45 billion in market cap. I lost approximately **80% of my net worth**.

**What I learned (documented in my post-mortem):**

1. **I had a thesis but no invalidation thesis.** I never quantified what would make me wrong or defined exit triggers.
2. **I ignored macro entirely.** I didn't understand what US10Y-US2Y meant, what VIXY represented, or how risk-off environments affect crypto.
3. **I was in an echo chamber.** Valid criticisms of Terra's sustainability were dismissed as FUD.
4. **Leverage amplified the damage.** I couldn't repay the Anchor loan in time (needed 70 more days), losing my wasAVAX and bATOM collateral on top of LUNA losses.

### The Recovery Period (2023-2025): Back to Narratives

After processing the loss, I returned to shorter-term narrative trades in the memecoin and AI agent space. Some highlights:

**Soulgraph (Oct/Nov 2024 - Q2 2025): Good Entry, Poor Exit**

During the AI narrative boom of late 2024, I identified Soulgraph, a Solana-based AI project similar to Character.AI that let users create and interact with personalized AI companions. My conviction came from:
- Novel product concept in a hot narrative (AI + crypto convergence)
- Founder hints at Y Combinator background on Twitter
- Strong community engagement and bullish sentiment from credible accounts

I entered around October/November 2024 with ~$20k. The position ran to approximately **$200k** as the AI agent narrative peaked. But I held through the downturn, eventually taking profit only to rotate into another position. Final exit: ~$5k.

**NOMAI (Late 2024 - 2025): Compounded Losses**

With profits from Soulgraph, I entered NOMAI, an AI agent built by Alphanomics (an on-chain data analytics platform) and deployed on Virtuals Protocol (Base chain). The thesis seemed sound:
- Alphanomics had legitimate infrastructure (data layer for blockchain analytics)
- NOMAI was the AI intelligence layer surfacing trading signals from that data
- Strong team with real product

I deployed ~$110k. But NOMAI was a sub-token of the Virtuals ecosystem, meaning its price was partially dependent on Virtuals Protocol's performance. As the broader AI agent narrative cooled and Virtuals declined, NOMAI fell with it, regardless of its fundamentals. Final value: ~$5k.

**The Gold and Silver Trade I Missed**

During this period, I also noticed the gold and silver rally building throughout 2024-2025. I was aware of some of the inputs:
- Russia-Ukraine war creating geopolitical uncertainty
- US dollar weakness
- Central bank buying accelerating
- Rate cut expectations

Yet I couldn't **connect the dots** into an actionable thesis. I saw the same information that led gold to surge 70%+ in 2025, but I didn't trade it.

The silver trade was even more compelling, and I missed it entirely. Silver hit all-time highs in 2025 (surpassing $75/oz by late December), rising over 150% year-to-date. What made silver unique was its **dual identity** as both a safe-haven asset AND an industrial metal:

**The Safe-Haven Demand (like gold):**
- Geopolitical tensions driving flight to hard assets
- Dollar weakness and rate cut expectations making non-yielding assets attractive
- Russia announcing plans to acquire $535 million in silver over three years (first central bank to explicitly include silver in purchases during this cycle)

**The Industrial Demand (unlike gold):**
- Silver has the highest electrical conductivity of any metal, making it irreplaceable in green technology
- Solar photovoltaic (PV) sector accounted for 29% of industrial silver demand in 2024, up from just 11% in 2014
- Electric vehicles use 2-3x more silver than traditional cars (25-50 grams per vehicle)
- AI data centers driving massive electricity demand, much of which is met by solar installations requiring silver
- The US added silver to its critical minerals list in 2025, signaling strategic importance

**The Supply Squeeze:**
- 2025 marked the fifth consecutive year of structural supply deficit
- Global silver demand reached 1.2 billion ounces in 2024, while mine production stagnated at ~813 million ounces
- The Silver Institute projected a 2025 deficit of approximately 117 million ounces
- Physical inventories at major trading hubs (Shanghai, London) hit multi-year lows

The thesis was hiding in plain sight: **geopolitical uncertainty + monetary easing + green energy transition + structural supply deficit = silver outperformance**. The information was all there. My ability to synthesize it into a trade was not.

---

## Complication

Entering 2026, I find myself in **stablecoins, waiting for conviction that won't come.** The problem isn't a lack of information; it's the opposite.

### 1. Information Overload Without Structure

I currently monitor multiple Telegram bots that track profitable wallets and surface token alerts:

**Hawk AI** provides signals like:
```
🚀 5 profitable traders bought a token in the last hour
Token: HOUSE | MC: $976.3k | Net Buy: $8.2k
Top Traders: [wallet addresses with 30d PNL and entry prices]
```

**From The Trenches** surfaces momentum plays:
```
PROFIT ALERT 🚀
├Multiplier:    42X
├Initial FDV:  $44.5K
└Current FDV:  $1.9M
```

These bots generate dozens of signals daily. Each signal represents a potential trade. But:
- There's no thesis attached, just on-chain flow data
- I can't evaluate which signals align with broader narratives
- There's no framework to determine position sizing, entry timing, or exit criteria

### 2. No Structured Trading Process

In five years of trading, I've never had:
- A formal trade memo documenting entry thesis, invalidation criteria, and target exits
- Defined take-profit or stop-loss levels
- A system for reviewing past trades to identify patterns in my decision-making

My Luna post-mortem was written *after* losing 80% of my net worth. Soulgraph and NOMAI didn't get post-mortems at all. I just watched six-figure gains evaporate because I had no predefined exit triggers.

### 3. The "Connecting Dots" Problem

I am a **narrative trader** who struggles to synthesize narratives from raw information. Consider the precious metals trades I missed:

**Gold:**
| What I Knew | What I Didn't Process |
|-------------|----------------------|
| Russia-Ukraine war ongoing | → Safe-haven demand accelerating |
| US showing economic weakness | → Dollar depreciation = gold tailwind |
| Fed likely to cut rates | → Non-yielding assets become attractive |
| Central banks buying gold | → Structural demand shift, not just speculation |

**Silver:**
| What I Knew | What I Didn't Process |
|-------------|----------------------|
| Same geopolitical tensions as gold | → Safe-haven demand (like gold) |
| Green energy transition accelerating | → Solar panels require silver (highest conductivity of any metal) |
| EV adoption growing | → EVs use 2-3x more silver than traditional cars |
| AI/data center boom | → Massive electricity demand met by solar = silver demand |
| (I didn't know) Supply deficits for 5 years | → Structural imbalance driving prices higher |

The silver thesis required connecting **two separate narratives** (safe-haven + industrial demand) plus understanding supply dynamics. I didn't have the knowledge base or the systematic process to do this. As the saying goes, "the market rhymes," but I don't know enough history to hear the rhyme.

### 4. Confidence Erosion

After Luna (-80% net worth), Soulgraph (gave back 90%+ gains), and NOMAI (-95%), my decision-making confidence is damaged. I face two distinct problems:

1. **I don't see clear narratives right now.** The obvious plays (AI agents, memecoins) feel late-cycle. But I might be wrong, and I can't tell.

2. **I don't trust my judgment.** Even if I identify a narrative, I question whether I'll execute properly or repeat the same mistakes (no exit plan, holding too long, echo chamber thinking).

### 5. Markets Have Evolved

The 2020-2021 playbook (find a novel narrative, buy early, hold for months) doesn't work the same way in 2025-2026. Markets are:
- **Faster**: Narratives play out in weeks, not months
- **More crowded**: Alpha decays quickly as information spreads
- **More complex**: Cross-chain dynamics (Virtuals affecting NOMAI), macro correlations, and institutional involvement add layers

Meanwhile, opportunities exist across multiple timeframes:
- **Macro/Long-term (6-12+ months)**: Gold, silver, sector rotations, structural trends
- **Narrative (1-6 months)**: AI agents, DeFi innovations, emerging categories

I want to play both. But I need a system that helps me see, evaluate, and execute across these timeframes.

---

## Question

**How do I build a personal trading intelligence system that transforms fragmented information into structured, actionable trade theses, while compensating for my weaknesses in macro knowledge, historical pattern recognition, and disciplined execution?**

Specifically, the system should:

### 1. Centralize and Modularize Data Sources
- **Macro/News**: Geopolitical developments, central bank actions, rate decisions, currency movements
- **On-Chain Data**: Wallet tracking, smart money flows, token metrics
- **Social/Sentiment**: Twitter/X feeds, Telegram alpha groups, community sentiment
- **Market Data**: Price action, volume, correlations across assets

The architecture should be modular, allowing me to add or remove sources as needs evolve.

### 2. Preprocess Information for Signal Extraction
Raw data is noise. The system should:
- Filter for relevance based on my trading style (narrative + macro)
- Identify emerging patterns across data sources
- Flag anomalies or divergences worth investigating

### 3. AI-Assisted Dot Connection
This is the core value. Given my weakness in synthesizing narratives, AI should:
- Surface potential trade theses based on detected patterns
- Provide historical context ("the last time X happened, Y followed")
- Explain the causal logic connecting data points to potential outcomes
- Offer objective analysis without echo chamber bias

### 4. Structured Trade Memo Generation
When I decide to investigate a signal, the system should help generate:
- **Thesis**: Why this trade? What narrative or macro theme supports it?
- **Invalidation Criteria**: What would make the thesis wrong? (Quantified)
- **Entry/Exit Framework**: Target entry zone, take-profit levels, stop-loss triggers
- **Position Sizing**: Based on conviction level and risk parameters
- **Timeline**: Expected duration and key milestones/catalysts

### 5. Support Multiple Timeframes
- **Macro Module**: Long-term plays (6-12+ months) like precious metals, sector rotations
- **Narrative Module**: Medium-term plays (1-6 months) like emerging crypto categories

Different data sources and analysis frameworks for each.

### 6. Trading Journal Integration
Document the journey:
- Record all trades with original thesis and outcome
- Track decision-making patterns over time
- Enable retrospective analysis ("Why did I hold Soulgraph too long?")

---

## Answer

The solution is **Meridian**: an externalized macro intelligence brain that surfaces kingmaker opportunities in metals and crypto through systematic event monitoring, historical pattern matching, and thesis-building workflows.

> "Where macro currents and crypto narratives converge."

The system is designed around three core principles:

1. **Macro-first, not crypto-first**: Start with global events, policy signals, and commodity intelligence. Crypto opportunities are derived downstream OR run as a parallel gap-filling track.
2. **Kingmaker framing**: Optimized for a few high-conviction trades per year with deep research, not reactive signal processing.
3. **Raw → Interpreted separation**: Raw facts from primary sources first, AI interpretation clearly separated. You form your own conviction; the system provides scaffolding.

---

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              MERIDIAN                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    MACRO INTELLIGENCE LAYER                        │ │
│  │                                                                    │ │
│  │  News Wires ──► Event Detection ──► Significance Score (0-100)    │ │
│  │       +                                                           │ │
│  │  Fed/ECB/BOJ ──► Policy Signals ──► Hawkish/Dovish Trend         │ │
│  │       +                                                           │ │
│  │  Economic Calendar ──► Data Releases ──► Surprise Detection       │ │
│  │       +                                                           │ │
│  │  Metals Intelligence (Gold, Silver, Copper)                       │ │
│  │       │                                                           │ │
│  │       ▼                                                           │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │  MACRO OPPORTUNITIES (Kingmaker Trades)                     │  │ │
│  │  │  • Metals plays (physical, miners, ETFs)                    │  │ │
│  │  │  • Historical precedent + counter-case                      │  │ │
│  │  │  • Thesis workspace                                         │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    TRANSMISSION LAYER                              │ │
│  │                                                                    │ │
│  │  Macro Event ──► Does a Crypto Transmission Path Exist?           │ │
│  │       │                                                           │ │
│  │       ├── YES ──► Crypto opportunity (macro-derived)              │ │
│  │       │           "Banking crisis → BTC digital gold narrative"   │ │
│  │       │                                                           │ │
│  │       └── NO ───► Pure macro play, no crypto angle                │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              +                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │              CRYPTO-NATIVE LAYER (Parallel Track)                  │ │
│  │                                                                    │ │
│  │  Telegram Bots ──► Signal Ingestion                               │ │
│  │  CryptoPanic ──► Narrative Detection                              │ │
│  │  Twitter/X ──► Sentiment & Crowding                               │ │
│  │       │                                                           │ │
│  │       ▼                                                           │ │
│  │  CRYPTO-NATIVE OPPORTUNITIES (Gap-Filling)                        │ │
│  │  • Memecoins, AI agents, protocol upgrades                        │ │
│  │  • Narrative rotation plays                                        │ │
│  │  • Crowding score to avoid late entries                           │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      INTERFACE LAYER                               │ │
│  │                                                                    │ │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │ │
│  │  │ MACRO RADAR │    │CRYPTO RADAR │    │ DAILY CHECK-IN      │   │ │
│  │  │ (Primary)   │    │(Secondary)  │    │ "⚡ Priority" or    │   │ │
│  │  │             │    │             │    │ "Nothing urgent"    │   │ │
│  │  └─────────────┘    └─────────────┘    └─────────────────────┘   │ │
│  │                                                                    │ │
│  │  Telegram Bot  │  Thesis Workspace  │  Historical Case Search     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Attention Model (Hybrid)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DAILY MODE                                       │
│                                                                         │
│  Default State:                                                         │
│  • Macro radar: MONITORING (always-on, thesis-building)                 │
│  • Crypto-native radar: ACTIVE (gap-filling when macro quiet)           │
│                                                                         │
│  When Macro Event Detected (significance ≥ 65):                         │
│  • "⚡ PRIORITY" flag surfaces                                          │
│  • Macro radar: ACTIVE (primary focus)                                  │
│  • Days/weeks to build thesis, not reactive trading                     │
│                                                                         │
│  Cross-Pollination:                                                     │
│  • Macro events checked for crypto transmission paths                   │
│  • Crypto narratives checked for macro drivers                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Technology Stack

| Layer | Technology | Cost | Notes |
|-------|------------|------|-------|
| **Backend** | Python 3.11+ / FastAPI | Free | ML/AI ecosystem, async, good for real-time |
| **Database** | PostgreSQL (Supabase free tier) | Free | 500MB, JSON support, full-text search |
| **Vector Search** | pgvector extension | Free | Semantic search for historical analogies |
| **Task Queue** | Celery + Redis | Free | Background jobs, scheduled ingestion |
| **Frontend** | Next.js 14 (App Router) | Free | SSR, React ecosystem, Vercel hosting |
| **AI (Heavy)** | Claude API (claude-sonnet-4-20250514) | ~$30-50/mo | Event analysis, synthesis, thesis generation |
| **AI (Light)** | Local Ollama (Llama/Mistral) | Free | Classification, extraction, filtering |
| **News** | Reuters/AP RSS feeds | Free | Breaking macro event detection |
| **Central Banks** | Fed/ECB/BOJ official sites | Free | Policy communication parsing |
| **Economic Calendar** | Investing.com/TradingEconomics | Free | Data releases, surprise detection |
| **Metals Prices** | Yahoo Finance | Free | GC=F, SI=F, HG=F, miners, ETFs |
| **Crypto Data** | CoinGecko (Demo tier) | Free | 30 calls/min, 10k calls/month |
| **Hosting** | Vercel (free) + VPS ($12-20/mo) | ~$15/mo | Frontend free, backend on cheap VPS |

**Total estimated cost: $45-70/month**

**Upgrade path when budget allows:**
- Supabase Pro ($25/mo): No pausing, 8GB storage, daily backups
- Dedicated VPS ($40/mo): More compute for local LLM
- Nansen/Token Metrics ($100-300/mo): Smart money tracking for crypto layer

---

### Implementation Phases

The system is built in three phases, each delivering immediate value. Unlike reactive trading systems, Meridian is designed for **thesis-building over days/weeks**, surfacing a few high-conviction kingmaker opportunities per year.

---

## Phase 1: Macro Intelligence (Weeks 1-8)
**Goal: Event detection, metals intelligence, thesis workspace, daily check-in**
**Time: ~25-35 hours total**

This phase solves the silver problem: you saw the inputs (Russia/Ukraine, dollar weakness, rate cuts) but couldn't connect them to an actionable thesis. Phase 1 gives you the synthesis layer.

### What You Get

1. **Macro Event Detection**
   - News wire ingestion (Reuters, AP RSS feeds)
   - Event extraction and classification
   - Significance scoring (0-100)
   - ⚡ PRIORITY flagging for events ≥65

2. **Metals Intelligence Dashboard**
   - Gold, Silver, Copper coverage
   - Pre-built knowledge base (supply chains, historical patterns, correlations)
   - Current prices + key levels + gold/silver ratio
   - Key actor tracking (central banks, ETF flows, miners)

3. **Historical Case Base**
   - 25-40 curated macro events with metal impacts
   - Searchable by event type, metal, outcome
   - Linked to current event analysis ("this rhymes with X")

4. **Thesis Workspace**
   - Create thesis for any opportunity
   - Bull case + counter-case (mandatory)
   - Track price since thesis creation
   - Notes over time
   - Export as markdown

5. **Daily Check-in (Telegram Bot)**
   - Morning summary: "⚡ PRIORITY: [Event]" or "Nothing urgent - monitoring mode"
   - Upcoming economic calendar
   - Active thesis updates
   - Quick commands: `/today`, `/gold`, `/silver`, `/copper`, `/events`

### Database Schema

```sql
-- Macro Events: Detected from news wires
CREATE TABLE macro_events (
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

-- Metals Knowledge Base: Pre-built understanding
CREATE TABLE metals_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metal TEXT NOT NULL,               -- 'gold', 'silver', 'copper'
  category TEXT NOT NULL,            -- 'supply_chain', 'use_cases', 'patterns', 'correlations', 'actors'
  content JSONB NOT NULL,            -- Structured knowledge (see spec section 6.2)
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Historical Cases: Past macro events for pattern matching
CREATE TABLE historical_cases (
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
  
  -- Embeddings for semantic search
  embedding vector(1536)
);

-- Theses: Investment ideas you're building conviction on
CREATE TABLE theses (
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

-- Central Bank Communications
CREATE TABLE central_bank_comms (
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
CREATE TABLE economic_events (
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
CREATE TABLE daily_digests (
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

### Metals Knowledge Base Structure

Each metal has structured knowledge covering five areas:

```yaml
# Example: Silver
silver:
  supply_chain:
    top_producers:
      - country: Mexico
        share: 24%
        notes: "Largest producer, peso correlation"
      - country: China
        share: 14%
        notes: "Domestic consumption high"
      - country: Peru
        share: 12%
        notes: "Political instability risk"
    chokepoints:
      - "Swiss refineries process majority of refined silver"
      - "London, New York, Shanghai primary trading hubs"
      - "COMEX futures dominant price discovery"
  
  use_cases:
    monetary:
      - "Store of value (like gold but higher beta)"
      - "Inflation/currency debasement hedge"
    industrial:
      - "Solar PV: 29% of industrial demand (2024), up from 11% (2014)"
      - "Electronics: highest electrical conductivity of any metal"
      - "EVs: 25-50g per vehicle (2-3x traditional cars)"
      - "AI data centers: massive electricity demand → solar → silver"
    jewelry:
      - "~20% of demand, price elastic"
  
  historical_patterns:
    - trigger: "Fed rate cut cycle begins"
      typical_response: "+30-50% over 12 months (higher beta than gold)"
      examples: ["2001-2002", "2008-2011", "2019-2020"]
      counter_examples: ["1994 - rate cuts but USD strength capped gains"]
    
    - trigger: "Geopolitical conflict escalation"
      typical_response: "+10-20% initial spike, follows gold"
      examples: ["Gulf War 1990", "Russia/Ukraine 2022"]
    
    - trigger: "Industrial demand surge"
      typical_response: "Sustained multi-year bull market"
      examples: ["2010-2011 solar boom", "2020-2025 green energy transition"]
  
  correlations:
    - asset: "Gold"
      relationship: "Positive (0.85+)"
      notes: "Silver typically 1.5-2x gold beta"
    
    - asset: "Gold/Silver Ratio"
      current_context: "Historical mean ~60, range 40-100"
      signal: "Above 80 = silver undervalued, mean reversion thesis"
    
    - asset: "USD (DXY)"
      relationship: "Inverse (-0.5)"
      notes: "Dollar weakness = silver tailwind"
    
    - asset: "Industrial metals (copper)"
      relationship: "Moderate positive (0.4-0.6)"
      notes: "Industrial demand correlation"
  
  key_actors:
    central_banks:
      - "Russia: Announced $535M silver acquisition plan (2025)"
      - "First major central bank to explicitly include silver"
    
    etf_flows:
      - "SLV (iShares): Largest silver ETF, flows signal sentiment"
      - "PSLV (Sprott): Physical-backed, often premium indicator"
    
    miners:
      - "First Majestic (AG): Pure-play silver miner"
      - "Pan American Silver (PAAS): Major producer"
      - "Note: Silver miners = leveraged silver bet"
    
    industrial:
      - "Solar panel manufacturers"
      - "EV battery/electronics supply chain"
```

### Macro Event Analysis Prompt

When an event is detected, Claude analyzes it with this structured prompt:

```typescript
const MACRO_EVENT_ANALYSIS_PROMPT = `You are a macro intelligence analyst helping identify kingmaker trades.

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
| **TOTAL** | 100% | [X] | |

If score >= 65, flag as ⚡ PRIORITY

### 3. METAL IMPACTS (If relevant)

**Gold:**
- Direction: [Bullish/Bearish/Neutral]
- Reasoning: [Why this event affects gold]
- Magnitude estimate: [If applicable]

**Silver:**
- Direction: [Bullish/Bearish/Neutral]
- Reasoning: [Why - note both monetary AND industrial angles]
- Magnitude estimate: [If applicable]

**Copper:**
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
`;
```

### Dashboard Components (Phase 1)

**1. Macro Radar (Primary Tab)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🌍 MACRO RADAR                                         Jan 2, 2026 AM  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ⚡ PRIORITY EVENTS (Score ≥ 65)                                        │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │ Score: 78 │ Fed signals accelerated rate cuts amid growth concerns  ││
│ │ Source: Reuters │ 4 hours ago │ [View Full Analysis]               ││
│ │                                                                     ││
│ │ Quick Take: Gold bullish, Silver higher beta play                  ││
│ │ Crypto Path: Moderate (risk-on sentiment, BTC correlation)         ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ 📊 MONITORING (Score 50-64)                                            │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │ Score: 58 │ China stimulus package announced                        ││
│ │ Score: 52 │ Copper inventories at multi-year lows                   ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ 📅 UPCOMING (Economic Calendar)                                        │
│ • Jan 3: US Non-Farm Payrolls (HIGH IMPACT)                            │
│ • Jan 5: FOMC Minutes Release                                          │
│ • Jan 8: CPI Data                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**2. Event Deep Dive (When you click an event)**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ EVENT: Fed signals accelerated rate cuts amid growth concerns          │
│ Source: Reuters │ 4 hours ago │ Score: 78/100 ⚡ PRIORITY             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─ RAW FACTS ─────────────────────────────────────────────────────────┐│
│ │ • Fed Chair indicated openness to 50bp cut in March                 ││
│ │ • GDP growth revised down to 1.8% for 2026                          ││
│ │ • Inflation at 2.3%, within target range                            ││
│ │ • Labor market showing signs of cooling                             ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ INTERPRETATION ────────────────────────────────────────────────────┐│
│ │                                                                     ││
│ │ METAL IMPACTS:                                                      ││
│ │ 🥇 Gold: BULLISH - Rate cuts → negative real rates → gold tailwind ││
│ │ 🥈 Silver: BULLISH (Higher Beta) - Follows gold + industrial demand││
│ │ 🥉 Copper: NEUTRAL/SLIGHT BEARISH - Growth concerns offset         ││
│ │                                                                     ││
│ │ HISTORICAL PRECEDENT:                                               ││
│ │ "2019 Fed Pivot" - Fed shifted from hiking to cutting. Gold +18%   ││
│ │ over next 12 months, Silver +25%. Pattern: initial rally,          ││
│ │ consolidation, then sustained move.                                 ││
│ │                                                                     ││
│ │ COUNTER-CASE:                                                       ││
│ │ • If USD strengthens despite cuts (safe haven), gold capped        ││
│ │ • If growth concerns deepen → risk-off → industrial metals down    ││
│ │ • 1994: Rate cuts + strong USD = gold flat                         ││
│ │                                                                     ││
│ │ CRYPTO TRANSMISSION:                                                ││
│ │ Path exists (MODERATE): Rate cuts → risk-on → BTC correlation      ││
│ │ Not a direct play; better as pure metals thesis                    ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ YOUR NOTES ────────────────────────────────────────────────────────┐│
│ │ [Add your thoughts here...]                                         ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ [Create Thesis from Event] [Dismiss] [Add to Watchlist]                │
└─────────────────────────────────────────────────────────────────────────┘
```

**3. Metals Intelligence View**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ⚗️ METALS INTELLIGENCE                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─ PRICES & RATIOS ───────────────────────────────────────────────────┐│
│ │ 🥇 Gold (GC=F)    $2,847.30   +0.8%   │ 52W: $2,100 - $2,920       ││
│ │ 🥈 Silver (SI=F)  $78.45      +1.2%   │ 52W: $24.00 - $82.00       ││
│ │ 🥉 Copper (HG=F)  $4.82       -0.3%   │ 52W: $3.80 - $5.10         ││
│ │                                                                     ││
│ │ Gold/Silver Ratio: 36.3 (Historical avg: 60)                       ││
│ │ Signal: Ratio LOW → Silver potentially overextended vs gold        ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ REGIME INDICATORS ─────────────────────────────────────────────────┐│
│ │ DXY (USD Index):     101.2  ↓ (Bearish for metals = bullish gold)  ││
│ │ Real Rates (10Y TIPS): -0.8%  (Negative = bullish gold)            ││
│ │ Fed Stance:          DOVISH (rate cuts expected)                   ││
│ │ VIX:                 15.3   (Low = risk-on environment)            ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ ACTIVE THESIS ─────────────────────────────────────────────────────┐│
│ │ "Silver: Safe-Haven + Industrial Convergence"                       ││
│ │ Created: Dec 15, 2025 │ Entry: $72.00 │ Current: $78.45 │ +8.9%    ││
│ │ Status: WATCHING │ [View Full Thesis]                              ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ [Gold Deep Dive] [Silver Deep Dive] [Copper Deep Dive]                 │
│ [Historical Cases] [Central Bank Monitor]                              │
└─────────────────────────────────────────────────────────────────────────┘
```

**4. Thesis Workspace**

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📝 THESIS: Silver: Safe-Haven + Industrial Convergence                 │
│ Status: WATCHING │ Created: Dec 15, 2025 │ Asset: Silver (SI=F, SLV)  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ TRIGGER EVENT                                                          │
│ Russia announced $535M silver acquisition plan + Fed pivot to cuts     │
│ + Solar/EV demand acceleration                                         │
│                                                                         │
│ CORE THESIS                                                            │
│ Silver is experiencing a rare convergence of monetary AND industrial   │
│ demand drivers simultaneously. Safe-haven buying (rate cuts, dollar    │
│ weakness, geopolitical uncertainty) combined with structural           │
│ industrial demand (solar PV now 29% of demand, EVs) creates            │
│ asymmetric upside. Fifth consecutive year of supply deficit.           │
│                                                                         │
│ ┌─ BULL CASE ──────────────────────────────────────────────────────────┐
│ │ • Fed cutting cycle → negative real rates → precious metals bid     │
│ │ • Russia central bank buying (first to explicitly include silver)   │
│ │ • Solar demand growing 15%+ annually, each panel needs silver       │
│ │ • EV adoption: 25-50g silver per vehicle vs 15g traditional         │
│ │ • Supply deficit: 117M oz projected shortfall in 2025              │
│ │ • Gold/silver ratio at 36 vs historical avg 60 (reversion?)        │
│ └──────────────────────────────────────────────────────────────────────┘
│                                                                         │
│ ┌─ BEAR CASE / COUNTER (MANDATORY) ────────────────────────────────────┐
│ │ • If USD strengthens (safe haven bid), caps silver upside           │
│ │ • Industrial recession would crush non-monetary demand              │
│ │ • Silver already up 150% YTD - how much is priced in?              │
│ │ • Low gold/silver ratio could mean silver overextended, not gold    │
│ │   undervalued                                                       │
│ │ • 2011 analog: Silver hit $50 then crashed 60% in months           │
│ └──────────────────────────────────────────────────────────────────────┘
│                                                                         │
│ KEY LEVELS                                                             │
│ • Entry consideration: $70-75 (pullback to support)                   │
│ • Target: $100 (round number, all-time high extension)                │
│ • Invalidation: Below $60 (breaks 2024 breakout level)                │
│                                                                         │
│ POSITION                                                               │
│ • Vehicle: SLV (ETF) or PSLV (physical-backed)                        │
│ • Size: [Not yet positioned]                                          │
│ • Entry: Waiting for pullback                                         │
│                                                                         │
│ ┌─ UPDATES LOG ────────────────────────────────────────────────────────┐
│ │ Jan 2: Silver +1.2% today. Fed language supportive. Thesis intact. │
│ │ Dec 28: Russia acquisition news. Added to bull case.               │
│ │ Dec 15: Thesis created after analyzing supply/demand dynamics.     │
│ └──────────────────────────────────────────────────────────────────────┘
│                                                                         │
│ [Add Update] [Export Markdown] [Close Thesis]                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**5. Telegram Bot Commands (Phase 1)**

```
/today     - Morning digest (priority events, metals snapshot, calendar)
/gold      - Gold price, key levels, regime indicators
/silver    - Silver price, gold/silver ratio, demand drivers
/copper    - Copper price, economic bellwether status
/events    - Recent high-significance events
/thesis    - List active theses with status
/note [thesis] [text] - Add note to a thesis
```

### Phase 1 Deliverables Checklist

**Week 1-2: Foundation**
- [ ] PostgreSQL database with full schema
- [ ] News ingestion pipeline (Reuters, AP RSS)
- [ ] Basic event classification

**Week 3-4: Intelligence Layer**
- [ ] Metals knowledge base loaded (gold, silver, copper)
- [ ] Historical case base (25-40 events)
- [ ] Claude integration for event analysis
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

---

## Phase 2: Crypto Layer + Transmission (Weeks 9-14)
**Goal: Add crypto-native radar, macro-to-crypto transmission, Telegram signal ingestion**
**Time: ~20-25 hours total**

Phase 2 adds the parallel crypto track that fills gaps when macro is quiet, plus the transmission layer that connects macro events to crypto opportunities.

### What You Get

1. **Crypto Radar (New Tab)**
   - Narrative detection from CryptoPanic + Telegram bots
   - Crowding score per narrative (0-100)
   - Lifecycle state tracking (Emerging → Early → Mainstream → Crowded → Distribution)
   - Rotation suggestions

2. **Macro-to-Crypto Transmission**
   - When macro event detected, check for crypto angles
   - "Banking crisis → BTC 'digital gold' narrative"
   - "Dollar weakness → stablecoin demand in emerging markets"
   - "Risk-on Fed pivot → altcoin correlation play"

3. **Telegram Signal Ingestion**
   - Forward signals from Hawk AI, From The Trenches to your bot
   - Auto-parsing and enrichment
   - Signal scoring and filtering
   - Integration into crypto radar

4. **Enhanced Thesis Workflow**
   - Full due diligence template for crypto
   - AI synthesis of notes
   - Bull/bear case generation
   - Export to Markdown/PDF

5. **Watchlist with Alerts**
   - Track both metals AND crypto opportunities
   - Price alerts via Telegram
   - Thesis update reminders

### Crypto-Native Signal Scoring

```typescript
interface CryptoSignalScore {
  total: number;          // 0-100
  components: {
    sourceQuality: number;      // Hawk AI vs random alpha group
    walletQuality: number;      // 30d PNL of wallets in signal
    narrativeAlignment: number; // Does this fit a known narrative?
    crowdingRisk: number;       // How late are we?
    macroAlignment: number;     // Does macro regime support risk-on?
  };
  lifecycle: 'emerging' | 'early' | 'mainstream' | 'crowded' | 'distribution';
  flags: string[];
}
```

### Narrative Crowding Score (0-100)

Indicates how "late" a crypto narrative is:

| Signal Category | Indicators |
|-----------------|------------|
| **Price Exhaustion** | % move from emergence, speed vs historical |
| **Social Reflexivity** | Volume peaked/flattening, engagement declining |
| **Quality Degradation** | Derivative content > original, retail dominance |
| **Dilution** | New token explosion, forks/clones |
| **Mainstream Validation** | CNBC/Bloomberg coverage = usually late |

### Crypto Radar Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🔮 CRYPTO RADAR                                      Jan 2, 2026 AM    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ⚡ MACRO TRANSMISSION (Derived from Macro Events)                       │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │ Fed Rate Cuts → BTC "Risk-On" Correlation Play                      ││
│ │ Transmission Strength: MODERATE │ Confidence: 65%                   ││
│ │ Note: BTC correlation to risk assets ~0.6 in cutting cycles        ││
│ │ [View Macro Event] [Create Thesis]                                  ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ 📊 NARRATIVE LIFECYCLE                                                 │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │ Narrative          │ Stage      │ Crowding │ Signal │               ││
│ │────────────────────│────────────│──────────│────────│───────────────││
│ │ AI Agents          │ MAINSTREAM │ 72/100   │ ⚠️ LATE│ Avoid new     ││
│ │ RWA Tokenization   │ EARLY      │ 34/100   │ 👀 Watch│ Building     ││
│ │ Bitcoin L2s        │ EMERGING   │ 18/100   │ ✅ Early│ Research     ││
│ │ DePIN              │ CROWDED    │ 85/100   │ 🚫 Exit │ Rotation out ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ 📥 SIGNAL INBOX (Telegram)                     Filter: Score >60       │
│ ┌─────────────────────────────────────────────────────────────────────┐│
│ │ Score │ Source      │ Token  │ MC      │ Narrative   │ Action      ││
│ │───────│─────────────│────────│─────────│─────────────│─────────────││
│ │ 78    │ Hawk AI     │ RUNE   │ $2.1M   │ Bitcoin L2  │ [Analyze]   ││
│ │ 65    │ Trenches    │ XYZ    │ $890k   │ AI Agent    │ [Analyze]   ││
│ │ 42    │ Manual      │ ABC    │ $50M    │ Unknown     │ [Dismiss]   ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Telegram Bot Commands (Phase 2 Additions)

```
# Existing from Phase 1
/today, /gold, /silver, /copper, /events, /thesis, /note

# New in Phase 2
/crypto         - Crypto radar summary (narratives + top signals)
/crowded        - List crowded narratives to avoid
/emerging       - List emerging narratives to watch
/signal [token] - Quick analysis of a token
/macro2crypto   - Current macro-to-crypto transmission paths
```

### Phase 2 Deliverables Checklist

**Week 9-10: Telegram Integration**
- [ ] Telegram bot receives forwarded signals
- [ ] Parsers for Hawk AI, From The Trenches formats
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

---

## Phase 3: Learning & Advanced (Weeks 15-24)
**Goal: Performance tracking, learning loops, counter-thesis engine, visualization**
**Time: ~25-30 hours total**

Phase 3 closes the feedback loop: track what worked, learn from what didn't, and proactively challenge your theses.

### What You Get

1. **Thesis Outcome Tracking**
   - Link thesis to actual trades/positions
   - "This thesis led to +X% / -Y%"
   - Pattern recognition on your own decisions
   - "You tend to exit too early on metals theses"

2. **Source Performance Tracking**
   - Per-source accuracy metrics (for crypto signals)
   - "Hawk AI signals: 62% win rate, 2.3R average"
   - Automatic tier adjustments

3. **Counter-Thesis Engine**
   - Proactive devil's advocate
   - "You've held this thesis for 30 days with no price movement. Here's what might be wrong."
   - Scheduled challenges on active theses

4. **Narrative Timeline Visualization**
   - Historical view of narratives and lifecycles
   - "Show me every commodity narrative since 2020"
   - Pattern spotting across cycles

5. **Advanced Historical Matching**
   - Semantic search across historical cases
   - "Find events similar to current Fed stance"
   - Auto-surface relevant precedents

6. **Adaptive Check-in Cadence**
   - Quiet periods → less frequent
   - High-activity → more touchpoints
   - Learns your engagement patterns

### Counter-Thesis Engine Prompt

```typescript
const COUNTER_THESIS_PROMPT = `You are a devil's advocate challenging an active investment thesis.

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
`;
```

### Performance Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📈 PERFORMANCE & LEARNING                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─ THESIS PERFORMANCE (All Time) ─────────────────────────────────────┐│
│ │ Total Theses: 12 │ Win: 7 (58%) │ Loss: 4 │ Open: 1                ││
│ │                                                                     ││
│ │ By Asset Type:                                                      ││
│ │ • Metals: 4 theses │ 75% win rate │ Avg +18% │ Avg hold: 45 days   ││
│ │ • Crypto (Macro-derived): 3 theses │ 67% win rate │ Avg +42%       ││
│ │ • Crypto (Native): 5 theses │ 40% win rate │ Avg -12%              ││
│ │                                                                     ││
│ │ Pattern: Your metals theses outperform crypto-native significantly ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ SOURCE PERFORMANCE (Crypto Signals) ───────────────────────────────┐│
│ │ Source          │ Signals │ Win Rate │ Avg R  │ Tier              ││
│ │─────────────────│─────────│──────────│────────│───────────────────││
│ │ Hawk AI         │ 23      │ 62%      │ 2.3R   │ ⭐ TIER 1         ││
│ │ From The Trenches│ 18     │ 44%      │ 1.1R   │ TIER 2            ││
│ │ Manual/Other    │ 8       │ 38%      │ 0.8R   │ TIER 3            ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ BEHAVIORAL PATTERNS ───────────────────────────────────────────────┐│
│ │ ⚠️ You tend to exit metals theses too early (avg 45 days vs        ││
│ │    optimal 90+ days based on historical precedent)                  ││
│ │ ⚠️ Your crypto-native win rate drops when crowding score >60       ││
│ │ ✅ Your macro-derived crypto trades outperform native signals      ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│ ┌─ ACTIVE THESIS CHALLENGES ──────────────────────────────────────────┐│
│ │ "Silver: Safe-Haven + Industrial" - Day 18                          ││
│ │ Status: HOLD │ Last challenge: 3 days ago                          ││
│ │ [View Challenge] [Respond]                                          ││
│ └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 3 Deliverables Checklist

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

---

### Quick Start: Week 1-2 Sprint

To get immediate value, here's your first two weeks action plan. Unlike reactive signal systems, this focuses on establishing the **macro intelligence foundation**.

**Days 1-3: Foundation (6 hours)**
1. Set up PostgreSQL database with core schema (events, theses, knowledge base)
2. Create Next.js app with basic routing
3. Set up Claude API integration

**Days 4-7: Metals Knowledge Base (8 hours)**
1. Load gold, silver, copper knowledge (from spec section 6.2)
2. Load 10-15 historical cases (start with major ones: 2008 GFC, 2020 COVID, 2022 Russia/Ukraine)
3. Build basic Metals Intelligence view

**Days 8-10: Event Detection (6 hours)**
1. Set up RSS ingestion (Reuters, AP)
2. Basic event extraction and classification
3. Connect to Claude for significance scoring

**Days 11-14: Daily Check-in (5 hours)**
1. Build Telegram bot with `/today` command
2. Daily digest generation
3. Basic thesis workspace

**By end of Week 2, you can:**
- Get a morning Telegram message summarizing macro events
- See significance scores that tell you what matters
- View metals prices with regime indicators
- Create theses for opportunities with bull/bear cases
- Access historical cases for pattern matching

This is the foundation that prevents another missed silver trade.

---

### Cost Projections

| Phase | Monthly Cost | What It Covers |
|-------|--------------|----------------|
| Phase 1 (Weeks 1-8) | ~$30-50 | Claude API for event analysis, thesis generation |
| Phase 2 (Weeks 9-14) | ~$40-60 | + Crypto signal analysis, narrative detection |
| Phase 3 (Weeks 15-24) | ~$50-70 | + Counter-thesis engine, pattern matching |

**Cost optimization tips:**
- Use Claude Haiku for simple classification tasks (event type, sentiment) at 1/10th the cost
- Cache AI responses for similar event patterns
- Batch events for daily synthesis rather than real-time analysis
- Use local Ollama for entity extraction and filtering

---

### Success Metrics

Track these to measure system effectiveness:

**Primary Success (6 Months):**
1. "I have a system instead of chaos"
2. "I caught 1-2 kingmaker macro plays I would have missed" (e.g., another silver)
3. "I caught 2-3 crypto plays I would have missed"
4. "Research feels lighter, not heavier"

**Process Metrics:**
- Events processed per week
- Priority events (≥65 score) identified
- Theses created vs. positions taken (selectivity ratio)
- Daily check-in streak (habit formation)

**Discipline Metrics:**
- % of positions with documented thesis
- % of theses with counter-case (should be 100%)
- % of exits that matched thesis (TP/SL hit vs. emotional)
- Average hold time vs. thesis expected duration

**Performance Metrics:**
- Win rate by asset type (metals vs. crypto-derived vs. crypto-native)
- Average return by thesis conviction level
- Source performance for crypto signals
- Behavioral pattern identification

**Learning Metrics:**
- Thesis updates per position
- Historical cases referenced
- Counter-thesis challenges responded to
- Pattern recognition improvement

---

### Failure Modes & Mitigations

| Failure Mode | Mitigation |
|--------------|------------|
| **False confidence** | Counter-cases mandatory, raw/interpretation separation |
| **Too many alerts** | Significance scoring, ⚡ PRIORITY only for ≥65 |
| **Ignored dashboard** | Daily Telegram check-in, habit formation |
| **Stale knowledge** | Regular knowledge base updates, clear versioning |
| **Missed events** | Multiple news sources, manual input fallback |
| **Echo chamber (again)** | Counter-thesis engine challenges active positions |

---

### What Meridian Solves

Looking back at the Complication section:

| Problem | Meridian Solution |
|---------|-------------------|
| Missed kingmaker trades (silver, gold) | Macro Intelligence Layer with significance scoring surfaces opportunities you'd otherwise miss |
| No systematic macro monitoring | Automated event detection from news wires, central bank communications, economic calendar |
| Fragmented information | Centralized dashboard with Macro Radar + Crypto Radar + Thesis Workspace |
| Couldn't connect dots | Pre-built metals knowledge + historical pattern matching + AI synthesis |
| Overwhelming noise | Significance scoring filters noise; only ≥65 gets ⚡ PRIORITY |
| No memory | Historical case base, thesis tracking, outcome learning |
| No exit discipline | Thesis workspace with mandatory counter-cases and invalidation criteria |
| Echo chamber thinking | Counter-thesis engine proactively challenges your positions |
| Confidence erosion | Performance tracking shows what actually works for YOU |

---

### The Meridian Difference

Most "crypto tools" start with signal bots and on-chain data. Meridian inverts the hierarchy:

```
TRADITIONAL CRYPTO TOOLS          MERIDIAN
─────────────────────────         ────────
Telegram signals                  Macro events
    ↓                                 ↓
On-chain data                     Metals intelligence
    ↓                                 ↓
Price action                      Historical precedent
    ↓                                 ↓
Maybe some macro                  Transmission layer
    ↓                                 ↓
Reactive trades                   Crypto (if path exists)
                                      ↓
                                  Crypto-native (gap-filling)
                                      ↓
                                  Kingmaker theses
```

The goal isn't to trade more. It's to **trade fewer, higher-conviction positions with deep research behind them**.

A few kingmaker trades per year in metals and crypto, with systematic thesis-building, historical grounding, and proactive counter-challenges.

That's what would have caught silver. That's what Meridian is designed to do.

---

### Future Enhancements (When Budget Allows)

**$100-200/month tier:**
- Dedicated VPS with local LLM for classification
- More aggressive event monitoring (near real-time)
- On-chain data for crypto layer (Nansen-lite)

**$300-500/month tier:**
- Nansen integration for smart money tracking
- Full historical data for backtesting theses
- Multi-exchange price feeds

**$1000+/month tier:**
- Custom fine-tuned model on your thesis history
- Real-time alerting infrastructure
- Advanced visualization and analytics

---

## Appendix: Key Trade History Reference

| Trade | Period | Entry Thesis | Result | Key Lesson |
|-------|--------|--------------|--------|------------|
| Terra Luna | 2021-May 2022 | Algorithmic stablecoin adoption drives burn mechanism | -80% net worth | No invalidation thesis, ignored macro, leverage killed |
| Soulgraph | Oct 2024-Q2 2025 | AI + crypto convergence, Y Combinator hints, strong community | $20k → $200k → $5k | No exit plan, held through narrative cooldown |
| NOMAI | Late 2024-2025 | Alphanomics data layer + AI agent, strong team | $110k → $5k | Didn't account for ecosystem dependency (Virtuals) |
| Gold/Silver | 2024-2025 | (Missed) | N/A | Saw inputs but couldn't synthesize thesis; silver required connecting safe-haven + industrial + supply dynamics |
