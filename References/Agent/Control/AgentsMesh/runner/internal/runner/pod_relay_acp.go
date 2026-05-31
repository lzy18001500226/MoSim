package runner

import (
	"encoding/json"

	"github.com/anthropics/agentsmesh/runner/internal/acp"
	"github.com/anthropics/agentsmesh/runner/internal/logger"
	"github.com/anthropics/agentsmesh/runner/internal/relay"
)

// ACPPodRelay implements PodRelay for ACP-mode pods.
type ACPPodRelay struct {
	podKey      string
	acpClient   *acp.ACPClient
	onCommand   func([]byte) // closure bound to pod ref at creation
	localServer LocalRelayBroker
}

// NewACPPodRelay creates a PodRelay for ACP mode.
// localServer is the runner-wide local relay server (nil to disable local fanout).
func NewACPPodRelay(podKey string, acpClient *acp.ACPClient, onCommand func([]byte), localServer LocalRelayBroker) *ACPPodRelay {
	return &ACPPodRelay{
		podKey:      podKey,
		acpClient:   acpClient,
		onCommand:   onCommand,
		localServer: localServer,
	}
}

func (r *ACPPodRelay) SetupHandlers(rc relay.RelayClient) {
	rc.SetMessageHandler(relay.MsgTypeAcpCommand, r.onCommand)
	rc.SetMessageHandler(relay.MsgTypeSnapshotRequest, func(_ []byte) {
		r.SendSnapshot(rc)
	})
	if r.localServer != nil {
		r.localServer.SetMessageHandler(r.podKey, relay.MsgTypeAcpCommand, r.onCommand)
		r.localServer.SetMessageHandler(r.podKey, relay.MsgTypeSnapshotRequest, func(_ []byte) {
			r.broadcastSnapshot()
		})
	}
}

func (r *ACPPodRelay) SendSnapshot(rc relay.RelayClient) {
	data := r.materializeSnapshot()
	if data == nil {
		return
	}
	if err := rc.Send(relay.MsgTypeAcpSnapshot, data); err != nil {
		logger.Pod().Warn("Failed to send ACP snapshot via relay", "pod_key", r.podKey, "error", err)
	}
}

// broadcastSnapshot pushes the ACP session snapshot to all local browsers.
func (r *ACPPodRelay) broadcastSnapshot() {
	if r.localServer == nil {
		return
	}
	data := r.materializeSnapshot()
	if data == nil {
		return
	}
	_ = r.localServer.Send(r.podKey, relay.MsgTypeAcpSnapshot, data)
}

func (r *ACPPodRelay) materializeSnapshot() []byte {
	if r.acpClient == nil {
		return nil
	}
	snapshot := r.acpClient.GetSessionSnapshot()
	data, err := json.Marshal(snapshot)
	if err != nil {
		logger.Pod().Error("Failed to marshal ACP snapshot", "pod_key", r.podKey, "error", err)
		return nil
	}
	return data
}

func (r *ACPPodRelay) OnRelayConnected(rc relay.RelayClient) {
	// No-op: ACP mode has no aggregator to wire
}

func (r *ACPPodRelay) OnRelayDisconnected() {
	// No-op: ACP mode has no aggregator to clear
}

// BroadcastEvent fans out an ACP event to both the cloud relay client and
// every local browser. Either side may be absent — the call is best-effort.
func (r *ACPPodRelay) BroadcastEvent(rc relay.RelayClient, msgType byte, payload []byte) {
	if rc != nil && rc.IsConnected() {
		_ = rc.Send(msgType, payload)
	}
	if r.localServer != nil && r.localServer.IsPodConnected(r.podKey) {
		_ = r.localServer.Send(r.podKey, msgType, payload)
	}
}

// Compile-time interface check.
var _ PodRelay = (*ACPPodRelay)(nil)
