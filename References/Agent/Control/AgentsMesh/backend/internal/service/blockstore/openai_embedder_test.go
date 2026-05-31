package blockstoreservice

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestOpenAIEmbedder_HappyPath(t *testing.T) {
	var captured *http.Request
	var bodyRaw []byte
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		captured = r
		bodyRaw, _ = io.ReadAll(r.Body)
		_, _ = w.Write([]byte(`{"data":[{"embedding":[0.1,0.2,0.3]}]}`))
	}))
	defer srv.Close()

	e, err := NewOpenAIEmbedder(OpenAIEmbedderConfig{
		APIKey: "sk-test", Model: "text-embedding-3-small",
		Dims: 3, BaseURL: srv.URL,
	})
	require.NoError(t, err)

	vec, err := e.Embed(context.Background(), "hello world")
	require.NoError(t, err)
	assert.Equal(t, []float32{0.1, 0.2, 0.3}, vec)

	require.NotNil(t, captured)
	assert.Equal(t, "Bearer sk-test", captured.Header.Get("Authorization"))
	assert.Equal(t, "/embeddings", captured.URL.Path)

	var body map[string]any
	require.NoError(t, json.Unmarshal(bodyRaw, &body))
	assert.Equal(t, "text-embedding-3-small", body["model"])
	assert.Equal(t, "hello world", body["input"])
}

func TestOpenAIEmbedder_APIError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(401)
		_, _ = w.Write([]byte(`{"error":{"message":"Invalid API key","type":"auth_error"}}`))
	}))
	defer srv.Close()

	e, _ := NewOpenAIEmbedder(OpenAIEmbedderConfig{
		APIKey: "sk-bad", BaseURL: srv.URL, Dims: 3,
	})
	_, err := e.Embed(context.Background(), "hi")
	require.Error(t, err)
	assert.Contains(t, err.Error(), "Invalid API key")
}

func TestOpenAIEmbedder_RequiresAPIKey(t *testing.T) {
	_, err := NewOpenAIEmbedder(OpenAIEmbedderConfig{Model: "foo"})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "APIKey")
}

func TestOpenAIEmbedder_DimsSelfHeal(t *testing.T) {
	// Server returns 5-dim even though caller configured 3 — embedder should
	// trust the server's response and update its reported Dims.
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, _ = w.Write([]byte(`{"data":[{"embedding":[0.1,0.2,0.3,0.4,0.5]}]}`))
	}))
	defer srv.Close()

	e, _ := NewOpenAIEmbedder(OpenAIEmbedderConfig{
		APIKey: "sk-test", BaseURL: srv.URL, Dims: 3,
	})
	vec, err := e.Embed(context.Background(), "hi")
	require.NoError(t, err)
	assert.Len(t, vec, 5)
	assert.Equal(t, 5, e.Dims())
}
