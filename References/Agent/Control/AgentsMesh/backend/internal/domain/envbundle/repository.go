package envbundle

import "context"

// OwnerFilter narrows a List query. Three-state semantics for AgentSlug:
//   - nil          → no agent_slug filter (matches any value, including NULL)
//   - &"" empty    → match only rows where agent_slug IS NULL (universal bundles)
//   - &"x" non-empty → match rows where agent_slug = "x"
type OwnerFilter struct {
	OwnerScope string
	OwnerID    int64
	Kind       string
	AgentSlug  *string
}

// Repository persists EnvBundles. Encryption is the service's concern; the
// repo passes BundleData through as opaque JSONB.
type Repository interface {
	Create(ctx context.Context, bundle *EnvBundle) error
	// CreateWithPrimary creates the bundle and atomically marks it primary
	// within its (owner_scope, owner_id, agent_slug, kind) group — clearing
	// any existing primary in that group. Both writes share a transaction
	// so a half-applied state (created but primary clear failed) never
	// persists.
	CreateWithPrimary(ctx context.Context, bundle *EnvBundle) error
	GetByID(ctx context.Context, id int64) (*EnvBundle, error)
	GetByName(ctx context.Context, ownerScope string, ownerID int64, name string) (*EnvBundle, error)
	Update(ctx context.Context, bundle *EnvBundle, updates map[string]interface{}) error
	Delete(ctx context.Context, id int64) (int64, error)

	List(ctx context.Context, f OwnerFilter) ([]*EnvBundle, error)

	// ListEffectiveForUser loads bundles visible to (userID, orgID) for an
	// optional agent_slug. Includes user-owned bundles AND org-owned bundles
	// (when orgID > 0). agent_slug filter applied as `agent_slug = X OR agent_slug IS NULL`
	// so both agent-specific and universal bundles are included. Empty agentSlug
	// disables the agent filter entirely.
	ListEffectiveForUser(ctx context.Context, userID, orgID int64, agentSlug string) ([]*EnvBundle, error)

	// SetPrimary atomically clears other primaries in the same
	// (owner_scope, owner_id, agent_slug, kind) group and sets this bundle.
	SetPrimary(ctx context.Context, bundle *EnvBundle) error

	NameExists(ctx context.Context, ownerScope string, ownerID int64, name string, excludeID *int64) (bool, error)
}
