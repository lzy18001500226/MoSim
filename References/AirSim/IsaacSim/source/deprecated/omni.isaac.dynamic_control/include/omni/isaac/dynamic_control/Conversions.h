// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include <carb/Types.h>

#include <omni/isaac/dynamic_control/DynamicControl.h>
#include <usdrt/gf/matrix.h>
#include <usdrt/gf/quat.h>
#include <usdrt/gf/vec.h>

#include <PxActor.h>

namespace omni
{
namespace isaac
{
namespace dynamic_control
{

namespace conversions
{
/**
 * @brief Converts a carb::Float3 into a pxr::GfVec3f.
 * @details Performs a direct component-wise conversion from Carb's Float3 to USD's GfVec3f.
 *
 * @param[in] v Input vector in Carb format
 * @return pxr::GfVec3f Equivalent vector in USD format
 *
 * @note No precision loss as both types use single precision
 */
inline pxr::GfVec3f asGfVec3f(const carb::Float3& v)
{
    return pxr::GfVec3f(v.x, v.y, v.z);
}

/**
 * @brief Converts a carb::Float4 into a pxr::GfQuatf.
 * @details
 * Converts a quaternion from Carb to USD format, handling component reordering:
 * - Carb format: (x, y, z, w)
 * - USD format: (w, x, y, z)
 *
 * @param[in] q Input quaternion in Carb format
 * @return pxr::GfQuatf Equivalent quaternion in USD format
 *
 * @note Component order is adjusted during conversion
 */
inline pxr::GfQuatf asGfQuatf(const carb::Float4& q)
{
    return pxr::GfQuatf(q.w, q.x, q.y, q.z);
}

/**
 * @brief Converts a carb::Float3 into a pxr::GfVec3d.
 * @details
 * Performs a component-wise conversion with promotion to double precision:
 * - x, y, z components are converted from float to double
 *
 * @param[in] v Input vector in Carb format (single precision)
 * @return pxr::GfVec3d Equivalent vector in USD format (double precision)
 *
 * @note Involves precision promotion from float to double
 */
inline pxr::GfVec3d asGfVec3d(const carb::Float3& v)
{
    return pxr::GfVec3d(v.x, v.y, v.z);
}

/**
 * @brief Converts a carb::Float4 into a pxr::GfQuatd.
 * @details
 * Converts a quaternion from Carb to USD format with precision promotion:
 * - Handles component reordering (x,y,z,w) -> (w,x,y,z)
 * - Promotes single precision to double precision
 *
 * @param[in] q Input quaternion in Carb format (single precision)
 * @return pxr::GfQuatd Equivalent quaternion in USD format (double precision)
 *
 * @note Combines component reordering with precision promotion
 */
inline pxr::GfQuatd asGfQuatd(const carb::Float4& q)
{
    return pxr::GfQuatd(q.w, q.x, q.y, q.z);
}

/**
 * @brief Converts a carb::Float4 into a pxr::GfRotation.
 * @details
 * Creates a USD rotation representation from a Carb quaternion:
 * 1. Converts the quaternion to GfQuatd format
 * 2. Constructs a GfRotation from the quaternion
 *
 * @param[in] q Input quaternion in Carb format
 * @return pxr::GfRotation Equivalent rotation in USD format
 *
 * @see asGfQuatd
 */
inline pxr::GfRotation asGfRotation(const carb::Float4& q)
{
    return pxr::GfRotation(asGfQuatd(q));
}

/**
 * @brief Converts a DcTransform into a pxr::GfTransform.
 * @details
 * Creates a complete transform from a Dynamic Control transform:
 * 1. Sets rotation using quaternion conversion
 * 2. Sets translation using vector conversion
 *
 * @param[in] pose Input transform in Dynamic Control format
 * @return pxr::GfTransform Equivalent transform in USD format
 *
 * @see asGfRotation
 * @see asGfVec3d
 */
inline pxr::GfTransform asGfTransform(const omni::isaac::dynamic_control::DcTransform& pose)
{
    pxr::GfTransform trans;
    trans.SetRotation(asGfRotation(pose.r));
    trans.SetTranslation(asGfVec3d(pose.p));
    return trans;
}

/**
 * @brief Converts a DcTransform to a GfMatrix4f.
 * @details
 * Creates a 4x4 transformation matrix in single precision:
 * 1. Sets translation component from position
 * 2. Sets rotation component from quaternion
 *
 * @param[in] input Input transform in Dynamic Control format
 * @return pxr::GfMatrix4f Equivalent transform matrix in USD format
 *
 * @note Uses single precision floating point
 * @see asGfVec3f
 * @see asGfQuatf
 */
inline pxr::GfMatrix4f asGfMatrix4f(const omni::isaac::dynamic_control::DcTransform& input)
{
    pxr::GfMatrix4f mat;
    mat.SetTranslateOnly(asGfVec3f(input.p));
    mat.SetRotateOnly(pxr::GfMatrix3f(asGfQuatf(input.r)));
    return mat;
}

/**
 * @brief Converts a DcTransform to a transposed GfMatrix4f.
 * @details
 * Creates a transposed 4x4 transformation matrix:
 * 1. Sets translation and rotation components
 * 2. Transposes the resulting matrix
 *
 * @param[in] input Input transform in Dynamic Control format
 * @return pxr::GfMatrix4f Transposed transform matrix in USD format
 *
 * @note Useful for operations requiring column-major matrix format
 * @see asGfMatrix4f
 */
inline pxr::GfMatrix4f asGfMatrix4fT(const omni::isaac::dynamic_control::DcTransform& input)
{
    pxr::GfMatrix4f mat;
    mat.SetTranslateOnly(asGfVec3f(input.p));
    mat.SetRotateOnly(pxr::GfMatrix3f(asGfQuatf(input.r)));
    return mat.GetTranspose();
}

/**
 * @brief Converts a DcTransform to a GfMatrix4d.
 * @details
 * Creates a 4x4 transformation matrix in double precision:
 * 1. Sets translation component with precision promotion
 * 2. Sets rotation component with precision promotion
 *
 * @param[in] input Input transform in Dynamic Control format
 * @return pxr::GfMatrix4d Equivalent transform matrix in USD format
 *
 * @note Promotes single precision components to double precision
 * @see asGfVec3d
 * @see asGfQuatd
 */
inline pxr::GfMatrix4d asGfMatrix4d(const omni::isaac::dynamic_control::DcTransform& input)
{
    pxr::GfMatrix4d mat;
    mat.SetTranslateOnly(asGfVec3d(input.p));
    mat.SetRotateOnly(pxr::GfMatrix3d(asGfQuatd(input.r)));
    return mat;
}

/**
 * @brief Converts DcTransform into PhysX transform.
 * @details
 * Creates a complete PhysX transform from Dynamic Control transform:
 * 1. Converts position to PxVec3
 * 2. Converts rotation to PxQuat
 *
 * @param[in] pose Input transform in Dynamic Control format
 * @return PxTransform Equivalent transform in PhysX format
 *
 * @note No precision loss as both formats use single precision
 * @see asPxVec3
 * @see asPxQuat
 */
inline ::physx::PxTransform asPxTransform(const omni::isaac::dynamic_control::DcTransform& pose)
{
    return ::physx::PxTransform{ asPxVec3(pose.p), asPxQuat(pose.r) };
}

/**
 * @brief Converts USD position and orientation into Dynamic Control transform.
 * @details
 * Creates a Dynamic Control transform from separate components:
 * 1. Converts position vector to Float3
 * 2. Converts orientation quaternion to Float4
 *
 * @param[in] p Position vector in USD format
 * @param[in] q Rotation quaternion in USD format
 * @return omni::isaac::dynamic_control::DcTransform Equivalent transform in Dynamic Control format
 *
 * @note No precision loss when using single precision USD types
 * @see asCarbFloat3
 * @see asCarbFloat4
 */
inline omni::isaac::dynamic_control::DcTransform asDcTransform(const pxr::GfVec3f& p, const pxr::GfQuatf& q)
{
    omni::isaac::dynamic_control::DcTransform pose;
    pose.p = asCarbFloat3(p);
    pose.r = asCarbFloat4(q);
    return pose;
}

/**
 * @brief Converts USD double precision position and orientation into Dynamic Control transform.
 * @details
 * Creates a Dynamic Control transform from separate components with precision demotion:
 * 1. Converts double precision position to Float3
 * 2. Converts double precision orientation to Float4
 *
 * @param[in] p Position vector in USD format (double precision)
 * @param[in] q Rotation quaternion in USD format (double precision)
 * @return omni::isaac::dynamic_control::DcTransform Equivalent transform in Dynamic Control format
 *
 * @warning Potential precision loss during double to float conversion
 * @see asCarbFloat3
 * @see asCarbFloat4
 */
inline omni::isaac::dynamic_control::DcTransform asDcTransform(const pxr::GfVec3d& p, const pxr::GfQuatd& q)
{
    omni::isaac::dynamic_control::DcTransform pose;
    pose.p = asCarbFloat3(p);
    pose.r = asCarbFloat4(q);
    return pose;
}
}
}
}
}
