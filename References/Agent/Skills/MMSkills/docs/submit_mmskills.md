# Submit MMSkills

MMSkills is intended to grow as a community skill library. We welcome reusable multimodal skill packages from new domains such as autonomous driving, robotics, mobile agents, web agents, scientific software, games, and other visual-agent environments.

## Submission Entry

Submit a package through the GitHub issue form:

```text
https://github.com/DeepExperience/MMSkills/issues/new?template=skill_submission.yml
```

The project website also links to the same submission entry. Each submission opens a GitHub issue assigned to the maintainer account. GitHub sends email notifications according to the maintainer's repository notification settings, so new submissions can be reviewed before being added to the public library.

## Package Format

Use the same product-neutral MMSkills package format used by Codex, OpenClaw, Claude Code, and the public Hugging Face dataset:

```text
<package>/<domain>/<skill>/
├── SKILL.md
├── runtime_state_cards.json
└── Images/
```

Recommended optional files:

- `plan.json` for procedure or dependency metadata.
- `state_cards.json` for richer audit-grade state metadata.
- `README.md` only when the package is a domain collection, not for every individual skill.
- Short demo clips, logs, benchmark IDs, or trajectory excerpts that help review.

## What Reviewers Look For

- The skill describes reusable procedure knowledge rather than a single private trace.
- `SKILL.md` clearly defines applicability, preconditions, procedure, verification cues, and common failure modes.
- `runtime_state_cards.json` is compact enough for inference-time use.
- Visual references are necessary, ordered, and referenced by runtime cards.
- The package contains no credentials, API keys, private user data, or non-redistributable assets.
- The contributor has the right to release the submitted text, images, and metadata under the repository license.

## Suggested Skill Scope

Good MMSkills are narrow enough to transfer reliably:

- `AUTODRIVE_Verify_Lane_Change_Gap_And_Merge`
- `ROBOTICS_Align_Gripper_With_Target_Handle`
- `MOBILE_Configure_App_Notification_Permissions`
- `WEB_Checkout_Address_Entry_And_Verification`

Avoid monolithic skills that encode an entire benchmark episode or rely on hidden task-specific paths.

## Review Workflow

1. Contributor opens a skill submission issue from the website or GitHub issue form.
2. Maintainers receive the issue notification and inspect the package link or ZIP attachment.
3. Maintainers check package structure, licensing, visual references, and reusability.
4. Accepted packages are normalized into the MMSkills library and added to the public Hugging Face dataset.
5. The website Skill Library is regenerated so the new domain appears in the public browser.

If the submission is promising but incomplete, maintainers may request changes in the issue thread before acceptance.
