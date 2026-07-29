param(
    [string]$TitleRegex = 'Sysplorer|MWORKS|Quadrotor|AWFF',
    [string]$ProcessRegex = '^(mworks|mw_browser_proxy|mw_crash_handler|syslab|sysplorer)',
    [string]$OutDir = 'Results/mworks_background_capture/manual',
    [switch]$IncludeHelperWindows,
    [switch]$MaximizeAllMatches,
    [switch]$RestoreMinimized,
    [switch]$Maximize,
    [switch]$KeepRestored,
    [switch]$MinimizeAfter,
    [int]$RestoreWaitMs = 800,
    [int]$RestoreSettleMs = 300,
    [int]$MaximizeWaitMs = 500
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;
using System.Text;
using System.Threading;

public static class BackgroundWindowCapture {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
  [DllImport("kernel32.dll")] public static extern void Sleep(uint dwMilliseconds);

  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

  static readonly IntPtr DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = new IntPtr(-4);

  public static string EnableDpiAwareness() {
    try {
      if (SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)) {
        return "per_monitor_v2";
      }
    } catch {}
    try {
      if (SetProcessDPIAware()) {
        return "system_dpi_aware";
      }
    } catch {}
    return "not_changed_or_already_set";
  }

  public static string Title(IntPtr hwnd) {
    StringBuilder title = new StringBuilder(512);
    GetWindowText(hwnd, title, title.Capacity);
    return title.ToString();
  }

  public static string ClassName(IntPtr hwnd) {
    StringBuilder className = new StringBuilder(256);
    GetClassName(hwnd, className, className.Capacity);
    return className.ToString();
  }

  public static uint ProcessId(IntPtr hwnd) {
    uint pid;
    GetWindowThreadProcessId(hwnd, out pid);
    return pid;
  }

  static readonly IntPtr HWND_BOTTOM = new IntPtr(1);
  const uint SWP_NOSIZE = 0x0001;
  const uint SWP_NOMOVE = 0x0002;
  const uint SWP_NOACTIVATE = 0x0010;
  const int SW_SHOWNOACTIVATE = 4;
  const int SW_SHOWMAXIMIZED = 3;
  const int SW_MINIMIZE = 6;
  const int SW_RESTORE = 9;

  public static string Capture(IntPtr hwnd, string path, bool restoreMinimized, bool maximize, bool keepRestored, bool minimizeAfter, int restoreWaitMs, int restoreSettleMs, int maximizeWaitMs) {
    bool wasMinimized = IsIconic(hwnd);
    bool wasMaximized = IsZoomed(hwnd);
    if (wasMinimized && restoreMinimized) {
      ShowWindowAsync(hwnd, SW_SHOWNOACTIVATE);
      Sleep((uint)Math.Max(0, restoreWaitMs));
      SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
      Sleep((uint)Math.Max(0, restoreSettleMs));
    }

    if (maximize) {
      ShowWindowAsync(hwnd, SW_SHOWMAXIMIZED);
      Sleep((uint)Math.Max(0, maximizeWaitMs));
    }

    RECT rect;
    if (!GetWindowRect(hwnd, out rect)) return "GetWindowRect failed";

    int width = Math.Max(1, rect.Right - rect.Left);
    int height = Math.Max(1, rect.Bottom - rect.Top);
    bool ok = false;

    using (Bitmap bitmap = new Bitmap(width, height, PixelFormat.Format32bppArgb)) {
      using (Graphics graphics = Graphics.FromImage(bitmap)) {
        IntPtr hdc = graphics.GetHdc();
        ok = PrintWindow(hwnd, hdc, 0x00000002);
        graphics.ReleaseHdc(hdc);
      }
      bitmap.Save(path, ImageFormat.Png);
    }

    bool minimizedBeforeReMinimize = IsIconic(hwnd);

    if (minimizeAfter && !keepRestored) {
      ShowWindowAsync(hwnd, SW_MINIMIZE);
    } else if (wasMinimized && restoreMinimized && !keepRestored) {
      ShowWindowAsync(hwnd, SW_MINIMIZE);
    } else if (maximize && !wasMaximized && !keepRestored) {
      ShowWindowAsync(hwnd, SW_RESTORE);
    }

    return String.Format(
      "ok={0}; was_minimized={1}; was_maximized={2}; maximize_requested={3}; minimize_after_requested={4}; restore_wait_ms={5}; restore_settle_ms={6}; maximize_wait_ms={7}; minimized_before_reminimize={8}; visible={9}; rect={10},{11},{12},{13}; size={14}x{15}; title={16}; path={17}",
      ok, wasMinimized, wasMaximized, maximize, minimizeAfter, restoreWaitMs, restoreSettleMs, maximizeWaitMs, minimizedBeforeReMinimize, IsWindowVisible(hwnd),
      rect.Left, rect.Top, rect.Right, rect.Bottom, width, height, Title(hwnd), path
    );
  }
}
"@

