package blockstoreconnect

import (
	"context"
	"encoding/json"
	"fmt"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	blockstoreservice "github.com/anthropics/agentsmesh/backend/internal/service/blockstore"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

// ApplyOps runs a batch of primitive ops. Mirrors REST POST /blocks/ops with
// the {workspace_id, ops[], idempotency_key?, parent_op_id?} body. Each op's
// payload arrives as an opaque JSON string and is parsed into the service
// layer's `map[string]any` Payload — matches today's REST shape.
func (s *Server) ApplyOps(
	ctx context.Context, req *connect.Request[blockstorev1.ApplyOpsRequest],
) (*connect.Response[blockstorev1.ApplyOpsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}

	in, err := applyOpsInputFromProto(req.Msg)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	actor := actorFromCtx(ctx, req)

	res, err := s.svc.ApplyOps(ctx, actor, in)
	if err != nil {
		return nil, translateErr(err)
	}
	out := &blockstorev1.ApplyOpsResponse{
		OpIds:     res.OpIDs,
		WasReplay: res.WasReplay,
	}
	if res.ParentOpID != nil {
		v := *res.ParentOpID
		out.ParentOpId = &v
	}
	return connect.NewResponse(out), nil
}

func applyOpsInputFromProto(req *blockstorev1.ApplyOpsRequest) (blockstoreservice.ApplyOpsInput, error) {
	envs := make([]blockstoreservice.OpEnvelope, 0, len(req.GetOps()))
	for i, env := range req.GetOps() {
		if env == nil {
			continue
		}
		payload := map[string]any{}
		raw := env.GetPayloadJson()
		if raw != "" {
			if err := json.Unmarshal([]byte(raw), &payload); err != nil {
				// Bad JSON in the op payload is a client bug; surface the
				// envelope index for debugging.
				return blockstoreservice.ApplyOpsInput{}, fmt.Errorf("invalid op payload at index %d: %w", i, err)
			}
		}
		envs = append(envs, blockstoreservice.OpEnvelope{
			Op:      env.GetOp(),
			Payload: payload,
		})
	}
	in := blockstoreservice.ApplyOpsInput{
		WorkspaceID:    req.GetWorkspaceId(),
		Ops:            envs,
		IdempotencyKey: req.GetIdempotencyKey(),
	}
	if req.ParentOpId != nil {
		v := *req.ParentOpId
		in.ParentOpID = &v
	}
	return in, nil
}
