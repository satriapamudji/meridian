# Task 29 — Central Bank Monitor UI

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-08.md` (central bank ingestion)  
**Spec references:** `spec.md` section 5.2, 8.1.4

## Objective

Create a Central Bank Monitor section or page that displays central bank communications, next meeting countdowns, and hawkish/dovish sentiment trends.

## Background

Central bank policy is a primary driver of metals prices (spec §5.2). The Fed ingestion pipeline exists and stores data in `central_bank_comms` table. The trader needs visibility into:
- Recent communications and their sentiment
- Upcoming meetings
- Trend in hawkish/dovish stance

## Deliverables

### Backend API

1. **`GET /central-banks`** - Central bank overview
   - Returns list of tracked banks (Fed, ECB, BOJ, BOE)
   - For each: next meeting date, days until, current sentiment trend

2. **`GET /central-banks/{bank}/communications`** - Recent communications
   - `bank` = `fed`, `ecb`, `boj`, `boe`
   - Returns last N communications with sentiment analysis

### Frontend

**Option A: Dedicated `/central-banks` Page**
```
┌─────────────────────────────────────────────────────────────┐
│ Central Bank Monitor                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🇺🇸 FEDERAL RESERVE                                      ││
│ │ Next Meeting: Jan 29, 2026 (23 days)                   ││
│ │ Current Stance: HAWKISH (0.6)                          ││
│ │ Trend: Slightly less hawkish vs. December             ││
│ │                                                        ││
│ │ Recent Communications:                                 ││
│ │ • Jan 3 - Powell Speech (hawkish, 0.7)               ││
│ │   "Inflation remains above target..."                 ││
│ │ • Dec 13 - FOMC Statement (neutral, 0.1)             ││
│ │   "Committee decided to maintain..."                  ││
│ │                                            [View All →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🇪🇺 EUROPEAN CENTRAL BANK                               ││
│ │ Next Meeting: Jan 25, 2026 (19 days)                   ││
│ │ Current Stance: DOVISH (-0.3)                          ││
│ │ Trend: Increasingly dovish                             ││
│ │                                            [View All →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🇯🇵 BANK OF JAPAN                                        ││
│ │ Next Meeting: Jan 24, 2026 (18 days)                   ││
│ │ Current Stance: DOVISH (-0.7)                          ││
│ │ Trend: Historic shift — hints at policy change         ││
│ │                                            [View All →]││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Option B: Integrate into Calendar or Metals page**

Could add a "Central Banks" section to the Calendar page since meetings are calendar events.

### Sidebar Navigation Update

If standalone page:
```typescript
{
  name: "Central Banks",
  href: "/central-banks",
  icon: Landmark, // from lucide-react
}
```

## Acceptance Criteria

- [ ] Display tracked central banks with next meeting dates
- [ ] Show days until next meeting as countdown
- [ ] Display current sentiment score and label (hawkish/neutral/dovish)
- [ ] Show sentiment trend vs. previous communications
- [ ] List recent communications with sentiment scores
- [ ] Link to view full communication text
- [ ] Mobile responsive

## Technical Notes

### Data Source

`central_bank_comms` table schema:
```sql
- id UUID
- bank TEXT ('fed', 'ecb', 'boj', 'boe')
- comm_type TEXT ('statement', 'minutes', 'speech', 'press_conference')
- published_at TIMESTAMPTZ
- full_text TEXT
- key_phrases TEXT[]
- sentiment TEXT ('hawkish', 'dovish', 'neutral')
- sentiment_score NUMERIC (-1 to +1)
- change_vs_previous TEXT
- forward_guidance TEXT
```

### Sentiment Display

| Score Range | Label | Color |
|-------------|-------|-------|
| 0.3 to 1.0 | Hawkish | Red/Orange |
| -0.3 to 0.3 | Neutral | Gray |
| -1.0 to -0.3 | Dovish | Green/Blue |

### API Response Shape

```typescript
// GET /central-banks
interface CentralBanksOverview {
  banks: Array<{
    code: 'fed' | 'ecb' | 'boj' | 'boe';
    name: string;
    flag: string; // emoji
    next_meeting: string | null;
    days_until_meeting: number | null;
    current_sentiment: 'hawkish' | 'neutral' | 'dovish';
    sentiment_score: number;
    trend: string;
    recent_comms: Array<{
      id: string;
      comm_type: string;
      published_at: string;
      sentiment: string;
      sentiment_score: number;
      summary: string; // First 100 chars of full_text
    }>;
  }>;
}
```

## Dependencies

- Need to seed meeting dates for 2026 (or pull from calendar)
- May need to enhance Fed ingestion to calculate trend

## Out of Scope

- Real-time speech monitoring
- Diff view between communications
- Sentiment charts over time

## Estimated Effort

- Backend API: 2-3 hours
- Frontend UI: 3-4 hours
- Total: ~1 day
