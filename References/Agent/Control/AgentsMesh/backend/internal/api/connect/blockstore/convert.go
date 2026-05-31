package blockstoreconnect

import (
	"context"
	"encoding/json"
	"time"

	"connectrpc.com/connect"
	"go.opentelemetry.io/otel/trace"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	blockstoreservice "github.com/anthropics/agentsmesh/backend/internal/service/blockstore"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

// actorFromCtx mirrors REST's actorFrom (blockstore_handler.go:36). At the
// Connect path the tenant context is already populated by ResolveOrgScope; we
// add the OTel trace id so audit metadata in BlockOp.Context lines up across
// transports (matches REST's traceIDFromContext).
func actorFromCtx(ctx context.Context, req connect.AnyRequest) blockstoreservice.ActorContext {
	tenant := middleware.GetTenant(ctx)
	traceID := ""
	if sc := trace.SpanContextFromContext(ctx); sc.IsValid() {
		traceID = sc.TraceID().String()
	}
	actor := blockstoreservice.ActorContext{
		UserID:    tenant.UserID,
		OrgID:     tenant.OrganizationID,
		ActorType: blockstore.ActorUser,
		ActorID:   tenant.UserID,
		TraceID:   traceID,
		RequestID: traceID,
	}
	// User-Agent and X-Forwarded-For are best-effort — Connect surfaces them
	// via the request header (req.Header()) when present.
	if req != nil {
		actor.UserAgent = req.Header().Get("User-Agent")
		// Prefer the canonical Forwarded chain, fall back to X-Forwarded-For
		// then the directly connected peer the connect handler exposes via
		// the X-Real-IP header (the auth middleware doesn't currently set it).
		if ip := req.Header().Get("X-Forwarded-For"); ip != "" {
			actor.IP = ip
		} else if ip := req.Header().Get("X-Real-IP"); ip != "" {
			actor.IP = ip
		}
	}
	return actor
}

// jsonMapToString serialises a JSONMap to a JSON-encoded string for the wire.
// Errors fall back to "{}" — the audit slot must stay parseable on the
// client; a malformed jsonmap would have failed db serialisation upstream.
func jsonMapToString(m blockstore.JSONMap) string {
	if m == nil {
		return "{}"
	}
	b, err := json.Marshal(m)
	if err != nil {
		return "{}"
	}
	return string(b)
}

func toProtoBlock(b *blockstore.Block) *blockstorev1.Block {
	if b == nil {
		return nil
	}
	out := &blockstorev1.Block{
		Id:          b.ID.String(),
		WorkspaceId: b.WorkspaceID.String(),
		Type:        b.Type,
		DataJson:    jsonMapToString(b.Data),
		MetaJson:    jsonMapToString(b.Meta),
		CreatedBy:   b.CreatedBy,
		CreatedAt:   b.CreatedAt.UTC().Format(time.RFC3339Nano),
		UpdatedAt:   b.UpdatedAt.UTC().Format(time.RFC3339Nano),
	}
	if b.Text != nil {
		s := *b.Text
		out.Text = &s
	}
	if b.DeletedAt != nil {
		s := b.DeletedAt.UTC().Format(time.RFC3339Nano)
		out.DeletedAt = &s
	}
	return out
}

func toProtoRef(r *blockstore.BlockRef) *blockstorev1.BlockRef {
	if r == nil {
		return nil
	}
	out := &blockstorev1.BlockRef{
		Id:          r.ID,
		WorkspaceId: r.WorkspaceID.String(),
		FromId:      r.FromID.String(),
		ToId:        r.ToID.String(),
		Rel:         r.Rel,
		MetaJson:    jsonMapToString(r.Meta),
		CreatedBy:   r.CreatedBy,
		CreatedAt:   r.CreatedAt.UTC().Format(time.RFC3339Nano),
		UpdatedAt:   r.UpdatedAt.UTC().Format(time.RFC3339Nano),
	}
	if r.OrderKey != nil {
		s := *r.OrderKey
		out.OrderKey = &s
	}
	if r.Anchor != nil {
		s := *r.Anchor
		out.Anchor = &s
	}
	return out
}

func toProtoOp(o *blockstore.BlockOp) *blockstorev1.BlockOp {
	if o == nil {
		return nil
	}
	out := &blockstorev1.BlockOp{
		Id:          o.ID,
		WorkspaceId: o.WorkspaceID.String(),
		ActorType:   o.ActorType,
		ActorId:     o.ActorID,
		Op:          o.Op,
		PayloadJson: jsonMapToString(o.Payload),
		ForwardJson: jsonMapToString(o.Forward),
		InverseJson: jsonMapToString(o.Inverse),
		ContextJson: jsonMapToString(o.Context),
		AppliedAt:   o.AppliedAt.UTC().Format(time.RFC3339Nano),
	}
	if o.IdempotencyKey != nil {
		s := *o.IdempotencyKey
		out.IdempotencyKey = &s
	}
	if o.TargetBlock != nil {
		s := o.TargetBlock.String()
		out.TargetBlock = &s
	}
	if o.TargetRef != nil {
		v := *o.TargetRef
		out.TargetRef = &v
	}
	if o.ParentOpID != nil {
		v := *o.ParentOpID
		out.ParentOpId = &v
	}
	return out
}

func toProtoWorkspaceView(w blockstoreservice.WorkspaceView) *blockstorev1.Workspace {
	out := &blockstorev1.Workspace{
		Id:             w.ID.String(),
		OrganizationId: w.OrganizationID,
		Slug:           w.Slug,
		Name:           w.Name,
		CreatedAt:      w.CreatedAt.UTC().Format(time.RFC3339),
	}
	if w.RootBlockID != nil {
		s := w.RootBlockID.String()
		out.RootBlockId = &s
	}
	return out
}
