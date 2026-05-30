---
name: codebase-spec-extractor
description: "Extract complete, replicable engineering specifications from existing codebases. Produces documentation detailed enough to fully replicate a project without seeing the original source code—even using a different tech stack. Use when: analyzing existing projects, documenting legacy systems, creating technical specs from code, preparing for system migration, or onboarding new teams. Triggers: 'extract spec from code', 'document codebase', 'analyze project architecture', 'create spec from existing system'."
license: MIT
compatibility: "Requires bash, standard Unix tools. Optional: ripgrep (rg) for faster scanning."
metadata:
  author: user
  version: "0.1.0"
  category: engineering
  tags: "specification, documentation, codebase-analysis, architecture"
---

# Codebase Spec Extractor

## Overview

Extract engineering specifications from existing codebases with one goal: **produce documentation so complete that the project can be fully replicated without seeing the original source code**.

This is NOT about filling templates. This is about **deconstructing every detail** and documenting it with engineering precision.

## Requirements

- `bash` (macOS default Bash 3.2 supported)
- Standard Unix tools: `find`, `grep`, `sed`, `wc`, `date`
- Optional (recommended): `rg` (ripgrep) for faster scans in large repos

## When to Use

- You need **implementation-grade** specs for a codebase (migration, rewrite, onboarding, vendor handoff).
- You keep finding “implicit rules” in code and want them made explicit.
- You want a repeatable inventory + spec skeleton + verification workflow.

## When NOT to Use

- You only need a quick architecture overview or a lightweight README update.
- Your main goal is security auditing, performance profiling, or code style cleanup (use dedicated workflows/tools).
- The repository contains highly sensitive data and you cannot safely store path-rich reports/specs.

## Core Principle: Deconstruction Thinking

**The framework is a guide, not a boundary.** Real projects are messy, creative, and often surprising. Your job is to:

1. **Discover** what exists (not assume what should exist)
2. **Understand** why it exists (not just what it does)
3. **Document** how to replicate it (not just describe it)

### The Deconstruction Questions

For EVERY piece of code, structure, or behavior you encounter, ask:

