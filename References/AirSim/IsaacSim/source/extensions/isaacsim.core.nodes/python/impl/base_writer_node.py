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

import copy
from typing import List, Union

import carb.events
import omni.replicator.core as rep
import omni.usd
from pxr import Usd

from .base_reset_node import BaseResetNode


class WriterRequest:
    def __init__(self, writer: rep.Writer, render_product_path: Union[str, List[str]], activate: bool = True):
        self.writer = writer
        self.render_product_path = render_product_path
        self.activate = activate

    def __repr__(self) -> str:
        output = f"{self.writer.node_type_id}\n\t{self.writer._kwargs}\n\t{self.render_product_path}\n\tAnnotators:\n"
        for a in self.writer._annotators:
            output = output + f"\t\t{a}\n"
        return output


class BaseWriterNode(BaseResetNode):
    """
    Base class for nodes that automatically reset when stop is pressed.
    """

    def __init__(self, initialize: bool = False):
        self._writers = []
        self._requests = []
        self._event_stream = None
        super().__init__(initialize=False)

    def custom_reset(self):
        for w in self._writers:
            self._append_request(WriterRequest(w, None, False))
        self._writers = []
        self.initialized = False

    def append_writer(self, writer):
        """
        Appends deepcopy of provided writer to internal writer list.
        """
        self._writers.append(copy.deepcopy(writer))

    def attach_writers(self, render_product_path):
        """
        Creates writer request for all stored writers using provided render product,
        and activates them.
        """
        for w in self._writers:
            self._append_request(WriterRequest(w, render_product_path, True))

    def attach_writer(self, writer, render_product_path):
        """
        Creates writer request for deepcopy of provided writer to provided render_product_path, and activates it.
        """
        # Appending provided writer to member list
        self._writers.append(copy.deepcopy(writer))

        # Ensure previously appended writer is referenced for the WriterRequest
        self._append_request(WriterRequest(self._writers[-1], render_product_path, True))

    def _append_request(self, request: WriterRequest):
        self._requests.append(request)
        if self._event_stream is None:
            self._event_stream = carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
                on_event=self._process_activation_requests,
                observer_name="BaseWriterNode._process_activation_requests",
            )

    def _process_activation_requests(self, event):
        stage = omni.usd.get_context().get_stage()
        if not stage:
            self._event_stream = None
            return
        with Usd.EditContext(stage, stage.GetSessionLayer()):
            for request in self._requests:
                try:
                    if request.activate:
                        request.writer.attach(request.render_product_path)
                        self.post_attach(request.writer, request.render_product_path)
                        ### WAR to make sure the graph is not deleted on stop
                        noop = rep.AnnotatorRegistry.get_annotator(
                            "IsaacNoop",
                        )
                        noop.attach([request.render_product_path])
                        carb.log_info(f"Attaching:\n{request}")
                    else:
                        request.writer.detach()
                except Exception as e:
                    carb.log_error(
                        f"Could not process writer attach request {request.writer, request.render_product_path}, {e}"
                    )
            # Stop processing additional requests until another one is appended
            self._requests = []
            self._event_stream = None

    # Defined by subclass
    def post_attach(self, writer, render_product):
        pass
