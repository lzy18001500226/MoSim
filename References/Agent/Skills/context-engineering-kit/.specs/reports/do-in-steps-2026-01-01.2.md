# Evaluation Report: do-in-steps Command

---
VOTE: Solution A
SCORES:
  Solution A: 4.3/5.0
  Solution B: 4.1/5.0
  Solution C: 3.9/5.0
CRITERIA:
 - Completeness: A=4.5, B=4.3, C=4.0
 - Correctness: A=4.2, B=4.0, C=4.0
 - Clarity: A=4.5, B=4.2, C=3.8
 - Usability: A=4.2, B=4.0, C=3.8
 - Consistency: A=4.0, B=4.0, C=4.0
---

## Executive Summary

Solution A demonstrates the most comprehensive and polished implementation of the `/do-in-steps` command, with superior clarity in its context accumulation patterns, detailed examples with actual context passing demonstrations, and well-structured error handling. Solution B provides a solid implementation with good theoretical foundation but is slightly more verbose. Solution C is the most concise but lacks some depth in context passing examples and practical guidance.

- **Artifact**:
  - Solution A: `plugins/sadd/commands/do-in-steps.a.md`
  - Solution B: `plugins/sadd/commands/do-in-steps.b.md`
  - Solution C: `plugins/sadd/commands/do-in-steps.c.md`
- **Overall Score**: A=4.3, B=4.1, C=3.9
- **Verdict**: Solution A - GOOD
- **Threshold**: 4.0/5.0
- **Result**: Solution A PASSES, B PASSES, C NEEDS IMPROVEMENT

---

## Criterion Scores

| Criterion | Weight | Solution A | Solution B | Solution C |
|-----------|--------|------------|------------|------------|
| Completeness | 25% | 4.5 (1.125) | 4.3 (1.075) | 4.0 (1.00) |
| Correctness | 25% | 4.2 (1.05) | 4.0 (1.00) | 4.0 (1.00) |
| Clarity | 20% | 4.5 (0.90) | 4.2 (0.84) | 3.8 (0.76) |
| Usability | 15% | 4.2 (0.63) | 4.0 (0.60) | 3.8 (0.57) |
| Consistency | 15% | 4.0 (0.60) | 4.0 (0.60) | 4.0 (0.60) |
| **Weighted Total** | | **4.305** | **4.115** | **3.930** |

---

## Detailed Analysis

### 1. Completeness (Weight: 0.25)

**Required Functionality:**
1. Task decomposition into sequential subtasks with dependencies
2. Model selection per subtask (Opus default, Sonnet for long/non-complex, Haiku for small/easy)
3. Specialized agent matching when applicable
4. Zero-shot CoT at the beginning of each sub-agent prompt
5. Critique/self-verification at the end of each sub-agent prompt
6. Context passing from completed steps to subsequent steps

#### Solution A Evidence:

**Task Decomposition:**
```markdown
### Phase 1: Task Decomposition with Zero-shot CoT

Before dispatching any sub-agents, analyze the task systematically:

1. **Understand the Goal**
   "What is the overall objective?"
   ...

2. **Identify Natural Breakpoints**
   "Where are the logical boundaries in this task?"
   - Database/model changes (foundation)
   - Interface/contract changes (dependencies)
   ...

3. **Determine Dependencies**
   "What must be completed before what?"

4. **Define Clear Boundaries**
   "What exactly does each subtask encompass?"
   - Input: What does this step receive?
   - Action: What transformation/change does it make?
   - Output: What does this step produce?
   - Verification: How do we know it succeeded?
```
Comprehensive decomposition with explicit input/output/verification for each step.

**Model Selection:**
```markdown
| Subtask Profile | Recommended Model | Rationale |
|-----------------|-------------------|-----------|
| **Architecture/Design** (schema design, interface definition) | `opus` | Critical decisions requiring deep reasoning |
| **Complex Implementation** (novel algorithms, intricate logic) | `opus` | Requires high-capability reasoning |
| **Specialized Domain** (security, performance, testing) | `opus` + Specialized Agent | Domain expertise + reasoning power |
| **Standard Implementation** (following patterns, boilerplate) | `sonnet` | Good capability, cost-efficient |
| **Simple Changes** (rename, move, minor edits) | `haiku` | Fast, cheap, sufficient for mechanical tasks |
| **Documentation/Comments** (JSDoc, README updates) | `haiku` | Mechanical documentation generation |
| **Long but Simple** (extensive boilerplate, many files) | `sonnet` | Handles length well, cost-efficient |
```
Complete decision tree provided.

