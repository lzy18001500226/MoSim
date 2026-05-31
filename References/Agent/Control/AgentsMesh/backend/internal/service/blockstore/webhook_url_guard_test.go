package blockstoreservice

import (
	"testing"
)

func TestValidateWebhookURL_BlocksSSRF(t *testing.T) {
	// Make sure the allowlist is off for these assertions — otherwise a stray
	// env var from the developer shell would make the tests pass for the
	// wrong reason.
	t.Setenv(allowedHostsEnv, "")

	cases := []struct {
		name    string
		url     string
		wantErr bool
	}{
		// Public IP literals skip DNS — deterministic in sandboxed test envs.
		{"https external IP ok", "https://8.8.8.8/hook", false},
		{"http external IP ok", "http://1.1.1.1/hook", false},
		{"file scheme rejected", "file:///etc/passwd", true},
		{"javascript scheme rejected", "javascript:alert(1)", true},
		{"localhost alias rejected", "http://localhost:5432", true},
		{"loopback ipv4 rejected", "http://127.0.0.1/admin", true},
		{"loopback ipv6 rejected", "http://[::1]/admin", true},
		{"rfc1918 10/8 rejected", "http://10.0.0.5/hook", true},
		{"rfc1918 172.16/12 rejected", "http://172.20.0.1/hook", true},
		{"rfc1918 192.168 rejected", "http://192.168.1.1/hook", true},
		{"aws metadata rejected", "http://169.254.169.254/latest/meta-data/", true},
		{"cgnat rejected", "http://100.64.1.1/hook", true},
		{"unspecified rejected", "http://0.0.0.0/hook", true},
		{"missing host rejected", "http:///hook", true},
		{"garbage rejected", "not-a-url-at-all", true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			err := ValidateWebhookURL(tc.url)
			gotErr := err != nil
			if gotErr != tc.wantErr {
				t.Fatalf("ValidateWebhookURL(%q) err=%v wantErr=%v", tc.url, err, tc.wantErr)
			}
		})
	}
}

func TestValidateWebhookURL_AllowlistBypass(t *testing.T) {
	// With the allowlist set, a private IP alias should still pass so dev/CI
	// (Docker host bridge) can reach a listener on the host.
	t.Setenv(allowedHostsEnv, "host.docker.internal,host.lan")

	if err := ValidateWebhookURL("http://host.docker.internal:12345/hook"); err != nil {
		t.Fatalf("allowlisted host should pass: %v", err)
	}
	// A host NOT in the allowlist must still be rejected.
	if err := ValidateWebhookURL("http://127.0.0.1/admin"); err == nil {
		t.Fatal("non-allowlisted loopback should still be rejected")
	}
}

// R1 sink: applyCreateBlock / applyUpdateBlock now call validateTriggerDefData
// directly. These tests verify the helper alone (behavior in the full ApplyOps
// flow is covered by e2e security-guards.spec.ts).
func TestValidateTriggerDefData(t *testing.T) {
	t.Setenv(allowedHostsEnv, "")

	cases := []struct {
		name    string
		data    map[string]any
		wantErr bool
	}{
		{"no action key → pass-through", map[string]any{"name": "t"}, false},
		{"agent action → bypass URL check", map[string]any{"action": map[string]any{"kind": "agent", "agent_slug": "x"}}, false},
		{"webhook with empty URL → pass", map[string]any{"action": map[string]any{"kind": "webhook"}}, false},
		{"webhook with public URL → pass", map[string]any{"action": map[string]any{"kind": "webhook", "url": "https://8.8.8.8/hook"}}, false},
		{"webhook with loopback → reject", map[string]any{"action": map[string]any{"kind": "webhook", "url": "http://127.0.0.1/admin"}}, true},
		{"webhook with rfc1918 → reject", map[string]any{"action": map[string]any{"kind": "webhook", "url": "http://10.0.0.1/x"}}, true},
		{"webhook with aws metadata → reject", map[string]any{"action": map[string]any{"kind": "webhook", "url": "http://169.254.169.254/"}}, true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			err := validateTriggerDefData(tc.data)
			gotErr := err != nil
			if gotErr != tc.wantErr {
				t.Fatalf("validateTriggerDefData(%v) err=%v wantErr=%v", tc.data, err, tc.wantErr)
			}
		})
	}
}
