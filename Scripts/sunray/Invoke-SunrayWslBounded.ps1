function Invoke-SunrayWslBash {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Script,
        [ValidateRange(1, 120)]
        [int]$TimeoutS = 20,
        [switch]$AllowNonZero
    )

    $wslExe = Join-Path $env:SystemRoot "System32\wsl.exe"
    if (-not (Test-Path -LiteralPath $wslExe)) {
        throw "WSL executable is unavailable: $wslExe"
    }

    $process = $null
    try {
        $payload = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Script))
        $bashCommand = "printf '%s' '$payload' | base64 --decode | bash"
        $arguments = "-d Ubuntu-20.04 --exec bash -lc `"$bashCommand`""

        # Start-Process can leave ExitCode unset in Windows PowerShell 5.1.
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = $wslExe
        $startInfo.Arguments = $arguments
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $startInfo
        if (-not $process.Start()) {
            throw "Could not start the WSL process."
        }
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()

        if (-not $process.WaitForExit($TimeoutS * 1000)) {
            $process.Kill()
            $process.WaitForExit()
            throw "WSL command exceeded the ${TimeoutS}s host timeout. It was stopped without shutting down the WSL distribution."
        }

        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        $result = [pscustomobject]@{
            ExitCode = $process.ExitCode
            StdOut = $stdout
            StdErr = $stderr
        }
        if ($process.ExitCode -ne 0 -and -not $AllowNonZero) {
            $detail = if ([string]::IsNullOrWhiteSpace($stderr)) { $stdout } else { $stderr }
            throw "WSL command failed with exit code $($process.ExitCode): $detail"
        }
        return $result
    } finally {
        if ($null -ne $process) {
            $process.Dispose()
        }
    }
}
