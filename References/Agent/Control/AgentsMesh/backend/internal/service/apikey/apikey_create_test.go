package apikey

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestCreateAPIKey(t *testing.T) {
	ctx := context.Background()

	t.Run("success — key format and hash", func(t *testing.T) {
		svc, _ := newTestService(t)

		resp, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      10,
			Name:           "test-key",
			Scopes:         []string{"pods:read", "tickets:write"},
		})
		require.NoError(t, err)
		require.NotNil(t, resp)

		// Raw key starts with "amk_"
		assert.True(t, strings.HasPrefix(resp.RawKey, "amk_"), "raw key should start with amk_")

		// Total length: "amk_" (4) + 80 hex chars (40 bytes) = 84
		assert.Len(t, resp.RawKey, 84)

		// Key prefix is first 12 chars
		assert.Equal(t, resp.RawKey[:12], resp.APIKey.KeyPrefix)
		assert.Len(t, resp.APIKey.KeyPrefix, 12)

		// Key hash is SHA-256 of the raw key
		hashBytes := sha256.Sum256([]byte(resp.RawKey))
		expectedHash := hex.EncodeToString(hashBytes[:])
		assert.Equal(t, expectedHash, resp.APIKey.KeyHash)

		// API key attributes
		assert.Equal(t, int64(1), resp.APIKey.OrganizationID)
		assert.Equal(t, int64(10), resp.APIKey.CreatedBy)
		assert.Equal(t, "test-key", resp.APIKey.Name)
		assert.True(t, resp.APIKey.IsEnabled)
		assert.Nil(t, resp.APIKey.ExpiresAt)
		assert.Len(t, resp.APIKey.Scopes, 2)
	})

	t.Run("invalid scope returns ErrInvalidScope", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "bad-scope-key",
			Scopes:         []string{"pods:read", "invalid:scope"},
		})
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrInvalidScope)
	})

	t.Run("duplicate name returns ErrDuplicateKeyName", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "dup-name",
			Scopes:         []string{"pods:read"},
		})
		require.NoError(t, err)

		_, err = svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "dup-name",
			Scopes:         []string{"pods:read"},
		})
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrDuplicateKeyName)
	})

	t.Run("same name in different org is allowed", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "shared-name",
			Scopes:         []string{"pods:read"},
		})
		require.NoError(t, err)

		_, err = svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 2,
			CreatedBy:      1,
			Name:           "shared-name",
			Scopes:         []string{"pods:read"},
		})
		require.NoError(t, err)
	})

	t.Run("name too long returns ErrNameTooLong", func(t *testing.T) {
		svc, _ := newTestService(t)

		longName := strings.Repeat("a", 256)
		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           longName,
			Scopes:         []string{"pods:read"},
		})
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrNameTooLong)
	})

	t.Run("name at max length is OK", func(t *testing.T) {
		svc, _ := newTestService(t)

		exactName := strings.Repeat("a", 255)
		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           exactName,
			Scopes:         []string{"pods:read"},
		})
		require.NoError(t, err)
	})

	t.Run("ExpiresIn too small returns ErrInvalidExpiresIn", func(t *testing.T) {
		svc, _ := newTestService(t)

		tooSmall := 299 // less than 300
		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "short-expiry",
			Scopes:         []string{"pods:read"},
			ExpiresIn:      &tooSmall,
		})
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrInvalidExpiresIn)
	})

	t.Run("ExpiresIn too large returns ErrInvalidExpiresIn", func(t *testing.T) {
		svc, _ := newTestService(t)

		tooLarge := 94608001 // more than 3 years
		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "long-expiry",
			Scopes:         []string{"pods:read"},
			ExpiresIn:      &tooLarge,
		})
		require.Error(t, err)
		assert.ErrorIs(t, err, ErrInvalidExpiresIn)
	})

	t.Run("ExpiresIn valid range sets ExpiresAt correctly", func(t *testing.T) {
		svc, _ := newTestService(t)

		expiry := 3600 // 1 hour
		before := time.Now()
		resp, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "valid-expiry",
			Scopes:         []string{"pods:read"},
			ExpiresIn:      &expiry,
		})
		after := time.Now()
		require.NoError(t, err)
		require.NotNil(t, resp.APIKey.ExpiresAt)

		expectedMin := before.Add(time.Duration(expiry) * time.Second)
		expectedMax := after.Add(time.Duration(expiry) * time.Second)
		assert.True(t, resp.APIKey.ExpiresAt.After(expectedMin) || resp.APIKey.ExpiresAt.Equal(expectedMin))
		assert.True(t, resp.APIKey.ExpiresAt.Before(expectedMax) || resp.APIKey.ExpiresAt.Equal(expectedMax))
	})

	t.Run("ExpiresIn nil means ExpiresAt is nil", func(t *testing.T) {
		svc, _ := newTestService(t)

		resp, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "no-expiry",
			Scopes:         []string{"pods:read"},
			ExpiresIn:      nil,
		})
		require.NoError(t, err)
		assert.Nil(t, resp.APIKey.ExpiresAt)
	})

	t.Run("ExpiresIn at minimum boundary (300)", func(t *testing.T) {
		svc, _ := newTestService(t)

		minExpiry := 300
		resp, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "min-expiry",
			Scopes:         []string{"pods:read"},
			ExpiresIn:      &minExpiry,
		})
		require.NoError(t, err)
		require.NotNil(t, resp.APIKey.ExpiresAt)
	})

	t.Run("ExpiresIn at maximum boundary (94608000)", func(t *testing.T) {
		svc, _ := newTestService(t)

		maxExpiry := 94608000
		resp, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "max-expiry",
			Scopes:         []string{"pods:read"},
			ExpiresIn:      &maxExpiry,
		})
		require.NoError(t, err)
		require.NotNil(t, resp.APIKey.ExpiresAt)
	})

	t.Run("empty scopes returns ErrScopesRequired", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "no-scopes",
			Scopes:         []string{},
		})
		require.ErrorIs(t, err, ErrScopesRequired)
	})

	t.Run("empty name returns ErrNameEmpty", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "",
			Scopes:         []string{"pods:read"},
		})
		require.ErrorIs(t, err, ErrNameEmpty)
	})

	t.Run("whitespace-only name returns ErrNameEmpty", func(t *testing.T) {
		svc, _ := newTestService(t)

		_, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "   \t  ",
			Scopes:         []string{"pods:read"},
		})
		require.ErrorIs(t, err, ErrNameEmpty)
	})

	t.Run("name with leading/trailing spaces is trimmed", func(t *testing.T) {
		svc, _ := newTestService(t)

		resp, err := svc.CreateAPIKey(ctx, &CreateAPIKeyRequest{
			OrganizationID: 1,
			CreatedBy:      1,
			Name:           "  padded-name  ",
			Scopes:         []string{"pods:read"},
		})
		require.NoError(t, err)
		assert.Equal(t, "padded-name", resp.APIKey.Name)
	})
}
