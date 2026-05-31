package protoconv

import "time"

// RFC3339 formats t as UTC RFC 3339 (second precision). The UTC normalisation
// matches the wire convention every connect convert.go followed before this
// helper existed; admin/convert.go's pre-existing non-UTC variants are
// converged onto this default to make the wire shape consistent.
func RFC3339(t time.Time) string {
	return t.UTC().Format(time.RFC3339)
}

// RFC3339Ptr returns nil when t is nil, otherwise an unaliased *string
// containing RFC3339(*t). Mirrors the
// `if t != nil { s := t.UTC().Format(...); out.X = &s }` pattern.
func RFC3339Ptr(t *time.Time) *string {
	if t == nil {
		return nil
	}
	s := RFC3339(*t)
	return &s
}

// RFC3339Nano formats t as UTC RFC 3339 with nanosecond precision. Used by
// blockstore-style domains where audit-grade timestamp precision must round
// trip; the Nano format is wire-compatible with RFC3339 parsers.
func RFC3339Nano(t time.Time) string {
	return t.UTC().Format(time.RFC3339Nano)
}

// RFC3339NanoPtr is RFC3339Ptr's Nano-precision variant.
func RFC3339NanoPtr(t *time.Time) *string {
	if t == nil {
		return nil
	}
	s := RFC3339Nano(*t)
	return &s
}

// ParseRFC3339 inverts RFC3339 — parses an RFC3339 (or Nano) string into
// time.Time. On parse failure returns the zero time without panicking; the
// caller is responsible for validating non-zero inputs upstream. This is the
// convention every existing convert.go followed (errors at the parse boundary
// were swallowed and only caught at the use site).
func ParseRFC3339(s string) time.Time {
	if s == "" {
		return time.Time{}
	}
	t, err := time.Parse(time.RFC3339Nano, s)
	if err != nil {
		t, _ = time.Parse(time.RFC3339, s)
	}
	return t
}

// ParseRFC3339Ptr returns nil when p is nil/empty, otherwise an unaliased
// *time.Time containing ParseRFC3339(*p).
func ParseRFC3339Ptr(p *string) *time.Time {
	if p == nil || *p == "" {
		return nil
	}
	t := ParseRFC3339(*p)
	return &t
}

// ParseRFC3339Nano is ParseRFC3339's Nano-precision variant. Behaviour is
// identical (time.Parse already accepts both RFC3339 and RFC3339Nano), the
// alias exists so codegen tags can distinguish the source precision.
func ParseRFC3339Nano(s string) time.Time { return ParseRFC3339(s) }

// ParseRFC3339NanoPtr mirrors ParseRFC3339Ptr for the Nano tag.
func ParseRFC3339NanoPtr(p *string) *time.Time { return ParseRFC3339Ptr(p) }
