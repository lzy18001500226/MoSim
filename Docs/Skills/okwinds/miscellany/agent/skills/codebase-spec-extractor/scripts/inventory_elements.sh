#!/usr/bin/env bash
set -euo pipefail

# inventory_elements.sh - Generate a complete inventory of documentable elements
# Usage: inventory_elements.sh <project_root> [output_file]

usage() {
  cat <<'EOF'
Usage:
  inventory_elements.sh <project_root> [output_file]

Generates an inventory of all documentable elements in a project:
  - API endpoints (routes, controllers, handlers)
  - Data models (entities, schemas, migrations)
  - Business logic (services, use cases, domain modules)
  - UI components (if frontend exists)
  - Configuration (env vars, config files)
  - Integrations (external API clients, adapters)
  - Background jobs (workers, cron, queues)

Output is a structured markdown file for review before extraction.
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

if [[ -n "$output" ]]; then
  mkdir -p "$(dirname "$output")"
  exec > "$output"
fi

echo "# Element Inventory"
echo "root: $root"
echo "generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Default ignores
ignores=(
  "node_modules"
  ".git"
  "__pycache__"
  ".next"
  ".nuxt"
  "dist"
  "build"
  "coverage"
  ".cache"
  "vendor"
  ".venv"
  "venv"
  "env"
)

ignore_pattern=""
for ig in "${ignores[@]}"; do
  ignore_pattern="$ignore_pattern -not -path '*/$ig/*'"
done

# Helper: find files with pattern, excluding ignored dirs
find_files() {
  local pattern="$1"
  eval "find \"$root\" -type f -name '$pattern' $ignore_pattern 2>/dev/null" | sed "s|^$root/||" | sort
}

# Helper: find directories with name
find_dirs() {
  local name="$1"
  eval "find \"$root\" -type d -name '$name' $ignore_pattern 2>/dev/null" | sed "s|^$root/||" | sort
}

# Helper: search for pattern in files
search_pattern() {
  local pattern="$1"
  local globs="$2"
  if command -v rg &>/dev/null; then
    rg -l --no-messages "$pattern" --glob "$globs" "$root" 2>/dev/null | sed "s|^$root/||" | sort || true
  else
    grep -rl "$pattern" --include="$globs" "$root" 2>/dev/null | sed "s|^$root/||" | sort || true
  fi
}

echo "## 1. API Layer"
echo ""

echo "### Route Definitions"
echo "Files likely containing route/endpoint definitions:"
echo ""

# Express/Node routes
for f in $(find_files "routes.ts" && find_files "routes.js" && find_files "router.ts" && find_files "router.js"); do
  echo "- $f"
done

# Look for route patterns
route_files=$(search_pattern "(app\.(get|post|put|delete|patch)|router\.(get|post|put|delete|patch)|@(Get|Post|Put|Delete|Patch))" "*.ts")
if [[ -n "$route_files" ]]; then
  echo ""
  echo "Files with route decorators/methods:"
  echo "$route_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "### Controllers"
controller_dirs=$(find_dirs "controllers")
if [[ -n "$controller_dirs" ]]; then
  echo "Controller directories:"
  echo "$controller_dirs" | while read -r d; do
    echo "- $d/"
    find "$root/$d" -type f -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" 2>/dev/null | sed "s|^$root/|  - |" | head -20
  done
fi

controller_files=$(find_files "*Controller.ts" && find_files "*_controller.py" && find_files "*controller.go")
if [[ -n "$controller_files" ]]; then
  echo ""
  echo "Controller files:"
  echo "$controller_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "### Middleware"
middleware_files=$(find_files "*middleware*.ts" && find_files "*middleware*.js" && find_files "*middleware*.py")
if [[ -n "$middleware_files" ]]; then
  echo "Middleware files:"
  echo "$middleware_files" | while read -r f; do echo "- $f"; done
else
  echo "(no middleware files found by pattern)"
fi
echo ""

echo "## 2. Data Layer"
echo ""

echo "### Models/Entities"
model_dirs=$(find_dirs "models" && find_dirs "entities")
if [[ -n "$model_dirs" ]]; then
  echo "Model directories:"
  echo "$model_dirs" | while read -r d; do
    echo "- $d/"
    find "$root/$d" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" \) 2>/dev/null | sed "s|^$root/|  - |" | head -30
  done
fi

# Prisma
if [[ -f "$root/prisma/schema.prisma" ]]; then
  echo ""
  echo "Prisma schema: prisma/schema.prisma"
fi

# TypeORM entities
typeorm_entities=$(search_pattern "@Entity" "*.ts")
if [[ -n "$typeorm_entities" ]]; then
  echo ""
  echo "TypeORM entities:"
  echo "$typeorm_entities" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "### Migrations"
migration_dirs=$(find_dirs "migrations" && find_dirs "migrate")
if [[ -n "$migration_dirs" ]]; then
  echo "Migration directories:"
  echo "$migration_dirs" | while read -r d; do
    echo "- $d/"
    find "$root/$d" -type f 2>/dev/null | sed "s|^$root/|  - |" | head -20
  done
fi

sql_files=$(find_files "*.sql")
if [[ -n "$sql_files" ]]; then
  echo ""
  echo "SQL files:"
  echo "$sql_files" | while read -r f; do echo "- $f"; done | head -20
fi
echo ""

echo "### Schemas/DTOs"
schema_files=$(find_files "*schema*.ts" && find_files "*dto*.ts" && find_files "*Schema.ts" && find_files "*DTO.ts")
if [[ -n "$schema_files" ]]; then
  echo "Schema/DTO files:"
  echo "$schema_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "## 3. Business Logic"
echo ""

echo "### Services"
service_dirs=$(find_dirs "services" && find_dirs "service")
if [[ -n "$service_dirs" ]]; then
  echo "Service directories:"
  echo "$service_dirs" | while read -r d; do
    echo "- $d/"
    find "$root/$d" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" -o -name "*.go" \) 2>/dev/null | sed "s|^$root/|  - |" | head -30
  done
fi

service_files=$(find_files "*Service.ts" && find_files "*_service.py" && find_files "*service.go")
if [[ -n "$service_files" ]]; then
  echo ""
  echo "Service files:"
  echo "$service_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "### Use Cases / Domain"
domain_dirs=$(find_dirs "domain" && find_dirs "usecases" && find_dirs "use-cases")
if [[ -n "$domain_dirs" ]]; then
  echo "Domain/Use Case directories:"
  echo "$domain_dirs" | while read -r d; do
    echo "- $d/"
    find "$root/$d" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" \) 2>/dev/null | sed "s|^$root/|  - |" | head -20
  done
fi
echo ""

echo "### Utils/Helpers"
util_dirs=$(find_dirs "utils" && find_dirs "helpers" && find_dirs "lib")
if [[ -n "$util_dirs" ]]; then
  echo "Utility directories:"
  echo "$util_dirs" | while read -r d; do echo "- $d/"; done
fi
echo ""

echo "## 4. UI Layer (if applicable)"
echo ""

echo "### Components"
component_dirs=$(find_dirs "components" && find_dirs "ui")
if [[ -n "$component_dirs" ]]; then
  echo "Component directories:"
  echo "$component_dirs" | while read -r d; do
    echo "- $d/"
    # Count components
    count=$(find "$root/$d" -type f \( -name "*.tsx" -o -name "*.vue" -o -name "*.svelte" \) 2>/dev/null | wc -l | tr -d ' ')
    echo "  ($count component files)"
  done
fi
echo ""

echo "### Pages/Views"
page_dirs=$(find_dirs "pages" && find_dirs "views" && find_dirs "app")
if [[ -n "$page_dirs" ]]; then
  echo "Page directories:"
  echo "$page_dirs" | while read -r d; do
    echo "- $d/"
    find "$root/$d" -type f \( -name "*.tsx" -o -name "*.vue" -o -name "*.svelte" -o -name "page.tsx" -o -name "page.js" \) 2>/dev/null | sed "s|^$root/|  - |" | head -20
  done
fi
echo ""

echo "### State Management"
state_files=$(find_files "*store*.ts" && find_files "*slice*.ts" && find_files "*context*.tsx" && find_files "*atom*.ts")
if [[ -n "$state_files" ]]; then
  echo "State management files:"
  echo "$state_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "## 5. Integrations"
echo ""

echo "### External API Clients"
client_files=$(find_files "*client*.ts" && find_files "*api*.ts" && find_files "*adapter*.ts")
if [[ -n "$client_files" ]]; then
  echo "API client files:"
  echo "$client_files" | while read -r f; do echo "- $f"; done | head -20
fi
echo ""

echo "### Queue/Worker"
worker_files=$(find_files "*worker*.ts" && find_files "*job*.ts" && find_files "*queue*.ts" && find_files "*consumer*.ts")
if [[ -n "$worker_files" ]]; then
  echo "Worker/Queue files:"
  echo "$worker_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "## 6. Configuration"
echo ""

echo "### Environment Variables"
env_files=$(find_files ".env*" && find_files "*.env")
if [[ -n "$env_files" ]]; then
  echo "Environment files:"
  echo "$env_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "### Config Files"
config_files=$(find_files "config*.ts" && find_files "config*.js" && find_files "settings*.py" && find_files "*.config.ts" && find_files "*.config.js")
if [[ -n "$config_files" ]]; then
  echo "Config files:"
  echo "$config_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "## 7. Testing"
echo ""

test_files=$(find_files "*.test.ts" && find_files "*.spec.ts" && find_files "*_test.go" && find_files "test_*.py")
test_count=$(echo "$test_files" | grep -c '^' || echo 0)
echo "Test files found: $test_count"
if [[ $test_count -gt 0 ]] && [[ $test_count -le 30 ]]; then
  echo "$test_files" | while read -r f; do echo "- $f"; done
elif [[ $test_count -gt 30 ]]; then
  echo "(showing first 30)"
  echo "$test_files" | head -30 | while read -r f; do echo "- $f"; done
fi
echo ""

echo "## 8. Infrastructure"
echo ""

echo "### Docker"
docker_files=$(find_files "Dockerfile*" && find_files "docker-compose*.yml" && find_files "docker-compose*.yaml")
if [[ -n "$docker_files" ]]; then
  echo "Docker files:"
  echo "$docker_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "### CI/CD"
ci_dirs=$(find_dirs ".github" && find_dirs ".gitlab" && find_dirs ".circleci")
if [[ -n "$ci_dirs" ]]; then
  echo "CI/CD directories:"
  echo "$ci_dirs" | while read -r d; do echo "- $d/"; done
fi
ci_files=$(find_files "*.yml" | grep -E "(github|gitlab|jenkins|circle)" || true)
if [[ -n "$ci_files" ]]; then
  echo "CI/CD files:"
  echo "$ci_files" | while read -r f; do echo "- $f"; done
fi
echo ""

echo "## Summary"
echo ""
echo "This inventory provides a starting point for specification extraction."
echo "Review each category and identify which elements require detailed documentation."
echo ""
echo "Priority order recommendation:"
echo "1. Data models (foundation for understanding the domain)"
echo "2. API endpoints (external interface contract)"
echo "3. Business logic services (core behavior)"
echo "4. UI components (if applicable)"
echo "5. Integrations (external dependencies)"
echo "6. Infrastructure (deployment requirements)"
