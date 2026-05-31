"""ESLint test wrapper — mirrors the `vitest_test` shape.

Drives the pnpm-linked `eslint` binary via aspect_rules_js's
`bin.eslint_test` factory with `chdir = native.package_name()` so
that ESLint v9's flat-config lookup finds `eslint.config.mjs` at the
caller's package root, and `eslint-config-next`'s internal
`require("next/dist/...")` walks up to the `next` symlink that
public_hoist_packages installed at the root `node_modules/next/`
(see MODULE.bazel).

Usage:
    load("//build_defs/web:eslint.bzl", "eslint_test")

    eslint_test(
        name = "lint",
        srcs = glob(["src/**/*.ts", "src/**/*.tsx", ...]),
    )

`bazel test //clients/web:lint` is then equivalent to running ESLint
in `clients/web/` directly — no per-app `pnpm exec eslint .` shell
shim needed, and the result is cached against the input file set
like any other Bazel test.
"""

load("@npm//:eslint/package_json.bzl", eslint_bin = "bin")

def eslint_test(
        name,
        srcs,
        config = "eslint.config.mjs",
        data = None,
        size = "medium",
        timeout = None,
        tags = None,
        chdir = None,
        max_warnings = -1):
    """Run ESLint over a TS package's sources as a Bazel test.

    Args:
        name: Target name.
        srcs: Source files to lint (`*.ts`, `*.tsx`, `*.js`, `*.mjs`).
        config: ESLint flat config file name (resolved relative to
            `chdir`). Defaults to `eslint.config.mjs`.
        data: Extra runfiles (shared configs etc).
        size: Bazel test size. Defaults to `medium`.
        timeout: Optional Bazel timeout string.
        tags: Bazel tags.
        chdir: CWD ESLint runs in. Defaults to the calling package
            so `eslint.config.mjs` is at the same level.
        max_warnings: `--max-warnings` flag value. -1 (default) means
            don't cap warnings; pass 0 to fail on any warning.
    """
    kwargs = {}
    if timeout:
        kwargs["timeout"] = timeout
    args = [
        "--no-warn-ignored",
        "--no-error-on-unmatched-pattern",
    ]
    if max_warnings >= 0:
        args.extend(["--max-warnings", str(max_warnings)])
    args.append(".")
    eslint_bin.eslint_test(
        name = name,
        args = args,
        chdir = chdir or native.package_name(),
        data = (data or []) + srcs + [config, "//:node_modules"],
        size = size,
        tags = tags or [],
        **kwargs
    )
