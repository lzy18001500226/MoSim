#!/usr/bin/env bash
set -euo pipefail

# generate_spec_skeleton.sh - Create the engineering spec output directory structure
# Updated to match v2 structure with 03_Security/, 04_Operations/
# Usage: generate_spec_skeleton.sh [output_root] [--force] [--agent]

usage() {
  cat <<'EOF'
Usage:
  generate_spec_skeleton.sh [output_root] [--force] [--agent]

Creates the standard engineering spec output directory structure with templates.
Default output_root is ./engineering-spec

Options:
  --force    Overwrite existing files (default: skip existing)
  --agent    Include agent-specific spec files (AI agent systems)
EOF
}

out_root="engineering-spec"
force=0
agent=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -f|--force) force=1; shift ;;
    --agent) agent=1; shift ;;
    *)
      if [[ "$1" == -* ]]; then
        echo "Unknown option: $1" >&2; usage; exit 2
      fi
      out_root="$1"; shift ;;
  esac
done

mkdir -p "$out_root"

# Core directories
dirs=(
  "00_Overview"
  "01_Requirements"
  "02_Technical_Design"
  "02_Technical_Design/schemas"
  "02_Technical_Design/openapi"
  "03_Security"
  "04_Operations"
  "05_Testing"
  "05_Testing/test-cases"
  "06_Implementation"
)

for d in "${dirs[@]}"; do mkdir -p "$out_root/$d"; done

write_file() {
  local path="$1" content="$2"
  if [[ -f "$path" && $force -eq 0 ]]; then echo "skip: $path"; return; fi
  printf "%s\n" "$content" > "$path"
  echo "write: $path"
}

# ── 00_Overview ────────────────────────────────────────────────

write_file "$out_root/00_Overview/SUMMARY.md" "# Engineering Specification Summary

## Document Info
- **Project:** [Project Name]
- **Version:** 1.0
- **Status:** [Draft | In Review | Approved]
- **Author:** [Name]
- **Last Updated:** [Date]

## Executive Summary
[One paragraph overview]

## Scope
### In Scope
- [Feature/capability]

### Out of Scope
- [What this does NOT cover]

## Key Decisions
| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| [decision] | [choice] | [why] | [date] |

## Document Index
- 00_Overview/ — Summary, traceability, decisions, tech stack
- 01_Requirements/ — User stories, functional & non-functional requirements
- 02_Technical_Design/ — Architecture, data model, API, business logic
- 03_Security/ — Auth, data security, audit
- 04_Operations/ — Deployment, config, monitoring, runbook
- 05_Testing/ — Test plan, acceptance tests
- 06_Implementation/ — Tasks, milestones, risks, migration"

write_file "$out_root/00_Overview/REQUIREMENTS_MATRIX.md" "# Requirements Traceability Matrix

| User Story | Functional Req | Tech Spec | Security | Test Coverage | Status |
|------------|----------------|-----------|----------|---------------|--------|
| US-001 | FR-001 | ARCH-001 | AUTH-001 | UT-001, IT-001 | ✅ |

## Coverage Summary
- Total Requirements: [count]
- Full Coverage: [count] ([%])
- Gaps: [list]"

write_file "$out_root/00_Overview/DECISION_LOG.md" "# Architecture Decision Log

## ADR-001: [Decision Title]
**Date:** [Date] | **Status:** [Proposed|Accepted|Deprecated]

### Context
[Why this decision is needed]

### Options Considered
| Option | Pros | Cons |
|--------|------|------|
| A: [name] | [benefits] | [drawbacks] |
| B: [name] | [benefits] | [drawbacks] |

### Decision
[What was decided and why]

### Consequences
[Positive and negative impacts]"

write_file "$out_root/00_Overview/TECH_STACK.md" "# Technology Stack

| Layer | Technology | Version | Rationale | Alternatives Considered |
|-------|-----------|---------|-----------|------------------------|
| Language | [lang] | [ver] | [why] | [alternatives] |
| Framework | [framework] | [ver] | [why] | [alternatives] |
| Database | [db] | [ver] | [why] | [alternatives] |
| Cache | [cache] | [ver] | [why] | [alternatives] |

