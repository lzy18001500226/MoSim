# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from typing import Callable, Tuple


def find_unique_string_name(initial_name: str, is_unique_fn: Callable[[str], bool]) -> str:
    """Find a unique string name based on the predicate function provided.

    The string is appended with "_N", where N is a natural number till the resultant string
    is unique.

    Args:
        initial_name (str): The initial string name.
        is_unique_fn (Callable[[str], bool]): The predicate function to validate against.

    Returns:
        str: A unique string based on input function.
    """
    if is_unique_fn(initial_name):
        return initial_name
    iterator = 1
    result = initial_name + "_" + str(iterator)
    while not is_unique_fn(result):
        result = initial_name + "_" + str(iterator)
        iterator += 1
    return result


def find_root_prim_path_from_regex(prim_path_regex: str) -> Tuple[str, int]:
    """Find the first prim above the regex pattern prim and its position.

    Args:
        prim_path_regex (str): full prim path including the regex pattern prim.

    Returns:
        Tuple[str, int]: First position is the prim path to the parent of the regex prim.
                    Second position represents the level of the regex prim in the USD stage tree representation.

    """
    prim_paths_list = str(prim_path_regex).split("/")
    root_idx = None
    for prim_path_idx in range(len(prim_paths_list)):
        chars = set("[]*|^")
        if any((c in chars) for c in prim_paths_list[prim_path_idx]):
            root_idx = prim_path_idx
            break
    root_prim_path = None
    tree_level = None
    if root_idx is not None:
        root_prim_path = "/".join(prim_paths_list[:root_idx])
        tree_level = root_idx
    return root_prim_path, tree_level
