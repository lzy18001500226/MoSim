package runner

import (
	"context"
	"fmt"
	"os"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"

	"github.com/anthropics/agentsmesh/runner/internal/client"
	"github.com/anthropics/agentsmesh/runner/internal/logger"
	otelinit "github.com/anthropics/agentsmesh/runner/internal/otel"
	"github.com/anthropics/agentsmesh/runner/internal/poddaemon"
	"github.com/anthropics/agentsmesh/runner/internal/terminal"
	"github.com/anthropics/agentsmesh/runner/internal/terminal/aggregator"
	"github.com/anthropics/agentsmesh/runner/internal/terminal/vt"
)

// Build creates the pod.
// The CreatePodCommand carries pre-evaluated execution instructions from Backend.
// Runner only resolves path placeholders ({{sandbox_root}}, {{work_dir}}) and executes.
func (b *PodBuilder) Build(ctx context.Context) (*Pod, error) {
	buildStart := time.Now()
	ctx, span := otel.Tracer("agentsmesh-runner").Start(ctx, "pod.build",
		trace.WithAttributes(
			attribute.String("pod.key", b.cmd.GetPodKey()),
			attribute.String("pod.agent", b.cmd.GetLaunchCommand()),
		),
	)
	defer func() {
		span.End()
		otelinit.PodBuildDuration.Record(ctx, float64(time.Since(buildStart).Milliseconds()))
	}()

	if b.cmd == nil {
		return nil, fmt.Errorf("command is required")
	}
	if b.cmd.PodKey == "" {
		return nil, fmt.Errorf("pod key is required")
	}
	if b.cmd.LaunchCommand == "" {
		return nil, &client.PodError{
			Code:    client.ErrCodeAgentfileEval,
			Message: "launch_command is required (Backend AgentFile eval should populate this)",
		}
	}

	launchCommand := b.cmd.LaunchCommand
	logger.Pod().InfoContext(ctx, "Building pod", "pod_key", b.cmd.PodKey, "command", launchCommand)

	b.sendProgress("pending", 0, "Initializing pod...")

	sandboxRoot, workingDir, branchName, err := b.setup(ctx)
	if err != nil {
		return nil, err
	}

	// Resolve path placeholders in args, env vars, and files
	resolvedArgs := resolveStringSlice(b.cmd.LaunchArgs, sandboxRoot, workingDir)
	if err := b.createFilesFromProto(b.cmd.FilesToCreate, sandboxRoot, workingDir); err != nil {
		return nil, err
	}

	envVars := b.mergeEnvVars(sandboxRoot)
	for k, v := range b.cmd.EnvVars {
		envVars[k] = resolvePathPlaceholders(v, sandboxRoot, workingDir)
	}

	// Handle prompt injection into args
	prompt := b.cmd.Prompt
	if prompt != "" {
		switch b.cmd.PromptPosition {
		case "prepend":
			resolvedArgs = append([]string{prompt}, resolvedArgs...)
		case "append":
			resolvedArgs = append(resolvedArgs, prompt)
		}
	}

	// Determine interaction mode
	interactionMode := b.cmd.InteractionMode
	if interactionMode == "" {
		interactionMode = InteractionModePTY
	}

	logger.Pod().DebugContext(ctx, "Resolved launch args", "pod_key", b.cmd.PodKey, "args", resolvedArgs)
	logger.Pod().DebugContext(ctx, "Merged environment variables", "pod_key", b.cmd.PodKey, "count", len(envVars))

	if interactionMode == InteractionModeACP {
		return b.buildACPPod(ctx, sandboxRoot, workingDir, branchName, resolvedArgs, envVars, launchCommand)
	}
	return b.buildPTYPod(ctx, sandboxRoot, workingDir, branchName, resolvedArgs, envVars, launchCommand)
}

