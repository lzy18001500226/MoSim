# Tools Specification Guide

How to define agent tools—external capabilities that agents can invoke to interact with systems, data, and the real world.

---

## What is a Tool?

A **Tool** is an external capability that an agent can invoke to perform actions outside its internal reasoning. Tools are the agent's "hands" for interacting with the world.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Tool Anatomy                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   NAME ─────────► Identifier for the tool                       │
│                                                                 │
│   DESCRIPTION ──► What it does (for LLM understanding)          │
│                                                                 │
│   PARAMETERS ───► What inputs it accepts                        │
│                                                                 │
│   EXECUTION ────► How it's called (API, function, etc.)         │
│                                                                 │
│   RESPONSE ─────► What it returns                               │
│                                                                 │
│   SAFETY ───────► Permissions, confirmation, audit              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tool Categories

### By Action Type

| Category | Description | Risk Level | Examples |
|----------|-------------|------------|----------|
| **Read** | Retrieve information | Low | Search, fetch data, read file |
| **Write** | Modify data | Medium | Update record, save file |
| **Execute** | Trigger actions | High | Send email, make purchase |
| **Delete** | Remove data | High | Delete record, clear cache |

### By Integration Type

| Category | Description | Examples |
|----------|-------------|----------|
| **API** | External web services | REST APIs, GraphQL |
| **Database** | Data storage | SQL queries, document DB |
| **File System** | File operations | Read/write files |
| **System** | OS-level actions | Run commands, access hardware |
| **Communication** | Messaging | Email, SMS, notifications |

---

## Tool Specification Template

### Tool: [Name]

```markdown
## Tool: [tool_name]

### 1. Overview

**Name:** `[tool_name]`  
**Category:** [Read/Write/Execute/Delete]  
**Risk Level:** [Low/Medium/High/Critical]  
**Description:** [What this tool does - written for LLM comprehension]

### 2. When to Use

**Use this tool when:**
- [Condition 1]
- [Condition 2]

**Do NOT use this tool when:**
- [Anti-condition 1]
- [Anti-condition 2]

**Prefer alternatives when:**
| Situation | Better Alternative |
|-----------|-------------------|
| [Situation] | [Alternative tool] |

### 3. Interface Definition

```json
{
  "type": "function",
  "function": {
    "name": "[tool_name]",
    "description": "[Detailed description for LLM - include what it does, when to use, what it returns]",
    "parameters": {
      "type": "object",
      "properties": {
        "[param1]": {
          "type": "[type]",
          "description": "[Description for LLM]",
          "enum": ["[if applicable]"]
        },
        "[param2]": {
          "type": "[type]",
          "description": "[Description]"
        }
      },
      "required": ["[required_params]"]
    }
  }
}
```

### 4. Parameter Details

| Parameter | Type | Required | Default | Validation | Description |
|-----------|------|----------|---------|------------|-------------|
| [param] | [type] | [Y/N] | [default] | [validation rules] | [description] |

#### Parameter Constraints

**[param1]:**
- Minimum: [value]
- Maximum: [value]
- Pattern: [regex if applicable]
- Allowed values: [enum if applicable]

### 5. Execution Details

| Attribute | Value |
|-----------|-------|
| **Endpoint** | `[URL or function path]` |
| **Method** | [GET/POST/PUT/DELETE] |
| **Authentication** | [Method: API key, OAuth, etc.] |
| **Timeout** | [Duration in seconds] |
| **Rate Limit** | [X requests per Y time] |
| **Retry Policy** | [Retry on 5xx? How many times?] |

#### Request Format
```http
POST /api/endpoint HTTP/1.1
Host: example.com
Authorization: Bearer {token}
Content-Type: application/json