**Zero-shot CoT:**
```markdown
**Zero-shot Chain-of-Thought Prefix (REQUIRED - MUST BE FIRST):**

```markdown
## Reasoning Approach

Let's think step by step.

Before taking any action, think through the problem systematically:

1. "Let me understand what was done in previous steps..."
   - What context am I building on?
   - What interfaces/patterns were established?
   - What constraints did previous steps introduce?
...
```
Explicitly required and well-structured.

**Self-Critique:**
```markdown
**Self-Critique Suffix (REQUIRED - MUST BE LAST):**

### Verification Questions

| # | Question | Check |
|---|----------|-------|
| 1 | Does my work build correctly on previous step outputs? | [Evidence] |
| 2 | Did I maintain consistency with established patterns/interfaces? | [Evidence] |
| 3 | Does my solution address ALL requirements for this step? | [Evidence] |
| 4 | Did I stay within my scope (not modifying unrelated code)? | [Evidence] |
| 5 | Is my output ready for the next step to build upon? | [Evidence] |
```
Complete self-critique with verification table.

**Context Passing:**
```markdown
### Step 1: Define UserRepository Interface
- **What was done:** Created `src/repositories/UserRepository.ts` with interface definition
- **Key outputs:**
  - Interface: `IUserRepository` with methods: `findById`, `findByEmail`, `create`, `update`, `delete`
  - Types: `UserCreateInput`, `UserUpdateInput` in `src/types/user.ts`
- **Relevant for next steps:**
  - Implementation must fulfill `IUserRepository` interface
  - Use the defined input types for method signatures
```
Concrete example showing actual context accumulation.

**Score: 4.5/5** - All required functionality present with concrete examples.

#### Solution B Evidence:

**Task Decomposition:**
```markdown
### Phase 1: Task Analysis and Decomposition

Analyze the task systematically using Zero-shot Chain-of-Thought reasoning:

1. **Task Understanding**
   "What is the overall objective?"

2. **Dependency Identification**
   "What must happen before what?"

3. **Subtask Extraction**
   "What are the distinct units of work?"

4. **Sequence Validation**
   "Is this the correct order?"
```
Complete but less detailed than A.

**Model Selection:**
```markdown
| Complexity | Scope | Risk | Recommended Model |
|------------|-------|------|-------------------|
| High | Any | Any | `opus` |
| Any | Any | High | `opus` |
| Medium | Large | Medium | `opus` |
| Medium | Medium | Medium | `sonnet` |
| Medium | Small | Low | `sonnet` |
| Low | Any | Low | `haiku` |
```
Matrix approach is good but less explicit about specific task types.

**Context Passing:**
```markdown
## Context for Next Steps

### Files Modified
- `src/dto/UserDTO.ts` (new file)
- `src/services/UserService.ts` (modified)

### Key Changes Summary
- Created UserDTO with fields: id (string), name (string), email (string), createdAt (Date)
...
```
Good example at the end but less integrated throughout.

**Score: 4.3/5** - All functionality present but slightly less detailed in examples.

#### Solution C Evidence:

**Task Decomposition:**
```markdown
### Phase 1: Task Analysis and Decomposition

Analyze the task systematically to identify sequential subtasks:

