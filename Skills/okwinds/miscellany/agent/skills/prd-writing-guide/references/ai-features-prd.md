# AI Features PRD Guide

Additional requirements guidance when your product includes AI-powered features.

---

## Why AI Features Need Special Treatment

AI features are fundamentally different from traditional software:

| Traditional Feature | AI Feature |
|---------------------|------------|
| Deterministic: Same input → same output | Probabilistic: Same input → may vary |
| Binary: Works or doesn't | Gradual: Works better or worse |
| Predictable failures | Unpredictable failures |
| Test with assertions | Test with evaluation datasets |
| Bug = code error | "Bug" = model behavior |

This means PRDs for AI features need **additional sections** beyond traditional requirements.

---

## Required Sections for AI Features

### 1. AI Behavior Specification

Don't just say "AI does X"—specify exactly what "doing X" means.

#### Template:

```markdown
## AI Feature: [Name]

### Purpose
[What problem this AI feature solves]

### Trigger
[When/how is the AI invoked?]
- User action: [What user does]
- Automatic: [What conditions trigger it]

### Input
[What data the AI receives]
- Source: [Where it comes from]
- Format: [Expected structure]
- Constraints: [Size limits, etc.]

### Expected Output
[What the AI should produce]
- Format: [Structure of output]
- Characteristics: [Tone, length, style, etc.]

### Success Criteria
[How we know the AI did a good job]
- Quality metric: [Accuracy, relevance, etc.]
- Target: [Specific number]
- Measurement: [How measured]

### Failure Modes
[What can go wrong]
| Failure | User Impact | Handling |
|---------|-------------|----------|
| [Mode] | [Impact] | [How to handle] |

### Examples
[Concrete input/output examples]
| Input | Good Output | Bad Output |
|-------|-------------|------------|
| [Example] | [Example] | [Example] |
```

#### Example:

```markdown
## AI Feature: Smart Reply Suggestions

### Purpose
Help users respond to messages quickly by suggesting contextually appropriate replies.

### Trigger
- Automatic: When user opens a message that expects a response
- Condition: Message is from last 24 hours and requires action

### Input
- Current message text (up to 2000 characters)
- Last 5 messages in thread for context
- User's name and role

### Expected Output
- 3 reply suggestions
- Each suggestion: 1-2 sentences
- Tone: Professional but friendly
- Format: Plain text, no formatting

### Success Criteria
- User clicks suggestion: >15% of exposures
- User sends suggestion as-is or with minor edits: >10%
- Negative feedback (<thumbs down): <5%

### Failure Modes
| Failure | User Impact | Handling |
|---------|-------------|----------|
| No suggestions generated | Can't use feature | Show "Compose your own reply" |
| Irrelevant suggestions | Feature seems broken | Allow "Not helpful" feedback |
| Offensive suggestion | Trust damage | Content filter before display |
| Slow (>2s) | User moves on | Show suggestions async, don't block |

### Examples
| Received Message | Good Suggestions | Bad Suggestions |
|------------------|------------------|-----------------|
| "Can you join the meeting at 3pm?" | "Yes, I'll be there!", "3pm works for me.", "I have a conflict—can we do 3:30?" | "No.", "What meeting?", "..." |
| "The report has errors on page 5" | "Thanks for catching that—I'll fix it.", "Can you be more specific about the errors?", "I'll review and send an updated version." | "You're wrong.", "What report?", "OK" |
```

---

### 2. Quality Metrics

AI features need quantified quality expectations.

#### Metrics to Define:

| Metric Type | Questions to Answer |
|-------------|---------------------|
| **Accuracy** | What % correct is acceptable? How is "correct" defined? |
| **Relevance** | How do we measure if output is relevant? |
| **Latency** | How fast must it respond? |
| **Coverage** | What % of inputs should it handle? |
| **Safety** | What outputs are never acceptable? |

#### Example Quality Spec:

```markdown
### Quality Requirements

| Metric | Target | Measurement | Minimum |
|--------|--------|-------------|---------|
| Accuracy | 90% | Human eval on 500 samples/month | 80% |
| Relevance | 85% "relevant or better" | User feedback widget | 75% |
| Latency | <1.5s P95 | APM monitoring | <3s |
| Coverage | 95% | % inputs with valid output | 90% |
| Safety | 0 harmful outputs | Red team + production monitoring | 0 |

### Evaluation Process
- Monthly: Random sample of 500 outputs human-evaluated
- Continuous: Monitor automated metrics in dashboard
- Quarterly: Red team testing for edge cases
```

---

### 3. Failure Handling

AI will fail. Define what happens when it does.

#### Questions to Answer:

1. **What if AI returns nothing?**
   - Show placeholder? Hide feature? Show error?

2. **What if AI returns garbage?**
   - Can we detect it? What do we show?

3. **What if AI is slow?**
   - Show loading? Timeout? Async delivery?

4. **What if AI is unavailable?**
   - Feature disabled? Fallback? Queue for later?

5. **What if AI returns harmful content?**
   - Filter before display? Log? Alert?

#### Example:

```markdown
### Failure Handling

| Condition | Detection | User Experience | System Action |
|-----------|-----------|-----------------|---------------|
| No response (timeout >5s) | Timeout | Show "Suggestions unavailable" | Log, alert if >5% |
| Low confidence (<0.3) | Model score | Don't show suggestions | Log for analysis |
| Harmful content | Content filter | Don't show, fallback | Log, alert, block |
| API error | HTTP status | "Feature temporarily unavailable" | Retry 3x, then fail |
| Rate limited | 429 status | Queue, show when ready | Backoff, respect limits |
```

---

