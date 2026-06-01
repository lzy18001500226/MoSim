---
name: deepwiki-rs
description: "AI-powered Rust documentation generation engine for comprehensive codebase analysis, C4 architecture diagrams, and automated technical documentation. Use when Claude needs to analyze source code, understand software architecture, generate technical specs, or create professional documentation from any programming language."
---

# Litho (deepwiki-rs) - AI-Powered Documentation Generation

## Quick Start Guide

**Use Litho when you need to:**
- Analyze entire codebases and generate architecture documentation
- Create C4 model diagrams (Context, Container, Component, Code)
- Understand complex software systems and module relationships
- Generate comprehensive technical specifications
- Document architecture evolution and design decisions

**Core Workflow:**
```bash
# Basic codebase analysis
deepwiki-rs -p ./src

# Complete C4 documentation with dual models
deepwiki-rs -p ./project --model-efficient gpt5-mini --model-powerful gpt5
```

## Decision Tree

### 📋 **Comprehensive Documentation** → Use "Full Litho Workflow"
Generate complete C4 model documentation with architecture diagrams and technical specs.

### ⚡ **Quick Code Analysis** → Use "Basic Analysis Mode"
Fast code insights without full documentation pipeline.

### 🏗️ **Architecture Understanding** → Use "Advanced C4 Generation"
Deep architectural analysis with detailed component relationships.

### 🔄 **CI/CD Integration** → Use "Automated Pipeline"
Continuous documentation generation for development workflows.

## Key Capabilities

### Multi-Language Support
- Rust, Python, Java, Go, C#, JavaScript/TypeScript
- Any language with recognizable code structure

### Documentation Structure
```
project-docs/
├── 1. Project Overview
├── 2. Architecture Overview
├── 3. Workflow Overview
└── 4. Deep Dive/
    ├── Topic1.md
    └── Topic2.md
```

### Essential Parameters
- `-p, --path`: Source directory
- `-o, --output`: Output location (default: ./litho.docs)
- `--model-efficient`: Fast model for quick analysis
- `--model-powerful`: Capable model for deep analysis
- `--skip-preprocessing`: Skip initial scanning phase
- `--skip-research`: Skip AI research phase

## Advanced Resources

For detailed configuration, troubleshooting, and advanced patterns:
- See [configuration.md](./configuration.md) for comprehensive setup guides
- See [examples.md](./examples.md) for real-world usage patterns
- See [integration.md](./integration.md) for CI/CD and automation
- See [troubleshooting.md](./troubleshooting.md) for common issues

## Security & Performance Notes

- Install only from trusted sources
- Use `--model-efficient` for large codebases
- Batch processing helps avoid API rate limits
- Memory-constrained environments: use `--skip-preprocessing`

## Installation
```bash
# Install from crates.io (recommended)
cargo install deepwiki-rs

# Build from source
git clone https://github.com/sopaco/deepwiki-rs.git && cd deepwiki-rs && cargo build --release
```