```
┌─────────────────────────────────────────────────────────────────┐
│                 The 7 Deconstruction Questions                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. WHAT is this?                                               │
│     → Name it. Classify it. Place it in context.                │
│                                                                 │
│  2. WHY does it exist?                                          │
│     → What problem does it solve? What would break without it?  │
│                                                                 │
│  3. HOW does it work?                                           │
│     → Step-by-step logic. Every branch. Every edge case.        │
│                                                                 │
│  4. WHAT are its inputs?                                        │
│     → All forms. All sources. All validations.                  │
│                                                                 │
│  5. WHAT are its outputs?                                       │
│     → All forms. All destinations. All side effects.            │
│                                                                 │
│  6. WHAT depends on it? What does it depend on?                 │
│     → Upstream. Downstream. External.                           │
│                                                                 │
│  7. WHAT can go wrong?                                          │
│     → Errors. Failures. Edge cases. Recovery.                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

If you can answer all 7 questions for every element, the spec is complete.

### Framework Flexibility

The output structure provided below is a **starting point**. When you encounter something that doesn't fit:

1. **Don't force it** into an existing category
2. **Create a new category** that accurately describes it
3. **Apply the same 7 questions** to document it
4. **Add it to the spec** with clear explanation

Examples of things that might not fit standard frameworks:
- Custom DSLs or configuration languages
- Unusual architectural patterns
- Legacy code with implicit rules
- Domain-specific algorithms
- Complex state machines
- Multi-system orchestration
- Real-time/streaming logic
- Hardware integrations

**Document what IS, not what SHOULD BE.**

## Replicability Test

Every piece of documentation must answer: **"Can someone implement this correctly using only this description?"**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Replicability Test                           │
├─────────────────────────────────────────────────────────────────┤
│  For each documented element, verify:                           │
│                                                                 │
│  □ Inputs: All possible input forms documented?                 │
│  □ Outputs: All possible output forms documented?               │
│  □ Logic: Complete decision tree with all branches?             │
│  □ Constraints: All validation rules and limits?                │
│  □ Edge cases: All boundary conditions handled?                 │
│  □ Dependencies: All upstream/downstream interactions?          │
│  □ Errors: All failure modes and handling strategies?           │
│                                                                 │
│  If any answer is "no", the documentation is incomplete.        │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow

### Phase 0: Project Discovery

Before applying any framework, understand what the project actually is.

**0.1 Initial Scan**
```bash
# Run the discovery script to get project overview
bash scripts/discover_project.sh <project_root>
```

The script identifies:
- Project type (backend API, frontend SPA, fullstack, library, CLI, etc.)
- Tech stack (languages, frameworks, databases, external services)
- Entry points and build system
- Directory structure patterns

**0.2 Scope Confirmation**

Clarify with user:
- Full project or specific modules?
- Include deployment/infrastructure specs?
- Target audience for the spec (same team? different team? different tech stack?)
- Any known areas of complexity or legacy code?

### Phase 1: Structural Decomposition

Decompose the project into documentable units. **Do not assume a fixed structure**—let the project's actual organization guide you.

**1.1 Identify All Documentable Elements**

Scan for and categorize everything that needs documentation:

| Category | What to Find | How to Find |
|----------|--------------|-------------|
| **Configuration** | Environment vars, config files, feature flags | `*.env*`, `config.*`, `settings.*` |
| **Data Layer** | Models, schemas, migrations, seeds | ORM definitions, SQL files, schema files |
| **API Layer** | Routes, controllers, middleware, auth | Route definitions, handler files |
| **Business Logic** | Services, use cases, domain rules | Service classes, domain modules |
| **Integration** | External APIs, queues, caches, storage | Client classes, adapter modules |
| **UI Layer** | Components, pages, state management | Component files, route configs |
| **Infrastructure** | Dockerfile, CI/CD, IaC | Deployment configs, pipeline files |
| **Testing** | Test files, fixtures, mocks | `*_test.*`, `*.spec.*`, `__tests__/` |

**1.2 Build the Element Inventory**

Create a complete inventory before documenting. Use:
```bash
bash scripts/inventory_elements.sh <project_root> <output_file>
```

**1.3 Handle Non-Standard Elements**

If you find elements that don't fit the categories above:
1. Create a new category
2. Document the category's purpose
3. Apply the same replicability standards

**The framework adapts to the project, not the other way around.**

**1.4 Document Discoveries and Surprises**

Real projects contain surprises. These are often the MOST IMPORTANT things to document because they're the hardest to discover:

| Discovery Type | Example | How to Document |
|----------------|---------|-----------------|
| **Implicit Rules** | "Orders over $1000 require manager approval" (found in code, not docs) | Create explicit business rule with source code reference |
| **Hidden Dependencies** | Service A secretly calls Service B for validation | Document in both A and B specs, explain the coupling |
| **Legacy Workarounds** | "We parse this field differently because of a 2019 bug" | Document the workaround AND the original bug context |
| **Undocumented APIs** | Internal endpoints used by admin tools | Full API spec, note "undocumented" status |
| **Magic Numbers** | `if (retries > 3)` - why 3? | Document the number AND reasoning if discoverable |
| **Implicit Ordering** | "This must run before that" with no explicit dependency | Document the ordering constraint explicitly |
| **Environment-Specific Behavior** | Different logic in prod vs dev | Document ALL environment variations |
| **Technical Debt** | "This should be refactored but works" | Document current behavior AND known issues |

**Key principle:** If you had to figure something out by reading code, that means it wasn't documented. Document it now so the next person doesn't have to.

### Phase 2: Deep Extraction

For each element in the inventory, extract complete specifications.

**2.1 Extraction Template**

Apply this template to every significant element:

```markdown
## [Element Name]

### Source
- Source: path/to/file.ext
- Source: path/to/file.ext#SymbolName
- Source: path/to/file.ext:123

### Purpose
What problem does this solve? Why does it exist?

### Interface
- Inputs: [All input parameters, types, constraints, defaults]
- Outputs: [All output forms, types, structures]
- Side effects: [State changes, external calls, events emitted]

### Logic
[Complete decision tree or algorithm description]
- Step 1: ...
- Step 2: ...
- Conditions: if X then Y, else Z
- Loops: for each item in collection, do...

### Constraints
- Validation rules: [All input validation]
- Business rules: [Domain constraints]
- Technical limits: [Size limits, rate limits, timeouts]

### Dependencies
- Uses: [What this element calls/imports]
- Used by: [What calls/imports this element]
- External: [Third-party services, APIs]

### Error Handling
- Error conditions: [What can go wrong]
- Error responses: [How errors are communicated]
- Recovery: [Retry logic, fallbacks, cleanup]

