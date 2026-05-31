package agentpod

func firstNonEmpty(vals ...string) string {
	for _, v := range vals {
		if v != "" {
			return v
		}
	}
	return ""
}

func firstNonEmptyPtr(resolved string, input *string) *string {
	if resolved != "" {
		return &resolved
	}
	return input
}

func firstNonNilInt64(resolved *int64, input *int64) *int64 {
	if resolved != nil {
		return resolved
	}
	return input
}
