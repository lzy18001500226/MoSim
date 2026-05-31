package blockstoreinfra

import (
	"context"
	"errors"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

func (w *txWriter) InsertBlock(ctx context.Context, b *blockstore.Block) error {
	if b.WorkspaceID == uuid.Nil {
		b.WorkspaceID = w.workspaceID
	}
	return w.tx.WithContext(ctx).Create(b).Error
}

func (w *txWriter) UpdateBlockFields(ctx context.Context, id uuid.UUID, fields map[string]any) error {
	if _, has := fields["updated_at"]; !has {
		fields["updated_at"] = gorm.Expr("CURRENT_TIMESTAMP")
	}
	res := w.tx.WithContext(ctx).
		Model(&blockstore.Block{}).
		Where("id = ? AND deleted_at IS NULL", id).
		Updates(fields)
	if res.Error != nil {
		return res.Error
	}
	if res.RowsAffected == 0 {
		return blockstore.ErrBlockNotFound
	}
	return nil
}

func (w *txWriter) SoftDeleteBlock(ctx context.Context, id uuid.UUID) error {
	res := w.tx.WithContext(ctx).
		Model(&blockstore.Block{}).
		Where("id = ? AND deleted_at IS NULL", id).
		Update("deleted_at", gorm.Expr("CURRENT_TIMESTAMP"))
	if res.Error != nil {
		return res.Error
	}
	if res.RowsAffected == 0 {
		return blockstore.ErrBlockNotFound
	}
	return nil
}

func (w *txWriter) FindBlockByID(ctx context.Context, id uuid.UUID) (*blockstore.Block, error) {
	var b blockstore.Block
	err := w.tx.WithContext(ctx).Where("id = ?", id).First(&b).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, blockstore.ErrBlockNotFound
		}
		return nil, err
	}
	return &b, nil
}
