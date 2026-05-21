# PRD Completeness Checklist

A systematic checklist to verify PRD completeness before engineering handoff.

## How to Use

1. Go through each item in order
2. Mark: ✅ Complete | ⚠️ Partial | ❌ Missing
3. For any ⚠️ or ❌: document what's missing and resolve before handoff
4. Aim for 100% ✅ on Critical items; 90%+ on Important items

---

## 1. Document Structure (Critical)

### 1.1 Basics
- [ ] Document has clear, descriptive title
- [ ] Version number present
- [ ] Author(s) identified
- [ ] Status clearly marked (Draft/Review/Approved)
- [ ] Last updated date current
- [ ] Revision history maintained

### 1.2 Stakeholder Alignment
- [ ] Approvers listed
- [ ] Approval status tracked
- [ ] Review comments addressed

---

## 2. Problem & Context (Critical)

### 2.1 Problem Statement
- [ ] Problem clearly articulated (not solution disguised as problem)
- [ ] Affected users identified
- [ ] Severity/impact quantified where possible
- [ ] Business value explained
- [ ] Current state described

### 2.2 Success Definition
- [ ] Success metrics defined (not just "improve" but specific targets)
- [ ] Baseline measurements provided (or noted as TBD with timeline)
- [ ] Measurement method specified
- [ ] Target timeline stated

---

## 3. Scope Definition (Critical)

### 3.1 In Scope
- [ ] All features/capabilities listed
- [ ] Priority clearly marked (P0/P1/P2 or MoSCoW)
- [ ] MVP explicitly defined
- [ ] Phase boundaries clear

### 3.2 Out of Scope
- [ ] Explicit "NOT doing" list present
- [ ] Reason for exclusion provided
- [ ] Future phase items clearly separated
- [ ] Related features that exist but aren't changing noted

---

## 4. Users & Personas (Critical)

### 4.1 User Identification
- [ ] All user types listed (including admin, support, etc.)
- [ ] Primary vs secondary distinguished
- [ ] Each persona has clear profile

### 4.2 Per Persona
For EACH user type, verify:
- [ ] Role/title defined
- [ ] Goals articulated
- [ ] Pain points documented
- [ ] Technical proficiency noted
- [ ] Usage frequency estimated
- [ ] Access level/permissions noted

---

## 5. User Stories (Critical)

### 5.1 Coverage
- [ ] All features have at least one user story
- [ ] Stories map to identified personas
- [ ] No orphan stories (unconnected to goals)

### 5.2 Story Quality
For EACH user story:
- [ ] Follows format: As a [role], I want [action], so that [benefit]
- [ ] Benefit explains value, not just restates action
- [ ] Appropriately sized (not epic-level)
- [ ] Dependencies noted

### 5.3 Acceptance Criteria Quality
For EACH user story's acceptance criteria:
- [ ] Criteria present (not missing)
- [ ] Written in Given/When/Then or clear conditional format
- [ ] Specific and testable (not vague)
- [ ] Covers happy path
- [ ] Covers negative/error cases
- [ ] Covers edge cases
- [ ] No ambiguous terms (see Ambiguity Checklist below)

---

## 6. Business Rules (Critical)

### 6.1 Rule Documentation
- [ ] All rules explicitly listed and numbered
- [ ] Rules stated precisely (not buried in prose)
- [ ] Rules traceable to user stories

### 6.2 Rule Completeness
For EACH business rule:
- [ ] Inputs specified
- [ ] Outputs specified
- [ ] All conditions/branches covered
- [ ] Boundary conditions defined
- [ ] Exceptions documented
- [ ] Examples provided

### 6.3 Calculations
For EACH calculation:
- [ ] Formula explicitly stated
- [ ] All variables defined
- [ ] Precision/rounding specified
- [ ] Edge cases (zero, negative, max) addressed

---

## 7. Data Requirements (Important)

### 7.1 Data Model
- [ ] All entities identified
- [ ] Key attributes listed
- [ ] Data types indicated
- [ ] Required vs optional noted
- [ ] Relationships documented

