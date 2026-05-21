# Common PRD Pitfalls

A guide to the most common mistakes in PRD writing and how to avoid them.

---

## Pitfall 1: Solution Disguised as Problem

### The Mistake
Writing "We need a dashboard" or "We need to build X" as the problem statement.

### Why It's Wrong
- Jumps to solution before understanding problem
- Limits solution space
- May solve wrong problem

### How to Spot It
Look for:
- "We need to build..."
- "We need a [solution]..."
- Problem statement that names a feature type

### How to Fix It

❌ **Wrong:**
> "We need a dashboard for project visibility."

✅ **Right:**
> "Project managers spend 2+ hours weekly compiling status updates from 5 different systems. They often miss critical blockers until standup meetings, causing an average 1.5 day delay in addressing issues."

---

## Pitfall 2: Vague Acceptance Criteria

### The Mistake
Using subjective or unmeasurable acceptance criteria.

### Why It's Wrong
- QA can't write tests
- Developers interpret differently
- Leads to rework

### How to Spot It
Look for:
- "Should be easy to..."
- "User can intuitively..."
- "System handles gracefully..."
- No specific numbers or behaviors

### How to Fix It

❌ **Wrong:**
> "User can easily search for products."

✅ **Right:**
> Given user is on the product page,
> When user enters search term of 2+ characters,
> Then:
> - Results appear within 500ms
> - Top 20 results displayed with pagination
> - Results ranked by relevance (title match > description match)
> - "No results" state shown if 0 matches with suggested terms

---

## Pitfall 3: Missing Negative Cases

### The Mistake
Only documenting the happy path—what happens when everything works.

### Why It's Wrong
- 80% of code handles edge cases
- Users WILL do unexpected things
- System WILL fail sometimes

### How to Spot It
- No error messages defined
- No "what if" scenarios
- Only successful flows documented

### How to Fix It

❌ **Wrong:**
> "User can upload a profile photo."

✅ **Right:**
> User can upload a profile photo:
> - **Happy path:** User selects file, image previews, user confirms, image uploads and displays
> - **File too large (>5MB):** Show error "Image must be under 5MB. Your file is [X]MB." Keep current photo.
> - **Wrong format:** Show error "Please upload a JPG, PNG, or GIF." List allowed formats.
> - **Upload fails:** Show "Upload failed. Please try again." Offer retry button. Log error.
> - **Slow connection:** Show progress bar. Allow cancel. Resume if supported.

---

## Pitfall 4: Implicit Assumptions

### The Mistake
Assuming developers know things that aren't written down.

### Why It's Wrong
- Different interpretations
- Tribal knowledge gets lost
- New team members can't onboard

### How to Spot It
- "Obviously..."
- "As expected..."
- No defaults specified
- No sorting/ordering specified

### How to Fix It

❌ **Wrong:**
> "Display user's orders."

✅ **Right:**
> Display user's orders:
> - **Default sort:** By order date, newest first
> - **Pagination:** 20 orders per page, infinite scroll on mobile
> - **Date range:** Last 90 days by default, option to view all
> - **Statuses shown:** All statuses (Pending, Processing, Shipped, Delivered, Cancelled)
> - **Empty state:** "No orders yet. Start shopping!" with link to catalog
> - **Loading state:** Skeleton loader matching order card layout

---

## Pitfall 5: Missing State Handling

### The Mistake
Not defining all possible states and transitions.

### Why It's Wrong
- Developers guess at transitions
- Invalid state combinations occur
- Recovery paths undefined

### How to Spot It
- No state diagram
- Transitions mentioned without conditions
- No "who can" definitions

### How to Fix It

❌ **Wrong:**
> "Order can be cancelled."

✅ **Right:**
> Order cancellation rules:
> 
> | Current Status | Can Cancel? | Who Can | Result | Side Effects |
> |----------------|-------------|---------|--------|--------------|
> | Pending | Yes | Customer, Admin | → Cancelled | Refund initiated |
> | Processing | Yes | Customer, Admin | → Cancelled | Refund initiated |
> | Shipped | No | — | Error: "Order already shipped" | Suggest: Contact support |
> | Delivered | No | — | Error: "Order delivered" | Suggest: Return process |
> | Cancelled | No | — | Error: "Already cancelled" | None |
> 
> Cancellation triggers:
> - Inventory restored immediately
> - Refund processed within 3-5 business days
> - Confirmation email sent
> - Order history shows "Cancelled by [actor]" with timestamp

---

## Pitfall 6: Undefined Permissions

### The Mistake
Not specifying who can do what.

### Why It's Wrong
- Security gaps
- Features built for wrong audience
- Inconsistent access control

### How to Spot It
- "Users can..."—which users?
- No role definitions
- No permission matrix

### How to Fix It

❌ **Wrong:**
> "Users can edit project settings."

✅ **Right:**
> Project settings permissions:
> 
> | Setting | Viewer | Member | Admin | Owner |
> |---------|--------|--------|-------|-------|
> | View settings | ✓ | ✓ | ✓ | ✓ |
> | Edit name/description | — | — | ✓ | ✓ |
> | Manage members | — | — | ✓ | ✓ |
> | Delete project | — | — | — | ✓ |
> | Transfer ownership | — | — | — | ✓ |
> 
> Unauthorized action: Show "You don't have permission" with "Request access" link.

---

## Pitfall 7: Undefined Boundaries

### The Mistake
Not specifying limits, maximums, or constraints.

### Why It's Wrong
- Developers make arbitrary decisions
- Performance issues at scale
- Inconsistent behavior