### 4. User Expectations

Set appropriate expectations for AI behavior.

#### Questions to Answer:

1. **Does user know it's AI?**
   - Transparency: Should we label it as AI-generated?

2. **What should user expect?**
   - Perfection? Assistance? Starting point?

3. **How can user correct it?**
   - Edit? Regenerate? Feedback?

4. **How does feedback work?**
   - Thumbs up/down? Report? Ignore?

#### Example:

```markdown
### User Experience Principles

**Transparency:**
- Label clearly: "Suggested by AI" or similar
- Don't pretend AI content is human-written

**Expectations:**
- Position as "suggestions" not "answers"
- Allow easy editing before sending
- Show confidence when relevant ("Best guess" vs "High confidence")

**Control:**
- User can disable AI suggestions in settings
- User can regenerate for different suggestions
- User can provide feedback (helpful/not helpful)

**Feedback Loop:**
- Thumbs up/down on each suggestion
- "Report inappropriate" option
- Aggregate feedback visible in analytics
```

---

### 5. Edge Cases for AI

AI has unique edge cases beyond normal software.

#### Common AI Edge Cases:

| Category | Edge Cases to Consider |
|----------|------------------------|
| **Input** | Empty input, very long input, foreign language, special characters, adversarial input (prompt injection) |
| **Content** | Sensitive topics, controversial topics, PII in input, legal/medical/financial advice |
| **Context** | Ambiguous requests, multiple valid interpretations, missing context |
| **Output** | Repetitive output, truncated output, off-topic output, contradictory output |
| **Timing** | First-time use, high load, degraded mode |

#### Example:

```markdown
### AI Edge Cases

| Edge Case | Handling | Rationale |
|-----------|----------|-----------|
| Input contains PII | Redact before processing | Privacy |
| Input is foreign language | Detect, respond "English only" or translate | Clear limitations |
| Input is adversarial (prompt injection) | Sanitize, log, don't process | Security |
| Topic is sensitive (health, legal, finance) | Add disclaimer, suggest professional | Liability |
| Input is ambiguous | Ask clarifying question or provide multiple interpretations | Quality |
| Output would reveal training data | Filter, don't output | Copyright/privacy |
| Output is very similar to recent output | Vary or acknowledge | User experience |
```

---

### 6. Cost Considerations

AI features often have per-use costs that traditional features don't.

#### Questions to Answer:

1. **What's the cost per use?**
   - API costs, compute costs

2. **What's the expected volume?**
   - Uses per user, total uses

3. **Are there cost controls?**
   - Rate limits, usage caps

4. **How does cost scale?**
   - Linear? Superlinear?

#### Example:

```markdown
### Cost Model

**Per-Request Cost:**
- Input tokens: ~500 avg × $0.01/1K = $0.005
- Output tokens: ~100 avg × $0.03/1K = $0.003
- **Total per request:** ~$0.008

**Volume Estimate:**
- Daily active users: 10,000
- Requests per DAU: 5
- Daily requests: 50,000
- **Daily cost:** $400
- **Monthly cost:** ~$12,000

**Cost Controls:**
- Rate limit: 20 requests/user/day
- Cache common queries: Expected 30% hit rate
- Fallback to smaller model after quota: Reduces cost 5x

**Scaling Triggers:**
- At 100K DAU: Evaluate batch processing
- At $50K/month: Evaluate fine-tuning smaller model
```

---

### 7. Testing AI Features

AI features need evaluation, not just testing.

#### Testing Types:

| Type | Purpose | Method |
|------|---------|--------|
| **Unit tests** | Code works correctly | Standard assertions |
| **Evaluation** | Model outputs are good | Human eval on benchmark |
| **Regression** | Quality doesn't decrease | Compare to baseline |
| **Red teaming** | Find failure modes | Adversarial testing |
| **A/B testing** | Compare approaches | Production experiment |

#### Example:

```markdown
### Testing Requirements

**Pre-Launch:**
- [ ] Evaluation dataset of 500+ examples with expected outputs
- [ ] Human evaluation scores >85% acceptable
- [ ] Red team testing: no critical failures found
- [ ] Load testing: handles 100 req/s

**Post-Launch:**
- [ ] A/B test against control (no AI) for 2 weeks
- [ ] Daily quality monitoring dashboard
- [ ] Weekly review of negative feedback
- [ ] Monthly full evaluation re-run

**Regression Testing:**
- Any prompt/model change requires:
  - Re-run evaluation dataset
  - Score must not decrease >5%
  - Review any new failure cases
```

---

## AI PRD Checklist

Additional checks for AI features:

- [ ] Behavior specification with concrete examples
- [ ] Quality metrics with targets and minimums
- [ ] All failure modes documented with handling
- [ ] User expectations/transparency defined
- [ ] Edge cases including adversarial inputs
- [ ] Cost model with controls
- [ ] Evaluation dataset defined
- [ ] Testing approach (not just unit tests)
- [ ] Feedback mechanism for users
- [ ] Monitoring plan for production

---

## Red Flags in AI Feature PRDs

Watch for these signs of incomplete AI requirements:

| Red Flag | Problem | Fix |
|----------|---------|-----|
| "AI will figure it out" | No behavior spec | Define exactly what "figuring out" means |
| "Smart/intelligent [feature]" | Marketing speak | Define measurable outcomes |
| "Natural language" | Ambiguous | Specify languages, formats, limits |
| "High accuracy" | No number | Define target accuracy and how measured |
| No examples | Can't evaluate | Provide input/output examples |
| No failure handling | Will break in production | Define every failure mode |
| "As good as a human" | Unmeasurable | Define specific tasks and metrics |
