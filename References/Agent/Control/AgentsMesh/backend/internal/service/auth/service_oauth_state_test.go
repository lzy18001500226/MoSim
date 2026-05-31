package auth

import (
	"context"
	"testing"
	"time"

	"github.com/alicebob/miniredis/v2"
	"github.com/redis/go-redis/v9"
)

func TestGenerateState(t *testing.T) {
	state1, err := GenerateState()
	if err != nil {
		t.Fatalf("GenerateState failed: %v", err)
	}
	if state1 == "" {
		t.Error("GenerateState returned empty string")
	}

	state2, err := GenerateState()
	if err != nil {
		t.Fatalf("GenerateState failed: %v", err)
	}

	// States should be unique
	if state1 == state2 {
		t.Error("GenerateState returned duplicate states")
	}
}

func TestGenerateOAuthState(t *testing.T) {
	// Start miniredis for testing
	mr, err := miniredis.Run()
	if err != nil {
		t.Fatalf("Failed to start miniredis: %v", err)
	}
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	cfg := &Config{
		JWTSecret:     "test-secret",
		JWTExpiration: time.Hour,
		Issuer:        "test-issuer",
	}
	svc := NewServiceWithRedis(cfg, nil, redisClient)
	ctx := context.Background()

	state, err := svc.GenerateOAuthState(ctx, "github", "https://example.com/callback")
	if err != nil {
		t.Fatalf("GenerateOAuthState failed: %v", err)
	}
	if state == "" {
		t.Error("State is empty")
	}

	// Validate the state
	redirectURL, err := svc.ValidateOAuthState(ctx, state)
	if err != nil {
		t.Fatalf("ValidateOAuthState failed: %v", err)
	}
	if redirectURL != "https://example.com/callback" {
		t.Errorf("RedirectURL = %s, want https://example.com/callback", redirectURL)
	}
}

func TestValidateOAuthState(t *testing.T) {
	// Start miniredis for testing
	mr, err := miniredis.Run()
	if err != nil {
		t.Fatalf("Failed to start miniredis: %v", err)
	}
	defer mr.Close()

	redisClient := redis.NewClient(&redis.Options{
		Addr: mr.Addr(),
	})
	defer redisClient.Close()

	cfg := &Config{
		JWTSecret:     "test-secret",
		JWTExpiration: time.Hour,
		Issuer:        "test-issuer",
	}
	svc := NewServiceWithRedis(cfg, nil, redisClient)
	ctx := context.Background()

	t.Run("valid state", func(t *testing.T) {
		state, _ := svc.GenerateOAuthState(ctx, "github", "https://example.com")
		redirectURL, err := svc.ValidateOAuthState(ctx, state)
		if err != nil {
			t.Fatalf("ValidateOAuthState failed: %v", err)
		}
		if redirectURL != "https://example.com" {
			t.Errorf("RedirectURL mismatch")
		}
	})

	t.Run("invalid state", func(t *testing.T) {
		_, err := svc.ValidateOAuthState(ctx, "invalid-state")
		if err == nil {
			t.Error("Expected error for invalid state")
		}
		if err != ErrInvalidState {
			t.Errorf("Expected ErrInvalidState, got %v", err)
		}
	})

	t.Run("state used twice", func(t *testing.T) {
		state, _ := svc.GenerateOAuthState(ctx, "github", "https://example.com")
		// First use should succeed
		_, err := svc.ValidateOAuthState(ctx, state)
		if err != nil {
			t.Fatalf("First validation failed: %v", err)
		}
		// Second use should fail (state is deleted after first use)
		_, err = svc.ValidateOAuthState(ctx, state)
		if err == nil {
			t.Error("Expected error for reused state")
		}
	})
}
