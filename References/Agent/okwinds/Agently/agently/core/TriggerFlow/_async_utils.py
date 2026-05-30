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

import asyncio

from typing import Any, Awaitable


async def gather_cancel_on_error(*awaitables: Awaitable[Any] | asyncio.Task[Any]):
    tasks: list[asyncio.Future[Any]] = []
    for awaitable in awaitables:
        if isinstance(awaitable, asyncio.Task):
            tasks.append(awaitable)
        else:
            tasks.append(asyncio.ensure_future(awaitable))
    try:
        return await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
