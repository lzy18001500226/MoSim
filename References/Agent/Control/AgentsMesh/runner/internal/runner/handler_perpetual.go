package runner

import (
	"fmt"
	"time"

	"github.com/anthropics/agentsmesh/runner/internal/logger"
	"github.com/anthropics/agentsmesh/runner/internal/poddaemon"
	"github.com/anthropics/agentsmesh/runner/internal/safego"
	"github.com/anthropics/agentsmesh/runner/internal/terminal"
	"github.com/anthropics/agentsmesh/runner/internal/terminal/aggregator"
	"github.com/anthropics/agentsmesh/runner/internal/terminal/vt"
)

const defaultVTHistoryLimit = 100

func isCleanExit(exitCode int) bool {
	return exitCode == 0 || exitCode >= 128 || exitCode == -1
}

// restartPerpetualPod restarts a perpetual pod's process in the same sandbox.
// Called from cleanupPodExit when a perpetual pod exits cleanly.
func (h *RunnerMessageHandler) restartPerpetualPod(pod *Pod, exitCode int) {
	log := logger.Pod()
	pod.RestartCount++
	log.Info("Perpetual pod restarting",
		"pod_key", pod.PodKey, "exit_code", exitCode, "restart_count", pod.RestartCount)

	// Collect token usage from the completed session before restart
	h.collectTokenUsageAsync(pod)

	// Clean up old state detector (references destroyed VirtualTerminal)
	pod.StopStateDetector()
	// Disconnect old relay client (will be re-subscribed by Backend)
	pod.DisconnectRelay()
	// Clear stale PTY error from previous session
	pod.SetPTYError("")

	pod.IO.Teardown()

	mgr := h.runner.GetPodDaemonManager()
	if mgr == nil {
		log.Error("PodDaemonManager unavailable, falling back to normal exit", "pod_key", pod.PodKey)
		h.cleanupPodExitFinal(pod, exitCode)
		return
	}

	const defaultCols, defaultRows = 80, 24

	dpty, _, err := mgr.CreateSession(poddaemon.CreateOpts{
		PodKey:         pod.PodKey,
		Agent:          pod.Agent,
		Command:        pod.LaunchCommand,
		Args:           pod.LaunchArgs,
		WorkDir:        pod.WorkDir,
		Env:            pod.LaunchEnv,
		Cols:           defaultCols,
		Rows:           defaultRows,
		SandboxPath:    pod.SandboxPath,
		RepositoryURL:  pod.RepositoryURL,
		Branch:         pod.Branch,
		TicketSlug:     pod.TicketSlug,
		VTHistoryLimit: defaultVTHistoryLimit,
		Perpetual:      true,
	})
	if err != nil {
		log.Error("Failed to restart perpetual pod, falling back to normal exit",
			"pod_key", pod.PodKey, "error", err)
		h.cleanupPodExitFinal(pod, exitCode)
		return
	}

	if err := h.rebuildPTYIO(pod, dpty, defaultCols, defaultRows); err != nil {
		log.Error("Failed to rebuild IO for perpetual pod", "pod_key", pod.PodKey, "error", err)
		dpty.Close()
		h.cleanupPodExitFinal(pod, exitCode)
		return
	}

	// Re-subscribe agent status bridge (lost when state detector was stopped)
	pod.SubscribeAgentStatusBridge(h.conn.SendAgentStatus)

	// Notify Backend with new PID (sent AFTER restart succeeds)
	if h.conn != nil {
		newPID := int32(0)
		if pod.IO != nil {
			newPID = int32(pod.IO.GetPID())
		}
		if err := h.conn.SendPodRestarting(pod.PodKey, int32(exitCode), int32(pod.RestartCount), newPID); err != nil {
			log.Error("Failed to send pod restarting event", "pod_key", pod.PodKey, "error", err)
		}
	}

	pod.SetStatus(PodStatusRunning)
	pod.StartedAt = time.Now()
	log.Info("Perpetual pod restarted", "pod_key", pod.PodKey, "restart_count", pod.RestartCount)
}

// collectTokenUsageAsync collects token usage from a completed session.
func (h *RunnerMessageHandler) collectTokenUsageAsync(pod *Pod) {
	agent := pod.Agent
	sandboxPath := pod.SandboxPath
	podStartedAt := pod.StartedAt
	podKey := pod.PodKey
	safego.Go("token-usage-perpetual", func() {
		h.collectAndSendTokenUsage(podKey, agent, sandboxPath, podStartedAt)
	})
}

