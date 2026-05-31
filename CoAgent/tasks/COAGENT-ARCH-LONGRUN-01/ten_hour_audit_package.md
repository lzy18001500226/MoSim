# COAGENT-ARCH-LONGRUN-01 Ten Hour Audit Package

Date: 2026-05-30
Status: active audit package, not completion claim

## Purpose

Provide one concentrated audit entry for the user after the 10-hour CoAgent
architecture push. This package does not replace the detailed design files; it
defines how to judge them without mistaking volume for completion.

The goal remains active until every requirement in the goal audit is proven or
explicitly deferred with an accepted next experiment or implementation gate.

## Audit Verdict Format

Use this table at review time:

| Area | Verdict | Evidence | Required Follow-Up |
|---|---|---|---|
| Task-first architecture | `pass | partial | fail` | file/command path | next step |
| Multi-conversation collaboration | `pass | partial | fail` | file/command path | next step |
| Dynamic task teams | `pass | partial | fail` | file/command path | next step |
| Context and memory | `pass | partial | fail` | file/command path | next step |
| Communication and packets | `pass | partial | fail` | file/command path | next step |
| Tool/MCP capability and fallback | `pass | partial | fail` | file/command path | next step |
| Worktree and Git | `pass | partial | fail` | file/command path | next step |
| Review and testing | `pass | partial | fail` | file/command path | next step |
| Safety and human intervention | `pass | partial | fail` | file/command path | next step |
| External intelligence | `pass | partial | fail` | file/command path | next step |
| Self-evolution | `pass | partial | fail` | file/command path | next step |
| Retrospective closure | `pass | partial | fail` | file/command path | next step |
| Implementation breakdown | `pass | partial | fail` | file/command path | next step |

Allowed verdict meanings:

- `pass`: current evidence is sufficient for the design level being claimed;
- `partial`: design exists but proof, validator, live run, or implementation is
  still missing;
- `fail`: evidence contradicts the claim, is missing, or the design would route
  work unsafely.

Do not use `pass` for any live capability that has only design evidence.

## Required Audit Commands

Run these commands before any final review statement:

```bash
python3 CoAgent/doctor/check_department_visibility.py
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/tests/test_design_surface_docs.py
python3 CoAgent/runtime/mosim_agent_runtime.py show --task-id COAGENT-ARCH-LONGRUN-01
git diff --check -- CoAgent/tasks/COAGENT-ARCH-LONGRUN-01 CoAgent/STATUS.md PROGRESS.md
```

Optional command when judging broader implementation health:

```bash
python3 CoAgent/doctor/coagent_doctor.py
```

The optional doctor may report warnings for runtime or transport surfaces. A
warning is not automatically a design failure, but it must be mapped to a
known blocker, risk, or implementation backlog item.

## Primary Evidence Set

Start with these files:

- `task_charter.md`
- `shared_task_board.md`
- `architecture_problem_matrix.md`
- `architecture_decision_record_summary.md`
- `goal_requirement_audit_map.md`
- `goal_completion_gate_protocol.md`
- `final_goal_completion_audit.md`
- `review_brief.md`
- `task_intake_to_proof_ladder_decision_table.md`
- `proof_ladder_and_validator_order.md`
- `implementation_sequence_and_release_plan.md`
- `post_design_implementation_backlog.md`

Then inspect the proof package designs:

- `candidate_a_packet_chain_blueprint.md`
- `candidate_a_proof_package_design.md`
- `candidate_a_validator_execution_design.md`
- `candidate_a_minimal_package_contract.md`
- `candidate_a_fixture_generation_plan.md`
- `candidate_a_manual_rehearsal_plan.md`
- `candidate_a_fixture_spec.md`
- `candidate_b_px4_parameter_proof_package.md`
- `candidate_c_ue_scene_truth_proof_package.md`
- `candidate_d_git_heavy_change_proof_package.md`
- `candidate_e_auth_license_interruption_proof_package.md`
- `common_proof_package_validator_design.md`

Then inspect the operating protocols:

