# Worked Example: HelpBot — PRD to Engineering Spec

> This example continues from the [prd-writing-guide](./prd-writing-guide-worked-example.md) and [ai-agent-prd](./ai-agent-prd-worked-example.md) worked examples, converting the **HelpBot** PRD into an engineering specification using the 7 Engineering Lenses.

---

## Phase 0: PRD Validation

### Standard Checklist (Pass/Fail)

| Check | Result | Notes |
|-------|--------|-------|
| User stories with acceptance criteria | ✅ | 3 P0 stories with Gherkin criteria |
| Functional requirements with priorities | ✅ | 4 features (F-001 to F-004), all prioritized |
| NFRs with measurable targets | ✅ | Latency, availability, scale, cost all quantified |
| System context diagram | ✅ | 5 external systems mapped |
| Data flow diagram | ✅ | Customer query resolution flow |
| Integration specs with auth/limits/failure | ✅ | All 5 integrations fully specified |
| Success metrics with baselines | ✅ | 5 metrics with current vs target |

### Agent-Specific Checklist (from agent-system-spec.md)

| Check | Result | Notes |
|-------|--------|-------|
| Agent identity and scope boundaries | ✅ | Can/Cannot table defined |
| Skills with triggers and tools | ✅ | 5 skills specified |
| Tool interfaces with error handling | ✅ | YAML specs for 3 tools |
| System prompt design (6 sections) | ✅ | All 6 sections present |
| Golden conversations (15+) | ✅ | 23 conversations across 6 categories |
| RAG specification | ✅ | Sources, chunking, retrieval, gap handling |
| Safety matrix | ✅ | 5 threats with detection + response |
| Evaluation framework | ✅ | 6 automated metrics with targets |
| Cost budget | ✅ | Component-level breakdown, $500/mo cap |

**Verdict:** PRD passes Phase 0. Proceed to specification.

---

## Phase 1–2: Requirements Extraction

*(Standard extraction of user stories → functional requirements → traceability matrix. Abbreviated here; see spec-templates.md for full format.)*

### Key Functional Requirements Derived

| FR | Source | Description | Priority |
|----|--------|-------------|----------|
| FR-001 | US-001, F-001 | RAG-based knowledge Q&A with plan-awareness | P0 |
| FR-002 | US-002, F-002 | Read-only billing lookup via Stripe | P0 |
| FR-003 | US-003, F-003 | Multi-signal escalation to human agent | P0 |
| FR-004 | F-001 | Knowledge base sync from Notion (weekly) | P0 |
| FR-005 | F-004 | Conversation analytics dashboard | P1 |
| FR-006 | Agent PRD | System prompt versioning and rollback | P0 |
| FR-007 | Agent PRD | Golden conversation regression testing | P0 |

---

## Phase 3: Engineering Specification (7 Lenses Applied)

