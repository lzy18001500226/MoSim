[CmdletBinding()]
param(
    [string]$GoldenPilotPath,
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

if (-not $GoldenPilotPath) {
    $GoldenPilotPath = Join-Path $repoRoot 'Results\report_word_layout_20260804\mathtype_conversion_pilot\source_omml_pilot.docx'
}
if (-not $EvidencePath) {
    $EvidencePath = Join-Path $repoRoot 'Results\report_word_layout_20260804\mathtype_conversion_pilot\mathtype_mathml_ole_format_probe_20260804.json'
}

$GoldenPilotPath = [System.IO.Path]::GetFullPath($GoldenPilotPath)
$EvidencePath = [System.IO.Path]::GetFullPath($EvidencePath)
if (-not (Test-Path -LiteralPath $GoldenPilotPath -PathType Leaf)) {
    throw "Required disposable pilot does not exist: $GoldenPilotPath"
}

$plan = [ordered]@{
    schema = 'mosim.report.mathtype_mathml_ole_format_probe.v1'
    mode = if ($Execute) { 'execute' } else { 'dry_run' }
    authorization_requirement = 'Live execution requires the owner thread to explicitly authorize this disposable read-only probe.'
    golden_pilot = $GoldenPilotPath
    golden_pilot_sha256 = Get-Sha256 -Path $GoldenPilotPath
    evidence = $EvidencePath
    allowed_actions = @(
        'require zero existing WINWORD processes',
        'start one isolated Word automation instance',
        'open only the disposable golden pilot read-only',
        'start the existing Equation.DSMT4 OLE server through the documented RunForConversion verb',
        'enumerate IDataObject DATADIR_GET and DATADIR_SET formats and call QueryGetData only for GET formats',
        'close and quit only the pilot-owned Word instance'
    )
    forbidden_actions = @(
        'open, save, update, or overwrite the authoritative report',
        'call IDataObject.SetData or IDataObject.GetData',
        'modify or save the disposable golden pilot',
        'attach to an existing Word process',
        'kill or restart Word or MathType',
        'accept repair, compatibility, overwrite, or unknown dialogs',
        'perform a multi-formula conversion batch'
    )
    probe_contract = [ordered]@{
        enumeration_direction = 'DATADIR_GET,DATADIR_SET'
        requested_mathml_clipboard_formats = @(
            'MathML Presentation',
            'MathML',
            'application/mathml+xml'
        )
        ole_activation = 'OLEFormat.DoVerb(2) / documented RunForConversion verb'
        set_data_invoked = $false
        get_data_invoked = $false
    }
}

if (-not $Execute) {
    $plan | ConvertTo-Json -Depth 8
    exit 0
}

if (Test-Path -LiteralPath $EvidencePath) {
    throw "Refusing to overwrite format-probe evidence: $EvidencePath"
}

$wordProcesses = @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue)
if ($wordProcesses.Count -ne 0) {
    $states = $wordProcesses | ForEach-Object { "pid=$($_.Id),responding=$($_.Responding),title=$($_.MainWindowTitle)" }
    throw "Read-only OLE format probe requires zero existing WINWORD processes: $($states -join '; ')"
}

$helperPath = Join-Path $PSScriptRoot 'MathTypeOleData.cs'
Add-Type -Path $helperPath

$word = $null
$document = $null
$shape = $null
$oleObject = $null
$mathTypeShapes = @()
$pilotPid = 0
$probe = $null
$status = 'failed'
$failure = $null
$oleVerbIndex = 2
$oleActivationAttempted = $false
$oleActivationCompleted = $false
$oleObjectAvailable = $false
$beforeSha256 = Get-Sha256 -Path $GoldenPilotPath
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($GoldenPilotPath, $false, $true, $false)
    if (-not $document.ReadOnly) {
        throw 'The disposable golden pilot did not open read-only.'
    }
    $pilotPid = [MathTypeOleData]::WindowProcessId([long]$word.ActiveWindow.Hwnd)
    if ($pilotPid -le 0) {
        throw 'Could not resolve the pilot-owned Word process id.'
    }

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
    # MathType's SDK requires the OLE server to be started before Object is
    # queried. This verb activates the existing OLE server; no document save or
    # IDataObject write/read operation is performed by this probe.
    $oleActivationAttempted = $true
    $shape.OLEFormat.DoVerb($oleVerbIndex)
    $oleActivationCompleted = $true
    $oleObject = $shape.OLEFormat.Object
    $oleObjectAvailable = ($null -ne $oleObject)
    if (-not $oleObjectAvailable) {
        throw 'MathType OLE server did not expose OLEFormat.Object after DoVerb.'
    }
    $probe = [MathTypeOleData]::ProbeMathMLFormats($oleObject)
    $status = 'read_only_format_probe_completed_pending_review'
}
catch {
    $failure = "{0}: {1}" -f $_.Exception.GetType().FullName, $_.Exception.Message
    throw
}
finally {
    if ($null -ne $document) {
        foreach ($comObject in @($oleObject, $shape)) {
            if ($null -ne $comObject) {
                try {
                    if ([System.Runtime.InteropServices.Marshal]::IsComObject($comObject)) {
                        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($comObject) | Out-Null
                    }
                }
                catch {}
            }
        }
        $mathTypeShapes = @()
        $oleObject = $null
        $shape = $null
        try { $document.Close($false) } catch {}
        try { [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) | Out-Null } catch {}
    }
    if ($null -ne $word) {
        try { $word.Quit($false) } catch {}
        try { [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    $afterSha256 = Get-Sha256 -Path $GoldenPilotPath
    $remainingWordProcesses = @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue | ForEach-Object {
        [ordered]@{ pid = $_.Id; responding = $_.Responding; title = $_.MainWindowTitle }
    })
    $evidence = [ordered]@{}
    foreach ($item in $plan.GetEnumerator()) {
        $evidence[$item.Key] = $item.Value
    }
    $evidence['status'] = $status
    $evidence['failure'] = $failure
    $evidence['pilot_word_pid'] = $pilotPid
    $evidence['pilot_read_only'] = $true
    $evidence['ole_verb_index'] = $oleVerbIndex
    $evidence['ole_activation_attempted'] = $oleActivationAttempted
    $evidence['ole_activation_completed'] = $oleActivationCompleted
    $evidence['ole_object_available'] = $oleObjectAvailable
    $evidence['golden_pilot_sha256_before'] = $beforeSha256
    $evidence['golden_pilot_sha256_after'] = $afterSha256
    $evidence['golden_pilot_unchanged'] = ($beforeSha256 -eq $afterSha256)
    $evidence['authoritative_report_touched'] = $false
    $evidence['remaining_winword_processes'] = $remainingWordProcesses
    $evidence['ole_format_probe'] = $probe
    $evidenceJson = $evidence | ConvertTo-Json -Depth 12
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText(
        $EvidencePath,
        $evidenceJson + [Environment]::NewLine,
        $utf8NoBom
    )
}

$evidence | ConvertTo-Json -Depth 12
