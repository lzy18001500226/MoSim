package blockstoreservice

import "testing"

// Regression for the fail-closed change. Prior to this fix, an unknown
// visibility value would fall through to `return true` (fail open), meaning
// a typo in meta.acl.visibility silently exposed a private block. The tests
// below guard both the known-good cases and the corrupt-ACL fail-closed path.

func TestBlockACL_Allows(t *testing.T) {
	cases := []struct {
		name         string
		acl          BlockACL
		actor        int64
		createdBy    int64
		wantAllowed  bool
	}{
		{"empty visibility allows org member", BlockACL{}, 10, 99, true},
		{"workspace visibility allows org member", BlockACL{Visibility: "workspace"}, 10, 99, true},
		{"org visibility allows org member", BlockACL{Visibility: "org"}, 10, 99, true},
		{"private allows author", BlockACL{Visibility: "private"}, 10, 10, true},
		{"private denies non-author without allowlist", BlockACL{Visibility: "private"}, 10, 99, false},
		{"private allows whitelisted user", BlockACL{Visibility: "private", AllowedUsers: []int64{10}}, 10, 99, true},
		{"private denies user not in allowlist", BlockACL{Visibility: "private", AllowedUsers: []int64{7, 8}}, 10, 99, false},
		// Fail-closed: unknown / typo / future value must NOT leak content.
		{"unknown visibility fails closed", BlockACL{Visibility: "public"}, 10, 99, false},
		{"typo visibility fails closed", BlockACL{Visibility: "privte"}, 10, 10, false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := tc.acl.allows(tc.actor, tc.createdBy)
			if got != tc.wantAllowed {
				t.Fatalf("allows(actor=%d, createdBy=%d) = %v, want %v", tc.actor, tc.createdBy, got, tc.wantAllowed)
			}
		})
	}
}
