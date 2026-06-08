param(
    [ValidateSet('List','MinimizeHelpers','CloseSafeErrors','Cleanup')]
    [string]$Mode = 'List',
    [string]$OutJson = '',
    [switch]$DryRun
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

$windows = New-Object System.Collections.Generic.List[object]
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
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    $visible = [MoSimWindowOps]::IsWindowVisible($Handle)
    $enabled = [MoSimWindowOps]::IsWindowEnabled($Handle)
    $minimized = [MoSimWindowOps]::IsIconic($Handle)

    $isMainWindow =
        ($processName -eq 'mworks' -and $title -match '^Sysplorer\b')

    $isHelperWindow =
        ($processName -match '^(mw_browser_proxy|mw_crash_handler|mw_memory_monitor|sysplorer-acp-server|sysplorer_docsearch)$') -or
        ($className -match '^(IME|MSCTFIME UI|QtitanTitleBarGlowWindow|Chrome_SystemMessageWindow|Chrome_WidgetWin_0|Base_PowerMessageWindow|PyInstallerOnefileHiddenWindow)$') -or
        ($title -eq 'MWORKS.Sysplorer 2026a')

    $licenseOrLoginLike = $title -match '登录|登陆|授权|License|激活|Demo|演示|教育|Sysplorer'
    $safeErrorLike = (
        -not $isMainWindow -and
        -not $licenseOrLoginLike -and
        $title -match '错误|Error|报告|Report|内存警告|Memory Warning|崩溃|Crash'
    )

    $obstructingHelper = (
        $processName -eq 'mw_browser_proxy' -and
        $title -eq 'MWORKS' -and
        $visible -and
        -not $minimized -and
        $width -gt 500 -and
        $height -gt 300
    )

    $windows.Add([pscustomobject]@{
        hwnd = $Handle.ToInt64()
        pid = [int]$windowPid
        process = $processName
        process_path = $processPath
        title = $title
        class_name = $className
        visible = $visible
        enabled = $enabled
        minimized = $minimized
        rect = @{
            left = $rect.Left
            top = $rect.Top
            right = $rect.Right
            bottom = $rect.Bottom
            width = $width
            height = $height
        }
        main_window = $isMainWindow
        helper_window = $isHelperWindow
        safe_error_window = $safeErrorLike
        obstructing_helper = $obstructingHelper
    }) | Out-Null

    return $true
}

[void][MoSimWindowOps]::EnumWindows($callback, [IntPtr]::Zero)

$actions = New-Object System.Collections.Generic.List[object]
foreach ($window in $windows) {
    $action = 'none'
    $ok = $null
    if (($Mode -eq 'MinimizeHelpers' -or $Mode -eq 'Cleanup') -and $window.obstructing_helper) {
        $action = 'minimize_helper'
        if (-not $DryRun) {
            $ok = [MoSimWindowOps]::ShowWindowAsync([IntPtr]$window.hwnd, [MoSimWindowOps]::SW_MINIMIZE)
        }
    } elseif (($Mode -eq 'CloseSafeErrors' -or $Mode -eq 'Cleanup') -and $window.safe_error_window) {
        $action = 'close_safe_error'
        if (-not $DryRun) {
            $ok = [MoSimWindowOps]::PostMessage([IntPtr]$window.hwnd, [MoSimWindowOps]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero)
        }
    }

    if ($action -ne 'none') {
        $actions.Add([pscustomobject]@{
            hwnd = $window.hwnd
            pid = $window.pid
            process = $window.process
            title = $window.title
            action = $action
            dry_run = [bool]$DryRun
            api_return = $ok
            main_mworks_not_targeted = -not $window.main_window
        }) | Out-Null
    }
}

Start-Sleep -Milliseconds 500

$result = [pscustomobject]@{
    schema_version = 'mosim.mworks_window_management.v1'
    created_at = (Get-Date -Format o)
    mode = $Mode
    dry_run = [bool]$DryRun
    window_count = $windows.Count
    action_count = $actions.Count
    actions = $actions
    windows = $windows
    policy = @{
        never_close_main_mworks_sysplorer = $true
        login_license_authorization_windows_are_not_closed = $true
        helper_windows_are_minimized_only = $true
        safe_error_windows_require_explicit_error_report_or_memory_warning_title = $true
    }
}

$json = $result | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText(
    (Resolve-Path -LiteralPath (Split-Path -Parent $OutJson)).Path + [System.IO.Path]::DirectorySeparatorChar + (Split-Path -Leaf $OutJson),
    $json,
    (New-Object System.Text.UTF8Encoding($false))
)
Write-Output $json