// buildPTYPod creates a pod with PTY terminal interaction.
func (b *PodBuilder) buildPTYPod(ctx context.Context, sandboxRoot, workingDir, branchName string, resolvedArgs []string, envVars map[string]string, launchCommand string) (*Pod, error) {
	b.sendProgress("starting_pty", 80, "Starting terminal...")

	// capturedEnv holds the full merged environment (os.Environ + AgentFile ENV)
	// as built by terminal.New. Replicated here for perpetual pod restart.
	capturedEnv := buildMergedEnv(envVars)

	// Inject W3C trace context into envVars map so terminal.New() propagates it
	// to the child process via both the ptyFactory (daemon mode) and direct PTY.
	injectTraceparent(ctx, envVars)
	if tp, ok := envVars["TRACEPARENT"]; ok {
		capturedEnv = append(capturedEnv, "TRACEPARENT="+tp)
	}

	// Build PTY factory for Pod Daemon mode (session persistence across restarts)
	var ptyFactory terminal.PTYFactory
	if b.deps.PodDaemonManager != nil && sandboxRoot != "" {
		mgr := b.deps.PodDaemonManager
		opts := poddaemon.CreateOpts{
			PodKey:         b.cmd.PodKey,
			Agent:          launchCommand,
			SandboxPath:    sandboxRoot,
			WorkDir:        workingDir,
			RepositoryURL:  b.cmd.GetSandboxConfig().GetHttpCloneUrl(),
			Branch:         branchName,
			TicketSlug:     b.cmd.GetSandboxConfig().GetTicketSlug(),
			VTHistoryLimit: b.vtHistoryLimit,
			Perpetual:      b.cmd.Perpetual,
		}
		ptyFactory = func(command string, args []string, workDir string, env []string, cols, rows int) (terminal.PtyProcess, error) {
			opts.Command = command
			opts.Args = args
			opts.Env = env
			opts.Cols = cols
			opts.Rows = rows
			dpty, _, err := mgr.CreateSession(opts)
			if err != nil {
				return nil, err
			}
			return dpty, nil
		}
	}

	term, err := terminal.New(terminal.Options{
		Command:    launchCommand,
		Args:       resolvedArgs,
		WorkDir:    workingDir,
		Env:        envVars,
		Rows:       b.rows,
		Cols:       b.cols,
		Label:      b.cmd.PodKey,
		PTYFactory: ptyFactory,
	})
	if err != nil {
		if sandboxRoot != "" {
			os.RemoveAll(sandboxRoot)
		}
		return nil, &client.PodError{
			Code:    client.ErrCodeCommandStart,
			Message: fmt.Sprintf("failed to create terminal: %v", err),
		}
	}

	virtualTerm := vt.NewVirtualTerminal(b.cols, b.rows, b.vtHistoryLimit)
	if b.oscHandler != nil {
		virtualTerm.SetOSCHandler(b.oscHandler)
	}

	// Create SmartAggregator for adaptive frame rate output
	agg := aggregator.NewSmartAggregator(nil,
		aggregator.WithFullRedrawThrottling(),
	)

	var ptyLogger *aggregator.PTYLogger
	if b.enablePTYLogging && b.ptyLogDir != "" {
		var logErr error
		ptyLogger, logErr = aggregator.NewPTYLogger(b.ptyLogDir, b.cmd.PodKey)
		if logErr != nil {
			logger.Pod().WarnContext(ctx, "Failed to create PTY logger", "pod_key", b.cmd.PodKey, "error", logErr)
		} else {
			agg.SetPTYLogger(ptyLogger)
			logger.Pod().InfoContext(ctx, "PTY logging enabled for pod", "pod_key", b.cmd.PodKey, "log_dir", ptyLogger.LogDir())
		}
	}

	pod := &Pod{
		ID:              b.cmd.PodKey,
		PodKey:          b.cmd.PodKey,
		Agent:           launchCommand,
		InteractionMode: InteractionModePTY,
		Branch:          branchName,
		SandboxPath:     sandboxRoot,
		LaunchCommand:   launchCommand,
		LaunchArgs:      resolvedArgs,
		WorkDir:         workingDir,
		LaunchEnv:       capturedEnv,
		Perpetual:       b.cmd.Perpetual,
		StartedAt:       time.Now(),
		Status:          PodStatusInitializing,
		vtProvider:      func() *vt.VirtualTerminal { return virtualTerm },
	}

	comps := &PTYComponents{Terminal: term, VirtualTerminal: virtualTerm, Aggregator: agg, PTYLogger: ptyLogger}
	ptyIO := NewPTYPodIO(b.cmd.PodKey, comps, PTYPodIODeps{
		GetOrCreateDetector: pod.GetOrCreateStateDetector,
		SubscribeState:      pod.SubscribeStateChange,
		UnsubscribeState:    pod.UnsubscribeStateChange,
		GetPTYError:         pod.GetPTYError,
	})
	pod.IO = ptyIO
	pod.Relay = NewPTYPodRelay(b.cmd.PodKey, pod.IO, comps, b.deps.LocalRelayServer)
	term.SetOutputHandler(NewPTYOutputHandler(b.cmd.PodKey, comps, pod.NotifyStateDetectorWithScreen))

	logger.Pod().InfoContext(ctx, "Pod built (PTY)", "pod_key", b.cmd.PodKey, "working_dir", workingDir, "cols", b.cols, "rows", b.rows)
	b.sendProgress("ready", 100, "Pod is ready")

	return pod, nil
}
