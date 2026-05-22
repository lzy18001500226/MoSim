# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import omni.ext
import omni.kit.window.property
from isaacsim.replicator.behavior.global_variables import EXPOSED_ATTR_NS

from .exposed_variables_widget import ExposedVariablesPropertyWidget
from .global_variables import WIDGET_NAME, WIDGET_TITLE


class Extension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._registered = False

    def on_startup(self, ext_id):
        self._register_widget()

    def on_shutdown(self):
        if self._registered:
            self._unregister_widget()

    def _register_widget(self):
        property_window = omni.kit.window.property.get_window()
        if property_window:
            property_window.register_widget(
                "prim",
                WIDGET_NAME,
                ExposedVariablesPropertyWidget(title=WIDGET_TITLE, attribute_namespace_filter=[EXPOSED_ATTR_NS]),
            )
            self._registered = True

    def _unregister_widget(self):
        property_window = omni.kit.window.property.get_window()
        if property_window:
            property_window.unregister_widget("prim", WIDGET_NAME)
            self._registered = False
