#!/usr/bin/env python3
"""Validate the CoAgent problem-to-solution design landing.

This check is intentionally static. It verifies that the design baseline and
template artifacts exist before runtime, transport, or automation expansion is
considered.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_DOCS = {
    "CoAgent/docs/architecture/coagent_solution_synthesis.md": [
        "Task Topology Selector",
        "Canonical Task Lifecycle",
        "Context Pack Quality Model",
        "Communication Protocol",
        "Human Intervention UX Baseline",
        "Stress Test A: PX4 Log to Simulation Parameters",
        "Stress Test B: UE/Fab Scene Truth and RflySim-Like Product Line",
        "These remain gated",
    ],
    "CoAgent/docs/architecture/coagent_user_intervention_ux.md": [
        "Intervention Classes",
        "Notification Levels",
        "Blocker Notification Contract",
        "Retry And Circuit Breaker Rules",
        "Email Adapter Guardrails",
        "Resume Packet",
    ],
    "CoAgent/docs/architecture/coagent_architecture_issue_register.md": [
        "Current Resolution Baseline",
        "COAGENT-DESIGN-12",
        "Still requiring experiments or separate approval",
        "Remaining Highest-Priority Discussion Order",
    ],
    "CoAgent/docs/architecture/coagent_department_capability_model.md": [
        "Capability Departments",
        "Conversation Mapping",
        "Required Permanent Conversations For Portable CoAgent",
        "Conditional Permanent Conversations",
        "Task-Scoped Conversations",
        "MoSim-Specific Initial Mapping",
        "Promotion And Demotion Rules",
        "Product Discovery / Strategy Deployment",
        "Flow Analytics / Operating Metrics",
        "Continuous Improvement / Retrospective Closure",
    ],
    "CoAgent/docs/architecture/coagent_conversation_mapping.md": [
        "11 required permanent conversations",
        "Conditional Permanent Conversations",
        "Hosted Capabilities At Startup",
        "Domain Engineering Mapping For MoSim",
        "Task-Scoped Conversation Rules",
        "First Minimal Closed-Loop Test Topology",
        "Current Registry Gap",
        "coagent_concrete_agent_design.md",
    ],
    "CoAgent/docs/architecture/coagent_concrete_agent_design.md": [
        "Universal Agent Contract",
        "Common Packet And State Model",
        "Required Permanent Agents",
        "Main PMO Agent",
        "Dispatch Agent",
        "Product Strategy Agent",
        "Agent Runtime Platform Agent",
        "Context Memory Agent",
        "Toolchain MCP Agent",
        "Knowledge Secretary Agent",
        "Verification Agent",
        "Safety Compliance Agent",
        "DevOps Release Agent",
        "External Intelligence Agent",
        "Permanent Agent Communication Matrix",
        "Permanent Agent Acceptance Matrix",
        "Task-Scoped Agent Relationship Matrix",
        "Minimal Closed-Loop Role Matrix",
        "Task-Scoped Agent Design",
        "PX4 Log To Simulation Parameters",
        "UE Scene Truth And RflySim-Like Product Line",
    ],
    "CoAgent/docs/architecture/coagent_vendor_gap_review_2026_05_29.md": [
        "Sources Rechecked",
        "Current Design Strengths",
        "Optimization Gaps",
        "Handoff Mode Selector Is Still Too Informal",
        "Capability Template And Conversation State Need Separation",
        "Workflow Graph Is Missing As A First-Class Object",
        "Shared Context Delta Needs A Concrete Packet",
        "Artifact Registry Is Under-Specified",
        "Trace And Evaluation Rubric Is Too Weak For Multi-Agent Work",
        "Prioritized Optimizations",
        "Impact On Current 11-Agent Design",
    ],
    "CoAgent/docs/architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md": [
        "Claude Agent Team Pattern",
        "Kimi Agent Swarm Pattern",
        "Codex Feature Use Matrix",
        "Thread Fork And Goal Policy",
        "Worktree And Runtime Workspace Policy",
        "Shared Task Board And Team Mailbox",
        "Hooks Are Hard Gates",
        "Plugins Are Capability Packages",
        "Design Extensions Required",
        "Impact On Current Permanent Conversations",
    ],
    "CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md": [
        "Dynamic Task Team V2 Design",
        "Core Objects",
        "Task Intake Flow",
        "Dynamic Team Policy",
        "Shared Task Board",
        "Team Mailbox",
        "Context Model",
        "Conversation Fork Policy",
        "Goal Ownership",
        "Worktree And File Surface Policy",
        "Review And Integration Flow",
        "Human Intervention Flow",
        "Metrics And Drift Control",
        "Stress Test A: PX4 Log To Simulation Parameters",
        "Stress Test B: UE Scene Truth And RflySim-Like Product Line",
        "Failure Mode Matrix",
        "Design Extension Backlog",
        "Acceptance Criteria For This Design",
    ],
    "CoAgent/docs/README.md": [
        "architecture/coagent_department_capability_model.md",
        "architecture/coagent_conversation_mapping.md",
        "architecture/coagent_concrete_agent_design.md",
        "architecture/coagent_vendor_gap_review_2026_05_29.md",
        "architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md",
        "architecture/coagent_dynamic_task_team_v2_design.md",
    ],
    "CoAgent/STATUS.md": [
        "Current department capability model",
        "CoAgent/docs/architecture/coagent_department_capability_model.md",
        "CoAgent/docs/architecture/coagent_conversation_mapping.md",
        "CoAgent/docs/architecture/coagent_concrete_agent_design.md",
        "CoAgent/docs/architecture/coagent_vendor_gap_review_2026_05_29.md",
        "CoAgent/docs/architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md",
        "CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md",
    ],
}


REQUIRED_TEMPLATES = {
    "CoAgent/protocol/templates/task_charter.yaml": [
        "canonical_task_goal:",
        "definition_of_done:",
        "circuit_breaker:",
        "result_contract:",
    ],
    "CoAgent/protocol/templates/context_pack.yaml": [
        "context_budget:",
        "layers:",
        "quality_gate:",
    ],
    "CoAgent/protocol/templates/scoped_conversation_packet.yaml": [
        "conversation_objective:",
        "checkpoint_plan:",
        "communication_rules:",
    ],
    "CoAgent/protocol/templates/blocker_notification.yaml": [
        "human_action_required:",
        "dedupe_key:",
        "email:",
    ],
    "CoAgent/protocol/templates/review_packet.yaml": [
        "claims_checked:",
        "decision_options:",
        "knowledge_promotion:",
    ],
    "CoAgent/protocol/templates/agent_profile.yaml": [
        "agent_id:",
        "conversation_label:",
        "hosted_departments:",
        "input_packets:",
        "output_packets:",
        "forbidden_actions:",
    ],
    "CoAgent/protocol/templates/task_scoped_agent_profile.yaml": [
        "task_agent_id:",
        "parent_task_id:",
        "canonical_task_goal:",
        "slice_objective:",
        "result_contract:",
        "close_condition:",
    ],
    "CoAgent/protocol/templates/handoff_mode.yaml": [
        "handoff_id:",
        "mode:",
        "authority_transfer:",
        "input_filter:",
        "cancellation_or_resume_rule:",
    ],
    "CoAgent/protocol/templates/capability_template.yaml": [
        "capability_id:",
        "supported_task_classes:",
        "allowed_skills:",
        "required_hooks:",
        "tool_risk_policy:",
    ],
    "CoAgent/protocol/templates/conversation_state.yaml": [
        "conversation_id:",
        "capability_template_id:",
        "current_assignment:",
        "blocked_or_interrupt:",
        "metrics:",
    ],
    "CoAgent/protocol/templates/context_delta.yaml": [
        "context_delta_id:",
        "delta_type:",
        "remove_or_mark_stale:",
        "requires_context_pack_regeneration:",
    ],
    "CoAgent/protocol/templates/artifact_manifest.yaml": [
        "artifact_id:",
        "artifact_type:",
        "provenance:",
        "lifecycle:",
        "security:",
    ],
    "CoAgent/protocol/templates/trace_eval_rubric.yaml": [
        "trace_eval_id:",
        "scope_discipline:",
        "context_economy:",
        "handoff_clarity:",
        "policy_compliance:",
    ],
    "CoAgent/protocol/templates/workflow_graph.yaml": [
        "workflow_id:",
        "node_type:",
        "edge_type:",
        "human_interrupt",
        "close_condition:",
    ],
}


def assert_contains(rel_path: str, needles: list[str]) -> None:
    path = ROOT / rel_path
    if not path.exists():
        raise AssertionError(f"missing required file: {rel_path}")
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{rel_path} missing required text: {needle}")


def main() -> int:
    for rel_path, needles in REQUIRED_DOCS.items():
        assert_contains(rel_path, needles)
    for rel_path, needles in REQUIRED_TEMPLATES.items():
        assert_contains(rel_path, needles)
    print("solution_design ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
