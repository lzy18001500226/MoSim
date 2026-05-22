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
"""This module provides the Selection class to encapsulate selection details, including a description and a timestamp."""

__all__ = ["Selection"]

import time


class Selection:
    """A class that encapsulates a selection with a description.

    This class holds the details of a selection, including a timestamp of when the selection was created or modified. It provides the ability to update the timestamp to the current time.

    Args:
        description (str): A brief description of the selection.
        selection: The actual content of the selection."""

    def __init__(self, description, selection):
        """Initialize a new Selection instance with the given description and selection data."""
        self.time = time.monotonic()
        self.description = description
        self.selection = selection

    def touch(self):
        """Updates the timestamp of the selection to the current time."""
        self.time = time.monotonic()