### Edge Cases
- Empty/null inputs: [Handling]
- Maximum values: [Handling]
- Concurrent access: [Handling]
- [Any other edge cases specific to this element]
```

**2.2 Extraction Checklist by Element Type**

See `references/extraction-checklist.md` for detailed checklists for:
- API endpoints
- Database entities
- Business logic modules
- UI components
- Background jobs
- Integration adapters

### Phase 3: Cross-Cutting Concerns

Document aspects that span multiple elements:

**3.1 Data Flow**
- How data enters the system
- How data transforms through layers
- How data exits the system
- Data validation checkpoints

**3.2 Authentication & Authorization**
- Auth mechanisms (JWT, sessions, API keys, OAuth)
- Permission model (RBAC, ABAC, custom)
- Protected resources and access rules

**3.3 Error Strategy**
- Global error handling patterns
- Error code taxonomy
- Logging and monitoring hooks
- User-facing error messages

**3.4 State Management**
- What state exists (DB, cache, session, UI state)
- State consistency guarantees
- State synchronization mechanisms

**3.5 Performance Characteristics**
- Caching strategies
- Query optimization patterns
- Async/background processing
- Rate limiting

### Phase 4: Test Specifications

Extract testable specifications that serve as both documentation and validation criteria.

**4.1 Unit Test Specs**

For each function/method with business logic:
```markdown
### Function: calculateDiscount(order, customer)

| Scenario | Input | Expected Output | Notes |
|----------|-------|-----------------|-------|
| New customer, small order | order.total=50, customer.isNew=true | 0 | Min threshold not met |
| New customer, large order | order.total=150, customer.isNew=true | 15 | 10% new customer discount |
| VIP customer | order.total=100, customer.tier='VIP' | 20 | 20% VIP discount |
| Combined discounts | order.total=200, customer.isNew=true, hasPromo=true | 30 | Max discount cap |
| Null order | null, customer | throws InvalidInputError | |
```

**4.2 Integration Test Specs**

For each module interaction:
```markdown
### Integration: OrderService → PaymentGateway

| Scenario | Setup | Action | Verification |
|----------|-------|--------|--------------|
| Successful payment | Valid order, funded card | processPayment() | Order status = PAID, payment record created |
| Declined card | Valid order, declined card | processPayment() | Order status = PAYMENT_FAILED, retry scheduled |
| Gateway timeout | Valid order, slow gateway | processPayment() | Timeout after 30s, order status = PENDING |
```

**4.3 E2E Test Specs**

For each critical user journey:
```markdown
### Journey: User completes purchase

Steps:
1. User adds item to cart → Cart shows 1 item
2. User proceeds to checkout → Checkout page loads with cart summary
3. User enters shipping info → Shipping options displayed
4. User selects payment method → Payment form shown
5. User submits order → Order confirmation displayed, email sent

Variations:
- Guest checkout vs logged-in user
- Single item vs multiple items
- Standard vs express shipping
```

### Phase 5: Verification & Validation

**5.1 Completeness Check**

Use scripts to **assist discovery and gap-finding**. These checks are heuristic—they help you find likely missing documentation or broken links, but they do not “prove” completeness.

Run bidirectional verification:

```bash
# Forward: Does every code element have spec coverage?
bash scripts/verify_coverage.sh <project_root> <spec_output>

# Spec → Code: Verify spec anchors map to code (requires Source: lines in your spec).
bash scripts/verify_implementation.sh <spec_output> <project_root>
```

**Source anchors (recommended)**

To make Spec → Code verification practical, add `Source:` lines to your spec markdown. Supported formats:

- `Source: relative/path/to/file.ext`
- `Source: relative/path/to/file.ext#SymbolName` (best-effort text match)
- `Source: relative/path/to/file.ext:123` (line existence check)
- `Source: relative/path/to/file.ext:123#SymbolName`

**5.2 Replication Test**

The ultimate validation—can the spec be used to replicate the project?

```markdown
## Replication Verification Protocol

1. Provide spec to a fresh Claude instance (no access to original code)
2. Ask it to implement [specific module] using only the spec
3. Compare:
   - Does it handle all documented inputs correctly?
   - Does it produce all documented outputs correctly?
   - Does it handle all documented edge cases?
   - Does it follow all documented constraints?

4. Any discrepancy = spec is incomplete. Update and repeat.
```

**5.3 Diff Report**

Generate a report of gaps:
```markdown
## Spec Completeness Report

### Documented and Verified
- [List of elements with complete specs]

### Documented but Unverified
- [List of elements needing verification]

### Found in Code but Not Documented
- [List of elements missing from spec]

### Ambiguous or Unclear
- [List of elements needing clarification]
```

