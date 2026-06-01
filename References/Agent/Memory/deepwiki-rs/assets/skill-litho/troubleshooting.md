# Litho Troubleshooting Guide

## 🔧 Common Issues & Solutions

### Installation Problems

#### **Issue**: Cargo installation fails
```
Error: could not find `deepwiki-rs` in registry
```
**Solutions:**
1. Update Cargo index:
```bash
cargo update
```
2. Install from source:
```bash
git clone https://github.com/sopaco/deepwiki-rs.git
cd deepwiki-rs
cargo build --release
cargo install --path .
```
3. Check Rust version:
```bash
rustc --version  # Should be 1.70+
```

#### **Issue**: Permission denied during installation
**Solution:**
```bash
# Use user installation
cargo install --user deepwiki-rs

# Or set Cargo home directory
export CARGO_HOME="$HOME/.cargo"
cargo install deepwiki-rs
```

### API Configuration Issues

#### **Issue**: API key not recognized
```
Error: Invalid API key or authentication failed
```
**Diagnostic Steps:**
```bash
# Test API key manually
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models

# Check environment variables
echo $LITHO_API_KEY
echo $OPENAI_API_KEY
```

**Solutions:**
1. Set environment variables properly:
```bash
export LITHO_API_KEY="your-api-key"
export OPENAI_API_KEY="your-openai-key"
```
2. Use command-line flags:
```bash
deepwiki-rs -p ./src --llm-api-key "your-api-key"
```
3. Create config file `~/litho.toml`:
```toml
[default]
llm_api_key = "your-api-key"
llm_api_base_url = "https://api.openai.com/v1"
```

#### **Issue**: API endpoint unreachable
```
Error: Network request failed: timeout
```
**Solutions:**
1. Test network connectivity:
```bash
curl -I https://api.openai.com/v1/models
```
2. Use alternative endpoint:
```bash
deepwiki-rs -p ./src --llm-api-base-url "https://api.openai.com/v1"
```
3. Set appropriate timeout:
```bash
deepwiki-rs -p ./src --timeout 120
```

### Memory & Performance Issues

#### **Issue**: Out of memory on large codebase
```
Error: Memory allocation failed
```
**Solutions:**
1. Use memory-efficient configuration:
```bash
deepwiki-rs -p ./large-project \
  --skip-preprocessing \
  --model-efficient gpt-4o-mini \
  --max-tokens 2000
```
2. Process in chunks:
```bash
deepwiki-rs -p ./src/module1 -o ./docs/module1
deepwiki-rs -p ./src/module2 -o ./docs/module2
```
3. Increase system swap space:
```bash
# Linux
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **Issue**: Very slow processing
**Diagnostic Commands:**
```bash
# Monitor CPU and memory usage
htop
# Check disk I/O
iotop
# Monitor network usage
nethogs
```

**Optimization Strategies:**
1. Use efficient model for initial processing:
```bash
deepwiki-rs -p ./src --model-efficient gpt-4o-mini
```
2. Skip preprocessing for incremental updates:
```bash
deepwiki-rs -p ./src --skip-preprocessing
```
3. Parallel processing for multiple directories:
```bash
find ./src -maxdepth 1 -type d | parallel -j 4 'deepwiki-rs -p {} -o ./docs/{/}'
```

### Output Issues

#### **Issue**: Generated documentation is incomplete
```
Warning: Documentation generation completed with warnings
```

**Diagnostic Steps:**
1. Check file counts:
```bash
find ./docs -name "*.md" -type f | wc -l
```
2. Verify source directory:
```bash
find ./src -type f \( -name "*.rs" -o -name "*.py" -o -name "*.js" \) | wc -l
```

**Solutions:**
1. Use more capable model:
```bash
deepwiki-rs -p ./src --model-powerful gpt-4o
```
2. Lower temperature for more consistent output:
```bash
deepwiki-rs -p ./src --temperature 0.1
```
3. Enable verbose logging:
```bash
export RUST_LOG=debug
deepwiki-rs -p ./src -v
```

#### **Issue**: Poor diagram quality
**Solutions:**
1. Regenerate with better model:
```bash
deepwiki-rs -p ./src --model-powerful gpt-4o
```
2. Check Mermaid syntax manually:
```bash
# Test a simple Mermaid diagram
echo "graph TD; A --> B;" | python3 -c "import sys; print('Valid' if 'graph TD' in sys.stdin.read() else 'Invalid')"
```

### Language-Specific Issues

#### **Issue**: Rust code not analyzed properly
**Common Causes:**
- Cargo.toml missing or unreadable
- Multiple workspaces
- Custom build configurations

**Solutions:**
```bash
# Ensure Cargo.toml is present and valid
cd ./rust-project
cargo check
deepwiki-rs -p .

