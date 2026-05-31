package main

import (
	"log/slog"
	"os"
	"strconv"

	blockstoreservice "github.com/anthropics/agentsmesh/backend/internal/service/blockstore"
)

// selectEmbedder wires the BlockstoreService's embedding provider from env.
// Returns nil to mean "keep the default (HashEmbedder 256 dims)".
//
// Env contract:
//
//	EMBEDDING_PROVIDER=hash           → default, zero-deps, offline-safe
//	EMBEDDING_PROVIDER=openai         → api.openai.com (requires OPENAI_API_KEY)
//	OPENAI_API_KEY=sk-...
//	OPENAI_EMBEDDING_MODEL=text-embedding-3-small (default)
//	OPENAI_EMBEDDING_DIMS=1536       (default; 3-small=1536, 3-large=3072)
//	OPENAI_BASE_URL=https://...       optional: Azure / proxy override
func selectEmbedder() blockstoreservice.EmbeddingProvider {
	provider := os.Getenv("EMBEDDING_PROVIDER")
	switch provider {
	case "", "hash":
		return nil
	case "openai":
		e, err := blockstoreservice.NewOpenAIEmbedder(blockstoreservice.OpenAIEmbedderConfig{
			APIKey:  os.Getenv("OPENAI_API_KEY"),
			Model:   os.Getenv("OPENAI_EMBEDDING_MODEL"),
			Dims:    envInt("OPENAI_EMBEDDING_DIMS", 1536),
			BaseURL: os.Getenv("OPENAI_BASE_URL"),
		})
		if err != nil {
			slog.Default().Warn("blockstore.embedder.openai_init_failed",
				"err", err.Error(), "fallback", "hash")
			return nil
		}
		slog.Default().Info("blockstore.embedder.openai_enabled",
			"model", e.Model(), "dims", e.Dims())
		return e
	default:
		slog.Default().Warn("blockstore.embedder.unknown_provider",
			"provider", provider, "fallback", "hash")
		return nil
	}
}

func envInt(key string, fallback int) int {
	s := os.Getenv(key)
	if s == "" {
		return fallback
	}
	n, err := strconv.Atoi(s)
	if err != nil || n <= 0 {
		return fallback
	}
	return n
}
