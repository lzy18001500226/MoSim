#!/usr/bin/env bash
# Block Store Phase 1 smoke test.
# Requires the deploy/dev stack to be running (see deploy/dev/dev.sh) and
# the dev test user "dev@agentsmesh.local / devpass123" to exist.
#
# Exits 0 on success, non-zero on any HTTP error.

set -euo pipefail

API="${API:-http://localhost:80}"
EMAIL="${EMAIL:-dev@agentsmesh.local}"
PASSWORD="${PASSWORD:-devpass123}"
ORG_SLUG="${ORG_SLUG:-dev-org}"

log() { printf '\033[36m[smoke]\033[0m %s\n' "$*"; }
die() { printf '\033[31m[smoke]\033[0m %s\n' "$*" >&2; exit 1; }

jq_required() {
  command -v jq >/dev/null || die "jq is required for this smoke test"
}
jq_required

log "1. Logging in as $EMAIL..."
TOKEN=$(
  curl -sS -X POST "$API/api/v1/auth/login" \
    -H 'content-type: application/json' \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
    | jq -er '.token'
)

authed() {
  curl -sS -H "authorization: Bearer $TOKEN" "$@"
}

log "2. Ensuring default workspace..."
WS=$(
  authed -X POST "$API/api/v1/orgs/$ORG_SLUG/blocks/workspaces/default"
)
WS_ID=$(echo "$WS" | jq -er '.id')
ROOT_ID=$(echo "$WS" | jq -er '.root_block_id')
log "   workspace=$WS_ID  root=$ROOT_ID"

IDEMPOTENCY_KEY="smoke-$(date +%s)-$$"
NEW_BLOCK_ID=$(uuidgen | tr A-Z a-z)
log "3. Creating a task block ($NEW_BLOCK_ID) under root..."
authed -X POST "$API/api/v1/orgs/$ORG_SLUG/blocks/ops" \
  -H 'content-type: application/json' \
  -d "{
    \"workspace_id\": \"$WS_ID\",
    \"idempotency_key\": \"$IDEMPOTENCY_KEY\",
    \"ops\": [
      {\"op\":\"createBlock\",\"payload\":{\"id\":\"$NEW_BLOCK_ID\",\"type\":\"task\",\"data\":{\"title\":\"Smoke-test task\",\"status\":\"todo\"}}},
      {\"op\":\"addRef\",\"payload\":{\"from\":\"$ROOT_ID\",\"to\":\"$NEW_BLOCK_ID\",\"rel\":\"nest\",\"order_key\":\"a0\"}}
    ]
  }" | jq -e '.op_ids | length == 2' >/dev/null \
  || die "ApplyOps returned unexpected shape"

log "4. Idempotency replay (same key)..."
REPLAY=$(
  authed -X POST "$API/api/v1/orgs/$ORG_SLUG/blocks/ops" \
    -H 'content-type: application/json' \
    -d "{
      \"workspace_id\": \"$WS_ID\",
      \"idempotency_key\": \"$IDEMPOTENCY_KEY\",
      \"ops\": [
        {\"op\":\"createBlock\",\"payload\":{\"type\":\"task\",\"data\":{\"title\":\"noop\"}}}
      ]
    }"
)
echo "$REPLAY" | jq -e '.was_replay == true' >/dev/null \
  || die "Replay did not short-circuit via idempotency key"

log "5. Fetching subtree..."
authed "$API/api/v1/orgs/$ORG_SLUG/blocks/workspaces/$WS_ID/subtree?root=$ROOT_ID" \
  | jq -e ".blocks | map(select(.id == \"$NEW_BLOCK_ID\")) | length == 1" >/dev/null \
  || die "New block missing from subtree"

log "PASS — Block Store Phase 1 is alive."
