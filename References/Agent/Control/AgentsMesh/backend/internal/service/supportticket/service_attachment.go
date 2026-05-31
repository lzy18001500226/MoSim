package supportticket

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"path"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/domain/supportticket"
	"github.com/google/uuid"
)

// UploadAttachment uploads a file attachment and associates it with a ticket/message.
// Admin path retains this single-shot flow (admin upload goes through REST today).
// User-side flow is split into PresignAttachmentUpload + AssociateAttachment.
func (s *Service) UploadAttachment(ctx context.Context, ticketID, userID int64, messageID *int64, isAdmin bool, req *UploadAttachmentRequest) (*supportticket.SupportTicketAttachment, error) {
	if s.storage == nil {
		return nil, ErrStorageError
	}

	ticket, err := s.repo.GetTicketByID(ctx, ticketID)
	if err != nil {
		return nil, err
	}
	if ticket == nil {
		return nil, ErrTicketNotFound
	}
	if ticket.UserID != userID && !isAdmin {
		return nil, ErrAccessDenied
	}

	if err := s.enforceMaxSize(req.Size); err != nil {
		return nil, err
	}

	storageKey := s.newAttachmentKey(userID, req.FileName)
	if _, err := s.storage.Upload(ctx, storageKey, req.Reader, req.Size, req.ContentType); err != nil {
		return nil, fmt.Errorf("%w: %v", ErrStorageError, err)
	}

	attachment, err := s.persistAttachment(ctx, ticketID, userID, messageID, storageKey, req.FileName, req.ContentType, req.Size)
	if err != nil {
		if delErr := s.storage.Delete(ctx, storageKey); delErr != nil {
			slog.WarnContext(ctx, "failed to cleanup uploaded file after DB error", "storage_key", storageKey, "error", delErr)
		}
		return nil, err
	}
	return attachment, nil
}

// PresignAttachmentRequest carries the metadata needed to mint a presigned
// PUT URL. The caller already created the ticket/message via Connect; this
// step only authorizes the upload + reserves an opaque storage key.
type PresignAttachmentRequest struct {
	TicketID    int64
	MessageID   *int64
	FileName    string
	ContentType string
	Size        int64
}

// PresignAttachmentResponse is the presign output. storage_key is opaque to
// the caller — they hand it back unchanged to AssociateAttachment.
type PresignAttachmentResponse struct {
	PutURL     string
	StorageKey string
}

// PresignAttachment authorizes an upload + mints a presigned PUT URL. No
// storage write yet — the browser PUTs directly to put_url, then calls
// AssociateAttachment to materialize the DB row.
func (s *Service) PresignAttachment(ctx context.Context, userID int64, req *PresignAttachmentRequest) (*PresignAttachmentResponse, error) {
	if s.storage == nil {
		return nil, ErrStorageError
	}
	ticket, err := s.repo.GetTicketByID(ctx, req.TicketID)
	if err != nil {
		return nil, err
	}
	if ticket == nil {
		return nil, ErrTicketNotFound
	}
	if ticket.UserID != userID {
		return nil, ErrAccessDenied
	}
	if err := s.enforceMaxSize(req.Size); err != nil {
		return nil, err
	}

	storageKey := s.newAttachmentKey(userID, req.FileName)
	putURL, err := s.storage.PresignPutURL(ctx, storageKey, req.ContentType, 15*time.Minute)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrStorageError, err)
	}
	return &PresignAttachmentResponse{PutURL: putURL, StorageKey: storageKey}, nil
}

// AssociateAttachmentRequest mirrors the per-file body of the Connect
// AssociateAttachments batch.
type AssociateAttachmentRequest struct {
	StorageKey  string
	FileName    string
	ContentType string
	Size        int64
	MessageID   *int64
}

// AssociateAttachment verifies the upload landed in storage and creates the
// DB row. Returns ErrAttachmentNotFound when the storage_key is missing — the
// browser PUT likely failed.
func (s *Service) AssociateAttachment(ctx context.Context, ticketID, userID int64, req *AssociateAttachmentRequest) (*supportticket.SupportTicketAttachment, error) {
	if s.storage == nil {
		return nil, ErrStorageError
	}
	ticket, err := s.repo.GetTicketByID(ctx, ticketID)
	if err != nil {
		return nil, err
	}
	if ticket == nil {
		return nil, ErrTicketNotFound
	}
	if ticket.UserID != userID {
		return nil, ErrAccessDenied
	}
	exists, err := s.storage.Exists(ctx, req.StorageKey)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", ErrStorageError, err)
	}
	if !exists {
		return nil, ErrAttachmentNotFound
	}
	return s.persistAttachment(ctx, ticketID, userID, req.MessageID, req.StorageKey, req.FileName, req.ContentType, req.Size)
}

// GetAttachmentURL returns a presigned URL for downloading an attachment
func (s *Service) GetAttachmentURL(ctx context.Context, attachmentID, userID int64) (string, error) {
	if s.storage == nil {
		return "", ErrStorageError
	}

	attachment, err := s.repo.GetAttachmentByID(ctx, attachmentID)
	if err != nil {
		return "", err
	}
	if attachment == nil {
		return "", ErrAttachmentNotFound
	}

	ticket, err := s.repo.GetTicketByID(ctx, attachment.TicketID)
	if err != nil {
		return "", err
	}
	if ticket == nil {
		return "", ErrTicketNotFound
	}
	if ticket.UserID != userID {
		return "", ErrAccessDenied
	}

	return s.storage.GetURL(ctx, attachment.StorageKey, 1*time.Hour)
}

func (s *Service) enforceMaxSize(size int64) error {
	maxSize := s.config.MaxFileSize * 1024 * 1024
	if maxSize <= 0 {
		maxSize = 10 * 1024 * 1024
	}
	if size > maxSize {
		return ErrFileTooLarge
	}
	return nil
}

func (s *Service) newAttachmentKey(userID int64, fileName string) string {
	ext := path.Ext(fileName)
	if ext == "" {
		ext = ".bin"
	}
	now := time.Now()
	return fmt.Sprintf("support-tickets/%d/%d/%02d/%s%s",
		userID, now.Year(), now.Month(), uuid.New().String(), ext)
}

func (s *Service) persistAttachment(
	ctx context.Context,
	ticketID, userID int64,
	messageID *int64,
	storageKey, fileName, contentType string,
	size int64,
) (*supportticket.SupportTicketAttachment, error) {
	attachment := &supportticket.SupportTicketAttachment{
		TicketID:     ticketID,
		MessageID:    messageID,
		UploaderID:   userID,
		OriginalName: fileName,
		StorageKey:   storageKey,
		MimeType:     contentType,
		Size:         size,
	}
	if err := s.repo.CreateAttachment(ctx, attachment); err != nil {
		return nil, fmt.Errorf("failed to create attachment record: %w", err)
	}
	return attachment, nil
}

// io.Reader is still referenced by UploadAttachmentRequest above; keep it
// imported so the admin path compiles.
var _ io.Reader = (io.Reader)(nil)
