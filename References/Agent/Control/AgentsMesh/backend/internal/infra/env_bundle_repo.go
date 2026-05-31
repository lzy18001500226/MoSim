package infra

import (
	"context"

	"github.com/anthropics/agentsmesh/backend/internal/domain/envbundle"
	"gorm.io/gorm"
)

var _ envbundle.Repository = (*envBundleRepo)(nil)

type envBundleRepo struct {
	db *gorm.DB
}

// NewEnvBundleRepository creates a GORM-backed EnvBundle repository.
func NewEnvBundleRepository(db *gorm.DB) envbundle.Repository {
	return &envBundleRepo{db: db}
}

func (r *envBundleRepo) Create(ctx context.Context, bundle *envbundle.EnvBundle) error {
	return r.db.WithContext(ctx).Create(bundle).Error
}

// CreateWithPrimary inserts the bundle and atomically promotes it to primary
// within its (owner_scope, owner_id, agent_slug, kind) group, demoting any
// existing primary in the same group. Both writes share one transaction so
// the unique-index invariant (at most one primary per group) is never
// momentarily violated mid-write.
func (r *envBundleRepo) CreateWithPrimary(ctx context.Context, bundle *envbundle.EnvBundle) error {
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		bundle.KindPrimary = false
		if err := tx.Create(bundle).Error; err != nil {
			return err
		}
		if err := clearPrimariesInGroup(tx, bundle, true); err != nil {
			return err
		}
		if err := tx.Model(bundle).Update("kind_primary", true).Error; err != nil {
			return err
		}
		bundle.KindPrimary = true
		return nil
	})
}

// clearPrimariesInGroup demotes any existing primary in the
// (owner_scope, owner_id, agent_slug, kind) group of the given bundle.
// When excludeSelf is true the bundle's own row is left alone (used by the
// post-insert promotion path in CreateWithPrimary).
func clearPrimariesInGroup(tx *gorm.DB, bundle *envbundle.EnvBundle, excludeSelf bool) error {
	q := tx.Model(&envbundle.EnvBundle{}).
		Where("owner_scope = ? AND owner_id = ? AND kind = ? AND kind_primary = ?",
			bundle.OwnerScope, bundle.OwnerID, bundle.Kind, true)
	if excludeSelf && bundle.ID != 0 {
		q = q.Where("id <> ?", bundle.ID)
	}
	if bundle.AgentSlug == nil {
		q = q.Where("agent_slug IS NULL")
	} else {
		q = q.Where("agent_slug = ?", *bundle.AgentSlug)
	}
	return q.Update("kind_primary", false).Error
}

func (r *envBundleRepo) GetByID(ctx context.Context, id int64) (*envbundle.EnvBundle, error) {
	var bundle envbundle.EnvBundle
	err := r.db.WithContext(ctx).Where("id = ?", id).First(&bundle).Error
	if err == gorm.ErrRecordNotFound {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	return &bundle, nil
}

func (r *envBundleRepo) GetByName(ctx context.Context, ownerScope string, ownerID int64, name string) (*envbundle.EnvBundle, error) {
	var bundle envbundle.EnvBundle
	err := r.db.WithContext(ctx).
		Where("owner_scope = ? AND owner_id = ? AND name = ?", ownerScope, ownerID, name).
		First(&bundle).Error
	if err == gorm.ErrRecordNotFound {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	return &bundle, nil
}

func (r *envBundleRepo) Update(ctx context.Context, bundle *envbundle.EnvBundle, updates map[string]interface{}) error {
	return r.db.WithContext(ctx).Model(bundle).Updates(updates).Error
}

func (r *envBundleRepo) Delete(ctx context.Context, id int64) (int64, error) {
	result := r.db.WithContext(ctx).Where("id = ?", id).Delete(&envbundle.EnvBundle{})
	return result.RowsAffected, result.Error
}

func (r *envBundleRepo) List(ctx context.Context, f envbundle.OwnerFilter) ([]*envbundle.EnvBundle, error) {
	q := r.db.WithContext(ctx).Model(&envbundle.EnvBundle{}).
		Where("owner_scope = ? AND owner_id = ? AND is_active = ?", f.OwnerScope, f.OwnerID, true)

	if f.Kind != "" {
		q = q.Where("kind = ?", f.Kind)
	}
	if f.AgentSlug != nil {
		if *f.AgentSlug == "" {
			q = q.Where("agent_slug IS NULL")
		} else {
			q = q.Where("agent_slug = ?", *f.AgentSlug)
		}
	}

	var bundles []*envbundle.EnvBundle
	if err := q.Order("kind, agent_slug NULLS FIRST, kind_primary DESC, name").Find(&bundles).Error; err != nil {
		return nil, err
	}
	return bundles, nil
}

func (r *envBundleRepo) ListEffectiveForUser(ctx context.Context, userID, orgID int64, agentSlug string) ([]*envbundle.EnvBundle, error) {
	q := r.db.WithContext(ctx).Model(&envbundle.EnvBundle{}).
		Where("is_active = ?", true)

	if orgID > 0 {
		q = q.Where(
			r.db.Where("owner_scope = ? AND owner_id = ?", envbundle.OwnerScopeUser, userID).
				Or("owner_scope = ? AND owner_id = ?", envbundle.OwnerScopeOrg, orgID),
		)
	} else {
		q = q.Where("owner_scope = ? AND owner_id = ?", envbundle.OwnerScopeUser, userID)
	}

	if agentSlug != "" {
		q = q.Where("agent_slug = ? OR agent_slug IS NULL", agentSlug)
	}

	var bundles []*envbundle.EnvBundle
	if err := q.Order("owner_scope, kind, name").Find(&bundles).Error; err != nil {
		return nil, err
	}
	return bundles, nil
}

func (r *envBundleRepo) SetPrimary(ctx context.Context, bundle *envbundle.EnvBundle) error {
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		if err := clearPrimariesInGroup(tx, bundle, false); err != nil {
			return err
		}
		return tx.Model(bundle).Update("kind_primary", true).Error
	})
}

func (r *envBundleRepo) NameExists(ctx context.Context, ownerScope string, ownerID int64, name string, excludeID *int64) (bool, error) {
	q := r.db.WithContext(ctx).Model(&envbundle.EnvBundle{}).
		Where("owner_scope = ? AND owner_id = ? AND name = ?", ownerScope, ownerID, name)
	if excludeID != nil {
		q = q.Where("id != ?", *excludeID)
	}
	var count int64
	err := q.Count(&count).Error
	return count > 0, err
}
