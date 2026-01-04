# Task 27 — Historical Cases Browser UI

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-06.md` (historical cases seed)  
**Spec references:** `spec.md` section 10.1, 11.1 Tab 6

## Objective

Create a `/history` page that allows the trader to browse the historical case base, search by event type or metal, and compare current events to historical precedents.

## Background

The historical case base (spec §10.1) contains curated macro events like 2008 GFC, 2020 COVID, 2022 Russia/Ukraine. These are used for pattern matching during event analysis. The trader should be able to browse these directly to build intuition and verify the system's historical matching.

Currently:
- 3 cases are seeded in `historical_cases` table
- `/cases/[caseId]` detail page exists but no list/browse view
- Event analysis references cases but trader can't explore them directly

## Deliverables

### Backend API

1. **`GET /cases`** - List all historical cases
   - Query params:
     - `event_type` (optional) - Filter by type
     - `metal` (optional) - Filter by metal impact (gold/silver/copper)
     - `year_from` / `year_to` (optional) - Date range filter
   - Returns summary list of cases

2. **`GET /cases/{case_id}`** - Already exists, verify it returns full detail

### Frontend Pages

1. **`/history` Page** (List View)
```
┌─────────────────────────────────────────────────────────────┐
│ Historical Case Base                                        │
│ Learn from past macro events to recognize patterns          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Filters: [Event Type ▼] [Metal Impact ▼] [Year Range ▼]   │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🔴 2022 Russia/Ukraine Invasion                    85   ││
│ │ Type: geopolitical_conflict | Feb 2022 - ongoing        ││
│ │ Gold: +15% | Silver: +12% | Copper: volatile            ││
│ │ Key lesson: War ≠ automatic BTC pump                    ││
│ │                                            [View Case →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🔴 2020 COVID Crash & Recovery                     90   ││
│ │ Type: financial_crisis | Mar 2020 - Dec 2021           ││
│ │ Gold: +30% | Silver: +50% | Copper: +60%               ││
│ │ Key lesson: Liquidity injection = all assets up        ││
│ │                                            [View Case →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🔴 2008 Global Financial Crisis                    95   ││
│ │ Type: financial_crisis | Sep 2008 - Mar 2009           ││
│ │ Gold: +25% | Silver: +20% | Copper: -50%               ││
│ │ Key lesson: Initial selloff, then safe haven bid       ││
│ │                                            [View Case →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ [3 cases total]                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

2. **`/cases/[caseId]` Page** (Detail View - enhance existing)
```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to History                                           │
│ 2022 Russia/Ukraine Invasion                         85/100│
├─────────────────────────────────────────────────────────────┤
│ Event Type: geopolitical_conflict                          │
│ Date Range: Feb 2022 - ongoing                             │
│                                                             │
│ STRUCTURAL DRIVERS                                          │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ • Energy supply shock (Russia = major oil/gas)             │
│ • Sanctions regime (financial system stress)               │
│ • Inflation acceleration                                    │
│ • Safe haven demand spike                                   │
│                                                             │
│ METAL IMPACTS                                               │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ ┌──────────┬───────────┬──────────────┬──────────────────┐ │
│ │ Metal    │ Direction │ Magnitude    │ Driver           │ │
│ ├──────────┼───────────┼──────────────┼──────────────────┤ │
│ │ Gold     │ UP        │ +15% (6mo)   │ Safe haven       │ │
│ │ Silver   │ UP        │ +12% (6mo)   │ Following gold   │ │
│ │ Copper   │ VOLATILE  │ +5% then -10%│ Demand concerns  │ │
│ └──────────┴───────────┴──────────────┴──────────────────┘ │
│                                                             │
│ TRADITIONAL MARKET REACTION                                 │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ • Oil +60% in 3 months                                     │
│ • EUR/USD -12%                                             │
│ • European equities -15%                                    │
│                                                             │
│ CRYPTO REACTION                                             │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ • BTC -15% initial (risk-off)                              │
│ • Stablecoin demand spike in Russia/Ukraine                │
│ • No sustained safe haven bid for BTC                      │
│                                                             │
│ CRYPTO TRANSMISSION                                         │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ Exists: Yes | Strength: Weak                               │
│ Path: Capital controls → stablecoin demand (but not BTC)   │
│                                                             │
│ TIME DELAYS                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ • Gold: Immediate spike, sustained over months             │
│ • Commodity inflation: 3-6 month feed-through              │
│                                                             │
│ KEY LESSONS                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ • War ≠ automatic BTC pump                                 │
│ • Traditional safe havens (gold) outperformed              │
│ • Stablecoin > BTC for capital flight                      │
│                                                             │
│ COUNTER-EXAMPLES                                            │
│ ━━━━━━━━━━━━━━━━━━━━━                                      │
│ • Unlike smaller conflicts, this had direct energy impact  │
│ • Sanctions made this more impactful than typical war      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar Navigation Update

Add History to sidebar navigation:
```typescript
{
  name: "History",
  href: "/history",
  icon: BookOpen, // from lucide-react
}
```

## Acceptance Criteria

- [ ] `/history` page lists all historical cases
- [ ] Each case shows: name, type, date range, metal impacts summary, key lesson
- [ ] Significance score badge displayed
- [ ] Filters work for event_type and metal impact
- [ ] Case detail page shows full structured data
- [ ] Link from event detail "Historical Precedent" to relevant case works
- [ ] Sidebar updated with History nav item
- [ ] Mobile responsive

## Technical Notes

### Data Source

`historical_cases` table schema:
```sql
- id UUID
- event_name TEXT
- date_range TEXT
- event_type TEXT
- significance_score INTEGER
- structural_drivers TEXT[]
- metal_impacts JSONB
- traditional_market_reaction TEXT[]
- crypto_reaction TEXT[]
- crypto_transmission JSONB
- time_delays TEXT[]
- lessons TEXT[]
- counter_examples TEXT[]
- embedding vector(1536)
```

### API Response Shape

```typescript
// GET /cases
interface CasesListResponse {
  cases: Array<{
    id: string;
    event_name: string;
    date_range: string;
    event_type: string;
    significance_score: number;
    metal_impacts: {
      gold?: { direction: string; magnitude: string };
      silver?: { direction: string; magnitude: string };
      copper?: { direction: string; magnitude: string };
    };
    key_lesson: string; // First item from lessons[]
  }>;
  total: number;
}

// GET /cases/{id} - full detail
interface CaseDetailResponse {
  // All fields from historical_cases table
}
```

## Out of Scope

- Adding new cases via UI (use seed scripts)
- Similarity search from this page (happens during event analysis)
- Case comparison view (side-by-side)

## Estimated Effort

- Backend API: 1-2 hours
- Frontend list page: 2-3 hours
- Frontend detail page enhancement: 2 hours
- Total: ~0.5-1 day
