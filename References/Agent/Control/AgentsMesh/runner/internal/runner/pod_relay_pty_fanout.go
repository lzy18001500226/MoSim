package runner

import (
	"github.com/anthropics/agentsmesh/runner/internal/relay"
)

// fanoutRelayWriter routes terminal output to both the cloud relay and the
// runner's local relay server. Either side can be down without breaking the
// other; aggregator drops bytes only when neither has a listener.
type fanoutRelayWriter struct {
	cloud       relay.RelayClient
	localServer LocalRelayBroker
	podKey      string
}

func (a *fanoutRelayWriter) SendOutput(data []byte) error {
	if a.cloud != nil && a.cloud.IsConnected() {
		_ = a.cloud.Send(relay.MsgTypeOutput, data)
	}
	if a.localServer != nil && a.localServer.IsPodConnected(a.podKey) {
		_ = a.localServer.Send(a.podKey, relay.MsgTypeOutput, data)
	}
	return nil
}

func (a *fanoutRelayWriter) IsConnected() bool {
	if a.cloud != nil && a.cloud.IsConnected() {
		return true
	}
	return a.localServer != nil && a.localServer.IsPodConnected(a.podKey)
}
