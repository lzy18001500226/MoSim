package blockstoreservice

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestTrigger_WebhookFiresOnCreate wires an end-to-end trigger.define path:
//   1. Register a trigger_def for type=okr on=create
//   2. Create an OKR block
//   3. Assert the webhook URL receives a POST with the expected payload
func TestTrigger_WebhookFiresOnCreate(t *testing.T) {
	// httptest servers bind to 127.0.0.1, which the SSRF guard normally blocks.
	// Permit loopback for the scope of this test so the trigger can reach the
	// stub server — production deployments leave this env empty.
	t.Setenv("BLOCKSTORE_WEBHOOK_ALLOW_HOSTS", "127.0.0.1")
	var fired atomic.Int32
	var gotBody atomic.Value
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, _ := io.ReadAll(r.Body)
		gotBody.Store(string(body))
		fired.Add(1)
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	// Register OKR indicator and trigger together.
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTypeDef,
				"data": map[string]any{
					"type_key": "okr",
					"columns": []map[string]any{
						{"key": "title", "type": "text", "required": true},
					},
				},
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTriggerDef,
				"data": map[string]any{
					"name":        "okr-created",
					"target_type": "okr",
					"on":          "create",
					"enabled":     true,
					"action": map[string]any{
						"kind": "webhook",
						"url":  server.URL,
					},
				},
			}},
		},
	})
	require.NoError(t, err)

	// Create an OKR — trigger should fire.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   uuid.New().String(),
				"type": "okr",
				"data": map[string]any{"title": "Ship it"},
			}},
		},
	})
	require.NoError(t, err)

	// Fire is async; poll up to 1 sec.
	deadline := time.Now().Add(1 * time.Second)
	for time.Now().Before(deadline) && fired.Load() == 0 {
		time.Sleep(20 * time.Millisecond)
	}
	require.Equal(t, int32(1), fired.Load(), "webhook should fire exactly once")

	raw, ok := gotBody.Load().(string)
	require.True(t, ok)
	var payload map[string]any
	require.NoError(t, json.Unmarshal([]byte(raw), &payload))
	assert.Equal(t, "okr-created", payload["trigger"])
	assert.Equal(t, "create", payload["event"])
}

// TestTrigger_PredicateFiltersEvent verifies that a predicate expression
// stops the webhook from firing when the condition is false.
func TestTrigger_PredicateFiltersEvent(t *testing.T) {
	t.Setenv("BLOCKSTORE_WEBHOOK_ALLOW_HOSTS", "127.0.0.1")
	var fired atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fired.Add(1)
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTypeDef,
				"data": map[string]any{
					"type_key": "okr",
					"columns": []map[string]any{
						{"key": "title", "type": "text", "required": true},
						{"key": "progress", "type": "number"},
					},
				},
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTriggerDef,
				"data": map[string]any{
					"name":        "okr-at-risk",
					"target_type": "okr",
					"on":          "update",
					"predicate":   "{progress} < 0.3",
					"enabled":     true,
					"action": map[string]any{
						"kind": "webhook",
						"url":  server.URL,
					},
				},
			}},
		},
	})
	require.NoError(t, err)

	// Create OKR.
	okrID := uuid.New()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   okrID.String(),
				"type": "okr",
				"data": map[string]any{"title": "Ship", "progress": 0.8},
			}},
		},
	})
	require.NoError(t, err)

	// Update to progress=0.5 → predicate false → no fire.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":   okrID.String(),
				"data": map[string]any{"title": "Ship", "progress": 0.5},
			}},
		},
	})
	require.NoError(t, err)

	// Update to progress=0.1 → predicate true → fire.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":   okrID.String(),
				"data": map[string]any{"title": "Ship", "progress": 0.1},
			}},
		},
	})
	require.NoError(t, err)

	deadline := time.Now().Add(1 * time.Second)
	for time.Now().Before(deadline) && fired.Load() < 1 {
		time.Sleep(20 * time.Millisecond)
	}
	assert.Equal(t, int32(1), fired.Load(), "only the low-progress update should fire")
}

