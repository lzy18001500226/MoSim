param(
    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [ValidateSet("Normal", "AboveNormal", "High")]
    [string]$PriorityClass = "Normal",

    [ValidateRange(1, 30)]
    [int]$WaitSeconds = 10
)

$ErrorActionPreference = "Stop"
$deadline = [DateTime]::UtcNow.AddSeconds($WaitSeconds)
$solver = $null
do {
    $solver = Get-Process -Name MWSolver -ErrorAction SilentlyContinue |
        Sort-Object StartTime -Descending |
        Select-Object -First 1
    if ($null -eq $solver) {
        Start-Sleep -Milliseconds 250
    }
} while ($null -eq $solver -and [DateTime]::UtcNow -lt $deadline)

if ($null -eq $solver) {
    throw "No active MWSolver process was found for MWORKS Live run $RunId"
}

$previousPriority = [string]$solver.PriorityClass
$solver.PriorityClass = $PriorityClass
$solver.Refresh()
$evidence = [ordered]@{
    schema = "mosim.mworks_live.mwsolver_priority.v1"
    run_id = $RunId
    process_id = $solver.Id
    process_start_time = $solver.StartTime.ToUniversalTime().ToString("o")
    previous_priority = $previousPriority
    requested_priority = $PriorityClass
    effective_priority = [string]$solver.PriorityClass
    accepted = ([string]$solver.PriorityClass -eq $PriorityClass)
    updated_at = [DateTime]::UtcNow.ToString("o")
}

$parent = Split-Path -Parent $OutputPath
if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
}
$json = $evidence | ConvertTo-Json -Depth 4
$json | Set-Content -LiteralPath $OutputPath -Encoding utf8
$json
if (-not $evidence.accepted) {
    exit 4
}