- `dynamic_team_decision_rules.md`
- `communication_context_protocol.md`
- `mailbox_ledger_and_replay_design.md`
- `context_lifecycle_schema.md`
- `context_delta_checker_design.md`
- `context_index_and_assembly_design.md`
- `handoff_workflow_validator_design.md`
- `result_packet_contract_hardening.md`
- `result_packet_validator_design.md`
- `tool_capability_health_and_fallback_protocol.md`
- `codex_visibility_drift_reliability_design.md`
- `transport_timeout_hardening_design.md`
- `blocker_packet_templates.md`
- `blocker_packet_validator_design.md`
- `worktree_git_integration_protocol.md`
- `verification_evaluation_protocol.md`
- `verification_gate_hardening.md`
- `evidence_label_doctor_design.md`
- `stress_test_artifact_validator_design.md`
- `validator_dependency_and_rollout_plan.md`
- `safety_human_intervention_protocol.md`
- `knowledge_promotion_protocol.md`
- `problem_driven_external_adoption_queue.md`
- `external_adoption_proposal_contract.md`
- `external_adoption_store_checker_design.md`
- `retrospective_and_improvement_closure_protocol.md`
- `operating_metrics_and_anti_drift_cadence.md`
- `operating_metrics_snapshot_design.md`

## Requirement-To-Audit Mapping

| Requirement | Minimum Evidence To Pass Design Audit | Current Expected Verdict |
|---|---|---|
| Task-first architecture | task flow plus intake-to-proof decision table routes examples without fixed department count | partial until Candidate A proof runs |
| Goal authority/decomposition | goal authority protocol rejects setup work, topology, elapsed time, and document volume as substitutes for user outcome | design pass, checker pending |
| Multi-conversation collaboration | active visible registry plus packet results plus Candidate A package design | partial until full packet chain runs |
| Dynamic task teams | topology rules plus proof-path team selection plus handoff/workflow validator design | partial until validator/live proof |
| Context/memory indexing | context protocol plus lifecycle schema plus context delta checker design plus index/assembly design plus Candidate A context delta requirement | partial until retrieval manifest and context checker |
| Cross-conversation communication | flat result packet contract plus validator design plus blocker templates plus department packets plus mailbox ledger/replay design | partial until packet, mailbox, and timeout validators exist |
| Tool/MCP capability and fallback | capability-card health protocol for MWORKS, UE, Fab/manual import, Codex transport, Git, and external-reference routes | partial until tool capability health gate checker and product-route proofs exist |
| Worktree/Git merge | Git-heavy proof package rejects broad staging and names integration gates | design pass, live proof pending |
| Review/testing gates | verification protocol, common validator design, Candidate A validator execution design, Candidate A fixtures, operating metrics snapshot design, stress-test artifact validator design, evidence-label doctor design, validator dependency plan | partial until executable validators, dependency-aware reports, and metrics snapshot |
| Safety boundaries | human-intervention protocol, Candidate E design, blocker packet validator design | partial until blocker validator/proof |
| Human intervention | exact PMO ask, resume condition, dedupe policy in Candidate E | partial until simulated proof |
| External intelligence | problem-driven adoption queue plus proposal contract plus store checker design | partial until proposal store/checker |
| Self-evolution | knowledge promotion protocol plus proposal accept/reject/promote contract plus evidence-level guard design | partial until promotion/rejection proof |
| Retrospective closure | retrospective protocol plus action schema plus promotion/rejection and stale-action policy | partial until retrospective checker/store and closeout proof |
| Reviewable docs | review brief, audit map, this package | design pass if commands pass |
| Problem matrix | P01-P59 with owners and outputs | design pass if maintained |
| Minimal closed loop | Candidate A package, minimal package contract, validator execution design, and fixtures | partial until fixture implementation, validator, or live proof |
| Department dispatch results | Dispatch/Context/Verify packets, Runtime timeout finding, and transport timeout hardening design | partial, transport risk remains until hardening/proof |
| Next implementation breakdown | NEXT-00 through NEXT-27 plus R0-R8 implementation phase ladder | design pass, requires user approval |

## Claims That Must Not Be Made Yet

Do not claim:

- CoAgent has proven unattended multi-conversation execution;
- Candidate A has passed live proof;
- PX4 parameter identification is operationally solved;
- UE scene truth is operationally solved;
- Fab/UE/MWORKS tooling is reliable through CoAgent;
- tool capability health cards/checkers are implemented or current;
- external learning is automated or scheduled;
- email/desktop notification is implemented;
- app-server transport is enabled;
- automatic conversation or worktree creation is enabled;
- result packet, blocker packet, stress-test artifact, evidence-label, context
  delta, operating metrics, or proof-package validators are implemented.

## User Decision Points

At audit time, the user should answer:

1. Should Candidate A remain the first live proof?
2. Should the first implementation slice be result packet hardening,
   Candidate A validator, context delta checker, metrics snapshot, or
   transport timeout hardening?
3. Should PX4 parameter identification or UE scene truth become the first
   product-adjacent proof after Candidate A?
4. Should Git-heavy safety be moved earlier because the repository is already
   noisy?
5. Should auth/license interruption be tested before any MWORKS or UE work?
6. Are the 11 permanent conversations sufficient for now, or should additional
   capability departments remain conditional?
