# Skill Risk Taxonomy (For Reviews)

Use this as a checklist when auditing *any* skill.

## Security

- **Command injection**: untrusted input interpolated into shell commands; `eval`; unsafe quoting.
- **Destructive operations**: deletes, overwrites, migrations, irreversible state changes.
- **Privilege escalation**: `sudo`, system config edits, credential store access.
- **Insecure defaults**: e.g. binding `0.0.0.0`, disabling TLS verification, permissive CORS.

## Privacy & Data Handling

- **Secrets exposure**: API keys in logs, examples that print env vars, copying tokens into chat.
- **Data exfiltration**: uploading files/logs to third parties; “paste full config here”.
- **Sensitive data retention**: writing outputs to shared locations, leaving temp files.

## Safety & Integrity

- **Prompt injection**: instructions to fetch external content and follow it blindly.
- **Unverified execution**: “run this script” without review or validation steps.
- **Ambiguous authority**: wording that discourages verification (“always do X”, “skip checks”).

## Supply Chain

- **Unpinned dependencies**: `latest`, floating versions, untrusted registries.
- **Install-time scripts**: `postinstall`, curl | bash patterns, remote installers.
- **Provenance gaps**: no source URL, unclear origin, no update cadence.

## Reliability & UX

- **Non-determinism**: relies on external services without retries/caching; race conditions.
- **Environment coupling**: OS-specific assumptions; missing prerequisites.
- **Context bloat**: large SKILL.md body that crowds out task context.

## Rating Guidance (Simple)

- **Severity**: impact if it goes wrong (Low/Med/High/Critical)
- **Likelihood**: how easy/likely to trigger (Rare/Possible/Likely)

