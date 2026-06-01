---
"@bradygaster/squad-cli": patch
---

docs: add fork contribution workflow to CONTRIBUTING.md

Closes five gaps discovered during PR #217:
- Fork-first setup instructions (fork → clone → upstream remote)
- PR must target `dev` branch, not `main` (`gh pr create --base dev`)
- Changeset is a required step in the PR process checklist
- `bradygaster/dev` now correctly described as the PR target for all contributions
- New "Keeping Your Fork in Sync" section with rebase-on-upstream/dev instructions
