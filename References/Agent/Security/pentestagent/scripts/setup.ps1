# PentestAgent PowerShell Setup Script

Write-Host "=================================================================="
Write-Host "                        PENTESTAGENT"
Write-Host "                  AI Penetration Testing"
Write-Host "=================================================================="
Write-Host ""
Write-Host "Setup"
Write-Host ""

# Check Python version
Write-Host "Checking Python version..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "Error: Python 3.10 or higher is required"
            exit 1
        }
        Write-Host "[OK] $pythonVersion"
    }
} catch {
    Write-Host "Error: Python not found. Please install Python 3.10+"
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..."
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "[OK] Virtual environment created"
} else {
    Write-Host "[OK] Virtual environment exists"
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
pip install -e ".[all]"
Write-Host "[OK] Dependencies installed"

# Install playwright browsers
Write-Host "Installing Playwright browsers..."
playwright install chromium
Write-Host "[OK] Playwright browsers installed"

# Create .env file if not exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    @"
# PentestAgent Configuration

# API Keys (set at least one for chat model)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# For web search functionality (optional)
TAVILY_API_KEY=

# Chat Model (any LiteLLM-supported model)
# OpenAI: gpt-5, gpt-4.1, gpt-4.1-mini
# Anthropic: claude-sonnet-4-20250514, claude-opus-4-20250514
# Google: gemini models require gemini/ prefix (e.g., gemini/gemini-2.5-flash)
# Other providers: azure/, bedrock/, groq/, ollama/, together_ai/ (see litellm docs)
PENTESTAGENT_MODEL=gpt-5

# Embeddings (for RAG knowledge base)
# Options: openai, local (default: openai if OPENAI_API_KEY set, else local)
# PENTESTAGENT_EMBEDDINGS=local

# Settings
PENTESTAGENT_DEBUG=false

# Agent max iterations (regular agent + crew workers, default: 30)
# PENTESTAGENT_AGENT_MAX_ITERATIONS=30

# Orchestrator max iterations (crew mode coordinator, default: 50)
# PENTESTAGENT_ORCHESTRATOR_MAX_ITERATIONS=50
"@ | Set-Content -Path ".env" -Encoding UTF8
    Write-Host "[OK] .env file created"
    Write-Host "[!] Please edit .env and add your API keys"
}

# Load .env into process environment variables (so the script can use them)
if (Test-Path -Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^(?:\s*#)|(?:\s*$)') { return }
        if ($_ -match '^(\s*([^=]+)?)=(.*)$') {
            $name = $Matches[2].Trim()
            $value = $Matches[3].Trim()
            if ($name) { [Environment]::SetEnvironmentVariable($name, $value, 'Process') }
        }
    }
}

# Create loot directory for reports
New-Item -ItemType Directory -Force -Path "loot" | Out-Null
Write-Host "[OK] Loot directory created"

Write-Host ""
Write-Host "Setup complete!"
Write-Host ""
Write-Host "To get started:"
Write-Host "  1. Edit .env and add your API keys"
Write-Host "  2. Activate: .\venv\Scripts\Activate.ps1"
Write-Host "  3. Run: pentestagent or python -m pentestagent"
Write-Host ""
