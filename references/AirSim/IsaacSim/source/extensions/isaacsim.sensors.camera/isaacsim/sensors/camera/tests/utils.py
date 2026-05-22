# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os

import cv2
import numpy as np


def save_image(
    image, filename: str, golden_dir: str, test_dir: str, save_as_golden: bool = False, save_as_test: bool = False
) -> None:
    if not filename.lower().endswith(".png"):
        filename += ".png"
    if save_as_test:
        image_path = os.path.join(test_dir, filename)
        print(f" - saving image (test): {image_path}")
        os.makedirs(test_dir, exist_ok=True)
        cv2.imwrite(image_path, image)
    if save_as_golden:
        image_path = os.path.join(golden_dir, filename)
        print(f" - saving image (golden): {image_path}")
        os.makedirs(golden_dir, exist_ok=True)
        cv2.imwrite(image_path, image)


def compare_images(src1, src2, ksize=5, thresh=30, hist_div=1):
    def compare_histograms(src1, src2):
        # gray scale images
        if src1.ndim == 2:
            # calculate histograms
            hist1 = cv2.calcHist([src1], [0], None, [int(256 / hist_div)], [0, 256])
            hist2 = cv2.calcHist([src2], [0], None, [int(256 / hist_div)], [0, 256])
        # colored images
        elif src1.ndim == 3 and src1.shape[2] == 3:
            # convert to HSV color space
            hsv1 = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)
            hsv2 = cv2.cvtColor(src2, cv2.COLOR_BGR2HSV)
            # calculate histograms
            hist1 = cv2.calcHist([hsv1], [0, 1], None, [int(180 / hist_div), int(256 / hist_div)], [0, 180, 0, 256])
            hist2 = cv2.calcHist([hsv2], [0, 1], None, [int(180 / hist_div), int(256 / hist_div)], [0, 180, 0, 256])
        else:
            raise ValueError(f"Unknown format. Shape: {src1.shape}")
        # normalize histograms
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        # compare histograms
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    def background_subtraction(src1, src2):
        # gray scale images
        if src1.ndim == 2:
            pass
        # colored images
        elif src1.ndim == 3 and src1.shape[2] == 3:
            # convert to gray scale
            src1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
            src2 = cv2.cvtColor(src2, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError(f"Unknown format. Shape: {src1.shape}")
        # compute naive background subtraction
        diff = cv2.absdiff(src1, src2)
        _, diff = cv2.threshold(diff, thresh, 255, cv2.THRESH_BINARY)  # + cv2.THRESH_OTSU)
        diff = cv2.erode(diff, np.ones((ksize, ksize), np.uint8))
        # scale mask
        return np.exp(-10 * np.sum(diff == 255) / diff.size)

    # pre-process images
    # - remove dimensions with shape 1
    src1 = np.squeeze(src1)
    src2 = np.squeeze(src2)
    # - check dims and shape/channels
    assert src1.ndim == src2.ndim, f"Number of dimensions does not match: {src1.ndim} != {src2.ndim}"
    if src1.ndim == 3:
        assert src1.shape[2] == src2.shape[2], f"Number of channels does not match: {src1.shape[2]} != {src2.shape[2]}"
    assert src1.shape[:2] == src2.shape[:2], f"Shapes does not match: {src1.shape[:2]} != {src2.shape[:2]}"
    # - apply filter to "smooth" images
    src1 = cv2.medianBlur(src1, ksize)
    src2 = cv2.medianBlur(src2, ksize)

    h_score = compare_histograms(src1, src2)
    bs_score = background_subtraction(src1, src2)
    return (h_score * bs_score, h_score, bs_score)
