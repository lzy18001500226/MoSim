package apikey

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// ─── ListAPIKeys ───────────────────────────────────────────────────

func TestListAPIKeys(t *testing.T) {
	ctx := context.Background()

	t.Run("returns correct results", func(t *testing.T) {
		svc, _ := newTestService(t)
		createTestAPIKey(t, svc, 1, "list-key-1", []string{"pods:read"})
		createTestAPIKey(t, svc, 1, "list-key-2", []string{"pods:write"})
		createTestAPIKey(t, svc, 1, "list-key-3", []string{"tickets:read"})

		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 1,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(3), total)
		assert.Len(t, keys, 3)
	})

	t.Run("respects organization filter", func(t *testing.T) {
		svc, _ := newTestService(t)
		createTestAPIKey(t, svc, 1, "org1-key", []string{"pods:read"})
		createTestAPIKey(t, svc, 2, "org2-key", []string{"pods:read"})
		createTestAPIKey(t, svc, 2, "org2-key-2", []string{"pods:write"})

		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 2,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(2), total)
		assert.Len(t, keys, 2)
	})

	t.Run("respects limit", func(t *testing.T) {
		svc, _ := newTestService(t)
		for i := 0; i < 5; i++ {
			createTestAPIKey(t, svc, 1, "limit-key-"+string(rune('A'+i)), []string{"pods:read"})
		}

		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 1,
			Limit:          2,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(5), total) // total is always full count
		assert.Len(t, keys, 2)
	})

	t.Run("respects offset", func(t *testing.T) {
		svc, _ := newTestService(t)
		createTestAPIKey(t, svc, 1, "offset-key-A", []string{"pods:read"})
		createTestAPIKey(t, svc, 1, "offset-key-B", []string{"pods:read"})
		createTestAPIKey(t, svc, 1, "offset-key-C", []string{"pods:read"})

		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 1,
			Limit:          10,
			Offset:         2,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(3), total)
		assert.Len(t, keys, 1)
	})

	t.Run("default limit applied when limit is 0", func(t *testing.T) {
		svc, _ := newTestService(t)
		createTestAPIKey(t, svc, 1, "default-limit-key", []string{"pods:read"})

		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 1,
			Limit:          0, // should use defaultListLimit (50)
		})
		require.NoError(t, err)
		assert.Equal(t, int64(1), total)
		assert.Len(t, keys, 1) // fewer items than default limit
	})

	t.Run("max limit capped", func(t *testing.T) {
		svc, _ := newTestService(t)
		createTestAPIKey(t, svc, 1, "cap-limit-key", []string{"pods:read"})

		// Request a limit higher than maxListLimit (200)
		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 1,
			Limit:          500,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(1), total)
		assert.Len(t, keys, 1)
	})

	t.Run("filter by is_enabled", func(t *testing.T) {
		svc, db := newTestService(t)
		createTestAPIKey(t, svc, 1, "enabled-key", []string{"pods:read"})
		createDisabledAPIKey(t, svc, db, 1, "disabled-key", []string{"pods:read"})

		enabledOnly := true
		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 1,
			IsEnabled:      &enabledOnly,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(1), total)
		assert.Len(t, keys, 1)
		assert.Equal(t, "enabled-key", keys[0].Name)
	})

	t.Run("empty result", func(t *testing.T) {
		svc, _ := newTestService(t)

		keys, total, err := svc.ListAPIKeys(ctx, &ListAPIKeysFilter{
			OrganizationID: 999,
		})
		require.NoError(t, err)
		assert.Equal(t, int64(0), total)
		assert.Empty(t, keys)
	})
}

// ─── GetAPIKey ─────────────────────────────────────────────────────

func TestGetAPIKey(t *testing.T) {
	ctx := context.Background()

	t.Run("existing key", func(t *testing.T) {
		svc, _ := newTestService(t)
		_, created := createTestAPIKey(t, svc, 1, "get-key", []string{"pods:read", "tickets:write"})

		key, err := svc.GetAPIKey(ctx, created.ID, 1)
		require.NoError(t, err)
		assert.Equal(t, created.ID, key.ID)
		assert.Equal(t, "get-key", key.Name)
		assert.Equal(t, int64(1), key.OrganizationID)
	})

	t.Run("non-existent key returns ErrAPIKeyNotFound", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.GetAPIKey(ctx, 9999, 1)
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrAPIKeyNotFound)
	})

	t.Run("wrong org returns ErrAPIKeyNotFound", func(t *testing.T) {
		svc, _ := newTestService(t)
		_, created := createTestAPIKey(t, svc, 1, "org1-key", []string{"pods:read"})

		_, err := svc.GetAPIKey(ctx, created.ID, 2) // wrong org
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrAPIKeyNotFound)
	})
}
