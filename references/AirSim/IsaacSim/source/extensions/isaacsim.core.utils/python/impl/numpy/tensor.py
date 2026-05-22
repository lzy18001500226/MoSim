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

import numpy as np


def as_type(data, dtype):
    if dtype == "float32":
        return data.astype(np.float32)
    elif dtype == "bool":
        return data.astype(bool)
    elif dtype == "int32":
        return data.astype(np.int32)
    elif dtype == "int64":
        return data.astype(np.int64)
    elif dtype == "long":
        return data.astype(np.long)
    elif dtype == "uint8":
        return data.astype(np.uint8)
    else:
        print(f"Type {dtype} not supported.")


def convert(data, device=None, dtype="float32", indexed=None):
    return as_type(np.asarray(data), dtype)


def create_zeros_tensor(shape, dtype, device=None):
    return as_type(np.zeros(shape), dtype)


def create_tensor_from_list(data, dtype, device=None):
    return as_type(np.array(data), dtype)


def clone_tensor(data, device=None):
    return np.copy(data)


def resolve_indices(indices, count, device=None):
    result = indices
    if isinstance(indices, list):
        result = np.array(indices)
    if indices is None:
        result = np.arange(count)
    return result


def move_data(data, device=None):
    return data


def tensor_cat(data, device=None, dim=-1):
    return np.concatenate(data, axis=dim)


def expand_dims(data, axis):
    return np.expand_dims(data, axis)


def pad(data, pad_width, mode="constant", value=None):
    if mode == "constant" and value is not None:
        return np.pad(data, pad_width, mode, constant_values=value)
    if mode == "linear_ramp" and value is not None:
        return np.pad(data, pad_width, mode, end_values=value)
    return np.pad(data, pad_width, mode)


def tensor_stack(data, dim=0):
    return np.stack(data, axis=dim)


def to_list(data):
    if not isinstance(data, list):
        return data.tolist()
    return data


def to_numpy(data):
    return data


def assign(src, dst, indices):
    if isinstance(indices, list):
        dst[tuple(indices)] = src
    else:
        dst[indices] = src
    return dst
