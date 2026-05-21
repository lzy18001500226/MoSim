# Agent Protocols & Standards

Protocol standards for the agent ecosystem — standardizing tool invocation, agent communication, and context sharing.

---

## Why Protocol Standards?

```
A world without standards:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Agent A ──(custom format)──► Tool 1                            │
│   Agent B ──(another format)─► Tool 1  ✗ Incompatible            │
│   Agent A ──────────────────► Agent B  ✗ Cannot communicate      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

A world with standards:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Agent A ──(std protocol)──► Tool 1   ✓                         │
│   Agent B ──(std protocol)──► Tool 1   ✓                         │
│   Agent A ──(std protocol)──► Agent B  ✓                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Major Protocol Standards

### 1. MCP (Model Context Protocol) - Anthropic

**Purpose:** Standardize how LLMs connect with external data sources and tools

```
┌─────────────────────────────────────────────────────────────────┐
│                   MCP Architecture                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐         ┌──────────┐         ┌──────────┐       │
│   │   Host   │◄───────►│  Server  │◄───────►│ Resource │       │
│   │ (Claude) │   MCP   │ (Adapter)│  Native │ (DB/API) │       │
│   └──────────┘         └──────────┘         └──────────┘       │
│                                                                 │
│   Host: LLM application                                         │
│   Server: MCP server, exposes resources                         │
│   Resource: Actual data source or tool                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**MCP Core Concepts:**

| Concept | Description |
|------|------|
| **Resources** | Data resources (files, DB records, etc.) |
| **Tools** | Executable operations |
| **Prompts** | Predefined prompt templates |
| **Sampling** | Request LLM to generate content |

**MCP Tool Definition Example:**
```json
{
  "name": "query_database",
  "description": "Execute a SQL query against the database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "SQL query to execute"
      }
    },
    "required": ["query"]
  }
}
```

**MCP Specification in PRD:**
```yaml
mcp_integration:
  enabled: true
  
  servers:
    - name: database_server
      transport: stdio
      command: "npx @mcp/database-server"
      config:
        connection_string: "${DB_URL}"
        
    - name: filesystem_server
      transport: http
      url: "http://localhost:3001"
      
  resources:
    - server: database_server
      expose: [users, orders, products]
      
  tools:
    - server: database_server
      expose: [query, insert, update]
      permissions: [query]  # Query only
```

### 2. OpenAI Function Calling

**Format Standard:**
```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Get the current weather in a location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g. San Francisco, CA"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"]
        }
      },
      "required": ["location"]
    }
  }
}
```

**Call Response:**
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "get_weather",
    "arguments": "{\"location\": \"San Francisco, CA\", \"unit\": \"celsius\"}"
  }
}
```

### 3. Agent Protocol (Open Standard)

**Purpose:** Communication standard between agents

**Core Endpoints:**
```
POST /ap/v1/agent/tasks            # Create task
GET  /ap/v1/agent/tasks/{id}       # Get task status
POST /ap/v1/agent/tasks/{id}/steps # Execute step
GET  /ap/v1/agent/tasks/{id}/artifacts # Get artifacts
```

**Task Lifecycle:**
```
Create task → Execute steps → ... → Complete/Fail
    │           │
    ▼           ▼
 pending    running    completed/failed
```

---

## Protocol Selection Guide

| Scenario | Recommended Protocol | Reason |
|------|----------|------|
| Claude apps | MCP | Native Anthropic support |
| OpenAI apps | Function Calling | Native OpenAI support |
| Multi-agent systems | Agent Protocol | Inter-agent interop |
| Mixed environments | MCP + adapter layer | MCP is more general |

---

## Protocol Compatibility Design

### Adapter Pattern

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│   ┌────────┐    ┌────────────┐    ┌────────────────────────┐ │
│   │ Agent  │───►│  Adapter   │───►│ Tool Implementation    │ │
│   │        │    │            │    │                        │ │
│   └────────┘    │ MCP ──────►│    │                        │ │
│                 │ OpenAI ───►│    │                        │ │
│                 │ Custom ───►│    │                        │ │
│                 └────────────┘    └────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Unified Tool Definition

Design tools using an intermediate format that compiles to different protocols:

```yaml
# Unified tool definition
tool:
  name: search_documents
  description: Search for documents in the knowledge base
  
  parameters:
    - name: query
      type: string
      required: true
      description: Search query
      
    - name: limit
      type: integer
      required: false
      default: 10
      description: Maximum results to return
      
  returns:
    type: array
    items:
      type: object
      properties:
        title: string
        content: string
        score: number
        
  # Protocol-specific configuration
  protocols:
    mcp:
      server: knowledge_server
    openai:
      strict: true
    anthropic:
      cache_control: ephemeral
```

---

## Agent Communication Patterns

### Pattern 1: Direct Call

```
Agent A ──(request)──► Agent B
        ◄──(response)──
```

### Pattern 2: Message Queue

```
Agent A ──► Queue ──► Agent B
        ◄── Queue ◄──
```

### Pattern 3: Publish/Subscribe

```
Agent A ──(publish)──► Topic
                          │
                          ├──► Agent B (subscribe)
                          └──► Agent C (subscribe)
```

### Pattern 4: Coordinator Pattern

```
             Coordinator
            /    │    \
           /     │     \
       Agent A  Agent B  Agent C
```

---

## Message Format Standards

### Agent Message Envelope

```json
{
  "message_id": "msg_123",
  "timestamp": "2024-01-15T10:30:00Z",
  "protocol_version": "1.0",
  
  "sender": {
    "agent_id": "agent_a",
    "agent_type": "researcher"
  },
  
  "recipient": {
    "agent_id": "agent_b",
    "agent_type": "writer"
  },
  
  "message_type": "task_request",
  
  "payload": {
    "task": "Write a summary",
    "context": {...},
    "constraints": {...}
  },
  
  "metadata": {
    "priority": "normal",
    "timeout_seconds": 300,
    "trace_id": "trace_456"
  }
}
```

### Common Message Types

| Type | Purpose |
|------|------|
| `task_request` | Request task execution |
| `task_response` | Task execution result |
| `status_update` | Status update |
| `query` | Query information |
| `notification` | Notification |
| `error` | Error report |

---

## Protocol Specification in PRD

```markdown
## Protocol & Integration Specification

### Tool Invocation Protocol

**Primary protocol:** [MCP / OpenAI Function Calling / Custom]

**Version:** [protocol version]

**Tool exposure:**
| Tool | Protocol | Permissions | Rate Limit |
|------|------|------|----------|
| [tool] | [protocol] | [permissions] | [limit] |

### Agent Communication Protocol

**Internal communication:** [protocol/format]
**External communication:** [protocol/format]

**Message format:**
```json
{
  // Message structure
}
```

### Compatibility

| Target System | Protocol | Adapter |
|----------|------|--------|
| [system] | [protocol] | [needed Y/N] |

### Extension Points

Extension points reserved for future protocols:
- [Extension point 1]
- [Extension point 2]
```

---

## Future Trends

| Trend | Description | PRD Consideration |
|------|------|----------|
| **Protocol convergence** | MCP etc. may become mainstream | Keep designs protocol-agnostic |
| **Agent marketplace** | Agents as services | Standardized interfaces |
| **Federated agents** | Cross-org agent collaboration | Trust and auth mechanisms |
| **Real-time protocols** | WebSocket/SSE dominant | Support streaming communication |
