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
brand = "ouster"
model = "OS1"
channels = 32

# use the get_beam_intrinsics so you have the angle azimuths and elevation...
#  THESE ARE JUST AN EXAMPLE, YOU SHOULD GET YOUR OWN FROM YOUR SENSOR!
# The Length of these should be the same as the channels in the sensor.
# yapf: disable
beam_intrinsics = {
    "beam_altitude_angles": [
        22.10, 20.67, 19.25, 17.82,
        16.40, 14.97, 13.55, 12.12,
        10.69, 9.27, 7.84, 6.42,
        4.99, 3.56, 2.14, 0.71, -0.71,
        -2.14, -3.56, -4.99, -6.42,
        -7.84, -9.27, -10.69, -12.12,
        -13.55, -14.97, -16.40, -17.82,
        -19.25, -20.67, -22.10],
    "beam_azimuth_angles": [
        4.23, 1.41, -1.4, -4.21, 4.22,
        1.42, -1.41, -4.22, 4.23, 1.41,
        -1.42, -4.21, 4.23, 1.42, -1.4,
        -4.2, 4.23, 1.41, -1.39, -4.21,
        4.25, 1.43, -1.41, -4.22, 4.24,
        1.44, -1.41, -4.22, 4.23, 1.42,
        -1.38, -4.22],
    "lidar_origin_to_beam_origin_mm": 15.806
}
# yapf: enable
# just a helper function so json file does not have the same entry for every comment
comment_count = 0


def comment(str_in):
    global comment_count
    comment_count = comment_count + 1
    return f'"comment{comment_count}" : "{str_in}"'


# Can configure the Hz and vertical resolutions
hzs = [10, 20]
resolutions = [512, 1024, 2048]
configs = []

for hz in hzs:
    for resolution in resolutions:
        if resolution * hz > 20480:
            # Not a legal configuration
            continue
        configs.append({"hz": hz, "resolution": resolution})


import os
import sys

original_stdout = sys.stdout

for config in configs:
    hz = config["hz"]
    resolution = config["resolution"]
    name = f"{model} {channels} {hz}hz @ {resolution} resolution"
    file_name = f"{model}_{channels}ch{hz}hz{resolution}res"
    file_name = f"./{file_name}.json"
    print(file_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w") as f:
        comment_count = 0
        sys.stdout = f
        print("{")
        print(
            f'    {comment("parameters obtained from https://storage.cloud.google.com/data.ouster.io/downloads/datasheets/datasheet-rev06-v2p4-os1.pdf")},'
        )
        print(f'    {comment("parameters without comments are assumed correct, but will ultimately need checking")},')
        print('    "class": "sensor",')
        print('    "type": "lidar",')
        print(
            f'    "name": "{name}", {comment(f"Ouster OS1 32 channels @ {hz}Hz {resolution} horizontal resolution")},'
        )
        print('    "driveWorksId": "GENERIC",')
        print('    "profile":')
        print("    {")
        print('        "scanType": "rotary",')
        print('        "intensityProcessing": "normalization",')
        print('        "rayType": "IDEALIZED",')
        print(f'        "nearRangeM": 0.3, {comment("OPTICAL PERFORMANCE-Minimum Range 0.3 m for point cloud data")},')
        print('        "minDistBetweenEchos": 0.3,')
        print(
            f'        "farRangeM": 120.0, {comment("OPTICAL PERFORMANCE- Range 100 m @ >90% detection probability, 100 klx sunlight 120 m @ >50% detection probability, 100 klx sunlight")},'
        )
        print("        ")
        print(f'        "rangeResolutionM": 0.001, {comment("OPTICAL PERFORMANCE- Range Resolution 0.1 cm")},')
        print("        ")
        print('        "avgPowerW": 0.002,')
        print(
            f'        "minReflectance": 0.1, {comment("OPTICAL PERFORMANCE - Range (10% Lambertian reflectivity, 1024 @ 10 Hz mode)")},'
        )
        print(
            f'        "minReflectanceRange": 55.0, {comment("OPTICAL PERFORMANCE - Range 45 m @ >90% detection probability, 100 klx sunlight 55 m @ >50% detection probability, 100 klx sunlight")},'
        )
        print(f'        "wavelengthNm": 865.0, {comment("LASER-  Laser Wavelength 865 nm")},')
        print('        "pulseTimeNs": 6,')
        print("        ")
        print(
            f'        {comment("These add noise to the emitter direction to each point randomly if Std is not 0.0")},'
        )
        print('        "azimuthErrorMean": 0.0,')
        print(
            f'        "azimuthErrorStd": 0.01, {comment("OPTICAL PERFORMANCE-Angular Sampling Accuracy Horizontal: ±0.01°")},'
        )
        print('        "elevationErrorMean": 0.0,')
        print(
            f'        "elevationErrorStd": 0.01, {comment("OPTICAL PERFORMANCE-Angular Sampling Accuracy Vertical: ±0.01°")},'
        )
        print("        ")
        print(f'        {comment("This adds jitter to the distance or the return but stays along the ray")},')
        print(
            f'        "rangeAccuracyM": 0.03, {comment("OPTICAL PERFORMANCE- Range Accuracy ±3 cm for lambertian targets, ±10 cm for retroreflectors")},'
        )
        print("        ")
        print('        "maxReturns": 2,')
        print("        ")
        print(f'        "scanRateBaseHz": {hz}.0,')
        print("        ")
        print(f'        "reportRateBaseHz": {hz*resolution},')
        print("        ")
        print(f'        "numberOfEmitters": {channels},')
        print("        ")
        print('        "emitters":')
        print("        {")

        print(f'            {comment("beam_azimuth_angles from get_beam_intrinsics")},')
        print('            "azimuthDeg": [', end="")
        for i in range(channels):
            end = ", "
            if i == channels - 1:
                end = "],"
            az = beam_intrinsics["beam_azimuth_angles"][i]
            print(f"{az}", end=end)
        print("")

        print(f'            {comment("beam_altitude_angles from get_beam_intrinsics")},')
        print('            "elevationDeg": [', end="")
        for i in range(channels):
            end = ", "
            if i == channels - 1:
                end = "],"
            el = beam_intrinsics["beam_altitude_angles"][i]
            print(f"{el}", end=end)
        print("")

        print(f'            "fireTimeNs": [', end="")
        firetimes_delta = int(1000000000.0 / (channels * hz * resolution))
        firetimes_start = int(firetimes_delta * 0.5)
        for i in range(channels):
            end = ", "
            if i == channels - 1:
                end = "]"
            ft = firetimes_start + i * firetimes_delta
            print(f"{ft}", end=end)
        print("")

        print("        },")
        print("        ")
        print('        "intensityMappingType": "LINEAR"')
        print("    }")
        print("}")

    sys.stdout = original_stdout  # Reset the standard output to its original value
