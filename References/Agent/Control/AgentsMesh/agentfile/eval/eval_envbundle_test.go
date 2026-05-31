package eval

import (
	"testing"

	"github.com/anthropics/agentsmesh/agentfile/parser"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// USE_ENV_BUNDLE merges named bundles into Result.EnvVars in declaration order.
// Later USE_ENV_BUNDLE declarations override earlier ones on key conflicts.
func TestEval_UseEnvBundle_BasicMerge(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT claude
USE_ENV_BUNDLE "work-creds"
USE_ENV_BUNDLE "org-defaults"
`)
	require.Empty(t, errs)

	ctx := NewContext(nil)
	ctx.EnvBundles = map[string]map[string]string{
		"work-creds": {
			"ANTHROPIC_API_KEY":  "sk-work",
			"ANTHROPIC_BASE_URL": "https://work.api",
		},
		"org-defaults": {
			"ANTHROPIC_BASE_URL": "https://org.api", // overrides work-creds
			"LOG_LEVEL":          "debug",
		},
	}
	require.NoError(t, Eval(prog, ctx))

	assert.Equal(t, "sk-work", ctx.Result.EnvVars["ANTHROPIC_API_KEY"])
	// Later USE_ENV_BUNDLE wins on conflict.
	assert.Equal(t, "https://org.api", ctx.Result.EnvVars["ANTHROPIC_BASE_URL"])
	assert.Equal(t, "debug", ctx.Result.EnvVars["LOG_LEVEL"])
}

// Missing bundles don't fail eval and don't mutate EnvVars — matches the MCP
// "load-everything-tolerantly" pattern.
func TestEval_UseEnvBundle_MissingBundleSilent(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT claude
USE_ENV_BUNDLE "deleted-bundle"
`)
	require.Empty(t, errs)

	ctx := NewContext(nil)
	ctx.EnvBundles = map[string]map[string]string{}
	require.NoError(t, Eval(prog, ctx))

	assert.Empty(t, ctx.Result.EnvVars)
}

// USE_ENV_BUNDLE is round-trip-safe through merge + serialize.
func TestEval_UseEnvBundle_Roundtrip(t *testing.T) {
	src := `
AGENT claude
USE_ENV_BUNDLE "work-creds"
`
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)
	require.NotNil(t, prog)
	require.Len(t, prog.Declarations, 2) // AgentDecl + UseEnvBundleDecl

	bundleDecl, ok := prog.Declarations[1].(*parser.UseEnvBundleDecl)
	require.True(t, ok)
	assert.Equal(t, "work-creds", bundleDecl.Name)
}

// Three-bundle cascading override: last wins on every key conflict, even
// when an earlier bundle already shadowed a still-earlier one. The Pod
// create dialog emits an ordered list of names, so this is the property
// users actually depend on when they stack bundles.
func TestEval_UseEnvBundle_CascadingOverride(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT claude
USE_ENV_BUNDLE "base"
USE_ENV_BUNDLE "overlay-1"
USE_ENV_BUNDLE "overlay-2"
`)
	require.Empty(t, errs)

	ctx := NewContext(nil)
	ctx.EnvBundles = map[string]map[string]string{
		"base": {
			"ANTHROPIC_API_KEY":  "sk-base",
			"ANTHROPIC_BASE_URL": "https://base.api",
			"LOG_LEVEL":          "info",
		},
		"overlay-1": {
			// overlay-1 overrides base on BASE_URL and adds PROXY.
			"ANTHROPIC_BASE_URL": "https://overlay1.api",
			"HTTPS_PROXY":        "http://proxy1:8080",
		},
		"overlay-2": {
			// overlay-2 overrides overlay-1 (already-overridden) on BASE_URL,
			// overrides base on LOG_LEVEL (skipped by overlay-1), adds a new
			// key, and overrides overlay-1's own additions on PROXY.
			"ANTHROPIC_BASE_URL": "https://overlay2.api",
			"LOG_LEVEL":          "debug",
			"HTTPS_PROXY":        "http://proxy2:8080",
			"FEATURE_FLAG":       "enabled",
		},
	}
	require.NoError(t, Eval(prog, ctx))

	// API key only present in base — survives untouched.
	assert.Equal(t, "sk-base", ctx.Result.EnvVars["ANTHROPIC_API_KEY"])
	// BASE_URL overridden twice — overlay-2 wins.
	assert.Equal(t, "https://overlay2.api", ctx.Result.EnvVars["ANTHROPIC_BASE_URL"])
	// LOG_LEVEL skipped by overlay-1, then overridden by overlay-2.
	assert.Equal(t, "debug", ctx.Result.EnvVars["LOG_LEVEL"])
	// PROXY set by overlay-1, replaced by overlay-2.
	assert.Equal(t, "http://proxy2:8080", ctx.Result.EnvVars["HTTPS_PROXY"])
	// New key from overlay-2 propagates.
	assert.Equal(t, "enabled", ctx.Result.EnvVars["FEATURE_FLAG"])
	assert.Len(t, ctx.Result.EnvVars, 5)
}

// A missing bundle interleaved between resolvable bundles is a no-op —
// later bundles still win on the keys earlier ones set. This guards
// against accidental "abort on missing" regressions when users rename a
// middle bundle.
func TestEval_UseEnvBundle_MissingInMiddleDoesNotBreakChain(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT claude
USE_ENV_BUNDLE "base"
USE_ENV_BUNDLE "deleted-bundle"
USE_ENV_BUNDLE "overlay"
`)
	require.Empty(t, errs)

	ctx := NewContext(nil)
	ctx.EnvBundles = map[string]map[string]string{
		"base":    {"KEY": "base"},
		"overlay": {"KEY": "overlay"},
	}
	require.NoError(t, Eval(prog, ctx))

	// overlay still wins despite the missing bundle in between.
	assert.Equal(t, "overlay", ctx.Result.EnvVars["KEY"])
}
