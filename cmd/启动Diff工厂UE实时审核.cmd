@echo off
setlocal

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "FACTORY_WORLD_WSL=/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
set "FACTORY_MODEL_PATH_WSL=/mnt/c/Users/HP/Desktop/MoSim/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\Scripts\sunray\start_diff_interactive_review.ps1" -OpenUnrealLiveMirror -WorldFileWsl "%FACTORY_WORLD_WSL%" -GazeboModelPathPrefixWsl "%FACTORY_MODEL_PATH_WSL%" %*
exit /b %ERRORLEVEL%