## Output Structure

Default output structure (adapt based on project type):

```
spec/
├── 00_Overview/
│   ├── PROJECT.md              # Identity, tech stack, architecture overview
│   ├── ARCHITECTURE.md         # System design, module relationships
│   ├── GLOSSARY.md             # Domain terms and definitions
│   └── diagrams/               # Architecture diagrams (Mermaid/PlantUML)
│
├── 01_Configuration/
│   ├── ENVIRONMENT.md          # All environment variables
│   ├── FEATURE_FLAGS.md        # Feature toggles and their effects
│   └── schemas/                # Config file schemas (JSON Schema, etc.)
│
├── 02_Data/
│   ├── ENTITIES.md             # All data entities with full field specs
│   ├── RELATIONSHIPS.md        # Entity relationships, constraints
│   ├── MIGRATIONS.md           # Schema evolution history
│   └── schemas/                # Executable schema definitions
│
├── 03_API/
│   ├── ENDPOINTS.md            # All API endpoints
│   ├── AUTHENTICATION.md       # Auth mechanisms and flows
│   ├── ERRORS.md               # Error codes and responses
│   └── openapi/                # OpenAPI specs if applicable
│
├── 04_Business_Logic/
│   ├── RULES.md                # Business rules catalog
│   ├── WORKFLOWS.md            # Multi-step processes
│   ├── STATE_MACHINES.md       # State transitions
│   └── CALCULATIONS.md         # Formulas and algorithms
│
├── 05_Integrations/
│   ├── EXTERNAL_APIS.md        # Third-party API interactions
│   ├── MESSAGING.md            # Queue/event interactions
│   └── STORAGE.md              # File/blob storage interactions
│
├── 06_UI/ (if applicable)
│   ├── COMPONENTS.md           # UI component catalog
│   ├── PAGES.md                # Page structures and routing
│   ├── STATE.md                # Frontend state management
│   └── INTERACTIONS.md         # User interaction patterns
│
├── 07_Infrastructure/
│   ├── DEPLOYMENT.md           # Deployment architecture
│   ├── SCALING.md              # Scaling strategies
│   └── MONITORING.md           # Observability setup
│
├── 08_Testing/
│   ├── UNIT_SPECS.md           # Unit test specifications
│   ├── INTEGRATION_SPECS.md    # Integration test specifications
│   ├── E2E_SPECS.md            # End-to-end test specifications
│   └── test-cases/             # Executable test case files
│
├── 09_Verification/
│   ├── COVERAGE_REPORT.md      # Spec coverage analysis
│   ├── REPLICATION_GUIDE.md    # How to replicate from spec
│   └── KNOWN_GAPS.md           # Documented limitations
│
└── SPEC_INDEX.md               # Master index of all spec documents
```

**Important**: This structure is a starting point. Add, remove, or reorganize sections based on what the project actually contains.

## Resources

**Scripts:**
- `scripts/discover_project.sh` - Initial project scanning and classification
- `scripts/inventory_elements.sh` - Generate element inventory from codebase
- `scripts/verify_coverage.sh` - Check spec completeness against code
- `scripts/verify_implementation.sh` - Validate spec Source anchors map to code
- `scripts/generate_skeleton.sh` - Create output directory structure

**References:**
- `references/extraction-checklist.md` - Detailed checklists by element type
- `references/replicability-criteria.md` - Standards for spec quality

## AI/ML Systems

If the project includes AI/ML components (LLM integrations, ML models, AI agents, RAG systems), document extra details required for replicability:

- Exact prompts and templates (not summaries)
- Model/provider identifiers and versions
- Context management (inputs, tool calls, memory, truncation rules)
- Retrieval (chunking, embedding model, ranking, filters)
- Evaluation datasets and pass/fail criteria

**Key principle:** AI systems require extra documentation because they are non-deterministic. Document exact prompts (not summaries), model versions, and evaluation data.

## Critical Reminders

1. **Framework is a guide, not a constraint**: If the project has elements outside the framework, extend the framework.

2. **Replicability is the only measure**: Every spec element must enable implementation without seeing original code.

3. **Verify bidirectionally**: Code → Spec and Spec → Code. Both directions must be complete.

4. **Document the unexpected**: Legacy code, workarounds, technical debt, and "why" decisions are often the most valuable documentation.

5. **Test specs are part of the spec**: If you can't write a test case for it, you haven't documented it well enough.

6. **AI systems need extra detail**: Prompts, model versions, and evaluation data are essential for replication.
