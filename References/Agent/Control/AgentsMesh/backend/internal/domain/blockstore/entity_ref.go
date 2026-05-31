package blockstore

import (
	"time"

	"github.com/google/uuid"
)

// BlockRef is the SINGLE relationship primitive. `rel` differentiates semantics:
//   - nest      : structural containment (from = container, to = child); unique per `to_id`
//   - mention   : @-style reference inside from's text
//   - embed     : from renders to at a slot
//   - depends_on: task graph dependency
//   - (extensible by business)
//
// order_key (fractional index) is used only for ordered rels such as `nest`.
//
// UpdatedAt tracks the last mutation to from_id / order_key / anchor / meta
// (service-layer UpdateRef refreshes it). It stays equal to CreatedAt for
// refs that are only ever inserted then deleted.
type BlockRef struct {
	ID          int64     `gorm:"primaryKey" json:"id"`
	WorkspaceID uuid.UUID `gorm:"type:uuid;not null;index" json:"workspace_id"`
	FromID      uuid.UUID `gorm:"type:uuid;not null;index" json:"from_id"`
	ToID        uuid.UUID `gorm:"type:uuid;not null;index" json:"to_id"`
	Rel         string    `gorm:"size:64;not null" json:"rel"`
	OrderKey    *string   `gorm:"type:text" json:"order_key,omitempty"`
	Anchor      *string   `gorm:"type:text" json:"anchor,omitempty"`
	Meta        JSONMap   `gorm:"type:jsonb;not null;default:'{}'" json:"meta"`
	CreatedBy   int64     `gorm:"not null" json:"created_by"`
	CreatedAt   time.Time `gorm:"not null;default:current_timestamp" json:"created_at"`
	UpdatedAt   time.Time `gorm:"not null;default:current_timestamp" json:"updated_at"`
}

func (BlockRef) TableName() string {
	return "block_refs"
}
