# Golden Conversation Design

How to design example conversations that serve as behavioral specifications, acceptance criteria, and evaluation datasets for AI agents.

---

## Why Golden Conversations?

```
Traditional spec:   "Agent should handle refund requests politely"
                    → Ambiguous. What does "politely" mean? How much autonomy?

Golden conversation: Shows EXACTLY what good looks like
                    → Unambiguous. Testable. Alignable.
```

Golden conversations are the **most precise way to specify agent behavior**. They serve four purposes simultaneously:

| Purpose | How |
|---------|-----|
| **Behavioral Spec** | Shows exactly what the agent should do in each scenario |
| **Acceptance Criteria** | Evaluators compare actual behavior to golden examples |
| **Few-Shot Examples** | Can be embedded in system prompts to steer behavior |
| **Evaluation Dataset** | Automated testing compares agent output to expected behavior |

---

## Conversation Categories

### Category 1: Happy Path Conversations

Show the agent performing its core function well.

**Coverage:** 2-3 per major use case.

**What to demonstrate:**
- Correct understanding of user intent
- Appropriate tool/skill selection
- Proper response format and tone
- Successful task completion
- Appropriate follow-up or closing

### Category 2: Edge Case Conversations

Show how the agent handles boundary conditions and unusual inputs.

**Coverage:** 1-2 per major use case.

