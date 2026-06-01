# Litho Integration & Automation Guide

## 🔄 CI/CD Pipeline Integration

### GitHub Actions
```yaml
# .github/workflows/litho-docs.yml
name: Litho Documentation Generation

on:
  push:
    branches: [main, develop]
    paths: ['src/**', 'lib/**', 'config/**']
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pages: write
      id-token: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: stable

      - name: Cache Cargo dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            target
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

      - name: Install Litho
        run: cargo install deepwiki-rs

      - name: Generate Documentation
        run: |
          echo "🔍 Analyzing codebase..."
          deepwiki-rs -p ./src \
            -o ./generated-docs \
            --model-efficient gpt-4o-mini \
            --model-powerful gpt-4o
        env:
          LITHO_API_KEY: ${{ secrets.LITHO_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Document Quality Check
        run: |
          echo "📊 Document analysis statistics..."
          find ./generated-docs -name "*.md" | wc -l

      - name: Archive Documentation Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: documentation-${{ github.sha }}
          path: ./generated-docs/
          retention-days: 30

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./generated-docs
          destination_dir: docs
```

### GitLab CI/CD
```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - deploy

variables:
  LITHO_VERSION: "latest"

analyze_codebase:
  stage: analyze
  image: rust:latest
  cache:
    paths:
      - target/
      - .cargo/
  before_script:
    - export CARGO_HOME=$CI_PROJECT_DIR/.cargo
    - cargo install deepwiki-rs
  script:
    - deepwiki-rs -p ./src -o ./docs --model-efficient gpt-4o-mini
  artifacts:
    paths:
      - docs/
    expire_in: 1 week
  only:
    - main
    - merge_requests

deploy_docs:
  stage: deploy
  image: alpine:latest
  script:
    - echo "Deploying documentation to production..."
    # Add your deployment logic here
  dependencies:
    - analyze_codebase
  only:
    - main
```

### Azure Pipelines
```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pr:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  LITHO_API_KEY: $(LITHO_API_KEY)

stages:
- stage: Analyze
  displayName: 'Code Analysis & Documentation'
  jobs:
  - job: GenerateDocs
    displayName: 'Generate Documentation with Litho'
    steps:
    - checkout: self
      fetchDepth: 0

    - task: RustToolchain@1
      inputs:
        toolchain: 'stable'

    - script: |
        cargo install deepwiki-rs
        deepwiki-rs -p ./src -o ./documentation --model-efficient gpt-4o-mini
      displayName: 'Install Litho and Generate Docs'
      env:
        LITHO_API_KEY: $(LITHO_API_KEY)

    - publish: $(Build.ArtifactStagingDirectory)/documentation
      artifact: documentation
```

## 🔧 Development Workflow Integration

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running Litho quick analysis..."

# Check if there are source code changes
if git diff --cached --name-only | grep -E '\.(rs|py|js|ts|java|go|cs)$' > /dev/null; then
  echo "📝 Generating quick documentation for staged changes..."

  # Create temp directory for documentation
  TEMP_DIR=$(mktemp -d)

  # Generate documentation for changed files
  deepwiki-rs -p ./src \
    -o "$TEMP_DIR" \
    --skip-preprocessing \
    --skip-research \
    --model-efficient gpt-4o-mini

  # Add generated documentation to commit
  git add "$TEMP_DIR"

  echo "✅ Documentation generated and staged"
  rm -rf "$TEMP_DIR"
fi

echo "🚀 Continuing with commit..."
```

### Post-commit Hooks
```bash
#!/bin/bash
# .git/hooks/post-commit

echo "📚 Generating comprehensive documentation in background..."

# Run full documentation generation in background
nohup deepwiki-rs -p ./src \
  -o ./docs \
  --model-efficient gpt-4o-mini \
  --model-powerful gpt-4o \
  > /tmp/litho-generation.log 2>&1 &

echo "🔄 Background documentation started. Check /tmp/litho-generation.log for progress."
```

## 🎯 Makefile Integration

```makefile
# Makefile
.PHONY: docs docs-quick docs-full clean-docs help

# Default documentation generation
docs:
	@echo "🔍 Generating comprehensive documentation..."
	deepwiki-rs -p ./src -o ./docs --model-efficient gpt-4o-mini

# Quick documentation for development
docs-quick:
	@echo "⚡ Generating quick documentation..."
	deepwiki-rs -p ./src -o ./docs-temp --skip-preprocessing --skip-research

# Full documentation with quality analysis
docs-full:
	@echo "📊 Generating full documentation with quality analysis..."
	deepwiki-rs -p ./src -o ./docs-full \
		--model-efficient gpt-4o-mini \
		--model-powerful gpt-4o

# Clean generated documentation
clean-docs:
	@echo "🧹 Cleaning generated documentation..."
	rm -rf ./docs ./docs-temp ./docs-full

# Multi-language documentation
docs-multilang:
	@echo "🌍 Generating multi-language documentation..."
	deepwiki-rs -p ./src --target-language en -o ./docs-en
	deepwiki-rs -p ./src --target-language ja -o ./docs-ja
	deepwiki-rs -p ./src --target-language zh -o ./docs-zh

# API documentation
docs-api:
	@echo "📡 Generating API documentation..."
	deepwiki-rs -p ./src/api -o ./docs-api --model-powerful gpt-4o

