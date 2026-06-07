param(
    [string]$TitleRegex = 'Sysplorer|MWORKS|Quadrotor|AWFF',
    [string]$OutDir = 'Results/mworks_background_capture/manual',
    [switch]$RestoreMinimized,
    [switch]$KeepRestored
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
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
  [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

  [StructLayout(LayoutKind.Sequential)]
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

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
  const int SW_MINIMIZE = 6;

  public static string Capture(IntPtr hwnd, string path, bool restoreMinimized, bool keepRestored) {
    bool wasMinimized = IsIconic(hwnd);
    if (wasMinimized && restoreMinimized) {
      ShowWindowAsync(hwnd, SW_SHOWNOACTIVATE);
      Thread.Sleep(800);
      SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);
      Thread.Sleep(300);
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

    if (wasMinimized && restoreMinimized && !keepRestored) {
      ShowWindowAsync(hwnd, SW_MINIMIZE);
    }

    return String.Format(
      "ok={0}; was_minimized={1}; minimized_before_reminimize={2}; visible={3}; rect={4},{5},{6},{7}; size={8}x{9}; title={10}; path={11}",
      ok, wasMinimized, minimizedBeforeReMinimize, IsWindowVisible(hwnd),
      rect.Left, rect.Top, rect.Right, rect.Bottom, width, height, Title(hwnd), path
    );
  }
}
"@

Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing

$resolvedOut = (Resolve-Path $OutDir).Path
$windowMatches = New-Object System.Collections.Generic.List[object]
$callback = [BackgroundWindowCapture+EnumWindowsProc]{
    param([IntPtr]$hWnd, [IntPtr]$lParam)
    $title = [BackgroundWindowCapture]::Title($hWnd)
    if ($title -match $TitleRegex) {
        $windowPid = [BackgroundWindowCapture]::ProcessId($hWnd)
        $processName = $null
        try {
            $processName = (Get-Process -Id $windowPid -ErrorAction Stop).ProcessName
        } catch {
            $processName = ''
        }
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

$rows = $windowMatches |
    Sort-Object pid, handle |
    ForEach-Object {
        $safeTitle = $_.title -replace '[\\/:*?"<>|\[\]]', '_'
        $leaf = "$($_.pid)_$($_.handle_hex)_$safeTitle.png"
        $path = Join-Path $resolvedOut $leaf
        $capture = [BackgroundWindowCapture]::Capture(
            [IntPtr]$_.handle,
            $path,
            [bool]$RestoreMinimized,
            [bool]$KeepRestored
        )

        [PSCustomObject]@{
            id = $_.pid
            process = $_.process
            title = $_.title
            class_name = $_.class_name
            handle = $_.handle
            handle_hex = $_.handle_hex
            visible = $_.visible
            minimized = $_.minimized
            capture = $capture
            path = $path
        }
    }

$manifest = Join-Path $resolvedOut 'capture_manifest.json'
$manifestJson = $rows | ConvertTo-Json -Depth 4
[System.IO.File]::WriteAllText(
    $manifest,
    $manifestJson,
    [System.Text.UTF8Encoding]::new($false)
)
$rows
