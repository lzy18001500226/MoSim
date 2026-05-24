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

from typing import Optional

import torch


class PytorchListener:
    """A Observer/Listener that keeps track of updated data sent by the writer. Is passed in the
    initialization of a PytorchWriter at which point it is pinged by the writer after any data is
    passed to the writer."""

    def __init__(self):
        self.data = {}

    def write_data(self, data: dict) -> None:
        """Updates the existing data in the listener with the new data provided.

        Args:
            data (dict): new data retrieved from writer.
        """

        self.data.update(data)

    def get_rgb_data(self) -> Optional[torch.Tensor]:
        """Returns RGB data as a batched tensor from the current data stored.

        Returns:
            images (Optional[torch.Tensor]): images in batched pytorch tensor form
        """

        if "pytorch_rgb" in self.data:
            images = self.data["pytorch_rgb"]
            images = images[..., :3]
            images = images.permute(0, 3, 1, 2)
            return images
        else:
            return None
