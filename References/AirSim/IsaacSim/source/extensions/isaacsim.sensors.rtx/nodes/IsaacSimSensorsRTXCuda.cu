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

#include <cub/device/device_select.cuh>

#include "GenericModelOutput.h"
#include "isaacsim/core/includes/ScopedCudaDevice.h"
#include "isaacsim/core/includes/Buffer.h"
#include "IsaacSimSensorsRTXCuda.cuh"

namespace isaacsim
{
namespace sensors
{
namespace rtx
{

__global__ void copyTimestampsKernel(uint64_t* __restrict__ timestamps, const uint64_t timestampNs, const int32_t* __restrict__ timeOffsetNs, const int numElements) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= numElements) {
        return;
    }
    timestamps[idx] = timeOffsetNs[idx] + timestampNs;
}

void copyTimestamps(uint64_t* timestamps, const uint64_t timestampNs, const int32_t* timeOffsetNs, const int numElements, int maxThreadsPerBlock, int multiProcessorCount, const int cudaDeviceIndex, cudaStream_t stream) {
    if (numElements == 0) {
        return;
    }
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);
    const int nt = numElements < 1024 ? 256 : maxThreadsPerBlock;
    const int nb = numElements < 1024 ? (multiProcessorCount * 4) : (numElements + nt - 1) / nt;
    copyTimestampsKernel<<<nb, nt, 0, stream>>>(timestamps, timestampNs, timeOffsetNs, numElements);
}

__global__ void fillIndicesKernel(size_t* __restrict__ indices, const int length) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= length)
        return;
    indices[idx] = idx;
}

struct IsValid
{
    uint8_t* __restrict__ flags{ nullptr }; // sensor specific flags

    __host__ __device__ __forceinline__
    IsValid(uint8_t* __restrict__ flags) : flags(flags) {}

    __host__ __device__ __forceinline__
    bool operator()(const int &i) const {
        const uint8_t fl = flags[i];
        return (fl & omni::sensors::ElementFlags::VALID) == omni::sensors::ElementFlags::VALID;
    }
};

// Version that uses pre-allocated temporary storage for vGPU compatibility
void findValidIndices(size_t* __restrict__ dataIn, size_t* __restrict__ dataOut, int* __restrict__ numValidPoints, size_t numPoints, uint8_t* __restrict__ flags,
                           int cudaDeviceIndex, cudaStream_t stream, void** __restrict__ d_temp_storage, size_t* __restrict__ temp_storage_bytes, int* __restrict__ cached_numPoints) {
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);

    cub::DeviceSelect::If(
        *d_temp_storage,
        *temp_storage_bytes,
        dataIn,
        dataOut,
        numValidPoints,
        numPoints,
        IsValid(flags),
        stream
    );
}

void fillIndices(size_t* __restrict__ indices, size_t numIndices, int maxThreadsPerBlock, int cudaDeviceIndex, cudaStream_t stream) {
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);

    const int nt = maxThreadsPerBlock;
    const int nb = (numIndices + nt - 1) / nt;

    fillIndicesKernel<<<nb, nt, 0, stream>>>(indices, numIndices);
}

size_t getTempStorageSizeForValidIndices(size_t maxPoints, int cudaDeviceIndex) {
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);

    void* d_temp_storage = nullptr;
    size_t temp_storage_bytes = 0;

    // Query temp storage size for max points
    cub::DeviceSelect::If(
        d_temp_storage,
        temp_storage_bytes,
        static_cast<size_t*>(nullptr),
        static_cast<size_t*>(nullptr),
        static_cast<int*>(nullptr),
        maxPoints,
        IsValid(static_cast<uint8_t*>(nullptr))
    );

    return temp_storage_bytes;
}

