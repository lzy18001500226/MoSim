# Memory Architecture Patterns

How to design agent memory systems for stateful, context-aware, and personalized interactions.

---

## Memory Types Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Memory Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   WORKING MEMORY                        │   │
│  │   Current conversation context                          │   │
│  │   Scope: Single turn    Persistence: None               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   SHORT-TERM MEMORY                     │   │
│  │   Session context, recent exchanges                      │   │
│  │   Scope: Session        Persistence: Temporary          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   LONG-TERM MEMORY                      │   │
│  │   User preferences, history, learned patterns            │   │
│  │   Scope: Cross-session  Persistence: Permanent          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   EXTERNAL MEMORY                       │   │
│  │   Knowledge bases, RAG, external databases              │   │
│  │   Scope: Shared         Persistence: External           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Memory Type Specifications

### Working Memory (Context Window)

The agent's immediate context—what's in the current prompt.

| Attribute | Specification |
|-----------|---------------|
| **Capacity** | Limited by context window (e.g., 128K tokens) |
| **Persistence** | Current request only |
| **Contents** | System prompt, conversation history, current input |
| **Management** | Truncation strategy when exceeded |

#### Working Memory Management

**Truncation Strategies:**

| Strategy | Description | Use When |
|----------|-------------|----------|
| **FIFO** | Remove oldest messages first | General conversation |
| **Importance-based** | Keep system prompt + recent + marked important | Complex workflows |
| **Summarization** | Compress older context into summary | Long conversations |
| **Sliding Window** | Keep last N turns only | High-volume chat |

**Priority Order for Retention:**
1. System prompt (always keep)
2. User's current message
3. Recent assistant response
4. Critical context (marked important)
5. Older conversation (truncate if needed)

### Short-Term Memory (Session)

Information that persists within a single user session.

| Attribute | Specification |
|-----------|---------------|
| **Capacity** | Configurable (typically unlimited) |
| **Persistence** | Until session ends |
| **Contents** | Full conversation, temporary state, task progress |
| **Storage** | In-memory / session store |

#### Session Memory Schema

```json
{
  "session_id": "uuid",
  "user_id": "uuid",
  "started_at": "timestamp",
  "last_activity": "timestamp",
  
  "conversation": [
    {
      "role": "user|assistant",
      "content": "...",
      "timestamp": "...",
      "metadata": {}
    }
  ],
  
  "context": {
    "current_task": "...",
    "task_state": {},
    "entities_mentioned": [],
    "preferences_this_session": {}
  },
  
  "temporary_data": {
    "draft_content": "...",
    "pending_confirmation": {}
  }
}
```

### Long-Term Memory (Persistent)

Information that persists across sessions—user preferences, interaction history, learned patterns.

| Attribute | Specification |
|-----------|---------------|
| **Capacity** | Large (database-limited) |
| **Persistence** | Permanent (with retention policy) |
| **Contents** | Preferences, history, learned facts |
| **Storage** | Vector DB, document store, relational DB |

#### Long-Term Memory Categories

| Category | Contents | Use |
|----------|----------|-----|
| **User Profile** | Preferences, settings, attributes | Personalization |
| **Interaction History** | Past conversations (summarized) | Context |
| **Learned Facts** | User-shared information | Recall |
| **Behavioral Patterns** | Usage patterns, preferences | Adaptation |

#### Long-Term Memory Schema

```json
{
  "user_id": "uuid",
  
  "profile": {
    "name": "...",
    "preferences": {
      "communication_style": "formal|casual",
      "verbosity": "concise|detailed",
      "topics_of_interest": []
    },
    "settings": {}
  },
  
  "facts": [
    {
      "fact_id": "uuid",
      "content": "User's company is Acme Corp",
      "source": "user_stated",
      "confidence": 1.0,
      "created_at": "timestamp",
      "last_used": "timestamp"
    }
  ],
  
  "history": {
    "total_interactions": 150,
    "topics_discussed": ["topic1", "topic2"],
    "recent_summaries": [
      {
        "session_id": "...",
        "summary": "Discussed project planning...",
        "key_outcomes": []
      }
    ]
  },
  
  "patterns": {
    "typical_usage_time": "morning",
    "common_tasks": ["scheduling", "research"],
    "feedback_patterns": {}
  }
}
```

---

## Memory Patterns

### Pattern 1: Stateless (No Memory)

Simplest pattern—no memory beyond current context.

```
Request → Agent → Response
         (no state)
```

**Use when:**
- Simple Q&A
- No personalization needed
- Privacy-first applications

**Specification:**
```yaml
memory:
  working: context_window_only
  session: none
  long_term: none
```

### Pattern 2: Session Memory Only

Memory within session, forgotten after.

```
Session Start
    ↓
[Request → Agent → Response] (accumulating context)
[Request → Agent → Response]
[Request → Agent → Response]
    ↓
Session End (memory cleared)
```

**Use when:**
- Task-focused interactions
- Privacy-sensitive contexts
- Ephemeral assistants

**Specification:**
```yaml
memory:
  working: 
    capacity: 100K tokens
    truncation: summarization
  session:
    enabled: true
    timeout: 30 minutes
    max_turns: 100
  long_term: none
```

### Pattern 3: User Profile Memory

Persistent user preferences and settings, no conversation history.

```
[User Profile] (persistent)
      ↓
Session Start
      ↓
[Profile loaded into context]
      ↓
[Conversation] (session only)
      ↓
Session End
      ↓
[Profile updates saved]
```

**Use when:**
- Personalization needed
- History not required
- Preference-driven agents

**Specification:**
```yaml
memory:
  working:
    includes: [system_prompt, user_profile, conversation]
  session:
    enabled: true
  long_term:
    enabled: true
    contents: [profile, preferences, settings]
    excludes: [conversation_history, facts]
```

