# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import omni.usd

from .array_widget import ArrayPropertiesWidget
from .custom_data import CustomDataWidget
from .name_override import NameOverrideWidget
from .namespace import NamespaceWidget


class IsaacPropertyWidgets(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._registered = False

    def on_startup(self, ext_id):
        self._register_widget()

    def on_shutdown(self):
        self._unregister_widget()

    def _register_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        w.register_widget("prim", "isaac_array", ArrayPropertiesWidget(title="Array Properties", collapsed=True), False)
        w.register_widget(
            "prim", "isaac_custom_data", CustomDataWidget(title="Prim Custom Data", collapsed=True), False
        )
        self._isaac_name_override = NameOverrideWidget(title="Name Override", collapsed=False)
        w.register_widget("prim", "isaac_name_override", self._isaac_name_override, False)
        self._isaac_namespace = NamespaceWidget(title="Namespace", collapsed=False)
        w.register_widget("prim", "isaac_namespace", self._isaac_namespace, False)

    def _unregister_widget(self):
        import omni.kit.window.property as p

        w = p.get_window()
        if w:
            w.unregister_widget("prim", "isaac_array")
            w.unregister_widget("prim", "isaac_custom_data")
            w.unregister_widget("prim", "isaac_name_override")
            w.unregister_widget("prim", "isaac_namespace")
            self._isaac_name_override.destroy()
            self._isaac_namespace.destroy()
            self._registered = False
