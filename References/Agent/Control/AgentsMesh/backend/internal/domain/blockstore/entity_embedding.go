package blockstore

import (
	"time"

	"github.com/google/uuid"
)

// BlockEmbedding persists the vector representation of a block's text
// summary. Separate from the blocks row so the vector shape / model can
// evolve without rewriting block history.
//
// IMPORTANT: the vector itself (JSONB `vector` and, when pgvector is
// available, `vec vector(D)`) is never read or written through GORM struct
// mapping — the repo layer uses raw SQL with `[]float32` for both JSON and
// pgvector text-literal paths. This struct exists purely as a schema anchor
// for GORM AutoMigrate and as a soft-delete target (`DeleteEmbedding`).
type BlockEmbedding struct {
	BlockID    uuid.UUID `gorm:"type:uuid;primaryKey" json:"block_id"`
	Model      string    `gorm:"size:64;not null" json:"model"`
	Dims       int       `gorm:"not null" json:"dims"`
	SourceHash string    `gorm:"size:64;not null" json:"source_hash"`
	CreatedAt  time.Time `gorm:"not null;default:current_timestamp" json:"created_at"`
	UpdatedAt  time.Time `gorm:"not null;default:current_timestamp" json:"updated_at"`
}

func (BlockEmbedding) TableName() string {
	return "block_embeddings"
}
