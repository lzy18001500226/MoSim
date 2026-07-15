param(
    [ValidateSet('MarkAlive', 'Check', 'RestartNow')]
    [string]$Mode = 'Check',
    [int]$MaxStaleMinutes = 90,
    [switch]$RestartIfStale,
    [switch]$SkipEmail,
    [string]$Source = 'windows_task',
    [string]$IncidentKind = 'codex_outer_watchdog',
    [string]$ManagerPath = 'D:\Program Files\Codex++\codex-plus-plus-manager.exe'
)

$ErrorActionPreference = 'Stop'

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$OutDir = Join-Path $Root 'Results\codex_watchdog'
$HeartbeatPath = Join-Path $OutDir 'codex_outer_cron_heartbeat.json'
$StatePath = Join-Path $OutDir 'windows_outer_watchdog_state.json'
$EmailScript = Join-Path $Root 'Scripts\agent\send_gateway_email_alert.py'

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Get-NowIso {
    return (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
}

function Write-JsonFile {
    param(
        [string]$Path,
        [hashtable]$Payload
    )
    $json = ($Payload | ConvertTo-Json -Depth 8)
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $encoding)
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return $null
    }
    try {
        return Get-Content -Path $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-CodexProcessSummary {
    $names = @('Codex', 'codex', 'codex-plus-plus', 'codex-plus-plus-manager')
    $items = @()
    foreach ($name in $names) {
        Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
            $items += [ordered]@{
                id = $_.Id
                process_name = $_.ProcessName
                main_window_title = $_.MainWindowTitle
                main_window_handle = $_.MainWindowHandle.ToString()
            }
        }
    }
    return $items
}

function Send-RestartEmail {
    param(
        [string]$Kind,
        [string]$Reason,
        [string]$CooldownKey
    )

    function U {
        param([string]$Text)
        return [regex]::Unescape($Text)
    }

    $subject = "MoSim Codex++ restart alert"
    $body = @(
        "!!! MoSim $(U '\u9700\u8981\u4eba\u5de5\u4ecb\u5165') !!!",
        "",
        "Codex++ $(U '\u7ef4\u62a4\u9762\u7591\u4f3c\u5931\u8054\uff0c\u5c06\u6309\u6388\u6743\u6d41\u7a0b\u5c1d\u8bd5\u91cd\u542f\u3002')",
        "$(U '\u539f\u56e0'):$Reason",
        "$(U '\u5982\u679c\u4f60\u5df2\u7ecf\u5728\u5904\u7406\uff0c\u53ef\u4ee5\u5ffd\u7565\u672c\u6b21\u544a\u8b66\u3002')"
    ) -join "`n"

    $args = @(
        $EmailScript,
        '--subject', $subject,
        '--body', $body,
        '--cooldown-key', $CooldownKey,
        '--cooldown-minutes', '0',
        '--timeout', '20'
    )

    try {
        $output = & python @args 2>&1
        $exit = $LASTEXITCODE
        $parsed = $null
        try {
            $parsed = ($output | Select-Object -Last 1) | ConvertFrom-Json
        } catch {
            $parsed = $null
        }
        return [ordered]@{
            ok = ($exit -eq 0)
            exit_code = $exit
            parsed = $parsed
            raw_tail = (($output | Select-Object -Last 3) -join "`n")
        }
    } catch {
        return [ordered]@{
            ok = $false
            error = "$($_.Exception.GetType().Name): $($_.Exception.Message)"
        }
    }
}

function Invoke-CodexPlusPlusRestart {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return [ordered]@{
            ok = $false
            reason = 'manager_path_missing'
            manager_path = $Path
        }
    }

    $manager = Get-Process -Name 'codex-plus-plus-manager' -ErrorAction SilentlyContinue | Select-Object -First 1
    $started = $false
    if (-not $manager) {
        Start-Process -FilePath $Path -WindowStyle Minimized | Out-Null
        $started = $true
        Start-Sleep -Seconds 3
        $manager = Get-Process -Name 'codex-plus-plus-manager' -ErrorAction SilentlyContinue | Select-Object -First 1
    }

    if (-not $manager) {
        return [ordered]@{
            ok = $false
            reason = 'manager_process_not_found_after_start'
            manager_path = $Path
            process_started = $started
        }
    }

    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes

    $deadline = (Get-Date).AddSeconds(20)
    $button = $null
    $windowName = ''
    $restartButtonName = ([string]([char]0x91CD) + [string]([char]0x542F) + ' Codex++')
    while ((Get-Date) -lt $deadline -and -not $button) {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $procCond = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
            $manager.Id
        )
        $windows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, $procCond)
        foreach ($window in $windows) {
            $windowName = $window.Current.Name
            $nameCond = New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::NameProperty,
                $restartButtonName
            )
            $button = $window.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $nameCond)
            if ($button) {
                break
            }
        }
        if (-not $button) {
            Start-Sleep -Milliseconds 500
        }
    }

    if (-not $button) {
        return [ordered]@{
            ok = $false
            reason = 'restart_button_not_found'
            manager_path = $Path
            process_id = $manager.Id
            process_started = $started
            last_window_name = $windowName
        }
    }

    try {
        $pattern = $button.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $pattern.Invoke()
        Start-Sleep -Seconds 3
        return [ordered]@{
            ok = $true
            method = 'UIAutomation InvokePattern'
            manager_path = $Path
            process_id = $manager.Id
            process_started = $started
            button_name = 'restart Codex++'
            window_name = $windowName
        }
    } catch {
        return [ordered]@{
            ok = $false
            reason = 'invoke_failed'
            error = "$($_.Exception.GetType().Name): $($_.Exception.Message)"
            manager_path = $Path
            process_id = $manager.Id
            process_started = $started
            button_name = 'restart Codex++'
            window_name = $windowName
        }
    }
}