### 7.2 Data Fields
For EACH significant data field:
- [ ] Type specified
- [ ] Format/constraints specified
- [ ] Required or optional
- [ ] Default value if optional
- [ ] Validation rules
- [ ] Display format (if different from storage)

### 7.3 Data Lifecycle
- [ ] Creation process documented
- [ ] Update process documented
- [ ] Delete process documented (soft vs hard)
- [ ] Retention requirements stated
- [ ] Archival needs addressed

---

## 8. User Experience (Important)

### 8.1 Flows
- [ ] Primary user flows documented
- [ ] Alternative flows documented
- [ ] Error flows documented
- [ ] Entry and exit points clear

### 8.2 Visual Design
- [ ] Wireframes/mockups provided (or design reference)
- [ ] Key screens identified
- [ ] Navigation flow clear
- [ ] Brand/style guidelines referenced

### 8.3 Interaction Specs
- [ ] Form behaviors documented
- [ ] Validation behavior specified
- [ ] Loading states described
- [ ] Error display approach defined
- [ ] Empty states described
- [ ] Confirmation dialogs specified

### 8.4 Content & Messaging
- [ ] Error messages defined
- [ ] Success messages defined
- [ ] Help text defined
- [ ] Tone/voice consistent

---

## 9. Error Handling (Critical)

### 9.1 Error Identification
- [ ] User input errors listed
- [ ] System errors listed
- [ ] External dependency failures listed
- [ ] Timeout scenarios covered
- [ ] Concurrency issues considered

### 9.2 Error Handling
For EACH error type:
- [ ] User message specified
- [ ] Recovery path described
- [ ] Data preservation addressed
- [ ] Retry behavior (if applicable)
- [ ] Escalation path (if applicable)

---

## 10. State Management (Important)

### 10.1 State Identification
For entities with state:
- [ ] All states listed
- [ ] Initial state identified
- [ ] Terminal states identified

### 10.2 State Transitions
For EACH transition:
- [ ] Trigger defined (what causes it)
- [ ] Actor defined (who can do it)
- [ ] Conditions defined (what must be true)
- [ ] Side effects documented
- [ ] Invalid transitions noted

---

## 11. Permissions (Critical)

### 11.1 Role Definition
- [ ] All roles listed
- [ ] Role hierarchy clear
- [ ] Role assignment process documented

### 11.2 Permission Matrix
For EACH action:
- [ ] Who can perform it
- [ ] Who cannot
- [ ] What happens if unauthorized
- [ ] How permissions are checked

---

## 12. Non-Functional Requirements (Important)

### 12.1 Performance
- [ ] Response time requirements (with percentiles)
- [ ] Throughput requirements
- [ ] Concurrent user expectations

### 12.2 Scalability
- [ ] Expected scale stated
- [ ] Growth timeline provided
- [ ] Scale triggers defined

### 12.3 Availability
- [ ] Uptime requirement stated
- [ ] Maintenance windows defined
- [ ] DR requirements addressed

### 12.4 Security
- [ ] Authentication requirements
- [ ] Authorization requirements
- [ ] Encryption requirements
- [ ] Compliance requirements
- [ ] Audit requirements

### 12.5 Accessibility
- [ ] Accessibility standards stated (WCAG level)
- [ ] Specific considerations noted

### 12.6 Compatibility
- [ ] Browser support defined
- [ ] Device support defined
- [ ] API versioning addressed

---

## 13. Dependencies & Integrations (Important)

### 13.1 Dependencies
- [ ] All dependencies listed
- [ ] Owners identified
- [ ] Timeline impacts noted
- [ ] Risks assessed

### 13.2 Integrations
For EACH integration:
- [ ] System identified
- [ ] Purpose clear
- [ ] Data exchanged specified
- [ ] Method defined (API, file, etc.)
- [ ] Failure handling documented
- [ ] Owner/contact provided

---

## 14. Timeline & Plan (Important)

### 14.1 Schedule
- [ ] Target dates provided
- [ ] Milestones defined
- [ ] Dependencies impact noted
- [ ] Buffer/contingency considered