### How to Spot It
- "Support multiple..."—how many?
- "Handle large..."—how large?
- No character limits on text fields

### How to Fix It

❌ **Wrong:**
> "User can add tags to their post."

✅ **Right:**
> Post tagging:
> - **Max tags per post:** 10
> - **Tag length:** 1-30 characters
> - **Allowed characters:** Letters, numbers, hyphens
> - **Case handling:** Stored lowercase, displayed as entered first time
> - **Duplicates:** Silently ignored (case-insensitive)
> - **Autocomplete:** Show top 10 matching existing tags after 2 characters

---

## Pitfall 8: No Error Messages

### The Mistake
Not defining what users see when things go wrong.

### Why It's Wrong
- Developers write technical messages
- Inconsistent user experience
- Users can't self-recover

### How to Spot It
- "Show an error"—what error?
- No error message catalog
- Technical errors exposed to users

### How to Fix It

❌ **Wrong:**
> "If save fails, show an error."

✅ **Right:**
> Save error handling:
> 
> | Error | User Message | Technical Log | Action Offered |
> |-------|--------------|---------------|----------------|
> | Network timeout | "Couldn't save. Check your connection and try again." | Timeout after 30s to /api/save | "Try again" button |
> | Validation failed | "[Field] is invalid: [reason]" | 400 response with field errors | Highlight field, focus |
> | Server error | "Something went wrong. We're looking into it." | 500 response with error ID | "Try again" + support link |
> | Conflict (concurrent edit) | "This was edited by someone else. Review changes?" | 409 with diff | "View changes" / "Overwrite" |

---

## Pitfall 9: Missing Empty States

### The Mistake
Only designing for "has data" scenarios.

### Why It's Wrong
- New users see broken-looking UI
- Missing opportunity for guidance
- Confusion about whether feature works

### How to Spot It
- No wireframe for empty state
- "Display list of..."—what if empty?
- No first-time user experience

### How to Fix It

❌ **Wrong:**
> "Show user's saved items."

✅ **Right:**
> Saved items states:
> 
> **Empty state (never saved):**
> - Illustration: Heart icon
> - Title: "No saved items yet"
> - Description: "Tap the heart on any item to save it here"
> - CTA: "Browse popular items" → catalog
> 
> **Empty state (all removed):**
> - Same as above but title: "No saved items"
> 
> **Has items:**
> - Grid view, 2 columns mobile, 4 columns desktop
> - Each item shows: image, name, price, remove button

---

## Pitfall 10: Overlooking Mobile/Responsive

### The Mistake
Designing only for desktop.

### Why It's Wrong
- 50%+ traffic is mobile
- Touch is different from click
- Screen space is limited

### How to Spot It
- Wireframes only show desktop
- No touch considerations
- Complex tables/forms with no mobile variant

### How to Fix It

❌ **Wrong:**
> "Display data in a table."

✅ **Right:**
> Data display by device:
> 
> **Desktop (>1024px):** Full table with all columns
> 
> **Tablet (768-1024px):** Table with priority columns, others in expandable row
> 
> **Mobile (<768px):** Card view with:
> - Primary info visible
> - "Show more" expands details
> - Swipe left to reveal actions

---

## Pitfall 11: No Consideration of Performance Impact

### The Mistake
Adding features without considering performance implications.

### Why It's Wrong
- Features that don't scale
- Poor user experience
- Expensive infrastructure

### How to Spot It
- "Load all..."
- "Real-time update..."
- No pagination mentioned

### How to Fix It

❌ **Wrong:**
> "Show all user notifications."

✅ **Right:**
> Notifications:
> - **Initial load:** Latest 20 notifications
> - **Load more:** Additional 20 on scroll or "Load more" click
> - **Max displayed:** 100 (older available in notification center)
> - **Real-time updates:** New notifications pushed via WebSocket
> - **Batching:** Multiple rapid notifications grouped ("3 new likes")
> - **Performance target:** Notification panel opens in <100ms

---

## Pitfall 12: Ignoring Existing Systems

### The Mistake
Not accounting for migration, backward compatibility, or existing user expectations.

### Why It's Wrong
- Breaks existing workflows
- Loses user data
- Confuses existing users

### How to Spot It
- No mention of current system
- No migration plan
- No consideration of existing users

### How to Fix It

❌ **Wrong:**
> "New project page design."

✅ **Right:**
> New project page:
> 
> **Migration:**
> - Existing projects auto-migrated; no action needed
> - Legacy fields mapped to new structure (see migration table)
> - Fields with no equivalent preserved in "Legacy" section
> 
> **Backward compatibility:**
> - API v1 continues to work, returns old format
> - API v2 required for new fields
> - Deprecation notice on v1, sunset in 6 months
> 
> **User transition:**
> - "What's new" banner on first visit
> - Guided tour highlighting key changes
> - Help article: "Understanding the new project page"

---

## Meta-Pitfall: Not Reviewing with Engineering

### The Mistake
Handing off PRD without engineering input.

### Why It's Wrong
- Technical impossibilities discovered late
- Effort underestimated
- Better approaches missed

### How to Fix It

Before marking PRD as "ready":
1. **Technical review:** Engineer reads full PRD, asks questions
2. **Feasibility check:** Any technically challenging items flagged
3. **Effort input:** High-level sizing validated
4. **Question log:** All questions documented and answered in PRD

**Rule:** If an engineer asks a question, it means the PRD was incomplete. Update the PRD with the answer.
