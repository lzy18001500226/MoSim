# Releasing Claude Swarm

This guide walks through the process of releasing a new version of Claude Swarm.

## Prerequisites

- Ensure you have push access to the repository
- Ensure the `RUBYGEMS_AUTH_TOKEN` secret is configured in GitHub repository settings
- Ensure all tests are passing on the main branch

## Release Steps

### 1. Update Version

Edit `lib/claude_swarm/version.rb` and update the version number:

```ruby
module ClaudeSwarm
  VERSION = "0.1.8"  # Update this
end
```

### 2. Update Changelog

Move items from the `[Unreleased]` section to a new version section in `CHANGELOG.md`:

```markdown
## [Unreleased]

## [0.1.8] - 2025-06-02

### Added
- Feature X

### Changed
- Enhancement Y

### Fixed
- Bug Z
```

### 3. Commit Changes

```bash
git add lib/claude_swarm/version.rb CHANGELOG.md
git commit -m "Bump version to 0.1.8"
```

### 4. Create and Push Tag

```bash
git tag -a v0.1.8 -m "Release version 0.1.8"
git push origin main
git push origin v0.1.8
```

### 5. Review Draft Release

The GitHub workflow will automatically create a draft release. Review it at:
https://github.com/parruda/claude-swarm/releases

### 6. Publish Release

Once you're satisfied with the release notes, click "Publish release". This will trigger the workflow to:
- Run tests
- Build the gem
- Publish to RubyGems.org
- Publish to GitHub Packages

### 7. Verify Publication

Check that the gem was published successfully:
- RubyGems: https://rubygems.org/gems/claude_swarm
- GitHub Packages: https://github.com/parruda/claude-swarm/packages

## Troubleshooting

### Failed Publication

If the release workflow fails:

1. Check the workflow logs at: https://github.com/parruda/claude-swarm/actions
2. Common issues:
   - Invalid `RUBYGEMS_AUTH_TOKEN` secret
   - Test failures
   - RuboCop violations
   - Network issues

### Manual Release

If you need to release manually:

```bash
# Ensure you're on the correct tag
git checkout v0.1.8

# Build the gem
gem build claude_swarm.gemspec

# Push to RubyGems (requires credentials)
gem push claude_swarm-0.1.8.gem
```

## Post-Release

After a successful release:

1. Create a new `[Unreleased]` section in `CHANGELOG.md`
2. Announce the release (optional)
3. Update any dependent projects