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
import omni.graph.core as og
from omni.replicator.core.utils import utils

_context = None


class ReplicatorIsaacContext:
    def __init__(self, num_envs, action_graph_entry_node):
        self._num_envs = num_envs
        self._action_graph_entry_node = action_graph_entry_node
        self._reset_inds = None
        self.trigger = False

        controller = og.Controller()
        self._graph = controller.graph(utils.GRAPH_PATH)
        self._tendon_attribute_stack = [None]

    def trigger_randomization(self, reset_inds):
        self.trigger = True
        self._reset_inds = reset_inds
        self._action_graph_entry_node.request_compute()
        self._graph.evaluate()

    @property
    def reset_inds(self):
        return self._reset_inds

    def get_tendon_exec_context(self):
        return self._tendon_attribute_stack[-1]

    def add_tendon_exec_context(self, node):
        self._tendon_attribute_stack.append(node)


def initialize_context(num_envs, action_graph_entry_node):
    global _context
    _context = ReplicatorIsaacContext(num_envs, action_graph_entry_node)


def get_reset_inds():
    return _context.reset_inds


def trigger_randomization(reset_inds):
    _context.trigger_randomization(reset_inds)
