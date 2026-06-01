# oh-my-claudecode v4.14.4: Native Windows hook manifest hotfix

## Release Notes

Hotfix release for the native Windows hook regression still present in the published v4.14.3 marketplace package.

### Highlights

- Ships plugin `hooks/hooks.json` with direct `node "$CLAUDE_PLUGIN_ROOT"/scripts/run.cjs ...` commands for every hook event, so native Windows no longer invokes `sh`, `/bin/sh`, or `find-node.sh` from the manifest. (#3121, #3124)
- Preserves macOS/Linux setup-cache repair to `find-node.sh` for non-interactive shells where nvm/fnm may not expose `node` on PATH. (#3124)
- Keeps doctor coverage for stale Windows plugin manifests and tightens test isolation so user/global MCP registry state cannot create false conflict failures in focused checks.

### Bug Fixes

- **Fix native Windows plugin hook manifest commands** (#3124)
- **Keep ralplan compact continuation read-only** (dev-only follow-up after v4.14.3)

### Install / Update

```bash
npm install -g oh-my-claude-sisyphus@4.14.4
```

Or reinstall/update the Claude plugin from the marketplace when v4.14.4 appears.

**Full Changelog**: https://github.com/Yeachan-Heo/oh-my-claudecode/compare/v4.14.3...v4.14.4

## Contributors

Thank you to all contributors who made this release possible!

@Yeachan-Heo