__global__ void fillValidCartesianPointsKernel(
    const float* __restrict__ azimuth,
    const float* __restrict__ elevation,
    const float* __restrict__ range,
    float3* __restrict__ cartesianPoints,
    const size_t* __restrict__ validIndices,
    int numValidPoints)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= numValidPoints) return;

    size_t srcIdx = validIndices[idx];
    float azimuthDeg = azimuth[srcIdx];
    float elevationDeg = elevation[srcIdx];
    float rangeVal = range[srcIdx];

    float cosAzimuth, sinAzimuth, cosElevation, sinElevation;
    sincospif(azimuthDeg / 180.0f, &sinAzimuth, &cosAzimuth);
    sincospif(elevationDeg / 180.0f, &sinElevation, &cosElevation);

    // Compute intermediate value once
    float rangeXY = rangeVal * cosElevation;

    // Vectorized store using make_float3
    cartesianPoints[idx] = make_float3(
        rangeXY * cosAzimuth,      // x
        rangeXY * sinAzimuth,      // y
        rangeVal * sinElevation    // z
    );
}

// High-accuracy version with cached device properties
void fillValidCartesianPoints(float* __restrict__ azimuth, float* __restrict__ elevation, float* __restrict__ range, float3* __restrict__ cartesianPoints,
                                                 size_t* __restrict__ validIndices, int* __restrict__ numValidPointsDevice, size_t maxPoints,
                                                 int maxThreadsPerBlock, int multiProcessorCount,
                                                 int cudaDeviceIndex, cudaStream_t stream) {
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);

    // Get actual number of points to process
    int numValidPointsHost;
    CUDA_CHECK(cudaMemcpyAsync(&numValidPointsHost, numValidPointsDevice, sizeof(int), cudaMemcpyDeviceToHost, stream));
    CUDA_CHECK(cudaStreamSynchronize(stream));

    if (numValidPointsHost == 0) return;

    // optimize for occupancy
    if (numValidPointsHost < 1024) {
        // vectorized approach - high occupancy
        int nt = 256;
        int nb = (multiProcessorCount * 4); // Ensure high occupancy
        fillValidCartesianPointsKernel<<<nb, nt, 0, stream>>>(
            azimuth, elevation, range, cartesianPoints, validIndices, numValidPointsHost);
    } else {
        // use all available threads
        int nt = maxThreadsPerBlock;
        int nb = (numValidPointsHost + nt - 1) / nt;
        fillValidCartesianPointsKernel<<<nb, nt, 0, stream>>>(
            azimuth, elevation, range, cartesianPoints, validIndices, numValidPointsHost);
    }
}

// fused kernel for required basic outputs (azimuth, elevation, distance, intensity)
__global__ void selectRequiredValidPointsKernel(
    const float* __restrict__ azimuthSrc, const float* __restrict__ elevationSrc, const float* __restrict__ distanceSrc, const float* __restrict__ intensitySrc,
    float* __restrict__ azimuthDst, float* __restrict__ elevationDst, float* __restrict__ distanceDst, float* __restrict__ intensityDst,
    const size_t* __restrict__ validIndices, int* __restrict__ numValidPoints, uint32_t enableMask)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= *numValidPoints) {
        return;
    }

    size_t srcIdx = validIndices[idx];

    // vectorized loads for better memory bandwidth
    if (enableMask & 0xF) {
        if (enableMask & 1) azimuthDst[idx] = azimuthSrc[srcIdx];      // bit 0: azimuth
        if (enableMask & 2) elevationDst[idx] = elevationSrc[srcIdx];  // bit 1: elevation
        if (enableMask & 4) distanceDst[idx] = distanceSrc[srcIdx];    // bit 2: distance
        if (enableMask & 8) intensityDst[idx] = intensitySrc[srcIdx];  // bit 3: intensity
    }
}