// TestTrigger_AgentActionWritesEventBlock verifies the agent callback path
// (action.kind="agent") writes a type="agent_event" block into the workspace
// when a matching op occurs. The block carries agent_slug / trigger_name /
// target metadata so the named agent can pick it up via subtree query or
// memory.retrieve.
func TestTrigger_AgentActionWritesEventBlock(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()
	_ = rootID

	triggerName := "okr-low-progress-agent"
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTriggerDef,
				"data": map[string]any{
					"name":        triggerName,
					"target_type": "task",
					"on":          "create",
					"action": map[string]any{
						"kind":       "agent",
						"agent_slug": "incident-commander",
					},
					"enabled": true,
				},
			}},
		},
	})
	require.NoError(t, err)

	// Create a task — the trigger should fire asynchronously and write an
	// agent_event block.
	taskID := uuid.New()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   taskID.String(),
				"type": blockstore.BlockTypeTask,
				"data": map[string]any{"title": "New incident", "status": "todo"},
			}},
		},
	})
	require.NoError(t, err)

	// Poll for the agent_event block — fireAgentAction runs in a goroutine.
	var events []*blockstore.Block
	deadline := time.Now().Add(2 * time.Second)
	for time.Now().Before(deadline) {
		eventType := blockstore.BlockTypeAgentEvent
		found, _, ferr := svc.repo.ListBlocks(ctx, blockstore.BlockFilter{
			WorkspaceID: wsID,
			Type:        &eventType,
		})
		require.NoError(t, ferr)
		if len(found) > 0 {
			events = found
			break
		}
		time.Sleep(30 * time.Millisecond)
	}
	require.NotEmpty(t, events, "agent_event block should be written")
	ev := events[0]
	assert.Equal(t, "incident-commander", ev.Data["agent_slug"])
	assert.Equal(t, triggerName, ev.Data["trigger_name"])
	assert.Equal(t, "task", ev.Data["target_type"])
	assert.Equal(t, taskID.String(), ev.Data["target_id"])
	assert.Equal(t, blockstore.OpCreateBlock, ev.Data["op_kind"])
	// Attribution: the event is owned by the user who authored the trigger,
	// not by System (UserID=0) or by the actor who created the task. This
	// is the "权限跟着人走" rule — triggers act on behalf of their creator,
	// and resulting side-effects inherit that user for ACL purposes.
	assert.Equal(t, actor.UserID, ev.CreatedBy,
		"agent_event must be attributed to the trigger's creator, not system")
	// ACL should be private + scoped to that same user so agents in other
	// pods (other people's pods) can't retrieve this inbox entry.
	acl, _ := ev.Meta["acl"].(map[string]any)
	require.NotNil(t, acl, "agent_event must carry an ACL object")
	assert.Equal(t, "private", acl["visibility"])
}

// TestTrigger_AgentEventDoesNotCascade protects against an unbounded write
// loop: if a workspace has a trigger whose target_type=="agent_event", a
// single triggered write would previously fire that same trigger on its own
// output, and so on forever. fireAgentAction sets SuppressTriggers=true on
// the ApplyOpsInput so the dispatch path skips system writes.
func TestTrigger_AgentEventDoesNotCascade(t *testing.T) {
	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	// Trigger A fires when a task is created and writes an agent_event.
	// Trigger B watches agent_event creation — if cascade protection
	// breaks, trigger B would fire on A's output, A or B would again fire
	// on the result, etc. We enforce the guard by SuppressTriggers, so
	// ONLY the single A-produced agent_event survives.
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTriggerDef,
				"data": map[string]any{
					"name": "a-on-task", "target_type": "task", "on": "create",
					"action":  map[string]any{"kind": "agent", "agent_slug": "watcher"},
					"enabled": true,
				},
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTriggerDef,
				"data": map[string]any{
					"name": "b-on-event", "target_type": "agent_event", "on": "create",
					"action":  map[string]any{"kind": "agent", "agent_slug": "watcher"},
					"enabled": true,
				},
			}},
		},
	})
	require.NoError(t, err)

	// Fire the root cause: a new task.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   uuid.New().String(),
				"type": blockstore.BlockTypeTask,
				"data": map[string]any{"title": "cascade probe", "status": "todo"},
			}},
		},
	})
	require.NoError(t, err)

	// Wait a couple of seconds to give any erroneous cascade a chance to
	// pile up extra agent_event rows.
	time.Sleep(1 * time.Second)

	eventType := blockstore.BlockTypeAgentEvent
	events, _, err := svc.repo.ListBlocks(ctx, blockstore.BlockFilter{
		WorkspaceID: wsID,
		Type:        &eventType,
	})
	require.NoError(t, err)
	// Exactly ONE event from trigger A; trigger B must NOT have fired.
	assert.Len(t, events, 1, "cascade guard should prevent trigger B firing on A's output")
	assert.Equal(t, "a-on-task", events[0].Data["trigger_name"])
}
