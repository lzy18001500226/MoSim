#!/usr/bin/env bash
set -euo pipefail

# generate_skeleton.sh - Create the spec output directory structure
# Usage: generate_skeleton.sh [output_root] [--force]

usage() {
  cat <<'EOF'
Usage:
  generate_skeleton.sh [output_root] [--force]

Creates the standard spec output directory structure with placeholder files.
Default output_root is ./spec

Options:
  --force    Overwrite existing files (default: skip existing)
EOF
}

out_root="spec"
force=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -f|--force)
      force=1
      shift
      ;;
    *)
      if [[ "$1" == -* ]]; then
        echo "Unknown option: $1" >&2
        usage
        exit 2
      fi
      out_root="$1"
      shift
      ;;
  esac
done

mkdir -p "$out_root"

dirs=(
  "00_Overview"
  "00_Overview/diagrams"
  "01_Configuration"
  "01_Configuration/schemas"
  "02_Data"
  "02_Data/schemas"
  "03_API"
  "03_API/openapi"
  "04_Business_Logic"
  "05_Integrations"
  "06_UI"
  "07_Infrastructure"
  "08_Testing"
  "08_Testing/test-cases"
  "09_Verification"
)

for d in "${dirs[@]}"; do
  mkdir -p "$out_root/$d"
done

write_file() {
  local path="$1"
  local content="$2"
  if [[ -f "$path" && $force -eq 0 ]]; then
    echo "skip: $path"
    return
  fi
  printf "%s\n" "$content" > "$path"
  echo "write: $path"
}

# 00_Overview
write_file "$out_root/00_Overview/PROJECT.md" \
"# Project Overview

## Identity
- Name: [Project name]
- Version: [Current version]
- Repository: [Repository URL]

## Description
[Brief description of what this project does]

## Tech Stack
- Language: [Primary language(s)]
- Framework: [Framework(s)]
- Database: [Database(s)]
- External Services: [List of external dependencies]

