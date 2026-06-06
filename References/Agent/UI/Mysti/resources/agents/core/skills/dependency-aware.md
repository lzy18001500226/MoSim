---
id: dependency-aware
name: Dependency Aware
description: Respects project dependencies and avoids unnecessary additions
icon: dependency-aware.png
category: maintenance
activationTriggers:
  - dependency
  - package
  - library
  - npm
  - install
  - version
---

# Instructions

Understand and respect project dependencies. Avoid unnecessary additions and keep versions aligned.

## Behavioral Guidelines

- Check if functionality exists before adding deps
- Prefer well-maintained, popular packages
- Consider bundle size impact
- Keep versions consistent across monorepo
- Audit for security vulnerabilities
- Understand transitive dependencies

## Before Adding a Dependency

1. Can we implement it ourselves reasonably?
2. Does an existing dependency provide this?
3. Is the package actively maintained?
4. What's the bundle size impact?
5. Are there security concerns?
6. Does it have acceptable licensing?

## Checklist

- [ ] Functionality not available in existing deps
- [ ] Package is actively maintained (recent commits)
- [ ] Acceptable bundle size for use case
- [ ] No known security vulnerabilities
- [ ] Compatible license
- [ ] Version aligns with other project deps
