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

from __future__ import annotations

import contextlib
import threading
from typing import Generator, Literal

import carb

_context = threading.local()  # thread-local storage to handle nested contexts and concurrent access
_fsd_enabled = carb.settings.get_settings().get_as_bool("/app/useFabricSceneDelegate")


@contextlib.contextmanager
def use_backend(
    backend: Literal["usd", "usdrt", "fabric", "tensor"],
    *,
    raise_on_unsupported: bool = False,
    raise_on_fallback: bool = False,
) -> Generator[None, None, None]:
    """Context manager that sets a thread-local backend value.

    .. warning::

        The :guilabel:`usdrt` and :guilabel:`fabric` backends require Fabric Scene Delegate (FSD) to be enabled.
        FSD can be enabled in *apps/.kit* experience files by setting ``app.useFabricSceneDelegate = true``.

    Args:
        backend: The value to set in the context.
        raise_on_unsupported: Whether to raise an exception if the backend is not supported when requested.
        raise_on_fallback: Whether to raise an exception if the backend is supported,
            but a fallback is being used at a particular point in time when requested.

    Raises:
        RuntimeError: If the ``usdrt`` or ``fabric`` backend is specified but Fabric Scene Delegate (FSD) is disabled.

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.backend as backend_utils
        >>>
        >>> with backend_utils.use_backend("usdrt"):
        ...    # operate on the specified backend
        ...    pass
        >>> # operate on the default backend
    """
    # check if USDRT/fabric backend
    if backend in ["usdrt", "fabric"] and not _fsd_enabled:
        raise RuntimeError(
            "'usdrt' and 'fabric' backends require Fabric Scene Delegate (FSD) to be enabled. "
            "Enable FSD in .kit experience settings ('app.useFabricSceneDelegate = true') to use them."
        )
    # store previous context value if it exists
    previous_backend = getattr(_context, "backend", None)
    previous_raise_on_unsupported = getattr(_context, "raise_on_unsupported", False)
    previous_raise_on_fallback = getattr(_context, "raise_on_fallback", False)
    # set new context value
    try:
        _context.backend = backend
        _context.raise_on_unsupported = raise_on_unsupported
        _context.raise_on_fallback = raise_on_fallback
        yield
    # remove context value or restore previous one if it exists
    finally:
        if previous_backend is None:
            delattr(_context, "backend")
        else:
            _context.backend = previous_backend
        _context.raise_on_unsupported = previous_raise_on_unsupported
        _context.raise_on_fallback = previous_raise_on_fallback


def get_current_backend(supported_backends: list[str], *, raise_on_unsupported: bool | None = None) -> str:
    """Get the current backend value if it exists.

    Args:
        supported_backends: The list of supported backends.
        raise_on_unsupported: Whether to raise an error if the backend is not supported when requested.
            If set to a value other than ``None``, this parameter has precedence over the context value.

    Returns:
        The current backend value or the default value (first supported backend) if no backend is active.
    """
    backend = getattr(_context, "backend", supported_backends[0])
    if backend not in supported_backends:
        if raise_on_unsupported is None:
            raise_on_unsupported = getattr(_context, "raise_on_unsupported", False)
        if raise_on_unsupported:
            supported_backends = ", ".join([f"'{item}'" for item in supported_backends])
            raise RuntimeError(f"Unsupported backend: '{backend}'. Supported backends: {supported_backends}")
        carb.log_warn(f"Unsupported backend: '{backend}'. Falling back to '{supported_backends[0]}' backend.")
        return supported_backends[0]
    return backend


def is_backend_set() -> bool:
    """Check if a backend is set in the context.

    Returns:
        Whether a backend is set in the context.
    """
    return getattr(_context, "backend", None) is not None


def should_raise_on_unsupported() -> bool:
    """Check whether an exception should be raised, depending on the context's raise on unsupported state.

    Returns:
        Whether an exception should be raised on unsupported backend.
    """
    return getattr(_context, "raise_on_unsupported", False)


def should_raise_on_fallback() -> bool:
    """Check whether an exception should be raised, depending on the context's raise on fallback state.

    Returns:
        Whether an exception should be raised on fallback backend.
    """
    return getattr(_context, "raise_on_fallback", False)
