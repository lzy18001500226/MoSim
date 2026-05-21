# PRD Writing Style Guide

How to write clear, unambiguous requirements that anyone can understand and implement.

---

## Core Principles

### 1. Precision Over Brevity

**Wrong:** "System should respond quickly."

**Right:** "API endpoints return response within 200ms at P95 under normal load (< 1000 concurrent users)."

### 2. Specific Over General

**Wrong:** "Support various file formats."

**Right:** "Support file upload for: PDF, DOC, DOCX, TXT. Max file size: 25MB. Other formats show error: 'Unsupported file type. Please upload PDF, DOC, DOCX, or TXT.'"

### 3. Concrete Over Abstract

**Wrong:** "Improve user experience."

**Right:** "Reduce checkout flow from 5 steps to 3 steps. Target completion time: < 90 seconds."

### 4. Complete Over Concise

**Wrong:** "User can delete their account."

**Right:** "User can delete their account:
- Location: Settings > Account > Delete Account
- Requires: Password confirmation
- Waiting period: 14 days (can cancel)
- Data deleted: All personal data (see data inventory)
- Data retained: Anonymized transaction history for accounting
- Notification: Email confirmation sent immediately and at deletion"

---

## Language Rules

### Use Active Voice

**Passive (avoid):** "The order will be shipped by the warehouse."

**Active (prefer):** "Warehouse ships the order within 24 hours."

### Use Present Tense

**Future (avoid):** "The system will display an error."

**Present (prefer):** "System displays error message."

### Name the Actor

**Ambiguous:** "Data is validated."

**Clear:** "Server validates data before saving."

### Quantify Everything

| Vague | Specific |
|-------|----------|
| Fast | < 200ms |
| Large | > 1MB |
| Many | > 100 |
| Soon | Within 24 hours |
| Regularly | Every 6 hours |
| Most | > 80% |
| Few | < 10% |

---

## Banned Words and Phrases

### Vague Adjectives (Replace or Define)

| Word | Problem | Replace With |
|------|---------|--------------|
| Easy | Subjective | [Specific interaction steps] |
| Simple | Subjective | [Specific design constraints] |
| Fast | Unmeasurable | [Specific time in ms/s] |
| Secure | Vague | [Specific security measures] |
| Modern | Meaningless | [Specific standards/patterns] |
| User-friendly | Subjective | [Specific usability metrics] |
| Intuitive | Subjective | [Specific learnability metrics] |
| Flexible | Vague | [Specific variations supported] |
| Robust | Vague | [Specific failure handling] |
| Clean | Subjective | [Specific design constraints] |
| Smart | Marketing | [Specific behavior] |
| Powerful | Marketing | [Specific capabilities] |

### Vague Verbs (Be Specific)

| Word | Problem | Replace With |
|------|---------|--------------|
| Handle | Too general | [Specific processing steps] |
| Process | Too general | [Specific algorithm/steps] |
| Support | Too general | [Specific capabilities list] |
| Manage | Too general | [Specific CRUD operations] |
| Improve | Unmeasurable | [Specific metric change] |
| Optimize | Unmeasurable | [Specific performance target] |
| Enhance | Marketing | [Specific new capability] |

### Weasel Words (Avoid Entirely)

- "Should" → Use "must" or "does"
- "Could" → Define if it does or doesn't
- "May" → Define the conditions
- "Might" → Eliminate ambiguity
- "Sometimes" → Define when exactly
- "Usually" → Define exceptions
- "Often" → Quantify frequency
- "Rarely" → Define when it occurs
- "Etc." → List everything
- "And so on" → List everything
- "As appropriate" → Define criteria

---

## Structure Patterns

### User Story Format

```
As a [specific role],
I want [specific action],
so that [specific benefit].
```

**Bad:**
> As a user, I want to save items, so that I can find them later.

**Good:**
> As a logged-in customer browsing products,
> I want to save products to a wishlist,
> so that I can purchase them later without searching again.

### Acceptance Criteria Format (Given-When-Then)

```
Given [specific context/precondition],
When [specific action/trigger],
Then [specific outcome/result].
```

**Bad:**
> Given user is logged in,
> When user saves an item,
> Then item is saved.

**Good:**
> Given customer is logged in and viewing a product page,
> When customer clicks the heart icon,
> Then:
> - Heart icon fills solid (visual feedback)
> - Product appears in Saved Items (accessible from header)
> - "Saved to wishlist" toast appears for 3 seconds
> - Saved Items counter increments by 1

### Requirement Format

```
[Actor] [action] [object] [conditions/constraints].
```

**Bad:**
> Files can be uploaded.

**Good:**
> Authenticated user uploads file (max 25MB; types: PDF, DOCX, TXT) to document library.

### Business Rule Format

```
WHEN [trigger condition]
IF [condition]
THEN [result]
ELSE [alternative result]
```

**Bad:**
> Apply discount for members.

