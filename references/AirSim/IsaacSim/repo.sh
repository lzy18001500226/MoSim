#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Check EULA acceptance first
SCRIPT_DIR="$( cd "$(dirname "$0")" ; pwd -P )"
echo "Script dir: ${SCRIPT_DIR}"
"${SCRIPT_DIR}/tools/eula_check.sh"
EULA_STATUS=$?

if [ $EULA_STATUS -ne 0 ]; then
    echo "Error: NVIDIA Software License Agreement and Product-Specific Terms for NVIDIA Omniverse must be accepted to proceed."
    exit 1
fi

set -e

# Set OMNI_REPO_ROOT early so `repo` bootstrapping can target the repository
# root when writing out Python dependencies.
export OMNI_REPO_ROOT="$( cd "$(dirname "$0")" ; pwd -P )"

# By default custom caching is disabled in repo_man. But if a repo-cache.json
# caching configuration file is generated via the `repo cache` command, it's
# presence will trigger the configuration of custom caching.
if [[ -f "${OMNI_REPO_ROOT}/repo-cache.json" ]]; then
    PM_PACKAGES_ROOT=$(grep '"PM_PACKAGES_ROOT"' "${OMNI_REPO_ROOT}/repo-cache.json" | sed 's/.*"PM_PACKAGES_ROOT": "\(.*\)".*/\1/')

    # PM_PACKAGES_ROOT is present in the config file. We set this early
    # so Packman will reference our cached package repository.
    if [[ -n "${PM_PACKAGES_ROOT}" ]]; then
        # Use eval to resolve ~ and perform parameter expansion
        RESOLVED_PACKAGES_ROOT=$(eval echo "$PM_PACKAGES_ROOT")

        if [[ "${RESOLVED_PACKAGES_ROOT}" != /* ]]; then
            # PM_PACKAGES_ROOT is not an abs path, assumption is then
            # that it is a relative path to the repository root.
            PM_PACKAGES_ROOT="${OMNI_REPO_ROOT}/${RESOLVED_PACKAGES_ROOT}"
        else
            PM_PACKAGES_ROOT=${RESOLVED_PACKAGES_ROOT}
        fi
        export PM_PACKAGES_ROOT
    fi
fi

# Use "exec" to ensure that environment variables don't accidentally affect other processes.
exec "${OMNI_REPO_ROOT}/tools/packman/python.sh" "${OMNI_REPO_ROOT}/tools/repoman/repoman.py" "$@"
