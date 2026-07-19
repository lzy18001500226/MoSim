$ErrorActionPreference = "Stop"

$script:MoSimProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$script:MoSimClient = Join-Path $script:MoSimProjectRoot "Scripts/ui/orchestrator_client.py"
$script:MoSimService = Join-Path $script:MoSimProjectRoot "Scripts/ui/orchestrator_service.py"
$script:MoSimStartupLogDir = Join-Path $script:MoSimProjectRoot "Results/ui_platform/startup"
$script:MoSimActiveRunFile = Join-Path $script:MoSimProjectRoot "Results/ui_platform/model_studio_active_run.json"

function Start-MoSimOrchestratorService {
    New-Item -ItemType Directory -Force -Path $script:MoSimStartupLogDir | Out-Null
    $lockPath = Join-Path $script:MoSimProjectRoot "Results/ui_platform/orchestrator_service.lock"
    if (Test-Path -LiteralPath $lockPath) {
        try {
            $stream = [System.IO.File]::Open(
                $lockPath,
                [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::ReadWrite,
                [System.IO.FileShare]::None
            )
            $stream.Dispose()
        } catch [System.IO.IOException] {
            return
        }
    }

    $stdout = Join-Path $script:MoSimStartupLogDir "orchestrator.stdout.log"
    $stderr = Join-Path $script:MoSimStartupLogDir "orchestrator.stderr.log"
    Start-Process -FilePath "python.exe" -WorkingDirectory $script:MoSimProjectRoot `
        -ArgumentList @($script:MoSimService) -WindowStyle Hidden `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
    Start-Sleep -Milliseconds 750
}

function Invoke-MoSimOrchestratorClient {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [switch]$AllowRejected
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $raw = & python.exe $script:MoSimClient @Arguments --format json --timeout-s 5 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    try {
        $response = $raw | ConvertFrom-Json
    } catch {
        throw "orchestrator_response_invalid: $raw"
    }
    if (-not $AllowRejected -and ($exitCode -ne 0 -or -not $response.accepted)) {
        throw "orchestrator_request_failed: $($response.reason_code)"
    }
    return $response
}

function Get-MoSimActiveRun {
    if (-not (Test-Path -LiteralPath $script:MoSimActiveRunFile)) {
        return $null
    }
    try {
        return Get-Content -Raw -LiteralPath $script:MoSimActiveRunFile | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-MoSimRunDirectory {
    param([Parameter(Mandatory = $true)][string]$RunId)
    if ($RunId -notmatch '^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$') {
        throw "invalid_run_id: $RunId"
    }
    return Join-Path $script:MoSimProjectRoot "Results/ui_platform/orchestrator_runs/$RunId"
}