{
  "param1": "value1",
  "param2": "value2"
}
```

### 6. Response Handling

#### Success Response (2xx)
```json
{
  "success": true,
  "data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

**Agent interpretation:** [How agent should understand this response]

#### Error Responses

| Status | Meaning | Agent Response |
|--------|---------|----------------|
| 400 | Bad request | Report input error to user |
| 401 | Unauthorized | Request re-authentication |
| 403 | Forbidden | Report permission issue |
| 404 | Not found | Report resource not found |
| 429 | Rate limited | Wait and retry |
| 500 | Server error | Retry or report issue |

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "[error_code]",
    "message": "[human_readable_message]"
  }
}
```

### 7. Safety Specification

#### Permission Model
| Requirement | Value |
|-------------|-------|
| **Required Role** | [Role needed] |
| **Required Scope** | [OAuth scope if applicable] |
| **User Consent** | [When/if needed] |

#### Destructive Assessment
| Question | Answer |
|----------|--------|
| Can this modify data? | [Yes/No] |
| Can this delete data? | [Yes/No] |
| Is this reversible? | [Yes/No] |
| Can this cost money? | [Yes/No] |
| Can this affect others? | [Yes/No] |

#### Confirmation Requirements
| Condition | Confirmation Type |
|-----------|-------------------|
| [When confirmation needed] | [How to confirm] |

#### Audit Requirements
| Field | Logged |
|-------|--------|
| Tool name | Yes |
| Parameters | [Yes/Redacted/No] |
| User ID | Yes |
| Timestamp | Yes |
| Result status | Yes |
| Result data | [Yes/Redacted/No] |

### 8. Examples

#### Example 1: Successful Use

**Scenario:** [Description]

**Agent decides to use tool:**
```
Reasoning: User asked to [action]. I should use [tool_name] because [reason].
```

**Tool call:**
```json
{
  "name": "[tool_name]",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Agent interpretation:**
```
The tool returned [interpretation]. I can now [next action].
```

#### Example 2: Error Handling

**Scenario:** [Error scenario]

**Tool call:**
```json
{
  "name": "[tool_name]",
  "parameters": {
    "param1": "invalid_value"
  }
}
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAM",
    "message": "param1 must be..."
  }
}
```

**Agent recovery:**
```
The tool returned an error because [reason]. I should [recovery action].
```

### 9. Edge Cases

| Scenario | Tool Behavior | Agent Should |
|----------|---------------|--------------|
| [Edge case] | [Behavior] | [Action] |

### 10. Dependencies

| Dependency | Type | Required |
|------------|------|----------|
| [Dependency] | [Type] | [Y/N] |

### 11. Version & Changelog

| Version | Date | Changes |
|---------|------|---------|
| [X.Y] | [Date] | [Changes] |
```

---

## Tool Design Patterns

### Pattern 1: Idempotent Read
Tools that can be safely called multiple times without side effects.

```
GET /api/resource/{id}

- Safe to retry
- No confirmation needed
- Cache responses when possible
```

### Pattern 2: Confirmed Write
Tools that modify data with user confirmation.

```
User: "Update my email"
Agent: "I'll update your email to new@example.com. Confirm?"
User: "Yes"
Agent: [calls update_email tool]
```

### Pattern 3: Atomic Transaction
Tools that must complete fully or not at all.

```
1. Begin transaction
2. Execute steps
3. Commit or rollback

Handle partial failures by rolling back.
```

### Pattern 4: Async with Callback
Tools that take time and report results later.

```
1. Agent submits job
2. Tool returns job_id
3. Agent polls or receives callback
4. Agent reports final result
```

### Pattern 5: Paginated Results
Tools that return large datasets in pages.

```
1. Call with page=1
2. Receive results + has_more=true
3. Call with page=2
4. Continue until has_more=false
```

---

## Tool Safety Matrix

Use this matrix to determine safety requirements:

| Tool Type | Confirmation | Audit | Rate Limit | Undo |
|-----------|--------------|-------|------------|------|
| Read (public) | No | Optional | Light | N/A |
| Read (private) | No | Yes | Light | N/A |
| Write (draft) | No | Yes | Medium | Yes |
| Write (publish) | Yes | Yes | Medium | Maybe |
| Delete (soft) | Yes | Yes | Medium | Yes |
| Delete (hard) | Double | Yes | Strict | No |
| Execute (internal) | Context | Yes | Medium | Varies |
| Execute (external) | Yes | Yes | Strict | No |
| Financial | Always | Yes | Strict | Varies |

---

## Tool Description Best Practices

The description field is crucial—it's how the LLM decides when to use the tool.

### Good Descriptions

✅ **Specific:**
```
"Search the company knowledge base for documents matching the query. 
Returns up to 10 results with title, snippet, and relevance score. 
Use when user asks about company policies, procedures, or documentation."
```

✅ **Includes constraints:**
```
"Send an email to the specified recipient. 
Maximum 5 recipients. 
Subject max 200 characters. 
Body max 10,000 characters. 
Requires user confirmation before sending."
```

✅ **Clear on when to use:**
```
"Calculate the total price including tax and discounts. 
Use this instead of manual calculation to ensure accuracy with 
current tax rates and valid discount codes."
```

### Bad Descriptions

❌ **Too vague:**
```
"Search for things."
```

❌ **Missing constraints:**
```
"Send email."
```

❌ **No usage guidance:**
```
"Processes user request."
```

---

## Tool Testing Checklist

### Functional Tests
- [ ] Successful call with valid parameters
- [ ] Each parameter validation works
- [ ] Each error code handled correctly
- [ ] Timeout behavior correct
- [ ] Retry logic works

### Security Tests
- [ ] Authentication required and enforced
- [ ] Authorization checked correctly
- [ ] Input sanitization works
- [ ] Output doesn't leak sensitive data
- [ ] Audit logging captures all calls

### Integration Tests
- [ ] Agent selects tool appropriately
- [ ] Agent interprets response correctly
- [ ] Agent handles errors gracefully
- [ ] Agent respects rate limits
- [ ] Agent asks for confirmation when required

### Edge Case Tests
- [ ] Empty input
- [ ] Maximum input size
- [ ] Special characters
- [ ] Concurrent calls
- [ ] Service unavailable

---

## Tool Documentation Checklist

Before finalizing a tool specification:

- [ ] Name follows naming convention
- [ ] Description is LLM-friendly
- [ ] All parameters documented
- [ ] Validation rules specified
- [ ] Success response documented
- [ ] All error codes covered
- [ ] Safety assessment complete
- [ ] Confirmation rules defined
- [ ] Audit requirements specified
- [ ] Examples include success and error cases
- [ ] Edge cases documented
- [ ] Version tracked
