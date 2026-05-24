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

#include <isaacsim/core/includes/Math.h>
#include <omni/isaac/dynamic_control/DynamicControlTypes.h>

#include <cmath>

namespace omni
{
namespace isaac
{
namespace dynamic_control
{
namespace math
{
using isaacsim::core::includes::math::operator+;
using isaacsim::core::includes::math::operator*;
/**
 * @brief Multiplies two transforms to compose them.
 * @details
 * Combines two transforms by applying them in sequence.
 * The order of multiplication matters (non-commutative).
 *
 * @param[in] self First transform (applied second)
 * @param[in] other Second transform (applied first)
 * @return DcTransform The composed transform
 *
 * @note The resulting transform applies other first, then self
 */
inline omni::isaac::dynamic_control::DcTransform operator*(const omni::isaac::dynamic_control::DcTransform& self,
                                                           const omni::isaac::dynamic_control::DcTransform& other)
{
    return omni::isaac::dynamic_control::DcTransform{ isaacsim::core::includes::math::rotate(self.r, other.p) + self.p,
                                                      isaacsim::core::includes::math::normalize(self.r * other.r) };
}

/**
 * @brief Computes the inverse of a transform.
 * @details
 * Calculates the inverse transform that, when applied after the original,
 * results in the identity transform.
 *
 * @param[in] transform Transform to invert
 * @return DcTransform The inverse transform
 *
 * @note For a valid transform T, T * inverse(T) equals the identity transform
 */
inline omni::isaac::dynamic_control::DcTransform inverse(const omni::isaac::dynamic_control::DcTransform& transform)
{
    omni::isaac::dynamic_control::DcTransform t;
    t.r = isaacsim::core::includes::math::inverse(transform.r);
    t.p = isaacsim::core::includes::math::rotate(t.r, transform.p) * -1.0f;
    return t;
}

/**
 * @brief Computes the relative transform from a to b.
 * @details
 * Calculates the transform that, when applied to a, results in b.
 * This is equivalent to inverse(a) * b.
 *
 * @param[in] a Reference transform
 * @param[in] b Target transform
 * @return DcTransform Transform from a to b
 */
inline omni::isaac::dynamic_control::DcTransform transformInv(const omni::isaac::dynamic_control::DcTransform& a,
                                                              const omni::isaac::dynamic_control::DcTransform& b)
{
    carb::Float4 qconj;
    qconj.w = a.r.w;
    qconj.x = -a.r.x;
    qconj.y = -a.r.y;
    qconj.z = -a.r.z;
    float invqnorm = 1.0f / (qconj.w * qconj.w + qconj.x * qconj.x + qconj.y * qconj.y + qconj.z * qconj.z);

    carb::Float4 qinv;
    qinv.w = qconj.w * invqnorm;
    qinv.x = -qconj.x * invqnorm;
    qinv.y = -qconj.y * invqnorm;
    qinv.z = -qconj.z * invqnorm;

    carb::Float4 qv = a.r;
    qv.w = 0;
    qv.x = b.p.x - a.p.x;
    qv.y = b.p.y - a.p.y;
    qv.z = b.p.z - a.p.z;

    carb::Float4 result = (qconj * (qv * qinv));
    carb::Float4 resQuat = (b.r * qconj);
    omni::isaac::dynamic_control::DcTransform res;
    res.p.x = result.x;
    res.p.y = result.y;
    res.p.z = result.z;
    res.r = resQuat;
    return res;
}


/**
 * @brief Linearly interpolates between two transforms.
 * @details
 * Performs separate linear interpolation on position and rotation components.
 * Position uses vector lerp, rotation uses quaternion lerp.
 *
 * @param[in] a Starting transform
 * @param[in] b Ending transform
 * @param[in] t Interpolation parameter [0,1]
 * @return DcTransform The interpolated transform
 */
inline omni::isaac::dynamic_control::DcTransform lerp(const omni::isaac::dynamic_control::DcTransform& a,
                                                      const omni::isaac::dynamic_control::DcTransform& b,
                                                      const float t)
{
    return omni::isaac::dynamic_control::DcTransform{ isaacsim::core::includes::math::lerp(a.p, b.p, t),
                                                      isaacsim::core::includes::math::lerp(a.r, b.r, t) };
}

/**
 * @brief Performs spherical linear interpolation between transforms.
 * @details
 * Interpolates position linearly and rotation using slerp.
 * This provides smoother rotation interpolation than regular lerp.
 *
 * @param[in] a Starting transform
 * @param[in] b Ending transform
 * @param[in] t Interpolation parameter [0,1]
 * @return DcTransform The interpolated transform
 */
inline omni::isaac::dynamic_control::DcTransform slerp(const omni::isaac::dynamic_control::DcTransform& a,
                                                       const omni::isaac::dynamic_control::DcTransform& b,
                                                       const float t)
{
    return omni::isaac::dynamic_control::DcTransform{ isaacsim::core::includes::math::lerp(a.p, b.p, t),
                                                      isaacsim::core::includes::math::slerp(a.r, b.r, t) };
}

}
}
}
}
