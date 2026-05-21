# Copyright 2023-2026 AgentEra(Agently.Tech)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import threading
import warnings
from sys import modules
from typing import Any

_DEPRECATION_WARNING_SETTING_KEY = "runtime.show_deprecation_warnings"


class DeprecationWarnings:
    _warned_once_keys: set[str] = set()
    _warning_once_lock = threading.Lock()

    @staticmethod
    def _mark_warning_key(key: str) -> bool:
        normalized_key = str(key)
        with DeprecationWarnings._warning_once_lock:
            if normalized_key in DeprecationWarnings._warned_once_keys:
                return False
            DeprecationWarnings._warned_once_keys.add(normalized_key)
            return True

    @staticmethod
    def _coerce_warning_setting_enabled(value) -> bool:
        if isinstance(value, str):
            return value.strip().lower() not in {
                "0",
                "false",
                "no",
                "off",
                "disable",
                "disabled",
            }
        return bool(value)

    @staticmethod
    def _deprecation_warnings_enabled() -> bool:
        base_module = modules.get("agently.base")
        settings = getattr(base_module, "settings", None)
        if settings is None:
            return True
        try:
            value = settings.get(_DEPRECATION_WARNING_SETTING_KEY, True)
        except Exception:
            return True
        return DeprecationWarnings._coerce_warning_setting_enabled(value)

    @staticmethod
    def warn_deprecated_once(
        key: str,
        message: str,
        *,
        stacklevel: int = 2,
    ):
        if not DeprecationWarnings._deprecation_warnings_enabled():
            return
        if not DeprecationWarnings._mark_warning_key(key):
            return
        warnings.warn(message, DeprecationWarning, stacklevel=stacklevel + 1)

    @staticmethod
    def log_deprecated_once(key: str, logger: Any, message: str):
        if not DeprecationWarnings._deprecation_warnings_enabled():
            return
        if DeprecationWarnings._mark_warning_key(key):
            logger.warning(message)

    @staticmethod
    def reset_registry():
        with DeprecationWarnings._warning_once_lock:
            DeprecationWarnings._warned_once_keys.clear()


warn_deprecated_once = DeprecationWarnings.warn_deprecated_once
log_deprecated_once = DeprecationWarnings.log_deprecated_once
reset_deprecation_warning_registry = DeprecationWarnings.reset_registry
