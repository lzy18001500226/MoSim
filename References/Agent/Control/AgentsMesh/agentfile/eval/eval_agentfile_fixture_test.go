package eval

// Test fixtures for AgentFile eval tests.
// Provides eval context factories and AgentFile source manipulation utilities.

func newMCPContext() *Context {
	return NewContext(map[string]interface{}{
		"config": make(map[string]interface{}),
		"mcp": map[string]interface{}{
			"enabled": true,
			"builtin": map[string]interface{}{
				"agentsmesh": map[string]interface{}{
					"type": "http",
					"url":  "http://127.0.0.1:19000/mcp",
				},
			},
			"installed": map[string]interface{}{},
		},
		"sandbox": map[string]interface{}{
			"root":     "/tmp/sandbox",
			"work_dir": "/tmp/sandbox/workspace",
		},
	})
}

// replaceConfigDefault replaces the default value for a CONFIG declaration in source.
func replaceConfigDefault(src, configName, newDefault string) string {
	lines := splitLines(src)
	var result []string
	for _, line := range lines {
		trimmed := trimSpace(line)
		if hasPrefix(trimmed, "CONFIG "+configName+" ") {
			idx := lastIndex(line, "= ")
			if idx >= 0 {
				result = append(result, line[:idx+2]+newDefault)
				continue
			}
		}
		result = append(result, line)
	}
	return joinLines(result)
}

// replaceModeDecl replaces the active MODE declaration (without args).
func replaceModeDecl(src, newMode string) string {
	lines := splitLines(src)
	var result []string
	for _, line := range lines {
		trimmed := trimSpace(line)
		if hasPrefix(trimmed, "MODE ") && !containsStr(trimmed, `"`) {
			result = append(result, "MODE "+newMode)
			continue
		}
		result = append(result, line)
	}
	return joinLines(result)
}

// --- String helpers (avoid importing "strings" in test package) ---

func splitLines(s string) []string {
	var lines []string
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == '\n' {
			lines = append(lines, s[start:i])
			start = i + 1
		}
	}
	if start < len(s) {
		lines = append(lines, s[start:])
	}
	return lines
}

func joinLines(lines []string) string {
	result := ""
	for i, l := range lines {
		if i > 0 {
			result += "\n"
		}
		result += l
	}
	return result
}

func trimSpace(s string) string {
	i, j := 0, len(s)
	for i < j && (s[i] == ' ' || s[i] == '\t') {
		i++
	}
	for j > i && (s[j-1] == ' ' || s[j-1] == '\t') {
		j--
	}
	return s[i:j]
}

func hasPrefix(s, prefix string) bool {
	return len(s) >= len(prefix) && s[:len(prefix)] == prefix
}

func lastIndex(s, sub string) int {
	for i := len(s) - len(sub); i >= 0; i-- {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}

func containsStr(s, sub string) bool { return lastIndex(s, sub) >= 0 }