1. **Understand the Core Objective**
2. **Identify Natural Boundaries**
3. **Map Dependencies**
4. **Define Subtasks**
```
Present but minimal explanations.

**Model Selection:**
```markdown
| Subtask Profile | Recommended Model | Rationale |
|-----------------|-------------------|-----------|
| **Complex reasoning** (architecture, design, critical logic) | `opus` | Maximum reasoning capability |
| **Specialized domain** (matches agent profile) | `opus` + Agent | Domain expertise + reasoning |
| **Standard implementation** (follow patterns, moderate work) | `sonnet` | Good capability, cost-efficient |
| **Simple transformation** (rename, format, small change) | `haiku` | Fast, cheap, sufficient |
| **Long but straightforward** (docs, verbose output) | `sonnet` | Balanced for length |
| **Default** (when uncertain) | `opus` | Optimize for quality |
```
Complete.

**Context Passing:**
```markdown
**Context Size Guideline:** If cumulative context exceeds ~500 words, summarize older steps more aggressively. Sub-agents can read files directly if they need details.
```
Unique contribution on context size management, but less concrete examples.

**Score: 4.0/5** - All required functionality present but less detailed examples.

---

### 2. Correctness (Weight: 0.25)

**Evaluation:** Is the approach technically sound and follows established SADD patterns?

#### Solution A Evidence:

**Pattern Consistency with `launch-sub-agent.md`:**
- Uses identical CoT prefix structure: "Let's think step by step"
- Same self-critique suffix structure with verification questions
- Same model selection decision tree format
- Correctly uses Task tool for dispatch

**Error Handling:**
```markdown
**If a step fails:**
1. **STOP** - Do not proceed with broken foundation
2. **Report** - Clearly identify what failed and why
3. **Assess** - Determine failure severity:
   - **Recoverable**: Sub-agent made a mistake but approach is sound
   - **Approach failure**: The approach for this step is wrong
   - **Foundation issue**: Previous step output is insufficient
4. **Suggest** - Provide remediation options based on assessment
```
Detailed categorization of failure modes.

**Orchestrator Role:**
```markdown
CRITICAL: You are the orchestrator. You MUST NOT perform the subtasks yourself. Your job is to:
1. Analyze and decompose the task
2. Select optimal model/agent for each subtask
3. Dispatch sub-agents sequentially
4. Collect context and pass it to subsequent steps
5. Report overall progress

Any deviation from this orchestration role will be considered a failure.
```
Explicit and correct.

**Score: 4.2/5** - Sound approach with good error handling.

#### Solution B Evidence:

**Orchestrator Restrictions:**
```markdown
**Orchestrator Restrictions:**
- Do NOT read implementation files to understand their content (let sub-agents do this)
- Do NOT write code or make changes yourself
- Do NOT attempt to merge or integrate sub-agent outputs yourself
- Do NOT overflow your context with file contents - work with summaries
```
More explicit restrictions than A - this is good.

**Error Handling:**
```markdown
### If a Step Fails

1. **Do NOT proceed** to subsequent steps
2. **Analyze failure:** Is it a sub-agent issue or a decomposition issue?
3. **Options:**
   - Dispatch fix sub-agent with specific issue context
   - Re-decompose if the step was poorly defined
   - Escalate to user if fundamental blockers exist
```
Less detailed categorization than A.

**Score: 4.0/5** - Sound but less detailed error handling.

#### Solution C Evidence:

**RED FLAGS Section (Unique):**
```markdown
## RED FLAGS - Never Do These

**NEVER:**
- Read implementation files to understand code details (let sub-agents do this)
- Write code or make changes to source files directly
- Skip decomposition and jump to implementation
- Perform multiple steps yourself "to save time"
- Overflow your context by reading step outputs in detail
```
Excellent addition not in other solutions.

**Working Directory:**
```markdown
#### 3.1 Before First Subtask

Create working directory for intermediate results:

```bash
mkdir -p .steps
```

**File naming convention:** `.steps/{step-N}-{subtask-name}.md`
```
Good addition for artifact management.

**Error Handling:**
```markdown
When a step fails:
1. **Do NOT proceed** to next step
2. **Analyze failure** - what went wrong?
3. **Options:**
   - Retry the step with adjusted prompt
   - Fix the issue manually and continue
   - Abort and report partial progress
