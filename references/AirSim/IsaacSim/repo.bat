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

:: Check EULA acceptance first
call "%~dp0tools\eula_check.bat"
if %errorlevel% neq 0 (
    echo Error: NVIDIA Software License Agreement and Product-Specific Terms for NVIDIA Omniverse must be accepted to proceed.
    exit /b 1
)

:: Set OMNI_REPO_ROOT early so `repo` bootstrapping can target the repository
:: root when writing out Python dependencies.
:: Use SETLOCAL and ENDLOCAL to constrain these variables to this batch file.
:: Use ENABLEDELAYEDEXPANSION to evaluate the value of PM_PACKAGES_ROOT
:: at execution time.
SETLOCAL ENABLEDELAYEDEXPANSION
set OMNI_REPO_ROOT="%~dp0"

:: Set Packman cache directory early if repo-cache.json is configured
:: so that the Packman Python version is not fetched from the web.
IF NOT EXIST "%~dp0repo-cache.json" goto :RepoCacheEnd

:: Read PM_PACKAGES_ROOT from repo-cache.json and make sure it is an absolute path (assume relative to the script directory).
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "$PM_PACKAGES_ROOT = (Get-Content '%~dp0repo-cache.json' | ConvertFrom-Json).PM_PACKAGES_ROOT; if ([System.IO.Path]::IsPathRooted($PM_PACKAGES_ROOT)) { Write-Output ('absolute;' + $PM_PACKAGES_ROOT) } else { Write-Output ('relative;' + $PM_PACKAGES_ROOT) }"`) do (
    for /f "tokens=1,2 delims=;" %%A in ("%%i") do (
        if /i "%%A" == "relative" (
            set PM_PACKAGES_ROOT=%~dp0%%B
        ) else (
            set PM_PACKAGES_ROOT=%%B
        )
    )
)

:RepoCacheEnd

call "%~dp0tools\packman\python.bat" "%~dp0tools\repoman\repoman.py" %*
if %errorlevel% neq 0 ( goto Error )

:Success
ENDLOCAL
exit /b 0

:Error
ENDLOCAL
exit /b %errorlevel%
