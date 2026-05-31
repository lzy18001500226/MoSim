// Package protoconv hosts the shared domain → proto conversion helpers used
// across `backend/internal/api/connect/<domain>/convert.go` files.
//
// Scope: stateless, schema-agnostic primitives only — RFC3339 time formatting
// (UTC, second precision), nullable pointer deep-copy, and a generic slice
// mapper. Anything domain-specific (multi-field projection, derived flags,
// enrichment loading) stays in the per-domain convert.go.
//
// Precision exception: `blockstore/convert.go` formats timestamps with
// `time.RFC3339Nano` for the audit log shape it inherited from REST; it owns
// its own helper instead of calling RFC3339 here.
package protoconv