# Help
help:
	@echo "Available documentation targets:"
	@echo "  docs         - Generate basic documentation"
	@echo "  docs-quick   - Quick documentation for development"
	@echo "  docs-full    - Full documentation with quality analysis"
	@echo "  clean-docs   - Clean generated documentation"
	@echo "  docs-multilang - Generate documentation in multiple languages"
	@echo "  docs-api     - Generate API-specific documentation"
	@echo "  help         - Show this help message"
```

## 🚀 Docker Integration

### Dockerfile for Documentation Generation
```dockerfile
# Dockerfile.litho
FROM rust:1.75-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Litho
RUN cargo install deepwiki-rs

# Create work directory
WORKDIR /workspace

# Set environment variables
ENV LITHO_OUTPUT_DIR=/workspace/docs
ENV LITHO_SOURCE_DIR=/workspace/src

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose documentation directory
VOLUME ["/workspace/docs", "/workspace/src"]

ENTRYPOINT ["entrypoint.sh"]
CMD ["generate"]
```

### Entrypoint Script
```bash
#!/bin/bash
# entrypoint.sh

set -euo pipefail

function generate_docs() {
    echo "🔍 Generating Litho documentation..."

    local source_dir="${LITHO_SOURCE_DIR:-/workspace/src}"
    local output_dir="${LITHO_OUTPUT_DIR:-/workspace/docs}"
    local model_efficient="${LITHO_MODEL_EFFICIENT:-gpt-4o-mini}"
    local model_powerful="${LITHO_MODEL_POWERFUL:-gpt-4o}"

    if [[ ! -d "$source_dir" ]]; then
        echo "❌ Source directory not found: $source_dir"
        exit 1
    fi

    deepwiki-rs -p "$source_dir" \
        -o "$output_dir" \
        --model-efficient "$model_efficient" \
        --model-powerful "$model_powerful" \
        ${LITHO_EXTRA_ARGS:-}

    echo "✅ Documentation generated successfully in $output_dir"
}

function watch_docs() {
    echo "👀 Watching for source changes..."

    local source_dir="${LITHO_SOURCE_DIR:-/workspace/src}"

    while inotifywait -r -e modify,create,delete "$source_dir" 2>/dev/null; do
        echo "📝 Source files changed. Regenerating documentation..."
        generate_docs
    done
}

case "${1:-generate}" in
    "generate")
        generate_docs
        ;;
    "watch")
        watch_docs
        ;;
    "shell")
        exec /bin/bash
        ;;
    *)
        echo "Usage: $0 {generate|watch|shell}"
        exit 1
        ;;
esac
```

### Docker Compose Integration
```yaml
# docker-compose.yml
version: '3.8'

services:
  litho:
    build:
      context: .
      dockerfile: Dockerfile.litho
    environment:
      - LITHO_API_KEY=${LITHO_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LITHO_MODEL_EFFICIENT=gpt-4o-mini
      - LITHO_MODEL_POWERFUL=gpt-4o
    volumes:
      - ./src:/workspace/src:ro
      - ./docs:/workspace/docs
    command: generate

  litho-watcher:
    build:
      context: .
      dockerfile: Dockerfile.litho
    environment:
      - LITHO_API_KEY=${LITHO_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./src:/workspace/src
      - ./docs:/workspace/docs
    command: watch
    profiles:
      - watcher
```

## 📊 Monitoring & Alerting

### Documentation Quality Metrics
```bash
#!/bin/bash
# scripts/litho-monitor.sh

function count_docs() {
    find ./docs -name "*.md" -type f | wc -l
}

function doc_size() {
    du -sh ./docs | cut -f1
}

function last_updated() {
    find ./docs -name "*.md" -type f -exec stat -c %Y {} \; | sort -n | tail -1 | xargs -I {} date -d @{} '+%Y-%m-%d %H:%M:%S'
}

echo "📊 Litho Documentation Metrics"
echo "================================"
echo "Total Documents: $(count_docs)"
echo "Documentation Size: $(doc_size)"
echo "Last Updated: $(last_updated)"

# Alert if documentation is too small
if [[ $(count_docs) -lt 5 ]]; then
    echo "⚠️  Warning: Documentation seems incomplete (less than 5 files)"
fi

# Alert if documentation is old
last_timestamp=$(find ./docs -name "*.md" -type f -exec stat -c %Y {} \; | sort -n | tail -1)
current_timestamp=$(date +%s)
age=$((current_timestamp - last_timestamp))
age_days=$((age / 86400))

if [[ $age_days -gt 7 ]]; then
    echo "⚠️  Warning: Documentation is $age_days days old"
fi
```

## 🔐 Security Considerations

### Secrets Management
```yaml
# GitHub Actions with secure secrets
- name: Generate Documentation
  env:
    LITHO_API_KEY: ${{ secrets.LITHO_API_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    # Never echo secrets
    deepwiki-rs -p ./src -o ./docs --model-efficient gpt-4o-mini
```

### Container Security
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' litho
USER litho
```

### Input Validation
```bash
#!/bin/bash
# Validate source directory before processing
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "❌ Invalid source directory: $SOURCE_DIR"
    exit 1
fi

# Check for suspicious files
if find "$SOURCE_DIR" -name "*.exe" -o -name "*.bat" -o -name "*.sh" | grep -q .; then
    echo "⚠️  Warning: Executable files found in source directory"
fi
```

This integration guide ensures Litho works seamlessly with your existing development infrastructure while maintaining security and quality standards.