### Lens 1: Architecture — "How does it fit together?"

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           HelpBot Architecture                         │
│                                                                         │
│  ┌──────────┐     ┌──────────────────────────────────────────────────┐ │
│  │ Intercom  │────►│                 API Gateway                      │ │
│  │ Webhook   │     │           (Auth + Rate Limit)                    │ │
│  └──────────┘     └────────────────────┬─────────────────────────────┘ │
│                                        │                                │
│                              ┌─────────▼──────────┐                    │
│                              │   Orchestrator      │                    │
│                              │   (Execution Loop)  │                    │
│                              └──┬───┬───┬───┬──────┘                   │
│                                 │   │   │   │                           │
│              ┌──────────────────┘   │   │   └────────────────┐         │
│              ▼                      ▼   ▼                    ▼         │
│  ┌───────────────┐  ┌──────────┐ ┌───────────┐  ┌──────────────────┐ │
│  │ RAG Pipeline   │  │ Stripe   │ │CloudStore │  │ Intercom Reply   │ │
│  │ (Pinecone +    │  │ Client   │ │ API Client│  │ + Handoff Client │ │
│  │  Embeddings)   │  └──────────┘ └───────────┘  └──────────────────┘ │
│  └───────┬───────┘                                                     │
│          │                                                              │
│  ┌───────▼───────┐    ┌────────────┐    ┌────────────────┐            │
│  │  Pinecone     │    │   Redis    │    │  PostgreSQL    │            │
│  │  (Vectors)    │    │  (Cache)   │    │ (Conversations │            │
│  └───────────────┘    └────────────┘    │  + Analytics)  │            │
│                                          └────────────────┘            │
└─────────────────────────────────────────────────────────────────────────┘
```

**Technology Decisions:**

| Component | Choice | Rationale | Alternatives Rejected |
|-----------|--------|-----------|----------------------|
| Runtime | Python 3.12 + FastAPI | Team expertise; async-native; LLM SDK support | Node.js (less ML ecosystem) |
| LLM | Claude 3.5 Sonnet (primary), GPT-4o (fallback) | Best quality/cost for support; fallback for resilience | Single-provider (SPOF risk) |
| Vector DB | Pinecone Starter | Managed, low-ops, sufficient scale (100K vectors) | Self-hosted Qdrant (ops burden too high for 3-person team) |
| Cache | Redis (Upstash serverless) | KB article cache + conversation session state | In-memory (lost on restart) |
| App DB | PostgreSQL (Supabase) | Conversation logs, analytics, prompt versions | MongoDB (team prefers SQL) |
| Hosting | Railway | Simple deploy, auto-scaling, affordable | AWS ECS (over-engineered for MVP) |

### Lens 2: Data — "What is stored, how, and why?"

**Entity: Conversation**

| Field | Type | Null | Constraints | Description |
|-------|------|------|-------------|-------------|
| id | UUID | No | PK | Conversation identifier |
| intercom_conversation_id | VARCHAR(64) | No | UNIQUE, INDEX | Intercom reference |
| user_id | VARCHAR(64) | No | INDEX | CloudStore user ID |
| started_at | TIMESTAMP | No | | Conversation start |
| ended_at | TIMESTAMP | Yes | | Conversation end (null if active) |
| status | ENUM | No | 'active','resolved','escalated' | Current state |
| resolution_type | ENUM | Yes | 'auto','human','abandoned' | How it ended |
| escalation_reason | VARCHAR(255) | Yes | | Why escalated (if applicable) |
| total_turns | INT | No | DEFAULT 0 | Message count |
| total_tokens | INT | No | DEFAULT 0 | LLM tokens consumed |
| total_cost_cents | INT | No | DEFAULT 0 | Total cost in cents |
| csat_score | SMALLINT | Yes | CHECK 1-5 | Post-conversation rating |
| created_at | TIMESTAMP | No | DEFAULT NOW() | Record creation |

**Entity: Message**

| Field | Type | Null | Constraints | Description |
|-------|------|------|-------------|-------------|
| id | UUID | No | PK | Message identifier |
| conversation_id | UUID | No | FK→Conversation, INDEX | Parent conversation |
| role | ENUM | No | 'user','assistant','system' | Message sender |
| content | TEXT | No | | Message text (PII-redacted for storage) |
| tool_calls | JSONB | Yes | | Tools invoked and results |
| rag_sources | JSONB | Yes | | Retrieved KB articles with scores |
| confidence_score | FLOAT | Yes | | Agent's confidence in response |
| tokens_used | INT | No | DEFAULT 0 | Tokens for this message |
| latency_ms | INT | Yes | | Response generation time |
| created_at | TIMESTAMP | No | DEFAULT NOW(), INDEX | Message timestamp |

**Entity: PromptVersion**

| Field | Type | Null | Constraints | Description |
|-------|------|------|-------------|-------------|
| id | SERIAL | No | PK | Version identifier |
| version_tag | VARCHAR(32) | No | UNIQUE | Semantic version "1.0.0" |
| prompt_text | TEXT | No | | Full system prompt |
| variables_schema | JSONB | No | | Expected dynamic variables |
| author | VARCHAR(128) | No | | Who created this version |
| is_active | BOOLEAN | No | DEFAULT FALSE | Currently deployed |
| test_results | JSONB | Yes | | Golden conversation test results |
| created_at | TIMESTAMP | No | DEFAULT NOW() | Version creation |
| activated_at | TIMESTAMP | Yes | | When set as active |

**Data Flow:** User message → PII scan (redact before storage) → store in Message table → process → store response → async: log to analytics.

### Lens 3: Contract — "What are the exact interfaces?"

**Intercom Webhook Endpoint:**

```yaml
POST /webhooks/intercom
Headers:
  X-Hub-Signature: HMAC-SHA256 signature for verification
