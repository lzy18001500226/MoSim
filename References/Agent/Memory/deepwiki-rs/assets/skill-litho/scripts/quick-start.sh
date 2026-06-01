#!/bin/bash
# Litho Quick Start Script
# This script helps users get started with Litho quickly

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Litho Quick Start Script      ${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_step() {
    echo -e "\n${GREEN}➡️  $1${NC}"
}

print_warning() {
    echo -e "\n${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "\n${RED}❌  $1${NC}"
}

print_success() {
    echo -e "\n${GREEN}✅  $1${NC}"
}

check_prerequisites() {
    print_step "Checking prerequisites..."

    # Check if Rust is installed
    if ! command -v cargo &> /dev/null; then
        print_error "Rust/Cargo not found. Please install Rust first:"
        echo "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        echo "source ~/.cargo/env"
        exit 1
    fi

    # Check Rust version
    RUST_VERSION=$(rustc --version | cut -d' ' -f2)
    echo "Found Rust version: $RUST_VERSION"

    # Check if we're in a directory with source code
    if [[ ! -d "./src" && ! -d "./lib" && ! -f "Cargo.toml" && ! -f "package.json" ]]; then
        print_warning "No typical source directory found in current location."
        read -p "Do you want to analyze the current directory anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Please run this script from your project root directory."
            exit 1
        fi
    fi

    print_success "Prerequisites check passed!"
}

install_litho() {
    print_step "Installing Litho..."

    if command -v deepwiki-rs &> /dev/null; then
        print_warning "Litho is already installed. Checking for updates..."
        if ! cargo install --list | grep -q "deepwiki-rs"; then
            print_warning "Litho installation found but not properly registered. Reinstalling..."
            cargo install deepwiki-rs
        else
            print_success "Litho is already installed and ready!"
        fi
    else
        print_stepInstalling Litho for the first time..."
        cargo install deepwiki-rs
        print_success "Litho installed successfully!"
    fi
}

setup_api_credentials() {
    print_step "Setting up API credentials..."

    # Check for existing API keys
    if [[ -n "${OPENAI_API_KEY:-}" || -n "${LITHO_API_KEY:-}" ]]; then
        print_success "API credentials already found in environment!"
        return
    fi

    echo -e "${YELLOW}To use Litho, you need an LLM provider API key.${NC}"
    echo "Supported providers:"
    echo "1. OpenAI (GPT models)"
    echo "2. Anthropic (Claude models)"
    echo "3. Google (Gemini models)"
    echo "4. Custom API endpoint"

    read -p "Which provider do you want to use? (1-4): " -n 1 -r
    echo

    case $REPLY in
        1)
            echo "OpenAI selected. Please enter your API key:"
            read -s -p "OpenAI API Key: " API_KEY
            echo
            export OPENAI_API_KEY="$API_KEY"
            export LITHO_API_KEY="$API_KEY"
            export LITHO_API_BASE_URL="https://api.openai.com/v1"
            MODEL_EFFICIENT="gpt-4o-mini"
            MODEL_POWERFUL="gpt-4o"
            ;;
        2)
            echo "Anthropic selected. Please enter your API key:"
            read -s -p "Anthropic API Key: " API_KEY
            echo
            export ANTHROPIC_API_KEY="$API_KEY"
            export LITHO_API_KEY="$API_KEY"
            export LITHO_API_BASE_URL="https://api.anthropic.com"
            MODEL_EFFICIENT="claude-3-haiku-20240307"
            MODEL_POWERFUL="claude-3-sonnet-20240229"
            ;;
        3)
            echo "Google selected. Please enter your API key:"
            read -s -p "Google API Key: " API_KEY
            echo
            export LITHO_API_KEY="$API_KEY"
            export LITHO_API_BASE_URL="https://generativelanguage.googleapis.com/v1beta"
            MODEL_EFFICIENT="gemini-1.5-flash"
            MODEL_POWERFUL="gemini-1.5-pro"
            ;;
        4)
            echo "Custom API endpoint selected."
            read -p "API Base URL: " API_URL
            read -s -p "API Key: " API_KEY
            echo
            export LITHO_API_KEY="$API_KEY"
            export LITHO_API_BASE_URL="$API_URL"
            MODEL_EFFICIENT="your-efficient-model"
            MODEL_POWERFUL="your-powerful-model"
            ;;
        *)
            print_error "Invalid selection. Please run the script again."
            exit 1
            ;;
    esac

    print_success "API credentials configured!"
}

analyze_project() {
    print_step "Analyzing your project..."

    # Detect source directory
    SOURCE_DIR="."
    if [[ -d "./src" ]]; then
        SOURCE_DIR="./src"
    elif [[ -d "./lib" ]]; then
        SOURCE_DIR="./lib"
    fi

    echo "Analyzing directory: $SOURCE_DIR"

    # Create output directory
    OUTPUT_DIR="./litho-docs"
    mkdir -p "$OUTPUT_DIR"

    # Run Litho with efficient model first
    print_step "Running initial analysis with efficient model..."
    deepwiki-rs -p "$SOURCE_DIR" \
        -o "$OUTPUT_DIR" \
        --model-efficient "${MODEL_EFFICIENT:-gpt-4o-mini}" \
        --skip-preprocessing

    print_success "Initial documentation generated in $OUTPUT_DIR/"
}

show_results() {
    print_step "Documentation generation complete!"

    echo -e "\n${BLUE}Generated Files:${NC}"
    if [[ -d "./litho-docs" ]]; then
        find ./litho-docs -name "*.md" -type f | head -10 | while read -r file; do
            echo "  📄 $file"
        done

        total_files=$(find ./litho-docs -name "*.md" -type f | wc -l)
        echo "  📊 Total files: $total_files"
    fi

    echo -e "\n${BLUE}Next Steps:${NC}"
    echo "1. Review the generated documentation in ./litho-docs/"
    echo "2. For higher quality docs, run: deepwiki-rs -p ./src --model-powerful ${MODEL_POWERFUL:-gpt-4o}"
    echo "3. Check the configuration guide: assets/configuration.md"
    echo "4. Explore examples: assets/examples.md"

    echo -e "\n${BLUE}Useful Commands:${NC}"
    echo "• Generate quick docs: deepwiki-rs -p ./src --skip-preprocessing"
    echo "• Generate comprehensive docs: deepwiki-rs -p ./src --model-powerful ${MODEL_POWERFUL:-gpt-4o}"
    echo "• Multi-language docs: deepwiki-rs -p ./src --target-language ja"
}

# Main execution
main() {
    print_header
    check_prerequisites
    install_litho
    setup_api_credentials
    analyze_project
    show_results

    print_success "Litho setup complete! 🎉"
}

# Run main function
main "$@"
