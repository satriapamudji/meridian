# Task 25 — Metals Intelligence Dashboard UI

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-10.md` (price ingestion), `task-05.md` (metals KB)  
**Spec references:** `spec.md` section 6, 8.1.2, 11.1 Tab 3

## Objective

Replace the placeholder `/metals` page with a full Metals Intelligence Dashboard showing current prices, ratios, knowledge base insights, and recent relevant events for Gold, Silver, and Copper.

## Background

The Metals Intelligence Module (spec §6) is a core differentiator for Meridian. The pre-built knowledge base exists in the database (`metals_knowledge` table with 15 entries), and price data is being ingested (`daily_prices` table). This task surfaces that data in a trader-friendly UI.

## Deliverables

### Backend API Enhancements

1. **`GET /metals`** - Metals overview endpoint
   - Returns latest prices for GC=F, SI=F, HG=F
   - Returns current gold/silver ratio with historical context (mean ~60, range 40-100)
   - Returns 24h/7d price changes

2. **`GET /metals/{metal}`** - Single metal detail endpoint
   - `metal` = `gold`, `silver`, or `copper`
   - Returns:
     - Current price + key levels (from `daily_prices`)
     - Knowledge base entries for that metal (from `metals_knowledge`)
     - Recent macro_events that mention this metal in `metal_impacts`

### Frontend Pages

1. **`/metals` Overview Page**
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │ Metals Intelligence                                         │
   ├─────────────────────────────────────────────────────────────┤
   │                                                             │
   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
   │  │ GOLD        │ │ SILVER      │ │ COPPER      │           │
   │  │ $2,048.50   │ │ $24.12      │ │ $3.82       │           │
   │  │ +0.5% 24h   │ │ +0.8% 24h   │ │ -0.2% 24h   │           │
   │  │ [View →]    │ │ [View →]    │ │ [View →]    │           │
   │  └─────────────┘ └─────────────┘ └─────────────┘           │
   │                                                             │
   │  Gold/Silver Ratio: 84.9                                   │
   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                        │
   │  Historical mean: ~60 | Range: 40-100                      │
   │  Signal: Above 80 = silver potentially undervalued         │
   │                                                             │
   └─────────────────────────────────────────────────────────────┘
   ```

2. **`/metals/[metal]` Detail Page** (e.g., `/metals/gold`)
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │ ← Back to Metals                                            │
   │ GOLD (GC=F)                               $2,048.50 +0.5%  │
   ├─────────────────────────────────────────────────────────────┤
   │                                                             │
   │ SUPPLY CHAIN                                                │
   │ ━━━━━━━━━━━━━━━━━━━━━                                      │
   │ Top Producers: China (11%), Australia (10%), Russia (9%)   │
   │ Top Consumers: Jewelry (50%), Investment (25%), CB (15%)   │
   │ Chokepoints: Swiss refineries process 70% of world's gold  │
   │                                                             │
   │ USE CASES                                                   │
   │ ━━━━━━━━━━━━━━━━━━━━━                                      │
   │ • Store of value during uncertainty                        │
   │ • Inflation hedge (historically)                           │
   │ • Portfolio diversification                                │
   │                                                             │
   │ KEY CORRELATIONS                                            │
   │ ━━━━━━━━━━━━━━━━━━━━━                                      │
   │ • USD (DXY): Inverse (-0.4 to -0.6)                       │
   │ • Real rates (10Y TIPS): Inverse (-0.7 to -0.9)           │
   │ • Silver: Positive (0.8+)                                  │
   │                                                             │
   │ RECENT RELEVANT EVENTS                                      │
   │ ━━━━━━━━━━━━━━━━━━━━━                                      │
   │ • [Event 1] - bullish - Fed signals rate cuts...           │
   │ • [Event 2] - neutral - China gold reserves unchanged...   │
   │                                                             │
   └─────────────────────────────────────────────────────────────┘
   ```

## Acceptance Criteria

- [ ] `/metals` page shows current prices for all 3 metals
- [ ] Gold/Silver ratio displayed with historical context
- [ ] Each metal card links to detail page
- [ ] Detail page shows knowledge base content by category
- [ ] Detail page shows recent events with metal impact
- [ ] Page renders within 1 second (uses SSR with caching)
- [ ] Mobile responsive

## Technical Notes

### Data Sources

- `daily_prices` table: Latest prices for GC=F, SI=F, HG=F
- `metals_knowledge` table: Knowledge base by metal + category
- `macro_events` table: Events with non-null `metal_impacts` JSONB

### Knowledge Base Categories

From `metals_knowledge.category`:
- `supply_chain`
- `use_cases`
- `patterns`
- `correlations`
- `actors`

### API Response Shapes

```typescript
// GET /metals
interface MetalsOverview {
  metals: {
    gold: { symbol: string; price: number; change_24h: number; change_7d: number };
    silver: { symbol: string; price: number; change_24h: number; change_7d: number };
    copper: { symbol: string; price: number; change_24h: number; change_7d: number };
  };
  gold_silver_ratio: {
    current: number;
    historical_mean: number;
    range_low: number;
    range_high: number;
    signal: string;
  };
  last_updated: string;
}

// GET /metals/{metal}
interface MetalDetail {
  metal: string;
  symbol: string;
  price: number;
  change_24h: number;
  change_7d: number;
  knowledge: {
    supply_chain: object;
    use_cases: object;
    patterns: object;
    correlations: object;
    actors: object;
  };
  recent_events: Array<{
    id: string;
    headline: string;
    published_at: string;
    impact: { direction: string; magnitude: string; driver: string };
  }>;
}
```

## Out of Scope

- Charts/graphs (Phase 2)
- Real-time price updates (daily is sufficient)
- Price alerts

## Estimated Effort

- Backend API: 2-3 hours
- Frontend UI: 4-6 hours
- Total: ~1 day