Body: Intercom webhook payload (conversation.user.created / conversation.user.replied)
Response: 200 OK (async processing)
Processing: 
  1. Verify HMAC signature
  2. Extract conversation_id, user message, user metadata
  3. Enqueue for orchestrator processing
  4. Return 200 within 3 seconds (Intercom timeout)
```

**Internal Orchestrator Interface:**

```yaml
POST /internal/process-message
Body:
  conversation_id: string
  user_message: string
  user_context:
    user_id: string
    user_name: string
    plan: "free" | "pro" | "enterprise"
    company: string
Response:
  action: "reply" | "escalate"
  reply_text: string | null
  escalation_context: EscalationPayload | null
  metadata:
    confidence: float
    tools_used: string[]
    rag_sources: Source[]
    tokens: int
    latency_ms: int
```

**RAG Search Internal Interface:**

```yaml
POST /internal/rag/search
Body:
  query: string
  top_k: int (default: 3)
  min_score: float (default: 0.75)
  plan_filter: "free" | "pro" | "enterprise" | null
Response:
  results:
    - chunk_text: string
      source_title: string
      source_url: string
      score: float
      metadata: { updated_at, section }
  search_latency_ms: int
```

### Lens 4: Failure — "What breaks and what happens?"

| Failure Mode | Detection | Impact | Recovery | RTO |
|-------------|-----------|--------|----------|-----|
| LLM API primary (Claude) down | HTTP 5xx / timeout >10s | Cannot generate responses | Automatic failover to GPT-4o | <5s |
| LLM API both providers down | Both fail health check | Full agent outage | Queue messages; auto-reply "We're experiencing issues, a human agent will follow up" | <30s to fallback message |
| Pinecone unavailable | Connection timeout >3s | Cannot search KB | Answer from LLM general knowledge; flag in response "I'm answering from general knowledge, accuracy may vary" | <5s |
| Stripe API down | HTTP 5xx / timeout >5s | Cannot look up billing | "Billing info temporarily unavailable"; offer human escalation | <5s |
| Redis cache down | Connection refused | No session cache, slower KB lookups | Bypass cache; direct Pinecone queries; slightly higher latency | 0s (graceful degradation) |
| PostgreSQL down | Connection error | Cannot log conversations | Buffer in Redis (5min TTL); alert ops; agent continues working | <5s for logging resume |
| Intercom webhook fails | Retry queue depth >100 | Missed messages | Intercom retries 3x; dead letter queue; manual reconciliation | Per Intercom retry (up to 24h) |

**Circuit Breaker Configuration:**

| Service | Failure Threshold | Open Duration | Half-Open Test |
|---------|------------------|---------------|---------------|
| Claude API | 5 failures in 30s | 60s | 1 request |
| GPT-4o API | 5 failures in 30s | 60s | 1 request |
| Stripe | 3 failures in 60s | 120s | 1 request |
| Pinecone | 3 failures in 30s | 60s | 1 request |

### Lens 5: Security — "How is it protected?"

**Authentication Flow:**

```
Intercom Webhook → Verify HMAC-SHA256 signature → Extract user identity from Intercom payload
                  → Map to CloudStore user via user_id
                  → Scope all data access to that user_id only
