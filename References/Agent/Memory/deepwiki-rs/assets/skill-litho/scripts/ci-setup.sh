#!/bin/bash
# Litho CI/CD Setup Script
# This script sets up Litho documentation generation in CI/CD pipelines

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Litho CI/CD Setup Script      ${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_step() {
    echo -e "\n${GREEN}➡️  $1${NC}"
}

print_warning() {
    echo -e "\n${YELLOW}⚠️  $1${NC}"
}

print_success() {
    echo -e "\n${GREEN}✅  $1${NC}"
}

print_error() {
    echo -e "\n${RED}❌  $1${NC}"
}

detect_ci_platform() {
    print_step "Detecting CI/CD platform..."

    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        CI_PLATFORM="github"
        print_success "GitHub Actions detected"
    elif [[ -n "${GITLAB_CI:-}" ]]; then
        CI_PLATFORM="gitlab"
        print_success "GitLab CI detected"
    elif [[ -n "${AZURE_PIPELINES:-}" ]]; then
        CI_PLATFORM="azure"
        print_success "Azure Pipelines detected"
    elif [[ -n "${JENKINS_URL:-}" ]]; then
        CI_PLATFORM="jenkins"
        print_success "Jenkins detected"
    else
        print_warning "No known CI platform detected. Using generic setup."
        CI_PLATFORM="generic"
    fi
}

setup_github_actions() {
    print_step "Setting up GitHub Actions workflow..."

    mkdir -p .github/workflows

    cat > .github/workflows/litho-docs.yml << 'EOF'
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
          fetch-depth: 0

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@stable

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
          deepwiki-rs -p ./src -o ./generated-docs --model-efficient gpt-4o-mini
        env:
          LITHO_API_KEY: ${{ secrets.LITHO_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload Documentation Artifacts
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
EOF

    print_success "GitHub Actions workflow created at .github/workflows/litho-docs.yml"
    print_warning "Don't forget to add LITHO_API_KEY or OPENAI_API_KEY to your repository secrets!"
}

setup_gitlab_ci() {
    print_step "Setting up GitLab CI configuration..."

    cat > .gitlab-ci.yml << 'EOF'
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
EOF

    print_success "GitLab CI configuration created at .gitlab-ci.yml"
    print_warning "Set LITHO_API_KEY in your GitLab CI/CD variables!"
}

setup_azure_pipelines() {
    print_step "Setting up Azure Pipelines configuration..."

    cat > azure-pipelines.yml << 'EOF'
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
EOF

    print_success "Azure Pipelines configuration created at azure-pipelines.yml"
    print_warning "Add LITHO_API_KEY to your Azure Pipelines variables!"
}

setup_generic_ci() {
    print_step "Creating generic CI script..."

    cat > ci-docs.sh << 'EOF'
#!/bin/bash
# Generic CI script for Litho documentation generation

set -euo pipefail

echo "🔍 Starting Litho documentation generation..."

# Install Rust if not present
if ! command -v cargo &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# Install Litho
if ! command -v deepwiki-rs &> /dev/null; then
    echo "Installing Litho..."
    cargo install deepwiki-rs
fi

# Generate documentation
echo "📚 Generating documentation..."
deepwiki-rs -p ./src -o ./docs --model-efficient gpt-4o-mini

echo "✅ Documentation generation complete!"
EOF

    chmod +x ci-docs.sh
    print_success "Generic CI script created at ci-docs.sh"
}

setup_pre_commit_hooks() {
    print_step "Setting up pre-commit hooks..."

    mkdir -p .git/hooks

    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Litho pre-commit hook

echo "🔍 Running Litho quick analysis..."

# Check if there are source code changes
if git diff --cached --name-only | grep -E '\.(rs|py|js|ts|java|go|cs)$' > /dev/null; then
    echo "📝 Generating quick documentation for staged changes..."

    # Create temp directory for documentation
    TEMP_DIR=$(mktemp -d)

    # Generate documentation for changed files
    if command -v deepwiki-rs &> /dev/null; then
        deepwiki-rs -p ./src \
            -o "$TEMP_DIR" \
            --skip-preprocessing \
            --skip-research \
            --model-efficient gpt-4o-mini

        # Add generated documentation to commit
        git add "$TEMP_DIR"

        echo "✅ Documentation generated and staged"
    else
        echo "⚠️  Litho not found. Skipping documentation generation."
    fi

    rm -rf "$TEMP_DIR"
fi

echo "🚀 Continuing with commit..."
EOF

    chmod +x .git/hooks/pre-commit
    print_success "Pre-commit hook installed"
}

create_makefile_targets() {
    print_step "Adding Litho targets to Makefile..."

    if [[ -f "Makefile" ]]; then
        print_warning "Makefile exists. Appending Litho targets..."
    else
        print_step "Creating new Makefile with Litho targets..."
    fi

    cat >> Makefile << 'EOF'

# Litho Documentation Targets
.PHONY: docs docs-quick docs-full clean-docs help-docs

docs:
	@echo "🔍 Generating comprehensive documentation..."
	deepwiki-rs -p ./src -o ./docs --model-efficient gpt-4o-mini

docs-quick:
	@echo "⚡ Generating quick documentation..."
	deepwiki-rs -p ./src -o ./docs-temp --skip-preprocessing --skip-research

docs-full:
	@echo "📊 Generating full documentation with quality analysis..."
	deepwiki-rs -p ./src -o ./docs-full --model-efficient gpt-4o-mini --model-powerful gpt-4o

clean-docs:
	@echo "🧹 Cleaning generated documentation..."
	rm -rf ./docs ./docs-temp ./docs-full

help-docs:
	@echo "Available documentation targets:"
	@echo "  docs         - Generate basic documentation"
	@echo "  docs-quick   - Quick documentation for development"
	@echo "  docs-full    - Full documentation with quality analysis"
	@echo "  clean-docs   - Clean generated documentation"
	@echo "  help-docs    - Show this help message"
EOF

    print_success "Makefile targets added"
}

setup_secrets_guide() {
    print_step "Creating secrets setup guide..."

    cat > SETUP_SECRETS.md << 'EOF'
# Setting Up API Secrets for Litho CI/CD

## GitHub Actions
1. Go to your repository Settings
2. Click on "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add one of the following:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LITHO_API_KEY`: Your LLM provider API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key

## GitLab CI
1. Go to your project Settings > CI/CD
2. Expand "Variables"
3. Click "Add variable"
4. Add:
   - `LITHO_API_KEY`: Your LLM provider API key
   - Check "Mask variable" for security

## Azure Pipelines
1. Go to your Pipelines > Library
2. Click "+ Variable group"
3. Add variables:
   - `LITHO_API_KEY`: Your LLM provider API key
4. Link the variable group to your pipeline

## Jenkins
1. Go to Manage Jenkins > Manage Credentials
2. Add new credentials
3. Use "Secret text" type
4. Add `LITHO_API_KEY` as ID

## Environment Variables (Local Testing)
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export LITHO_API_KEY="your-api-key"
```
EOF

    print_success "Secrets setup guide created at SETUP_SECRETS.md"
}

main() {
    print_header

    # Check if we're in a project directory
    if [[ ! -d "./src" && ! -d "./lib" && ! -f "Cargo.toml" && ! -f "package.json" ]]; then
        print_error "Please run this script from your project root directory."
        exit 1
    fi

    detect_ci_platform

    # Setup based on detected platform
    case $CI_PLATFORM in
        github)
            setup_github_actions
            ;;
        gitlab)
            setup_gitlab_ci
            ;;
        azure)
            setup_azure_pipelines
            ;;
        generic|*)
            setup_generic_ci
            ;;
    esac

    # Common setup for all platforms
    setup_pre_commit_hooks
    create_makefile_targets
    setup_secrets_guide

    print_success "CI/CD setup complete! 🎉"

    echo -e "\n${BLUE}Next Steps:${NC}"
    echo "1. Configure your API secrets (see SETUP_SECRETS.md)"
    echo "2. Test the workflow by pushing to your repository"
    echo "3. Customize the workflow files as needed"
    echo "4. Check the generated documentation artifacts"
}

# Run main function
main "$@"
