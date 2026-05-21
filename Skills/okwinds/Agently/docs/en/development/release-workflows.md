---
title: Release Workflows
description: Current Agently repository automation for docs, installers, and PyPI publishing.
keywords: Agently, release, GitHub Actions, PyPI, docs
---

# Release Workflows

> Languages: **English** · [中文](../../cn/development/release-workflows.md)

This page records the current main-repository automation surfaces.

## Documentation

GitHub Pages uses the `docs/` directory from the `main` branch.

The `docs/_config.yml` file records the Pages/Jekyll settings for this branch source, including the site base URL and relative Markdown link handling.

The old `docs` branch is retired and should not be used as a documentation source. Do not add workflows or release steps that publish documentation from the retired branch.

## Desktop installers

Desktop installers are not part of the current main-repository release flow.

Do not keep or re-enable desktop installer workflows only to support the retired `docs` branch flow.

## PyPI publishing

The main PyPI automation is `Publish on version change`. It runs on pushes to `main` that touch `pyproject.toml`, detects whether the package version changed, and publishes with Poetry only when the version changed.

The PyPI project list page shows the package metadata `Summary`, which comes from `[project].description` in `pyproject.toml`. The full project page renders the README from `[project].readme`.

When preparing a release:

- keep `[project].description` non-empty and concise
- keep `[project].readme` pointed at `README.md`
- do not expect PyPI metadata for an existing uploaded version to update in place; publish a new version when metadata must change publicly
