---
id: auto-commit
name: Auto-Commit
description: Commits incrementally with safe branching practices
icon: auto-commit.png
category: workflow
activationTriggers:
  - commit
  - branch
  - save
  - checkpoint
  - incremental
---

# Instructions

Commit incrementally on feature changes, create branches to isolate work and prevent main branch pollution.

## Behavioral Guidelines

- Create feature branches for new work
- Commit frequently with meaningful messages
- Use conventional commit format
- Keep commits atomic and reversible
- Never commit directly to main/master
- Push branches regularly as backup

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

## Example Workflow

```bash
git checkout -b feature/add-user-auth
# Make changes...
git add -p  # Stage incrementally
git commit -m "feat(auth): add login endpoint"
# More changes...
git commit -m "feat(auth): add JWT validation"
git push -u origin feature/add-user-auth
```
