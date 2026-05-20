param(
    [string]$RflySimProject = "D:\PX4PSP\RflySim3D\RflySim3D",
    [string]$ScratchRoot = "D:\UE_MigrationScratch",
    [string]$ScratchProjectName = "QuadrotorRflySimSceneProbe"
)

$ErrorActionPreference = "Stop"

$sourceProject = Join-Path $RflySimProject "RflySim3D.uproject"
$scratchProject = Join-Path $ScratchRoot $ScratchProjectName
$scratchUproject = Join-Path $scratchProject "RflySim3D.uproject"

Write-Host "RflySim source project:"
Write-Host "  $sourceProject"
Write-Host "Scratch project path:"
Write-Host "  $scratchProject"
Write-Host ""

if (-not (Test-Path $sourceProject)) {
    throw "RflySim source .uproject not found: $sourceProject"
}

Write-Host "This helper is dry-run by default. It does not copy assets."
Write-Host "Diagnostic-only manual steps:"
Write-Host "  1. Create scratch folder outside the repository:"
Write-Host "     New-Item -ItemType Directory -Force `"$ScratchRoot`""
Write-Host "  2. Copy the RflySim UE project to scratch with robocopy:"
Write-Host "     robocopy `"$RflySimProject`" `"$scratchProject`" /MIR /XD Binaries DerivedDataCache Intermediate Saved .git /XF *.suo *.user"
Write-Host "  3. If diagnostics require an Unreal Editor open, use UE4.27 explicitly:"
Write-Host "     `"D:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor.exe`" `"$scratchUproject`""
Write-Host "  4. Do not expect this packaged/runtime RflySim tree to rebuild as an editable UE source project."
Write-Host "  5. Fill review checklist only if a map actually opens:"
Write-Host "     results/rflysim/rflysim_vision_ring_manual_review_checklist.md"
Write-Host "  6. If project-owned assets are recreated/exported into a local staging folder, validate it:"
Write-Host "     python scripts/check_unreal_migration_package.py --package-dir <project-local-staging-dir>"
Write-Host ""
Write-Host "Main route:"
Write-Host "  Use RflySim3D runtime for scene/protocol reference, then recreate approved assets in the project-owned UE5 renderer."
Write-Host ""
Write-Host "Stop if Unreal reports missing proprietary plugins, missing core geometry, missing source/binaries, or package assets that cannot be licensed."
