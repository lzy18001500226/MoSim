param(
    [string]$TitleRegex = 'Sysplorer|MWORKS|Quadrotor|AWFF',
    [double]$XRatio = -1,
    [double]$YRatio = -1,
    [int]$ClientX = -1,
    [int]$ClientY = -1,
    [string]$OutDir = 'Results/mworks_background_operation/manual',
    [switch]$RestoreMinimized,
    [switch]$KeepRestored,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$resolvedOut = (Resolve-Path $OutDir).Path
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$evidencePath = Join-Path $resolvedOut "background_click_$stamp.json"

$code = @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public static class BackgroundWindowClick {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

  public static IntPtr MakeLParam(int x, int y) {
    return new IntPtr(((y & 0xFFFF) << 16) | (x & 0xFFFF));
  }
}
"@

Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue

function Get-WindowInfo {
    param([IntPtr]$Handle)

    $title = New-Object System.Text.StringBuilder 512
    [void][BackgroundWindowClick]::GetWindowText($Handle, $title, $title.Capacity)
    $class = New-Object System.Text.StringBuilder 256
    [void][BackgroundWindowClick]::GetClassName($Handle, $class, $class.Capacity)
    [uint32]$windowPid = 0
    [void][BackgroundWindowClick]::GetWindowThreadProcessId($Handle, [ref]$windowPid)

    [PSCustomObject]@{
        hwnd = ('0x{0:X}' -f $Handle.ToInt64())
        pid = [int64]$windowPid
        title = $title.ToString()
        class = $class.ToString()
        visible = [BackgroundWindowClick]::IsWindowVisible($Handle)
        minimized = [BackgroundWindowClick]::IsIconic($Handle)
    }
}

$windowMatches = New-Object System.Collections.Generic.List[object]
$callback = [BackgroundWindowClick+EnumWindowsProc]{
    param([IntPtr]$hWnd, [IntPtr]$lParam)
    $info = Get-WindowInfo -Handle $hWnd
    if ($info.title -match $TitleRegex) {
        $windowMatches.Add($info) | Out-Null
    }
    return $true
}

[void][BackgroundWindowClick]::EnumWindows($callback, [IntPtr]::Zero)
$target = $windowMatches | Where-Object { $_.visible } | Sort-Object minimized, title | Select-Object -First 1

if (-not $target) {
    [PSCustomObject]@{
        timestamp = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK')
        status = 'blocked_no_matching_visible_window'
        title_regex = $TitleRegex
        matches = $windowMatches
    } | ConvertTo-Json -Depth 6 | Set-Content -Path $evidencePath -Encoding UTF8
    Get-Content -Path $evidencePath -Raw
    exit 2
}

$targetHwnd = [IntPtr]([Convert]::ToInt64(($target.hwnd -replace '^0x', ''), 16))
$before = Get-WindowInfo -Handle $targetHwnd
$foregroundBefore = [BackgroundWindowClick]::GetForegroundWindow()
$wasMinimized = [BackgroundWindowClick]::IsIconic($targetHwnd)

if ($wasMinimized -and $RestoreMinimized) {
    # SW_SHOWNOACTIVATE. Restores the target window without intending to steal focus.
    [void][BackgroundWindowClick]::ShowWindow($targetHwnd, 4)
    Start-Sleep -Milliseconds 900
}

$rect = New-Object BackgroundWindowClick+RECT
[void][BackgroundWindowClick]::GetWindowRect($targetHwnd, [ref]$rect)
$width = [Math]::Max(1, $rect.Right - $rect.Left)
$height = [Math]::Max(1, $rect.Bottom - $rect.Top)

if ($ClientX -ge 0 -and $ClientY -ge 0) {
    $clickX = $ClientX
    $clickY = $ClientY
} elseif ($XRatio -ge 0 -and $YRatio -ge 0) {
    $clickX = [int][Math]::Round($width * $XRatio)
    $clickY = [int][Math]::Round($height * $YRatio)
} else {
    throw 'Provide either -ClientX/-ClientY or -XRatio/-YRatio.'
}

$lParam = [BackgroundWindowClick]::MakeLParam($clickX, $clickY)
$posted = $false
if (-not $DryRun) {
    $WM_MOUSEMOVE = 0x0200
    $WM_LBUTTONDOWN = 0x0201
    $WM_LBUTTONUP = 0x0202
    $MK_LBUTTON = [IntPtr]1

    [void][BackgroundWindowClick]::PostMessage($targetHwnd, $WM_MOUSEMOVE, [IntPtr]::Zero, $lParam)
    Start-Sleep -Milliseconds 100
    [void][BackgroundWindowClick]::PostMessage($targetHwnd, $WM_LBUTTONDOWN, $MK_LBUTTON, $lParam)
    Start-Sleep -Milliseconds 120
    [void][BackgroundWindowClick]::PostMessage($targetHwnd, $WM_LBUTTONUP, [IntPtr]::Zero, $lParam)
    $posted = $true
    Start-Sleep -Milliseconds 800
}

if ($wasMinimized -and $RestoreMinimized -and -not $KeepRestored) {
    # SW_SHOWMINNOACTIVE. Re-minimizes without intending to steal focus.
    [void][BackgroundWindowClick]::ShowWindow($targetHwnd, 7)
    Start-Sleep -Milliseconds 400
}

$after = Get-WindowInfo -Handle $targetHwnd
$foregroundAfter = [BackgroundWindowClick]::GetForegroundWindow()

[PSCustomObject]@{
    timestamp = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK')
    status = if ($DryRun) { 'dry_run_no_click_posted' } else { 'posted_background_click' }
    method = 'Win32 ShowWindow optional SW_SHOWNOACTIVATE + PostMessage WM_MOUSEMOVE/WM_LBUTTONDOWN/WM_LBUTTONUP + optional SW_SHOWMINNOACTIVE'
    title_regex = $TitleRegex
    target_before = $before
    target_after = $after
    restore_minimized = [bool]$RestoreMinimized
    keep_restored = [bool]$KeepRestored
    was_minimized = $wasMinimized
    rect = @{
        left = $rect.Left
        top = $rect.Top
        right = $rect.Right
        bottom = $rect.Bottom
        width = $width
        height = $height
    }
    click_client = @{
        x = $clickX
        y = $clickY
    }
    click_ratio = @{
        x = if ($XRatio -ge 0) { $XRatio } else { $null }
        y = if ($YRatio -ge 0) { $YRatio } else { $null }
    }
    click_posted = $posted
    foreground_before = (Get-WindowInfo -Handle $foregroundBefore)
    foreground_after = (Get-WindowInfo -Handle $foregroundAfter)
    focus_stolen_by_target = ($foregroundAfter -eq $targetHwnd)
    claim_boundary = 'Background PostMessage works for some Qt/window controls but not all. Use only for approved low-risk UI actions; for license, login, crash, or error-report dialogs, capture evidence and return to PMO instead of clicking recovery buttons.'
} | ConvertTo-Json -Depth 8 | Set-Content -Path $evidencePath -Encoding UTF8

Get-Content -Path $evidencePath -Raw
