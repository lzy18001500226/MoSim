[CmdletBinding()]
param(
    [int]$FormulaId = 102,
    [string]$ManifestPath,
    [string]$GoldenPilotPath,
    [string]$OutputPath,
    [string]$EvidencePath,
    [switch]$Execute
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)

    $stream = [System.IO.File]::OpenRead($Path)
    $hash = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $hash.Dispose()
        $stream.Dispose()
    }
}

if (-not $ManifestPath) {
    $ManifestPath = Join-Path $repoRoot 'Results\report_word_layout_20260804\MATHTYPE_FORMULA_MANIFEST.json'
}
if (-not $GoldenPilotPath) {
    $GoldenPilotPath = Join-Path $repoRoot 'Results\report_word_layout_20260804\mathtype_conversion_pilot\source_omml_pilot.docx'
}
if (-not $OutputPath) {
    $OutputPath = Join-Path $repoRoot ("Results\report_word_layout_20260804\mathtype_conversion_pilot\mathml_ole_formula_{0:D3}.docx" -f $FormulaId)
}
if (-not $EvidencePath) {
    $EvidencePath = [System.IO.Path]::ChangeExtension($OutputPath, '.json')
}

$ManifestPath = [System.IO.Path]::GetFullPath($ManifestPath)
$GoldenPilotPath = [System.IO.Path]::GetFullPath($GoldenPilotPath)
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$EvidencePath = [System.IO.Path]::GetFullPath($EvidencePath)

foreach ($required in @($ManifestPath, $GoldenPilotPath)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required pilot input does not exist: $required"
    }
}
if (Test-Path -LiteralPath $OutputPath) {
    throw "Refusing to overwrite disposable pilot output: $OutputPath"
}
if (Test-Path -LiteralPath $EvidencePath) {
    throw "Refusing to overwrite pilot evidence: $EvidencePath"
}

$utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)
$manifest = [System.IO.File]::ReadAllText($ManifestPath, $utf8Strict) | ConvertFrom-Json
$formula = @($manifest.formulas | Where-Object { $_.formula_id -eq $FormulaId })
if ($formula.Count -ne 1) {
    throw "Manifest must contain exactly one formula with id $FormulaId"
}
$formula = $formula[0]

$plan = [ordered]@{
    schema = 'mosim.report.mathtype_mathml_ole_pilot.v1'
    mode = if ($Execute) { 'execute' } else { 'dry_run' }
    formula_id = $FormulaId
    expected_number = $formula.expected_number
    manifest = $ManifestPath
    manifest_sha256 = Get-Sha256 -Path $ManifestPath
    golden_pilot = $GoldenPilotPath
    golden_pilot_sha256 = Get-Sha256 -Path $GoldenPilotPath
    output = $OutputPath
    evidence = $EvidencePath
    allowed_actions = @(
        'start one isolated Word automation instance when no WINWORD process exists',
        'copy and modify only the disposable golden pilot',
        'set and read back one Equation.DSMT4 object through the configured MathML OLE format',
        'save, reopen, close, and quit only the pilot-owned Word instance'
    )
    forbidden_actions = @(
        'open, save, update, or overwrite the authoritative report',
        'attach to an existing Word process',
        'kill or restart Word or MathType',
        'accept any repair, compatibility, save-overwrite, or unknown dialog'
    )
}

if (-not $Execute) {
    $plan | ConvertTo-Json -Depth 6
    exit 0
}

$wordProcesses = @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue)
if ($wordProcesses.Count -ne 0) {
    $states = $wordProcesses | ForEach-Object { "pid=$($_.Id),responding=$($_.Responding),title=$($_.MainWindowTitle)" }
    throw "OLE pilot requires zero existing WINWORD processes: $($states -join '; ')"
}

$helperPath = Join-Path $PSScriptRoot 'MathTypeOleData.cs'
Add-Type -Path $helperPath
Copy-Item -LiteralPath $GoldenPilotPath -Destination $OutputPath

