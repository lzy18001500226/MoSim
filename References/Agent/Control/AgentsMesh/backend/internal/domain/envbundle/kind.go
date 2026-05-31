package envbundle

// Kind enumerates the recognized envbundle categories. Stored in the DB as a
// plain VARCHAR so adding a new value never requires a schema migration; the
// allowed set is purely a code-layer convention. Unknown kinds round-trip
// transparently — they're rendered in the catch-all bucket by the UI.
const (
	// KindCredential bundles store secret API keys / tokens. The service
	// layer encrypts every value before writing and decrypts on read.
	KindCredential = "credential"

	// KindRuntime bundles store non-secret runtime preferences (model name,
	// log level, base URL overrides, etc.). Values are stored as plaintext.
	KindRuntime = "runtime"

	// KindShared bundles are owned at org scope and visible to org members.
	// Values may be plaintext or encrypted depending on per-bundle settings;
	// the first iteration treats them as plaintext.
	//
	// STATUS: reserved capability. The DB schema + repo `ListEffectiveForUser`
	// already union user-scope with org-scope bundles by OwnerScope, but the
	// REST surface only exposes user-scope CRUD (/api/v1/users/env-bundles).
	// Creating an org-scope bundle therefore requires direct DB access today;
	// the per-org REST endpoints + admin/member permission model are tracked
	// for a follow-up iteration (see plan: "Org 级 EnvBundle 的权限模型细化").
	// Do NOT take "KindShared exists" to mean the full UX is wired up.
	KindShared = "shared"
)

// OwnerScope distinguishes user-private bundles from org-shared bundles.
//
// OwnerScopeOrg rows are honored by `ListEffectiveForUser` (so Pods can
// reference org-shared bundle names via USE_ENV_BUNDLE), but no REST/UI
// flow currently creates them. See KindShared comment above.
const (
	OwnerScopeUser = "user"
	OwnerScopeOrg  = "org"
)

// IsEncryptedKind reports whether values in a bundle of this kind should be
// transparently encrypted by the service layer. Add new encrypted kinds here.
func IsEncryptedKind(kind string) bool {
	return kind == KindCredential
}
