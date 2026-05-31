package protoconv

// StringPtr returns nil when p is nil, otherwise an unaliased *string copy.
// The deep copy keeps the proto and domain pointers independent so a later
// in-place mutation on the caller's side can't accidentally edit the wire
// value.
func StringPtr(p *string) *string {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}

// Int32Ptr is the *int32 deep-copy analogue of StringPtr.
func Int32Ptr(p *int32) *int32 {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}

// Int64Ptr is the *int64 deep-copy analogue of StringPtr.
func Int64Ptr(p *int64) *int64 {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}

// BoolPtr is the *bool deep-copy analogue of StringPtr.
func BoolPtr(p *bool) *bool {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}

// IntToInt32 narrows an arch-sized `int` (Go default integer; backend
// domain models use it for counts/limits) to `int32` (proto wire). Overflow
// silently truncates — same behaviour as the hand-written `int32(x)` casts
// every convert.go uses today, kept intentionally so the codegen output
// stays bit-for-bit identical to the hand-written version it replaces.
func IntToInt32(v int) int32 { return int32(v) }

// IntToInt64 widens int to int64. No-op on 64-bit platforms; needed for
// codegen symmetry with IntToInt32.
func IntToInt64(v int) int64 { return int64(v) }

// Int32ToInt is the inverse of IntToInt32 for FromProto.
func Int32ToInt(v int32) int { return int(v) }

// Int64ToInt is the inverse of IntToInt64 for FromProto.
func Int64ToInt(v int64) int { return int(v) }

// IntPtrToInt32Ptr narrows `*int` → `*int32`, preserving nil.
func IntPtrToInt32Ptr(p *int) *int32 {
	if p == nil {
		return nil
	}
	v := int32(*p)
	return &v
}

// IntPtrToInt64Ptr widens `*int` → `*int64`, preserving nil.
func IntPtrToInt64Ptr(p *int) *int64 {
	if p == nil {
		return nil
	}
	v := int64(*p)
	return &v
}

// Int32PtrToIntPtr is the inverse of IntPtrToInt32Ptr.
func Int32PtrToIntPtr(p *int32) *int {
	if p == nil {
		return nil
	}
	v := int(*p)
	return &v
}

// Int64PtrToIntPtr is the inverse of IntPtrToInt64Ptr.
func Int64PtrToIntPtr(p *int64) *int {
	if p == nil {
		return nil
	}
	v := int(*p)
	return &v
}