// Optimized fused kernel for optional outputs
__global__ void selectOptionalValidPointsKernel(
    const uint64_t* __restrict__ timestampSrc, const uint32_t* __restrict__ emitterIdSrc, const uint32_t* __restrict__ materialIdSrc, const uint8_t* __restrict__ objectIdSrc,
    const float3* __restrict__ normalSrc, const float3* __restrict__ velocitySrc,
    uint64_t* __restrict__ timestampDst, uint32_t* __restrict__ emitterIdDst, uint32_t* __restrict__ materialIdDst, uint8_t* __restrict__ objectIdDst,
    float3* __restrict__ normalDst, float3* __restrict__ velocityDst,
    const size_t* __restrict__ validIndices, int* __restrict__ numValidPoints, uint32_t enableMask)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= *numValidPoints) {
        return;
    }

    size_t srcIdx = validIndices[idx];

    // Optional outputs - less frequently accessed together
    if (enableMask & (1 << 4)) timestampDst[idx] = timestampSrc[srcIdx];      // bit 4: timestamp
    if (enableMask & (1 << 5)) emitterIdDst[idx] = emitterIdSrc[srcIdx];      // bit 5: emitter ID
    if (enableMask & (1 << 6)) materialIdDst[idx] = materialIdSrc[srcIdx];    // bit 6: material ID
    if (enableMask & (1 << 7)) {                                              // bit 7: object ID
        for (size_t i = 0; i < 16; i++) {   // handle striding
            objectIdDst[idx * 16 + i] = objectIdSrc[srcIdx * 16 + i];
        }
    }
    if (enableMask & (1 << 8)) normalDst[idx] = normalSrc[srcIdx];            // bit 8: normal
    if (enableMask & (1 << 9)) velocityDst[idx] = velocitySrc[srcIdx];        // bit 9: velocity
}

// Host function to launch the required outputs kernel
void selectRequiredValidPoints(
    const float* __restrict__ azimuthSrc, const float* __restrict__ elevationSrc, const float* __restrict__ distanceSrc, const float* __restrict__ intensitySrc,
    float* __restrict__ azimuthDst, float* __restrict__ elevationDst, float* __restrict__ distanceDst, float* __restrict__ intensityDst,
    const size_t* __restrict__ validIndices, int* __restrict__ numValidPoints, size_t maxPoints,
    uint32_t enableMask, int maxThreadsPerBlock, int cudaDeviceIndex, cudaStream_t stream)
{
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);

    // Only launch if any required outputs are enabled
    if (enableMask == 0) return;

    const int nt = maxThreadsPerBlock;
    const int nb = (maxPoints + nt - 1) / nt;

    selectRequiredValidPointsKernel<<<nb, nt, 0, stream>>>(
        azimuthSrc, elevationSrc, distanceSrc, intensitySrc,
        azimuthDst, elevationDst, distanceDst, intensityDst,
        validIndices, numValidPoints, enableMask);
}

// Host function to launch the optional outputs kernel
void selectOptionalValidPoints(
    const uint64_t* __restrict__ timestampSrc, const uint32_t* __restrict__ emitterIdSrc, const uint32_t* __restrict__ materialIdSrc, const uint8_t* __restrict__ objectIdSrc,
    const float3* __restrict__ normalSrc, const float3* __restrict__ velocitySrc,
    uint64_t* __restrict__ timestampDst, uint32_t* __restrict__ emitterIdDst, uint32_t* __restrict__ materialIdDst, uint8_t* __restrict__ objectIdDst,
    float3* __restrict__ normalDst, float3* __restrict__ velocityDst,
    const size_t* __restrict__ validIndices, int* __restrict__ numValidPoints, size_t maxPoints,
    uint32_t enableMask, int maxThreadsPerBlock, int cudaDeviceIndex, cudaStream_t stream)
{
    isaacsim::core::includes::ScopedDevice scopedDevice(cudaDeviceIndex);

    // launch if any optional outputs are enabled
    if (enableMask == 0) return;

    const int nt = maxThreadsPerBlock;
    const int nb = (maxPoints + nt - 1) / nt;

    selectOptionalValidPointsKernel<<<nb, nt, 0, stream>>>(
        timestampSrc, emitterIdSrc, materialIdSrc, objectIdSrc,
        normalSrc, velocitySrc,
        timestampDst, emitterIdDst, materialIdDst, objectIdDst,
        normalDst, velocityDst,
        validIndices, numValidPoints, enableMask);
}

}   // namespace isaacsim
}   // namespace sensors
}   // namespace rtx
