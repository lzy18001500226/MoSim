# Requirement Prioritization & Management

How to prioritize requirements and manage them through the product lifecycle.

---

## Part 1: Prioritization Frameworks

### Framework 1: MoSCoW Method

| Priority | Meaning | Definition | Percentage |
|----------|---------|------------|------------|
| **M**ust Have | Critical | Without this, the product doesn't work. Launch blocker. | ~60% |
| **S**hould Have | Important | Significant value, but workarounds exist. Include if possible. | ~20% |
| **C**ould Have | Desirable | Nice to have. Include only if time allows. | ~20% |
| **W**on't Have | Out of scope | Explicitly not in this release. May be future. | Documented |

**Usage:**
- Start by identifying Must Haves (what's truly critical?)
- Everything else defaults to Could Have
- Promote to Should Have only with justification
- Explicitly list Won't Haves to prevent scope creep

### Framework 2: Impact vs Effort Matrix

```
        High Impact
             │
             │  Quick Wins    │   Big Bets
             │  (Do First)    │   (Plan Carefully)
             │                │
Low Effort───┼────────────────┼───High Effort
             │                │
             │  Fill-ins      │   Money Pits
             │  (Do If Time)  │   (Avoid)
             │
        Low Impact
```

**How to use:**
1. Plot each requirement on the matrix
2. Prioritize: Quick Wins → Big Bets → Fill-ins
3. Challenge anything in Money Pits quadrant

### Framework 3: RICE Scoring

| Factor | Definition | Scale |
|--------|------------|-------|
| **R**each | How many users affected per time period | Actual number |
| **I**mpact | How much it moves the needle per user | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| **C**onfidence | How sure are we about estimates | 100%=high, 80%=medium, 50%=low |
| **E**ffort | Person-months to complete | Actual estimate |

**Formula:** RICE Score = (Reach × Impact × Confidence) / Effort

**Example:**
| Feature | Reach | Impact | Confidence | Effort | Score |
|---------|-------|--------|------------|--------|-------|
| Feature A | 10,000 | 2 | 80% | 3 | 5,333 |
| Feature B | 5,000 | 3 | 50% | 1 | 7,500 |
| Feature C | 50,000 | 0.5 | 100% | 6 | 4,167 |

→ Prioritize: B, then A, then C

### Framework 4: Kano Model

Categorize features by how they affect satisfaction:

| Category | If Present | If Absent | Strategy |
|----------|------------|-----------|----------|
| **Basic** (Must-be) | Neutral | Very dissatisfied | Must have all |
| **Performance** (One-dimensional) | Satisfied | Dissatisfied | More is better |
| **Delighter** (Attractive) | Very satisfied | Neutral | Differentiate |
| **Indifferent** | Neutral | Neutral | Skip |
| **Reverse** | Dissatisfied | Satisfied | Avoid |

**How to identify:**
1. Ask: "How would you feel if this feature is present?"
2. Ask: "How would you feel if this feature is absent?"
3. Map responses to category

---

## Part 2: Priority Negotiation

### When Stakeholders Disagree

**Step 1: Understand each perspective**
- What problem does each stakeholder think we're solving?
- What does success look like to each?
- What constraints does each have?

**Step 2: Find common ground**
- What do all parties agree is important?
- What's the shared goal?

**Step 3: Use data**
- User research
- Analytics
- Market data
- Cost estimates

**Step 4: Make tradeoffs explicit**
- "If we do X, we can't do Y in this release"
- "Feature A affects 10x more users than Feature B"
- "Delaying X costs $Y per month"

**Step 5: Escalate if needed**
- Document the disagreement
- Present options with tradeoffs
- Let appropriate decision-maker decide

### Priority Negotiation Template

```markdown
## Priority Discussion: [Feature/Requirement]

### Current Priority: [Current]
### Requested Priority: [Requested]

### Arguments For Higher Priority:
- [Argument 1]
- [Argument 2]

### Arguments Against Higher Priority:
- [Argument 1]
- [Argument 2]

### Data:
- User impact: [number]
- Business impact: [metric]
- Effort: [estimate]

### Tradeoff:
If we prioritize this higher, we would need to deprioritize:
- [Item 1]
- [Item 2]

### Recommendation:
[Recommendation with rationale]

### Decision:
[Decision made by whom on what date]
```

---

## Part 3: Requirements Change Management

### Change Request Process

```
┌─────────────────┐
│ Change Request  │
│ Submitted       │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Impact Analysis │ ← Effort, timeline, dependencies
└────────┬────────┘
         ↓
┌─────────────────┐
│ Review Meeting  │ ← PM, Eng Lead, Stakeholders
└────────┬────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌───────┐ ┌───────┐
│Approve│ │Reject │
└───┬───┘ └───┬───┘
    ↓         ↓
┌───────┐ ┌───────┐
│Update │ │Document│
│PRD    │ │Decision│
└───────┘ └───────┘
```

### Change Request Template

```markdown
## Change Request: [ID]

**Requested by:** [Name]
**Date:** [Date]
**Priority:** Critical / High / Medium / Low

### Current Requirement
[What the PRD currently says]

### Proposed Change
[What the requestor wants it to say]

### Reason for Change
[Why this change is needed]

### Impact Analysis

| Area | Impact |
|------|--------|
| Scope | [Increase/decrease/no change] |
| Timeline | [Days/weeks added or removed] |
| Effort | [Additional hours/sprints] |
| Dependencies | [Affected items] |
| Risk | [New risks introduced] |

### Recommendation
[Accept / Reject / Defer / Modify]

### Decision
| Decision | [Accept/Reject] |
| Made by | [Name] |
| Date | [Date] |
| Rationale | [Why] |
```

### When to Accept vs Reject Changes

**Accept when:**
- Critical bug or gap discovered
- User research reveals major issue
- Business priority genuinely shifted
- Regulatory/legal requirement

**Reject when:**
- "Nice to have" disguised as critical
- Scope creep without priority tradeoff
- Too late in development cycle
- Insufficient justification

**Defer when:**
- Valid but not urgent
- Better suited for next release
- Needs more research

### PRD Versioning

**When to version:**
- Any change to requirements (not just typos)
- Addition or removal of features
- Change to scope or priority

**Version format:** Major.Minor
- Major: Significant scope change
- Minor: Clarifications or small additions

**Version log entry:**

```markdown
| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0 | [date] | [name] | Initial approved version |
| 1.1 | [date] | [name] | Added error handling for X |
| 2.0 | [date] | [name] | Removed feature Y, added feature Z |
```

---

## Part 4: Cross-Team Collaboration

### Working with Design

**Input to Design:**
- Problem statement (not solution)
- User personas
- User goals and tasks
- Constraints (technical, business)
- Success metrics

**Collaboration points:**
- Design review: Is it feasible? Does it meet requirements?
- Edge cases: Have we covered all states?
- Handoff: Are specs complete for implementation?

**Common issues:**
| Issue | Solution |
|-------|----------|
| Design too early | Wait for requirements to stabilize |
| PM dictating UI | Describe problems, let design solve |
| Missing states | Review empty/loading/error explicitly |

### Working with Engineering

**Input to Engineering:**
- Complete requirements (not partial)
- Clear priorities
- Dependencies identified
- Success criteria defined

**Collaboration points:**
- Feasibility review: Is it buildable?
- Effort estimation: How long?
- Technical design: What's the approach?
- Trade-off discussions: Scope vs timeline

**Common issues:**
| Issue | Solution |
|-------|----------|
| Requirements incomplete | Use completeness checklist |
| Questions during dev | Track and add to PRD |
| Scope creep | Formal change request process |

### Working with QA

**Input to QA:**
- Testable acceptance criteria
- Edge cases documented
- Error handling specified
- Test data requirements

**Collaboration points:**
- Test plan review: Coverage complete?
- Bug triage: Is this a bug or unclear requirement?
- Release criteria: What must pass?

---

## Part 5: Internationalization Requirements

### Checklist for International Products

#### Text & Language
- [ ] Languages to support listed
- [ ] Text expansion/contraction accounted for (German 30% longer, Chinese 50% shorter)
- [ ] Right-to-left (RTL) support if needed
- [ ] Character set requirements
- [ ] Translation process defined

#### Formatting
- [ ] Date formats per locale
- [ ] Time formats (12h vs 24h)
- [ ] Number formats (decimal: . vs ,)
- [ ] Currency formats
- [ ] Address formats
- [ ] Phone number formats

#### Cultural
- [ ] Color meanings considered
- [ ] Icons reviewed for cultural sensitivity
- [ ] Images reviewed for cultural sensitivity
- [ ] Names and titles handled properly

#### Technical
- [ ] Unicode support
- [ ] Timezone handling
- [ ] Multi-byte character support
- [ ] Sorting/collation rules

### I18n Requirements Template

```markdown
### Internationalization Requirements

**Supported Languages:** [List]
**Primary/Default:** [Language]

**Locale-Specific Behavior:**
| Element | US (en-US) | UK (en-GB) | Germany (de-DE) | Japan (ja-JP) |
|---------|------------|------------|-----------------|---------------|
| Date | MM/DD/YYYY | DD/MM/YYYY | DD.MM.YYYY | YYYY/MM/DD |
| Time | 12h | 24h | 24h | 24h |
| Currency | $X,XXX.XX | £X,XXX.XX | X.XXX,XX € | ¥X,XXX |

**Translation Process:**
- Who translates: [Team/vendor]
- Review process: [Steps]
- Launch criteria: [All languages must be complete before launch? or phased?]
```

---

## Part 6: Compliance & Legal Requirements

### Common Compliance Frameworks

| Framework | Applies To | Key Requirements |
|-----------|------------|------------------|
| **GDPR** | EU users' personal data | Consent, right to deletion, data portability |
| **CCPA** | California residents' data | Disclosure, opt-out, deletion rights |
| **HIPAA** | Health information | Encryption, access controls, audit trails |
| **PCI-DSS** | Payment card data | Secure storage, encryption, access limits |
| **SOC 2** | Service organizations | Security, availability, confidentiality |
| **Accessibility** | Public-facing web | WCAG compliance |

### Compliance Requirements Checklist

#### Privacy (GDPR/CCPA)
- [ ] Data collection disclosed and justified
- [ ] Consent mechanism defined
- [ ] Opt-out mechanism defined
- [ ] Data export capability (portability)
- [ ] Data deletion capability
- [ ] Data retention policy documented
- [ ] Third-party data sharing disclosed

#### Security
- [ ] Authentication requirements defined
- [ ] Authorization model documented
- [ ] Encryption requirements specified
- [ ] Audit logging requirements
- [ ] Incident response plan referenced

#### Accessibility
- [ ] WCAG level specified (A, AA, AAA)
- [ ] Screen reader compatibility
- [ ] Keyboard navigation
- [ ] Color contrast requirements
- [ ] Text alternatives for images

### Compliance Requirements Template

```markdown
### Compliance Requirements

**Applicable Regulations:**
- [ ] GDPR (EU users)
- [ ] CCPA (California residents)
- [ ] HIPAA (health data)
- [ ] PCI-DSS (payment data)
- [ ] Other: [specify]

**Privacy Requirements:**
| Requirement | Implementation | Verification |
|-------------|----------------|--------------|
| Consent collection | [How] | [How verified] |
| Data deletion | [How] | [How verified] |
| Data export | [How] | [How verified] |

**Security Requirements:**
| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Data encryption (transit) | TLS 1.2+ | [How] |
| Data encryption (rest) | AES-256 | [How] |
| Access logging | [Retention] | [System] |

**Accessibility Requirements:**
| Standard | Level | Testing Method |
|----------|-------|----------------|
| WCAG | 2.1 AA | [Tool/process] |

**Legal Review:**
- [ ] Legal has reviewed privacy implications
- [ ] Terms of service updated if needed
- [ ] Privacy policy updated if needed
```
