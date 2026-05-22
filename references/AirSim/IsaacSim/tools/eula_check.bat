:: SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
:: SPDX-License-Identifier: Apache-2.0
::
:: Licensed under the Apache License, Version 2.0 (the "License");
:: you may not use this file except in compliance with the License.
:: You may obtain a copy of the License at
::
:: http://www.apache.org/licenses/LICENSE-2.0
::
:: Unless required by applicable law or agreed to in writing, software
:: distributed under the License is distributed on an "AS IS" BASIS,
:: WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
:: See the License for the specific language governing permissions and
:: limitations under the License.

@echo off
setlocal EnableDelayedExpansion

REM Get repository root (parent directory of script directory)
set REPO_ROOT=%~dp0..

REM Check if EULA has already been accepted in either current directory or repository root
if exist ".eula_accepted" (
    exit /b 0
) else if exist "%REPO_ROOT%\.eula_accepted" (
    exit /b 0
)

echo === END USER LICENSE AGREEMENT ===
echo Building or using the software requires additional components licenced under other terms. These additional components include dependencies such as the Omniverse Kit SDK, as well as 3D models and textures.
echo.
echo License terms for these additional NVIDIA owned and licensed components can be found here:
echo.
echo https://www.nvidia.com/en-us/agreements/enterprise-software/isaac-sim-additional-software-and-materials-license/
echo.
echo ================================
echo.
set /p response="Do you accept the governing terms? (yes/No): "

REM Check response
if /i "!response!"=="YES" goto :accept
if /i "!response!"=="Y" goto :accept
goto :reject

:accept
type nul > "%REPO_ROOT%\.eula_accepted"
exit /b 0
:reject
exit /b 1
