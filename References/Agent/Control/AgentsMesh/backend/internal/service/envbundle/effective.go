package envbundle

import (
	"context"
	"log/slog"
)

// EffectiveBundle is a decrypted bundle ready to be merged into a Pod's
// process environment. The caller (ConfigBuilder) decides which subset is
// actually mounted based on AgentFile USE_ENV_BUNDLE declarations.
type EffectiveBundle struct {
	Name       string
	Kind       string
	OwnerScope string
	AgentSlug  *string
	Data       map[string]string
}

// GetEffectiveForUser returns all bundles visible to (userID, orgID),
// optionally filtered by agent_slug (bundles with agent_slug=NULL match any
// agent). Values are decrypted in the returned EffectiveBundle.Data.
//
// Mirrors the MCP pattern (buildMCPContext): backend pre-loads everything,
// AgentFile picks via USE_ENV_BUNDLE. No precedence logic at this layer.
//
// Decrypt failures on individual bundles are logged at ERROR level and that
// bundle is skipped — we choose isolation (other bundles still mount) over
// aborting Pod creation entirely. The log is the only signal an operator
// gets that a credential bundle is corrupt; do not silence it.
func (s *Service) GetEffectiveForUser(ctx context.Context, userID, orgID int64, agentSlug string) ([]*EffectiveBundle, error) {
	bundles, err := s.repo.ListEffectiveForUser(ctx, userID, orgID, agentSlug)
	if err != nil {
		return nil, err
	}

	out := make([]*EffectiveBundle, 0, len(bundles))
	for _, b := range bundles {
		if !b.IsActive {
			continue
		}
		data, err := s.decryptData(b.Kind, b.Data)
		if err != nil {
			slog.ErrorContext(ctx,
				"env bundle decrypt failed; skipping bundle for this pod",
				"bundle_id", b.ID,
				"name", b.Name,
				"kind", b.Kind,
				"owner_scope", b.OwnerScope,
				"error", err,
			)
			continue
		}
		out = append(out, &EffectiveBundle{
			Name:       b.Name,
			Kind:       b.Kind,
			OwnerScope: b.OwnerScope,
			AgentSlug:  b.AgentSlug,
			Data:       data,
		})
	}
	return out, nil
}

// AsContextMap converts a slice of effective bundles into the
// `map[bundle_name] -> KV map` shape consumed by AgentFile eval's
// USE_ENV_BUNDLE handler.
func AsContextMap(bundles []*EffectiveBundle) map[string]map[string]string {
	out := make(map[string]map[string]string, len(bundles))
	for _, b := range bundles {
		out[b.Name] = b.Data
	}
	return out
}
