// Package fileconnect hosts Connect-RPC handlers for the file service.
// Mirrors backend/internal/api/rest/v1/files.go but exposes the
// presigned-URL RPC via Connect (binary protobuf wire, conventions §2.5).
// REST stays mounted in parallel during the dual-track migration window.
//
// Only the JSON-bodied presign RPC moves to Connect — the actual S3 PUT
// is a direct browser → S3 upload (no proxy).
package fileconnect

import (
	"context"
	"errors"
	"log/slog"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	fileservice "github.com/anthropics/agentsmesh/backend/internal/service/file"
	filev1 "github.com/anthropics/agentsmesh/proto/gen/go/file/v1"
)

const ServiceName = "proto.file.v1.FileService"

const PresignUploadProcedure = "/" + ServiceName + "/PresignUpload"

// FileServiceInterface mirrors the REST FileServiceInterface (v1/files.go:16)
// — keeps the dual-track wiring shareable.
type FileServiceInterface interface {
	RequestPresignedUpload(ctx context.Context, req *fileservice.PresignUploadRequest) (*fileservice.PresignUploadResponse, error)
}

type Server struct {
	svc    FileServiceInterface
	orgSvc middleware.OrganizationService
}

func NewServer(svc FileServiceInterface, orgSvc middleware.OrganizationService) *Server {
	return &Server{svc: svc, orgSvc: orgSvc}
}

func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(PresignUploadProcedure, connect.NewUnaryHandler(
		PresignUploadProcedure, srv.PresignUpload, opts...,
	))
}

// PresignUpload — REST analogue: POST /api/v1/orgs/:slug/files/presign.
// Returns put_url + get_url. Service-layer enforces max file size and
// content-type allow-list.
func (s *Server) PresignUpload(
	ctx context.Context, req *connect.Request[filev1.PresignUploadRequest],
) (*connect.Response[filev1.PresignUploadResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if s.svc == nil {
		return nil, connect.NewError(connect.CodeUnavailable, errors.New("storage not configured"))
	}
	if req.Msg.GetFilename() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("filename is required"))
	}
	if req.Msg.GetContentType() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("content_type is required"))
	}
	if req.Msg.GetSize() <= 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("size must be > 0"))
	}

	tenant := middleware.GetTenant(ctx)
	resp, err := s.svc.RequestPresignedUpload(ctx, &fileservice.PresignUploadRequest{
		OrganizationID: tenant.OrganizationID,
		FileName:       req.Msg.GetFilename(),
		ContentType:    req.Msg.GetContentType(),
		Size:           req.Msg.GetSize(),
	})
	if err != nil {
		return nil, mapFileError(ctx, err, req.Msg)
	}
	return connect.NewResponse(&filev1.PresignUploadResponse{
		PutUrl: resp.PutURL,
		GetUrl: resp.GetURL,
	}), nil
}

// mapFileError translates fileservice sentinels to Connect codes per
// conventions §10. Mirrors REST PresignUpload's error switch.
func mapFileError(ctx context.Context, err error, req *filev1.PresignUploadRequest) error {
	switch {
	case errors.Is(err, fileservice.ErrFileTooLarge):
		return connect.NewError(connect.CodeResourceExhausted, err)
	case errors.Is(err, fileservice.ErrInvalidFileType):
		slog.WarnContext(ctx, "Presign upload rejected: invalid type",
			"content_type", req.GetContentType(),
			"filename", req.GetFilename(),
		)
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, fileservice.ErrStorageError):
		slog.ErrorContext(ctx, "Presign upload failed: storage error",
			"error", err, "filename", req.GetFilename(),
		)
		return connect.NewError(connect.CodeUnavailable, err)
	default:
		slog.ErrorContext(ctx, "Presign upload failed",
			"error", err, "filename", req.GetFilename(),
		)
		return connect.NewError(connect.CodeInternal, err)
	}
}
