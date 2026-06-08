param(
    [ValidateSet('List','MinimizeHelpers','CloseSafeErrors','Cleanup')]
    [string]$Mode = 'List',
    [string]$OutJson = '',
    [switch]$DryRun,
    [string]$AuthorizedRequestId = '',
    [Int64]$ExpectedHwnd = 0,
    [string]$ExpectedTitlePattern = '',
    [string]$ExpectedProcess = '',
    [string]$IncidentPacketPath = '',
    [string]$FixtureJson = ''
)

$ErrorActionPreference = 'Stop'

if (-not $OutJson) {
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $OutJson = "Results/mworks_window_management/manage_mworks_windows_$stamp.json"
}

$outDir = Split-Path -Parent $OutJson
if ($outDir) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

if (-not $FixtureJson) {
    Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public static class MoSimWindowOps {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindowEnabled(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    public const int SW_MINIMIZE = 6;
    public const uint WM_CLOSE = 0x0010;
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
}

function Get-WindowTextValue([IntPtr]$Handle) {
    $buffer = New-Object System.Text.StringBuilder 512
    [void][MoSimWindowOps]::GetWindowText($Handle, $buffer, $buffer.Capacity)
    return $buffer.ToString()
}

function Get-ClassNameValue([IntPtr]$Handle) {
    $buffer = New-Object System.Text.StringBuilder 256
    [void][MoSimWindowOps]::GetClassName($Handle, $buffer, $buffer.Capacity)
    return $buffer.ToString()
}

function Get-ObjectValue($Object, [string]$Name, $Default) {
    if ($null -ne $Object -and $null -ne $Object.PSObject.Properties[$Name]) {
        return $Object.PSObject.Properties[$Name].Value
    }
    return $Default
}

function Normalize-ProcessName([string]$ProcessName) {
    if (-not $ProcessName) {
        return ''
    }
    return ($ProcessName -replace '\.exe$', '')
}

function Test-ProtectedMworksWindow([string]$Title) {
    if (-not $Title) {
        return $false
    }
    return $Title -match '登录|登陆|授权|License|激活|Demo|演示|教育|错误报告|Error Report|Crash Report|发送错误报告|发送报告|Send\s*Report|重启|Restart'
}

function ConvertTo-WindowRecord(
    [Int64]$Hwnd,
    [int]$WindowPid,
    [string]$ProcessName,
    [string]$ProcessPath,
    [string]$Title,
    [string]$ClassName,
    [bool]$Visible,
    [bool]$Enabled,
    [bool]$Minimized,
    $Rect
) {
    $processName = Normalize-ProcessName $ProcessName
    $left = [int](Get-ObjectValue $Rect 'left' 0)
    $top = [int](Get-ObjectValue $Rect 'top' 0)
    $right = [int](Get-ObjectValue $Rect 'right' 0)
    $bottom = [int](Get-ObjectValue $Rect 'bottom' 0)
    $width = if ($right -ne 0 -or $left -ne 0) { $right - $left } else { [int](Get-ObjectValue $Rect 'width' 0) }
    $height = if ($bottom -ne 0 -or $top -ne 0) { $bottom - $top } else { [int](Get-ObjectValue $Rect 'height' 0) }

    $isMainWindow =
        ($processName -eq 'mworks' -and $Title -match '^Sysplorer\b')

    $isHelperWindow =
        ($processName -match '^(mw_browser_proxy|mw_crash_handler|mw_memory_monitor|sysplorer-acp-server|sysplorer_docsearch)$') -or
        ($ClassName -match '^(IME|MSCTFIME UI|QtitanTitleBarGlowWindow|Chrome_SystemMessageWindow|Chrome_WidgetWin_0|Base_PowerMessageWindow|PyInstallerOnefileHiddenWindow)$') -or
        ($Title -eq 'MWORKS.Sysplorer 2026a')

    $protectedWindow = $isMainWindow -or (Test-ProtectedMworksWindow $Title)
    $closeCandidate = (
        -not $isMainWindow -and
        $Title -match '错误|Error|报告|Report|内存警告|Memory Warning|崩溃|Crash'
    )
    $safeErrorLike = (
        $closeCandidate -and
        -not $protectedWindow
    )

    $obstructingHelper = (
        $processName -eq 'mw_browser_proxy' -and
        $Title -eq 'MWORKS' -and
        $Visible -and
        -not $Minimized -and
        $width -gt 500 -and
        $height -gt 300
    )

    return [pscustomobject]@{
        hwnd = $Hwnd
        pid = $WindowPid
        process = $processName
        process_path = $ProcessPath
        title = $Title
        class_name = $ClassName
        visible = $Visible
        enabled = $Enabled
        minimized = $Minimized
        rect = @{
            left = $left
            top = $top
            right = $right
            bottom = $bottom
            width = $width
            height = $height
        }
        main_window = $isMainWindow
        helper_window = $isHelperWindow
        protected_window = $protectedWindow
        close_candidate_window = $closeCandidate
        safe_error_window = $safeErrorLike
        obstructing_helper = $obstructingHelper
    }
}

function Get-TargetMatch($Window) {
    $expectedHwndMatches = ($ExpectedHwnd -ne 0 -and [Int64]$Window.hwnd -eq $ExpectedHwnd)
    $expectedTitleMatches = ($ExpectedTitlePattern -and $Window.title -match $ExpectedTitlePattern)
    $expectedProcessMatches = ($ExpectedProcess -and $Window.process -match $ExpectedProcess)
    $titleProcessMatches = ($ExpectedTitlePattern -and $ExpectedProcess -and $expectedTitleMatches -and $expectedProcessMatches)
    return [pscustomobject]@{
        expected_hwnd_matches = [bool]$expectedHwndMatches
        expected_title_matches = [bool]$expectedTitleMatches
        expected_process_matches = [bool]$expectedProcessMatches
        matched_expected_target = [bool]($expectedHwndMatches -or $titleProcessMatches)
        target_condition = if ($expectedHwndMatches) { 'expected_hwnd' } elseif ($titleProcessMatches) { 'expected_title_and_process' } else { 'none' }
    }
}

function Get-CloseAuthorization($Window) {
    $target = Get-TargetMatch $Window
    $missing = New-Object System.Collections.Generic.List[string]
    if (-not $AuthorizedRequestId) {
        $missing.Add('-AuthorizedRequestId') | Out-Null
    }
    if (-not $IncidentPacketPath) {
        $missing.Add('-IncidentPacketPath') | Out-Null
    }
    if (-not $target.matched_expected_target) {
        $missing.Add('-ExpectedHwnd or -ExpectedTitlePattern plus -ExpectedProcess') | Out-Null
    }

    $blockedReasons = New-Object System.Collections.Generic.List[string]
    if ($missing.Count -gt 0) {
        $blockedReasons.Add('missing authorization fields: ' + ($missing -join ', ')) | Out-Null
    }
    if ($Window.main_window) {
        $blockedReasons.Add('main Sysplorer/MWORKS window is never closed') | Out-Null
    }
    if ($Window.protected_window) {
        $blockedReasons.Add('login/license/activation/authorization/error-report/send-report/restart window is protected') | Out-Null
    }
    if (-not $Window.safe_error_window) {
        $blockedReasons.Add('window is not an approved safe-error target') | Out-Null
    }

    $authorized = (
        $missing.Count -eq 0 -and
        -not $Window.main_window -and
        -not $Window.protected_window -and
        $Window.safe_error_window
    )

    return [pscustomobject]@{
        authorized = [bool]$authorized
        why_allowed = if ($authorized) { 'explicit request id, incident packet, and expected target matched a non-main safe-error window' } else { '' }
        why_blocked = if ($authorized) { '' } else { ($blockedReasons -join '; ') }
        matched_expected_target = [bool]$target.matched_expected_target
        expected_hwnd_matches = [bool]$target.expected_hwnd_matches
        expected_title_matches = [bool]$target.expected_title_matches
        expected_process_matches = [bool]$target.expected_process_matches
        target_condition = $target.target_condition
        no_main_window_targeted = [bool](-not $Window.main_window)
    }
}

$windows = New-Object System.Collections.Generic.List[object]

if ($FixtureJson) {
    $fixture = Get-Content -LiteralPath $FixtureJson -Raw | ConvertFrom-Json
    $fixtureWindows = @()
    if ($null -ne $fixture.windows) {
        $fixtureWindows = @($fixture.windows)
    } else {
        $fixtureWindows = @($fixture)
    }
    foreach ($rawWindow in $fixtureWindows) {
        $rect = Get-ObjectValue $rawWindow 'rect' ([pscustomobject]@{})
        $processName = Get-ObjectValue $rawWindow 'process' (Get-ObjectValue $rawWindow 'process_name' '')
        $windows.Add((ConvertTo-WindowRecord `
            -Hwnd ([Int64](Get-ObjectValue $rawWindow 'hwnd' 0)) `
            -WindowPid ([int](Get-ObjectValue $rawWindow 'pid' 0)) `
            -ProcessName $processName `
            -ProcessPath (Get-ObjectValue $rawWindow 'process_path' '') `
            -Title (Get-ObjectValue $rawWindow 'title' '') `
            -ClassName (Get-ObjectValue $rawWindow 'class_name' '') `
            -Visible ([bool](Get-ObjectValue $rawWindow 'visible' $true)) `
            -Enabled ([bool](Get-ObjectValue $rawWindow 'enabled' $true)) `
            -Minimized ([bool](Get-ObjectValue $rawWindow 'minimized' $false)) `
            -Rect $rect)) | Out-Null
    }
} else {
    $callback = [MoSimWindowOps+EnumWindowsProc]{
        param([IntPtr]$Handle, [IntPtr]$LParam)

        [uint32]$windowPid = 0
        [void][MoSimWindowOps]::GetWindowThreadProcessId($Handle, [ref]$windowPid)
        $process = Get-Process -Id $windowPid -ErrorAction SilentlyContinue
        $processName = if ($process) { $process.ProcessName } else { '' }
        $processPath = ''
        if ($process) {
            try { $processPath = $process.Path } catch { $processPath = '' }
        }

        $title = Get-WindowTextValue $Handle
        $className = Get-ClassNameValue $Handle

        if (
            $processName -notmatch '^(mworks|mw_browser_proxy|mw_crash_handler|mw_memory_monitor|sysplorer-acp-server|sysplorer_docsearch)$' -and
            $title -notmatch 'MWORKS|Sysplorer|错误|Error|报告|Report|内存|Memory|登录|授权|License|Demo|演示|教育'
        ) {
            return $true
        }

        $rect = New-Object MoSimWindowOps+RECT
        [void][MoSimWindowOps]::GetWindowRect($Handle, [ref]$rect)
        $recordRect = [pscustomobject]@{
            left = $rect.Left
            top = $rect.Top
            right = $rect.Right
            bottom = $rect.Bottom
        }

        $windows.Add((ConvertTo-WindowRecord `
            -Hwnd $Handle.ToInt64() `
            -WindowPid ([int]$windowPid) `
            -ProcessName $processName `
            -ProcessPath $processPath `
            -Title $title `
            -ClassName $className `
            -Visible ([MoSimWindowOps]::IsWindowVisible($Handle)) `
            -Enabled ([MoSimWindowOps]::IsWindowEnabled($Handle)) `
            -Minimized ([MoSimWindowOps]::IsIconic($Handle)) `
            -Rect $recordRect)) | Out-Null

        return $true
    }

    [void][MoSimWindowOps]::EnumWindows($callback, [IntPtr]::Zero)
}

$actions = New-Object System.Collections.Generic.List[object]
foreach ($window in $windows) {
    if (($Mode -eq 'MinimizeHelpers' -or $Mode -eq 'Cleanup') -and $window.obstructing_helper) {
        $ok = $null
        $executed = [bool](-not $DryRun -and -not $FixtureJson)
        if ($executed) {
            $ok = [MoSimWindowOps]::ShowWindowAsync([IntPtr]$window.hwnd, [MoSimWindowOps]::SW_MINIMIZE)
        }
        $actions.Add([pscustomobject]@{
            hwnd = $window.hwnd
            pid = $window.pid
            process = $window.process
            title = $window.title
            action = 'minimize_helper'
            dry_run = [bool]$DryRun
            fixture_mode = [bool]$FixtureJson
            authorized = $true
            close_authorization_required = $false
            why_allowed = 'obstructing helper minimize is allowed without close authorization'
            why_blocked = ''
            matched_expected_target = $false
            no_main_window_targeted = [bool](-not $window.main_window)
            executed = $executed
            api_return = $ok
            main_mworks_not_targeted = -not $window.main_window
        }) | Out-Null
    }

    if (($Mode -eq 'CloseSafeErrors' -or $Mode -eq 'Cleanup') -and $window.close_candidate_window) {
        $auth = Get-CloseAuthorization $window
        $ok = $null
        $executed = [bool]($auth.authorized -and -not $DryRun -and -not $FixtureJson)
        if ($executed) {
            $ok = [MoSimWindowOps]::PostMessage([IntPtr]$window.hwnd, [MoSimWindowOps]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero)
        }
        $actions.Add([pscustomobject]@{
            hwnd = $window.hwnd
            pid = $window.pid
            process = $window.process
            title = $window.title
            action = 'close_safe_error'
            dry_run = [bool]$DryRun
            fixture_mode = [bool]$FixtureJson
            authorized = [bool]$auth.authorized
            close_authorization_required = $true
            why_allowed = $auth.why_allowed
            why_blocked = $auth.why_blocked
            matched_expected_target = [bool]$auth.matched_expected_target
            expected_hwnd_matches = [bool]$auth.expected_hwnd_matches
            expected_title_matches = [bool]$auth.expected_title_matches
            expected_process_matches = [bool]$auth.expected_process_matches
            target_condition = $auth.target_condition
            no_main_window_targeted = [bool]$auth.no_main_window_targeted
            executed = $executed
            api_return = $ok
            main_mworks_not_targeted = -not $window.main_window
        }) | Out-Null
    }
}

if (-not $FixtureJson) {
    Start-Sleep -Milliseconds 500
}

$result = [pscustomobject]@{
    schema_version = 'mosim.mworks_window_management.v2'
    created_at = (Get-Date -Format o)
    mode = $Mode
    dry_run = [bool]$DryRun
    fixture_mode = [bool]$FixtureJson
    window_count = $windows.Count
    action_count = $actions.Count
    actions = $actions
    windows = $windows
    authorization_request = @{
        authorized_request_id_present = [bool]$AuthorizedRequestId
        expected_hwnd = $ExpectedHwnd
        expected_title_pattern_present = [bool]$ExpectedTitlePattern
        expected_process_present = [bool]$ExpectedProcess
        incident_packet_path_present = [bool]$IncidentPacketPath
    }
    policy = @{
        never_close_main_mworks_sysplorer = $true
        login_license_activation_authorization_windows_are_not_closed = $true
        error_report_send_report_restart_windows_are_not_closed = $true
        helper_windows_are_minimized_only = $true
        close_safe_error_defaults_to_planned_action = $true
        close_safe_error_requires_authorized_request_id = $true
        close_safe_error_requires_incident_packet_path = $true
        close_safe_error_requires_expected_hwnd_or_title_process = $true
    }
}

$json = $result | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText(
    (Resolve-Path -LiteralPath (Split-Path -Parent $OutJson)).Path + [System.IO.Path]::DirectorySeparatorChar + (Split-Path -Leaf $OutJson),
    $json,
    (New-Object System.Text.UTF8Encoding($false))
)
Write-Output $json