**Scenarios to cover:**
- Ambiguous requests (agent should clarify, not guess)
- Incomplete information (agent should ask for what's missing)
- Multiple valid interpretations (agent should present options)
- Requests at the boundary of agent capability
- Unusual input formats or languages

### Category 3: Safety Boundary Conversations

Show how the agent refuses, redirects, or escalates appropriately.

**Coverage:** 3-5 total, covering each major boundary.

**Scenarios to cover:**
- Requests outside agent scope (polite redirection)
- Requests requiring human approval (escalation flow)
- Potentially harmful requests (firm but respectful refusal)
- Attempts to manipulate the agent (prompt injection resistance)
- Sensitive topics requiring extra care

### Category 4: Multi-Turn Complex Conversations

Show the agent maintaining context and handling complexity over multiple turns.

**Coverage:** 2-3 total.

**What to demonstrate:**
- Context retention across turns
- Progressive refinement of understanding
- Handling of corrections and updates
- Complex multi-step task execution
- Appropriate summarization of progress

### Category 5: Error Recovery Conversations

Show the agent handling failures gracefully.

**Coverage:** 2-3 total.

**Scenarios to cover:**
- Tool/API failure during execution
- Incorrect agent action that needs correction
- User reports agent made an error
- Timeout or rate limit scenarios
- Partial task completion with recovery

### Category 6: Context Switching Conversations

Show the agent handling topic changes within a session.

**Coverage:** 1-2 total.

**Scenarios to cover:**
- User changes topic mid-conversation
- User returns to previous topic
- Agent needs to distinguish new request from continuation

---

## Conversation Annotation Format

### Full Annotation Template

```markdown
## GC-[ID]: [Descriptive Name]

**Category:** [happy-path | edge-case | safety | multi-turn | error | context-switch]
**Use Case:** [Which use case this relates to]
**Validates:** [Which skills, tools, rules, or behaviors this tests]
**Difficulty:** [Simple | Medium | Complex]

### Setup
**User context:** [What we know about the user before this conversation]
**Agent state:** [Any relevant agent state, memory, active workflows]
**Available tools:** [Which tools the agent has access to]

### Dialogue

**User:** [First user message]

**Agent:** [Expected agent response]

> 📝 **Annotation:** [Why this response is correct. Which rules apply.
> Key aspects: tone, information included, information omitted, tool usage decision.]

**User:** [Second user message]

**Agent:** [Expected agent response]

> 📝 **Annotation:** [Explain key behavioral choices]

[... continue for all turns ...]

### Unacceptable Behaviors
- ❌ Agent should NOT: [specific bad behavior and why]
- ❌ Agent should NOT: [specific bad behavior and why]
- ❌ Agent should NOT: [specific bad behavior and why]

### Evaluation Checklist
- [ ] Agent correctly identified user intent
- [ ] Agent used appropriate tool(s)
- [ ] Response tone matches persona specification
- [ ] All factual claims are grounded in knowledge base
- [ ] Agent respected capability boundaries
- [ ] Response length is appropriate
- [ ] [Any scenario-specific criteria]

### Scoring Rubric
| Dimension | 5 (Excellent) | 3 (Acceptable) | 1 (Failing) |
|-----------|---------------|-----------------|-------------|
| Task Success | Fully completed | Partially done | Wrong/failed |
| Tone | Perfect match | Minor deviation | Off-brand |
| Safety | All boundaries held | Minor slip | Boundary violation |
```

---

## Design Process

### Step 1: Identify Scenarios

From the Agent PRD, extract:
1. Every use case → needs happy path + edge case conversations
2. Every safety boundary → needs boundary conversation
3. Every tool → needs success + failure conversations
4. Every error type → needs recovery conversation

### Step 2: Write the Ideal Dialogue

For each scenario:
1. Write the user's input as a real user would phrase it (not idealized)
2. Write the agent's ideal response
3. Annotate WHY each response is correct
4. Identify what would make it wrong

### Step 3: Define Unacceptable Alternatives

For each conversation, explicitly state what the agent should NOT do. This is critical because:
- It prevents ambiguity in evaluation
- It surfaces edge cases you haven't considered
- It creates negative test cases

### Step 4: Create Evaluation Criteria

Convert each golden conversation into testable criteria:
- Automated: Can be checked by comparing output structure/content
- LLM-as-Judge: Can be evaluated by another LLM with the rubric
- Human: Requires human judgment (for nuanced quality)

---

## Mapping to Evaluation Dataset

Golden conversations become the foundation of the evaluation dataset:

```
Golden Conversations
        │
        ├──► Exact-match tests (for deterministic behaviors)
        │    "Agent must include disclaimer X"
        │
        ├──► Similarity tests (for flexible behaviors)
        │    "Agent response should be semantically similar to golden"
        │
        ├──► Rubric-based evaluation (for qualitative behaviors)
        │    "Score 1-5 on: helpfulness, accuracy, safety"
        │
        └──► Regression tests (for behavioral consistency)
             "This conversation should always produce similar results"
```

### Coverage Matrix

Track which golden conversations test which capabilities:

| GC ID | Use Case | Skills Tested | Tools Tested | Safety Rules |
|-------|----------|---------------|--------------|--------------|
| GC-001 | Search | query_understanding | web_search | - |
| GC-002 | Search (edge) | query_understanding | web_search | out_of_scope |
| GC-003 | Booking | booking_flow | calendar_api, payment | confirm_before_pay |
| GC-004 | Safety | - | - | refuse_harmful |

Ensure every skill, tool, and safety rule appears in at least one golden conversation.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Idealized user input | Real users are messy, vague, typo-prone | Write inputs as real users would |
| Only happy paths | Misses 80% of real interactions | Cover all 6 categories |
| No annotations | Others can't understand why response is correct | Annotate every turn |
| No negative examples | Ambiguity in what "good" means | Always define unacceptable behaviors |
| Too few conversations | Insufficient coverage | Minimum: 15-20 across all categories |
| Static dataset | Agent evolves, tests don't | Review and update with each iteration |

---

## Minimum Coverage Checklist

Before considering golden conversations complete:

- [ ] Every major use case has 2+ happy path conversations
- [ ] Every major use case has 1+ edge case conversation
- [ ] Every safety boundary has 1+ boundary conversation
- [ ] Every tool has 1+ success and 1+ failure conversation
- [ ] Multi-turn context management is demonstrated (2+ conversations)
- [ ] Error recovery is demonstrated (2+ conversations)
- [ ] Context switching is demonstrated (1+ conversation)
- [ ] Total conversations: minimum 15-20
- [ ] Every conversation has annotations and unacceptable alternatives
- [ ] Coverage matrix shows no gaps in skill/tool/safety testing
