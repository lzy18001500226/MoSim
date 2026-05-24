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
"""This module provides functions for file-related actions within the Omniverse Kit Menu such as posting notifications, quitting the application, handling USD stages, and registering or deregistering actions."""

__all__ = ["register_actions", "deregister_actions"]

import carb
import omni.kit.actions.core
import omni.kit.window.file
import omni.usd


def post_notification(message: str, info: bool = False, duration: int = 3):
    """Posts a notification with a given message.

    Args:
        message (str): The message to be displayed in the notification.
        info (bool, optional): If True, the notification is of type INFO. Otherwise, it's of type WARNING. Defaults to False.
        duration (int, optional): The duration in seconds for which the notification should be displayed. Defaults to 3.
    """
    try:
        import omni.kit.notification_manager as nm

        _type = nm.NotificationStatus.WARNING
        if info:
            _type = nm.NotificationStatus.INFO

        nm.post_notification(message, status=_type, duration=duration)
    except ModuleNotFoundError:
        carb.log_warn(message)


def quit_kit(fast: bool = False):
    """Initiates the application shutdown process.

    Args:
        fast (bool): If True, sets the application to fast shutdown mode before quitting.
                     Default is False, which means a regular shutdown.
    """
    if fast:
        carb.settings.get_settings().set("/app/fastShutdown", True)
    omni.kit.app.get_app().post_quit()


def open_stage_with_new_edit_layer():
    """Opens the current USD stage with a new edit layer.

    This function retrieves the current stage from the USD context, checks if it is valid,
    and then opens it with a new edit layer using the 'open_with_new_edit_layer' method
    from 'omni.kit.window.file'. If the stage is not valid, a notification is posted.

    Raises:
        Posts a warning notification if no valid stage is available."""
    stage = omni.usd.get_context().get_stage()
    if not stage:
        post_notification("Cannot Re-open with New Edit Layer. No valid stage")
        return

    omni.kit.window.file.open_with_new_edit_layer(stage.GetRootLayer().identifier)


def register_actions(extension_id):
    """Registers file-related actions within an extension.

    Args:
        extension_id (str): The unique identifier for the extension that is registering the actions.

    This method registers several actions related to file operations, including exiting the application, exiting quickly, and opening the current stage with a new edit layer. These actions are tagged as 'File Actions' and are made available in the application's UI under the 'File' menu.
    """
    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "File Actions"

    action_registry.register_action(
        extension_id,
        "quit",
        lambda: quit_kit(fast=False),
        display_name="File->Exit",
        description="Exit",
        tag=actions_tag,
    )
    action_registry.register_action(
        extension_id,
        "quit_fast",
        lambda: quit_kit(fast=True),
        display_name="File->Exit Fast",
        description="Exit Fast",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "open_stage_with_new_edit_layer",
        open_stage_with_new_edit_layer,
        display_name="File->Open Current Stage With New Edit Layer",
        description="Open Stage With New Edit Layer",
        tag=actions_tag,
    )


def deregister_actions(extension_id):
    """Removes all registered actions for a given extension from the action registry.

    Args:
        extension_id (str): The unique identifier of the extension whose actions are to be deregistered.
    """
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)
