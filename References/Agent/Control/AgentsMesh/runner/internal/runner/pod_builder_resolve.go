package runner

import (
	"context"
	"fmt"
	"os"
	"strings"

	"go.opentelemetry.io/otel/trace"

	"github.com/anthropics/agentsmesh/runner/internal/envfilter"
)

func resolvePathPlaceholders(s, sandboxRoot, workDir string) string {
	s = strings.ReplaceAll(s, "{{sandbox_root}}", sandboxRoot)
	s = strings.ReplaceAll(s, "{{work_dir}}", workDir)
	s = strings.ReplaceAll(s, "{{.sandbox.root_path}}", sandboxRoot)
	s = strings.ReplaceAll(s, "{{.sandbox.work_dir}}", workDir)
	return s
}

func resolveStringSlice(ss []string, sandboxRoot, workDir string) []string {
	result := make([]string, len(ss))
	for i, s := range ss {
		result[i] = resolvePathPlaceholders(s, sandboxRoot, workDir)
	}
	return result
}

func (b *PodBuilder) resolvePath(pathTemplate, sandboxRoot, workDir string) string {
	return resolvePathPlaceholders(pathTemplate, sandboxRoot, workDir)
}

func mapToEnvSlice(m map[string]string) []string {
	s := make([]string, 0, len(m))
	for k, v := range m {
		s = append(s, k+"="+v)
	}
	return s
}

func buildMergedEnv(userEnv map[string]string) []string {
	envMap := make(map[string]string)
	for _, e := range envfilter.FilterEnv(os.Environ()) {
		if idx := strings.Index(e, "="); idx >= 0 {
			envMap[e[:idx]] = e[idx+1:]
		}
	}
	delete(envMap, "CLAUDECODE")
	envMap["TERM"] = "xterm-256color"
	envMap["COLORTERM"] = "truecolor"
	for k, v := range userEnv {
		envMap[k] = v
	}
	return mapToEnvSlice(envMap)
}

func injectTraceparent(ctx context.Context, envVars map[string]string) {
	span := trace.SpanFromContext(ctx)
	sc := span.SpanContext()
	if !sc.IsValid() {
		return
	}
	flags := byte(0x00)
	if sc.IsSampled() {
		flags = 0x01
	}
	envVars["TRACEPARENT"] = fmt.Sprintf("00-%s-%s-%02x",
		sc.TraceID().String(), sc.SpanID().String(), flags)
}
