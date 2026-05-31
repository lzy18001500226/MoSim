package relay

import (
	"net/http"
	"time"

	"github.com/gorilla/websocket"
)

// RegisterPod records an accepted token for a pod. Subsequent incoming
// browser connections that present any registered token (via ?token=) are
// accepted. Multi-user shared pods can have multiple live tokens at once;
// tokens are cleared en bloc when UnregisterPod is called or the pod
// terminates. The backend-issued JWT TTL bounds individual token lifetime.
func (s *LocalServer) RegisterPod(podKey, expectedToken string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return
	}
	lane, ok := s.pods[podKey]
	if !ok {
		lane = &localPodLane{
			expectedTokens: make(map[string]struct{}),
			handlers:       make(map[byte]func([]byte)),
			conns:          make(map[*websocket.Conn]struct{}),
		}
		s.pods[podKey] = lane
	}
	lane.mu.Lock()
	if lane.expectedTokens == nil {
		lane.expectedTokens = make(map[string]struct{})
	}
	lane.expectedTokens[expectedToken] = struct{}{}
	lane.mu.Unlock()
}

// UnregisterPod stops accepting new connections for this pod and closes all
// existing browser conns. Subsequent connection attempts are rejected.
func (s *LocalServer) UnregisterPod(podKey string) {
	s.mu.Lock()
	lane, ok := s.pods[podKey]
	if ok {
		delete(s.pods, podKey)
	}
	s.mu.Unlock()
	if !ok {
		return
	}
	lane.mu.Lock()
	for c := range lane.conns {
		_ = c.Close()
	}
	lane.conns = nil
	lane.handlers = nil
	lane.expectedTokens = nil
	lane.mu.Unlock()
}

// SetMessageHandler registers an inbound handler for a given message type on
// the pod. Replaces any prior handler for the same type. No-op when the pod
// is not registered.
func (s *LocalServer) SetMessageHandler(podKey string, msgType byte, handler func([]byte)) {
	lane := s.lookupLane(podKey)
	if lane == nil {
		return
	}
	lane.mu.Lock()
	defer lane.mu.Unlock()
	if lane.handlers == nil {
		return
	}
	lane.handlers[msgType] = handler
}

// Send broadcasts an encoded message to every browser connected for this pod.
// Returns nil even when there are no listeners — output drops are expected.
// On per-conn write error we close the conn so the read loop drops it from
// lane.conns immediately rather than waiting for the next read attempt.
func (s *LocalServer) Send(podKey string, msgType byte, payload []byte) error {
	lane := s.lookupLane(podKey)
	if lane == nil {
		return nil
	}
	encoded := EncodeMessage(msgType, payload)
	conns := lane.snapshotConns()
	for _, c := range conns {
		_ = c.SetWriteDeadline(time.Now().Add(localWriteTimeout))
		if err := c.WriteMessage(websocket.BinaryMessage, encoded); err != nil {
			_ = c.Close()
		}
	}
	return nil
}

// IsPodConnected reports whether at least one browser is currently connected
// for this pod.
func (s *LocalServer) IsPodConnected(podKey string) bool {
	lane := s.lookupLane(podKey)
	if lane == nil {
		return false
	}
	lane.mu.RLock()
	defer lane.mu.RUnlock()
	return len(lane.conns) > 0
}

func (s *LocalServer) lookupLane(podKey string) *localPodLane {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.pods[podKey]
}

// handleBrowser is the WebSocket entry point for browser connections.
// Path: /browser/relay?token=<jwt>&pod=<pod_key>
func (s *LocalServer) handleBrowser(w http.ResponseWriter, r *http.Request) {
	podKey := r.URL.Query().Get("pod")
	token := r.URL.Query().Get("token")
	if podKey == "" || token == "" {
		http.Error(w, "pod and token required", http.StatusBadRequest)
		return
	}

	lane := s.lookupLane(podKey)
	if lane == nil {
		http.Error(w, "unknown pod", http.StatusNotFound)
		return
	}
	lane.mu.RLock()
	_, accepted := lane.expectedTokens[token]
	lane.mu.RUnlock()
	if !accepted {
		http.Error(w, "invalid token", http.StatusUnauthorized)
		return
	}

	conn, err := localUpgrader.Upgrade(w, r, nil)
	if err != nil {
		s.logger.Warn("Local relay upgrade failed", "pod_key", podKey, "error", err)
		return
	}
	conn.SetReadLimit(localReadLimitBytes)
	_ = conn.SetReadDeadline(time.Now().Add(localReadTimeout))
	conn.SetPongHandler(func(string) error {
		return conn.SetReadDeadline(time.Now().Add(localReadTimeout))
	})

	lane.mu.Lock()
	if lane.conns == nil {
		lane.mu.Unlock()
		_ = conn.Close()
		return
	}
	lane.conns[conn] = struct{}{}
	lane.mu.Unlock()

	s.logger.Info("Local relay browser connected", "pod_key", podKey)

	go s.readLoop(podKey, lane, conn)
}

func (s *LocalServer) readLoop(podKey string, lane *localPodLane, conn *websocket.Conn) {
	defer func() {
		lane.mu.Lock()
		delete(lane.conns, conn)
		lane.mu.Unlock()
		_ = conn.Close()
		s.logger.Info("Local relay browser disconnected", "pod_key", podKey)
	}()

	for {
		mt, data, err := conn.ReadMessage()
		if err != nil {
			return
		}
		_ = conn.SetReadDeadline(time.Now().Add(localReadTimeout))
		if mt != websocket.BinaryMessage || len(data) < 1 {
			continue
		}
		msgType := data[0]
		payload := data[1:]
		lane.mu.RLock()
		handler := lane.handlers[msgType]
		lane.mu.RUnlock()
		if handler != nil {
			handler(payload)
		}
	}
}

func (l *localPodLane) snapshotConns() []*websocket.Conn {
	l.mu.RLock()
	defer l.mu.RUnlock()
	out := make([]*websocket.Conn, 0, len(l.conns))
	for c := range l.conns {
		out = append(out, c)
	}
	return out
}
