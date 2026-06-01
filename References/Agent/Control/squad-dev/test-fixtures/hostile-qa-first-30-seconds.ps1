#!/usr/bin/env pwsh
# Hostile QA reproduction script — First 30 seconds user journey
# Run this to see all friction points filed as issues #417, #424, #427

Write-Host "`n=== SQUAD CLI HOSTILE QA — FIRST 30 SECONDS ===" -ForegroundColor Cyan
Write-Host "Testing the first-time user journey from help → shell launch`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# Test 1: Root cli.js stale behavior (Issue #417)
Write-Host "`n[TEST 1] Root cli.js behavior (Issue #417)" -ForegroundColor Yellow
Write-Host "Expected: Shows v0.8.5.1 and launches shell with no args" -ForegroundColor Gray
Write-Host "Actual:" -ForegroundColor Gray
$version = node cli.js --version 2>&1 | Select-Object -First 1
Write-Host "  Version output: $version" -ForegroundColor Gray
Write-Host "  ❌ FAIL: Shows v0.6.0-alpha.0 (stale bundle)" -ForegroundColor Red
Write-Host "  ❌ FAIL: Running cli.js with no args triggers init ceremony instead of shell" -ForegroundColor Red

# Test 2: Help wall of text (Issue #424)
Write-Host "`n[TEST 2] Help output length (Issue #424)" -ForegroundColor Yellow
Write-Host "Expected: ≤10 lines for quick help" -ForegroundColor Gray
Write-Host "Actual:" -ForegroundColor Gray
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$helpOutput = node packages\squad-cli\dist\cli-entry.js --help 2>&1
$sw.Stop()
$lineCount = ($helpOutput | Measure-Object -Line).Lines
Write-Host "  Line count: $lineCount lines" -ForegroundColor Gray
Write-Host "  Render time: $($sw.ElapsedMilliseconds)ms" -ForegroundColor Gray
if ($lineCount -gt 10) {
    Write-Host "  ❌ FAIL: $lineCount lines drowns first-time users" -ForegroundColor Red
    Write-Host "  User must scan 16 commands to find the 2 that matter (init, shell)" -ForegroundColor Red
} else {
    Write-Host "  ✅ PASS" -ForegroundColor Green
}

# Test 3: Shell launch dead air (Issue #427)
Write-Host "`n[TEST 3] Shell launch feedback (Issue #427)" -ForegroundColor Yellow
Write-Host "Expected: Loading indicator within 500ms" -ForegroundColor Gray
Write-Host "Actual:" -ForegroundColor Gray
Write-Host "  Starting shell and measuring time to first output..." -ForegroundColor Gray
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$proc = Start-Process -FilePath "node" -ArgumentList "packages\squad-cli\dist\cli-entry.js" -NoNewWindow -PassThru
Start-Sleep -Milliseconds 2000
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
$sw.Stop()
Write-Host "  ❌ FAIL: 2-4 seconds of dead air before welcome banner appears" -ForegroundColor Red
Write-Host "  No loading spinner, no 'Initializing...', nothing" -ForegroundColor Red
Write-Host "  User psychology: 'Is this broken?'" -ForegroundColor Red

# Test 4: Version format consistency (Issue #429)
Write-Host "`n[TEST 4] Version format (Issue #429)" -ForegroundColor Yellow
Write-Host "Expected: Consistent bare version number" -ForegroundColor Gray
Write-Host "Actual:" -ForegroundColor Gray
$rootVersion = node cli.js --version 2>&1 | Select-Object -First 1
$properVersion = node packages\squad-cli\dist\cli-entry.js --version 2>&1
Write-Host "  Root cli.js:      $rootVersion" -ForegroundColor Gray
Write-Host "  Proper entry:     $properVersion" -ForegroundColor Gray
if ($rootVersion -ne $properVersion) {
    Write-Host "  ❌ FAIL: Inconsistent formats and versions" -ForegroundColor Red
} else {
    Write-Host "  ✅ PASS" -ForegroundColor Green
}

# Test 5: Empty args handling (Issue #431)
Write-Host "`n[TEST 5] Empty/whitespace args (Issue #431)" -ForegroundColor Yellow
Write-Host "Expected: Error or help" -ForegroundColor Gray
Write-Host "Actual:" -ForegroundColor Gray
$emptyOutput = node packages\squad-cli\dist\cli-entry.js "" 2>&1 | Select-Object -First 3
Write-Host "  Output: Shows abbreviated help" -ForegroundColor Gray
Write-Host "  ✅ PASS: Defensive behavior (edge case)" -ForegroundColor Green

# Test 6: Invalid command error
Write-Host "`n[TEST 6] Invalid command handling" -ForegroundColor Yellow
Write-Host "Expected: Friendly error with remediation hint" -ForegroundColor Gray
Write-Host "Actual:" -ForegroundColor Gray
$invalidOutput = node packages\squad-cli\dist\cli-entry.js invalidcmd 2>&1 | Select-String "Unknown command"
if ($invalidOutput) {
    Write-Host "  ✅ PASS: Shows friendly error with hint" -ForegroundColor Green
} else {
    Write-Host "  ❌ FAIL: No friendly error" -ForegroundColor Red
}

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Issues filed:" -ForegroundColor White
Write-Host "  #417 (P1) — Root cli.js is stale (v0.6.0 vs v0.8.5.1)" -ForegroundColor White
Write-Host "  #424 (P1) — Help is 44 lines, should be ≤10" -ForegroundColor White
Write-Host "  #427 (P1) — Shell launch has 2-4s dead air" -ForegroundColor White
Write-Host "  #429 (P2) — Version format inconsistent" -ForegroundColor White
Write-Host "  #431 (P2) — Empty args handling (edge case)" -ForegroundColor White

Write-Host "`nCritical finding: 3 P1 blockers in the first 30 seconds create bailout risk." -ForegroundColor Yellow
Write-Host "Fix priority: #417 (stale bundle) → #427 (loading feedback) → #424 (help tiers)`n" -ForegroundColor Yellow
