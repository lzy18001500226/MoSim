#!/usr/bin/env bash

# Function to check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ Error: $1 is not installed or not in PATH"
        echo "💡 Please run the following command from the repository root:"
        if [ "$1" = "ruff" ]; then
            echo "   uv pip install -r requirements-dev.txt"
        elif [ "$1" = "eslint" ] || [ "$1" = "prettier" ]; then
            echo "   npm install"
        fi
        return 1
    fi
    return 0
}

# Check for required commands
echo "🔍 Checking required dependencies..."
check_command "ruff" && check_command "eslint" && check_command "prettier"
DEPS_STATUS=$?

if [ $DEPS_STATUS -eq 0 ]; then
    DEPS_MESSAGE="All required dependencies are installed"
    echo "✅ $DEPS_MESSAGE"
else
    DEPS_MESSAGE="Missing required dependencies"
    echo "❌ $DEPS_MESSAGE"
fi

return 0  # Always return success