## External Dependencies
| Dependency | Purpose | Version Pinned | License | Risk |
|-----------|---------|---------------|---------|------|
| [dep] | [purpose] | [Y/N] | [license] | [level] |"

# ── 01_Requirements ────────────────────────────────────────────

write_file "$out_root/01_Requirements/USER_STORIES.md" "# User Stories

## US-001: [Story Title]
**Priority:** P0 | **Status:** Draft

**Story:** As a [role], I want to [action], so that [benefit].

**Acceptance Criteria:**
\`\`\`gherkin
Given [precondition]
When [action]
Then [expected result]
\`\`\`

**Business Rules:** BR-001
**Dependencies:** Blocks US-002"

write_file "$out_root/01_Requirements/FUNCTIONAL_REQS.md" "# Functional Requirements

### FR-001: [Requirement Title]
**Source:** US-001 | **Priority:** P0

**Description:** [What the system must do]

**Inputs:** [type, constraints]
**Outputs:** [type, format]
**Business Rules:** BR-001

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]"

write_file "$out_root/01_Requirements/NON_FUNCTIONAL_REQS.md" "# Non-Functional Requirements

## Performance
| ID | Requirement | Metric | Target | Verification |
|----|-------------|--------|--------|--------------|
| NFR-PERF-001 | API Response Time | P99 latency | <200ms | Load test |
| NFR-PERF-002 | Throughput | Requests/sec | >1000 | Load test |

## Availability
| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-AVAIL-001 | Uptime | 99.9% | Monthly |
| NFR-AVAIL-002 | RTO | <1 hour | DR test |
| NFR-AVAIL-003 | RPO | <5 minutes | DR test |

## Security
| ID | Requirement | Standard | Verification |
|----|-------------|----------|--------------|
| NFR-SEC-001 | Authentication | OAuth 2.0 | Security review |
| NFR-SEC-002 | Encryption | AES-256 at rest, TLS 1.3 transit | Audit |"

# ── 02_Technical_Design ────────────────────────────────────────

write_file "$out_root/02_Technical_Design/ARCHITECTURE.md" "# System Architecture

## Overview
[High-level description]

## Architecture Diagram
\`\`\`mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Service A]
    B --> D[Service B]
    C --> E[(Database)]
    C --> F[(Cache)]
\`\`\`

## Components
| Component | Purpose | Technology | Notes |
|-----------|---------|------------|-------|
| [name] | [purpose] | [tech] | [notes] |

## Communication
| From | To | Protocol | Pattern | Auth |
|------|-----|----------|---------|------|
| [src] | [dst] | [REST/gRPC] | [sync/async] | [method] |"

write_file "$out_root/02_Technical_Design/DATA_MODEL.md" "# Data Model

## Entity Relationship Diagram
\`\`\`mermaid
erDiagram
    ENTITY_A ||--o{ ENTITY_B : has
\`\`\`

## Entity: [EntityName]
**Purpose:** [What this represents]

| Field | Type | Null | Default | Constraints | Description |
|-------|------|------|---------|-------------|-------------|
| id | UUID | No | gen | PK | Identifier |
| created_at | timestamp | No | now() | - | Creation time |

**Indexes:**
| Name | Columns | Type | Purpose |
|------|---------|------|---------|

**Relationships:**
| Relation | Target | Type | FK | Cascade |
|----------|--------|------|-----|---------|"

write_file "$out_root/02_Technical_Design/API_SPEC.md" "# API Specification

## Overview
- Base URL: \`/api/v1\`
- Authentication: [method]
- Content-Type: application/json

## Common Error Format
\`\`\`json
{\"error\": {\"code\": \"ERROR_CODE\", \"message\": \"Description\", \"details\": []}}
\`\`\`

## Endpoints

### GET /api/v1/[resource]
**Purpose:** [Description] | **Auth:** Required | **Rate Limit:** [limit]

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|

**Response 200:** \`{\"data\": [], \"pagination\": {\"total\": 0, \"limit\": 20, \"offset\": 0}}\`

| Error Code | HTTP | Condition |
|-----------|------|-----------|
| UNAUTHORIZED | 401 | Missing/invalid token |"

write_file "$out_root/02_Technical_Design/BUSINESS_LOGIC.md" "# Business Logic

## Rule: BR-001 [Rule Name]
**Source:** US-001, FR-001 | **Priority:** Critical

**Description:** [What this rule enforces]
**Trigger:** [When evaluated]

\`\`\`pseudocode
IF condition THEN result_a ELSE result_b
\`\`\`

| Condition A | Condition B | Result |
|-------------|-------------|--------|
| True | True | X |
| True | False | Y |

**Edge Cases:**
| Case | Input | Expected | Rationale |
|------|-------|----------|-----------|"

# ── 03_Security (NEW) ─────────────────────────────────────────

write_file "$out_root/03_Security/AUTH_DESIGN.md" "# Authentication & Authorization Design

## Authentication Flow
\`\`\`mermaid
sequenceDiagram
    participant User
    participant Client
    participant Auth
    participant API
    User->>Client: Credentials
    Client->>Auth: Authenticate
    Auth-->>Client: Token
    Client->>API: Request + Token
    API-->>Client: Response
\`\`\`

## Token Specification
| Attribute | Value |
|-----------|-------|
| Type | [JWT / Session / API Key] |
| Lifetime | [duration] |
| Refresh Strategy | [method] |
| Storage (client) | [httpOnly cookie / memory] |
| Revocation | [method] |

## Authorization Model
[RBAC / ABAC / ReBAC]

| Role | Permissions | Scope |
|------|------------|-------|
| admin | [full] | global |
| user | [read, write own] | own resources |

## Enforcement Points
| Layer | Check | Implementation |
|-------|-------|---------------|
| Gateway | Token validity | [method] |
| Controller | Role permissions | [middleware] |
| Service | Resource ownership | [query filter] |
| Database | Row-level security | [RLS] |"

write_file "$out_root/03_Security/DATA_SECURITY.md" "# Data Security Specification

## Data Classification
| Level | Examples | Encryption | Access | Retention |
|-------|----------|-----------|--------|-----------|
| Public | Marketing | Optional | Anyone | Indefinite |
| Confidential | User emails | Transit + rest | Role-based | 2 years |
| Restricted | Passwords, SSN | All layers | Need-to-know | Minimum |

## Encryption
| Context | Method | Algorithm | Key Management |
|---------|--------|-----------|---------------|
| In transit | TLS | 1.3 | Auto |
| At rest | [method] | AES-256 | [KMS/Vault] |

## PII Handling
| Field | Storage | Display | Logging | Export |
|-------|---------|---------|---------|--------|

## Input Security
| Attack Vector | Prevention | Implementation |
|--------------|-----------|---------------|
| SQL Injection | Parameterized queries | ORM |
| XSS | Output encoding | Auto-escape |

## Secrets Management
| Secret Type | Storage | Rotation | Access |
|-------------|---------|----------|--------|"

write_file "$out_root/03_Security/AUDIT_SPEC.md" "# Audit & Compliance Specification

## Events to Log
| Category | Events | Data Captured |
|----------|--------|---------------|
| Authentication | Login, logout, failures | User ID, IP, timestamp |
| Authorization | Permission denied | User, resource, action |
| Data Access | Sensitive read/write | User, resource, fields |
| Admin Actions | Config changes | Admin, before/after |

## Log Format
\`\`\`json
{\"timestamp\":\"ISO-8601\",\"level\":\"INFO\",\"event_type\":\"auth.login\",\"actor\":{\"user_id\":\"\",\"ip\":\"\"},\"resource\":{\"type\":\"\",\"id\":\"\"},\"action\":\"\",\"result\":\"success\"}
\`\`\`

## PII in Logs
- NEVER log: passwords, tokens, full credit cards
- HASH: emails, phone, IP
- OK: user IDs, action types

## Retention
| Log Type | Retention | Access |
|----------|-----------|--------|
| Security | 1 year | Security team |
| Audit trail | 7 years | Compliance |
| Application | 90 days | Engineering |"

# ── 04_Operations (NEW) ───────────────────────────────────────

write_file "$out_root/04_Operations/DEPLOYMENT.md" "# Deployment Specification

## Environments
| Environment | Purpose | URL | Data |
|-------------|---------|-----|------|
| Development | Feature work | localhost | Seed data |
| Staging | Pre-production | staging.example.com | Sanitized |
| Production | Live | app.example.com | Production |

## CI/CD Pipeline
| Stage | Tool | Trigger | Failure Action |
|-------|------|---------|---------------|
| Build | [tool] | Push | Block |
| Test | [tool] | Post-build | Block |
| Security Scan | [tool] | Post-build | Block (critical) |
| Deploy Staging | [tool] | Tests pass | Alert |
| Deploy Prod | [tool] | Approval | Auto-rollback |

## Rollout Strategy
| Attribute | Value |
|-----------|-------|
| Method | [Canary / Blue-Green / Rolling] |
| Canary % | [percent] |
| Health Check | [endpoint] |
| Auto-Rollback | [trigger condition] |
| DB Migration | [forward-only / reversible] |"

write_file "$out_root/04_Operations/CONFIGURATION.md" "# Configuration Specification

## Configuration Registry
| Parameter | Type | Default | Env Var | Secret | Restart Required | Description |
|-----------|------|---------|---------|--------|-----------------|-------------|
| db.host | string | localhost | DB_HOST | No | Yes | Database host |

## Hierarchy
1. Environment variables (highest)
2. Config file (env-specific)
3. Defaults (lowest)

## Feature Flags
| Flag | Default | Description | Rollout |
|------|---------|-------------|---------|

## Per-Environment Overrides
| Parameter | Dev | Staging | Prod |
|-----------|-----|---------|------|
| log.level | DEBUG | INFO | WARN |"

write_file "$out_root/04_Operations/MONITORING.md" "# Monitoring Specification

## Metrics
| Category | Metric | Type | Alert Threshold |
|----------|--------|------|----------------|
| System | CPU usage | gauge | >80% 5min |
| System | Memory | gauge | >85% 5min |
| App | Error rate | ratio | >1% 5min |
| App | P99 latency | histogram | >500ms 5min |
| Business | [metric] | [type] | [threshold] |

## Alerting
| Alert | Severity | Channel | Escalation |
|-------|----------|---------|-----------|
| Error rate >5% | P1 | PagerDuty | Immediate |
| Error rate >1% | P2 | Slack | 15min |
| Disk >90% | P3 | Email | Next day |

## Logging
\`\`\`json
{\"timestamp\":\"ISO-8601\",\"level\":\"INFO\",\"service\":\"\",\"trace_id\":\"\",\"message\":\"\",\"duration_ms\":0}
\`\`\`

## PII Rules
- NEVER: passwords, tokens
- MASK: emails, phones
- OK: user IDs, request IDs"

write_file "$out_root/04_Operations/RUNBOOK.md" "# Operations Runbook

## Service Overview
| Attribute | Value |
|-----------|-------|
| Service | [name] |
| Owner | [team] |
| Escalation | [contact] |
| SLA | [target] |

## Incident: [Type]

**Symptoms:** [what you observe]
**Impact:** [users affected, severity]

### Diagnosis
1. Check [metric]: \`[command]\`
2. Review logs: \`[query]\`

### Resolution
1. [Step]: \`[command]\`
2. Verify: \`[command]\`

### Escalation
If not resolved in [X min], contact [team]

## Common Operations
- Scale up: \`[command]\`
- Restart: \`[command]\`
- Rollback: \`[command]\`"

# ── 05_Testing ─────────────────────────────────────────────────

write_file "$out_root/05_Testing/TEST_PLAN.md" "# Test Plan

## Test Levels
| Level | Scope | Coverage Target | Framework |
|-------|-------|----------------|-----------|
| Unit | Functions/methods | 80%+ | [framework] |
| Integration | Service boundaries | API contracts | [framework] |
| E2E | User journeys | Critical paths | [framework] |
| Security | Auth, input validation | OWASP Top 10 | [tools] |
| Performance | Load, stress | NFR targets | [tools] |

## Test Environments
| Environment | Purpose | Data |
|-------------|---------|------|
| Local | Dev | Mock/seed |
| CI | Automated | Fixtures |
| Staging | Integration | Sanitized prod |

## Coverage Requirements
| Area | Target | Gate |
|------|--------|------|
| Business logic | 90% | CI block |
| API handlers | 80% | CI block |
| Security paths | 100% | Manual review |"

write_file "$out_root/05_Testing/ACCEPTANCE_TESTS.md" "# Acceptance Tests

## Feature: [Feature Name]

### Scenario: Happy Path
\`\`\`gherkin
Given [precondition]
When [action]
Then [expected result]
\`\`\`

### Scenario: Error Case
\`\`\`gherkin
Given [precondition]
When [invalid action]
Then [error handling]
\`\`\`

### Scenario: Edge Case
\`\`\`gherkin
Given [boundary condition]
When [action at limit]
Then [expected behavior]
\`\`\`"

# ── 06_Implementation ──────────────────────────────────────────

write_file "$out_root/06_Implementation/TASK_BREAKDOWN.md" "# Task Breakdown

### TASK-001: [Title]
**Implements:** FR-001 | **Estimate:** [hours] | **Phase:** M1

**Description:** [What to do]

**Definition of Done:**
- [ ] Code complete + unit tests
- [ ] Integration tests pass
- [ ] Security review (if applicable)
- [ ] Code reviewed
- [ ] Docs updated"

write_file "$out_root/06_Implementation/MILESTONES.md" "# Milestones

## M1: [Milestone Name]
**Target:** [Date] | **Status:** Not Started

**Deliverables:** [list]
**Tasks:** TASK-001, TASK-002
**Success Criteria:** [criteria]

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|"

write_file "$out_root/06_Implementation/RISKS.md" "# Risk Assessment

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|-----------|-------|
| R-001 | [risk] | [H/M/L] | [H/M/L] | [action] | [name] |"

write_file "$out_root/06_Implementation/MIGRATION.md" "# Migration & Compatibility Plan
[Skip if greenfield with no migration needs]

## Data Migration
| Source (Old) | Target (New) | Transformation |
|-------------|-------------|----------------|

## API Compatibility
| Change | v1 Behavior | v2 Behavior | Migration Path |
|--------|------------|------------|---------------|

## Cutover Plan
| Step | Action | Duration | Owner | Rollback |
|------|--------|----------|-------|----------|"

# ── Agent-specific (optional) ──────────────────────────────────

if [[ $agent -eq 1 ]]; then
  mkdir -p "$out_root/02_Technical_Design/agent"

  write_file "$out_root/02_Technical_Design/AI_COMPONENTS.md" "# AI Components Specification

## Agent Architecture
| Component | Purpose | Technology |
|-----------|---------|------------|
| Orchestrator | Execution loop | [tech] |
| Skills | Capabilities | [tech] |
| Tools | External integrations | [tech] |
| Memory | Context management | [tech] |
| RAG | Knowledge retrieval | [tech] |

## System Prompt → See agent/SYSTEM_PROMPT_SPEC.md
## Golden Conversations → See agent/CONVERSATIONS.md

## Cost Management
| Component | Cost Driver | Estimate | Budget |
|-----------|------------|----------|--------|"

  write_file "$out_root/02_Technical_Design/agent/SYSTEM_PROMPT_SPEC.md" "# System Prompt Design Spec

**Version:** 1.0 | **Owner:** [name]

## Sections
1. Identity Declaration
2. Capability Declaration
3. Behavioral Instructions
4. Constraint Boundaries
5. Output Format Rules
6. Escalation Rules

## Dynamic Variables
| Variable | Source | Example |
|----------|--------|---------|

## Version Control
- Storage: [repo/path]
- Review: [process]
- Rollback: [method]"

  write_file "$out_root/02_Technical_Design/agent/CONVERSATIONS.md" "# Golden Conversations

## Coverage
| Category | Required | Done |
|----------|----------|------|
| Happy path | 2-3/use case | |
| Edge cases | 1-2/use case | |
| Safety | 3-5 total | |
| Multi-turn | 2-3 | |
| Error recovery | 2-3 | |
| Context switch | 1-2 | |

## Conversation: [ID] - [Title]
**Category:** [type] | **Use Case:** [which]

\`\`\`
User: [message]
Agent: [response]
  [Annotation: Why correct]
  [Unacceptable: What NOT to say]
\`\`\`"

  echo "  (Agent files created in 02_Technical_Design/agent/)"
fi

# ── SPEC_INDEX.md ──────────────────────────────────────────────

idx="# Engineering Specification Index

## 00 Overview
- [SUMMARY.md](00_Overview/SUMMARY.md) — Executive summary
- [REQUIREMENTS_MATRIX.md](00_Overview/REQUIREMENTS_MATRIX.md) — Traceability
- [DECISION_LOG.md](00_Overview/DECISION_LOG.md) — Architecture decisions
- [TECH_STACK.md](00_Overview/TECH_STACK.md) — Technology stack

## 01 Requirements
- [USER_STORIES.md](01_Requirements/USER_STORIES.md)
- [FUNCTIONAL_REQS.md](01_Requirements/FUNCTIONAL_REQS.md)
- [NON_FUNCTIONAL_REQS.md](01_Requirements/NON_FUNCTIONAL_REQS.md)

## 02 Technical Design
- [ARCHITECTURE.md](02_Technical_Design/ARCHITECTURE.md)
- [DATA_MODEL.md](02_Technical_Design/DATA_MODEL.md)
- [API_SPEC.md](02_Technical_Design/API_SPEC.md)
- [BUSINESS_LOGIC.md](02_Technical_Design/BUSINESS_LOGIC.md)

## 03 Security
- [AUTH_DESIGN.md](03_Security/AUTH_DESIGN.md)
- [DATA_SECURITY.md](03_Security/DATA_SECURITY.md)
- [AUDIT_SPEC.md](03_Security/AUDIT_SPEC.md)

## 04 Operations
- [DEPLOYMENT.md](04_Operations/DEPLOYMENT.md)
- [CONFIGURATION.md](04_Operations/CONFIGURATION.md)
- [MONITORING.md](04_Operations/MONITORING.md)
- [RUNBOOK.md](04_Operations/RUNBOOK.md)

## 05 Testing
- [TEST_PLAN.md](05_Testing/TEST_PLAN.md)
- [ACCEPTANCE_TESTS.md](05_Testing/ACCEPTANCE_TESTS.md)

## 06 Implementation
- [TASK_BREAKDOWN.md](06_Implementation/TASK_BREAKDOWN.md)
- [MILESTONES.md](06_Implementation/MILESTONES.md)
- [RISKS.md](06_Implementation/RISKS.md)
- [MIGRATION.md](06_Implementation/MIGRATION.md)"

if [[ $agent -eq 1 ]]; then
  idx="$idx

## Agent System
- [AI_COMPONENTS.md](02_Technical_Design/AI_COMPONENTS.md)
- [SYSTEM_PROMPT_SPEC.md](02_Technical_Design/agent/SYSTEM_PROMPT_SPEC.md)
- [CONVERSATIONS.md](02_Technical_Design/agent/CONVERSATIONS.md)"
fi

write_file "$out_root/SPEC_INDEX.md" "$idx"

echo ""
echo "✅ Engineering spec skeleton created at: $out_root"
echo ""
echo "Structure:"
find "$out_root" -type f -name "*.md" | sort | sed "s|^$out_root/|  |"