Add-Type -TypeDefinition $code -ReferencedAssemblies @('System.Drawing')
$dpiAwareness = [BackgroundWindowCapture]::EnableDpiAwareness()

$resolvedOut = (Resolve-Path $OutDir).Path
$windowMatches = New-Object System.Collections.Generic.List[object]
$callback = [BackgroundWindowCapture+EnumWindowsProc]{
    param([IntPtr]$hWnd, [IntPtr]$lParam)
    $title = [BackgroundWindowCapture]::Title($hWnd)
    $windowPid = [BackgroundWindowCapture]::ProcessId($hWnd)
    $processName = $null
    try {
        $processName = (Get-Process -Id $windowPid -ErrorAction Stop).ProcessName
    } catch {
        $processName = ''
    }
    if (($title -match $TitleRegex) -and ($processName -match $ProcessRegex)) {
        $windowMatches.Add([PSCustomObject]@{
            pid = [int64]$windowPid
            process = $processName
            title = $title
            class_name = [BackgroundWindowCapture]::ClassName($hWnd)
            handle = $hWnd.ToInt64()
            handle_hex = ('0x{0:X}' -f $hWnd.ToInt64())
            visible = [BackgroundWindowCapture]::IsWindowVisible($hWnd)
            minimized = [BackgroundWindowCapture]::IsIconic($hWnd)
        }) | Out-Null
    }
    return $true
}
[void][BackgroundWindowCapture]::EnumWindows($callback, [IntPtr]::Zero)