7. What manual-review channel is acceptable later for Candidate E:
   main chat only, email draft only, or real notification after approval?
8. Should `COAGENT-IMPL-NEXT-10` be moved earlier so external learning and
   self-evolution have a proposal store/checker before more source study?
9. Should the next approved implementation follow R1 validator foundation
   first, or does the user explicitly want to record a skip/deviation for a
   higher-risk phase?

## Recommended Next Approval Queue

Default order:

1. `COAGENT-IMPL-NEXT-11`: result packet contract hardening.
2. `COAGENT-IMPL-NEXT-15`: Candidate A proof-package validator and fixture
   harness.
3. `COAGENT-IMPL-NEXT-13`: handoff mode and workflow graph validators.
4. `COAGENT-IMPL-NEXT-02`: context delta template/checker.
5. `COAGENT-IMPL-NEXT-05`: blocker packet validator using
   `blocker_packet_validator_design.md`.
6. `COAGENT-IMPL-NEXT-07`: evidence-label doctor using
   `evidence_label_doctor_design.md`.
7. `COAGENT-IMPL-NEXT-06`: PX4/UE stress-test artifact validators using
   `stress_test_artifact_validator_design.md`.
8. `COAGENT-IMPL-NEXT-09`: read-only operating metrics snapshot using
   `operating_metrics_snapshot_design.md`.
9. `COAGENT-IMPL-NEXT-12`: transport timeout and plugin-sync hardening.
10. `COAGENT-IMPL-NEXT-10`: external adoption proposal store/checker using
   `external_adoption_store_checker_design.md` if more vendor/open-source
   learning is requested before Candidate A.
11. `COAGENT-IMPL-NEXT-21`: context index and assembly checker if new scoped
   conversations are blocked by context quality risk.
12. `COAGENT-IMPL-NEXT-22`: Codex visibility drift gate if department
   visibility continues to require manual `sync-visible` repairs.
13. `COAGENT-IMPL-NEXT-23`: mailbox ledger and replay checker if
    cross-conversation communication remains unrecoverable after timeout,
    contradiction, context compaction, or session loss.
14. `COAGENT-IMPL-NEXT-25`: goal alignment checker if the next priority is
    preventing task decomposition or completion audits from weakening the
    user's objective.
15. `COAGENT-IMPL-NEXT-26`: retrospective closure checker if repeated
    failures, user corrections, review escapes, or incidents are being
    recorded without owned closeout and promotion/rejection decisions.
16. `COAGENT-IMPL-NEXT-27`: tool capability health gate checker if UE,
    MWORKS, Fab/manual import, Codex transport, Git, or external-reference
    routes become a product or dispatch bottleneck.
17. Candidate A live proof only after the above or explicit user approval to
   accept packet/transport risk.

Phase rule:

- use `implementation_sequence_and_release_plan.md` to decide the earliest
  safe phase;
- do not treat backlog presence as approval;
- any jump past R1/R2/R3 requires an explicit skip/deviation record and review
  owner acceptance.

Deviation rules:

- move Git-heavy proof earlier if a large rename/import is imminent;
- move auth/license interruption earlier if MWORKS/UE/Codex tooling blocks
  product work;
- move UE scene truth earlier if maps become the project bottleneck;
- move PX4 earlier if parameter identification becomes the project bottleneck.

## Final Audit Closeout Checklist

Before claiming this long-running goal complete, all must be true:

- every requirement in `goal_requirement_audit_map.md` has a non-partial
  verdict or an explicitly accepted deferral;
- `goal_completion_gate_protocol.md` has been applied and
  `final_goal_completion_audit.md` exists;
- `shared_task_board.md` has no stale current-state contradictions;
- `architecture_problem_matrix.md` includes all newly discovered problems and
  their statuses;
- `review_brief.md` points to every material artifact;
- required commands pass or failures are mapped to blocker packets/backlog;
- no gated implementation was silently performed;
- next implementation approvals are small, named, and reviewable;
- next implementation approval names the phase, entry evidence, exit evidence,
  and forbidden actions from `implementation_sequence_and_release_plan.md`;
- user-facing summary distinguishes design evidence from live proof and
  implementation evidence.

## Current Interim Verdict

Current expected verdict is:

```text
architecture design: substantial partial
runtime/proof implementation: not complete
goal completion: not proven
```

Reason:

The architecture is now much more concrete and auditable, but key mechanisms
remain design-level: Candidate A live proof, proof validators, context checker,
metrics snapshot, transport hardening, and product-adjacent PX4/UE proofs are
not yet executed.
