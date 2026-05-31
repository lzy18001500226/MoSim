package blockstore

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// roundTripper captures the last request issued by the client so assertions
// can confirm Auth header and body shape without spinning a full backend.
type roundTripper struct {
	response func(req *http.Request) (*http.Response, error)
}

func (rt *roundTripper) RoundTrip(req *http.Request) (*http.Response, error) {
	return rt.response(req)
}

func newTestClient(handler func(req *http.Request) (*http.Response, error)) *Client {
	hc := &http.Client{Transport: &roundTripper{response: handler}}
	return NewClient(Config{
		BaseURL:    "http://blockstore.test",
		OrgSlug:    "acme",
		Token:      "test-token",
		HTTPClient: hc,
	})
}

func okJSON(body string) func(req *http.Request) (*http.Response, error) {
	return func(req *http.Request) (*http.Response, error) {
		return &http.Response{
			StatusCode: 200,
			Body:       io.NopCloser(strings.NewReader(body)),
			Header:     http.Header{},
		}, nil
	}
}

func TestClient_CreateBlock(t *testing.T) {
	var captured *http.Request
	var capturedBody string
	c := newTestClient(func(req *http.Request) (*http.Response, error) {
		captured = req
		raw, _ := io.ReadAll(req.Body)
		capturedBody = string(raw)
		return okJSON(`{"op_ids":[42],"was_replay":false}`)(req)
	})

	ref, err := c.CreateBlock(context.Background(), "ws-abc", "task",
		map[string]any{"title": "hi", "status": "todo"})
	require.NoError(t, err)
	assert.Equal(t, int64(42), ref.OpID)

	require.NotNil(t, captured)
	assert.Equal(t, "POST", captured.Method)
	assert.Equal(t, "/api/v1/orgs/acme/blocks/ops", captured.URL.Path)
	assert.Equal(t, "Bearer test-token", captured.Header.Get("Authorization"))

	var body map[string]any
	require.NoError(t, json.Unmarshal([]byte(capturedBody), &body))
	assert.Equal(t, "ws-abc", body["workspace_id"])
	ops := body["ops"].([]any)
	require.Len(t, ops, 1)
	op0 := ops[0].(map[string]any)
	assert.Equal(t, "createBlock", op0["op"])
	payload := op0["payload"].(map[string]any)
	assert.Equal(t, "task", payload["type"])
}

func TestClient_ApplyOps_ServerErrorBubblesUp(t *testing.T) {
	c := newTestClient(func(req *http.Request) (*http.Response, error) {
		return &http.Response{
			StatusCode: 409,
			Body:       io.NopCloser(strings.NewReader(`{"error":"stale"}`)),
			Header:     http.Header{},
		}, nil
	})
	_, err := c.ApplyOps(context.Background(), "ws", []OpEnvelope{
		{Op: "updateBlock", Payload: map[string]any{"id": "x"}},
	}, "")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "409")
	assert.Contains(t, err.Error(), "stale")
}

func TestClient_EnsureDefaultWorkspace(t *testing.T) {
	c := newTestClient(okJSON(`{"id":"ws-1","organization_id":7,"slug":"default","name":"Default","root_block_id":"root-1","created_at":"2026-04-17T10:00:00Z"}`))
	ws, err := c.EnsureDefaultWorkspace(context.Background())
	require.NoError(t, err)
	assert.Equal(t, "ws-1", ws.ID)
	require.NotNil(t, ws.RootBlockID)
	assert.Equal(t, "root-1", *ws.RootBlockID)
}

// httptest smoke — keeps the integration style close to what real callers hit.
func TestClient_AgainstLiveHTTPServer(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "Bearer live", r.Header.Get("Authorization"))
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"op_ids":[1,2],"was_replay":false}`))
	}))
	defer srv.Close()

	c := NewClient(Config{BaseURL: srv.URL, OrgSlug: "acme", Token: "live"})
	res, err := c.ApplyOps(context.Background(), "ws", []OpEnvelope{
		{Op: "createBlock", Payload: map[string]any{"type": "task"}},
	}, "idem-1")
	require.NoError(t, err)
	assert.Equal(t, []int64{1, 2}, res.OpIDs)
}

func TestClient_RetrieveMemory(t *testing.T) {
	var captured *http.Request
	var body string
	c := newTestClient(func(req *http.Request) (*http.Response, error) {
		captured = req
		raw, _ := io.ReadAll(req.Body)
		body = string(raw)
		return okJSON(`{"memories":[{"block_id":"b1","type":"task","snippet":"ship it","score":0.72}]}`)(req)
	})

	hits, err := c.RetrieveMemory(context.Background(), "ws-abc", "shipping plan", 5)
	require.NoError(t, err)
	require.Len(t, hits, 1)
	assert.Equal(t, "b1", hits[0].BlockID)
	assert.InDelta(t, 0.72, hits[0].Score, 1e-5)

	require.NotNil(t, captured)
	assert.Equal(t, "POST", captured.Method)
	assert.Equal(t, "/api/v1/orgs/acme/blocks/workspaces/ws-abc/memory/retrieve", captured.URL.Path)
	assert.Contains(t, body, `"query":"shipping plan"`)
	assert.Contains(t, body, `"k":5`)
}
