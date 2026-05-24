# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import asyncio
import json

import carb
import omni.kit.test

message = "Hello World!"


class TestSockets(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        settings = carb.settings.get_settings()
        self._socket_port = settings.get("/exts/isaacsim.code_editor.vscode/port")
        self._publish_carb_logs = settings.get("/exts/isaacsim.code_editor.vscode/carb_logs")

    # After running each test
    async def tearDown(self):
        pass

    async def test_tcp_socket(self):
        # open TCP socket (code execution)
        reader, writer = await asyncio.open_connection("127.0.0.1", self._socket_port)
        writer.write(f'print("{message}")'.encode())
        # wait for code execution
        for _ in range(10):
            await asyncio.sleep(0.1)
        # parse response
        data = await reader.read()
        data = json.loads(data.decode())
        # validate output
        print("response:", data)
        self.assertEqual("ok", data.get("status", None))
        self.assertEqual(message, data.get("output", None))

    async def test_udp_socket(self):
        class ClientProtocol(asyncio.Protocol):
            def connection_made(self, transport):
                self.transport = transport
                self._data = []

            def datagram_received(self, data, addr):
                self._data.append(data.decode())

            def get_data(self):
                return " ".join(self._data)

        if not self._publish_carb_logs:
            carb.log_warn("carb log publishing is disabled")
            return

        # register client to consume carb logs
        transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: ClientProtocol(), remote_addr=("127.0.0.1", self._socket_port)
        )
        transport.sendto(b"*")
        # open TCP socket (code execution to log info)
        reader, writer = await asyncio.open_connection("127.0.0.1", self._socket_port)
        writer.write(f'carb.log_info("{message}")'.encode())
        # wait for code execution
        for _ in range(10):
            await asyncio.sleep(0.1)
        # close UDP socket
        transport.close()
        # validate logs
        print("logs:", protocol.get_data())
        self.assertIn(f"[Info][isaacsim.code_editor.vscode.extension] {message}", protocol.get_data())
