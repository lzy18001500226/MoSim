# Project Bootstrap Boundary

This reference defines the reusable project-start pattern for CoAgent.

## Purpose

Every host project may have a project-local adapter:

```text
C:\Users\HP\Desktop\<Project>\CoAgent
```

The adapter lets a fresh Codex conversation find project routes, packet paths,
permissions, and workflow adapters without reading another project's private
state.

## Layer Split

| Layer | Path | Owns | Must Not Own |
|---|---|---|---|
| Global CoAgent core | `C:\Users\HP\Desktop\CoAgent` | reusable skills, scripts, schemas, protocol templates, generic operating docs, capability cards | project thread ids, project packets, project acceptance decisions, project evidence facts |
| Project CoAgent adapter | `C:\Users\HP\Desktop\<Project>\CoAgent` | project registry, adapter docs, packet path mapping, project permission boundary, project board integration | reusable skill source, global scripts as forked copies, unrelated project state |

The current MoSim repository may temporarily host portable CoAgent assets until
the project is complete. Do not migrate or move files as part of bootstrap
unless the user explicitly starts a migration task.

## Generated Adapter Meaning

The bootstrap adapter is a scaffold. It does not imply:

- any Codex thread exists;
- any scheduler is running;
- any email channel is configured;
- any visible department is approved;
- any global core path is trusted for project facts.

The host project's `AGENTS.md` or equivalent entry document should later state
whether reading the global CoAgent core is allowed.

## Default Project Rule

For a new project, the recommended entry rule is:

```text
The project may read C:\Users\HP\Desktop\CoAgent as the local reusable CoAgent
core for skills, scripts, schemas, and portable operating procedures. Project
facts, task state, packets, evidence, and acceptance decisions remain under
this project directory unless the user approves a named infrastructure action.
```

## No-Loss Migration Rule

Bootstrap is not migration. If an existing project already has CoAgent files:

1. audit existing files;
2. create a section-level migration map;
3. preserve host-local facts in the host project;
4. copy only portable rules into the global core after review;
5. never delete first.
