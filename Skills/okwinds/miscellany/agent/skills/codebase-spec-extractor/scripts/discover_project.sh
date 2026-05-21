#!/usr/bin/env bash
set -euo pipefail

# discover_project.sh - Scan a project to identify its type, tech stack, and structure
# Usage: discover_project.sh <project_root> [output_file]

usage() {
  cat <<'EOF'
Usage:
  discover_project.sh <project_root> [output_file]

Scans a project directory to identify:
  - Project type (backend, frontend, fullstack, library, CLI, etc.)
  - Tech stack (languages, frameworks, databases)
  - Entry points and build system
  - Directory structure patterns
  - Key files for further analysis

If output_file is provided, results are written there; otherwise printed to stdout.
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

root="$1"
output="${2:-}"

if [[ ! -d "$root" ]]; then
  echo "Error: Directory not found: $root" >&2
  exit 1
fi

root="$(cd "$root" && pwd)"

# Redirect output if file specified
if [[ -n "$output" ]]; then
  mkdir -p "$(dirname "$output")"
  exec > "$output"
fi

echo "# Project Discovery Report"
echo "root: $root"
echo "generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Helper: check if file exists (glob-safe)
has_file() {
  local pattern="$1"
  compgen -G "$root/$pattern" > /dev/null 2>&1
}

# Helper: count files matching pattern
count_files() {
  local pattern="$1"
  find "$root" -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Helper: list files matching pattern (limited)
list_files() {
  local pattern="$1"
  local limit="${2:-10}"
  find "$root" -name "$pattern" -type f 2>/dev/null | head -n "$limit" | sed "s|^$root/||"
}

echo "## Tech Stack Detection"
echo ""

# Languages
echo "### Languages"
lang_names=(
  "JavaScript"
  "TypeScript"
  "Python"
  "Go"
  "Rust"
  "Java"
  "Kotlin"
  "Ruby"
  "PHP"
  "C#"
  "Swift"
)

lang_globs=(
  "*.js"
  "*.ts"
  "*.py"
  "*.go"
  "*.rs"
  "*.java"
  "*.kt"
  "*.rb"
  "*.php"
  "*.cs"
  "*.swift"
)

for i in "${!lang_names[@]}"; do
  lang="${lang_names[$i]}"
  count=$(count_files "${lang_globs[$i]}")
  if [[ $count -gt 0 ]]; then
    echo "- $lang: $count files"
  fi
done
echo ""

# Package managers / build tools
echo "### Package Managers & Build Tools"
[[ -f "$root/package.json" ]] && echo "- npm/yarn/pnpm (package.json found)"
[[ -f "$root/package-lock.json" ]] && echo "  - Uses npm (package-lock.json)"
[[ -f "$root/yarn.lock" ]] && echo "  - Uses yarn (yarn.lock)"
[[ -f "$root/pnpm-lock.yaml" ]] && echo "  - Uses pnpm (pnpm-lock.yaml)"
[[ -f "$root/requirements.txt" ]] && echo "- pip (requirements.txt found)"
[[ -f "$root/Pipfile" ]] && echo "- pipenv (Pipfile found)"
[[ -f "$root/pyproject.toml" ]] && echo "- Poetry/modern Python (pyproject.toml found)"
[[ -f "$root/go.mod" ]] && echo "- Go modules (go.mod found)"
[[ -f "$root/Cargo.toml" ]] && echo "- Cargo/Rust (Cargo.toml found)"
[[ -f "$root/pom.xml" ]] && echo "- Maven (pom.xml found)"
[[ -f "$root/build.gradle" ]] && echo "- Gradle (build.gradle found)"
[[ -f "$root/Gemfile" ]] && echo "- Bundler/Ruby (Gemfile found)"
[[ -f "$root/composer.json" ]] && echo "- Composer/PHP (composer.json found)"
echo ""

# Frameworks detection
echo "### Frameworks Detected"

# JavaScript/TypeScript frameworks
if [[ -f "$root/package.json" ]]; then
  if grep -q '"react"' "$root/package.json" 2>/dev/null; then
    echo "- React"
    grep -q '"next"' "$root/package.json" 2>/dev/null && echo "  - Next.js"
    grep -q '"gatsby"' "$root/package.json" 2>/dev/null && echo "  - Gatsby"
  fi
  grep -q '"vue"' "$root/package.json" 2>/dev/null && echo "- Vue.js"
  grep -q '"nuxt"' "$root/package.json" 2>/dev/null && echo "  - Nuxt.js"
  grep -q '"@angular/core"' "$root/package.json" 2>/dev/null && echo "- Angular"
  grep -q '"svelte"' "$root/package.json" 2>/dev/null && echo "- Svelte"
  grep -q '"express"' "$root/package.json" 2>/dev/null && echo "- Express.js"
  grep -q '"fastify"' "$root/package.json" 2>/dev/null && echo "- Fastify"
  grep -q '"nest"' "$root/package.json" 2>/dev/null && echo "- NestJS"
  grep -q '"koa"' "$root/package.json" 2>/dev/null && echo "- Koa"
  grep -q '"hono"' "$root/package.json" 2>/dev/null && echo "- Hono"
fi

# Python frameworks
if [[ -f "$root/requirements.txt" ]] || [[ -f "$root/pyproject.toml" ]]; then
  grep -qi 'django' "$root/requirements.txt" "$root/pyproject.toml" 2>/dev/null && echo "- Django"
  grep -qi 'flask' "$root/requirements.txt" "$root/pyproject.toml" 2>/dev/null && echo "- Flask"
  grep -qi 'fastapi' "$root/requirements.txt" "$root/pyproject.toml" 2>/dev/null && echo "- FastAPI"
  grep -qi 'starlette' "$root/requirements.txt" "$root/pyproject.toml" 2>/dev/null && echo "- Starlette"
fi

# Go frameworks
if [[ -f "$root/go.mod" ]]; then
  grep -q 'gin-gonic/gin' "$root/go.mod" 2>/dev/null && echo "- Gin"
  grep -q 'labstack/echo' "$root/go.mod" 2>/dev/null && echo "- Echo"
  grep -q 'gofiber/fiber' "$root/go.mod" 2>/dev/null && echo "- Fiber"
fi
echo ""

# Database indicators
echo "### Database Indicators"
# ORM/DB libraries
if [[ -f "$root/package.json" ]]; then
  grep -q '"prisma"' "$root/package.json" 2>/dev/null && echo "- Prisma ORM"
  grep -q '"typeorm"' "$root/package.json" 2>/dev/null && echo "- TypeORM"
  grep -q '"sequelize"' "$root/package.json" 2>/dev/null && echo "- Sequelize"
  grep -q '"mongoose"' "$root/package.json" 2>/dev/null && echo "- Mongoose (MongoDB)"
  grep -q '"pg"' "$root/package.json" 2>/dev/null && echo "- PostgreSQL client"
  grep -q '"mysql"' "$root/package.json" 2>/dev/null && echo "- MySQL client"
  grep -q '"redis"' "$root/package.json" 2>/dev/null && echo "- Redis client"
fi

# Schema files
has_file "prisma/schema.prisma" && echo "- Prisma schema found"
has_file "*.sql" && echo "- SQL files found: $(count_files '*.sql')"
[[ -d "$root/migrations" ]] && echo "- migrations/ directory found"
[[ -d "$root/db/migrate" ]] && echo "- db/migrate/ directory found (Rails-style)"
echo ""

# Project type inference
echo "## Project Type Analysis"
echo ""

project_types=()

# Frontend indicators
frontend_score=0
[[ -d "$root/src/components" ]] && ((frontend_score+=2))
[[ -d "$root/components" ]] && ((frontend_score+=2))
[[ -d "$root/pages" ]] && ((frontend_score+=1))
[[ -d "$root/app" ]] && ((frontend_score+=1))
[[ -f "$root/index.html" ]] && ((frontend_score+=1))
has_file "*.tsx" && ((frontend_score+=2))
has_file "*.vue" && ((frontend_score+=2))
has_file "*.svelte" && ((frontend_score+=2))

# Backend indicators
backend_score=0
[[ -d "$root/api" ]] && ((backend_score+=2))
[[ -d "$root/routes" ]] && ((backend_score+=2))
[[ -d "$root/controllers" ]] && ((backend_score+=2))
[[ -d "$root/services" ]] && ((backend_score+=1))
[[ -d "$root/models" ]] && ((backend_score+=1))
has_file "*.sql" && ((backend_score+=1))
[[ -d "$root/migrations" ]] && ((backend_score+=1))

# Library indicators
library_score=0
[[ -d "$root/lib" ]] && ((library_score+=1))
[[ -d "$root/src/lib" ]] && ((library_score+=1))
[[ -f "$root/index.ts" ]] || [[ -f "$root/index.js" ]] && ((library_score+=1))
grep -q '"main"' "$root/package.json" 2>/dev/null && ((library_score+=1))
grep -q '"exports"' "$root/package.json" 2>/dev/null && ((library_score+=1))

# CLI indicators
cli_score=0
[[ -d "$root/bin" ]] && ((cli_score+=2))
[[ -d "$root/cmd" ]] && ((cli_score+=2))
grep -q '"bin"' "$root/package.json" 2>/dev/null && ((cli_score+=2))
has_file "cli.*" && ((cli_score+=1))

echo "### Scores (higher = more likely)"
echo "- Frontend: $frontend_score"
echo "- Backend: $backend_score"
echo "- Library: $library_score"
echo "- CLI: $cli_score"
echo ""

# Determine primary type
if [[ $frontend_score -ge 3 ]] && [[ $backend_score -ge 3 ]]; then
  echo "### Detected: Fullstack Application"
elif [[ $frontend_score -ge 3 ]]; then
  echo "### Detected: Frontend Application"
elif [[ $backend_score -ge 3 ]]; then
  echo "### Detected: Backend Application"
elif [[ $library_score -ge 3 ]]; then
  echo "### Detected: Library/Package"
elif [[ $cli_score -ge 2 ]]; then
  echo "### Detected: CLI Tool"
else
  echo "### Detected: Unknown (manual inspection needed)"
fi
echo ""

# Key directories
echo "## Directory Structure"
echo ""
echo "### Top-level directories"
find "$root" -maxdepth 1 -type d ! -name '.*' ! -name 'node_modules' ! -name '__pycache__' ! -name '.git' | sort | sed "s|^$root/||" | grep -v '^$' | head -20
echo ""

# Entry points
echo "## Entry Points"
echo ""
echo "### Potential entry files"
for f in "index.ts" "index.js" "main.ts" "main.js" "app.ts" "app.js" "server.ts" "server.js" "main.py" "app.py" "manage.py" "main.go" "cmd/main.go"; do
  [[ -f "$root/$f" ]] && echo "- $f"
done
[[ -f "$root/src/index.ts" ]] && echo "- src/index.ts"
[[ -f "$root/src/index.js" ]] && echo "- src/index.js"
[[ -f "$root/src/main.ts" ]] && echo "- src/main.ts"
[[ -f "$root/src/main.js" ]] && echo "- src/main.js"
echo ""

# Config files
echo "## Configuration Files"
echo ""
for cfg in "tsconfig.json" "jsconfig.json" "vite.config.*" "webpack.config.*" "next.config.*" "nuxt.config.*" "tailwind.config.*" ".eslintrc*" ".prettierrc*" "docker-compose.yml" "Dockerfile" ".env.example" ".env.sample"; do
  matches=$(compgen -G "$root/$cfg" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    echo "$matches" | sed "s|^$root/|- |"
  fi
done
echo ""

# Testing setup
echo "## Testing Setup"
echo ""
[[ -d "$root/__tests__" ]] && echo "- __tests__/ directory found"
[[ -d "$root/test" ]] && echo "- test/ directory found"
[[ -d "$root/tests" ]] && echo "- tests/ directory found"
[[ -d "$root/spec" ]] && echo "- spec/ directory found"
has_file "*.test.ts" && echo "- TypeScript test files found: $(count_files '*.test.ts')"
has_file "*.test.js" && echo "- JavaScript test files found: $(count_files '*.test.js')"
has_file "*.spec.ts" && echo "- TypeScript spec files found: $(count_files '*.spec.ts')"
has_file "*_test.go" && echo "- Go test files found: $(count_files '*_test.go')"
has_file "test_*.py" && echo "- Python test files found: $(count_files 'test_*.py')"
[[ -f "$root/jest.config.js" ]] || [[ -f "$root/jest.config.ts" ]] && echo "- Jest configured"
[[ -f "$root/vitest.config.ts" ]] && echo "- Vitest configured"
[[ -f "$root/pytest.ini" ]] || [[ -f "$root/pyproject.toml" ]] && grep -q 'pytest' "$root/pyproject.toml" 2>/dev/null && echo "- Pytest configured"
echo ""

echo "## Next Steps"
echo ""
echo "1. Run inventory_elements.sh to catalog all documentable elements"
echo "2. Review the key entry points and configuration files"
echo "3. Identify the main modules/packages for deep extraction"
