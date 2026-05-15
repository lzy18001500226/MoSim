param(
    [Parameter(Mandatory = $true)]
    [string]$ModelicaPath,

    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolved = Resolve-Path -LiteralPath $ModelicaPath
$text = Get-Content -Raw -LiteralPath $resolved

# Remove common comment forms before counting. This is intentionally simple:
# it is a preflight guard for generated model files, not a full Modelica parser.
$withoutBlockComments = [regex]::Replace($text, "(?s)/\*.*?\*/", "")
$withoutComments = [regex]::Replace($withoutBlockComments, "(?m)//.*$", "")

$connectMatches = [regex]::Matches(
    $withoutComments,
    "(?is)\bconnect\s*\((?<pair>.*?)\)\s*(?<annotation>annotation\s*\(\s*Line\s*\(\s*points\s*=.*?)?;"
)

$connections = @()
$missingLine = @()
$zeroLengthLine = @()

foreach ($match in $connectMatches) {
    $pair = (($match.Groups["pair"].Value -replace "\s+", " ").Trim())
    $hasLine = $match.Groups["annotation"].Success
    $lineText = $match.Groups["annotation"].Value

    $isZeroLength = $false
    if ($hasLine -and ($lineText -match "points\s*=\s*\{\{\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)\s*\}\s*,\s*\{\s*\1\s*,\s*\2\s*\}\s*\}")) {
        $isZeroLength = $true
        $zeroLengthLine += $pair
    }

    if (-not $hasLine) {
        $missingLine += $pair
    }

    $connections += [PSCustomObject]@{
        pair = $pair
        has_line_points_annotation = $hasLine
        zero_length_line = $isZeroLength
    }
}

$result = [PSCustomObject]@{
    modelica_path = [string]$resolved
    connect_count = $connections.Count
    line_points_annotation_count = @($connections | Where-Object { $_.has_line_points_annotation }).Count
    missing_line_annotation_count = $missingLine.Count
    zero_length_line_count = $zeroLengthLine.Count
    passed = ($missingLine.Count -eq 0 -and $zeroLengthLine.Count -eq 0)
    missing_line_connections = $missingLine
    zero_length_line_connections = $zeroLengthLine
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
