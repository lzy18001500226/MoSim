# Discovery Questions

A comprehensive question bank for requirement discovery. Use these questions in stakeholder interviews, user research sessions, and self-review to ensure no requirement is missed.

## How to Use This Document

1. Select relevant sections based on your project
2. Ask these questions during discovery
3. Document answers directly—they become your PRD content
4. Flag questions that can't be answered—these are risks

---

## 1. Problem & Opportunity Questions

### Problem Definition
- What specific problem are we solving?
- Who experiences this problem?
- How frequently do they experience it?
- How severe is the impact? (Time lost? Money lost? Frustration?)
- What triggers the problem?

### Current State
- How do users solve this problem today?
- What tools/workarounds do they use?
- What's painful about current solutions?
- What works well that we should preserve?
- Who else has tried to solve this? What happened?

### Business Value
- Why solve this now? What's the driver?
- What's the cost of NOT solving this?
- What business metric will this improve?
- How much improvement do we expect?
- What's the ROI calculation?

### Success Definition
- How will we know we've succeeded?
- What metric will we measure?
- What's the target value?
- What's the timeline to see results?
- What's the minimum acceptable outcome?

---

## 2. User Questions

### User Identification
- Who are ALL the users of this feature?
- Who's the primary user? Who's secondary?
- Are there internal users? (Admin, support, ops)
- Are there system users? (APIs, integrations)
- Who are NOT users? (Explicitly exclude)

### For Each User Type

#### Demographics & Context
- What's their role/job title?
- What's their technical proficiency?
- What devices do they use?
- What environment? (Office, mobile, noisy, rushed?)
- What time of day do they use this?

#### Goals & Motivations
- What's their ultimate goal?
- What are they trying to accomplish?
- What motivates them?
- What frustrates them?
- What would delight them?

#### Behavior
- How often will they use this?
- How long do they spend on this task?
- What's their attention span?
- Do they multitask?
- Are they experts or casual users?

#### Constraints
- What limitations do they have?
- What permissions do they have?
- What training will they have?
- What support is available to them?

---

## 3. Functional Requirement Questions

### Core Functionality
- What must the system do? (List every action)
- What's the primary user flow?
- What are alternative flows?
- What's the minimum viable version?
- What's the ideal full version?

### Scope Boundaries
- What is explicitly OUT of scope?
- What's deferred to future phases?
- What existing functionality is affected?
- What will we NOT change?
- What integrations are NOT included?

### For Each Feature/Function

#### Input Questions
- What data does the user provide?
- What format? What constraints?
- What's required vs optional?
- What are valid values?
- What are invalid values?
- What's the default if not provided?

#### Processing Questions
- What happens to the input?
- What business logic applies?
- What calculations are performed?
- What conditions/branches exist?
- What external systems are called?

#### Output Questions
- What does the user see/receive?
- What format is the output?
- Where is output stored?
- Who else is notified?
- What side effects occur?

---

## 4. Business Rule Questions

### Rule Identification
- What rules govern this process?
- What regulations apply?
- What policies must be followed?
- What calculations are required?
- What validations are needed?

### For Each Business Rule

#### Definition
- What is the rule in plain language?
- What triggers the rule?
- What's the formula/logic?
- What are the inputs?
- What's the output?

#### Boundaries
- What's the minimum value?
- What's the maximum value?
- What happens at boundaries?
- What precision/rounding applies?
- What timezone applies?

#### Exceptions
- Are there exceptions to this rule?
- Who can override the rule?
- How is override tracked?
- What approvals are needed?

---

## 5. Data Questions

### Data Identification
- What data entities are involved?
- What are the key attributes?
- What are the relationships?
- What's the data source?
- Who owns this data?

### For Each Data Element

#### Definition
- What does this data represent?
- What type is it? (String, number, date, etc.)
- What format? (Pattern, length, range)
- Is it required?
- What's the default?

#### Lifecycle
- How is it created?
- How is it updated?
- Can it be deleted?
- How long is it retained?
- Is it archived?

#### Access
- Who can view it?
- Who can modify it?
- Is it sensitive/PII?
- Is it encrypted?
- Is it audited?

#### Quality
- What validation applies?
- Can it be null/empty?
- Can it contain duplicates?
- How is it cleaned?
- What's the source of truth?

---

## 6. User Experience Questions

### Navigation
- How does the user get here?
- Where can they go from here?
- Can they go back?
- Is there a "home" state?
- How do they exit?

### Visual Design
- What existing patterns should we follow?
- What brand guidelines apply?
- What visual hierarchy is needed?
- What density is appropriate?
- What colors/icons are meaningful?

### Interaction
- What actions are available?
- What gestures are supported?
- What keyboard shortcuts?
- What's the tab order?
- What's the focus behavior?

### Feedback
- How does the user know it worked?
- How do they know it's loading?
- How do they know there's an error?
- Are there confirmations?
- Are there undo options?

### States
- What does empty state look like?
- What does loading state look like?
- What does error state look like?
- What does success state look like?
- What does partial state look like?

### Accessibility
- What accessibility standards apply?
- How is screen reader support handled?
- What's the color contrast requirement?
- What's the font size range?
- Are there motion sensitivities?

---

## 7. Error & Exception Questions

### Error Identification
- What can the user do wrong?
- What can the system do wrong?
- What can external systems do wrong?
- What timing issues can occur?
- What resource issues can occur?

### For Each Error

#### Detection
- How is the error detected?
- When is it detected? (Client, server, async?)
- What information is available?

