# MoSim Codex CLI

`src/Agent/codex-main/` contains the vendored OpenAI Codex CLI source snapshot.
It is part of the MoSim delivery so a copied repository can build the same local
Codex client. The source is licensed under Apache-2.0; retain
`codex-main/LICENSE` and `codex-main/NOTICE` in every redistribution.

`CODEX_SOURCE_MANIFEST.json` records the imported-source tree fingerprint,
anchor hashes, license files, and the security-scan baseline. The imported
snapshot did not retain an upstream Git revision, so the manifest and the MoSim
release commit together identify the exact delivered source tree.

`.gitattributes` disables Git whitespace diagnostics only below `codex-main/`.
That preserves upstream test fixtures and terminal frames byte-for-byte; the
MoSim bridge, build scripts, manifest, and documentation stay under normal
whitespace checks.

Codex CLI is a client and agent runtime, not GPT model weights. The Model Studio
AI tab uses the GPT provider and authentication configured for Codex on the
current machine. No API key, token, or user `CODEX_HOME` state belongs in this
repository.

## Build

The build is optional. Skipping it does not affect MWORKS models, simulation,
metrics, or code generation.

### Windows

Install Rust stable and the Visual Studio C++ Build Tools first, then run:

```powershell
cd $env:MOSIM_ROOT\src\Agent
.\build_codex.ps1
```

Expected output:

```text
src\Agent\codex-main\codex-rs\target\release\codex.exe
```

The imported Codex source documentation lists Windows 11 through WSL2 as its
documented system path. `build_codex.ps1` is a MoSim native-Windows convenience
entry point so Studio can launch an `.exe`; it must be treated as unverified
until the target machine completes the build and `codex.exe --version` check.
Do not substitute a WSL ELF binary for the Windows Studio bridge.

### Linux / macOS

Install Rust stable and a native C/C++ toolchain first, then run:

```bash
cd "${MOSIM_ROOT}/src/Agent"
./build_codex.sh
```

Expected output:

```text
src/Agent/codex-main/codex-rs/target/release/codex
```

Both scripts call `cargo build --locked --release --bin codex`. They never
silently install Rust, `just`, or other global tools, and use the vendored
`Cargo.lock` to prevent dependency resolution drift. The first build can still
download the lockfile-pinned crates and Git dependencies, so it requires network
access unless the local Cargo cache is already populated.

## GPT Configuration

After building, configure Codex once in the user's normal `CODEX_HOME`:

```powershell
& "$env:MOSIM_ROOT\src\Agent\codex-main\codex-rs\target\release\codex.exe" login
& "$env:MOSIM_ROOT\src\Agent\codex-main\codex-rs\target\release\codex.exe" login status
```

```bash
"${MOSIM_ROOT}/src/Agent/codex-main/codex-rs/target/release/codex" login
"${MOSIM_ROOT}/src/Agent/codex-main/codex-rs/target/release/codex" login status
```

For API-key authentication, use Codex's `login --with-api-key` flow from a
protected terminal. Do not put a key in MoSim, a command history file, a
Studio field, or a project configuration file. Merge
`codex.config.example.toml` into the user's `CODEX_HOME/config.toml` when a
specific GPT model or compatible provider endpoint is required.

The Model Studio bridge deliberately removes API-key environment variables from
the child `codex exec` process. It relies on the user's Codex login state so an
assistant request cannot expose a shell-inherited key.

## Studio Integration

The fourth Model Studio tab starts this local chain on the first question:

```text
Model Studio (Julia)
  -> loopback HTTP bridge (127.0.0.1)
  -> Scripts/agent/codex_cli_agent_server.py
  -> src/Agent/codex-main/codex-rs/target/release/codex
  -> configured GPT provider
```

The bridge accepts only loopback requests and runs `codex exec` with a
read-only sandbox and no approval bypass. It may inspect project files to
answer a question, but cannot modify project files, start MWORKS simulation,
generate code, or send QGC/Gazebo/PX4 commands. The prior
`mworks_analysis_agent_server.py` Responses backend remains only as a legacy
implementation; Studio no longer starts it.

If a debug build is needed, set `MOSIM_CODEX_BIN` to an executable under the
current repository. The bridge rejects overrides outside `MOSIM_ROOT`.

## Verification

```powershell
& "$env:MOSIM_ROOT\src\Agent\codex-main\codex-rs\target\release\codex.exe" --version
python -m unittest Scripts.agent.tests.test_codex_cli_agent_server
```

```bash
"${MOSIM_ROOT}/src/Agent/codex-main/codex-rs/target/release/codex" --version
python -m unittest Scripts.agent.tests.test_codex_cli_agent_server
```

The current source identity is bound by the vendored `Cargo.toml` and
`Cargo.lock`; their SHA256 values and the full source-tree fingerprint are
recorded in `CODEX_SOURCE_MANIFEST.json` and `RELEASE_CHECKLIST.md`.

## Security Scan Baseline

The initial `gitleaks` scan reports 13 signatures inside the upstream source:
test fixtures, documentation examples, or hash constants. They are retained
unchanged because this is a source snapshot, not MoSim credential material.
Their exact fingerprints are constrained in `.gitleaksignore`, so a new file or
line is not implicitly ignored. No project credential is permitted under
`src/Agent/`; rerun the scan after an upstream refresh and investigate any new
finding before release.

```powershell
gitleaks detect --source src/Agent --no-git --gitleaks-ignore-path src/Agent
```
