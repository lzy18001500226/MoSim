param(
  [string]$SceneId = "factoryenvironmentcollect",
  [string]$ProjectRoot = "C:\Users\HP\Desktop\MoSim",
  [int]$MaxFrames = 8,
  [int]$MaxPointsPerFrame = 900,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Normalize-SceneId([string]$Id) {
  switch -Regex ($Id) {
    "^(factoryenvironmentcollect|FactoryEnvironmentCollect|factory)$" { return "factoryenvironmentcollect" }
    "^(derelictcorridormegascans|DerelictCorridorMegascans|derelict)$" { return "derelictcorridormegascans" }
    default { throw "Unsupported scene: $Id. Use factoryenvironmentcollect or derelictcorridormegascans." }
  }
}

function Read-JsonlFrames([string]$Path, [int]$Limit) {
  $frames = New-Object System.Collections.Generic.List[object]
  Get-Content -LiteralPath $Path -TotalCount $Limit | ForEach-Object {
    if ($_.Trim().Length -gt 0) {
      $frames.Add(($_ | ConvertFrom-Json))
    }
  }
  if ($frames.Count -eq 0) {
    throw "No frames loaded from $Path"
  }
  return $frames
}

$SceneId = Normalize-SceneId $SceneId
$SceneDir = Join-Path $ProjectRoot "Results\unreal_scene_mapping\$SceneId"
$LidarPath = Join-Path $SceneDir "lidar_point_frames.jsonl"
$MapPath = Join-Path $SceneDir "local_known_map_frames.jsonl"
$PlanPath = Join-Path $SceneDir "local_plan_frames.jsonl"

foreach ($required in @($LidarPath, $MapPath, $PlanPath)) {
  if (!(Test-Path -LiteralPath $required)) {
    throw "Missing preview artifact: $required"
  }
}

$lidarFrames = Read-JsonlFrames $LidarPath $MaxFrames
$mapFrames = Read-JsonlFrames $MapPath $MaxFrames
$planFrames = Read-JsonlFrames $PlanPath $MaxFrames
$frameCount = [Math]::Min($lidarFrames.Count, [Math]::Min($mapFrames.Count, $planFrames.Count))

if ($DryRun) {
  $pointCount = 0
  $cellCount = 0
  for ($i = 0; $i -lt $frameCount; $i++) {
    $pointCount += [Math]::Min($lidarFrames[$i].points_m.Count, $MaxPointsPerFrame)
    $cellCount += $mapFrames[$i].cells.Count
  }
  [pscustomobject]@{
    schema = "mosim.native_pointcloud_preview_dryrun.v1"
    scene_id = $SceneId
    frames = $frameCount
    displayed_lidar_points_upper_bound = $pointCount
    local_map_cells = $cellCount
    claim = "dry-run only; no native preview window was opened; this is not FAST-LIO/RViz runtime evidence"
  } | ConvertTo-Json -Depth 8
  exit 0
}

Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase

$window = New-Object System.Windows.Window
$window.Title = "MoSim native point-cloud preview - $SceneId"
$window.Width = 1100
$window.Height = 760
$window.Background = "White"

$grid = New-Object System.Windows.Controls.Grid
$grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition -Property @{ Height = "Auto" }))
$grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition -Property @{ Height = "*" }))

$label = New-Object System.Windows.Controls.TextBlock
$label.Margin = "10"
$label.FontSize = 14
$label.Text = "Native preview fallback: lidar/local map/path projection. Use RViz for official PointCloud2/FAST-LIO evidence."
[System.Windows.Controls.Grid]::SetRow($label, 0)
$grid.Children.Add($label) | Out-Null

$canvas = New-Object System.Windows.Controls.Canvas
$canvas.Background = "#111111"
[System.Windows.Controls.Grid]::SetRow($canvas, 1)
$grid.Children.Add($canvas) | Out-Null
$window.Content = $grid

function Add-Circle($Canvas, [double]$X, [double]$Y, [double]$Radius, [string]$Color, [double]$Opacity) {
  $ellipse = New-Object System.Windows.Shapes.Ellipse
  $ellipse.Width = $Radius * 2
  $ellipse.Height = $Radius * 2
  $ellipse.Fill = $Color
  $ellipse.Opacity = $Opacity
  [System.Windows.Controls.Canvas]::SetLeft($ellipse, $X - $Radius)
  [System.Windows.Controls.Canvas]::SetTop($ellipse, $Y - $Radius)
  $Canvas.Children.Add($ellipse) | Out-Null
}

function Add-Line($Canvas, [double]$X1, [double]$Y1, [double]$X2, [double]$Y2, [string]$Color, [double]$Thickness) {
  $line = New-Object System.Windows.Shapes.Line
  $line.X1 = $X1
  $line.Y1 = $Y1
  $line.X2 = $X2
  $line.Y2 = $Y2
  $line.Stroke = $Color
  $line.StrokeThickness = $Thickness
  $Canvas.Children.Add($line) | Out-Null
}

$frameIndex = 0
$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMilliseconds(250)
$timer.Add_Tick({
  $canvas.Children.Clear()
  $frame = $lidarFrames[$frameIndex]
  $map = $mapFrames[$frameIndex]
  $plan = $planFrames[$frameIndex]
  $origin = $map.origin_m
  $gridM = [double]$map.grid_m
  $width = [Math]::Max(1.0, $canvas.ActualWidth)
  $height = [Math]::Max(1.0, $canvas.ActualHeight)
  $scale = 25.0
  $cx = $width * 0.5
  $cy = $height * 0.5

  foreach ($cell in $map.cells) {
    $x = $cx + ([double]$cell.offset[0]) * $gridM * $scale
    $y = $cy - ([double]$cell.offset[1]) * $gridM * $scale
    if ($cell.state -eq "observed_occupied") {
      Add-Circle $canvas $x $y 3.0 "#ff5555" 0.85
    } else {
      Add-Circle $canvas $x $y 1.6 "#555555" 0.35
    }
  }

  $points = $frame.points_m
  $limit = [Math]::Min($points.Count, $MaxPointsPerFrame)
  for ($i = 0; $i -lt $limit; $i++) {
    $point = $points[$i]
    $dx = ([double]$point[0]) - ([double]$origin[0])
    $dy = ([double]$point[1]) - ([double]$origin[1])
    Add-Circle $canvas ($cx + $dx * $scale) ($cy - $dy * $scale) 1.8 "#66ccff" 0.70
  }

  $path = $plan.plan_points_m
  if ($path.Count -gt 1) {
    for ($i = 1; $i -lt $path.Count; $i++) {
      $a = $path[$i - 1]
      $b = $path[$i]
      $x1 = $cx + (([double]$a[0]) - ([double]$origin[0])) * $scale
      $y1 = $cy - (([double]$a[1]) - ([double]$origin[1])) * $scale
      $x2 = $cx + (([double]$b[0]) - ([double]$origin[0])) * $scale
      $y2 = $cy - (([double]$b[1]) - ([double]$origin[1])) * $scale
      Add-Line $canvas $x1 $y1 $x2 $y2 "#ffff66" 2.0
    }
  }

  $label.Text = "Scene=$SceneId frame=$frameIndex/$($frameCount - 1) lidar_points_displayed=$limit map_cells=$($map.cells.Count) | fallback preview only; RViz/FAST-LIO topics are official runtime evidence"
  $script:frameIndex = ($frameIndex + 1) % $frameCount
})

$window.Add_Loaded({ $timer.Start() })
$window.Add_Closed({ $timer.Stop() })
$window.ShowDialog() | Out-Null
