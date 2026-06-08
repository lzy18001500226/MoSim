// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include "GenericModelOutput.h"
#include "isaacsim/core/includes/Buffer.h"

namespace isaacsim
{
namespace sensors
{
namespace rtx
{

void copyTimestamps(uint64_t* timestamps, const uint64_t timestampNs, const int32_t* timeOffsetNs, const int numElements, int maxThreadsPerBlock, int multiProcessorCount, const int cudaDeviceIndex, cudaStream_t stream);

// Cached version that reuses temp storage to avoid reallocation every frame
void findValidIndices(size_t* dataIn, size_t* dataOut, int* numValidPoints, size_t numPoints, uint8_t* flags,
                           int cudaDeviceIndex, cudaStream_t stream, void** d_temp_storage, size_t* temp_storage_bytes, int* cached_numPoints);

void fillIndices(size_t* indices, size_t numIndices, int maxThreadsPerBlock, int cudaDeviceIndex, cudaStream_t stream = 0);

size_t getTempStorageSizeForValidIndices(size_t maxPoints, int cudaDeviceIndex);

void fillValidCartesianPoints(float* azimuth, float* elevation, float* range, float3* cartesianPoints, size_t* validIndices, int* numValidPoints, size_t maxPoints, int maxThreadsPerBlock, int multiProcessorCount, int cudaDeviceIndex, cudaStream_t stream);

// Fused function for required basic outputs (azimuth, elevation, distance, intensity)
void selectRequiredValidPoints(
    const float* azimuthSrc, const float* elevationSrc, const float* distanceSrc, const float* intensitySrc,
    float* azimuthDst, float* elevationDst, float* distanceDst, float* intensityDst,
    const size_t* validIndices, int* numValidPoints, size_t maxPoints,
    uint32_t enableMask, int maxThreadsPerBlock, int cudaDeviceIndex, cudaStream_t stream);

// Fused function for optional outputs (timestamp, IDs, normals, velocities)
void selectOptionalValidPoints(
    const uint64_t* timestampSrc, const uint32_t* emitterIdSrc, const uint32_t* materialIdSrc, const uint8_t* objectIdSrc,
    const float3* normalSrc, const float3* velocitySrc,
    uint64_t* timestampDst, uint32_t* emitterIdDst, uint32_t* materialIdDst, uint8_t* objectIdDst,
    float3* normalDst, float3* velocityDst,
    const size_t* validIndices, int* numValidPoints, size_t maxPoints,
    uint32_t enableMask, int maxThreadsPerBlock, int cudaDeviceIndex, cudaStream_t stream);

}
}
}
