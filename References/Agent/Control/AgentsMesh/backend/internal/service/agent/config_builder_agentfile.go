package agent

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/anthropics/agentsmesh/agentfile/eval"
	"github.com/anthropics/agentsmesh/agentfile/parser"
	"github.com/anthropics/agentsmesh/backend/internal/domain/agent"
	envbundleservice "github.com/anthropics/agentsmesh/backend/internal/service/envbundle"
	runnerv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner/v1"
)

// Sandbox path placeholders — Runner replaces with real paths after sandbox setup.
const (
	PlaceholderSandboxRoot = "{{sandbox_root}}"
	PlaceholderWorkDir     = "{{work_dir}}"
)

// buildFromAgentfile evaluates the agent's AgentFile with placeholder sandbox
// paths and produces a CreatePodCommand. Credential injection is handled by
// AgentFile USE_ENV_BUNDLE declarations referencing entries in the eval
// context's EnvBundles map; the backend no longer threads a parallel
// credential blob through CreatePodCommand.
func (b *ConfigBuilder) buildFromAgentfile(
	ctx context.Context,
	req *ConfigBuildRequest,
	agentDef *agent.Agent,
) (*runnerv1.CreatePodCommand, error) {
	mergedSource := req.MergedAgentfileSource
	if mergedSource == "" {
		return nil, fmt.Errorf("agent %s: MergedAgentfileSource is empty (AgentFile resolve should always produce it)", req.AgentSlug)
	}

	// Build MCP context
	builtinMCP, installedMCP := b.buildMCPContext(ctx, req, agentDef.Slug)

	// Build EnvBundle context (mirror of MCP pattern: load every visible
	// bundle, decrypt, expose by name to eval; USE_ENV_BUNDLE picks).
	envBundles := b.buildEnvBundleContext(ctx, req, agentDef.Slug)

	// Parse and eval AgentFile with placeholder context
	prog, errs := parser.Parse(mergedSource)
	if len(errs) > 0 {
		return nil, fmt.Errorf("agentfile parse error: %v", errs[0])
	}

	evalCtx := buildEvalContext(req, builtinMCP, installedMCP, envBundles)
	if err := eval.Eval(prog, evalCtx); err != nil {
		return nil, fmt.Errorf("agentfile eval error: %w", err)
	}
	eval.ApplyModeArgs(evalCtx.Result)
	eval.ApplyRemoves(evalCtx.Result)

	// AgentFile SETUP is the most specific source for preparation scripts.
	// Preserve repository-level preparation as a fallback when SETUP is absent.
	effectiveReq := *req
	if evalCtx.Result.Setup.Script != "" {
		effectiveReq.PreparationScript = evalCtx.Result.Setup.Script
		effectiveReq.PreparationTimeout = evalCtx.Result.Setup.Timeout
	}

	cmd := buildResultToProto(&effectiveReq, evalCtx.Result)
	cmd.ResourcesToDownload = b.buildSkillResources(ctx, req, agentDef.Slug)
	return cmd, nil
}

func (b *ConfigBuilder) buildSkillResources(ctx context.Context, req *ConfigBuildRequest, agentSlug string) []*runnerv1.ResourceToDownload {
	if b.extensionProvider == nil || req.RepositoryID == nil {
		return nil
	}

	skills, err := b.extensionProvider.GetEffectiveSkills(ctx, req.OrganizationID, req.UserID, *req.RepositoryID, agentSlug)
	if err != nil {
		slog.WarnContext(ctx, "Failed to load skills for agentfile", "agent_slug", agentSlug, "error", err)
		return nil
	}

	resources := make([]*runnerv1.ResourceToDownload, 0, len(skills))
	for _, skill := range skills {
		if skill == nil {
			continue
		}
		if skill.ContentSha == "" || skill.DownloadURL == "" || skill.Slug == "" {
			slog.WarnContext(ctx, "Skipping skill with incomplete download metadata",
				"agent_slug", agentSlug, "skill_slug", skill.Slug)
			continue
		}
		resources = append(resources, &runnerv1.ResourceToDownload{
			Sha:          skill.ContentSha,
			DownloadUrl:  skill.DownloadURL,
			TargetPath:   skillTargetPath(agentSlug, skill.Slug),
			ResourceType: "skill_package",
			SizeBytes:    skill.PackageSize,
		})
	}
	return resources
}

func skillTargetPath(agentSlug, skillSlug string) string {
	switch agentSlug {
	case "codex-cli", "codex":
		return "{{.sandbox.root_path}}/codex-home/skills/" + skillSlug
	case "claude-code", "claude":
		return "{{.sandbox.work_dir}}/.claude/skills/" + skillSlug
	default:
		return "{{.sandbox.root_path}}/skills/" + skillSlug
	}
}

// buildEnvBundleContext loads every bundle visible to the user/org for this
// agent, decrypts credential-kind values, and returns a name → KV map for
// the eval phase to consume via USE_ENV_BUNDLE declarations.
//
// Mirrors buildMCPContext: tolerant — load failure degrades to "no bundles
// loaded" rather than aborting Pod creation. AgentFile declarations referring
// to missing bundles are silently skipped (warn-only) in evalUseEnvBundleDecl.
func (b *ConfigBuilder) buildEnvBundleContext(ctx context.Context, req *ConfigBuildRequest, agentSlug string) map[string]map[string]string {
	bundles, err := b.envBundleSvc.GetEffectiveForUser(ctx, req.UserID, req.OrganizationID, agentSlug)
	if err != nil {
		slog.WarnContext(ctx, "Failed to load env bundles for agentfile", "agent_slug", agentSlug, "error", err)
		return nil
	}
	return envbundleservice.AsContextMap(bundles)
}