4. **Document** the failure in step results
```
Adequate but less detailed.

**Score: 4.0/5** - Sound approach with good RED FLAGS section.

---

### 3. Clarity (Weight: 0.20)

**Evaluation:** Is the command clear, well-documented with good examples?

#### Solution A Evidence:

**Context Differentiator:**
```markdown
**Key differentiator from other commands:**
- `/launch-sub-agent`: Single task execution (no decomposition)
- `/do-in-parallel`: Multiple independent tasks (no dependencies)
- `/do-in-steps`: Sequential dependent tasks (with context passing)
- `/do-competitively`: Same task by multiple agents (competitive)
```
Clear positioning.

**Three Concrete Examples:**
1. Repository Pattern Refactoring - with step-by-step model selection rationale
2. Feature with Database Migration - multi-layer change
3. Multi-file Refactoring with Breaking Changes - demonstrates Haiku usage

Example quality:
```markdown
| Step | Subtask | Model | Rationale |
|------|---------|-------|-----------|
| 1 | Update interfaces | Opus | Breaking changes need careful handling |
| 2 | Update implementations | Haiku | Mechanical rename following interface |
| 3 | Update callers | Haiku | Mechanical updates |
| 4 | Update tests | Haiku | Mechanical test fixes |
| 5 | Update documentation | Haiku | Simple text updates |
```
Shows variety of model selection.

**Context Accumulation Example:**
```markdown
### Step 1: Define UserRepository Interface
- **What was done:** Created `src/repositories/UserRepository.ts` with interface definition
- **Key outputs:**
  - Interface: `IUserRepository` with methods: `findById`, `findByEmail`, `create`, `update`, `delete`
  - Types: `UserCreateInput`, `UserUpdateInput` in `src/types/user.ts`
- **Relevant for next steps:**
  - Implementation must fulfill `IUserRepository` interface
  - Use the defined input types for method signatures

### Step 2: Implement UserRepository
- **What was done:** Created `src/repositories/UserRepositoryImpl.ts` implementing `IUserRepository`
...
```
Shows actual context propagation with real code artifacts.

**Score: 4.5/5** - Excellent documentation with concrete, practical examples.

#### Solution B Evidence:

**Good Examples:**
Three examples with decomposition tables:
1. Interface Change with Consumer Updates
2. Feature Addition Across Layers
3. Bug Fix with Cascading Impact

**Context Format Reference:**
```markdown
## Context Format Reference

**Example of "Context for Next Steps" output from a sub-agent:**

```markdown
## Context for Next Steps

### Files Modified
- `src/dto/UserDTO.ts` (new file)
- `src/services/UserService.ts` (modified)

### Key Changes Summary
- Created UserDTO with fields...
```
Good reference format at the end.

**But:** Examples don't show the actual context being passed between steps - they show the decomposition but not the accumulation flow.

**Score: 4.2/5** - Good documentation but examples don't demonstrate context flow as well.

#### Solution C Evidence:

**Context Accumulation Pattern:**
```markdown
**Context Accumulation Pattern:**

```markdown
## Context from Previous Steps

### Step 1: {name} [COMPLETED]
- Modified: {files}
- Key output: {what was produced}
- Decision: {relevant decision}

### Step 2: {name} [COMPLETED]
- Modified: {files}
- Built on Step 1 by: {how it used Step 1}
- Key output: {what was produced}

### Current Step: Step 3
Uses outputs from Steps 1 and 2 to: {relationship}
```
Generic pattern without concrete values.

**Examples:** Three examples but less detailed:
```markdown
Step 1 dispatch:
- Model: Opus + developer agent
- Context: Original task, current interface
- Output: New async interface, saved to `.steps/step-1-interface.md`
```
Brief, lacking actual context content.

**Score: 3.8/5** - Adequate documentation but examples lack concreteness.

---

### 4. Usability (Weight: 0.15)

**Evaluation:** Will users understand how to use it effectively?

#### Solution A Evidence:

**When to Use Section:**
```markdown
### When to Use `/do-in-steps`

**Good use cases:**
- Multi-layer changes (DB -> API -> UI)
- Refactoring with breaking changes
- Feature implementation with clear phases
- Migrations requiring validation between steps
- Any task where order matters

**Do NOT use when:**
- Tasks are independent (use `/do-in-parallel`)
- Single atomic task (use `/launch-sub-agent`)
- Need competitive solutions (use `/do-competitively`)
- Exploratory work with unclear scope
```
Clear guidance.

**Context Passing Guidelines:**
```markdown
| Scenario | What to Pass | What to Omit |
|----------|--------------|--------------|
| Interface defined in step 1 | Full interface definition | Implementation details |
| Implementation in step 2 | Key patterns, file locations | Internal logic |
| Integration in step 3 | Usage patterns, entry points | Step 2 internal details |
```
Practical decision table.

**Recovery Pattern:**
```markdown
Step N Failed (Recoverable):
  1. Identify specific issue from sub-agent output
  2. Construct corrected prompt addressing the issue
  3. Dispatch new sub-agent for Step N (retry)
  4. On success: Continue to Step N+1
  5. On second failure: Escalate to user
