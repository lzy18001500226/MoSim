# Litho Real-World Examples

## 🔍 Code Review Preparation

### Before Code Review
```bash
# Generate architecture overview for feature branch
deepwiki-rs -p ./feature-branch \
  --model-efficient gpt-4o-mini \
  -o ./review-docs \
  --skip-preprocessing
```

**Output Structure:**
```
review-docs/
├── 1. Project Overview.md          # Feature branch purpose
├── 2. Architecture Overview.md     # Added/modified components
└── 3. Changes Summary.md           # Key architectural impacts
```

### PR Documentation Generation
```bash
# Compare main vs feature branch
deepwiki-rs -p ./main -o ./main-docs
deepwiki-rs -p ./feature-branch -o ./feature-docs
# Use diff tools to compare generated documentation
```

## 👥 Team Onboarding

### New Developer Kit
```bash
# Comprehensive onboarding documentation
deepwiki-rs -p ./main-project \
  -o ./onboarding-docs \
  --model-powerful gpt-4o \
  --target-language en
```

**Generated Onboarding Package:**
```
onboarding-docs/
├── 1. Project Overview.md
│   ├── System Purpose & Goals
│   ├── Technology Stack
│   └── Core Business Logic
├── 2. Architecture Overview.md
│   ├── High-Level System Design
│   ├── Module Dependencies
│   └── Data Flow Diagrams
├── 3. Development Workflow.md
│   ├── Code Organization
│   ├── Build Process
│   └── Testing Strategy
└── 4. Getting Started Guide.md
    ├── Local Development Setup
    ├── Common Development Tasks
    └── Troubleshooting Guide
```

### Architecture Decision Records (ADR)
```bash
# Focus on architectural context
deepwiki-rs -p ./project --model-powerful gpt-4o -o ./adr-docs
```

## 🏗️ Architecture Evolution

### Version Comparison
```bash
# Document architectural changes between versions
deepwiki-rs -p ./v1.0 -o ./v1-docs
deepwiki-rs -p ./v2.0 -o ./v2-docs
deepwiki-rs -p ./v3.0 -o ./v3-docs
```

### Migration Planning
```bash
# Before major refactoring
deepwiki-rs -p ./current-system -o ./migration-analysis \
  --model-powerful gpt-4o
```

**Migration Analysis Includes:**
- Current architecture assessment
- Risk identification
- Dependency mapping
- Impact analysis

## 🚀 CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Generate Documentation
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Litho
        run: cargo install deepwiki-rs

      - name: Generate Documentation
        run: |
          deepwiki-rs -p ./src \
            -o ./docs \
            --model-efficient gpt-4o-mini
        env:
          LITHO_API_KEY: ${{ secrets.LITHO_API_KEY }}

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

### Pre-commit Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "🔍 Generating quick documentation..."
deepwiki-rs -p ./src \
  -o ./temp-docs \
  --skip-preprocessing \
  --model-efficient gpt-4o-mini

echo "📝 Adding documentation to commit..."
git add ./temp-docs/
echo "✅ Documentation generated and staged"
```

## 🔧 Project-Specific Examples

### Node.js/TypeScript Project
```bash
deepwiki-rs -p ./frontend \
  --model-powerful gpt-4o \
  --target-language en \
  -o ./frontend-docs
```

**Typical Output for TypeScript:**
```
frontend-docs/
├── 1. Project Overview.md
│   ├── Application Architecture
│   ├── React/Vue/Angular Setup
│   └── Build Configuration
├── 2. Architecture Overview.md
│   ├── Component Hierarchy
│   ├── State Management
│   └── Routing Structure
├── 3. Workflow Overview.md
│   ├── Component Lifecycle
│   ├── Data Flow Patterns
│   └── Event Handling
└── 4. Deep Dive/
    ├── Core Components.md
    ├── API Integration.md
    └── Styling System.md
```

### Rust Backend Project
```bash
deepwiki-rs -p ./backend \
  --model-efficient gpt-4o-mini \
  --model-powerful gpt-4o \
  -o ./rust-docs
```

**Rust-Specific Analysis:**
```
rust-docs/
├── 1. Project Overview.md
│   ├── Cargo.toml Dependencies
│   ├── Architecture Patterns
│   └── Core Crates
├── 2. Architecture Overview.md
│   ├── Module System
│   ├── Thread Safety
│   └── Error Handling
├── 3. Workflow Overview.md
│   ├── Request Processing
│   ├── Database Interactions
│   └── Async Operations
└── 4. Deep Dive/
    ├── Data Structures.md
    ├── Concurrency Patterns.md
    └── Unsafe Code Analysis.md
```

### Multi-Repository Monorepo
```bash
# Analyze entire monorepo
deepwiki-rs -p ./packages \
  --model-powerful gpt-4o \
  -o ./monorepo-docs

# Package-specific analysis
deepwiki-rs -p ./packages/frontend -o ./frontend-docs
deepwiki-rs -p ./packages/backend -o ./backend-docs
deepwiki-rs -p ./packages/shared -o ./shared-docs
```

## 📊 Performance Optimization Examples

### Large Codebase Analysis
```bash
# For codebase > 500k lines
deepwiki-rs -p ./large-project \
  --model-efficient gpt-4o-mini \
  --skip-preprocessing \
  --max-tokens 3000 \
  -o ./large-project-docs
```

### Incremental Documentation
```bash
# Quick updates for small changes
deepwiki-rs -p ./src \
  --skip-preprocessing \
  --skip-research \
  --model-efficient gpt-4o-mini \
  -o ./quick-docs
```

### Focused Analysis
```bash
# Analyze specific module
deepwiki-rs -p ./src/core/authentication \
  --model-powerful gpt-4o \
  -o ./auth-docs
```

## 🎯 Specialized Use Cases

### Security Audit Documentation
```bash
deepwiki-rs -p ./security-sensitive-code \
  --model-powerful gpt-4o \
  -o ./security-docs
```

### Legacy System Documentation
```bash
deepwiki-rs -p ./legacy-system \
  --model-efficient gpt-4o-mini \
  --model-powerful gpt-4o \
  -o ./legacy-docs
```

### API Documentation Generation
```bash
deepwiki-rs -p ./api-endpoints \
  --model-powerful gpt-4o \
  -o ./api-docs
```

## 📈 Quality Assurance

### Documentation Quality Check
```bash
# Generate with dual models for quality assurance
deepwiki-rs -p ./critical-path \
  --model-efficient gpt-4o-mini \
  --model-powerful gpt-4o \
  -o ./quality-docs
```

### Multi-Language Documentation
```bash
# Generate documentation in multiple languages
deepwiki-rs -p ./src --target-language en -o ./docs-en
deepwiki-rs -p ./src --target-language ja -o ./docs-ja
deepwiki-rs -p ./src --target-language zh -o ./docs-zh
```

These examples demonstrate Litho's versatility across different scenarios, project types, and organizational needs. Choose the appropriate configuration based on your specific use case and constraints.