```

| Security Control | Implementation |
|-----------------|---------------|
| Webhook verification | HMAC-SHA256 with Intercom signing secret |
| User data isolation | All DB queries include `WHERE user_id = {authenticated_user}` |
| Stripe access | Restricted API key: read-only invoices + subscriptions |
| CloudStore API | Service token with read-only scope |
| PII handling | Scan messages with regex + NER before storage; hash email/phone in analytics |
| Secrets storage | Railway environment variables (encrypted at rest) |
| Prompt injection | Input sanitization layer; system prompt has anti-injection framing |
| Rate limiting | 10 messages/minute per user; 1000 webhooks/minute global |

**Data Classification:**

| Data | Classification | Storage | Logging |
|------|---------------|---------|---------|
| User messages | Confidential | Encrypted at rest, PII-redacted | Hash only |
| Billing data | Restricted | Never stored locally; fetched on-demand | Never logged |
| KB articles | Internal | Pinecone (encrypted) | Title only |
| Conversation metadata | Internal | PostgreSQL (encrypted at rest) | Full |
| System prompts | Internal | PostgreSQL (versioned) | Version ID only |

### Lens 6: Operations — "How is it deployed, monitored, debugged?"

**Deployment:**

| Attribute | Value |
|-----------|-------|
| Platform | Railway (container) |
| Image | Python 3.12 slim |
| CI/CD | GitHub Actions → Railway auto-deploy |
| Environments | staging (auto-deploy from `develop`), production (manual promote from `main`) |
| Rollout | Blue-green on Railway; instant rollback via previous deployment |
| DB migrations | Alembic; forward-only; tested in staging first |

**Configuration Registry:**

| Parameter | Env Var | Secret | Restart | Default |
|-----------|---------|--------|---------|---------|
| LLM model (primary) | `LLM_PRIMARY_MODEL` | No | No (hot-swap) | claude-3-5-sonnet |
| LLM model (fallback) | `LLM_FALLBACK_MODEL` | No | No | gpt-4o |
| Claude API key | `ANTHROPIC_API_KEY` | Yes | Yes | — |
| OpenAI API key | `OPENAI_API_KEY` | Yes | Yes | — |
| Intercom signing secret | `INTERCOM_WEBHOOK_SECRET` | Yes | Yes | — |
| Stripe restricted key | `STRIPE_API_KEY` | Yes | Yes | — |
| Pinecone API key | `PINECONE_API_KEY` | Yes | Yes | — |
| RAG min score | `RAG_MIN_SCORE` | No | No | 0.75 |
| Max conversation turns | `MAX_TURNS_IN_CONTEXT` | No | No | 20 |
| Cost alert threshold | `COST_ALERT_DAILY_CENTS` | No | No | 2000 |

**Monitoring:**

| Metric | Type | Alert Threshold | Channel |
|--------|------|----------------|---------|
| Error rate (5xx) | ratio | >2% for 5min | Slack #helpbot-alerts |
| P95 response latency | histogram | >8s for 5min | Slack #helpbot-alerts |
| LLM primary failure rate | ratio | >10% for 2min | PagerDuty (triggers failover) |
| Daily LLM cost | counter | >$20/day | Slack #helpbot-alerts |
| Escalation rate | ratio | >30% for 1hr | Slack #helpbot-analytics |
| CSAT <3 streak | counter | 3 consecutive | Slack #helpbot-alerts |

**Logging Format:**
```json
{
  "timestamp": "ISO-8601",
  "level": "INFO",
  "service": "helpbot",
  "trace_id": "conv_{intercom_conversation_id}",
  "event": "message_processed",
  "user_id_hash": "sha256:abc...",
  "tools_used": ["rag_search"],
  "confidence": 0.87,
  "latency_ms": 2340,
  "tokens": 850,
  "cost_cents": 3
}
```

### Lens 7: Replicability — "Could another team rebuild this from the spec?"

**Replicability Checklist:**

| Item | Specified | Location |
|------|----------|----------|
| ✅ All runtime versions pinned | Python 3.12, FastAPI 0.109+ | TECH_STACK.md |
| ✅ All external service versions | Intercom API v2.10, Stripe 2024-04-10 | API_SPEC.md |
| ✅ All environment variables documented | 10 params with types/defaults | CONFIGURATION.md |
| ✅ Database schema with types/constraints | 3 entities, full DDL-ready | DATA_MODEL.md |
| ✅ Every API interface with request/response | 3 internal + 5 external | API_SPEC.md |
| ✅ Every failure mode with recovery | 7 failure modes, circuit breaker config | FAILURE_MODES.md |
| ✅ Business rules as pseudocode | Escalation logic, confidence thresholds | BUSINESS_LOGIC.md |
| ✅ Security controls enumerated | 8 controls, data classification table | AUTH_DESIGN.md |
| ✅ Deployment target with config | Railway, GitHub Actions pipeline | DEPLOYMENT.md |
| ✅ Monitoring with concrete thresholds | 6 metrics, alert channels | MONITORING.md |
| ✅ System prompt as versioned artifact | Full prompt, variable schema, version table | SYSTEM_PROMPT_SPEC.md |
| ✅ Test suite defined | 23 golden conversations + 6 automated metrics | TEST_PLAN.md |

**Verdict:** A competent team could rebuild HelpBot from this spec without access to the original developers.

---

## Phase 4: Agent System Specification (Excerpts)

*(Derived from agent-system-spec.md reference)*

### Orchestrator Execution Loop

```
1. RECEIVE: Intercom webhook → extract message + user context
2. PERCEIVE: Classify intent (knowledge_qa | billing | account | escalation | chitchat)
3. PLAN: Select skill based on intent → determine required tools
4. EXECUTE: 
   a. If knowledge_qa → rag_search → format answer with citations
   b. If billing → stripe_billing → format billing breakdown  
   c. If account → cloudstore_api → format account summary
   d. If escalation signals detected at any point → intercom_handoff
