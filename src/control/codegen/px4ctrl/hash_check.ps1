[CmdletBinding()]
param(
  [string]$ManifestPath = (Join-Path $PSScriptRoot 'codegen_manifest.json')
)

$ErrorActionPreference = 'Stop'

function Test-ManifestEntry {
  param(
    [Parameter(Mandatory = $true)]$Entry,
    [Parameter(Mandatory = $true)][string]$Section
  )

  $path = Join-Path $PSScriptRoot $Entry.path
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
    Write-Error "$Section missing: $($Entry.path)"
    return $false
  }

  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
  $expected = [string]$Entry.sha256
  if ($actual -ne $expected) {
    Write-Error "$Section hash mismatch: $($Entry.path) expected $expected actual $actual"
    return $false
  }

  Write-Host "OK $Section $($Entry.path)"
  return $true
}

$manifest = Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json
$ok = $true
$ok = (Test-ManifestEntry -Entry $manifest.modelica_source -Section 'modelica_source') -and $ok
foreach ($section in 'generated_files', 'delivery_files', 'binary_evidence') {
  foreach ($entry in @($manifest.$section)) {
    $ok = (Test-ManifestEntry -Entry $entry -Section $section) -and $ok
  }
}

if (-not $ok) {
  exit 1
}

Write-Host 'All manifest hashes match.'
