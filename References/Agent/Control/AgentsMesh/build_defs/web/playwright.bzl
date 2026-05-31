"""Playwright test runner wrapped as a Bazel test.

Delegates to `@npm//:@playwright/test/package_json.bzl`'s auto-generated
`playwright_test` rule — the aspect_rules_js pattern that rules_playwright
recommends in its `examples/rules_js` reference.

**Single-importer constraint:** `@playwright/test` MUST be declared
only in the ROOT `package.json`, never in per-workspace `package.json`
files. aspect_rules_js links each npm dependency per-importer, and
Playwright's runner has module-level state — if a spec imports the
workspace-linked copy and the runner is spawned from a different link,
Playwright raises "two different versions of @playwright/test" and
refuses to register tests. Declaring Playwright only at the root
collapses all importers onto the same link tree via pnpm hoisting.

**Browsers:** NOT fetched via `@playwright//:chromium-*` targets from
rules_playwright 0.5.3. Its hard-coded Chromium CDN pattern
(`playwright.azureedge.net/builds/chromium/%s/...`) 404s for
Playwright 1.59's Chrome-for-Testing browsers, which live at
`cdn.playwright.dev/builds/cft/<browserVersion>/...`. Run
`pnpm exec playwright install chromium` once per machine / CI runner
to populate `~/Library/Caches/ms-playwright` (or
`$PLAYWRIGHT_BROWSERS_PATH` in CI).
"""

load("@npm//:@playwright/test/package_json.bzl", _playwright_bin = "bin")

def playwright_test(
        name,
        srcs,
        config = "playwright.config.ts",
        data = None,
        env = None,
        size = "enormous",
        timeout = "eternal",
        tags = None,
        chdir = None,
        browsers_path = "",
        extra_args = None):
    """Run `playwright test` via aspect_rules_js's auto-generated bin.

    Args:
        name: Target name.
        srcs: Test files (spec.ts + fixtures).
        config: Playwright config file.
        data: Extra runfiles.
        env: Environment (BASE_URL, CI=1, ...).
        size: Bazel test size.
        timeout: Bazel timeout label.
        tags: Bazel tags; `e2e` + `manual` + `no-sandbox` auto-added.
        chdir: Working directory (defaults to package path).
        browsers_path: Absolute path to the Playwright browser cache.
            Empty means inherit from the caller's environment.
        extra_args: Additional CLI args.
    """
    merged_tags = list(tags or [])
    for required in ["e2e", "manual", "no-sandbox"]:
        if required not in merged_tags:
            merged_tags.append(required)

    merged_env = dict(env or {})
    merged_env.setdefault("CI", "1")
    if browsers_path:
        merged_env["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

    _playwright_bin.playwright_test(
        name = name,
        args = ["test", "--config", config, "--reporter=line"] + (extra_args or []),
        data = (data or []) + srcs + [config],
        env = merged_env,
        chdir = chdir or native.package_name(),
        size = size,
        timeout = timeout,
        tags = merged_tags,
    )
