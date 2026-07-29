@echo off
setlocal

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "UE_EDITOR=D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
set "UPROJECT=%PROJECT_ROOT%\UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject"
set "CALIBRATION_CSV=%PROJECT_ROOT%\Results\unreal_scene_mapping\factory_l2_calibration_rig_review_20260702_192443\factory_l2_calibration_segments.csv"
set "CALIBRATION_MARKER_CSV=%PROJECT_ROOT%\Results\unreal_scene_mapping\factory_l2_calibration_rig_review_20260702_192443\factory_l2_calibration_markers.csv"

if not exist "%UE_EDITOR%" (
  echo UnrealEditor.exe not found: "%UE_EDITOR%"
  exit /b 2
)

if not exist "%UPROJECT%" (
  echo Unreal project not found: "%UPROJECT%"
  exit /b 2
)

if not exist "%CALIBRATION_CSV%" (
  echo Calibration CSV not found: "%CALIBRATION_CSV%"
  exit /b 2
)

if not exist "%CALIBRATION_MARKER_CSV%" (
  echo Calibration marker CSV not found: "%CALIBRATION_MARKER_CSV%"
  exit /b 2
)

start "" "%UE_EDITOR%" "%UPROJECT%" -game -windowed -ResX=1280 -ResY=720 -NoSplash /Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode -MoSimSimulationReview -MoSimDayReview -MoSimReviewSunIntensity=6.0 -MoSimReviewSkyLightIntensity=2.0 -MoSimReviewExposureBias=0.0 -MoSimFactoryCalibrationFrame -MoSimFactoryCalibrationCsv="%CALIBRATION_CSV%" -MoSimFactoryCalibrationMarkerCsv="%CALIBRATION_MARKER_CSV%" -MoSimNoPlayback -MoSimNoReviewCollision -MoSimReviewCameraX=-650 -MoSimReviewCameraY=-11350 -MoSimReviewCameraZ=320 -MoSimReviewCameraPitch=-18 -MoSimReviewCameraYaw=-45 -MoSimReviewMoveSpeed=800
exit /b 0
