# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


import os

import carb
import omni.client
import omni.ext


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):
        """Initialize the extension.

        Args:
            ext_id: The extension ID.
        """
        self._auth_cb = None

        # Register authentication callback only if ETM_ACTIVE environment variable is set
        if os.getenv("ETM_ACTIVE"):
            self._auth_cb = omni.client.register_authentication_callback(self._authenticate)

    def _authenticate(self, prefix):
        """Authentication callback for Omniverse client.

        Args:
            prefix: URL prefix for authentication.

        Returns:
            tuple: (username, password) if credentials are available, None otherwise.
        """
        omniuser = os.getenv("ISAACSIM_OMNI_USER")
        omnipass = os.getenv("ISAACSIM_OMNI_PASS")

        if omniuser and omnipass:
            return (omniuser, omnipass)
        return None

    def on_shutdown(self):
        """Clean up resources when the extension is shut down."""
        self._auth_cb = None