// rebuildPTYIO reconstructs the Pod's I/O layer with a new daemon PTY.
func (h *RunnerMessageHandler) rebuildPTYIO(pod *Pod, dpty terminal.PtyProcess, cols, rows int) error {
	ptyFactory := func(command string, args []string, workDir string, env []string, c, r int) (terminal.PtyProcess, error) {
		return dpty, nil
	}

	term, err := terminal.New(terminal.Options{
		Command:    pod.LaunchCommand,
		Args:       pod.LaunchArgs,
		WorkDir:    pod.WorkDir,
		Cols:       cols,
		Rows:       rows,
		Label:      pod.PodKey,
		PTYFactory: ptyFactory,
	})
	if err != nil {
		return fmt.Errorf("create terminal: %w", err)
	}

	virtualTerm := vt.NewVirtualTerminal(cols, rows, defaultVTHistoryLimit)
	virtualTerm.SetOSCHandler(h.createOSCHandler(pod.PodKey))

	agg := aggregator.NewSmartAggregator(nil, aggregator.WithFullRedrawThrottling())

	cfg := h.runner.GetConfig()
	var ptyLogger *aggregator.PTYLogger
	if cfg.LogPTY {
		pl, logErr := aggregator.NewPTYLogger(cfg.GetLogPTYDir(), pod.PodKey)
		if logErr == nil {
			ptyLogger = pl
			agg.SetPTYLogger(ptyLogger)
		}
	}

	pod.vtProvider = func() *vt.VirtualTerminal { return virtualTerm }

	comps := &PTYComponents{Terminal: term, VirtualTerminal: virtualTerm, Aggregator: agg, PTYLogger: ptyLogger}
	term.SetOutputHandler(NewPTYOutputHandler(pod.PodKey, comps, pod.NotifyStateDetectorWithScreen))

	ptyIO := NewPTYPodIO(pod.PodKey, comps, PTYPodIODeps{
		GetOrCreateDetector: pod.GetOrCreateStateDetector,
		SubscribeState:      pod.SubscribeStateChange,
		UnsubscribeState:    pod.UnsubscribeStateChange,
		GetPTYError:         pod.GetPTYError,
	})
	pod.IO = ptyIO
	pod.Relay = NewPTYPodRelay(pod.PodKey, pod.IO, comps, h.runner.GetLocalRelayServer())

	pod.IO.SetExitHandler(h.createExitHandler(pod.PodKey))
	pod.IO.SetIOErrorHandler(h.createPTYErrorHandler(pod.PodKey, pod))

	if err := pod.IO.Start(); err != nil {
		pod.IO.Teardown()
		return fmt.Errorf("start terminal: %w", err)
	}

	return nil
}

// cleanupPodExitFinal runs the standard cleanup when perpetual restart fails.
func (h *RunnerMessageHandler) cleanupPodExitFinal(pod *Pod, exitCode int) {
	h.podStore.Delete(pod.PodKey)

	if ac := h.runner.GetAutopilotByPodKey(pod.PodKey); ac != nil {
		ac.Stop()
		if agentMon := h.runner.GetAgentMonitor(); agentMon != nil {
			agentMon.Unsubscribe("autopilot-" + ac.Key())
		}
		h.runner.RemoveAutopilot(ac.Key())
	}

	pod.SetStatus(PodStatusStopped)
	pod.StopStateDetector()
	pod.DisconnectRelay()
	if pod.SandboxPath != "" {
		_ = poddaemon.DeleteState(pod.SandboxPath)
	}
	if mcpSrv := h.runner.GetMCPServer(); mcpSrv != nil {
		mcpSrv.UnregisterPod(pod.PodKey)
	}
	if agentMon := h.runner.GetAgentMonitor(); agentMon != nil {
		agentMon.UnregisterPod(pod.PodKey)
	}

	podStatus, errorMsg := "completed", ""
	if ptyErr := pod.GetPTYError(); ptyErr != "" {
		podStatus, errorMsg = "error", ptyErr
	} else if exitCode > 0 && exitCode < 128 {
		podStatus, errorMsg = "error", fmt.Sprintf("process exited with code %d", exitCode)
	}
	if h.conn != nil {
		_ = h.conn.SendPodTerminated(pod.PodKey, int32(exitCode), errorMsg, podStatus)
	}
}