### Pattern 4: Full Memory

Complete memory—profile, facts, and summarized history.

```
[Long-Term Memory]
├── User Profile
├── Learned Facts
└── Conversation Summaries
         ↓
Session Start
         ↓
[Relevant memories retrieved and loaded]
         ↓
[Conversation with full context]
         ↓
Session End
         ↓
[New facts extracted and stored]
[Session summarized and stored]
```

**Use when:**
- Personal assistant use cases
- Relationship-building agents
- Complex, ongoing tasks

**Specification:**
```yaml
memory:
  working:
    capacity: 128K tokens
    priority: [system_prompt, relevant_memories, recent_conversation]
  session:
    enabled: true
    persist_to_long_term: true
  long_term:
    enabled: true
    contents:
      - profile
      - preferences
      - facts
      - conversation_summaries
    retrieval:
      method: semantic_search
      top_k: 10
    retention:
      facts: indefinite
      summaries: 90_days
```

### Pattern 5: Shared Team Memory

Memory shared across team members (with permissions).

```
[Team Knowledge Base] (shared)
[User A Profile] (private)
[User B Profile] (private)
         ↓
Session (User A)
         ↓
[Team knowledge + User A profile loaded]
         ↓
[Updates to team knowledge visible to team]
[Updates to profile visible only to User A]
```

**Use when:**
- Team collaboration tools
- Shared workspace assistants
- Enterprise agents

**Specification:**
```yaml
memory:
  scopes:
    personal:
      owner: user
      contents: [profile, preferences, personal_facts]
    team:
      owner: team
      contents: [shared_knowledge, team_facts, workflows]
      permissions: [read, write_with_approval]
    global:
      owner: organization
      contents: [policies, procedures, company_knowledge]
      permissions: [read_only]
```

---

## Memory Operations

### Storing Memories

When to store and what to store:

| Trigger | What to Store | Where |
|---------|---------------|-------|
| User states preference | Preference | Long-term / Profile |
| User shares fact | Fact with attribution | Long-term / Facts |
| Session ends | Conversation summary | Long-term / History |
| Task completes | Outcome and learnings | Long-term / Patterns |
| User explicitly asks | Whatever user specifies | Long-term / Facts |

### Retrieving Memories

How to retrieve relevant memories:

| Method | Description | Use When |
|--------|-------------|----------|
| **Always Include** | Profile, critical preferences | Every interaction |
| **Semantic Search** | Query-relevant memories | User asks about past |
| **Recency-based** | Recent interactions | Continuing work |
| **Task-based** | Memories related to task type | Specialized tasks |

### Updating Memories

When to update vs. add new:

| Scenario | Action |
|----------|--------|
| New preference stated | Update existing or add new |
| Conflicting information | Ask user to clarify, then update |
| Time-sensitive information | Update with timestamp |
| User explicitly corrects | Update with high confidence |

### Forgetting Memories

When and how to remove memories:

| Trigger | Action |
|---------|--------|
| User requests deletion | Delete immediately |
| Retention period expires | Auto-delete |
| Conflicting information | Archive old, add new |
| Low-confidence + old | Candidate for cleanup |

---

## Memory Retrieval Strategies

### Strategy 1: Always Available

Certain memories always in context:

```yaml
always_include:
  - user_name
  - core_preferences
  - critical_facts (flagged)
```

### Strategy 2: Query-Time Retrieval

Retrieve based on current query:

```yaml
retrieval:
  trigger: every_query
  method: semantic_similarity
  query_source: user_message
  top_k: 5
  threshold: 0.7
```

### Strategy 3: Predictive Loading

Predict what memories will be needed:

```yaml
retrieval:
  trigger: session_start
  method: predict_from_history
  preload:
    - recent_topics
    - common_tasks
    - pending_items
```

---

## Privacy & Compliance

### User Control Requirements

| Control | Implementation |
|---------|----------------|
| View memories | API/UI to see all stored memories |
| Edit memories | Ability to correct facts |
| Delete memories | Delete specific or all memories |
| Export memories | Download all data |
| Opt-out | Disable memory entirely |

### Data Classification

| Category | Handling |
|----------|----------|
| PII | Encrypt, limit access, honor deletion |
| Preferences | Standard storage |
| Conversation | Summarize, don't store verbatim (unless opted in) |
| Sensitive topics | Don't store without explicit consent |

### Retention Policies

| Data Type | Retention | Justification |
|-----------|-----------|---------------|
| Preferences | Indefinite (until deleted) | Core functionality |
| Facts | Indefinite (until deleted) | User value |
| Session logs | 30 days | Debugging |
| Conversation summaries | 90 days | Context |
| Full conversations | 7 days (if stored) | Short-term debugging |

---

## Memory Specification Template

```yaml
memory:
  # Working Memory
  working:
    max_tokens: 128000
    priority_order:
      - system_prompt
      - user_profile
      - relevant_memories
      - recent_conversation
    truncation_strategy: summarize_middle

  # Session Memory
  session:
    enabled: true
    timeout_minutes: 60
    max_turns: 200
    persist_on_end: true
    
  # Long-Term Memory
  long_term:
    enabled: true
    storage: vector_db
    
    contents:
      profile:
        fields: [name, preferences, settings]
        update_policy: explicit_only
        
      facts:
        max_count: 1000
        confidence_threshold: 0.7
        deduplication: true
        
      history:
        store_summaries: true
        store_verbatim: false
        summary_retention_days: 90
        
    retrieval:
      method: hybrid  # semantic + keyword
      top_k: 10
      min_similarity: 0.6
      
    privacy:
      user_can_view: true
      user_can_edit: true
      user_can_delete: true
      encryption: at_rest_and_transit
      pii_handling: redact_in_summaries
```
