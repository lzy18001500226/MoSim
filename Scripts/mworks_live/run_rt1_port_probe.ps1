param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [int]$SampleCount = 24,
    [int]$SampleIntervalMs = 500
)

$ErrorActionPreference = "SilentlyContinue"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$samplesPath = Join-Path $OutputDir "endpoint_samples.jsonl"
Remove-Item -LiteralPath $samplesPath -Force -ErrorAction SilentlyContinue
$preflight = Join-Path $PSScriptRoot "preflight_connection.py"
$preflightAttempts = 0
$rt1Accepted = $false

Start-Sleep -Seconds 1
foreach ($sample in 1..$SampleCount) {
    $endpointLines = @(netstat -ano -p udp | Select-String ':49020')
    $solvers = @(Get-Process MWSolver)
    [pscustomobject]@{
        sample = $sample
        timestamp = Get-Date -Format o
        endpoint_count = $endpointLines.Count
        endpoint = @($endpointLines | ForEach-Object { $_.Line.Trim() })
        mwsolver = @($solvers | Select-Object Id, StartTime, CPU, PriorityClass)
    } | ConvertTo-Json -Depth 5 -Compress |
        Add-Content -LiteralPath $samplesPath -Encoding utf8

    if ($endpointLines.Count -gt 0 -and -not $rt1Accepted -and $preflightAttempts -lt 5) {
        $preflightAttempts += 1
        $preflightOutput = Join-Path $OutputDir ("connection_preflight_attempt{0}.json" -f $preflightAttempts)
        & python $preflight `
            --host 127.0.0.1 `
            --port 49020 `
            --ros-master-uri http://127.0.0.1:11311 `
            --rate-hz 200 `
            --timeout-s 0.35 `
            --sample-count 5 `
            --output $preflightOutput
        $LASTEXITCODE | Set-Content -LiteralPath (
            Join-Path $OutputDir ("preflight_attempt{0}_exit.txt" -f $preflightAttempts))
        $result = Get-Content -LiteralPath $preflightOutput -Raw | ConvertFrom-Json
        $rt1Accepted = [bool]$result.rt1.reachable
    }
    Start-Sleep -Milliseconds $SampleIntervalMs
}

[pscustomobject]@{
    endpoint_observed = [bool](Select-String -LiteralPath $samplesPath -Pattern '"endpoint_count":(?!0)' -Quiet)
    preflight_attempts = $preflightAttempts
    rt1_bidirectional_ready = $rt1Accepted
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDir "probe_summary.json") -Encoding utf8
