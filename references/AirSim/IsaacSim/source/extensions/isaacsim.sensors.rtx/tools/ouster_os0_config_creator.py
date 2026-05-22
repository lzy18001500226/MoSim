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
model = "OS0"
channels = 128

# use the get_beam_intrinsics so you have the angle azimuths and elevation...
#  THESE ARE JUST AN EXAMPLE, YOU SHOULD GET YOUR OWN FROM YOUR SENSOR!
# The Length of these should be the same as the channels in the sensor.
# yapf: disable
beam_intrinsics = {
   "beam_azimuth_angles": [
        4.23, 1.41, -1.4, -4.21, 4.22,
        1.42, -1.41, -4.22, 4.23, 1.41,
        -1.42, -4.21, 4.23, 1.42, -1.4,
        -4.2, 4.23, 1.41, -1.39, -4.21,
        4.25, 1.43, -1.41,-4.22, 4.24,
        1.44, -1.41, -4.22, 4.23, 1.42,
        -1.38, -4.22, 4.23, 1.41, -1.4,
       -4.21, 4.22, 1.42, -1.41, -4.22,
       4.23, 1.41, -1.42, -4.21, 4.23,
       1.42, -1.4, -4.2, 4.23, 1.41,
       -1.39, -4.21,4.25, 1.43, -1.41,
       -4.22, 4.24, 1.44, -1.41, -4.22,
       4.23, 1.42, -1.38, -4.22,
        4.23, 1.41, -1.4, -4.21, 4.22,
        1.42, -1.41, -4.22, 4.23, 1.41,
        -1.42, -4.21, 4.23, 1.42, -1.4,
        -4.2, 4.23, 1.41, -1.39, -4.21,
        4.25, 1.43, -1.41,-4.22, 4.24,
        1.44, -1.41, -4.22, 4.23, 1.42,
        -1.38, -4.22, 4.23, 1.41, -1.4,
       -4.21, 4.22, 1.42, -1.41, -4.22,
       4.23, 1.41, -1.42, -4.21, 4.23,
       1.42, -1.4, -4.2, 4.23, 1.41,
       -1.39, -4.21,4.25, 1.43, -1.41,
       -4.22, 4.24, 1.44, -1.41, -4.22,
       4.23, 1.42, -1.38, -4.22],
   "beam_altitude_angles": [
       44.50, 43.80, 43.10, 42.40, 41.70,
       41.00, 40.30, 39.59, 38.89, 38.19,
       37.49, 36.79, 36.09, 35.39, 34.69,
       33.99, 33.29, 32.59, 31.89, 31.19,
       30.48, 29.78, 29.08, 28.38, 27.68,
       26.98, 26.28, 25.58, 24.88, 24.18,
       23.48, 22.78, 22.07, 21.37, 20.67,
       19.97, 19.27, 18.57, 17.87, 17.17,
       16.47, 15.77, 15.07, 14.37, 13.67,
       12.96, 12.26, 11.56, 10.86, 10.16,
       9.46, 8.76, 8.06, 7.36, 6.66, 5.96,
       5.26, 4.56, 3.85, 3.15, 2.45, 1.75,
       1.05, 0.35, -0.35, -1.05, -1.75,
       -2.45, -3.15, -3.85, -4.56, -5.26,
       -5.96, -6.66, -7.36, -8.06, -8.76,
       -9.46, -10.16, -10.86, -11.56, -12.26,
       -12.96, -13.67, -14.37, -15.07, -15.77,
       -16.47, -17.17, -17.87, -18.57, -19.27,
       -19.97, -20.67, -21.37, -22.07, -22.78,
       -23.48, -24.18, -24.88, -25.58, -26.28,
       -26.98, -27.68, -28.38, -29.08, -29.78,
       -30.48, -31.19, -31.89, -32.59, -33.29,
       -33.99, -34.69, -35.39, -36.09, -36.79,
       -37.49, -38.19, -38.89, -39.59, -40.30,
       -41.00, -41.70, -42.40, -43.10, -43.80,
       -44.50],
   "lidar_origin_to_beam_origin_mm": 36.180
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
            f'    "name": "{name}", {comment(f"{brand} {model} {channels} channels @ {hz}Hz {resolution} horizontal resolution")},'
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
            f'        "farRangeM": 50.0, {comment("OPTICAL PERFORMANCE- Range 45 m @ >90% detection probability, 100 klx sunlight 50 m @ >50% detection probability, 100 klx sunlight")},'
        )
        print("        ")
        print(f'        "rangeResolutionM": 0.001, {comment("OPTICAL PERFORMANCE- Range Resolution 0.1 cm")},')
        print("        ")
        print('        "avgPowerW": 0.002,')
        print(
            f'        "minReflectance": 0.1, {comment("OPTICAL PERFORMANCE - Range (10% Lambertian reflectivity, 1024 @ 10 Hz mode)")},'
        )
        print(
            f'        "minReflectanceRange": 20.0, {comment("OPTICAL PERFORMANCE - Range 15 m @ >90% detection probability, 100 klx sunlight 20 m @ >50% detection probability, 100 klx sunlight")},'
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
