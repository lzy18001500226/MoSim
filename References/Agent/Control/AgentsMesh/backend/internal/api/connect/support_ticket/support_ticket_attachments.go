package supportticketconnect

import (
	"context"
	"errors"
	"log/slog"

	"connectrpc.com/connect"

	supportticketsvc "github.com/anthropics/agentsmesh/backend/internal/service/supportticket"
	supportticketv1 "github.com/anthropics/agentsmesh/proto/gen/go/support_ticket/v1"
)

// CreateSupportTicket creates a new ticket without any attachments. Files
// follow up via PresignAttachmentUpload + AssociateAttachments — see proto
// schema header for the 3-step flow rationale.
func (s *Server) CreateSupportTicket(
	ctx context.Context, req *connect.Request[supportticketv1.CreateSupportTicketRequest],
) (*connect.Response[supportticketv1.SupportTicket], error) {
	userID, err := userIDFromCtx(ctx)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetTitle() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("title is required"))
	}
	if req.Msg.GetContent() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("content is required"))
	}
	ticket, err := s.svc.Create(ctx, userID, &supportticketsvc.CreateRequest{
		Title:    req.Msg.GetTitle(),
		Category: req.Msg.GetCategory(),
		Content:  req.Msg.GetContent(),
		Priority: req.Msg.GetPriority(),
	})
	if err != nil {
		return nil, mapSupportTicketError(err)
	}
	return connect.NewResponse(ToProtoSupportTicket(ticket)), nil
}

// AddSupportTicketMessage appends a user message to an existing ticket.
// Returns the new message; ownership is enforced by the service layer.
func (s *Server) AddSupportTicketMessage(
	ctx context.Context, req *connect.Request[supportticketv1.AddSupportTicketMessageRequest],
) (*connect.Response[supportticketv1.SupportTicketMessage], error) {
	userID, err := userIDFromCtx(ctx)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetTicketId() == 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("ticket_id is required"))
	}
	if req.Msg.GetContent() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("content is required"))
	}
	msg, err := s.svc.AddMessage(ctx, req.Msg.GetTicketId(), userID, &supportticketsvc.AddMessageRequest{
		Content: req.Msg.GetContent(),
	})
	if err != nil {
		return nil, mapSupportTicketError(err)
	}
	return connect.NewResponse(ToProtoSupportTicketMessage(msg)), nil
}

// PresignAttachmentUpload returns a presigned PUT URL + opaque storage_key.
// The browser PUTs the bytes directly to put_url, then hands storage_key
// back via AssociateAttachments to materialize the DB row.
func (s *Server) PresignAttachmentUpload(
	ctx context.Context, req *connect.Request[supportticketv1.PresignAttachmentUploadRequest],
) (*connect.Response[supportticketv1.PresignAttachmentUploadResponse], error) {
	userID, err := userIDFromCtx(ctx)
	if err != nil {
		return nil, err
	}
	if err := validatePresignReq(req.Msg); err != nil {
		return nil, err
	}
	presignReq := &supportticketsvc.PresignAttachmentRequest{
		TicketID:    req.Msg.GetTicketId(),
		FileName:    req.Msg.GetFilename(),
		ContentType: req.Msg.GetContentType(),
		Size:        req.Msg.GetSize(),
	}
	if req.Msg.MessageId != nil {
		mid := req.Msg.GetMessageId()
		presignReq.MessageID = &mid
	}
	resp, err := s.svc.PresignAttachment(ctx, userID, presignReq)
	if err != nil {
		return nil, mapSupportTicketError(err)
	}
	return connect.NewResponse(&supportticketv1.PresignAttachmentUploadResponse{
		PutUrl:     resp.PutURL,
		StorageKey: resp.StorageKey,
	}), nil
}

// AssociateAttachments verifies each upload landed in storage and creates
// the DB rows. Batched so the client makes one round-trip after PUTting all
// files. Returns the materialized SupportTicketAttachment rows.
func (s *Server) AssociateAttachments(
	ctx context.Context, req *connect.Request[supportticketv1.AssociateAttachmentsRequest],
) (*connect.Response[supportticketv1.AssociateAttachmentsResponse], error) {
	userID, err := userIDFromCtx(ctx)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetTicketId() == 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("ticket_id is required"))
	}
	out := make([]*supportticketv1.SupportTicketAttachment, 0, len(req.Msg.GetAttachments()))
	for _, ref := range req.Msg.GetAttachments() {
		if ref.GetStorageKey() == "" {
			slog.WarnContext(ctx, "skipping attachment association: empty storage_key",
				"ticket_id", req.Msg.GetTicketId())
			continue
		}
		assocReq := &supportticketsvc.AssociateAttachmentRequest{
			StorageKey:  ref.GetStorageKey(),
			FileName:    ref.GetFilename(),
			ContentType: ref.GetContentType(),
			Size:        ref.GetSize(),
		}
		if ref.MessageId != nil {
			mid := ref.GetMessageId()
			assocReq.MessageID = &mid
		}
		att, err := s.svc.AssociateAttachment(ctx, req.Msg.GetTicketId(), userID, assocReq)
		if err != nil {
			return nil, mapSupportTicketError(err)
		}
		out = append(out, ToProtoSupportTicketAttachment(att))
	}
	return connect.NewResponse(&supportticketv1.AssociateAttachmentsResponse{
		Items: out,
	}), nil
}

func validatePresignReq(req *supportticketv1.PresignAttachmentUploadRequest) error {
	if req.GetTicketId() == 0 {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("ticket_id is required"))
	}
	if req.GetFilename() == "" {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("filename is required"))
	}
	if req.GetContentType() == "" {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("content_type is required"))
	}
	if req.GetSize() <= 0 {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("size must be > 0"))
	}
	return nil
}
