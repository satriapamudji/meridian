
# Task 24 — Frontend Modernization (Tailwind + Shadcn)

**Epic:** Technical Debt / UI Overhaul
**Phase:** 1 (Foundation)
**Depends on:** N/A
**Spec references:** N/A

## Objective

Replace the fragile custom CSS implementation with a robust, scalable design system using Tailwind CSS and Shadcn/UI (Headless UI). This enables the construction of complex dashboards (like the Thesis Workspace) with standard, accessible components.

## Deliverables

- **Infrastructure:**
  - Tailwind CSS configured with "Meridian" brand colors.
  - `lib/utils.ts` (cn helper).
  - Lucide React icons installed.

- **Component Primitives (Shadcn-compatible):**
  - `Button`
  - `Card`
  - `Input` / `Label`
  - `Badge`
  - `Table` (later phase)

- **Layout:**
  - Sidebar Navigation (replacing the topbar).
  - App Shell component.

## Execution Phases

1. **Setup:** Install deps, config Tailwind, map theme variables.
2. **Components:** Create base components (Button, Card, Input).
3. **Migration:** Refactor existing pages to use new components.
4. **Cleanup:** Remove legacy CSS from `globals.css`.

## Acceptance Criteria

- [x] Frontend builds without errors.
- [x] Tailwind utility classes work.
- [x] Brand colors (Ink/Accent) are preserved.
- [x] UI components are accessible and consistent.

## Completed Work

### Phase 1: Infrastructure (DONE)
- Downgraded from Tailwind v4 to v3.4.17 (v4 had breaking PostCSS changes)
- `tailwind.config.ts` - Meridian brand colors + Shadcn CSS variables
- `postcss.config.js` - Standard PostCSS setup
- `lib/utils.ts` - cn() helper for class merging
- `globals.css` - Tailwind directives + CSS custom properties

### Phase 2: Components (DONE)
- `components/ui/button.tsx` - Primary, secondary, outline, ghost variants
- `components/ui/card.tsx` - Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
- `components/ui/input.tsx` - Styled input with focus states
- `components/ui/label.tsx` - Form labels
- `components/ui/badge.tsx` - Default + Meridian variants (pending, analyzed, watching, active, closed)

### Phase 3: Layout (DONE)
- `components/layout/sidebar.tsx` - Fixed vertical sidebar with nav links + system status
- `components/layout/app-shell.tsx` - Main layout wrapper
- Updated `app/layout.tsx` to use AppShell (replaced horizontal topbar)

### Phase 4: Page Migrations (DONE)
- `app/page.tsx` - Home page with Card components and Badge for status
- `app/metals/page.tsx` - Placeholder page with Card and Gem icon
- `app/macro-radar/page.tsx` - Event list with filters, Card, Badge, Button, Input, Label
- `app/macro-radar/[eventId]/page.tsx` - Event detail with analysis sections
- `app/theses/page.tsx` - Thesis workspace with Table component for updates log

### Phase 5: Cleanup (DONE)
- `globals.css` already minimal (only Tailwind directives + CSS variables + body styles)
- No legacy CSS classes remaining
- All pages now use Tailwind utility classes

## Task Status: COMPLETE

All acceptance criteria met:
- [x] Frontend builds without errors
- [x] Tailwind utility classes work
- [x] Brand colors (Ink/Accent) preserved
- [x] UI components accessible and consistent

