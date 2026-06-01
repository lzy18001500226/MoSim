# Litho Configuration Guide

## Installation Methods

### Option 1: Install from crates.io (Recommended)
```bash
cargo install deepwiki-rs
```

### Option 2: Build from Source
```bash
git clone https://github.com/sopaco/deepwiki-rs.git
cd deepwiki-rs
cargo build --release
```

## LLM Provider Configuration

### OpenAI
```bash
deepwiki-rs -p ./src \
  --llm-api-base-url https://api.openai.com/v1 \
  --llm-api-key your-openai-api-key \
  --model-efficient gpt-4o-mini \
  --model-powerful gpt-4o
```

### Anthropic Claude
```bash
deepwiki-rs -p ./src \
  --llm-api-base-url https://api.anthropic.com \
  --llm-api-key your-anthropic-api-key \
  --model-efficient claude-3-haiku \
  --model-powerful claude-3-sonnet
```

### Google Gemini
```bash
deepwiki-rs -p ./src \
  --llm-api-base-url https://generativelanguage.googleapis.com/v1beta \
  --llm-api-key your-gemini-api-key \
  --model-efficient gemini-1.5-flash \
  --model-powerful gemini-1.5-pro
```

### Custom API Provider
```bash
deepwiki-rs -p ./src \
  --llm-api-base-url https://your-custom-provider.com/v1 \
  --llm-api-key your-api-key \
  --model-efficient your-efficient-model \
  --model-powerful your-powerful-model
```

## Advanced Configuration Options

### Complete Parameter Reference
```bash
deepwiki-rs [OPTIONS] --path <PATH>

OPTIONS:
    -p, --path <PATH>                    Source code directory path
    -o, --output <DIR>                   Output directory [default: ./litho.docs]
        --target-language <LANG>          Documentation language [en|ja|zh] [default: en]
        --model-efficient <MODEL>         Fast model for quick analysis
        --model-powerful <MODEL>          Capable model for deep analysis
        --llm-api-base-url <URL>          LLM API base URL
        --llm-api-key <KEY>               LLM API key
        --skip-preprocessing              Skip initial code scanning phase
        --skip-research                   Skip AI research phase
        --disable-preset-tools            Disable automatic tool scanning
        --max-tokens <NUMBER>             Maximum tokens per request
        --temperature <NUMBER>            Model temperature [0.0-2.0]
        --timeout <SECONDS>               Request timeout in seconds
```

### Dual Model Setup (Recommended for Production)
```bash
deepwiki-rs -p ./project \
  --model-efficient gpt-4o-mini \
  --model-powerful gpt-4o \
  --llm-api-base-url https://api.openai.com/v1 \
  --llm-api-key your-api-key
```

### Language-Specific Configuration
```bash
# Generate Japanese documentation
deepwiki-rs -p ./src --target-language ja

# Generate Chinese documentation
deepwiki-rs -p ./src --target-language zh
```

### Performance Tuning
```bash
# For large codebases (>100k lines)
deepwiki-rs -p ./large-project \
  --model-efficient gpt-4o-mini \
  --skip-preprocessing \
  --max-tokens 4000

# For memory-constrained environments
deepwiki-rs -p ./project \
  --skip-preprocessing \
  --skip-research \
  --model-efficient gpt-4o-mini

# For maximum quality analysis
deepwiki-rs -p ./critical-project \
  --model-powerful gpt-4o \
  --temperature 0.1
```

## Environment Variables
```bash
# Set API keys via environment variables
export LITHO_API_KEY="your-api-key"
export LITHO_API_BASE_URL="https://api.openai.com/v1"

# Use environment variables in commands
deepwiki-rs -p ./src  # Automatically uses env vars
```

## Configuration File Support
Create `~/litho.toml`:
```toml
[default]
model_efficient = "gpt-4o-mini"
model_powerful = "gpt-4o"
llm_api_base_url = "https://api.openai.com/v1"
output_dir = "./litho.docs"
target_language = "en"
temperature = 0.3

[profile.fast]
model_efficient = "gpt-4o-mini"
skip_preprocessing = true
skip_research = true

[profile.detailed]
model_powerful = "gpt-4o"
temperature = 0.1
```

Use profiles:
```bash
deepwiki-rs -p ./src --profile fast
deepwiki-rs -p ./src --profile detailed
```
