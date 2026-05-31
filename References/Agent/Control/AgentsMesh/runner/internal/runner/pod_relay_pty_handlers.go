package runner

import (
	"encoding/binary"
	"encoding/json"

	"github.com/anthropics/agentsmesh/runner/internal/logger"
	"github.com/anthropics/agentsmesh/runner/internal/relay"
)

func (r *PTYPodRelay) inputHandler() func([]byte) {
	log := logger.Pod()
	podKey := r.podKey
	io := r.io
	return func(payload []byte) {
		if io == nil {
			return
		}
		if err := io.SendInput(string(payload)); err != nil {
			log.Error("Failed to write relay input to pod", "pod_key", podKey, "error", err)
		}
	}
}

func (r *PTYPodRelay) resizeHandler() func([]byte) {
	log := logger.Pod()
	podKey := r.podKey
	io := r.io
	return func(payload []byte) {
		if len(payload) < 4 {
			log.Error("Failed to decode resize from relay", "pod_key", podKey, "error", "payload too short")
			return
		}
		cols := binary.BigEndian.Uint16(payload[0:2])
		rows := binary.BigEndian.Uint16(payload[2:4])
		ta, ok := io.(TerminalAccess)
		if !ok {
			return
		}
		if _, err := ta.Resize(int(cols), int(rows)); err != nil {
			log.Error("Failed to resize from relay", "pod_key", podKey, "error", err)
		}
	}
}

func (r *PTYPodRelay) installLocalHandlers() {
	if r.localServer == nil {
		return
	}
	r.localServer.SetMessageHandler(r.podKey, relay.MsgTypeInput, r.inputHandler())
	r.localServer.SetMessageHandler(r.podKey, relay.MsgTypeResize, r.resizeHandler())
	r.localServer.SetMessageHandler(r.podKey, relay.MsgTypeSnapshotRequest, func(_ []byte) {
		r.sendSnapshotToLocal()
	})
}

func (r *PTYPodRelay) sendSnapshotToLocal() {
	if r.localServer == nil {
		return
	}
	data := r.materializeSnapshot()
	if data == nil {
		return
	}
	_ = r.localServer.Send(r.podKey, relay.MsgTypeSnapshot, data)
}

// materializeSnapshot returns a JSON-encoded VT snapshot, falling back to the
// last cached payload when the live VT has nothing meaningful to render
// (i.e. before any output is written).
func (r *PTYPodRelay) materializeSnapshot() []byte {
	log := logger.Pod()
	vt := r.components.VirtualTerminal
	if vt == nil {
		return nil
	}
	snapshot := vt.GetSnapshot()
	if snapshot == nil {
		return nil
	}

	hasContent := len(snapshot.SerializedContent) > 20

	data, err := json.Marshal(snapshot)
	if err != nil {
		log.Error("Failed to marshal VT snapshot", "pod_key", r.podKey, "error", err)
		return nil
	}

	r.lastSnapshotMu.Lock()
	if hasContent {
		r.lastSnapshot = data
	} else if r.lastSnapshot != nil {
		data = r.lastSnapshot
	}
	r.lastSnapshotMu.Unlock()
	return data
}
