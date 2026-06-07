# Interface DRY Violations & Hardcoded Patterns

A comprehensive audit of ugly hardcoded stuff and DRY violations in the interface codebase.

**Last updated:** After round 2 of fixes

---

## FIXED ✅

### Input Styling (was 20+ copies)
**Status:** RESOLVED - Now using shared Input component or proper abstractions

### Stat Component (was 2+ copies)
**Status:** RESOLVED - Consolidated into shared component

### Field Component (was 2 copies)
**Status:** MOSTLY RESOLVED - Only 1 remaining in `AgentCron.tsx`

---

## STILL PENDING

### 1. Loading Pulse Dot (11 copies) 🔴

**Files affected:**
- `AgentConfig.tsx` (1)
- `Settings.tsx` (2)
- `AgentChannels.tsx` (1)
- `AgentCron.tsx` (2)
- `AgentIngest.tsx` (1)
- `AgentCortex.tsx` (1)
- `AgentMemories.tsx` (1)
- `MemoryGraph.tsx` (1)
- `Overview.tsx` (1)

**Hardcoded pattern:**
```tsx
<div className="flex items-center gap-2 text-ink-dull">
  <div className="h-2 w-2 animate-pulse rounded-full bg-accent" />
  Loading...
</div>
```

**Note:** `Loader.tsx` exists but has a spinner icon, not the pulse dot. Need either:
- Add pulse variant to `Loader`
- Or create a simple `LoadingDot` component

---

### 2. Color/Style Maps Still Scattered (4 locations) 🟡

#### TYPE_COLORS in `AgentMemories.tsx` (lines 36-45):
```tsx
const TYPE_COLORS: Record<MemoryType, string> = {
  fact: "bg-blue-500/15 text-blue-400",
  preference: "bg-pink-500/15 text-pink-400",
  // ... 6 more
};
```

#### EVENT_CATEGORY_COLORS in `AgentCortex.tsx` (lines 18-32):
```tsx
const EVENT_CATEGORY_COLORS: Record<string, string> = {
  bulletin_generated: "bg-blue-500/15 text-blue-400",
  // ... 11 more
};
```

#### MEMORY_TYPE_COLORS in `AgentDetail.tsx` (line 303):
```tsx
const MEMORY_TYPE_COLORS = [
  "bg-blue-500/15 text-blue-400",
  // ... array of colors
];
```

#### platformColor in `lib/format.ts`:
```tsx
export function platformColor(platform: string): string {
  switch (platform) {
    case "discord": return "bg-indigo-500/20 text-indigo-400";
    // ...
  }
}
```

**Fix:** Create a centralized `theme.ts` or `colors.ts` with all color mappings.

---

### 3. Toolbar/Header Pattern (10+ copies) 🟡

**Common pattern:**
```tsx
<div className="flex items-center gap-3 border-b border-app-line/50 bg-app-darkBox/20 px-6 py-3">
```

**Variations in:**
- `AgentConfig.tsx` (2 toolbar headers)
- `Settings.tsx` (sidebar + content headers)
- `AgentChannels.tsx` (toolbar)
- `AgentCortex.tsx` (filter bar)
- `AgentMemories.tsx` (2 toolbars)
- `ChannelDetail.tsx` (header)

**Fix:** Create a `Toolbar` or `PageHeader` component in `ui/`.

---

### 4. Grid Column Layout Duplication 🟡

**In `AgentMemories.tsx`:**
```tsx
// Table header (line 231)
<div className="grid grid-cols-[80px_1fr_100px_120px_100px] gap-3 ...">

// Table row (line 280)
<div className="grid h-auto w-full grid-cols-[80px_1fr_100px_120px_100px] ...">
```

**Fix:** Define column layout as a constant or use CSS grid template areas.

---

### 5. text-tiny text-ink-faint (69 matches) 🟡

**This is a very common pattern** - might be acceptable if used intentionally for consistency, but could also indicate:
- Missing typography components
- Over-reliance on utility classes

**Files with highest usage:**
- `ChannelDetail.tsx` (15 matches)
- `AgentDetail.tsx` (9 matches)
- `Settings.tsx` (14 matches)
- `AgentConfig.tsx` (6 matches)

---

### 6. Field Component Remaining 🟡

**File:** `AgentCron.tsx` (line 400)
```tsx
function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-ink-dull">{label}</label>
      {children}
    </div>
  );
}
```

**Fix:** Use `Forms.Field` from `ui/forms/index.ts` instead.

---

## NEW COMPONENTS ADDED ✅

### NumberStepper
**File:** `ui/NumberStepper.tsx`
**Usage:** Reusable number input with +/- buttons
**Exported:** Yes, in `ui/index.ts`

---

## LOW PRIORITY PATTERNS

These are acceptable repetition or would be over-engineering to DRY:

1. **Empty/Error State Patterns** - Similar but context-specific
2. **AnimatePresence Wrappers** - Framer Motion patterns are fine
3. **Modal/Dialog Structures** - Each has unique content
4. **Pagination Controls** - Only 2-3 instances, not worth abstracting yet

---

## PRIORITY ORDER

1. **Loading pulse dot** - 11 copies, easy win, should be component
2. **Color maps consolidation** - Centralize all color mappings
3. **Toolbar component** - 10+ identical patterns
4. **Field component** - 1 remaining, quick fix
5. **Grid layouts** - Only if more tables added
