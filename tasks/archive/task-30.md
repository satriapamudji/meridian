# Task 30 — Event-to-Thesis Linking + User Notes

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-20.md` (event detail UI), `task-21.md` (thesis workspace)  
**Spec references:** `spec.md` section 11.2

## Objective

Add the ability to create a thesis directly from an event, and add user notes to events. This completes the event card UX specified in §11.2.

## Background

The spec §11.2 shows the event card should have:
```
📝 YOUR NOTES
[Click to add notes...]

[Create Thesis] [Add to Watchlist] [Dismiss]
```

Currently:
- Event detail page has no "Create Thesis" button
- No user notes field on events
- No dismiss/watchlist functionality

This task adds the workflow to convert a macro event into an active thesis.

## Deliverables

### Backend Changes

1. **Add `user_notes` column to `macro_events` table**
   ```sql
   ALTER TABLE macro_events ADD COLUMN user_notes TEXT;
   ```

2. **`PATCH /events/{id}/notes`** - Update user notes
   ```json
   { "notes": "My thoughts on this event..." }
   ```

3. **`POST /events/{id}/create-thesis`** - Create thesis from event
   - Seeds thesis with:
     - `title`: Generated from headline
     - `trigger_event`: Event headline + link
     - `historical_precedent`: From event analysis
     - `asset_type`: Primary metal from metal_impacts
   - Returns created thesis ID
   - Updates event status to `thesis_created`

### Frontend Changes

1. **Event Detail Page (`/macro-radar/[eventId]`)**

   Add action buttons section:
   ```
   ┌─────────────────────────────────────────────────────────────┐
   │ 📝 YOUR NOTES                                               │
   │ ┌─────────────────────────────────────────────────────────┐│
   │ │ [Click to add notes...]                                 ││
   │ └─────────────────────────────────────────────────────────┘│
   │                                                             │
   │ [Create Thesis] [Add to Watchlist] [Dismiss]               │
   └─────────────────────────────────────────────────────────────┘
   ```

2. **Notes Editor**
   - Click to expand textarea
   - Auto-save on blur or after 2 seconds idle
   - Show "Saved" indicator

3. **Create Thesis Button**
   - Only shown for priority events (significance ≥ 65)
   - Opens modal or redirects to thesis workspace with pre-filled data
   - Shows confirmation: "Thesis created: [title]"

4. **Watchlist Button** (optional - can defer)
   - Adds event to a "watching" list
   - Shown in sidebar or separate view

5. **Dismiss Button**
   - Sets event status to `dismissed`
   - Removes from active Macro Radar view
   - Can be undone

### Event Status Flow

```
new → analyzed → thesis_created
         ↓
     dismissed
```

## Acceptance Criteria

- [ ] User can add/edit notes on any event
- [ ] Notes persist and show on event detail page
- [ ] "Create Thesis" button visible for priority events
- [ ] Clicking "Create Thesis" creates thesis with pre-filled data
- [ ] User redirected to thesis workspace after creation
- [ ] Event status updated to `thesis_created`
- [ ] "Dismiss" button hides event from main radar view
- [ ] Dismissed events can be viewed via filter
- [ ] Mobile responsive

## Technical Notes

### Create Thesis Logic

```python
def create_thesis_from_event(event_id: str) -> Thesis:
    event = get_event(event_id)
    
    # Determine primary metal from impacts
    metal_impacts = event.metal_impacts or {}
    primary_metal = None
    for metal in ['gold', 'silver', 'copper']:
        if metal in metal_impacts:
            impact = metal_impacts[metal]
            if impact.get('direction') in ['bullish', 'up']:
                primary_metal = metal
                break
    
    thesis = Thesis(
        title=f"{primary_metal.title() if primary_metal else 'Macro'}: {event.headline[:50]}...",
        asset_type=primary_metal or 'macro',
        trigger_event=f"[{event.headline}](/macro-radar/{event.id})",
        core_thesis="",  # User fills this in
        historical_precedent=event.historical_precedent,
        status='watching',
    )
    
    # Link event to thesis
    event.thesis_id = thesis.id
    event.status = 'thesis_created'
    
    return thesis
```

### UI Component: NotesEditor

```typescript
function NotesEditor({ eventId, initialNotes }: Props) {
  const [notes, setNotes] = useState(initialNotes || '');
  const [saving, setSaving] = useState(false);
  
  const saveNotes = async () => {
    setSaving(true);
    await fetch(`/api/events/${eventId}/notes`, {
      method: 'PATCH',
      body: JSON.stringify({ notes }),
    });
    setSaving(false);
  };
  
  return (
    <div>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        onBlur={saveNotes}
        placeholder="Add your notes about this event..."
      />
      {saving && <span>Saving...</span>}
    </div>
  );
}
```

## Migration

```sql
-- Add user_notes column
ALTER TABLE macro_events ADD COLUMN IF NOT EXISTS user_notes TEXT;

-- Add index for thesis_id lookup
CREATE INDEX IF NOT EXISTS idx_macro_events_thesis_id ON macro_events(thesis_id);
```

## Out of Scope

- Watchlist as a separate feature (can be status-based for now)
- Bulk dismiss
- Note history/versioning

## Estimated Effort

- Backend migration + API: 2 hours
- Frontend notes editor: 2 hours
- Create thesis flow: 3 hours
- Dismiss functionality: 1 hour
- Total: ~1 day
