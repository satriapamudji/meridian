# Task 26 — Calendar Tab UI

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-09.md` (economic calendar ingestion)  
**Spec references:** `spec.md` section 5.3, 8.1.5, 11.1 Tab 4

## Objective

Create a `/calendar` page showing upcoming economic events and central bank meetings with significance highlighting, enabling the trader to prepare for market-moving releases.

## Background

Economic calendar data is already being ingested into the `economic_events` table. Central bank meeting dates should be highlighted. The trader needs a forward-looking view to prepare theses around known catalyst dates.

## Deliverables

### Backend API

1. **`GET /calendar`** - Calendar events endpoint
   - Query params:
     - `days` (default: 14) - How many days forward to show
     - `impact` (optional) - Filter by impact level: `high`, `medium`, `low`
   - Returns upcoming economic events sorted by date
   - Includes central bank meeting dates with special flag

2. **`GET /calendar/today`** - Today's events only
   - Used by daily digest and quick glance

### Frontend Page

**`/calendar` Page**
```
┌─────────────────────────────────────────────────────────────┐
│ Economic Calendar                          [Next 14 days ▼] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ TODAY - Monday, Jan 6, 2026                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│ 🔴 10:00 ET  ISM Manufacturing PMI (US)          HIGH      │
│              Expected: 48.5 | Previous: 47.8               │
│                                                             │
│ 🔴 14:00 ET  FOMC Minutes                        HIGH      │
│              Fed December meeting minutes                   │
│                                                             │
│ TOMORROW - Tuesday, Jan 7, 2026                            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│ 🟡 08:30 ET  Trade Balance (US)                  MEDIUM    │
│              Expected: -$78.2B | Previous: -$73.8B         │
│                                                             │
│ WEDNESDAY, Jan 8, 2026                                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│ 🔴 08:30 ET  ADP Employment Change               HIGH      │
│                                                             │
│ ⭐ THURSDAY, Jan 9, 2026 — FOMC MEETING                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│ Central bank meeting - expect volatility                   │
│                                                             │
│ FRIDAY, Jan 10, 2026                                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│ 🔴 08:30 ET  Non-Farm Payrolls                   HIGH      │
│              Expected: 180K | Previous: 199K               │
│ 🔴 08:30 ET  Unemployment Rate                   HIGH      │
│              Expected: 4.2% | Previous: 4.2%               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar Navigation Update

Add Calendar to sidebar navigation:
```typescript
{
  name: "Calendar",
  href: "/calendar",
  icon: Calendar, // from lucide-react
}
```

## Acceptance Criteria

- [ ] `/calendar` page displays upcoming economic events
- [ ] Events grouped by day with clear date headers
- [ ] Impact level shown with color coding (🔴 HIGH, 🟡 MEDIUM, 🟢 LOW)
- [ ] Expected/Previous/Actual values displayed where available
- [ ] Central bank meetings highlighted with special styling
- [ ] Filter dropdown for time range (7/14/30 days)
- [ ] Filter for impact level (All/High only)
- [ ] Sidebar updated with Calendar nav item
- [ ] Mobile responsive

## Technical Notes

### Data Source

`economic_events` table schema:
```sql
- id UUID
- event_name TEXT
- event_date TIMESTAMPTZ
- region TEXT
- impact_level TEXT ('high', 'medium', 'low')
- expected_value TEXT
- actual_value TEXT
- previous_value TEXT
- surprise_direction TEXT
- surprise_magnitude NUMERIC
- historical_metal_impact JSONB
```

### Central Bank Meetings

Detect central bank meetings by:
- `event_name` containing: FOMC, ECB, BOJ, BOE, RBA
- Or `region` + `event_name` pattern matching

### API Response Shape

```typescript
// GET /calendar
interface CalendarResponse {
  events: Array<{
    id: string;
    event_name: string;
    event_date: string;
    region: string;
    impact_level: 'high' | 'medium' | 'low';
    expected_value: string | null;
    actual_value: string | null;
    previous_value: string | null;
    is_central_bank: boolean;
    historical_metal_impact: object | null;
  }>;
  date_range: {
    start: string;
    end: string;
  };
}
```

## Out of Scope

- Surprise detection display (shows after release)
- Historical impact charts
- Push notifications for events

## Estimated Effort

- Backend API: 1-2 hours
- Frontend UI: 3-4 hours
- Sidebar update: 30 min
- Total: ~0.5 day
