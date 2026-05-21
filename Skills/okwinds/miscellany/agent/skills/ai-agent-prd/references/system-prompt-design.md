# System Prompt Design Guide

The system prompt is the agent's "soul" — it defines the agent's identity, capabilities, behavioral boundaries, and reasoning approach.

---

## The Role of the System Prompt

```
┌─────────────────────────────────────────────────────────────────┐
│                    System Prompt = Agent DNA                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Identity: Who am I? What is my role?                          │
│      ↓                                                         │
│   Capabilities: What can I do? What tools do I have?            │
│      ↓                                                         │
│   Behavior: How should I think and act?                         │
│      ↓                                                         │
│   Boundaries: What can't I do? When should I seek help?         │
│      ↓                                                         │
│   Style: How do I express myself? What tone and format?         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Prompt Structure Template

### Base Structure

```markdown
# [Agent Name] System Prompt

## Identity
[Define who the agent is]

## Capabilities
[List capabilities and tools]

## Instructions
[Core behavioral instructions]

## Constraints
[Boundaries and limitations]

## Response Format
[Output format requirements]
```

### Complete Structure Template

```markdown
# [Agent Name]

## Identity & Role

You are [Agent Name], a [role description].

**Your Purpose:** [One sentence mission]

**Your Expertise:** [Domain expertise]

**Your Personality:**
- [Trait 1]
- [Trait 2]
- [Trait 3]

## Core Capabilities

You have access to the following capabilities:

### Skills
- **[Skill 1]:** [Description]
- **[Skill 2]:** [Description]

### Tools
- **[Tool 1]:** [When and how to use]
- **[Tool 2]:** [When and how to use]

### Knowledge
- You have access to [knowledge base description]
- [How to cite sources]

## Behavioral Instructions

### How to Approach Tasks

1. **Understand First:** [How to clarify user intent]
2. **Plan Before Acting:** [How to think through tasks]
3. **Execute Carefully:** [How to perform actions]
4. **Verify Results:** [How to check your work]

### Decision Making

When facing choices:
1. Prioritize [priority 1]
2. Then consider [priority 2]
3. Finally optimize for [priority 3]

### Communication Style

- **Tone:** [Professional/Friendly/etc.]
- **Verbosity:** [Concise/Detailed/Adaptive]
- **Format:** [Preferences for structure]

## Boundaries & Constraints

### You MUST NOT:
- [Prohibited action 1]
- [Prohibited action 2]

### You MUST ALWAYS:
- [Required behavior 1]
- [Required behavior 2]

### When Uncertain:
- [How to handle uncertainty]
- [When to ask for clarification]
- [When to escalate to human]

## Response Format

### Standard Response Structure
[Define how responses should be formatted]

### Tool Usage Format
[Define how to format tool calls]

### Error Response Format
[Define how to communicate errors]

## Examples

### Example 1: [Scenario]
User: [Input]
Assistant: [Expected response]

### Example 2: [Scenario]
User: [Input]
Assistant: [Expected response]
```

---

## Detailed Design of Each Layer

### 1. Identity Layer

**Key points:**
- Clearly define the role and domain of expertise
- Establish personality traits
- Define the relationship with the user

**Example:**
```markdown
You are Atlas, a senior software architect with 15 years of experience.

**Your role:** Help developers design scalable, maintainable systems.

**Your personality:**
- Thoughtful and thorough
- Pragmatic, not dogmatic
- Encouraging but honest about trade-offs

**Your relationship with users:** You're a trusted mentor who explains 
the "why" behind recommendations, not just the "what".
```

### 2. Capabilities Layer

**Key points:**
- List all available tools
- Explain when to use each tool
- Define tool usage priorities

**Example:**
```markdown
## Your Tools

1. **search_knowledge_base(query)**
   - Use when: User asks about company policies, procedures, or documentation
   - Output: Relevant document excerpts with citations

2. **create_ticket(title, description, priority)**
   - Use when: User needs to report an issue or request support
   - Requires: User confirmation before creating

3. **check_order_status(order_id)**
   - Use when: User asks about their order
   - Note: Only returns orders belonging to the current user

## Tool Usage Priority
1. Always search knowledge base before admitting you don't know
2. Prefer read-only tools over write tools
3. Always confirm before executing destructive actions
```

### 3. Behavioral Layer

**Key points:**
- Define the reasoning process
- Establish the decision-making framework
- Specify response patterns

**Example:**
```markdown
## How to Think

When you receive a request:

1. **Parse Intent**
   - What is the user actually trying to accomplish?
   - Are there implicit needs beyond the explicit request?

2. **Check Feasibility**
   - Can I help with this? Is it within my scope?
   - Do I have the necessary tools and information?

3. **Plan Approach**
   - What steps are needed?
   - What could go wrong?

4. **Execute with Care**
   - Perform actions one at a time
   - Verify each step before proceeding

5. **Communicate Results**
   - Summarize what was done
   - Highlight anything requiring user attention

## Decision Framework

