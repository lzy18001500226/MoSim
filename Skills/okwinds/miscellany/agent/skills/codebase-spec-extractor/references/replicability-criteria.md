# Replicability Criteria

Standards for evaluating whether a specification is complete enough to enable accurate replication without access to the original source code.

## The Replicability Test

A specification passes the replicability test if:

1. **A competent developer** who has never seen the original code
2. **Using only the specification** (no access to original source)
3. **Could implement a system** that:
   - Handles all the same inputs
   - Produces all the same outputs
   - Exhibits all the same behaviors
   - Enforces all the same constraints
   - Handles all the same edge cases
   - Fails in all the same ways

The implementation may use different:
- Programming languages
- Frameworks
- Libraries
- Code structure
- Variable names

But must produce **functionally identical behavior**.

---

## Levels of Specification Quality

### Level 1: Inadequate
The spec describes what the system does at a high level, but leaves significant ambiguity.

**Symptoms:**
- Uses vague terms ("handles errors appropriately", "validates input")
- Missing edge cases
- No concrete examples
- Business rules described in prose without precision

**Example of inadequate spec:**
> "The discount function calculates the appropriate discount for an order based on the customer's status and order total."

**Problems:**
- What customer statuses exist?
- What are the discount percentages?
- Is there a minimum order for discount?
- What if the customer has multiple statuses?

### Level 2: Partial
The spec covers the main cases but misses edge cases and error handling.

**Symptoms:**
- Happy path well documented
- Error cases mentioned but not detailed
- Some edge cases missing
- Implicit assumptions not stated

**Example of partial spec:**
> "The discount function applies 10% for VIP customers and 5% for regular customers. Orders under $50 get no discount."

**Still missing:**
- What if order is exactly $50?
- What about new customers?
- What if VIP status expired yesterday?
- Maximum discount cap?
- Currency precision?

### Level 3: Complete
The spec covers all cases with enough detail to implement without guesswork.

**Symptoms:**
- All input combinations documented
- All output forms documented
- All error conditions documented
- Edge cases explicitly addressed
- Business rules stated with precision
- Examples provided

**Example of complete spec:**
```markdown
## calculateDiscount(order, customer)

### Inputs
- order.totalCents: integer, minimum 0
- order.itemCount: integer, minimum 1
- customer.tier: enum ["NEW", "REGULAR", "VIP", "SUSPENDED"]
- customer.tierSince: ISO date string

### Output
- discountCents: integer, minimum 0

### Business Rules
1. SUSPENDED customers get no discount (0)
2. Orders with totalCents < 5000 get no discount (0)
3. NEW customers (tier="NEW") get 15% discount
4. REGULAR customers get 5% discount
5. VIP customers get 10% discount
6. If customer has been VIP for >1 year, add 5% (max 15% for VIP)
7. Maximum discount is 30% of totalCents
8. Discount is rounded DOWN to nearest cent

### Tier Determination
- Tier is determined by customer.tier at time of call
- tierSince is used only for VIP duration bonus

### Edge Cases
| Case | Input | Output | Rationale |
|------|-------|--------|-----------|
| Exactly $50 | totalCents=5000 | Apply discount | >= threshold |
| $49.99 | totalCents=4999 | 0 | < threshold |
| Expired VIP | tier="VIP", tierSince=yesterday | Apply VIP discount | Tier is current status |
| Null customer | customer=null | throws InvalidInputError | |
| Negative total | totalCents=-100 | throws InvalidInputError | |

### Examples
1. order.totalCents=10000, customer.tier="VIP", tierSince=2y ago
   → discount = 10000 * 0.15 = 1500 cents
2. order.totalCents=10000, customer.tier="NEW"
   → discount = 10000 * 0.15 = 1500 cents
3. order.totalCents=4999, customer.tier="VIP"
   → discount = 0 (below threshold)
```

### Level 4: Verifiable
Level 3 plus machine-executable test cases and formal validation criteria.

**Additional elements:**
- Test cases in executable format
- Acceptance criteria as Given/When/Then
- Performance benchmarks
- Security requirements with verification method

---

## Specification Completeness Checklist

