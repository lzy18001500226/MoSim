package envbundle

import (
	"context"

	"github.com/anthropics/agentsmesh/backend/internal/domain/envbundle"
)

// CreateParams is the input shape for creating a new bundle.
type CreateParams struct {
	OwnerScope  string
	OwnerID     int64
	AgentSlug   *string
	Name        string
	Description *string
	Kind        string
	KindPrimary bool
	Data        map[string]string
}

// UpdateParams is the input shape for updating an existing bundle. nil fields
// are skipped. Data has three states:
//   - nil           → no change
//   - &empty map    → clear all keys (caller explicitly wants the bundle empty)
//   - &non-empty    → replace stored values
type UpdateParams struct {
	Name        *string
	Description *string
	Kind        *string
	KindPrimary *bool
	Data        *map[string]string
	IsActive    *bool
}

// Create stores a new bundle. Credential-kind values are encrypted; other
// kinds are stored as plaintext. When KindPrimary is requested, the bundle
// row and the primary-promotion live in one transaction (see
// Repository.CreateWithPrimary) so we never end up with "created but failed
// to promote" partial state.
func (s *Service) Create(ctx context.Context, params *CreateParams) (*envbundle.EnvBundle, error) {
	if !validScope(params.OwnerScope) {
		return nil, ErrInvalidScope
	}
	if params.Kind == "" {
		return nil, ErrInvalidKind
	}

	exists, err := s.repo.NameExists(ctx, params.OwnerScope, params.OwnerID, params.Name, nil)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, ErrNameExists
	}

	data, err := s.encryptData(params.Kind, params.Data)
	if err != nil {
		return nil, err
	}

	bundle := &envbundle.EnvBundle{
		OwnerScope:  params.OwnerScope,
		OwnerID:     params.OwnerID,
		AgentSlug:   params.AgentSlug,
		Name:        params.Name,
		Description: params.Description,
		Kind:        params.Kind,
		Data:        data,
		IsActive:    true,
	}

	if params.KindPrimary {
		if err := s.repo.CreateWithPrimary(ctx, bundle); err != nil {
			return nil, err
		}
		return bundle, nil
	}
	if err := s.repo.Create(ctx, bundle); err != nil {
		return nil, err
	}
	return bundle, nil
}

// Update applies the non-nil fields. Data, when non-nil and non-empty, replaces
// the stored map after re-encryption.
func (s *Service) Update(ctx context.Context, ownerScope string, ownerID, id int64, params *UpdateParams) (*envbundle.EnvBundle, error) {
	bundle, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if bundle == nil || bundle.OwnerScope != ownerScope || bundle.OwnerID != ownerID {
		return nil, ErrNotFound
	}

	updates := map[string]interface{}{}
	if params.Name != nil && *params.Name != bundle.Name {
		exists, err := s.repo.NameExists(ctx, bundle.OwnerScope, bundle.OwnerID, *params.Name, &bundle.ID)
		if err != nil {
			return nil, err
		}
		if exists {
			return nil, ErrNameExists
		}
		updates["name"] = *params.Name
	}
	if params.Description != nil {
		updates["description"] = *params.Description
	}
	if params.Kind != nil && *params.Kind != bundle.Kind {
		updates["kind"] = *params.Kind
	}
	if params.IsActive != nil {
		updates["is_active"] = *params.IsActive
	}
	if params.Data != nil {
		// nil = "no change"; non-nil (incl. empty) = "replace" — empty map
		// means "explicitly clear all keys" so the bundle row stays alive
		// but its data becomes {}.
		effectiveKind := bundle.Kind
		if params.Kind != nil {
			effectiveKind = *params.Kind
		}
		data, err := s.encryptData(effectiveKind, *params.Data)
		if err != nil {
			return nil, err
		}
		updates["data"] = data
	}

	if len(updates) > 0 {
		if err := s.repo.Update(ctx, bundle, updates); err != nil {
			return nil, err
		}
	}

	if params.KindPrimary != nil {
		if *params.KindPrimary {
			if err := s.repo.SetPrimary(ctx, bundle); err != nil {
				return nil, err
			}
		} else if bundle.KindPrimary {
			if err := s.repo.Update(ctx, bundle, map[string]interface{}{"kind_primary": false}); err != nil {
				return nil, err
			}
		}
	}

	return s.repo.GetByID(ctx, id)
}

// Delete removes a bundle owned by (scope, ownerID).
func (s *Service) Delete(ctx context.Context, ownerScope string, ownerID, id int64) error {
	bundle, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return err
	}
	if bundle == nil || bundle.OwnerScope != ownerScope || bundle.OwnerID != ownerID {
		return ErrNotFound
	}
	rows, err := s.repo.Delete(ctx, id)
	if err != nil {
		return err
	}
	if rows == 0 {
		return ErrNotFound
	}
	return nil
}

// Get returns a bundle owned by (scope, ownerID).
func (s *Service) Get(ctx context.Context, ownerScope string, ownerID, id int64) (*envbundle.EnvBundle, error) {
	bundle, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if bundle == nil || bundle.OwnerScope != ownerScope || bundle.OwnerID != ownerID {
		return nil, ErrNotFound
	}
	return bundle, nil
}

// SetPrimary marks a bundle as the primary in its (owner, agent_slug, kind)
// group. Clears any existing primary in that group atomically.
func (s *Service) SetPrimary(ctx context.Context, ownerScope string, ownerID, id int64) (*envbundle.EnvBundle, error) {
	bundle, err := s.Get(ctx, ownerScope, ownerID, id)
	if err != nil {
		return nil, err
	}
	if err := s.repo.SetPrimary(ctx, bundle); err != nil {
		return nil, err
	}
	return s.repo.GetByID(ctx, id)
}

// List returns bundles owned by (scope, ownerID), optionally filtered.
func (s *Service) List(ctx context.Context, f envbundle.OwnerFilter) ([]*envbundle.EnvBundle, error) {
	return s.repo.List(ctx, f)
}

// ResponseWithValues builds a Response and fills exactly one of
// ConfiguredFields / ConfiguredValues:
//   - encrypted kinds (credential): ConfiguredFields = key names, no values
//   - plaintext kinds (runtime/shared): ConfiguredValues = decrypted KV map
//
// The two slots are disjoint by construction; callers never need to reconcile
// "fields == keys(values)" duplication.
func (s *Service) ResponseWithValues(bundle *envbundle.EnvBundle) (*envbundle.Response, error) {
	resp := bundle.ToResponse()
	if envbundle.IsEncryptedKind(bundle.Kind) {
		if len(bundle.Data) > 0 {
			fields := make([]string, 0, len(bundle.Data))
			for k := range bundle.Data {
				fields = append(fields, k)
			}
			resp.ConfiguredFields = fields
		}
		return resp, nil
	}
	dec, err := s.decryptData(bundle.Kind, bundle.Data)
	if err != nil {
		return resp, err
	}
	if len(dec) > 0 {
		resp.ConfiguredValues = dec
	}
	return resp, nil
}

func validScope(s string) bool {
	return s == envbundle.OwnerScopeUser || s == envbundle.OwnerScopeOrg
}