5. VALIDATE: Check confidence score ≥ 0.75; check response against guardrails
6. RESPOND: Send via Intercom API
7. LOG: Async write to PostgreSQL + update metrics
```

**Termination Conditions:**
- User says goodbye/thanks → resolve conversation
- Successful escalation to human → mark as escalated
- 30 minutes of inactivity → auto-close
- User sends >20 messages without resolution → auto-escalate

### System Prompt as Versioned Artifact

| Version | Date | Change | Test Results | Status |
|---------|------|--------|-------------|--------|
| 1.0.0 | 2025-05-20 | Initial prompt | 21/23 pass (91%) | Active |
| 1.0.1 | — | Planned: Improve billing dispute handling | — | Draft |

Rollback procedure: `UPDATE prompt_versions SET is_active = FALSE WHERE version_tag = 'current'; UPDATE prompt_versions SET is_active = TRUE WHERE version_tag = 'previous';` — takes effect on next conversation (no restart required).

---

## Phase 5–6: Testing & Implementation

### Test Plan Summary

| Test Type | Count | Automation | Gate |
|-----------|-------|-----------|------|
| Golden conversation regression | 23 | Fully automated (LLM-as-judge) | CI: block deploy if <90% pass |
| Unit tests (orchestrator, RAG) | ~50 | pytest | CI: block if coverage <80% |
| Integration tests (Intercom, Stripe) | ~15 | pytest + mocked APIs | CI: block |
| Security tests (injection, auth) | ~10 | pytest | CI: block |
| Load test (50 concurrent) | 1 suite | k6 | Pre-release: manual |
| End-to-end (staging + real Intercom sandbox) | 5 scenarios | Semi-automated | Pre-release: manual |

### Implementation Milestones

| Milestone | Tasks | Target | Dependencies |
|-----------|-------|--------|-------------|
| M1: RAG Pipeline | KB sync, embedding, Pinecone setup, search API | Week 1-2 | Notion API access |
| M2: Orchestrator Core | Execution loop, intent classification, tool dispatch | Week 2-4 | M1 |
| M3: Integrations | Stripe client, CloudStore API client, Intercom webhook + reply | Week 3-5 | API keys provisioned |
| M4: Safety & Prompt | System prompt v1, guardrails, input sanitization | Week 4-6 | M2 |
| M5: Testing & Monitoring | Golden conversations, CI pipeline, dashboards, alerts | Week 5-7 | M2, M3, M4 |
| M6: Staging & Launch | Staging deploy, load test, canary 10%, full rollout | Week 7-8 | All |

---

## Output Structure Generated

```
engineering-spec/
├── 00_Overview/
│   ├── SUMMARY.md
│   ├── REQUIREMENTS_MATRIX.md
│   ├── DECISION_LOG.md              ← 6 ADRs (LLM choice, vector DB, hosting, etc.)
│   └── TECH_STACK.md
├── 01_Requirements/
│   ├── USER_STORIES.md              ← 3 P0 stories + 2 P1 stories
│   ├── FUNCTIONAL_REQS.md           ← 7 functional requirements
│   └── NON_FUNCTIONAL_REQS.md       ← Latency, availability, scale, cost, security
├── 02_Technical_Design/
│   ├── ARCHITECTURE.md              ← Component diagram + technology decisions
│   ├── DATA_MODEL.md                ← 3 entities with full schemas
│   ├── API_SPEC.md                  ← 3 internal + 5 external interfaces
│   ├── BUSINESS_LOGIC.md            ← Escalation rules, confidence thresholds
│   └── agent/
│       ├── AI_COMPONENTS.md         ← Execution loop, skills, tools, memory, RAG
│       ├── SYSTEM_PROMPT_SPEC.md    ← Full prompt, versioning, variables
│       └── CONVERSATIONS.md         ← 23 golden conversations
├── 03_Security/
│   ├── AUTH_DESIGN.md               ← Webhook auth, user isolation, token scoping
│   ├── DATA_SECURITY.md             ← Classification, encryption, PII handling
│   └── AUDIT_SPEC.md                ← Events, log format, retention
├── 04_Operations/
│   ├── DEPLOYMENT.md                ← Railway, CI/CD, blue-green rollout
│   ├── CONFIGURATION.md             ← 10 env vars with types/defaults
│   ├── MONITORING.md                ← 6 metrics + alert thresholds
│   └── RUNBOOK.md                   ← LLM failover, Pinecone outage, cost spike
├── 05_Testing/
│   ├── TEST_PLAN.md                 ← 6 test types with automation + gates
│   └── ACCEPTANCE_TESTS.md          ← Gherkin scenarios from user stories
├── 06_Implementation/
│   ├── TASK_BREAKDOWN.md            ← ~25 tasks across 6 milestones
│   ├── MILESTONES.md                ← M1-M6, 8-week timeline
│   ├── RISKS.md                     ← 5 risks (LLM quality, cost overrun, etc.)
│   └── MIGRATION.md                 ← N/A (greenfield)
└── SPEC_INDEX.md
```

---

## Key Takeaways

1. **Engineering Lenses caught gaps the PRD missed** — the Failure lens forced explicit circuit breaker design for 4 services; the Security lens caught that Stripe keys needed read-only scoping; the Replicability lens identified 3 missing environment variable docs.

2. **Agent-specific specs add significant depth** — the orchestrator execution loop, system prompt versioning, and golden conversation test suite are not covered by standard engineering spec practices. The `agent-system-spec.md` reference was essential.

3. **The 03_Security/ and 04_Operations/ directories** ensured security and ops weren't afterthoughts. The data classification table revealed that billing data should never be stored locally — a design decision that affects the entire architecture.

4. **Replicability verification** is the ultimate quality check. Walking through the checklist at the end exposed that the Intercom webhook retry behavior hadn't been documented, which would have caused debugging confusion for a new team.
