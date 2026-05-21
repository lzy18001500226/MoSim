# Skills Specification Guide

How to define agent skills—reusable capability modules that enable specific agent behaviors.

---

## What is a Skill?

A **Skill** is a modular, reusable capability that an agent can invoke to accomplish a specific type of task.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Skill Anatomy                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   TRIGGER ──► When should this skill activate?                  │
│                                                                 │
│   INPUT ────► What information does it need?                    │
│                                                                 │
│   PROCESS ──► What steps does it take?                          │
│                                                                 │
│   OUTPUT ───► What does it produce?                             │
│                                                                 │
│   BOUNDS ───► What can't it do?                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Skill vs Tool

| Aspect | Skill | Tool |
|--------|-------|------|
| **Nature** | Internal capability | External action |
| **Location** | Within agent | Outside agent |
| **Control** | Agent logic | API/function call |
| **Example** | "Summarize text" | "Send email" |
| **Composition** | Can use tools | Is used by skills |

---

## Skill Specification Template

### Skill: [Name]

```markdown
## Skill: [Descriptive Name]

### 1. Purpose

**What:** [One sentence describing what this skill does]

**Why:** [Business value this skill provides]

**When:** [Situations where this skill should activate]

### 2. Trigger Conditions

#### Intent Patterns
The skill activates when user intent matches these patterns:

| Pattern | Example | Confidence Required |
|---------|---------|---------------------|
| [Pattern description] | "[Example user input]" | [High/Medium/Low] |

#### Context Requirements
Additional conditions that must be true:

| Condition | Check | Required |
|-----------|-------|----------|
| [Condition] | [How to verify] | [Yes/No] |

#### Negative Conditions
The skill should NOT activate when:

| Anti-pattern | Why Excluded |
|--------------|--------------|
| [Pattern] | [Reason] |

### 3. Input Specification

| Parameter | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| [param] | [type] | [Y/N] | [default] | [rules] | [description] |

#### Input Examples

**Valid Inputs:**
```json
{
  "param1": "valid value",
  "param2": 123
}
```

**Invalid Inputs:**
```json
{
  "param1": "",  // Empty not allowed
  "param2": -1   // Must be positive
}
```

### 4. Process Logic

#### High-Level Flow
```
1. Validate inputs
2. [Step 2]
3. [Step 3]
4. [Step N]
5. Format and return output
```

#### Detailed Logic
```pseudocode
function skill_name(inputs):
    // Step 1: Validate
    if not validate(inputs):
        return error("Invalid input")
    
    // Step 2: Main processing
    result = process(inputs)
    
    // Step 3: Post-process
    formatted = format(result)
    
    return formatted
```

#### Decision Points

| Decision | Options | Selection Criteria |
|----------|---------|-------------------|
| [Decision point] | [Options] | [How to choose] |

### 5. Output Specification

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| [field] | [type] | [Y/N] | [description] |

#### Output Format
```json
{
  "status": "success|error",
  "result": {
    "field1": "value",
    "field2": 123
  },
  "metadata": {
    "confidence": 0.95,
    "source": "..."
  }
}
```

### 6. Dependencies

#### Tools Required
| Tool | Usage | Required |
|------|-------|----------|
| [Tool] | [How used] | [Y/N] |

#### Knowledge Required
| Knowledge Source | Usage | Required |
|------------------|-------|----------|
| [Source] | [How used] | [Y/N] |

#### Other Skills
| Skill | Relationship |
|-------|--------------|
| [Skill] | [How related] |

### 7. Examples

#### Example 1: [Scenario Name]

**Input:**
```json
{
  "param1": "example value"
}
```

**Process Trace:**
```
1. Received input: param1="example value"
2. Validated: OK
3. Processing: [description]
4. Result: [description]
```

**Output:**
```json
{
  "status": "success",
  "result": {
    "output1": "result value"
  }
}
```

#### Example 2: [Edge Case]
[Similar structure]

### 8. Boundaries & Limitations

#### Cannot Do
| Limitation | Reason | Alternative |
|------------|--------|-------------|
| [What it can't do] | [Why] | [What to do instead] |

#### Edge Cases
| Edge Case | Handling |
|-----------|----------|
| [Case] | [How handled] |

#### Error Conditions
| Error | Trigger | Response |
|-------|---------|----------|
| [Error type] | [When it occurs] | [How to handle] |

### 9. Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Accuracy | [%] | [How measured] |
| Latency | [ms] | [How measured] |
| Success rate | [%] | [How measured] |

### 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| [X.Y] | [Date] | [What changed] |
```