## Build & Run
\`\`\`bash
# Install dependencies
[command]

# Build
[command]

# Run
[command]

# Test
[command]
\`\`\`

## Environment Requirements
- [Runtime version]
- [System dependencies]
- [Required environment variables - see 01_Configuration/ENVIRONMENT.md]
"

write_file "$out_root/00_Overview/ARCHITECTURE.md" \
"# System Architecture

## High-Level Overview

\`\`\`
[ASCII diagram or reference to Mermaid diagram]
\`\`\`

## Layers

### Presentation Layer
[Description of how requests enter the system]

### Application Layer
[Description of business logic organization]

### Domain Layer
[Description of core domain models and rules]

### Infrastructure Layer
[Description of external integrations, persistence, etc.]

## Module Dependencies

| Module | Depends On | Depended By |
|--------|------------|-------------|
| [module] | [dependencies] | [dependents] |

## Communication Patterns
- [Sync/Async patterns]
- [Event-driven patterns]
- [API patterns]

## Diagrams
See \`diagrams/\` folder for:
- System context diagram
- Container diagram
- Component diagrams
"

write_file "$out_root/00_Overview/GLOSSARY.md" \
"# Glossary

## Domain Terms

| Term | Definition | Usage |
|------|------------|-------|
| [Term] | [What it means in this domain] | [Where/how it's used] |

## Technical Terms

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

## Abbreviations

| Abbrev | Full Form |
|--------|-----------|
| [Abbrev] | [Full form] |
"

# 01_Configuration
write_file "$out_root/01_Configuration/ENVIRONMENT.md" \
"# Environment Variables

## Required Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| [VAR_NAME] | string | [What it does] | [Example value] |

## Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| [VAR_NAME] | string | [default] | [What it does] |

## Secrets (Do Not Commit)

| Variable | Description | How to Obtain |
|----------|-------------|---------------|
| [SECRET_NAME] | [What it's for] | [Where to get it] |

## Environment-Specific Settings

### Development
\`\`\`
[Dev-specific variables]
\`\`\`

### Production
\`\`\`
[Prod-specific variables]
\`\`\`
"

write_file "$out_root/01_Configuration/FEATURE_FLAGS.md" \
"# Feature Flags

## Active Flags

| Flag | Type | Default | Description | Affects |
|------|------|---------|-------------|---------|
| [FLAG_NAME] | boolean | false | [What it controls] | [Components affected] |

## Deprecated Flags
[Flags scheduled for removal]

## Flag Evaluation Logic
[How flags are evaluated - env vars, config service, etc.]
"

# 02_Data
write_file "$out_root/02_Data/ENTITIES.md" \
"# Data Entities

## Entity: [EntityName]

### Purpose
[What this entity represents]

### Fields

| Field | Type | Nullable | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| id | UUID | No | auto | PK | Primary identifier |
| [field] | [type] | [Y/N] | [default] | [constraints] | [description] |

### Indexes
- [index name]: [columns] - [purpose]

### Lifecycle
- Created: [when/how]
- Updated: [when/how]
- Deleted: [soft/hard, when/how]

### Validation Rules
- [rule 1]
- [rule 2]

---

## Entity: [NextEntity]
[Repeat pattern]
"

write_file "$out_root/02_Data/RELATIONSHIPS.md" \
"# Entity Relationships

## ER Diagram
\`\`\`mermaid
erDiagram
    [Entity relationships in Mermaid syntax]
\`\`\`

## Relationship Details

### [EntityA] → [EntityB]
- Type: [1:1, 1:N, N:N]
- Foreign Key: [field]
- Cascade: [ON DELETE/UPDATE behavior]
- Nullable: [Yes/No]
- Business Rule: [Why this relationship exists]
"

write_file "$out_root/02_Data/MIGRATIONS.md" \
"# Schema Migrations

## Migration History

| Version | Date | Description | Reversible |
|---------|------|-------------|------------|
| [version] | [date] | [what changed] | [Y/N] |

## Current Schema Version
[version]

## Pending Migrations
[List of migrations not yet applied to production]

## Migration Strategy
[How migrations are applied - manual, automatic, CI/CD]

## Rollback Procedures
[How to rollback if needed]
"

# 03_API
write_file "$out_root/03_API/ENDPOINTS.md" \
"# API Endpoints

## Authentication
All endpoints require: [authentication method]
Exceptions: [public endpoints]

## Endpoint Catalog

### [Resource Name]

#### GET /api/[resource]
**Purpose**: [What it does]

**Authentication**: [Required/Optional/None]

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| [param] | [type] | [Y/N] | [default] | [description] |

**Response 200**:
\`\`\`json
{
  \"data\": [...],
  \"pagination\": {...}
}
\`\`\`

**Errors**:
| Code | Condition |
|------|-----------|
| 401 | [when] |
| 403 | [when] |

---

#### POST /api/[resource]
[Repeat pattern for each endpoint]
"

write_file "$out_root/03_API/AUTHENTICATION.md" \
"# Authentication

## Auth Methods Supported
- [JWT / Session / API Key / OAuth]

## Auth Flow

### Login Flow
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Token Refresh Flow
[How tokens are refreshed]

### Logout Flow
[How sessions are terminated]

## Token Structure
\`\`\`json
{
  \"sub\": \"user_id\",
  \"exp\": \"expiration\",
  \"...\"
}
\`\`\`

## Permission Model
[RBAC / ABAC / Custom]

### Roles
| Role | Permissions |
|------|-------------|
| [role] | [what they can do] |

### Protected Resources
| Resource | Required Permission |
|----------|---------------------|
| [resource] | [permission] |
"

write_file "$out_root/03_API/ERRORS.md" \
"# Error Handling

## Error Response Format
\`\`\`json
{
  \"error\": {
    \"code\": \"ERROR_CODE\",
    \"message\": \"Human readable message\",
    \"details\": {}
  }
}
\`\`\`

## Error Codes

### Client Errors (4xx)

| Code | HTTP | Condition | Resolution |
|------|------|-----------|------------|
| VALIDATION_ERROR | 400 | [when] | [how to fix] |
| UNAUTHORIZED | 401 | [when] | [how to fix] |
| FORBIDDEN | 403 | [when] | [how to fix] |
| NOT_FOUND | 404 | [when] | [how to fix] |

### Server Errors (5xx)

| Code | HTTP | Condition | Recovery |
|------|------|-----------|----------|
| INTERNAL_ERROR | 500 | [when] | [retry strategy] |
| SERVICE_UNAVAILABLE | 503 | [when] | [retry strategy] |

## Error Handling Strategy
- [Logging]
- [Monitoring]
- [User notification]
"

# 04_Business_Logic
write_file "$out_root/04_Business_Logic/RULES.md" \
"# Business Rules

## Rule: [Rule Name]

### Description
[What this rule enforces]

### Trigger
[When this rule is evaluated]

### Logic
\`\`\`
IF [condition]
THEN [action]
ELSE [alternative]
\`\`\`

### Pseudocode
\`\`\`python
def apply_rule(input):
    if condition:
        return result_a
    else:
        return result_b
\`\`\`

### Edge Cases
| Case | Input | Expected | Rationale |
|------|-------|----------|-----------|
| [case] | [input] | [output] | [why] |

### Exceptions
[When this rule does NOT apply]

---

## Rule: [Next Rule]
[Repeat pattern]
"

write_file "$out_root/04_Business_Logic/STATE_MACHINES.md" \
"# State Machines

## [Entity] State Machine

### States
| State | Description | Entry Conditions | Exit Conditions |
|-------|-------------|------------------|-----------------|
| [STATE] | [meaning] | [how to enter] | [how to exit] |

### Transitions

\`\`\`mermaid
stateDiagram-v2
    [Mermaid state diagram]
\`\`\`

### Transition Details

| From | To | Trigger | Guard Conditions | Side Effects |
|------|-----|---------|------------------|--------------|
| [from] | [to] | [event] | [conditions] | [what happens] |

### Invalid Transitions
[Transitions that are explicitly forbidden and why]
"

write_file "$out_root/04_Business_Logic/WORKFLOWS.md" \
"# Workflows

## Workflow: [Workflow Name]

### Purpose
[What this workflow accomplishes]

### Trigger
[What initiates this workflow]

### Steps

1. **[Step Name]**
   - Input: [what it receives]
   - Action: [what it does]
   - Output: [what it produces]
   - On Error: [error handling]

2. **[Next Step]**
   [Repeat]

### Flow Diagram
\`\`\`mermaid
flowchart TD
    [Mermaid flowchart]
\`\`\`

### Compensation (Rollback)
[How to undo if workflow fails midway]

### Timeouts
[Any time-based constraints]
"

# 08_Testing
write_file "$out_root/08_Testing/UNIT_SPECS.md" \
"# Unit Test Specifications

## Module: [Module Name]

### Function: [functionName]

**Purpose**: [What it does]

**Test Cases**:

| ID | Scenario | Input | Expected | Notes |
|----|----------|-------|----------|-------|
| U001 | Happy path | [input] | [output] | |
| U002 | Empty input | null/[] | [error/default] | |
| U003 | Max value | [max] | [output] | Boundary test |
| U004 | Invalid type | [wrong type] | TypeError | |

**Setup Requirements**:
- [Mocks needed]
- [Test data]

---

## Module: [Next Module]
[Repeat pattern]
"

write_file "$out_root/08_Testing/INTEGRATION_SPECS.md" \
"# Integration Test Specifications

## Integration: [ServiceA] ↔ [ServiceB]

### Purpose
[What this integration tests]

### Test Cases

| ID | Scenario | Setup | Action | Verification |
|----|----------|-------|--------|--------------|
| I001 | [scenario] | [setup] | [action] | [checks] |

### Test Data Requirements
- [Data that must exist]
- [State that must be set up]

### Cleanup
[How to reset after tests]

---

## Integration: [Next Integration]
[Repeat pattern]
"

write_file "$out_root/08_Testing/E2E_SPECS.md" \
"# End-to-End Test Specifications

## Journey: [Journey Name]

### Description
[What user journey this tests]

### Preconditions
- [System state]
- [User state]
- [Data state]

### Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | [user action] | [system response] |
| 2 | [user action] | [system response] |

### Variations
- [Variation 1]: [how it differs]
- [Variation 2]: [how it differs]

### Known Issues
[Any known flaky behavior or limitations]

---

## Journey: [Next Journey]
[Repeat pattern]
"

# 09_Verification
write_file "$out_root/09_Verification/COVERAGE_REPORT.md" \
"# Spec Coverage Report

Generated: [date]

## Summary
- Total code elements: [count]
- Documented elements: [count]
- Coverage: [percentage]

## Documented and Verified
[List of elements with complete specs]

## Documented but Unverified
[List of elements needing verification]

## Found in Code but Not Documented
[List of elements missing from spec]

## Ambiguous or Unclear
[List of elements needing clarification]
"

write_file "$out_root/09_Verification/REPLICATION_GUIDE.md" \
"# Replication Guide

## Purpose
This guide explains how to use these specifications to replicate the project.

## Prerequisites
- [Required knowledge]
- [Required tools]
- [Required access]

## Recommended Order

1. **Environment Setup**
   - Follow 01_Configuration/ENVIRONMENT.md
   - Set up database per 02_Data/ENTITIES.md

2. **Data Layer**
   - Implement entities from 02_Data/ENTITIES.md
   - Implement relationships from 02_Data/RELATIONSHIPS.md

3. **Business Logic**
   - Implement rules from 04_Business_Logic/RULES.md
   - Implement workflows from 04_Business_Logic/WORKFLOWS.md

4. **API Layer**
   - Implement endpoints from 03_API/ENDPOINTS.md
   - Implement auth from 03_API/AUTHENTICATION.md

5. **Verification**
   - Run test cases from 08_Testing/
   - Compare against acceptance criteria

## Verification Checklist
- [ ] All endpoints respond correctly
- [ ] All business rules enforced
- [ ] All state transitions work
- [ ] All error codes returned correctly
- [ ] Performance within specified bounds
"

write_file "$out_root/09_Verification/KNOWN_GAPS.md" \
"# Known Documentation Gaps

## Intentionally Omitted
[Things deliberately not documented and why]

## To Be Documented
[Things that need documentation but haven't been done yet]

| Area | Gap | Priority | Notes |
|------|-----|----------|-------|
| [area] | [what's missing] | [H/M/L] | [notes] |

## Unclear Areas
[Areas where the original code is ambiguous]

## Technical Debt
[Known issues or workarounds in the original code]
"

# Index file
write_file "$out_root/SPEC_INDEX.md" \
"# Specification Index

## Overview
- [00_Overview/PROJECT.md](00_Overview/PROJECT.md) - Project identity and tech stack
- [00_Overview/ARCHITECTURE.md](00_Overview/ARCHITECTURE.md) - System architecture
- [00_Overview/GLOSSARY.md](00_Overview/GLOSSARY.md) - Domain terminology

## Configuration
- [01_Configuration/ENVIRONMENT.md](01_Configuration/ENVIRONMENT.md) - Environment variables
- [01_Configuration/FEATURE_FLAGS.md](01_Configuration/FEATURE_FLAGS.md) - Feature toggles

## Data Model
- [02_Data/ENTITIES.md](02_Data/ENTITIES.md) - Data entities
- [02_Data/RELATIONSHIPS.md](02_Data/RELATIONSHIPS.md) - Entity relationships
- [02_Data/MIGRATIONS.md](02_Data/MIGRATIONS.md) - Schema history

## API
- [03_API/ENDPOINTS.md](03_API/ENDPOINTS.md) - API endpoints
- [03_API/AUTHENTICATION.md](03_API/AUTHENTICATION.md) - Auth mechanisms
- [03_API/ERRORS.md](03_API/ERRORS.md) - Error handling

## Business Logic
- [04_Business_Logic/RULES.md](04_Business_Logic/RULES.md) - Business rules
- [04_Business_Logic/STATE_MACHINES.md](04_Business_Logic/STATE_MACHINES.md) - State transitions
- [04_Business_Logic/WORKFLOWS.md](04_Business_Logic/WORKFLOWS.md) - Multi-step processes

## Testing
- [08_Testing/UNIT_SPECS.md](08_Testing/UNIT_SPECS.md) - Unit test specs
- [08_Testing/INTEGRATION_SPECS.md](08_Testing/INTEGRATION_SPECS.md) - Integration test specs
- [08_Testing/E2E_SPECS.md](08_Testing/E2E_SPECS.md) - E2E test specs

## Verification
- [09_Verification/COVERAGE_REPORT.md](09_Verification/COVERAGE_REPORT.md) - Spec coverage
- [09_Verification/REPLICATION_GUIDE.md](09_Verification/REPLICATION_GUIDE.md) - How to replicate
- [09_Verification/KNOWN_GAPS.md](09_Verification/KNOWN_GAPS.md) - Documentation gaps
"

echo ""
echo "✅ Spec skeleton created at: $out_root"
echo ""
echo "Structure:"
find "$out_root" -type f -name "*.md" | sort | sed "s|^$out_root/|  |"