#### User Experience
- What does the user see?
- What message is displayed?
- Is the error recoverable?
- What action should user take?
- Is help available?

#### System Response
- Is the error logged?
- Is anyone alerted?
- Is it retried automatically?
- What cleanup is needed?
- What data is preserved?

#### Recovery
- How does user recover?
- Is there a fallback?
- What's the retry strategy?
- Is data saved for later?
- Who can help?

---

## 8. State & Workflow Questions

### State Identification
- What states can this entity be in?
- What's the initial state?
- What are the terminal states?
- How many concurrent states are possible?

### For Each State Transition

#### Trigger
- What triggers this transition?
- Who can trigger it?
- What conditions must be met?
- What data is required?

#### Action
- What happens during transition?
- What side effects occur?
- What notifications are sent?
- What is recorded/logged?

#### Guard
- What prevents invalid transitions?
- What error occurs if invalid?
- Can transitions be reversed?

---

## 9. Permission & Security Questions

### Authentication
- How do users authenticate?
- What credentials are required?
- What's the session duration?
- How is "remember me" handled?
- How is password reset handled?

### Authorization
- What roles exist?
- What can each role do?
- How are roles assigned?
- Can roles be customized?
- How is access revoked?

### For Each Protected Action
- Who can perform this action?
- What happens if unauthorized?
- Is there a request access flow?
- Is access logged?

### Data Security
- What data is sensitive?
- How is it protected in transit?
- How is it protected at rest?
- Who can access it?
- Is access logged?

### Compliance
- What regulations apply? (GDPR, HIPAA, SOC2, etc.)
- What audit requirements exist?
- What retention policies apply?
- What deletion rights exist?

---

## 10. Performance Questions

### Response Time
- What's acceptable response time?
- What's for different operations?
- What percentile? (P50, P95, P99)
- What happens if exceeded?

### Throughput
- How many users concurrently?
- How many requests per second?
- What's the peak load?
- What's typical load?

### Data Volume
- How much data now?
- How much in 1 year?
- How fast does it grow?
- What's the query performance at scale?

### Resource Usage
- What's the memory budget?
- What's the CPU budget?
- What's the storage budget?
- What's the bandwidth budget?

---

## 11. Integration Questions

### For Each Integration

#### System Information
- What system are we integrating with?
- Who owns it?
- What's their SLA?
- Who's the contact?
- What's the documentation?

#### Data Exchange
- What data do we send?
- What data do we receive?
- What format?
- What frequency?
- What volume?

#### Connection
- How do we connect? (API, file, queue, etc.)
- How do we authenticate?
- What's the endpoint?
- What's the rate limit?
- Is there a sandbox?

#### Failure Handling
- What if it's unavailable?
- What's the retry strategy?
- Is there a fallback?
- How do we detect issues?
- Who do we notify?

#### Cost & Limits
- Is there per-call pricing? What's the cost model?
- Are there rate limits? What are the quotas?
- What happens when limits are hit? (Queue? Reject? Degrade?)
- Do costs scale linearly or are there tier breaks?
- Are there bandwidth or data transfer charges?

#### Versioning & Compatibility
- What API version are we integrating with?
- How does the vendor handle breaking changes?
- What's the deprecation notice period?
- Do we need to support multiple versions simultaneously?

#### Security & Compliance
- What authentication method? (API key, OAuth, mTLS?)
- How are credentials stored and rotated?
- Does the integration handle PII? If so, what data residency requirements?
- Does the vendor have SOC2/ISO27001/relevant certifications?
- Are there contractual data handling obligations?

#### Testing & Environments
- Is there a sandbox/staging environment?
- Does the sandbox fully mirror production behavior?
- How do we test failure scenarios?
- What test data is available?

---

## 12. Timeline & Priority Questions

### Timeline
- When must this launch?
- Why that date?
- What's driving the deadline?
- What happens if we miss it?
- Is the date flexible?

### Priority
- What's the priority vs other projects?
- What's P0 vs P1 vs P2?
- What can be cut if needed?
- What absolutely cannot be cut?
- Who decides priority disputes?

### Phases
- Can this be phased?
- What's the MVP?
- What's Phase 2?
- What's the long-term vision?
- What gates between phases?

---

## 13. Risk & Assumption Questions

### Assumptions
- What are we assuming is true?
- What if each assumption is wrong?
- How can we validate assumptions?
- What assumptions are risky?

### Dependencies
- What do we depend on?
- Who do we depend on?
- What's the risk of each dependency?
- What's our contingency?

### Risks
- What could go wrong?
- What's the probability?
- What's the impact?
- What's our mitigation?
- Who owns each risk?

### Unknowns
- What don't we know yet?
- When will we know?
- Who's finding out?
- What do we do until then?

---

## Question Asking Tips

### Good Question Patterns
- "What happens if...?" (Edge cases)
- "What about when...?" (States)
- "Who can...?" (Permissions)
- "How does the user know...?" (Feedback)
- "What if this fails...?" (Errors)
- "How many...?" (Quantities)
- "How often...?" (Frequency)
- "How long...?" (Duration)

### Red Flag Answers
- "It depends" → On what exactly?
- "Usually" → What about unusually?
- "We'll figure it out" → When? This is a risk.
- "That won't happen" → But if it does?
- "The user will know" → How exactly?
- "It's obvious" → To whom?

### Follow-Up Techniques
- "Can you give me an example?"
- "What would happen if that's wrong?"
- "Who else should I ask about this?"
- "Is there documentation I can review?"
- "Has this been done before?"
