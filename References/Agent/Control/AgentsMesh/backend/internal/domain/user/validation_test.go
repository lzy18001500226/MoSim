package user

import (
	"errors"
	"strings"
	"testing"
)

func TestValidateUsername(t *testing.T) {
	cases := []struct {
		name    string
		input   string
		wantErr bool
	}{
		{"valid lowercase", "alice", false},
		{"valid mixed case", "Alice", false},
		{"valid digits", "alice123", false},
		{"valid with hyphen", "alice-doe", false},
		{"valid with underscore", "alice_doe", false},
		{"valid mixed", "Alice-1_b", false},
		{"too short", "ab", true},
		{"empty", "", true},
		{"too long", strings.Repeat("a", UsernameMaxLen+1), true},
		{"unicode", "用户名", true},
		{"emoji", "🚀user", true},
		{"dot", "alice.doe", true},
		{"at sign", "alice@example.com", true},
		{"space", "alice doe", true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			err := ValidateUsername(tc.input)
			if tc.wantErr && err == nil {
				t.Errorf("ValidateUsername(%q) = nil, want error", tc.input)
			}
			if !tc.wantErr && err != nil {
				t.Errorf("ValidateUsername(%q) = %v, want nil", tc.input, err)
			}
			if tc.wantErr && err != nil && !errors.Is(err, ErrInvalidUsername) {
				t.Errorf("ValidateUsername(%q) error = %v, want wrapping ErrInvalidUsername", tc.input, err)
			}
		})
	}
}