function New-EvidencePath {
    param([string]$Prefix)
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    return Join-Path $OutDir "$Prefix`_$stamp.json"
}

Set-Location $Root

if ($Mode -eq 'MarkAlive') {
    $payload = [ordered]@{
        timestamp = Get-NowIso
        mode = $Mode
        source = $Source
        status = 'alive_marker_written'
        thread_id = '019e9bc1-ea9f-7102-b41a-4ef9b2308992'
        department_name = 'MoSim legacy ops patrol'
        claim_boundary = 'This marker proves the detached automation job ran, not that the legacy ops patrol visible thread accepted a turn.'
    }
    Write-JsonFile -Path $HeartbeatPath -Payload $payload
    Write-JsonFile -Path (New-EvidencePath 'codex_outer_cron_mark_alive') -Payload $payload
    $payload | ConvertTo-Json -Depth 8
    exit 0
}

$now = Get-Date
$heartbeat = Read-JsonFile -Path $HeartbeatPath
$heartbeatAgeMinutes = $null
$heartbeatStatus = 'missing'
if ($heartbeat -and $heartbeat.timestamp) {
    try {
        $heartbeatTime = [datetime]::Parse([string]$heartbeat.timestamp)
        $heartbeatAgeMinutes = [math]::Round(($now - $heartbeatTime).TotalMinutes, 2)
        $heartbeatStatus = if ($heartbeatAgeMinutes -le $MaxStaleMinutes) { 'fresh' } else { 'stale' }
    } catch {
        $heartbeatStatus = 'unparseable'
    }
}

$processes = Get-CodexProcessSummary
$codexAppProcesses = @($processes | Where-Object { $_.process_name -eq 'Codex' -or $_.process_name -eq 'codex-plus-plus' })
$incident = ($Mode -eq 'RestartNow') -or ($heartbeatStatus -ne 'fresh') -or ($codexAppProcesses.Count -eq 0)
$reasonParts = New-Object System.Collections.Generic.List[string]
if ($Mode -eq 'RestartNow') { $reasonParts.Add('forced_restart_incident') | Out-Null }
if ($heartbeatStatus -ne 'fresh') { $reasonParts.Add("outer_cron_heartbeat_$heartbeatStatus") | Out-Null }
if ($codexAppProcesses.Count -eq 0) { $reasonParts.Add('codex_app_process_missing') | Out-Null }
if ($reasonParts.Count -eq 0) { $reasonParts.Add('healthy') | Out-Null }
$reason = ($reasonParts -join ';')

$record = [ordered]@{
    timestamp = Get-NowIso
    mode = $Mode
    source = $Source
    status = if ($incident) { 'incident_detected' } else { 'healthy' }
    incident_kind = $IncidentKind
    reason = $reason
    max_stale_minutes = $MaxStaleMinutes
    heartbeat_path = $HeartbeatPath
    heartbeat_status = $heartbeatStatus
    heartbeat_age_minutes = $heartbeatAgeMinutes
    codex_process_count = $codexAppProcesses.Count
    processes = $processes
    restart_requested = [bool]($incident -and ($RestartIfStale -or $Mode -eq 'RestartNow'))
    claim_boundary = 'This watchdog does not inspect Codex private databases or session files. It detects stale detached automation evidence or missing visible Codex processes, then follows the email-before-restart route.'
}

if ($incident -and ($RestartIfStale -or $Mode -eq 'RestartNow')) {
    $cooldownKey = "codex-restart:${IncidentKind}:" + (Get-Date -Format 'yyyyMMdd_HHmmss')
    if ($SkipEmail) {
        $record.email_result = [ordered]@{
            ok = $null
            skipped = $true
            reason = 'skip_email_requested'
            note = 'Caller is responsible for recording the mandatory pre-restart email audit.'
        }
    } else {
        $record.email_result = Send-RestartEmail -Kind $IncidentKind -Reason $reason -CooldownKey $cooldownKey
    }
    $record.restart_result = Invoke-CodexPlusPlusRestart -Path $ManagerPath
}

Write-JsonFile -Path $StatePath -Payload $record
$evidencePath = New-EvidencePath 'codex_outer_watchdog_check'
Write-JsonFile -Path $evidencePath -Payload $record
$record.evidence_path = $evidencePath
$record | ConvertTo-Json -Depth 10
