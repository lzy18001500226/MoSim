#!/usr/bin/env bash
set -euo pipefail

# generate_prd_skeleton.sh - Generate PRD document structure
# Usage: generate_prd_skeleton.sh [--force] <output_dir> <project_name>

die() {
  echo "Error: $*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  generate_prd_skeleton.sh [--force] <output_dir> <project_name>

Generates a complete PRD document structure with templates.

By default, refuses to overwrite existing files. Use --force to overwrite.

Example:
  generate_prd_skeleton.sh ./docs/prd "User Dashboard Redesign"
  generate_prd_skeleton.sh --force ./docs/prd "User Dashboard Redesign"
EOF
}

force=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--force)
      force=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      usage
      die "Unknown option: $1"
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

output_dir="$1"
project_name="$2"
date_now=$(date +"%Y-%m-%d")

mkdir -p "$output_dir"

echo "Creating PRD structure for: $project_name"
echo "Output directory: $output_dir"

target_files=(
  "PRD.md"
  "PERSONAS.md"
  "USER_STORIES.md"
  "BUSINESS_RULES.md"
  "USER_FLOWS.md"
  "ERROR_HANDLING.md"
  "CHECKLIST.md"
)

if [[ $force -eq 0 ]]; then
  existing=()
  for filename in "${target_files[@]}"; do
    if [[ -e "$output_dir/$filename" ]]; then
      existing+=("$output_dir/$filename")
    fi
  done

  if [[ ${#existing[@]} -gt 0 ]]; then
    echo "Refusing to overwrite existing files:" >&2
    for path in "${existing[@]}"; do
      echo "  - $path" >&2
    done
    echo "" >&2
    echo "Choose a new output directory, or re-run with --force to overwrite." >&2
    exit 2
  fi
fi

# Main PRD document
cat > "$output_dir/PRD.md" << ENDPRD
# PRD: $project_name

| Field | Value |
|-------|-------|
| **Author** | [Your Name] |
| **Status** | Draft |
| **Version** | 0.1 |
| **Created** | $date_now |
| **Last Updated** | $date_now |

---

## 1. Executive Summary

### 1.1 Problem Statement

[Describe the problem in one paragraph. Be specific about WHO has the problem, WHAT the problem is, and WHY it matters.]

### 1.2 Solution Overview

[Describe the proposed solution in one paragraph.]

### 1.3 Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| [Primary metric] | [baseline] | [target] | [timeframe] |
| [Secondary metric] | [baseline] | [target] | [timeframe] |

---

## 2. Background & Context

### 2.1 Business Context

[Why is this important now? What's the strategic driver?]

### 2.2 User Research Summary

[Summary of user research. Link to full research docs if available.]

### 2.3 Current State

[How does it work today? What are the pain points?]

---

## 3. Goals & Non-Goals

### 3.1 Goals

1. **[Goal 1]:** [Measurable objective]
2. **[Goal 2]:** [Measurable objective]
3. **[Goal 3]:** [Measurable objective]

### 3.2 Non-Goals (Explicitly Out of Scope)

1. **[Non-goal 1]:** [Why out of scope]
2. **[Non-goal 2]:** [Why out of scope]

### 3.3 Success Criteria

**Launch criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Success criteria (post-launch):**
- [ ] [Metric] reaches [target] within [timeframe]

---

## 4. Users & Personas

See: [PERSONAS.md](./PERSONAS.md)

---

## 5. User Stories & Requirements

See: [USER_STORIES.md](./USER_STORIES.md)

### 5.1 Functional Requirements Summary

| ID | Requirement | Priority | User Story |
|----|-------------|----------|------------|
| FR-001 | [Description] | P0 | US-001 |

### 5.2 Business Rules Summary

See: [BUSINESS_RULES.md](./BUSINESS_RULES.md)

---

## 6. User Experience

### 6.1 User Flows

See: [USER_FLOWS.md](./USER_FLOWS.md)

### 6.2 Wireframes

[Link to designs or embed key screens]

### 6.3 States

| State | Description | Display |
|-------|-------------|---------|
| Empty | No data yet | [Description] |
| Loading | Fetching data | [Description] |
| Loaded | Data displayed | [Description] |
| Error | Something failed | [Description] |

---

## 7. Data Requirements

### 7.1 Data Entities

| Entity | Description | Key Attributes |
|--------|-------------|----------------|
| [Entity] | [Purpose] | [Attributes] |

### 7.2 Data Lifecycle

| Event | Trigger | Action |
|-------|---------|--------|
| Create | [Trigger] | [Action] |
| Update | [Trigger] | [Action] |
| Delete | [Trigger] | [Action] |

---

## 8. Non-Functional Requirements

### 8.1 Performance

| Metric | Requirement |
|--------|-------------|
| Page load | < [X]s |
| API response | < [X]ms at P95 |

### 8.2 Security

| Requirement | Specification |
|-------------|---------------|
| Authentication | [Method] |
| Authorization | [Model] |

### 8.3 Accessibility

- WCAG [Level] compliance required

---

## 9. Dependencies & Integrations

### 9.1 Dependencies

| Dependency | Owner | Risk |
|------------|-------|------|
| [Dependency] | [Team] | [H/M/L] |

### 9.2 Integrations

| System | Purpose | Method |
|--------|---------|--------|
| [System] | [Purpose] | [API/etc] |

---

## 10. Timeline & Milestones

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| [Milestone] | [Date] | [Criteria] |

---

## 11. Risks & Open Questions

### 11.1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

### 11.2 Open Questions

| Question | Owner | Due | Status |
|----------|-------|-----|--------|
| [Question] | [Name] | [Date] | Open |

### 11.3 Assumptions

| Assumption | Impact if Wrong |
|------------|-----------------|
| [Assumption] | [Impact] |

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### B. References

| Document | Link |
|----------|------|
| [Doc] | [Link] |

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | $date_now | [Name] | Initial draft |
ENDPRD

# Personas document
cat > "$output_dir/PERSONAS.md" << 'ENDPERSONAS'
# User Personas

## Persona 1: [Name]

| Attribute | Description |
|-----------|-------------|
| **Role** | [Job title/function] |
| **Description** | [Brief profile] |
| **Goals** | [What they want to achieve] |
| **Pain Points** | [What frustrates them] |
| **Technical Level** | [Novice / Intermediate / Expert] |
| **Usage Frequency** | [Daily / Weekly / Monthly] |
| **Key Behaviors** | [Relevant behaviors] |

### Scenario

[A typical scenario where this persona uses the product]

---

## Persona 2: [Name]

[Repeat structure]

---

## Persona 3: [Name]

[Repeat structure]
ENDPERSONAS

# User stories document
cat > "$output_dir/USER_STORIES.md" << 'ENDSTORIES'
# User Stories

## US-001: [Title]

**Priority:** P0

**Story:**
As a [role],
I want [action],
so that [benefit].

**Acceptance Criteria:**
- **AC-1:** Given [context], when [action], then [result]
- **AC-2:** Given [context], when [action], then [result]
- **AC-3:** Given [context], when [action], then [result]

**Business Rules:** [BR-xxx]

**Notes:**
[Additional context]

---

## US-002: [Title]

**Priority:** P0

**Story:**
As a [role],
I want [action],
so that [benefit].

**Acceptance Criteria:**
- **AC-1:** Given [context], when [action], then [result]

**Business Rules:** [BR-xxx]

---

## US-003: [Title]

[Repeat structure]
ENDSTORIES

# Business rules document
cat > "$output_dir/BUSINESS_RULES.md" << 'ENDRULES'
# Business Rules

## BR-001: [Rule Name]

**Description:** [Plain language description]

**Trigger:** [When this rule applies]

**Logic:**
```
IF [condition]
THEN [result]
ELSE [alternative]
```

**Examples:**
| Input | Output | Explanation |
|-------|--------|-------------|
| [Example] | [Result] | [Why] |

**Edge Cases:**
- [Edge case 1]: [handling]
- [Edge case 2]: [handling]

**Related:** US-001, FR-001

---

## BR-002: [Rule Name]

[Repeat structure]

---

## BR-003: [Rule Name]

[Repeat structure]
ENDRULES

# User flows document
cat > "$output_dir/USER_FLOWS.md" << 'ENDFLOWS'
# User Flows

## Flow 1: [Flow Name]

**Trigger:** [How the user starts this flow]

**Actors:** [Who is involved]

**Preconditions:**
- [Condition 1]
- [Condition 2]

### Steps

| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | User | [Action] | [Response] |
| 2 | User | [Action] | [Response] |
| 3 | System | [Action] | [Response] |
| 4 | User | [Action] | [Response] |

### Success End State

[What indicates successful completion]

### Alternative Paths

| At Step | Condition | Alternative Flow |
|---------|-----------|------------------|
| 2 | [Condition] | [What happens] |

### Error Paths

| At Step | Error | User Sees | System Action |
|---------|-------|-----------|---------------|
| 3 | [Error] | [Message] | [Action] |

---

## Flow 2: [Flow Name]

[Repeat structure]
ENDFLOWS

# Error handling document
cat > "$output_dir/ERROR_HANDLING.md" << 'ENDERRORS'
# Error Handling Specification

## Error Categories

### User Errors (Validation)

| Error | Condition | User Message | Recovery |
|-------|-----------|--------------|----------|
| [Error] | [When it occurs] | [Message shown] | [What user can do] |

### System Errors

| Error | Condition | User Message | System Action |
|-------|-----------|--------------|---------------|
| [Error] | [When it occurs] | [Message shown] | [Logging/alerting] |

### External Errors

| Error | Condition | User Message | Fallback |
|-------|-----------|--------------|----------|
| [Error] | [When it occurs] | [Message shown] | [Alternative behavior] |

## Error Message Standards

- Tone: [Friendly/Professional/etc.]
- Format: [Title + description + action]
- Length: [Max characters]

## Error Message Catalog

| ID | Type | Title | Message | Actions |
|----|------|-------|---------|---------|
| ERR-001 | Validation | [Title] | [Message] | [Buttons] |
| ERR-002 | System | [Title] | [Message] | [Buttons] |
ENDERRORS

# Checklist document
cat > "$output_dir/CHECKLIST.md" << 'ENDCHECK'
# PRD Completion Checklist

Use this checklist before declaring PRD "ready for engineering review."

## Content Completeness

### Problem & Context
- [ ] Problem statement is specific (not solution disguised as problem)
- [ ] Success metrics defined with targets
- [ ] Current state documented

### Scope
- [ ] In-scope features listed with priority
- [ ] Out-of-scope explicitly stated
- [ ] MVP defined

### Users
- [ ] All user types identified
- [ ] Personas documented
- [ ] Permissions per user type defined

### Requirements
- [ ] All user stories have acceptance criteria
- [ ] All acceptance criteria are testable
- [ ] All business rules documented with examples
- [ ] All edge cases documented
- [ ] All error handling specified

### Experience
- [ ] User flows documented
- [ ] Wireframes/mockups provided or referenced
- [ ] All states defined (empty, loading, error, success)
- [ ] Error messages specified

### Technical
- [ ] Performance requirements quantified
- [ ] Security requirements specified
- [ ] Dependencies identified
- [ ] Integrations documented

### Plan
- [ ] Timeline with milestones
- [ ] Risks identified with mitigation
- [ ] Open questions tracked

## Quality Checks

### Clarity
- [ ] No vague terms (fast, easy, etc.) without definition
- [ ] No undefined boundaries (many, large, etc.)
- [ ] Terminology consistent
- [ ] Glossary covers domain terms

### Testability
- [ ] QA can write test cases from acceptance criteria
- [ ] Success criteria are measurable

### Review
- [ ] Stakeholders have reviewed
- [ ] Engineering has reviewed
- [ ] All review questions incorporated into PRD
ENDCHECK

echo ""
echo "PRD structure created successfully!"
echo ""
echo "Files created:"
echo "  $output_dir/PRD.md              - Main PRD document"
echo "  $output_dir/PERSONAS.md         - User personas"
echo "  $output_dir/USER_STORIES.md     - User stories"
echo "  $output_dir/BUSINESS_RULES.md   - Business rules"
echo "  $output_dir/USER_FLOWS.md       - User flows"
echo "  $output_dir/ERROR_HANDLING.md   - Error handling specs"
echo "  $output_dir/CHECKLIST.md        - Completion checklist"
echo ""
echo "Next steps:"
echo "  1. Start with PRD.md - fill in executive summary"
echo "  2. Define personas in PERSONAS.md"
echo "  3. Write user stories in USER_STORIES.md"
echo "  4. Document business rules in BUSINESS_RULES.md"
echo "  5. Map user flows in USER_FLOWS.md"
echo "  6. Specify error handling in ERROR_HANDLING.md"
echo "  7. Use CHECKLIST.md before handoff"
