# MoSim Codex CLI Builder (Windows)
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$codexRsDir = Join-Path $scriptDir "codex-main\codex-rs"
$manifestPath = Join-Path $codexRsDir "Cargo.toml"
$lockPath = Join-Path $codexRsDir "Cargo.lock"
$codexBin = Join-Path $codexRsDir "target\release\codex.exe"

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "Cargo was not found. Install the Rust stable toolchain, reopen PowerShell, then rerun this script."
}

if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) {
    Write-Error "rustc was not found. Install the Rust stable toolchain, reopen PowerShell, then rerun this script."
}

if (-not (Test-Path -LiteralPath $manifestPath) -or -not (Test-Path -LiteralPath $lockPath)) {
    Write-Error "The vendored Codex Cargo workspace or Cargo.lock is missing: $codexRsDir"
}

Write-Host "Building vendored Codex CLI with the locked dependency graph..."
Write-Host "Cargo: $(cargo --version)"
Write-Host "Rustc: $(rustc --version)"

Push-Location $codexRsDir
try {
    & cargo build --locked --release --bin codex
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

if (-not (Test-Path -LiteralPath $codexBin)) {
    Write-Error "Cargo completed without producing the expected executable: $codexBin"
}

Write-Host "Build complete: $codexBin"
& $codexBin --version
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
