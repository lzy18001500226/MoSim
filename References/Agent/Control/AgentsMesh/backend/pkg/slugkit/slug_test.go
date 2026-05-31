package slugkit

import (
	"context"
	"errors"
	"strings"
	"testing"
)

func TestSanitize(t *testing.T) {
	cases := []struct {
		in, want string
	}{
		{"John.Doe", "john-doe"},
		{"UPPER", "upper"},
		{"user_123", "user-123"},
		{"foo bar", "foo-bar"},
		{"foo--bar", "foo-bar"},
		{"a---b", "a-b"},
		{"  spaced  ", "spaced"},
		{"-leading-trailing-", "leading-trailing"},
		{"already-clean", "already-clean"},
		{"a1b2c3", "a1b2c3"},
		{"", ""},
		{"---", ""},
		{"@#$%", ""},
		{"张三", ""},
		{"🚀rocket", "rocket"},
		{"mix中文123", "mix-123"},
		{"user@example.com", "user-example-com"},
	}
	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			got := Sanitize(tc.in)
			if got != tc.want {
				t.Errorf("Sanitize(%q) = %q, want %q", tc.in, got, tc.want)
			}
		})
	}
}

func TestSanitize_RespectsMaxLen(t *testing.T) {
	long := strings.Repeat("a", 150)
	if got := Sanitize(long); len(got) != MaxLen {
		t.Errorf("Sanitize len = %d, want %d", len(got), MaxLen)
	}
}

func TestSanitize_TrimsTrailingHyphenAfterTruncation(t *testing.T) {
	in := strings.Repeat("a", 99) + "-bbbb"
	got := Sanitize(in)
	if strings.HasSuffix(got, "-") {
		t.Errorf("Sanitize(%q) = %q, has trailing hyphen", in, got)
	}
	if len(got) > MaxLen {
		t.Errorf("Sanitize len = %d, exceeds max %d", len(got), MaxLen)
	}
}

func TestValidate_Accepts(t *testing.T) {
	valid := []string{"foo", "foo-bar", "a1", "1a", "a-b-c-d", "nested-2-deep"}
	for _, s := range valid {
		t.Run(s, func(t *testing.T) {
			if err := Validate(s); err != nil {
				t.Errorf("Validate(%q) = %v, want nil", s, err)
			}
		})
	}
}

func TestValidate_Rejects(t *testing.T) {
	cases := []struct {
		in  string
		err error
	}{
		{"", ErrEmpty},
		{"a", ErrTooShort},
		{"1", ErrTooShort},
		{strings.Repeat("a", MaxLen+1), ErrTooLong},
		{"Foo", ErrInvalidFormat},
		{"foo--bar", ErrInvalidFormat},
		{"-foo", ErrInvalidFormat},
		{"foo-", ErrInvalidFormat},
		{"foo_bar", ErrInvalidFormat},
		{"foo.bar", ErrInvalidFormat},
		{"foo bar", ErrInvalidFormat},
		{"admin", ErrReserved},
		{"api", ErrReserved},
		{"onboarding", ErrReserved},
	}
	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			err := Validate(tc.in)
			if !errors.Is(err, tc.err) {
				t.Errorf("Validate(%q) = %v, want %v", tc.in, err, tc.err)
			}
		})
	}
}

func TestSanitizeAndValidate_Contract(t *testing.T) {
	inputs := []string{
		"John.Doe", "user_123", "张三", "🚀test",
		"UPPER_CASE.WITH.DOTS", "  spaced  ", strings.Repeat("a", 200),
	}
	for _, in := range inputs {
		t.Run(in, func(t *testing.T) {
			s, err := SanitizeAndValidate(in)
			if err != nil {
				if !errors.Is(err, ErrEmpty) && !errors.Is(err, ErrTooShort) && !errors.Is(err, ErrReserved) {
					t.Errorf("SanitizeAndValidate(%q) unexpected error: %v", in, err)
				}
				return
			}
			if vErr := Validate(s); vErr != nil {
				t.Errorf("output %q failed Validate: %v", s, vErr)
			}
		})
	}
}

func TestGenerateUnique_FirstAvailable(t *testing.T) {
	ctx := context.Background()
	check := func(_ context.Context, _ string) (bool, error) { return true, nil }
	got, err := GenerateUnique(ctx, "John.Doe", check)
	if err != nil || got != "john-doe" {
		t.Errorf("got (%q,%v), want (john-doe,nil)", got, err)
	}
}

func TestGenerateUnique_AppendsSuffixOnCollision(t *testing.T) {
	ctx := context.Background()
	taken := map[string]bool{"john-doe": true, "john-doe-2": true}
	check := func(_ context.Context, c string) (bool, error) { return !taken[c], nil }
	got, err := GenerateUnique(ctx, "John.Doe", check)
	if err != nil || got != "john-doe-3" {
		t.Errorf("got (%q,%v), want (john-doe-3,nil)", got, err)
	}
}

func TestGenerateUnique_ExhaustsAttempts(t *testing.T) {
	ctx := context.Background()
	check := func(_ context.Context, _ string) (bool, error) { return false, nil }
	_, err := GenerateUnique(ctx, "foo", check)
	if !errors.Is(err, ErrCollisionExhausted) {
		t.Errorf("err = %v, want ErrCollisionExhausted", err)
	}
}

func TestGenerateUnique_BaseReservedReturnsErr(t *testing.T) {
	ctx := context.Background()
	check := func(_ context.Context, _ string) (bool, error) { return true, nil }
	_, err := GenerateUnique(ctx, "admin", check)
	if !errors.Is(err, ErrReserved) {
		t.Errorf("err = %v, want ErrReserved", err)
	}
}

func TestGenerateUnique_BaseEmptyReturnsErr(t *testing.T) {
	ctx := context.Background()
	check := func(_ context.Context, _ string) (bool, error) { return true, nil }
	_, err := GenerateUnique(ctx, "🚀", check)
	if !errors.Is(err, ErrEmpty) {
		t.Errorf("err = %v, want ErrEmpty (sanitized to empty)", err)
	}
}

func TestGenerateUnique_BaseTooShortReturnsErr(t *testing.T) {
	ctx := context.Background()
	check := func(_ context.Context, _ string) (bool, error) { return true, nil }
	_, err := GenerateUnique(ctx, "a", check)
	if !errors.Is(err, ErrTooShort) {
		t.Errorf("err = %v, want ErrTooShort", err)
	}
}

func TestGenerateUnique_LongBaseTruncatedToFitSuffix(t *testing.T) {
	ctx := context.Background()
	long := strings.Repeat("a", MaxLen)
	truncated := strings.Repeat("a", MaxLen-suffixReserve)
	taken := map[string]bool{long: true, truncated: true}
	check := func(_ context.Context, c string) (bool, error) { return !taken[c], nil }

	got, err := GenerateUnique(ctx, long, check)
	if err != nil {
		t.Fatalf("expected truncation to allow retry, got error: %v", err)
	}
	if len(got) > MaxLen {
		t.Errorf("candidate %q exceeds MaxLen=%d (len=%d)", got, MaxLen, len(got))
	}
	want := truncated + "-2"
	if got != want {
		t.Errorf("candidate = %q, want %q (truncated base + -2)", got, want)
	}
}

func TestIsReserved(t *testing.T) {
	if !IsReserved("admin") {
		t.Error("admin should be reserved")
	}
	if IsReserved("john-doe") {
		t.Error("john-doe should not be reserved")
	}
}
