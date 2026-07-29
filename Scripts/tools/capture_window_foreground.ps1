param(
    [string]$TitleRegex = 'Gazebo|Ignition',
    [string]$ProcessRegex = '.*',
    [string]$OutDir = 'Results/window_foreground_capture/manual',
    [switch]$Maximize,
    [switch]$MinimizeAfter,
    [int]$ActivateWaitMs = 700,
    [int]$CaptureSettleMs = 500
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -eq 'Core') {
    $windowsRoot = $env:SystemRoot
    if (-not $windowsRoot) {
        $windowsRoot = 'C:\Windows'
    }
    $legacyPowerShell = Join-Path $windowsRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    if (-not (Test-Path -LiteralPath $legacyPowerShell)) {
        throw 'Native window capture requires Windows PowerShell when System.Drawing.Common cannot compile the capture helper.'
    }

    $forwarded = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath)
    foreach ($entry in $PSBoundParameters.GetEnumerator()) {
        if ($entry.Value -is [System.Management.Automation.SwitchParameter]) {
            if ($entry.Value.IsPresent) {
                $forwarded += "-$($entry.Key)"
            }
        } else {
            $forwarded += "-$($entry.Key)"
            $forwarded += [string]$entry.Value
        }
    }
    & $legacyPowerShell @forwarded
    exit $LASTEXITCODE
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;
using System.Text;

public static class ForegroundWindowCapture {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
  [DllImport("kernel32.dll")] public static extern void Sleep(uint dwMilliseconds);

  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

  static readonly IntPtr DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = new IntPtr(-4);
  static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
  static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);
  const uint SWP_NOSIZE = 0x0001;
  const uint SWP_NOMOVE = 0x0002;
  const int SW_SHOWMAXIMIZED = 3;
  const int SW_MINIMIZE = 6;
  const int SW_RESTORE = 9;

  public static string EnableDpiAwareness() {
    try {
      if (SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)) return "per_monitor_v2";
    } catch {}
    try {
      if (SetProcessDPIAware()) return "system_dpi_aware";
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

  public static string Capture(IntPtr hwnd, string path, bool maximize, bool minimizeAfter, int activateWaitMs, int captureSettleMs) {
    bool wasMinimized = IsIconic(hwnd);
    bool wasMaximized = IsZoomed(hwnd);
    if (maximize) {
      ShowWindowAsync(hwnd, SW_SHOWMAXIMIZED);
    } else {
      ShowWindowAsync(hwnd, SW_RESTORE);
    }
    Sleep((uint)Math.Max(0, activateWaitMs));
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    bool foregroundOk = SetForegroundWindow(hwnd);
    Sleep((uint)Math.Max(0, captureSettleMs));

    RECT rect;
    if (!GetWindowRect(hwnd, out rect)) return "GetWindowRect failed";
    int width = Math.Max(1, rect.Right - rect.Left);
    int height = Math.Max(1, rect.Bottom - rect.Top);

    using (Bitmap bitmap = new Bitmap(width, height, PixelFormat.Format32bppArgb)) {
      using (Graphics graphics = Graphics.FromImage(bitmap)) {
        graphics.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(width, height));
      }
      bitmap.Save(path, ImageFormat.Png);
    }

    if (minimizeAfter || wasMinimized) {
      ShowWindowAsync(hwnd, SW_MINIMIZE);
    } else if (maximize && !wasMaximized) {
      ShowWindowAsync(hwnd, SW_RESTORE);
    }

    return String.Format(
      "foreground_ok={0}; was_minimized={1}; was_maximized={2}; maximize_requested={3}; minimize_after_requested={4}; rect={5},{6},{7},{8}; size={9}x{10}; visible={11}; title={12}; path={13}",
      foregroundOk, wasMinimized, wasMaximized, maximize, minimizeAfter, rect.Left, rect.Top, rect.Right, rect.Bottom, width, height, IsWindowVisible(hwnd), Title(hwnd), path
    );
  }
}
"@

Add-Type -TypeDefinition $code -ReferencedAssemblies @('System.Drawing')
$dpiAwareness = [ForegroundWindowCapture]::EnableDpiAwareness()
$resolvedOut = (Resolve-Path $OutDir).Path
$windowMatches = New-Object System.Collections.Generic.List[object]

$callback = [ForegroundWindowCapture+EnumWindowsProc]{
    param([IntPtr]$hWnd, [IntPtr]$lParam)
    $title = [ForegroundWindowCapture]::Title($hWnd)
    $windowPid = [ForegroundWindowCapture]::ProcessId($hWnd)
    $processName = ''
    try {
        $processName = (Get-Process -Id $windowPid -ErrorAction Stop).ProcessName
    } catch {}
    if (($title -match $TitleRegex) -and ($processName -match $ProcessRegex)) {
        $windowMatches.Add([PSCustomObject]@{
            pid = [int64]$windowPid
            process = $processName
            title = $title
            class_name = [ForegroundWindowCapture]::ClassName($hWnd)
            handle = $hWnd.ToInt64()
            handle_hex = ('0x{0:X}' -f $hWnd.ToInt64())
            visible = [ForegroundWindowCapture]::IsWindowVisible($hWnd)
            minimized = [ForegroundWindowCapture]::IsIconic($hWnd)
        }) | Out-Null
    }
    return $true
}
[void][ForegroundWindowCapture]::EnumWindows($callback, [IntPtr]::Zero)

$rows = @(
    $windowMatches |
        Sort-Object pid, handle |
        ForEach-Object {
        $safeTitle = $_.title -replace '[\\/:*?"<>|\[\]]', '_'
        $leaf = "$($_.pid)_$($_.handle_hex)_$safeTitle.png"
        $path = Join-Path $resolvedOut $leaf
        $capture = [ForegroundWindowCapture]::Capture(
            [IntPtr]$_.handle,
            $path,
            [bool]$Maximize,
            [bool]$MinimizeAfter,
            $ActivateWaitMs,
            $CaptureSettleMs
        )
        $captureWidth = $null
        $captureHeight = $null
        if ($capture -match 'size=(\d+)x(\d+)') {
            $captureWidth = [int]$Matches[1]
            $captureHeight = [int]$Matches[2]
        }
        [PSCustomObject]@{
            pid = $_.pid
            process = $_.process
            title = $_.title
            class_name = $_.class_name
            handle = $_.handle
            handle_hex = $_.handle_hex
            visible = $_.visible
            minimized = $_.minimized
            capture_width = $captureWidth
            capture_height = $captureHeight
            capture_reliability = 'foreground_copyfromscreen_window_rect'
            known_boundary = 'Requires bringing the target window to the foreground; use this for OpenGL/Gazebo review when PrintWindow background capture cannot capture the 3D viewport.'
            capture = $capture
            output_png = if (Test-Path $path) { $path } else { $null }
        }
        }
)

$manifestPath = Join-Path $resolvedOut 'capture_manifest.json'
$rows | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $manifestPath
[PSCustomObject]@{
    schema = 'mosim.window_foreground_capture.v1'
    status = if ($rows.Count -gt 0) { 'captured' } else { 'no_matching_windows' }
    title_regex = $TitleRegex
    process_regex = $ProcessRegex
    out_dir = $resolvedOut
    dpi_awareness = $dpiAwareness
    count = $rows.Count
    manifest = $manifestPath
    rows = $rows
} | ConvertTo-Json -Depth 7
