---
name: coagent-project-bootstrap
description: Initialize or audit a project-local CoAgent adapter folder for a new workspace. Use when a user starts a new project, asks to create a Desktop project CoAgent folder, asks how a project should reference a global CoAgent core, or wants a reusable project bootstrap skill instead of hand-written setup instructions.
---

# CoAgent Project Bootstrap

Use this skill to create or audit the project-local CoAgent adapter layer for a
workspace. It does not migrate an existing project into a desktop-level
CoAgent core and does not move current project state.

## Boundary

Keep two layers separate:

```text
C:\Users\HP\Desktop\CoAgent
  reusable core: skills, scripts, schemas, portable operating docs

C:\Users\HP\Desktop\<Project>\CoAgent
  project adapter: registry, packet paths, board adapters, project permissions
```

The global core provides capability. The project adapter owns project facts,
thread ids, packet locations, board state, and evidence mapping.

Read `references/project_bootstrap_boundary.md` before changing bootstrap
behavior or explaining the architecture.

## Workflow

1. Identify the target project root. If the user does not provide one, use the
   current workspace root.
2. Decide the global CoAgent core path. Default to
   `C:\Users\HP\Desktop\CoAgent`, but do not require it to exist during a
   project-local dry run.
3. Run the bundled script in plan mode first:

```powershell
python CoAgent/skills/coagent-project-bootstrap/scripts/bootstrap_project_coagent.py `
  --project-root "C:\Users\HP\Desktop\<Project>" `
  --global-coagent-root "C:\Users\HP\Desktop\CoAgent" `
  --json
```

4. Review the planned files. If the target already contains important project
   files, do not overwrite them unless the user explicitly asks.
5. Apply only after the target is correct:

```powershell
python CoAgent/skills/coagent-project-bootstrap/scripts/bootstrap_project_coagent.py `
  --project-root "C:\Users\HP\Desktop\<Project>" `
  --global-coagent-root "C:\Users\HP\Desktop\CoAgent" `
  --apply `
  --json
```

6. Report created/skipped files and any blockers. Do not claim that runtime
   dispatch, scheduler, email, thread tools, or window automation is configured
   unless a separate workflow proves it.

## Script Contract

The script creates a minimal adapter:

```text
<Project>\CoAgent\README.md
<Project>\CoAgent\dispatch\department_threads.json
<Project>\CoAgent\docs\adapters\README.md
<Project>\CoAgent\protocol\README.md
```

It is non-destructive by default:

- no `--apply`: print a plan only;
- existing files are skipped unless `--overwrite` is passed;
- files outside `<Project>\CoAgent` are never modified;
- the global core path is recorded as a pointer only.

## Completion Rules

Complete when the adapter exists or the dry-run plan is produced and the user
has enough information to approve application.

Block when:

- target project root is ambiguous;
- target path resolves outside the intended project;
- existing adapter files conflict and overwrite is not authorized;
- filesystem operations fail.
