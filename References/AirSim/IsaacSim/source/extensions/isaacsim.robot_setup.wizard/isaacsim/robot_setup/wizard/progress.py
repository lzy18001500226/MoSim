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
from enum import Enum

from .utils.utils import Singleton


class ProgressColorState(Enum):
    REMAINING = 0
    IN_PROGRESS = 1
    ACTIVE = 2
    COMPLETE = 3


def Singleton(class_):
    """A singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@Singleton
class ProgressRegistry:
    class _Event(set):
        """
        A list of callable objects. Calling an instance of this will cause a
        call to each item in the list in ascending order by index.
        """

        def __call__(self, *args, **kwargs):
            """Called when the instance is “called” as a function"""
            # Call all the saved functions
            for f in self:
                f(*args, **kwargs)

        def __repr__(self):
            """
            Called by the repr() built-in function to compute the “official”
            string representation of an object.
            """
            return f"Event({set.__repr__(self)})"

    class _EventSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, event, fn):
            """
            Save the function, the event, and add the function to the event.
            """
            self._fn = fn
            self._event = event
            event.add(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    def __init__(self):
        # TODO: begin_edit/end_edit
        self.__on_progress_changed = self._Event()
        self._steps_dict = {}

    def destroy(self):
        """Called to cancel current search"""
        pass

    def set_steps(self, steps):
        """Set the steps"""
        self._steps_dict = steps

    def get_progress_by_name(self, step_name):
        """Get the steps"""
        if step_name in self._steps_dict:
            return self._steps_dict[step_name]
        return None

    def _progress_changed(self, step_name, state):
        """Call the event object that has the list of functions"""
        self.__on_progress_changed(step_name, state)

    def subscribe_progress_changed(self, fn):
        """
        Return the object that will automatically unsubscribe when destroyed.
        """
        return self._EventSubscription(self.__on_progress_changed, fn)

    def set_step_progress(self, step_name, state):
        if step_name in self._steps_dict:
            if self._steps_dict[step_name] != state:
                self._steps_dict[step_name] = state
                self._progress_changed(step_name, state)

    def get_active_step(self):
        """Return the name of the currently active step"""
        for step_name, state in self._steps_dict.items():
            if state == ProgressColorState.ACTIVE:
                return step_name
        return None