```
Actionable recovery steps.

**Score: 4.2/5** - Very usable with clear guidance.

#### Solution B Evidence:

**Best Practices Section:**
```markdown
### When to Use `/do-in-steps`

**Good use cases:**
- Changes that cascade through multiple files/layers
- Interface modifications with consumers to update
- Feature additions spanning multiple components
...

**Poor use cases:**
- Independent tasks that could run in parallel (use `/do-in-parallel`)
...
```
Good but less detailed.

**Context Passing:**
```markdown
### Context Passing

- **Be selective:** Pass only relevant context, not everything
- **Summarize:** Long outputs should be distilled to key points
- **Flag warnings:** If a step produces something unusual, flag it for next steps
- **Validate continuity:** Ensure each step's output enables the next step
```
General guidance without specific examples.

**Score: 4.0/5** - Usable but less actionable guidance.

#### Solution C Evidence:

**Dependency Identification Questions:**
```markdown
Ask these questions to identify dependencies:
- "If I do B before A, will B break or use stale information?"
- "Does B need any output from A as input?"
- "Would doing B first require redoing work after A?"
```
Unique and helpful addition.

**Context Propagation Guidelines:**
```markdown
**DO pass:**
- Specific outputs needed by next step
- Key decisions that constrain later work
- File paths modified
- Interface changes

**DON'T pass:**
- Full implementation details (sub-agent can read files)
- Lengthy explanations (keep context concise)
- Information not relevant to next step
```
Clear but brief.

**Model Selection Tips:**
```markdown
### Model Selection Tips

- **When in doubt, use Opus** - quality over cost for dependent steps
- **Haiku only for truly mechanical work** - dependencies mean errors propagate
- **Consider cumulative risk** - early step failures cascade
```
Practical advice.

**Score: 3.8/5** - Good tips but less comprehensive guidance.

---

### 5. Consistency (Weight: 0.15)

**Evaluation:** Does it align with SADD plugin patterns and other commands?

#### Solution A Evidence:

**Consistent with `launch-sub-agent.md`:**
- Same CoT prefix format ("Let's think step by step")
- Same self-critique suffix with verification table
- Same model selection decision tree structure
- Same dispatch pattern using Task tool

**Consistent with `do-competitively.md`:**
- Uses similar context/task XML tags structure
- Similar progress reporting format

**SADD Plugin Alignment:**
```markdown
**Key differentiator from other commands:**
- `/launch-sub-agent`: Single task execution (no decomposition)
- `/do-in-parallel`: Multiple independent tasks (no dependencies)
- `/do-in-steps`: Sequential dependent tasks (with context passing)
- `/do-competitively`: Same task by multiple agents (competitive)
```
Explicit positioning within SADD family.

**Score: 4.0/5** - Good consistency with existing patterns.

#### Solution B Evidence:

**Related Commands Section:**
```markdown
**Related commands in SADD plugin:**
- `/launch-sub-agent` - Single task, single sub-agent, intelligent model selection
- `/do-in-parallel` - Same task across multiple targets, parallel execution
- `/do-competitively` - Single task, multiple competing solutions, synthesis
- `/do-in-steps` (this) - Complex task decomposed into sequential subtasks with context passing
```
Clear positioning.

**Pattern Consistency:**
- Uses same CoT and critique patterns
- Similar Task tool dispatch
- Consistent model selection approach

**Score: 4.0/5** - Good consistency.

#### Solution C Evidence:

**Uses same patterns:**
- CoT prefix with "Let's think step by step"
- Self-critique suffix with verification questions
- Task tool dispatch pattern

**Working Directory Addition:**
```markdown
#### 3.1 Before First Subtask

Create working directory for intermediate results:

