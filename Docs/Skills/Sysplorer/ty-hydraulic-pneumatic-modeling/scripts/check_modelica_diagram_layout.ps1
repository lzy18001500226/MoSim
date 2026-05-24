param(
    [Parameter(Mandatory = $true)]
    [string]$ModelicaPath,

    [double]$MinCenterDistance = 24,

    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolved = Resolve-Path -LiteralPath $ModelicaPath
$text = Get-Content -Raw -LiteralPath $resolved

$withoutBlockComments = [regex]::Replace($text, "(?s)/\*.*?\*/", "")
$withoutComments = [regex]::Replace($withoutBlockComments, "(?m)//.*$", "")

$diagram = [regex]::Match(
    $withoutComments,
    "Diagram\s*\(\s*coordinateSystem\s*\(\s*extent\s*=\s*\{\{\s*(?<x1>[-+]?\d+(?:\.\d+)?)\s*,\s*(?<y1>[-+]?\d+(?:\.\d+)?)\s*\}\s*,\s*\{\s*(?<x2>[-+]?\d+(?:\.\d+)?)\s*,\s*(?<y2>[-+]?\d+(?:\.\d+)?)\s*\}\s*\}"
)

$hasDiagram = $diagram.Success
$diagramBounds = $null
if ($hasDiagram) {
    $diagramBounds = [PSCustomObject]@{
        x1 = [double]$diagram.Groups["x1"].Value
        y1 = [double]$diagram.Groups["y1"].Value
        x2 = [double]$diagram.Groups["x2"].Value
        y2 = [double]$diagram.Groups["y2"].Value
    }
}

$placementPattern = "(?is)(?<class>[A-Za-z_][\w.]*)(?:\s+)(?<name>[A-Za-z_]\w*)\s*(?:\([^;]*?\))?\s*annotation\s*\(\s*Placement\s*\(\s*transformation\s*\((?<body>.*?)\)\s*\)\s*\)\s*;"
$matches = [regex]::Matches($withoutComments, $placementPattern)

$components = @()
foreach ($match in $matches) {
    $name = $match.Groups["name"].Value
    $body = $match.Groups["body"].Value

    $originMatch = [regex]::Match($body, "origin\s*=\s*\{\s*(?<x>[-+]?\d+(?:\.\d+)?)\s*,\s*(?<y>[-+]?\d+(?:\.\d+)?)\s*\}")
    $extentMatch = [regex]::Match($body, "extent\s*=\s*\{\{\s*(?<x1>[-+]?\d+(?:\.\d+)?)\s*,\s*(?<y1>[-+]?\d+(?:\.\d+)?)\s*\}\s*,\s*\{\s*(?<x2>[-+]?\d+(?:\.\d+)?)\s*,\s*(?<y2>[-+]?\d+(?:\.\d+)?)\s*\}\s*\}")

    if (-not $extentMatch.Success) {
        continue
    }

    $ex1 = [double]$extentMatch.Groups["x1"].Value
    $ey1 = [double]$extentMatch.Groups["y1"].Value
    $ex2 = [double]$extentMatch.Groups["x2"].Value
    $ey2 = [double]$extentMatch.Groups["y2"].Value

    if ($originMatch.Success) {
        $cx = [double]$originMatch.Groups["x"].Value
        $cy = [double]$originMatch.Groups["y"].Value
        $minX = $cx + [Math]::Min($ex1, $ex2)
        $maxX = $cx + [Math]::Max($ex1, $ex2)
        $minY = $cy + [Math]::Min($ey1, $ey2)
        $maxY = $cy + [Math]::Max($ey1, $ey2)
    }
    else {
        $minX = [Math]::Min($ex1, $ex2)
        $maxX = [Math]::Max($ex1, $ex2)
        $minY = [Math]::Min($ey1, $ey2)
        $maxY = [Math]::Max($ey1, $ey2)
        $cx = ($minX + $maxX) / 2
        $cy = ($minY + $maxY) / 2
    }

    $components += [PSCustomObject]@{
        name = $name
        center_x = $cx
        center_y = $cy
        min_x = $minX
        max_x = $maxX
        min_y = $minY
        max_y = $maxY
    }
}

$outOfBounds = @()
if ($hasDiagram) {
    foreach ($c in $components) {
        if ($c.min_x -lt $diagramBounds.x1 -or $c.max_x -gt $diagramBounds.x2 -or $c.min_y -lt $diagramBounds.y1 -or $c.max_y -gt $diagramBounds.y2) {
            $outOfBounds += $c.name
        }
    }
}

$overlaps = @()
$tooClose = @()
for ($i = 0; $i -lt $components.Count; $i++) {
    for ($j = $i + 1; $j -lt $components.Count; $j++) {
        $a = $components[$i]
        $b = $components[$j]
        if ($a.min_x -lt $b.max_x -and $a.max_x -gt $b.min_x -and $a.min_y -lt $b.max_y -and $a.max_y -gt $b.min_y) {
            $overlaps += "$($a.name)<->$($b.name)"
        }

        $dx = $a.center_x - $b.center_x
        $dy = $a.center_y - $b.center_y
        $distance = [Math]::Sqrt(($dx * $dx) + ($dy * $dy))
        if ($distance -lt $MinCenterDistance) {
            $tooClose += "$($a.name)<->$($b.name)"
        }
    }
}

$uniqueCenters = @($components | ForEach-Object { "$([Math]::Round($_.center_x, 3)),$([Math]::Round($_.center_y, 3))" } | Select-Object -Unique).Count
$sameCenterCrowding = ($components.Count -gt 1 -and $uniqueCenters -lt $components.Count)

$result = [PSCustomObject]@{
    modelica_path = [string]$resolved
    has_diagram_coordinate_system = $hasDiagram
    placement_count = $components.Count
    unique_center_count = $uniqueCenters
    same_center_crowding = $sameCenterCrowding
    out_of_bounds_count = $outOfBounds.Count
    overlap_count = $overlaps.Count
    too_close_count = $tooClose.Count
    passed = ($hasDiagram -and $components.Count -gt 0 -and -not $sameCenterCrowding -and $outOfBounds.Count -eq 0 -and $overlaps.Count -eq 0 -and $tooClose.Count -eq 0)
    out_of_bounds_instances = $outOfBounds
    overlapping_pairs = $overlaps
    too_close_pairs = $tooClose
}

if ($Json) {
    $result | ConvertTo-Json -Depth 6
}
else {
    $result | Format-List
}

if (-not $result.passed) {
    exit 1
}
