package crypto

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEncryptor_EncryptDecrypt(t *testing.T) {
	t.Run("should encrypt and decrypt correctly", func(t *testing.T) {
		enc := NewEncryptor("test-secret-key")
		plaintext := "Hello, World!"

		ciphertext, err := enc.Encrypt(plaintext)
		require.NoError(t, err)
		assert.NotEmpty(t, ciphertext)
		assert.NotEqual(t, plaintext, ciphertext)

		decrypted, err := enc.Decrypt(ciphertext)
		require.NoError(t, err)
		assert.Equal(t, plaintext, decrypted)
	})

	t.Run("should handle empty string", func(t *testing.T) {
		enc := NewEncryptor("test-secret-key")

		ciphertext, err := enc.Encrypt("")
		require.NoError(t, err)

		decrypted, err := enc.Decrypt(ciphertext)
		require.NoError(t, err)
		assert.Equal(t, "", decrypted)
	})

	t.Run("should handle unicode strings", func(t *testing.T) {
		enc := NewEncryptor("test-secret-key")
		plaintext := "你好世界！🎉"

		ciphertext, err := enc.Encrypt(plaintext)
		require.NoError(t, err)

		decrypted, err := enc.Decrypt(ciphertext)
		require.NoError(t, err)
		assert.Equal(t, plaintext, decrypted)
	})

	t.Run("should produce different ciphertext for same plaintext", func(t *testing.T) {
		enc := NewEncryptor("test-secret-key")
		plaintext := "test message"

		ciphertext1, err := enc.Encrypt(plaintext)
		require.NoError(t, err)

		ciphertext2, err := enc.Encrypt(plaintext)
		require.NoError(t, err)

		// Due to random nonce, ciphertexts should be different
		assert.NotEqual(t, ciphertext1, ciphertext2)
	})

	t.Run("should fail with invalid ciphertext", func(t *testing.T) {
		enc := NewEncryptor("test-secret-key")

		_, err := enc.Decrypt("not-valid-base64!!!")
		assert.ErrorIs(t, err, ErrInvalidCiphertext)
	})

	t.Run("should fail with too short ciphertext", func(t *testing.T) {
		enc := NewEncryptor("test-secret-key")

		// Valid base64 but too short for nonce
		_, err := enc.Decrypt("YWJj") // "abc" in base64
		assert.ErrorIs(t, err, ErrInvalidCiphertext)
	})

	t.Run("should fail with wrong key", func(t *testing.T) {
		enc1 := NewEncryptor("key-1")
		enc2 := NewEncryptor("key-2")

		ciphertext, err := enc1.Encrypt("secret message")
		require.NoError(t, err)

		_, err = enc2.Decrypt(ciphertext)
		assert.ErrorIs(t, err, ErrDecryptionFailed)
	})
}

func TestHashPassword(t *testing.T) {
	t.Run("should hash password", func(t *testing.T) {
		password := "my-secure-password"

		hash, err := HashPassword(password)
		require.NoError(t, err)
		assert.NotEmpty(t, hash)
		assert.NotEqual(t, password, hash)
		// bcrypt hashes start with $2a$ or $2b$
		assert.True(t, strings.HasPrefix(hash, "$2"))
	})

	t.Run("should produce different hashes for same password", func(t *testing.T) {
		password := "my-secure-password"

		hash1, err := HashPassword(password)
		require.NoError(t, err)

		hash2, err := HashPassword(password)
		require.NoError(t, err)

		// bcrypt uses random salt, so hashes should be different
		assert.NotEqual(t, hash1, hash2)
	})
}

func TestVerifyPassword(t *testing.T) {
	t.Run("should verify correct password", func(t *testing.T) {
		password := "my-secure-password"
		hash, err := HashPassword(password)
		require.NoError(t, err)

		assert.True(t, VerifyPassword(password, hash))
	})

	t.Run("should reject wrong password", func(t *testing.T) {
		password := "my-secure-password"
		hash, err := HashPassword(password)
		require.NoError(t, err)

		assert.False(t, VerifyPassword("wrong-password", hash))
	})

	t.Run("should reject invalid hash", func(t *testing.T) {
		assert.False(t, VerifyPassword("password", "invalid-hash"))
	})
}

func TestGenerateRandomString(t *testing.T) {
	t.Run("should generate string of correct length", func(t *testing.T) {
		str, err := GenerateRandomString(32)
		require.NoError(t, err)
		assert.Len(t, str, 32)
	})

	t.Run("should generate hex string", func(t *testing.T) {
		str, err := GenerateRandomString(16)
		require.NoError(t, err)

		// Verify it's valid hex
		for _, c := range str {
			assert.True(t, (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))
		}
	})

	t.Run("should generate unique strings", func(t *testing.T) {
		str1, err := GenerateRandomString(32)
		require.NoError(t, err)

		str2, err := GenerateRandomString(32)
		require.NoError(t, err)

		assert.NotEqual(t, str1, str2)
	})
}