**Good:**
> WHEN calculating order total
> IF customer has active Premium membership AND order subtotal ≥ $50
> THEN apply 15% discount to subtotal before tax
> ELSE IF customer has active Basic membership AND order subtotal ≥ $100
> THEN apply 10% discount to subtotal before tax
> ELSE no discount applied

---

## Formatting Guidelines

### Use Tables for Complex Information

**Bad (prose):**
> Admin users can create, read, update, and delete all projects. Manager users can create and read all projects, and update and delete only projects they own. Member users can only read projects they're assigned to.

**Good (table):**

| Action | Admin | Manager | Member |
|--------|-------|---------|--------|
| Create project | ✓ All | ✓ All | — |
| Read project | ✓ All | ✓ All | Own only |
| Update project | ✓ All | Own only | — |
| Delete project | ✓ All | Own only | — |

### Use Lists for Sequences

**Bad (paragraph):**
> The user enters their email, then enters their password, then clicks submit, then the system validates the credentials, then if valid the user sees the dashboard, otherwise they see an error.

**Good (numbered list):**
1. User enters email
2. User enters password
3. User clicks "Sign In"
4. System validates credentials
   - Valid → Display dashboard
   - Invalid → Display error: "Invalid email or password"
   - Locked → Display: "Account locked. Reset password to unlock."

### Use Headings for Scanability

Organize requirements so readers can:
- Find what they need quickly
- Understand scope at a glance
- Navigate to specific sections

### Use Diagrams for Flows

State machines, user flows, and system interactions are often clearer as diagrams than prose.

---

## Examples: Before and After

### Example 1: Feature Description

**Before:**
> Users should be able to search for products easily and get relevant results fast.

**After:**
> **Product Search**
> 
> **Trigger:** User enters text in search bar (header, all pages)
> 
> **Behavior:**
> - Search triggers after 300ms of no typing (debounced)
> - Minimum query length: 2 characters
> - Results appear in dropdown (max 10 items)
> - Full results page on Enter or "See all results" click
> 
> **Results:**
> - Ranked by: (1) exact title match, (2) partial title match, (3) description match, (4) category match
> - Each result shows: thumbnail, title, price, rating
> - Response time: < 500ms for dropdown, < 1s for full page
> 
> **Empty State:**
> - "No results for '[query]'. Try different keywords."
> - Show 3 suggested searches based on popular queries

### Example 2: Business Rule

**Before:**
> Free shipping for orders over $50, except for some items.

**After:**
> **Business Rule: Free Shipping Eligibility**
> 
> **Rule ID:** BR-SHIP-001
> 
> **Logic:**
> ```
> IF order.subtotal >= $50.00
>    AND all items in order are shipping_eligible
>    AND shipping_address is in continental US
> THEN shipping_cost = $0.00
> ELSE shipping_cost = calculated_rate
> ```
> 
> **Definitions:**
> - `subtotal`: Sum of item prices before tax and shipping
> - `shipping_eligible`: Item flag (false for oversized, hazmat, marketplace items)
> - `continental US`: 48 contiguous states (excludes AK, HI, territories)
> - `calculated_rate`: Based on carrier API (see Shipping Calculation spec)
> 
> **Display:**
> - Cart shows: "Add $X more for free shipping" if eligible items < $50
> - Cart shows: "Free shipping!" when threshold met
> - Cart shows: "Some items require shipping fee" if ineligible items present

### Example 3: Error Handling

**Before:**
> Show an error if payment fails.

**After:**
> **Payment Error Handling**
> 
> | Error Type | Detection | User Message | Actions Available | System Action |
> |------------|-----------|--------------|-------------------|---------------|
> | Card declined | Payment API response | "Your card was declined. Please try another card or contact your bank." | "Try again" / "Use different card" | Log error code |
> | Expired card | Payment API response | "Your card has expired. Please update your card details." | "Update card" | Log, no retry |
> | Insufficient funds | Payment API response | "Payment could not be processed. Please try another payment method." | "Try again" / "Use different card" | Log error code |
> | Network timeout | No response in 30s | "We couldn't connect to the payment system. Please try again." | "Try again" | Log, alert if >5% |
> | Fraud suspected | Payment API flag | "We couldn't process this payment. Please contact support." | "Contact support" | Log, alert security |
> | Unknown error | Unrecognized response | "Something went wrong. Please try again or contact support." | "Try again" / "Contact support" | Log full response, alert |
> 
> **All payment errors:**
> - Preserve cart contents
> - Do not create order
> - Log full error details (not shown to user)
> - Display error on same page (no redirect)

---

## Checklist: Is My Requirement Clear?

Before finalizing any requirement, verify:

- [ ] **Who** performs the action is explicit
- [ ] **What** they do is specific (not vague verb)
- [ ] **When** it happens is defined (trigger/condition)
- [ ] **Where** in the product it occurs is specified
- [ ] **How** it works is detailed (not "system handles")
- [ ] **What if** something goes wrong is documented
- [ ] **Numbers** replace adjectives where applicable
- [ ] **Examples** illustrate the requirement
- [ ] A **new team member** could implement it without asking questions