$rows = @(
    $windowMatches |
        Sort-Object pid, handle |
        ForEach-Object {
        $isHelperWindow =
            ($_.process -match '^(mw_browser_proxy|mw_crash_handler|mw_memory_monitor|sysplorer-acp-server|sysplorer_docsearch)$') -or
            ($_.class_name -match '^(IME|MSCTFIME UI|QtitanTitleBarGlowWindow|Chrome_SystemMessageWindow|Base_PowerMessageWindow|PyInstallerOnefileHiddenWindow)$') -or
            ($_.title -eq 'MWORKS.Sysplorer 2026a')
        $baseShouldCapture = (-not $isHelperWindow) -or [bool]$IncludeHelperWindows
        $shouldMaximize = [bool]$Maximize -and ((-not $isHelperWindow) -or [bool]$MaximizeAllMatches)
        $shouldRestoreMinimized = [bool]$RestoreMinimized -and $baseShouldCapture
        $minimizedRequiresRestore = $baseShouldCapture -and [bool]$_.minimized -and -not $shouldRestoreMinimized
        $shouldCapture = $baseShouldCapture -and -not $minimizedRequiresRestore
        $safeTitle = $_.title -replace '[\\/:*?"<>|\[\]]', '_'
        $leaf = "$($_.pid)_$($_.handle_hex)_$safeTitle.png"
        $path = Join-Path $resolvedOut $leaf
        $capture = "skipped_by_default_helper_window"
        $recommendedAction = ""
        if ($minimizedRequiresRestore) {
            $capture = "skipped_minimized_window_requires_restoreminimized"
            $recommendedAction = "rerun with -RestoreMinimized, and add -Maximize -MinimizeAfter when full-window evidence is required"
        }
        if ($shouldCapture) {
            $capture = [BackgroundWindowCapture]::Capture(
                [IntPtr]$_.handle,
                $path,
                $shouldRestoreMinimized,
                $shouldMaximize,
                [bool]$KeepRestored,
                [bool]$MinimizeAfter,
                $RestoreWaitMs,
                $RestoreSettleMs,
                $MaximizeWaitMs
            )
        }
        $captureWidth = $null
        $captureHeight = $null
        if ($capture -match 'size=(\d+)x(\d+)') {
            $captureWidth = [int]$Matches[1]
            $captureHeight = [int]$Matches[2]
        }
        $stillMinimizedAtCapture = $false
        if ($capture -match 'minimized_before_reminimize=True') {
            $stillMinimizedAtCapture = $true
        }
        $smallCapture = (($null -ne $captureWidth -and $captureWidth -lt 500) -or ($null -ne $captureHeight -and $captureHeight -lt 300))
        $captureReliability = 'window_level_capture'
        if ($minimizedRequiresRestore) {
            $captureReliability = 'not_captured_minimized_window_requires_restore'
        } elseif (-not $baseShouldCapture -and $isHelperWindow) {
            $captureReliability = 'not_captured_default_helper_window'
        } elseif ($_.minimized -and $shouldRestoreMinimized -and ($stillMinimizedAtCapture -or $smallCapture)) {
            $captureReliability = 'incomplete_restored_minimized_window'
            $recommendedAction = "rerun with -RestoreMinimized -Maximize -MinimizeAfter, or use foreground/window-specific evidence if full client-area capture is required"
        } elseif ($_.minimized -and $shouldRestoreMinimized) {
            $captureReliability = 'restored_minimized_window_capture'
        } elseif ($smallCapture) {
            $captureReliability = 'small_helper_or_incomplete_window'
        } elseif ($_.title -match 'Sysplorer.*教育版|Sysplorer.*演示版|QuadrotorModel') {
            $captureReliability = if ([bool]$Maximize) { 'maximized_main_qt_window_body_printwindow' } else { 'main_qt_window_body_printwindow' }
        }

        [PSCustomObject]@{
            id = $_.pid
            process = $_.process
            title = $_.title
            class_name = $_.class_name
            handle = $_.handle
            handle_hex = $_.handle_hex
            visible = $_.visible
            minimized = $_.minimized
            helper_window = $isHelperWindow
            helper_capture_included = [bool]$IncludeHelperWindows
            restore_minimized_requested = [bool]$RestoreMinimized
            restore_minimized_applied = $shouldRestoreMinimized
            skipped_minimized_requires_restore = $minimizedRequiresRestore
            maximize_applied = $shouldMaximize
            minimize_after_requested = [bool]$MinimizeAfter
            restore_wait_ms = $RestoreWaitMs
            restore_settle_ms = $RestoreSettleMs
            maximize_wait_ms = $MaximizeWaitMs
            capture_width = $captureWidth
            capture_height = $captureHeight
            still_minimized_at_capture = $stillMinimizedAtCapture
            capture_reliability = $captureReliability
            recommended_action = $recommendedAction
            known_blind_spot = 'PrintWindow cannot capture a full client area for minimized windows without restoring first, and may miss Qt/browser-proxy child surfaces such as the right MWORKS AI panel or separate login panes; use -RestoreMinimized and, when needed, -Maximize plus foreground/Windows MCP visible-desktop evidence for login/license and full GUI/layout acceptance.'
            capture = $capture
            dpi_awareness = $dpiAwareness
            path = if ($shouldCapture) { $path } else { $null }
        }
        }
)

$manifest = Join-Path $resolvedOut 'capture_manifest.json'
$rowArray = @($rows)
$manifestJson = ConvertTo-Json -InputObject $rowArray -Depth 4
[System.IO.File]::WriteAllText(
    $manifest,
    $manifestJson,
    [System.Text.UTF8Encoding]::new($false)
)
$rows
