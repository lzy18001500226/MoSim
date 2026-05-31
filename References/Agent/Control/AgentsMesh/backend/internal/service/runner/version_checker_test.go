package runner

import (
	"context"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// testLogger returns a no-op logger for tests
func testLogger() *slog.Logger {
	return slog.Default()
}

func TestNormalizeVersion(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"v1.2.3", "1.2.3"},
		{"1.2.3", "1.2.3"},
		{"v0.1.0-beta.1", "0.1.0-beta.1"},
		{"", ""},
		{"  v1.0.0  ", "1.0.0"},
	}

	for _, tt := range tests {
		t.Run(tt.input, func(t *testing.T) {
			assert.Equal(t, tt.expected, NormalizeVersion(tt.input))
		})
	}
}

func TestNewVersionChecker_DisabledWhenNilRedis(t *testing.T) {
	vc := NewVersionChecker(nil)
	assert.Nil(t, vc, "VersionChecker should be nil when redisClient is nil")
}

func TestVersionChecker_GetLatestVersion_NilChecker(t *testing.T) {
	var vc *VersionChecker
	assert.Equal(t, "", vc.GetLatestVersion(context.Background()))
}

func TestVersionChecker_GetLatestVersion_NilRedis(t *testing.T) {
	vc := &VersionChecker{
		redisClient: nil,
		logger:      testLogger(),
	}
	assert.Equal(t, "", vc.GetLatestVersion(context.Background()))
}

// newTestVersionChecker creates a VersionChecker pointing to a test HTTP server
func newTestVersionChecker(serverURL string) *VersionChecker {
	return &VersionChecker{
		httpClient: &http.Client{
			Transport: &rewriteTransport{
				base:    http.DefaultTransport,
				baseURL: serverURL,
			},
		},
		logger: testLogger(),
	}
}

func TestVersionChecker_CheckGitHubRelease_Success(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/repos/AgentsMesh/AgentsMesh/releases/latest", r.URL.Path)
		assert.Equal(t, "application/vnd.github+json", r.Header.Get("Accept"))

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"tag_name": "v1.5.0", "draft": false}`))
	}))
	defer server.Close()

	vc := newTestVersionChecker(server.URL)

	version, err := vc.checkGitHubRelease(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "1.5.0", version)
}

func TestVersionChecker_CheckGitHubRelease_APIError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusForbidden)
	}))
	defer server.Close()

	vc := newTestVersionChecker(server.URL)

	_, err := vc.checkGitHubRelease(context.Background())
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "403")
}

func TestVersionChecker_CheckGitHubRelease_InvalidJSON(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`not json`))
	}))
	defer server.Close()

	vc := newTestVersionChecker(server.URL)

	_, err := vc.checkGitHubRelease(context.Background())
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "decode")
}

func TestVersionChecker_CheckGitHubRelease_EmptyTag(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"tag_name": "", "draft": false}`))
	}))
	defer server.Close()

	vc := newTestVersionChecker(server.URL)

	_, err := vc.checkGitHubRelease(context.Background())
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "empty version")
}

// rewriteTransport rewrites all requests to point to a test server URL
type rewriteTransport struct {
	base    http.RoundTripper
	baseURL string
}

func (t *rewriteTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	// Rewrite the URL to point to the test server, preserving the path
	req.URL.Scheme = "http"
	req.URL.Host = t.baseURL[len("http://"):]
	return t.base.RoundTrip(req)
}
