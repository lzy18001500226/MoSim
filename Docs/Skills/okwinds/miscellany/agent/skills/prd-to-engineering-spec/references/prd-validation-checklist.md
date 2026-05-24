# PRD Validation Checklist

A comprehensive checklist for validating Product Requirements Documents before technical design begins. Every unchecked item represents a potential requirement gap that could cause implementation issues.

## How to Use This Checklist

1. Go through each section systematically
2. Mark items as: ✅ Present | ⚠️ Unclear | ❌ Missing
3. Generate a defect report for items marked ⚠️ or ❌
4. Do NOT proceed to technical design until all ❌ items are resolved

---

## 1. Document Basics

- [ ] Document has clear title and version
- [ ] Author and stakeholders identified
- [ ] Date and revision history present
- [ ] Document status (Draft/Review/Approved) clear
- [ ] Scope of the document defined

## 2. Problem Statement

- [ ] Problem being solved is clearly articulated
- [ ] Why this problem matters (business value)
- [ ] Who experiences this problem (affected users)
- [ ] Current state / pain points described
- [ ] Success metrics defined (how will we know it's solved?)

## 3. Users & Personas

### 3.1 User Identification
- [ ] All user types/roles identified
- [ ] Primary vs secondary users distinguished
- [ ] User personas with relevant characteristics

### 3.2 Per User Type
For EACH user type, verify:
- [ ] Goals and motivations documented
- [ ] Pain points specific to this user
- [ ] Technical proficiency level
- [ ] Access/permission level
- [ ] Frequency of use

## 4. Functional Requirements

### 4.1 Feature Completeness
- [ ] All features listed
- [ ] Feature priority clearly marked (P0/P1/P2 or MoSCoW)
- [ ] MVP scope explicitly defined
- [ ] What's OUT of scope explicitly stated
- [ ] Future phases mentioned but clearly separated

### 4.2 User Stories
For EACH user story, verify:
- [ ] Follows "As a [role], I want [action], so that [benefit]"
- [ ] Benefit explains business value, not just action
- [ ] Acceptance criteria present and testable
- [ ] Story is appropriately sized (not epic)
- [ ] Dependencies on other stories noted

### 4.3 Acceptance Criteria Quality
For EACH acceptance criterion:
- [ ] Written in Given/When/Then format (preferred) or clear conditions
- [ ] Specific and measurable (not vague)
- [ ] Covers both positive and negative cases
- [ ] Edge cases mentioned
- [ ] No ambiguous terms (e.g., "appropriate", "user-friendly", "fast")

## 5. Business Rules

### 5.1 Rule Documentation
- [ ] All business rules explicitly listed
- [ ] Rules are numbered/identified for traceability
- [ ] Rules are stated precisely (not prose)

### 5.2 Rule Completeness
For EACH business rule:
- [ ] Input conditions specified
- [ ] Output/result specified
- [ ] All branches of logic covered
- [ ] Boundary conditions defined
- [ ] Exception cases documented

### 5.3 Calculations & Formulas
For EACH calculation:
- [ ] Formula explicitly provided
- [ ] Input variables defined
- [ ] Output type and precision specified
- [ ] Rounding rules stated
- [ ] Edge cases (zero, negative, max) addressed

## 6. Data Requirements

### 6.1 Data Elements
- [ ] All data entities mentioned
- [ ] Key attributes of each entity listed
- [ ] Required vs optional fields indicated
- [ ] Data types specified (at least conceptually)
- [ ] Validation rules mentioned

### 6.2 Data Sources
- [ ] Where data comes from identified
- [ ] For integrations: source system identified
- [ ] For user input: input method described
- [ ] For calculated data: calculation defined
- [ ] Data freshness requirements

### 6.3 Data Lifecycle
- [ ] How data is created
- [ ] How data is updated
- [ ] How data is deleted (or if deletion is allowed)
- [ ] Data retention requirements
- [ ] Data archival needs

## 7. UI/UX Requirements

### 7.1 Visual Design
- [ ] Wireframes or mockups provided (if UI exists)
- [ ] Key screens/pages identified
- [ ] Navigation flow described
- [ ] Brand/style guidelines referenced

### 7.2 Interaction Design
- [ ] User flows documented
- [ ] Form behaviors described
- [ ] Error display approach mentioned
- [ ] Loading states mentioned
- [ ] Empty states mentioned

### 7.3 Accessibility
- [ ] Accessibility requirements stated
- [ ] Compliance level (WCAG AA, etc.) specified
- [ ] Key a11y considerations mentioned

### 7.4 Responsive/Multi-device
- [ ] Supported devices/browsers listed
- [ ] Mobile-specific behaviors mentioned
- [ ] Screen size considerations

## 8. Error Handling & Edge Cases

### 8.1 Error Scenarios
- [ ] Known error scenarios listed
- [ ] User-caused errors (validation)
- [ ] System errors (failures)
- [ ] External dependency failures

### 8.2 Error Handling Requirements
For EACH error type:
- [ ] How error should be communicated to user
- [ ] Recovery path described
- [ ] Data preservation requirements
- [ ] Retry behavior (if applicable)

### 8.3 Edge Cases
- [ ] Empty data scenarios
- [ ] Maximum data scenarios
- [ ] Concurrent user scenarios
- [ ] Timeout scenarios
- [ ] Partial failure scenarios

## 9. Non-Functional Requirements

### 9.1 Performance
- [ ] Response time requirements (with percentiles)
- [ ] Throughput requirements (requests/second)
- [ ] Concurrent user expectations
- [ ] Data volume expectations
- [ ] Growth projections

### 9.2 Scalability
- [ ] Expected scale (users, data, transactions)
- [ ] Scale timeline (when do we need to support X?)
- [ ] Scaling approach preferences (vertical/horizontal)

### 9.3 Availability
- [ ] Uptime requirements (e.g., 99.9%)
- [ ] Maintenance window requirements
- [ ] Disaster recovery requirements
- [ ] Backup requirements

### 9.4 Security
- [ ] Authentication requirements
- [ ] Authorization requirements
- [ ] Data encryption requirements
- [ ] Compliance requirements (GDPR, HIPAA, etc.)
- [ ] Audit logging requirements
- [ ] Sensitive data handling

### 9.5 Compatibility
- [ ] Browser support requirements
- [ ] Device support requirements
- [ ] API versioning requirements
- [ ] Backward compatibility requirements

## 10. Integration Requirements

### 10.1 External Systems
For EACH integration:
- [ ] System identified
- [ ] Integration purpose clear
- [ ] Data exchanged described
- [ ] Integration method (API, file, etc.)
- [ ] Availability/SLA of external system
- [ ] Failure handling

### 10.2 API Requirements
- [ ] API consumers identified (if providing API)
- [ ] API contract expectations
- [ ] Rate limiting requirements
- [ ] Versioning approach

## 11. Dependencies & Constraints

### 11.1 Technical Constraints
- [ ] Required technologies (if mandated)
- [ ] Prohibited technologies
- [ ] Infrastructure constraints
- [ ] Budget constraints

### 11.2 External Dependencies
- [ ] Third-party services needed
- [ ] External approvals needed
- [ ] Data from other teams
- [ ] Timeline dependencies on other projects

### 11.3 Organizational Constraints
- [ ] Compliance requirements
- [ ] Approval processes
- [ ] Legal/contract constraints
- [ ] Resource availability

## 12. Timeline & Milestones

- [ ] Target launch date
- [ ] Key milestones defined
- [ ] Phased rollout plan (if any)
- [ ] Beta/pilot plans
- [ ] Dependencies affecting timeline

## 13. Success Criteria

### 13.1 Launch Criteria
- [ ] What must be true to launch
- [ ] Blocking vs nice-to-have features
- [ ] Performance thresholds
- [ ] Quality thresholds

### 13.2 Success Metrics
- [ ] KPIs defined
- [ ] Baseline measurements (if available)
- [ ] Target values
- [ ] Measurement method
- [ ] Measurement timeline

## 14. Open Questions & Risks

- [ ] Known unknowns documented
- [ ] Assumptions explicitly stated
- [ ] Risks identified
- [ ] Decision points identified

---

## Validation Summary Template

After completing the checklist:

```markdown
# PRD Validation Summary

**Document:** [PRD Name]
**Version:** [Version]
**Validated:** [Date]
**Validator:** [Name]

## Completeness Score
- Section 1 (Basics): X/Y items ✓
- Section 2 (Problem): X/Y items ✓
- ...

## Critical Gaps (❌ - Must Fix)
1. [Gap description]
   - Location: [Section]
   - Impact: [Why this matters]
   - Needed: [What information is required]

## Warnings (⚠️ - Should Clarify)
1. [Unclear item]
   - Location: [Section]
   - Concern: [What's unclear]

## Assumptions Made
1. [Assumption we're proceeding with]
   - Source: [Why we assume this]
   - Risk if wrong: [Impact]

## Recommendation
[ ] ✅ Proceed to technical design
[ ] ⚠️ Proceed with noted assumptions
[ ] ❌ Requires PRD revision before proceeding
```

---

## Red Flags to Watch For

### Vague Language
Watch for and flag:
- "User-friendly" → What does this mean specifically?
- "Fast" → What latency is acceptable?
- "Secure" → What security measures required?
- "Easy to use" → For whom? In what context?
- "Appropriate" → Based on what criteria?
- "Similar to X" → What aspects? Exactly like it?

### Missing Boundaries
- "Handle errors gracefully" → Which errors? How?
- "Support multiple users" → How many? Concurrent?
- "Scale as needed" → To what level?
- "Store user data" → How much? How long?

### Assumed Knowledge
- References to undefined terms
- Dependencies on unnamed systems
- Business rules without formulas
- Processes without steps

### Incomplete Flows
- Happy path only, no error handling
- Create operations without delete
- UI without loading/error states
- Workflows without exception paths