$word = $null
$document = $null
$pilotPid = 0
$status = 'failed'
$readback = $null
$failure = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($OutputPath, $false, $false, $false)
    $pilotPid = [MathTypeOleData]::WindowProcessId([long]$word.ActiveWindow.Hwnd)
    if ($pilotPid -le 0) {
        throw 'Could not resolve the pilot-owned Word process id.'
    }

    $mathTypeShapes = @()
    for ($index = 1; $index -le $document.InlineShapes.Count; $index++) {
        $shape = $document.InlineShapes.Item($index)
        try {
            if ($shape.OLEFormat.ProgID -eq 'Equation.DSMT4') {
                $mathTypeShapes += $shape
            }
        }
        catch {
        }
    }
    if ($mathTypeShapes.Count -ne 1) {
        throw "Golden pilot must contain one Equation.DSMT4 object; found $($mathTypeShapes.Count)"
    }

    $shape = $mathTypeShapes[0]
    $shape.OLEFormat.DoVerb(2)
    [MathTypeOleData]::SetPresentationMathML($shape.OLEFormat.Object, [string]$formula.mathml)
    $document.Save()
    $document.Close($false)
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) | Out-Null
    $document = $null

    $document = $word.Documents.Open($OutputPath, $false, $false, $false)
    $shape = $null
    for ($index = 1; $index -le $document.InlineShapes.Count; $index++) {
        $candidate = $document.InlineShapes.Item($index)
        try {
            if ($candidate.OLEFormat.ProgID -eq 'Equation.DSMT4') {
                $shape = $candidate
                break
            }
        }
        catch {
        }
    }
    if ($null -eq $shape) {
        throw 'Saved/reopened pilot no longer contains Equation.DSMT4.'
    }
    $shape.OLEFormat.DoVerb(2)
    $readback = [MathTypeOleData]::GetPresentationMathML($shape.OLEFormat.Object)
    if (-not $readback.Contains('<math')) {
        throw 'MathType OLE readback does not contain a MathML root.'
    }
    $status = 'ole_mathml_roundtrip_passed_pending_visual_review'
}
catch {
    $failure = "{0}: {1}" -f $_.Exception.GetType().FullName, $_.Exception.Message
    throw
}
finally {
    if ($null -ne $document) {
        try { $document.Close($false) } catch {}
        try { [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) | Out-Null } catch {}
    }
    if ($null -ne $word) {
        try { $word.Quit($false) } catch {}
        try { [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    $evidence = [ordered]@{}
    foreach ($item in $plan.GetEnumerator()) {
        $evidence[$item.Key] = $item.Value
    }
    $evidence['status'] = $status
    $evidence['failure'] = $failure
    $evidence['pilot_word_pid'] = $pilotPid
    $evidence['readback_bytes'] = if ($null -ne $readback) { [Text.Encoding]::UTF8.GetByteCount($readback) } else { 0 }
    $evidence['readback_sha256'] = if ($null -ne $readback) {
        $bytes = [Text.Encoding]::UTF8.GetBytes($readback)
        $hash = [Security.Cryptography.SHA256]::Create()
        try { ([BitConverter]::ToString($hash.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() } finally { $hash.Dispose() }
    } else { $null }
    $evidence['output_exists'] = Test-Path -LiteralPath $OutputPath -PathType Leaf
    $evidence['output_bytes'] = if ($evidence['output_exists']) { (Get-Item -LiteralPath $OutputPath).Length } else { 0 }
    $evidence['output_sha256'] = if ($evidence['output_exists']) { Get-Sha256 -Path $OutputPath } else { $null }
    $evidence['authoritative_report_touched'] = $false
    $evidenceJson = $evidence | ConvertTo-Json -Depth 8
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText(
        $EvidencePath,
        $evidenceJson + [Environment]::NewLine,
        $utf8NoBom
    )
}

$evidence | ConvertTo-Json -Depth 8
