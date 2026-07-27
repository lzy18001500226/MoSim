# COAGENT-ARCH-LONGRUN-01 Knowledge Promotion Protocol

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define how CoAgent turns accepted lessons into durable project knowledge
without polluting docs with raw chat or unstable ideas.

## Promotion Targets

| Target | Use When |
|---|---|
| architecture doc | stable system design or protocol |
| decision record | user/PMO-approved decision or gate |
| workflow doc | repeatable operating procedure |
| skill | reusable task execution guidance |
| hook | mandatory safety or policy enforcement |
| doctor check | machine-checkable health or protocol rule |
| runtime backlog | implementation task needed |
| rejected idea archive | useful elsewhere, not accepted now |

## Promotion Gate

A lesson can be promoted only when:

- it maps to a named task or incident;
- source evidence exists;
- for external ideas, a proposal record exists under the contract in
  `external_adoption_proposal_contract.md`;
- owner accepts the lesson;
- stale alternatives are marked;
- Safety checks risk if tools/secrets/external paths are involved;
- Verification defines how to detect future regression if applicable.

## User Corrections

User corrections have high priority, but still need placement:

- behavior rule -> `AGENTS.md` or project workflow if durable;
- CoAgent architecture correction -> `CoAgent/docs/architecture/`;
- current task correction -> task board/context pack/problem matrix;
- repeated mistake -> skill, hook, or doctor check proposal.

## Stale Document Handling

When a new decision supersedes an old document:

1. update the old document or mark it superseded;
2. update reading order if needed;
3. update context packs;
4. record the change in `PROGRESS.md` if recovery-critical.

## Do Not Promote

- raw transcript excerpts;
- unverified external project claims;
- one-off speculation;
- implementation details from gated features;
- secrets or local credentials;
- broad summaries with no problem mapping.
- external ideas that have no proposal decision, evidence level, owner, review
  owner, promotion target, and verification method.

## Secretary Boundary

KnowledgeSecretaryAgent records and promotes accepted knowledge.

It does not:

- decide canonical task goals;
- own user-facing asks;
- approve unsafe actions;
- merge Git changes;
- certify product correctness.