func TestGenerateRandomBytes(t *testing.T) {
	t.Run("should generate bytes of correct length", func(t *testing.T) {
		bytes, err := GenerateRandomBytes(32)
		require.NoError(t, err)
		assert.Len(t, bytes, 32)
	})

	t.Run("should generate unique bytes", func(t *testing.T) {
		bytes1, err := GenerateRandomBytes(32)
		require.NoError(t, err)

		bytes2, err := GenerateRandomBytes(32)
		require.NoError(t, err)

		assert.NotEqual(t, bytes1, bytes2)
	})
}

func TestGenerateToken(t *testing.T) {
	t.Run("should generate 64 character token", func(t *testing.T) {
		token, err := GenerateToken()
		require.NoError(t, err)
		assert.Len(t, token, 64)
	})
}

func TestGenerateAPIKey(t *testing.T) {
	t.Run("should generate 32 character API key", func(t *testing.T) {
		key, err := GenerateAPIKey()
		require.NoError(t, err)
		assert.Len(t, key, 32)
	})
}

func TestSHA256Hash(t *testing.T) {
	t.Run("should produce consistent hash", func(t *testing.T) {
		input := "test input"

		hash1 := SHA256Hash(input)
		hash2 := SHA256Hash(input)

		assert.Equal(t, hash1, hash2)
		assert.Len(t, hash1, 64) // SHA-256 produces 32 bytes = 64 hex chars
	})

	t.Run("should produce different hashes for different inputs", func(t *testing.T) {
		hash1 := SHA256Hash("input1")
		hash2 := SHA256Hash("input2")

		assert.NotEqual(t, hash1, hash2)
	})

	t.Run("should handle empty string", func(t *testing.T) {
		hash := SHA256Hash("")
		assert.NotEmpty(t, hash)
		assert.Len(t, hash, 64)
	})
}

func TestCompareHashes(t *testing.T) {
	t.Run("should return true for equal strings", func(t *testing.T) {
		assert.True(t, CompareHashes("abc123", "abc123"))
	})

	t.Run("should return false for different strings", func(t *testing.T) {
		assert.False(t, CompareHashes("abc123", "abc124"))
	})

	t.Run("should return false for different lengths", func(t *testing.T) {
		assert.False(t, CompareHashes("abc", "abcd"))
	})

	t.Run("should return true for empty strings", func(t *testing.T) {
		assert.True(t, CompareHashes("", ""))
	})
}

func TestMaskString(t *testing.T) {
	t.Run("should mask middle of string", func(t *testing.T) {
		result := MaskString("1234567890", 2)
		assert.Equal(t, "12****90", result)
	})

	t.Run("should return **** for short strings", func(t *testing.T) {
		result := MaskString("abc", 2)
		assert.Equal(t, "****", result)
	})

	t.Run("should handle edge case at boundary", func(t *testing.T) {
		result := MaskString("abcd", 2)
		assert.Equal(t, "****", result) // len=4, n*2=4, so it's not greater
	})

	t.Run("should handle n=1", func(t *testing.T) {
		result := MaskString("abcdef", 1)
		assert.Equal(t, "a****f", result)
	})
}

func TestMaskEmail(t *testing.T) {
	t.Run("should mask email correctly", func(t *testing.T) {
		result := MaskEmail("john.doe@example.com")
		assert.Equal(t, "j****e@example.com", result)
	})

	t.Run("should handle short local part", func(t *testing.T) {
		result := MaskEmail("a@example.com")
		assert.Equal(t, "****", result)
	})

	t.Run("should handle no @ symbol", func(t *testing.T) {
		result := MaskEmail("notanemail")
		assert.Equal(t, "****", result)
	})

	t.Run("should handle @ at start", func(t *testing.T) {
		result := MaskEmail("@example.com")
		assert.Equal(t, "****", result)
	})

	t.Run("should handle two character local part", func(t *testing.T) {
		result := MaskEmail("ab@example.com")
		assert.Equal(t, "a****b@example.com", result)
	})
}

func TestEncryptWithKey(t *testing.T) {
	t.Run("should encrypt and decrypt", func(t *testing.T) {
		key := "my-secret-key"
		plaintext := "sensitive data"

		ciphertext, err := EncryptWithKey(plaintext, key)
		require.NoError(t, err)
		assert.NotEmpty(t, ciphertext)

		decrypted, err := DecryptWithKey(ciphertext, key)
		require.NoError(t, err)
		assert.Equal(t, plaintext, decrypted)
	})

	t.Run("should handle empty plaintext", func(t *testing.T) {
		key := "my-secret-key"

		ciphertext, err := EncryptWithKey("", key)
		require.NoError(t, err)
		assert.Empty(t, ciphertext)
	})

	t.Run("should handle empty ciphertext", func(t *testing.T) {
		key := "my-secret-key"

		decrypted, err := DecryptWithKey("", key)
		require.NoError(t, err)
		assert.Empty(t, decrypted)
	})
}
