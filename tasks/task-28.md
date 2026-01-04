# Task 28 — Daily Digest Dashboard Page

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-17.md` (digest API)  
**Spec references:** `spec.md` section 8.1.8, 11.3, 11.4

## Objective

Create a `/digest` page that displays the daily briefing content, giving the trader a single view of what matters today. This is the "morning check-in" view that the Telegram bot will also send.

## Background

The daily digest is a core part of the Meridian workflow (spec §8.1.8). The API endpoint `GET /digest/today` already exists and returns:
- Priority events (significance ≥ 65)
- Metals snapshot (prices + changes)
- Economic calendar for today
- Active thesis updates

This task creates the frontend page to consume that API.

## Deliverables

### Frontend Page

**`/digest` Page** (or `/digest/today`)
```
┌─────────────────────────────────────────────────────────────┐
│ ☀️ MERIDIAN DAILY BRIEFING                                  │
│ Monday, January 6, 2026                              [Refresh]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ⚡ PRIORITY EVENTS (2)                                      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ Fed signals potential March rate cut          78/100   ││
│ │ Reuters • 6 hours ago                                  ││
│ │ Gold +1.2% | Analysis ready              [View Event →]││
│ └─────────────────────────────────────────────────────────┘│
│ ┌─────────────────────────────────────────────────────────┐│
│ │ China manufacturing PMI beats estimates       68/100   ││
│ │ AP • 8 hours ago                                       ││
│ │ Copper +0.8%                                 [View Event →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ 📊 METALS STATUS                                            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ┌─────────────┬─────────────┬─────────────┐               │
│ │ GOLD        │ SILVER      │ COPPER      │               │
│ │ $2,048.50   │ $24.12      │ $3.82       │               │
│ │ +0.5% ▲     │ +0.8% ▲     │ -0.2% ▼     │               │
│ └─────────────┴─────────────┴─────────────┘               │
│ G/S Ratio: 84.9 (elevated — above 80)                     │
│                                                             │
│ 📅 TODAY'S CALENDAR                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ 🔴 10:00 ET — ISM Manufacturing PMI (US)                   │
│ 🔴 14:00 ET — FOMC Minutes                                 │
│                                                             │
│ 📋 THESIS UPDATES                                           │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ Silver mean reversion                         ACTIVE   ││
│ │ Day 12 | Silver: $24.12 (+3.2% since entry)           ││
│ │                                            [View Thesis →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ 💡 No urgent action required. Continue monitoring.         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar Navigation Update

Add Digest to sidebar as first item (it's the home base):
```typescript
{
  name: "Daily Digest",
  href: "/digest",
  icon: Newspaper, // from lucide-react
}
```

### Optional: Make `/` redirect to `/digest`

Update home page to redirect to daily digest, or show digest content directly on home.

## Acceptance Criteria

- [ ] `/digest` page displays full daily briefing
- [ ] Priority events section with links to event detail
- [ ] Metals snapshot with prices and changes
- [ ] Gold/Silver ratio with context
- [ ] Today's calendar events (high impact only)
- [ ] Active thesis updates with progress
- [ ] Refresh button to reload data
- [ ] Shows "Nothing urgent" message when no priority events
- [ ] Sidebar updated with Daily Digest nav item
- [ ] Mobile responsive

## Technical Notes

### Data Source

`GET /digest/today` API response (already exists):
```json
{
  "digest_date": "2026-01-06",
  "priority_events": [...],
  "metals_snapshot": {
    "gold": { "price": 2048.50, "change_pct": 0.5 },
    "silver": { "price": 24.12, "change_pct": 0.8 },
    "copper": { "price": 3.82, "change_pct": -0.2 },
    "gold_silver_ratio": 84.9
  },
  "economic_calendar": [...],
  "active_theses": [...],
  "full_digest": "markdown string"
}
```

### Status Messages

Based on priority_events count:
- 0 events: "✅ Nothing urgent today. Monitoring mode."
- 1-2 events: "⚡ {n} priority event(s) require attention."
- 3+ events: "🔥 High activity day. {n} priority events detected."

## Out of Scope

- Telegram message formatting (task-22)
- Historical digest archive
- Custom digest time configuration

## Estimated Effort

- Frontend UI: 3-4 hours
- Sidebar update: 30 min
- Total: ~0.5 day
