package protoconv

import "github.com/lib/pq"

// Slice maps items through fn, preserving order and capacity. Returns a
// non-nil empty slice when items is empty so the wire shape is a `[]` rather
// than absent — matches the conventions §6 zero-value emission rule.
func Slice[T any, U any](items []T, fn func(T) U) []U {
	out := make([]U, 0, len(items))
	for _, item := range items {
		out = append(out, fn(item))
	}
	return out
}

// StringSlice converts a pq.StringArray (postgres text[] gorm column type)
// into a plain []string wire shape. pq.StringArray is defined as
// `type StringArray []string` so the conversion is a zero-cost type cast;
// the helper exists so codegen can emit a single fully-qualified function
// reference rather than threading a `pq.` import into every generated file.
func StringSlice(s pq.StringArray) []string {
	if s == nil {
		return nil
	}
	return []string(s)
}

// StringArray is StringSlice's inverse — promotes a wire []string into the
// pq.StringArray gorm column type. Used by FromProto generators.
func StringArray(s []string) pq.StringArray {
	if s == nil {
		return nil
	}
	return pq.StringArray(s)
}