### Interface Completeness
- [ ] All input parameters documented with types
- [ ] All input constraints documented (min, max, format, valid values)
- [ ] All output types documented
- [ ] All possible output states documented
- [ ] All exceptions/errors documented with conditions

### Logic Completeness
- [ ] Main algorithm documented step by step
- [ ] All conditional branches documented
- [ ] All loops documented with bounds
- [ ] All calculations shown with formulas
- [ ] Order of operations clear

### Constraint Completeness
- [ ] All validation rules explicit
- [ ] All business rules stated
- [ ] All technical limits documented
- [ ] All security constraints documented

### Edge Case Completeness
- [ ] Null/undefined handling documented
- [ ] Empty collection handling documented
- [ ] Boundary values documented
- [ ] Concurrent access handling documented
- [ ] Timeout/failure handling documented

### Example Completeness
- [ ] At least one example per main scenario
- [ ] At least one example per edge case
- [ ] Examples show exact input → output

---

## Common Replicability Failures

### 1. Implied Defaults
**Problem:** Spec doesn't state what happens when optional parameter is omitted.

**Bad:**
> "limit parameter controls how many results to return"

**Good:**
> "limit: integer, optional, default=20, range [1, 100]"

### 2. Ambiguous Ordering
**Problem:** Spec doesn't state how results are ordered.

**Bad:**
> "Returns list of users"

**Good:**
> "Returns list of users ordered by created_at DESC, then by id ASC"

### 3. Missing Error Conditions
**Problem:** Spec only describes success case.

**Bad:**
> "Returns the user with the given ID"

**Good:**
> "Returns the user with the given ID. Returns 404 if user not found. Returns 403 if requester lacks permission to view user."

### 4. Unstated Assumptions
**Problem:** Spec assumes knowledge not documented.

**Bad:**
> "Applies the standard discount rules"

**Good:**
> [Full documentation of discount rules with all conditions]

### 5. Imprecise Timing
**Problem:** Spec doesn't state exact timing behavior.

**Bad:**
> "Token expires after some time"

**Good:**
> "Token expires 24 hours after issuance, evaluated at second precision"

### 6. Vague Error Handling
**Problem:** Spec says errors are handled but not how.

**Bad:**
> "Handles database errors gracefully"

**Good:**
> "On database connection failure: retry 3 times with exponential backoff (1s, 2s, 4s), then return 503 with error code DB_UNAVAILABLE"

---

## Verification Methods

### 1. Peer Review
Have someone unfamiliar with the code review the spec:
- Can they explain what the system does?
- Can they identify all the inputs and outputs?
- Can they trace through edge cases?

### 2. Implementation Test
Give the spec to an AI or developer without code access:
- Can they implement it?
- Where do they ask questions?
- Where do they make assumptions?

### 3. Test Case Derivation
From the spec alone:
- Can complete test cases be written?
- Do the test cases cover all documented behavior?
- Are there behaviors that can't be tested because spec is unclear?

### 4. Diff Analysis
After implementation from spec:
- Compare behavior against original
- Any differences indicate spec gaps
- Document and add missing details

---

## Quality Metrics

### Coverage Metrics
- **Element Coverage:** % of code elements with specifications
- **Branch Coverage:** % of conditional branches documented
- **Error Coverage:** % of error conditions documented
- **Edge Case Coverage:** % of boundary conditions documented

### Precision Metrics
- **Ambiguity Count:** Number of spec statements that could be interpreted multiple ways
- **Assumption Count:** Number of unstated assumptions discovered during implementation
- **Question Count:** Number of clarifying questions needed during implementation

### Verification Metrics
- **Test Derivation Rate:** % of behaviors with derivable test cases
- **Implementation Accuracy:** % of behaviors correctly implemented from spec alone
- **First-Pass Success:** % of implementations correct without iteration

---

## Continuous Improvement

### After Each Replication Attempt

1. **Document failures:** What was wrong in the replication?
2. **Trace to spec:** What was missing or unclear in the spec?
3. **Update spec:** Add the missing information
4. **Add test case:** Ensure this case is covered going forward

### Feedback Loop
```
Spec → Implementation → Compare → Gaps → Update Spec → Repeat
```

The spec is never "done"—it improves with each replication attempt.