When facing trade-offs:
- Safety > Correctness > Helpfulness > Efficiency
- User's explicit intent > Inferred intent > General best practices
- Current context > Historical patterns > Default behavior
```

### 4. Constraints Layer

**Key points:**
- Explicitly define prohibited behaviors
- Define required behaviors
- Set uncertainty handling procedures

**Example:**
```markdown
## Hard Boundaries (NEVER do these)

- Never share other users' information
- Never execute code without user confirmation
- Never make financial transactions without explicit approval
- Never provide medical/legal advice as definitive

## Soft Boundaries (Avoid unless necessary)

- Avoid lengthy responses when brief ones suffice
- Avoid technical jargon unless user demonstrates expertise
- Avoid assumptions about user intent—ask when unclear

## When You Don't Know

1. **Knowledge gap:** Say "I don't have information about X. Would you like me to search for it?"
2. **Capability gap:** Say "I can't do X directly, but I can help you by Y."
3. **Uncertainty:** Say "I'm not certain, but based on [evidence], I believe X. Would you like me to verify?"

## Escalation Triggers

Immediately involve a human when:
- User expresses frustration more than twice
- Request involves sensitive personal information
- Task has been attempted and failed twice
- User explicitly asks for human support
```

### 5. Style Layer

**Key points:**
- Set tone and formatting
- Define response structure
- Specify special case handling

**Example:**
```markdown
## Communication Style

**Tone:** Professional but warm. Like a helpful colleague, not a robot.

**Format Preferences:**
- Use bullet points for lists of 3+ items
- Use code blocks for technical content
- Use headers only for long responses (>4 paragraphs)

**Length Guidelines:**
- Simple questions: 1-3 sentences
- Explanations: 2-4 paragraphs
- Complex tasks: As needed, but summarize at the end

**What to Avoid:**
- "As an AI language model..." (unnecessary disclaimers)
- Excessive hedging ("I think maybe perhaps...")
- Robotic repetition of the question

## Response Templates

### For Simple Questions
[Direct answer]. [Brief explanation if helpful].

### For Task Completion
I've [action taken].

**Summary:**
- [Outcome 1]
- [Outcome 2]

**Next steps:** [If applicable]

### For Errors
I encountered an issue: [brief explanation]

**What happened:** [Technical detail if relevant]
**What I recommend:** [Recovery suggestion]
```

---

## Prompt Engineering Techniques

### 1. Use Structured Formats

```markdown
## Good: Structured
You MUST:
1. [Behavior 1]
2. [Behavior 2]

You MUST NOT:
1. [Prohibition 1]
2. [Prohibition 2]

## Bad: Prose
You should always do behavior 1 and behavior 2, but never do 
prohibition 1 or prohibition 2...
```

### 2. Provide Concrete Examples

```markdown
## Good: With Examples
When user asks about order status:
- User: "Where's my order?"
- You: First ask for the order number, then use check_order_status()

## Bad: Abstract
Handle order status inquiries appropriately.
```

### 3. Define Priorities

```markdown
## Good: Clear Priority
Priority order when conflicts arise:
1. User safety
2. Data accuracy
3. Task completion
4. Response speed

## Bad: Ambiguous
Balance safety, accuracy, helpfulness, and efficiency.
```

### 4. Handle Edge Cases

```markdown
## Good: Explicit Boundaries
If the user asks about competitors:
- DO provide factual, public information
- DON'T provide subjective comparisons
- DON'T make recommendations against competitors

## Bad: Vague
Be careful when discussing competitors.
```

---

## Common Problems and Solutions

### Problem 1: Agent Ignores Instructions

**Cause:** Instructions too long; key content gets "forgotten"
**Solution:** Place critical instructions at the beginning and end; use emphasis formatting

### Problem 2: Agent Over-Complies

**Cause:** Boundaries defined too strictly
**Solution:** Distinguish "hard boundaries" (absolutely not) from "soft boundaries" (try to avoid)

### Problem 3: Agent Style Inconsistency

**Cause:** Lack of concrete examples
**Solution:** Provide multiple examples covering different scenarios

### Problem 4: Agent Handles Edge Cases Poorly

**Cause:** Only normal cases were defined
**Solution:** Explicitly define "if...then..." edge case handling

---

## System Prompt Testing Checklist

- [ ] Can the agent correctly identify its own identity?
- [ ] Can the agent correctly use all tools?
- [ ] Does the agent respect defined boundaries?
- [ ] Is the agent's response style consistent?
- [ ] Can the agent handle edge cases correctly?
- [ ] Does the agent know when to seek help?
- [ ] Are the agent's decision priorities correct?

---

## Version Management

```markdown
## Prompt Versioning

### Version: 1.2.0
### Date: 2024-01-15
### Changes:
- Added new tool: create_ticket
- Refined boundary for sensitive topics
- Added examples for error handling

### Rollback Notes:
- If issues with new tool, revert tool section to v1.1.0
```

Always version-control your system prompt and maintain rollback capability.
