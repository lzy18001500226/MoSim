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


from agently.core import BaseAgent


class StreamingPrintExtension(BaseAgent):
    async def async_streaming_print(self):
        async_generator = self.get_async_generator(type="delta")
        print()
        async for delta in async_generator:
            print(delta, end="", flush=True)
        print()

    def streaming_print(self):
        generator = self.get_generator(type="delta")
        print()
        for delta in generator:
            print(delta, end="", flush=True)
        print()
