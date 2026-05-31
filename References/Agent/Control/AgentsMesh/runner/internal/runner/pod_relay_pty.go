package runner

import (
	"sync"
	"time"

	"github.com/anthropics/agentsmesh/runner/internal/logger"
	"github.com/anthropics/agentsmesh/runner/internal/relay"
	"github.com/anthropics/agentsmesh/runner/internal/safego"
)

// PTYPodRelay implements PodRelay for PTY-mode pods.
type PTYPodRelay struct {
	podKey         string
	io             PodIO
	components     *PTYComponents
	localServer    LocalRelayBroker
	lastSnapshotMu sync.Mutex
	lastSnapshot   []byte
}

// NewPTYPodRelay constructs a PodRelay for PTY mode.
// localServer == nil disables local-side fanout (e.g. when 127.0.0.1 binding failed).
func NewPTYPodRelay(podKey string, io PodIO, comps *PTYComponents, localServer LocalRelayBroker) *PTYPodRelay {
	return &PTYPodRelay{podKey: podKey, io: io, components: comps, localServer: localServer}
}

func (r *PTYPodRelay) SetupHandlers(rc relay.RelayClient) {
	rc.SetMessageHandler(relay.MsgTypeInput, r.inputHandler())
	rc.SetMessageHandler(relay.MsgTypeResize, r.resizeHandler())
	rc.SetMessageHandler(relay.MsgTypeSnapshotRequest, func(_ []byte) {
		r.SendSnapshot(rc)
	})
	r.installLocalHandlers()
}

func (r *PTYPodRelay) SendSnapshot(rc relay.RelayClient) {
	log := logger.Pod()
	data := r.materializeSnapshot()
	if data == nil {
		log.Warn("SendSnapshot: no snapshot available", "pod_key", r.podKey)
		return
	}
	_ = rc.Send(relay.MsgTypeSnapshot, data)

	vt := r.components.VirtualTerminal
	term := r.components.Terminal
	if vt != nil && vt.IsAltScreen() && term != nil {
		safego.Go("relay-snapshot-redraw", func() {
			time.Sleep(100 * time.Millisecond)
			if err := term.Redraw(); err != nil {
				log.Warn("Failed to redraw terminal after relay snapshot",
					"pod_key", r.podKey, "error", err)
			}
		})
	}
}

func (r *PTYPodRelay) OnRelayConnected(rc relay.RelayClient) {
	if r.components.Aggregator == nil {
		return
	}
	r.components.Aggregator.SetRelayClient(&fanoutRelayWriter{
		cloud:       rc,
		localServer: r.localServer,
		podKey:      r.podKey,
	})
}

func (r *PTYPodRelay) OnRelayDisconnected() {
	if r.components.Aggregator != nil {
		r.components.Aggregator.SetRelayClient(nil)
	}
}

// BroadcastEvent is a no-op for PTY pods; PTY output flows through the
// aggregator's fanoutRelayWriter, not via discrete events.
func (r *PTYPodRelay) BroadcastEvent(_ relay.RelayClient, _ byte, _ []byte) {}

var _ PodRelay = (*PTYPodRelay)(nil)
