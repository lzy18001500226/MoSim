@echo off
setlocal

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "UE_EDITOR=D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
set "UPROJECT=%PROJECT_ROOT%\UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject"
set "FRAME_SEGMENTS_CSV=%PROJECT_ROOT%\Results\unreal_scene_mapping\factory_l2_gazebo_to_ue_frame_overlay_current\factory_l2_gazebo_structure_frame_segments.csv"
set "FRAME_MARKERS_CSV=%PROJECT_ROOT%\Results\unreal_scene_mapping\factory_l2_gazebo_to_ue_frame_overlay_current\factory_l2_gazebo_structure_frame_markers.csv"

if not exist "%UE_EDITOR%" (
  echo UnrealEditor.exe not found: "%UE_EDITOR%"
  exit /b 2
)

if not exist "%UPROJECT%" (
  echo Unreal project not found: "%UPROJECT%"
  exit /b 2
)

if not exist "%FRAME_SEGMENTS_CSV%" (
  echo Factory frame segments CSV not found: "%FRAME_SEGMENTS_CSV%"
  exit /b 2
)

if not exist "%FRAME_MARKERS_CSV%" (
  echo Factory frame markers CSV not found: "%FRAME_MARKERS_CSV%"
  exit /b 2
)

start "" "%UE_EDITOR%" "%UPROJECT%" -game -windowed -ResX=1280 -ResY=720 -NoSplash /Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode -MoSimSimulationReview -MoSimDayReview -MoSimReviewSunIntensity=6.0 -MoSimReviewSkyLightIntensity=2.0 -MoSimReviewExposureBias=0.0 -MoSimFactoryCalibrationFrame -MoSimFactoryCalibrationCsv="%FRAME_SEGMENTS_CSV%" -MoSimFactoryCalibrationMarkerCsv="%FRAME_MARKERS_CSV%" -MoSimFactoryCalibrationLineThickness=8.0 -MoSimFactoryCalibrationLifetime=1.0 -MoSimNoPlayback -MoSimNoReviewCollision -MoSimReviewCameraX=-7000 -MoSimReviewCameraY=-21000 -MoSimReviewCameraZ=9000 -MoSimReviewCameraPitch=-28 -MoSimReviewCameraYaw=50 -MoSimReviewMoveSpeed=1800
exit /b 0