---

## Skill Categories

### Information Skills
Skills that retrieve, synthesize, or transform information.

| Skill Type | Purpose | Example |
|------------|---------|---------|
| Search | Find relevant information | "Search knowledge base" |
| Summarize | Condense content | "Summarize document" |
| Extract | Pull specific data | "Extract entities" |
| Translate | Convert formats/languages | "Translate to Spanish" |
| Explain | Make concepts understandable | "Explain in simple terms" |

### Action Skills
Skills that trigger actions or modify state.

| Skill Type | Purpose | Example |
|------------|---------|---------|
| Create | Make something new | "Draft email" |
| Update | Modify existing | "Edit document" |
| Execute | Run a process | "Run analysis" |
| Schedule | Plan future action | "Set reminder" |
| Notify | Send information | "Send notification" |

### Reasoning Skills
Skills that analyze, decide, or plan.

| Skill Type | Purpose | Example |
|------------|---------|---------|
| Analyze | Examine and interpret | "Analyze trends" |
| Compare | Evaluate options | "Compare products" |
| Recommend | Suggest best option | "Recommend next steps" |
| Plan | Create action sequence | "Plan project" |
| Diagnose | Identify problems | "Troubleshoot issue" |

### Conversation Skills
Skills that manage dialogue.

| Skill Type | Purpose | Example |
|------------|---------|---------|
| Clarify | Resolve ambiguity | "Ask clarifying question" |
| Confirm | Verify understanding | "Confirm action" |
| Redirect | Change topic appropriately | "Redirect to scope" |
| Handoff | Transfer to human | "Escalate to support" |

---

## Skill Composition Patterns

### Sequential Composition
Skills that run one after another:

```
Skill A ──► Skill B ──► Skill C ──► Result
```

**Example:** Search → Summarize → Format

### Conditional Composition
Skills chosen based on conditions:

```
        ┌─► Skill A (if condition X)
Input ──┼─► Skill B (if condition Y)
        └─► Skill C (else)
```

**Example:** Simple question → Direct answer; Complex question → Research then answer

### Parallel Composition
Skills that run simultaneously:

```
        ┌─► Skill A ──┐
Input ──┤             ├──► Combine ──► Result
        └─► Skill B ──┘
```

**Example:** Search multiple sources in parallel, combine results

### Iterative Composition
Skills that repeat until done:

```
Input ──► Skill ──► Check ──► Done?
              ↑              │
              └──── No ──────┘
```

**Example:** Refine answer until quality threshold met

---

## Skill Design Best Practices

### 1. Single Responsibility
Each skill should do one thing well.

❌ **Bad:** "HandleUserRequest" (too broad)
✅ **Good:** "SearchKnowledgeBase", "SummarizeText", "FormatAsTable"

### 2. Clear Boundaries
Define what the skill can't do.

❌ **Bad:** "This skill helps with documents"
✅ **Good:** "This skill extracts text from PDFs up to 50 pages. Does not handle scanned images."

### 3. Explicit Dependencies
Document all required tools, knowledge, and other skills.

### 4. Rich Examples
Provide multiple input/output examples covering:
- Happy path
- Edge cases
- Error cases

### 5. Measurable Quality
Define specific metrics that can be evaluated.

### 6. Version Control
Track changes over time with clear version history.

---

## Skill Testing Checklist

### Functional Testing
- [ ] Happy path works correctly
- [ ] All input validations work
- [ ] All error conditions handled
- [ ] Output format is correct

### Edge Case Testing
- [ ] Empty input
- [ ] Maximum input size
- [ ] Invalid input types
- [ ] Missing optional parameters

### Integration Testing
- [ ] Tool dependencies work
- [ ] Knowledge retrieval works
- [ ] Skill composition works

### Quality Testing
- [ ] Meets accuracy target
- [ ] Meets latency target
- [ ] Consistent behavior

---

## Skill Documentation Checklist

Before finalizing a skill specification:

- [ ] Purpose is clear and specific
- [ ] Trigger conditions are unambiguous
- [ ] All inputs are documented with validation
- [ ] Process logic is complete
- [ ] Output format is specified
- [ ] Dependencies are listed
- [ ] Examples cover key scenarios
- [ ] Boundaries are explicit
- [ ] Metrics are defined
- [ ] Version is tracked