# For workspaces, specify specific member
deepwiki-rs -p ./member-crate
```

#### **Issue**: Node.js project analysis fails
**Diagnostic:**
```bash
# Check package.json validity
cd ./node-project
node -e "JSON.parse(require('fs').readFileSync('package.json'))"
```

**Solutions:**
1. Ensure node_modules is not in source path:
```bash
# Exclude node_modules
deepwiki-rs -p ./src --exclude node_modules
```

### Platform-Specific Issues

#### **Linux/Unix:**
```bash
# Check if binary has execute permissions
chmod +x $(which deepwiki-rs)

# Verify Rust toolchain
rustup show
```

#### **Windows:**
```powershell
# Check PATH environment variable
Get-Command deepwiki-rs -ErrorAction SilentlyContinue

# Reinstall if needed
cargo install --force deepwiki-rs
```

#### **macOS:**
```bash
# Check xcode command line tools
xcode-select --install

# Update Homebrew if installed via brew
brew update && brew upgrade deepwiki-rs
```

## 🐛 Advanced Debugging

### Enable Debug Logging
```bash
# Set Rust log level
export RUST_LOG=debug
export RUST_BACKTRACE=1

# Run with verbose output
deepwiki-rs -p ./src -v

# Full debugging info
RUST_LOG=trace deepwiki-rs -p ./src > debug.log 2>&1
```

### Test with Small Sample
```bash
# Create test directory structure
mkdir -p test-project/src
echo 'fn main() { println!("Hello, world!"); }' > test-project/src/main.rs
cd test-project

# Test Litho on minimal project
deepwiki-rs -p . -o test-docs
```

### Profile Performance
```bash
# Using cargo's built-in profiler
cargo run --release --bin deepwiki-rs -- -p ./src

# With perf (Linux only)
perf record --call-graph dwarf cargo run --release -p deepwiki-rs
perf report

# With flamegraph (Linux)
cargo install flamegraph
cargo flamegraph --bin deepwiki-rs -- -p ./src
```

### Network Debugging
```bash
# Monitor API calls
tcpdump -i any -n 'host api.openai.com'

# Test with curl
curl -v -H "Authorization: Bearer $API_KEY" https://api.openai.com/v1/models

# Check DNS resolution
nslookup api.openai.com
```

## 📋 Quick Reference Commands

### Installation & Setup
```bash
cargo install deepwiki-rs
cargo install --force deepwiki-rs  # Reinstall
cargo uninstall deepwiki-rs     # Uninstall
```

### Basic Troubleshooting
```bash
# Check version
deepwiki-rs --version

# Verify API key
export LITHO_API_KEY="test-key"
deepwiki-rs --help

# Test with simple project
deepwiki-rs -p ./simple-example --model-efficient gpt-4o-mini
```

### Performance Tuning
```bash
# Quick mode
deepwiki-rs -p ./src --skip-preprocessing --model-efficient gpt-4o-mini

# Quality mode
deepwiki-rs -p ./src --model-powerful gpt-4o --temperature 0.1

# Parallel processing
find ./src -maxdepth 2 -type d | parallel -j 2 'deepwiki-rs -p {} -o ./docs/{/}'
```

### Logging & Debugging
```bash
# Enable debug logging
RUST_LOG=debug deepwiki-rs -p ./src

# Create log file
deepwiki-rs -p ./src 2>&1 | tee litho.log

# Backtrace on crash
RUST_BACKTRACE=full deepwiki-rs -p ./src
```

## 🆘 Getting Help

### Community Resources
- **GitHub Issues**: https://github.com/sopaco/deepwiki-rs/issues
- **Documentation**: https://docs.deepwiki.rs
- **Discord Community**: [invite link]

### Bug Report Template
```markdown
## Bug Description
[Describe the issue]

## Environment
- OS: [Linux/Windows/macOS]
- Litho version: [deepwiki-rs --version]
- Rust version: [rustc --version]

## Reproduction Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Minimal Example
[Provide minimal reproduction case]

## Error Logs
[Paste error logs here]

## Additional Context
[Any additional information]
```

### Feature Request Template
```markdown
## Feature Description
[Describe the feature]

## Use Case
[Explain why this is needed]

## Proposed Solution
[How should it work]

## Alternatives Considered
[Other approaches you've considered]
```

Remember to include relevant logs, system information, and minimal reproduction cases when seeking help. The more information you provide, the faster we can assist you.