### 14.2 Phasing
- [ ] Phases clearly defined
- [ ] Phase criteria specified
- [ ] What's in each phase explicit

---

## 15. Risks & Unknowns (Important)

### 15.1 Risks
- [ ] Risks identified
- [ ] Probability assessed
- [ ] Impact assessed
- [ ] Mitigation planned
- [ ] Owners assigned

### 15.2 Assumptions
- [ ] Assumptions explicitly stated
- [ ] Impact if wrong noted
- [ ] Validation plan where possible

### 15.3 Open Questions
- [ ] Questions listed
- [ ] Owners assigned
- [ ] Due dates set
- [ ] Status tracked

---

## Ambiguity Checklist

Search your PRD for these red-flag terms and replace with specifics:

### Vague Adjectives
| Term | Problem | Fix |
|------|---------|-----|
| "Fast" | How fast? | "< 200ms at P95" |
| "Secure" | What security? | "OAuth 2.0, encrypted at rest (AES-256)" |
| "User-friendly" | Subjective | "Task completion in < 2 min without help" |
| "Easy" | Subjective | "< 3 clicks from homepage" |
| "Simple" | Subjective | Describe exact UI/flow |
| "Appropriate" | Based on what? | Define criteria |
| "Reasonable" | Who decides? | Define threshold |
| "Flexible" | How flexible? | List specific variations supported |
| "Modern" | Compared to what? | Cite specific standards/patterns |
| "Clean" | Subjective | Define specific design constraints |

### Vague Quantities
| Term | Problem | Fix |
|------|---------|-----|
| "Many" | How many? | "Up to 1,000" |
| "Some" | How many? | "3-5 items" |
| "Large" | How large? | "10MB max" |
| "Several" | How many? | Specific number or range |
| "Multiple" | How many? | "2 or more" or specific limit |
| "Frequently" | How often? | "More than 10x per day" |
| "Quickly" | How quick? | "Within 5 seconds" |
| "Soon" | When? | Specific date/milestone |

### Vague Actions
| Term | Problem | Fix |
|------|---------|-----|
| "Handle" | How exactly? | Describe specific handling |
| "Process" | What processing? | Step-by-step description |
| "Support" | What support? | List specific capabilities |
| "Manage" | What management? | List specific actions |
| "Integrate" | How? | Describe integration method |

### Passive Voice & Ambiguous Subjects
| Term | Problem | Fix |
|------|---------|-----|
| "Should be shown" | By whom? To whom? | "System displays X to user" |
| "Will be handled" | By what? How? | "API returns error code 400" |
| "Is validated" | By what? When? | "Client validates before submit" |

---

## Pre-Handoff Final Check

### Content Quality
- [ ] No placeholder text remaining ([TBD], [TODO])
- [ ] All cross-references valid
- [ ] Terminology consistent throughout
- [ ] Glossary covers all domain terms

### Stakeholder Sign-off
- [ ] Product/business stakeholders approved
- [ ] Design stakeholders approved (if applicable)
- [ ] Engineering has reviewed and confirms understanding
- [ ] Questions from review have been answered and incorporated

### Testability
- [ ] QA can write test cases from acceptance criteria
- [ ] All requirements are verifiable
- [ ] Success criteria are measurable

---

## Scoring Guide

| Section | Weight | Score |
|---------|--------|-------|
| 1. Document Structure | 5% | /100 |
| 2. Problem & Context | 10% | /100 |
| 3. Scope Definition | 10% | /100 |
| 4. Users & Personas | 10% | /100 |
| 5. User Stories | 15% | /100 |
| 6. Business Rules | 15% | /100 |
| 7. Data Requirements | 5% | /100 |
| 8. User Experience | 5% | /100 |
| 9. Error Handling | 10% | /100 |
| 10. State Management | 5% | /100 |
| 11. Permissions | 5% | /100 |
| 12. Non-Functional | 5% | /100 |
| **TOTAL** | 100% | /100 |

**Minimum for handoff:** 90% overall, 100% on Critical sections
