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

import re

from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry


class ExposedVariablesPropertyWidget(UsdPropertiesWidget):
    def __init__(self, title: str, attribute_namespace_filter: list, collapsed: bool = False):
        # Set multi_edit=False to handle each prim individually
        super().__init__(title, collapsed, multi_edit=False)

        # Only properties starting with these namespaces will be included in the widget
        self._attribute_namespace_filter = attribute_namespace_filter

        # Stores the properties ui entries to be built by the widget
        self._props_to_build = []

        # Initialize the multiple selection flag
        self._multiple_selection = False

    def on_new_payload(self, payload):
        """Handles new payloads to refresh UI or update models."""
        if not super().on_new_payload(payload):
            return False

        if not self._payload or len(self._payload) == 0:
            return False

        stage = self._payload.get_stage()
        if not stage:
            return False

        # Collect properties from all selected prims
        self._props_to_build = []
        for prim_path in self._payload:
            prim = self._get_prim(prim_path)
            if not prim:
                continue
            # Skip if the prim does not have scripting enabled
            if not prim.HasAttribute("omni:scripting:scripts"):
                continue
            # Skip if the scripts list is empty
            if not prim.GetAttribute("omni:scripting:scripts").Get():
                continue
            props = self._get_prim_properties(prim)
            for prop in props:
                # Get the property name (e.g., 'exposedVar:locationRandomizer:includeChildren')
                prop_name = prop.GetName()

                # Check if the property starts with the filter namespace (e.g., 'exposedVar', ignore the rest)
                if not prop_name.split(":")[0] in self._attribute_namespace_filter:
                    continue

                # Set the initia display name to the prim path (e.g., '/World/MyPrim'); will be adjusted later
                display_group = str(prim_path)

                # Update metadata with the default value (non-schema properties do not have a default value) to avoid warning:
                # [Warning] [omni.kit.property.usd.placeholder_attribute] PlaceholderAttribute.Get() customData.default or default not found in metadata
                metadata_with_default = prop.GetAllMetadata()
                metadata_with_default.update({"default": prop.Get()})

                # Used by the UI to select the appropriate editor widget for this property (e.g., 'int', 'string')
                prop_type = prop.GetPropertyType() if hasattr(prop, "GetPropertyType") else type(prop)

                # Create a new UI entry for the property
                ui_entry = UsdPropertyUiEntry(prop_name, display_group, metadata_with_default, prop_type)

                # List of UI property entries will be forwarded to '_customize_props_layout' to build the widget
                self._props_to_build.append(ui_entry)

        # If multiple prims are selected, the widget will display the properties into separate groups using the prim path
        self._multiple_selection = len(self._payload) > 1

        # Do not create the widget if no valid properties found
        return bool(self._props_to_build)

    def _get_shared_properties_from_selected_prims(self, anchor_prim):
        """Override to provide properties for the base class's build_items()."""
        # Return only the filtered UI properties to _customize_props_layout
        return self._props_to_build

    def _customize_props_layout(self, props):
        """Customize the layout by setting display groups and names for properties."""
        # Iterate over the UI property entries and set the (nested) display group(s) and name
        for prop in props:
            # The display group has been previously set as the prim path
            prim_path = prop.display_group

            # If only one prim is selected, do not include the prim path in the display group
            if not self._multiple_selection:
                prim_path = ""

            # Get the property name (e.g., 'exposedVar:locationRandomizer:range:minPosition')
            prop_name = prop.prop_name

            # Split the property name into parts
            parts = prop_name.split(":")
            # If the property name has at least 3 parts, it includes the filter namespace and the property name
            if len(parts) >= 3:
                # The first part is the filter namespace, remove it (e.g., 'exposedVar')
                parts = parts[1:]
                # The last part is the property display name which will not be capitalized (e.g., 'includeChildren')
                display_name = parts[-1]
                # Capitalize the other parts to create the nested display groups (e.g., 'Location Randomizer', 'Range')
                group_titles = [self._make_capitalized_title(part) for part in parts[:-1]]

                # Using colon ':' in display_group creates the nested groups in the UI (e.g.,'Location Randomizer:Range')
                # If multiple selection, include the prim path in the display group (e.g., '/World/MyPrim:Location Randomizer:Range')
                new_display_group = f"{prim_path}:{':'.join(group_titles)}" if prim_path else ":".join(group_titles)
            else:
                # Randomizer namespace not inlcuded: adding to a default group
                group_title = "Other"
                display_name = prop_name
                # If multiple selection, include the prim path in the display group (e.g., '/World/MyPrim:Other')
                new_display_group = f"{prim_path}:{group_title}" if prim_path else group_title

            # Override the display group and display name with the new values
            prop.override_display_group(new_display_group)
            prop.override_display_name(display_name)

        # Return the UI property entries with the updated display groups and names to be built by the widget
        return props

    def _make_capitalized_title(self, namespace_name):
        """Convert names to 'Capitalized With Spaces' format."""
        if "_" in namespace_name:
            return namespace_name.replace("_", " ").title()  # snake_case
        return re.sub(r"(?<!^)(?=[A-Z])", " ", namespace_name).title()  # camelCase or PascalCase
