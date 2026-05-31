package eventsconnect

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/infra/eventbus"
	"github.com/anthropics/agentsmesh/backend/internal/infra/websocket"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	eventsv1 "github.com/anthropics/agentsmesh/proto/gen/go/events/v1"
)

// Subscribe mirrors the legacy `/api/v1/orgs/:slug/ws/events` upgrade —
// the client opens a server-stream RPC and the handler forwards every
// `eventbus.Event` routed through the hub to the stream until ctx
// cancels (client disconnect / server shutdown).
func (s *Server) Subscribe(
	ctx context.Context,
	req *connect.Request[eventsv1.SubscribeRequest],
	stream *connect.ServerStream[eventsv1.Event],
) error {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return connect.NewError(connect.CodeUnauthenticated,
			errors.New("authentication required"))
	}

	client := websocket.NewConnectEventsClient(s.hub, tenant.UserID, tenant.OrganizationID)
	s.hub.Register(client)
	defer s.hub.Unregister(client)

	outbound := client.Outbound()
	for {
		select {
		case <-ctx.Done():
			return nil
		case raw, ok := <-outbound:
			if !ok {
				return nil
			}
			evt, err := convertHubEventToProto(raw)
			if err != nil {
				slog.DebugContext(ctx, "skipping malformed hub event",
					"error", err, "raw_len", len(raw))
				continue
			}
			if err := stream.Send(evt); err != nil {
				// Client disconnect — exit cleanly.
				return nil
			}
		}
	}
}

// convertHubEventToProto turns the JSON envelope that the hub broadcasts
// (eventbus.Event marshaled by HubEventSubscriber) into a proto Event
// message. The proto keeps `data_json` as the original JSON-encoded
// payload (35+ event types are heterogeneous; oneof is over-engineering
// for the wire and the consumer-side schema lives in the events crate).
func convertHubEventToProto(raw []byte) (*eventsv1.Event, error) {
	var src eventbus.Event
	if err := json.Unmarshal(raw, &src); err != nil {
		return nil, err
	}
	dataJSON := string(src.Data)
	if dataJSON == "" {
		dataJSON = "{}"
	}
	out := &eventsv1.Event{
		Type:           string(src.Type),
		Category:       string(src.Category),
		OrganizationId: src.OrganizationID,
		EntityType:     optString(src.EntityType),
		EntityId:       optString(src.EntityID),
		TargetUserIds:  src.TargetUserIDs,
		DataJson:       dataJSON,
		Timestamp:      src.Timestamp,
	}
	return out, nil
}

func optString(v string) *string {
	if v == "" {
		return nil
	}
	return &v
}
