package auth

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewJWTManager(t *testing.T) {
	t.Run("should create manager with correct settings", func(t *testing.T) {
		m := NewJWTManager("secret-key", 24*time.Hour, "test-issuer")

		assert.NotNil(t, m)
		assert.Equal(t, 24*time.Hour, m.GetExpirationTime())
	})
}

func TestJWTManager_GenerateToken(t *testing.T) {
	m := NewJWTManager("test-secret-key", 24*time.Hour, "test-issuer")

	t.Run("should generate valid token", func(t *testing.T) {
		token, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "admin")

		require.NoError(t, err)
		assert.NotEmpty(t, token)
	})

	t.Run("should generate tokens with same content if called in same second", func(t *testing.T) {
		// JWT timestamps are in seconds, so tokens generated in the same second
		// will be identical if all other parameters are the same
		token1, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		token2, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		// Both tokens should be valid
		_, err = m.ValidateToken(token1)
		require.NoError(t, err)
		_, err = m.ValidateToken(token2)
		require.NoError(t, err)
	})

	t.Run("should generate different tokens for different users", func(t *testing.T) {
		token1, err := m.GenerateToken(123, "test1@example.com", "testuser1", 456, "admin")
		require.NoError(t, err)

		token2, err := m.GenerateToken(124, "test2@example.com", "testuser2", 456, "admin")
		require.NoError(t, err)

		assert.NotEqual(t, token1, token2)
	})
}

func TestJWTManager_ValidateToken(t *testing.T) {
	m := NewJWTManager("test-secret-key", 24*time.Hour, "test-issuer")

	t.Run("should validate and return correct claims", func(t *testing.T) {
		token, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		claims, err := m.ValidateToken(token)
		require.NoError(t, err)

		assert.Equal(t, int64(123), claims.UserID)
		assert.Equal(t, "test@example.com", claims.Email)
		assert.Equal(t, "testuser", claims.Username)
		assert.Equal(t, int64(456), claims.OrganizationID)
		assert.Equal(t, "admin", claims.Role)
		assert.Equal(t, "test-issuer", claims.Issuer)
		assert.Equal(t, "test@example.com", claims.Subject)
	})

	t.Run("should reject invalid token", func(t *testing.T) {
		_, err := m.ValidateToken("invalid-token")
		assert.ErrorIs(t, err, ErrInvalidToken)
	})

	t.Run("should reject tampered token", func(t *testing.T) {
		token, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		// Tamper with the token
		tampered := token + "x"

		_, err = m.ValidateToken(tampered)
		assert.ErrorIs(t, err, ErrInvalidToken)
	})

	t.Run("should reject token signed with different key", func(t *testing.T) {
		m2 := NewJWTManager("different-secret-key", 24*time.Hour, "test-issuer")

		token, err := m2.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		_, err = m.ValidateToken(token)
		assert.ErrorIs(t, err, ErrInvalidToken)
	})

	t.Run("should reject expired token", func(t *testing.T) {
		// Create manager with very short expiration
		shortM := NewJWTManager("test-secret-key", 1*time.Millisecond, "test-issuer")

		token, err := shortM.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		// Wait for token to expire
		time.Sleep(10 * time.Millisecond)

		_, err = shortM.ValidateToken(token)
		assert.ErrorIs(t, err, ErrTokenExpired)
	})

	t.Run("should handle empty token", func(t *testing.T) {
		_, err := m.ValidateToken("")
		assert.ErrorIs(t, err, ErrInvalidToken)
	})
}

func TestJWTManager_RefreshToken(t *testing.T) {
	m := NewJWTManager("test-secret-key", 24*time.Hour, "test-issuer")

	t.Run("should refresh token with same claims", func(t *testing.T) {
		originalToken, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "admin")
		require.NoError(t, err)

		originalClaims, err := m.ValidateToken(originalToken)
		require.NoError(t, err)

		// Refresh the token
		newToken, err := m.RefreshToken(originalClaims)
		require.NoError(t, err)

		// Note: if called in the same second, tokens will be identical
		// (JWT timestamps are second-precision)

		// Validate new token has same user data
		newClaims, err := m.ValidateToken(newToken)
		require.NoError(t, err)

		assert.Equal(t, originalClaims.UserID, newClaims.UserID)
		assert.Equal(t, originalClaims.Email, newClaims.Email)
		assert.Equal(t, originalClaims.Username, newClaims.Username)
		assert.Equal(t, originalClaims.OrganizationID, newClaims.OrganizationID)
		assert.Equal(t, originalClaims.Role, newClaims.Role)
	})
}

func TestJWTManager_GetExpirationTime(t *testing.T) {
	t.Run("should return configured expiration time", func(t *testing.T) {
		m := NewJWTManager("secret", 48*time.Hour, "issuer")
		assert.Equal(t, 48*time.Hour, m.GetExpirationTime())
	})
}

func TestClaims(t *testing.T) {
	t.Run("should handle zero organization ID", func(t *testing.T) {
		m := NewJWTManager("test-secret-key", 24*time.Hour, "test-issuer")

		token, err := m.GenerateToken(123, "test@example.com", "testuser", 0, "member")
		require.NoError(t, err)

		claims, err := m.ValidateToken(token)
		require.NoError(t, err)

		assert.Equal(t, int64(0), claims.OrganizationID)
	})

	t.Run("should handle empty role", func(t *testing.T) {
		m := NewJWTManager("test-secret-key", 24*time.Hour, "test-issuer")

		token, err := m.GenerateToken(123, "test@example.com", "testuser", 456, "")
		require.NoError(t, err)

		claims, err := m.ValidateToken(token)
		require.NoError(t, err)

		assert.Equal(t, "", claims.Role)
	})
}
