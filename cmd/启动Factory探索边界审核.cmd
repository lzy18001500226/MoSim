@echo off
setlocal

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "UE_EDITOR=D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
set "UPROJECT=%PROJECT_ROOT%\UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject"
set "BOUNDARY_SEGMENTS_CSV=%PROJECT_ROOT%\Results\unreal_scene_mapping\factory_l2_exploration_boundary_review_current\factory_l2_exploration_boundary_segments.csv"
set "BOUNDARY_MARKERS_CSV=%PROJECT_ROOT%\Results\unreal_scene_mapping\factory_l2_exploration_boundary_review_current\factory_l2_exploration_boundary_markers.csv"

if not exist "%UE_EDITOR%" (
  echo UnrealEditor.exe not found: "%UE_EDITOR%"
  exit /b 2
)

if not exist "%UPROJECT%" (
  echo Unreal project not found: "%UPROJECT%"
  exit /b 2
)

if not exist "%BOUNDARY_SEGMENTS_CSV%" (
  echo Boundary segments CSV not found: "%BOUNDARY_SEGMENTS_CSV%"
  exit /b 2
)

if not exist "%BOUNDARY_MARKERS_CSV%" (
  echo Boundary markers CSV not found: "%BOUNDARY_MARKERS_CSV%"
  exit /b 2
)

start "" "%UE_EDITOR%" "%UPROJECT%" -game -windowed -ResX=1280 -ResY=720 -NoSplash /Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode -MoSimSimulationReview -MoSimDayReview -MoSimReviewSunIntensity=6.0 -MoSimReviewSkyLightIntensity=2.0 -MoSimReviewExposureBias=0.0 -MoSimFactoryCalibrationFrame -MoSimFactoryCalibrationCsv="%BOUNDARY_SEGMENTS_CSV%" -MoSimFactoryCalibrationMarkerCsv="%BOUNDARY_MARKERS_CSV%" -MoSimFactoryCalibrationLineThickness=16.0 -MoSimFactoryCalibrationLifetime=1.0 -MoSimNoPlayback -MoSimNoReviewCollision -MoSimReviewCameraX=-1000 -MoSimReviewCameraY=1900 -MoSimReviewCameraZ=100000 -MoSimReviewCameraPitch=-88 -MoSimReviewCameraYaw=0 -MoSimReviewMoveSpeed=12000
exit /b 0
