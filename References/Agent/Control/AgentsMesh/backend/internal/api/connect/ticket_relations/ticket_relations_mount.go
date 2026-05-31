package ticketrelationsconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	ticketservice "github.com/anthropics/agentsmesh/backend/internal/service/ticket"
)

// mapServiceError mirrors REST's handler-by-handler `apierr` mapping
// (ticket_relations.go / ticket_comments.go / ticket_commits.go). Translates
// ticket-domain sentinels to Connect codes per conventions §10.
func mapServiceError(err error) error {
	if err == nil {
		return nil
	}
	switch {
	case errors.Is(err, ticketservice.ErrTicketNotFound),
		errors.Is(err, ticketservice.ErrCommentNotFound),
		errors.Is(err, ticketservice.ErrRelationNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, ticketservice.ErrUnauthorizedComment):
		return connect.NewError(connect.CodePermissionDenied, err)
	case errors.Is(err, ticketservice.ErrSelfRelation):
		return connect.NewError(connect.CodeInvalidArgument, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}

// Mount registers all TicketRelationsService procedures on mux behind the
// auth interceptor supplied via opts (see cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListRelationsProcedure, connect.NewUnaryHandler(
		ListRelationsProcedure, srv.ListRelations, opts...,
	))
	mux.Handle(CreateRelationProcedure, connect.NewUnaryHandler(
		CreateRelationProcedure, srv.CreateRelation, opts...,
	))
	mux.Handle(DeleteRelationProcedure, connect.NewUnaryHandler(
		DeleteRelationProcedure, srv.DeleteRelation, opts...,
	))
	mux.Handle(ListMergeRequestsProcedure, connect.NewUnaryHandler(
		ListMergeRequestsProcedure, srv.ListMergeRequests, opts...,
	))
	mux.Handle(ListCommitsProcedure, connect.NewUnaryHandler(
		ListCommitsProcedure, srv.ListCommits, opts...,
	))
	mux.Handle(LinkCommitProcedure, connect.NewUnaryHandler(
		LinkCommitProcedure, srv.LinkCommit, opts...,
	))
	mux.Handle(UnlinkCommitProcedure, connect.NewUnaryHandler(
		UnlinkCommitProcedure, srv.UnlinkCommit, opts...,
	))
	mux.Handle(ListCommentsProcedure, connect.NewUnaryHandler(
		ListCommentsProcedure, srv.ListComments, opts...,
	))
	mux.Handle(CreateCommentProcedure, connect.NewUnaryHandler(
		CreateCommentProcedure, srv.CreateComment, opts...,
	))
	mux.Handle(UpdateCommentProcedure, connect.NewUnaryHandler(
		UpdateCommentProcedure, srv.UpdateComment, opts...,
	))
	mux.Handle(DeleteCommentProcedure, connect.NewUnaryHandler(
		DeleteCommentProcedure, srv.DeleteComment, opts...,
	))
}
