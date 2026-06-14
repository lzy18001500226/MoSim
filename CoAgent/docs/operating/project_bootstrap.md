# CoAgent Project Bootstrap

Status: portable scaffold rule, 2026-06-12 CST.

This document defines the default CoAgent layout for a new host project. It is
not a migration order for the current MoSim project.

## 1. Default Layout

For a new project under the Desktop, create a project-local adapter:

```text
C:\Users\HP\Desktop\<Project>\CoAgent
```

This folder is the host-project adapter. It records project routes, packet
paths, workflow adapters, permission boundaries, and evidence mapping.

The future reusable core can live at:

```text
C:\Users\HP\Desktop\CoAgent
```

The reusable core owns generic skills, scripts, schemas, protocol templates,
and portable operating docs. It must not own project thread ids, project
packets, project acceptance decisions, or project evidence facts.

## 2. Bootstrap Skill

Use the project-local skill:

```text
CoAgent/skills/coagent-project-bootstrap/SKILL.md
```

The skill wraps:

```text
CoAgent/skills/coagent-project-bootstrap/scripts/bootstrap_project_coagent.py
```

Default behavior is dry-run. Applying the scaffold requires `--apply`.
Existing files are skipped unless `--overwrite` is explicitly passed.

## 3. Generated Adapter

The minimal scaffold is:

```text
<Project>\CoAgent\README.md
<Project>\CoAgent\dispatch\department_threads.json
<Project>\CoAgent\docs\adapters\README.md
<Project>\CoAgent\protocol\README.md
```

This scaffold does not create Codex threads, start schedulers, configure email,
approve visible departments, or grant runtime authority.

## 4. New Project Entry Rule

When a host project is allowed to use the global core, add a rule like this to
that project's entry document:

```text
The project may read C:\Users\HP\Desktop\CoAgent as the local reusable CoAgent
core for skills, scripts, schemas, and portable operating procedures. Project
facts, task state, packets, evidence, and acceptance decisions remain under
this project directory unless the user approves a named infrastructure action.
```

## 5. MoSim Boundary

MoSim currently hosts portable CoAgent assets inside its repository while the
project is still active. Do not move, rename, or delete those files as part of
project bootstrap. A future desktop-level migration must use the no-loss
migration process and separate portable core content from MoSim host-local
facts.