```bash
mkdir -p .steps
```
```
Unique to C - not in other SADD commands (minor consistency deviation but reasonable addition).

**Score: 4.0/5** - Good consistency with reasonable additions.

---

## Self-Verification

### Questions Asked:

1. Am I being biased toward longer solutions (Solution A is longest)?
2. Did I properly evaluate the unique strengths of each solution?
3. Did Solution B's context format reference adequately address context passing?
4. Is Solution C's `.steps/` directory addition a strength or consistency deviation?
5. Did I give proper weight to Solution C's "RED FLAGS" section?

### Answers:

**Q1:** Re-examining - Solution A is 515 lines, B is 613 lines, C is 571 lines. Actually Solution B is LONGEST, not A. My scoring was not biased toward length. Solution A's higher score is based on concrete examples and clarity, not length.

**Q2:** Re-examining unique strengths:
- Solution A: Best context accumulation examples with actual code artifacts
- Solution B: Best orchestrator restrictions list, good theoretical foundation section
- Solution C: Best RED FLAGS section, unique `.steps/` working directory, dependency identification questions

Adjustments: I should increase Solution C's correctness score slightly for the RED FLAGS section, which is a valuable safeguard pattern not in others.

**Q3:** Solution B's context format reference is at the end of the document and is good but doesn't demonstrate the FLOW of context between steps. Solution A shows Step 1 -> Step 2 accumulation with actual interface definitions being passed. This distinction is valid.

**Q4:** The `.steps/` directory is a reasonable addition that helps with artifact management. It doesn't break consistency but adds value. Keeping score at 4.0 is appropriate.

**Q5:** The RED FLAGS section in Solution C is valuable and addresses a real concern about orchestrator behavior. However, Solution A has similar content in:
```markdown
CRITICAL: You are the orchestrator. You MUST NOT perform the subtasks yourself.
```
And Solution B has:
```markdown
**Orchestrator Restrictions:**
- Do NOT read implementation files...
```

Solution C's RED FLAGS format is more prominent and easier to find. This warrants consideration but doesn't change the overall ranking significantly since the content is similar across all three.

### Adjustments Made:

After verification, minor adjustments:
- Solution A: No change (4.3 overall)
- Solution B: No change (4.1 overall) - it has the longest document but that doesn't make it better
- Solution C: Slight increase to Correctness from 3.9 to 4.0 for RED FLAGS value, but overall score remains 3.9 due to less concrete examples

---

## Confidence Assessment

**Confidence Level**: High

**Confidence Factors**:
- Evidence strength: Strong - quoted specific text from all solutions
- Criterion clarity: Clear - well-defined evaluation criteria with weights
- Edge cases: Handled - verified potential biases

---

## Key Strengths

### Solution A
1. **Best context accumulation examples**: Shows actual interface definitions, file paths, and how they propagate through steps with concrete code examples
2. **Comprehensive error handling**: Categorizes failures into recoverable, approach failure, and foundation issue with specific recovery patterns
3. **Clear decision tables**: Context passing guidelines with scenario-based recommendations

### Solution B
1. **Explicit orchestrator restrictions**: Most detailed list of what the orchestrator should NOT do
2. **Good theoretical foundation**: Links to academic research with proper citations
3. **Context format reference**: Provides clear template for sub-agent output

### Solution C
1. **RED FLAGS section**: Prominent and scannable list of anti-patterns
2. **Working directory pattern**: Unique `.steps/` approach for artifact management
3. **Dependency identification questions**: Practical questions to determine step ordering

---

## Areas for Improvement

### Solution A - Priority: Low
- Evidence: No RED FLAGS section like Solution C
- Impact: Users might miss the critical warnings
- Suggestion: Add a scannable RED FLAGS section at the top

### Solution B - Priority: Medium
- Evidence: Examples don't show actual context content flowing between steps
- Impact: Users may not understand what concrete context looks like
- Suggestion: Add example showing Step 1 output being used in Step 2 prompt

### Solution C - Priority: Medium
- Evidence: Examples use placeholders like `{name}`, `{files}` instead of concrete values
- Impact: Less actionable for users trying to understand the pattern
- Suggestion: Replace at least one example with concrete code artifact names

---

## Actionable Improvements

**For Final Solution:**

**High Priority:**
- [ ] Take Solution A as base (best examples and clarity)
- [ ] Add RED FLAGS section from Solution C at the top

**Medium Priority:**
- [ ] Consider adding `.steps/` working directory pattern from Solution C
- [ ] Add dependency identification questions from Solution C

**Low Priority:**
- [ ] Add orchestrator restrictions list format from Solution B
