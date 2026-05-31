package apikey

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestValidateKey(t *testing.T) {
	ctx := context.Background()

	t.Run("valid key returns correct result", func(t *testing.T) {
		svc, _ := newTestService(t)
		resp, key := createTestAPIKey(t, svc, 1, "validate-key", []string{"pods:read", "tickets:write"})

		result, err := svc.ValidateKey(ctx, resp.RawKey)
		require.NoError(t, err)
		require.NotNil(t, result)

		assert.Equal(t, key.ID, result.APIKeyID)
		assert.Equal(t, int64(1), result.OrganizationID)
		assert.Equal(t, int64(1), result.CreatedBy)
		assert.Equal(t, "validate-key", result.KeyName)
		assert.ElementsMatch(t, []string{"pods:read", "tickets:write"}, result.Scopes)
	})

	t.Run("non-existent key returns ErrAPIKeyNotFound", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.ValidateKey(ctx, "amk_nonexistentkey1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrAPIKeyNotFound)
	})

	t.Run("disabled key returns ErrAPIKeyDisabled", func(t *testing.T) {
		svc, db := newTestService(t)
		resp, _ := createDisabledAPIKey(t, svc, db, 1, "disabled-key", []string{"pods:read"})

		_, err := svc.ValidateKey(ctx, resp.RawKey)
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrAPIKeyDisabled)
	})

	t.Run("expired key returns ErrAPIKeyExpired", func(t *testing.T) {
		svc, db := newTestService(t)
		resp, _ := createExpiredAPIKey(t, svc, db, 1, "expired-key", []string{"pods:read"})

		_, err := svc.ValidateKey(ctx, resp.RawKey)
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrAPIKeyExpired)
	})

	t.Run("works without redis (redisClient = nil)", func(t *testing.T) {
		svc, _ := newTestService(t) // already uses nil redis
		resp, _ := createTestAPIKey(t, svc, 1, "no-redis-key", []string{"channels:read"})

		// First call — hits DB
		result, err := svc.ValidateKey(ctx, resp.RawKey)
		require.NoError(t, err)
		assert.Equal(t, "no-redis-key", result.KeyName)

		// Second call — still hits DB (no cache)
		result2, err := svc.ValidateKey(ctx, resp.RawKey)
		require.NoError(t, err)
		assert.Equal(t, result.APIKeyID, result2.APIKeyID)
	})

	t.Run("completely bogus key returns ErrAPIKeyNotFound", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.ValidateKey(ctx, "not-even-an-amk-key")
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrAPIKeyNotFound)
	})
}
