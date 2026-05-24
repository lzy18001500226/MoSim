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

#include <omni/isaac/dynamic_control/DynamicControlTypes.h>

#include <memory>
#include <unordered_map>

namespace std
{
}

namespace omni
{
namespace isaac
{
namespace dynamic_control
{
constexpr uint64_t kHandleContextMask = 0xffffff0000000000;
constexpr uint64_t kHandleTypeMask = 0x000000ff00000000;
constexpr uint64_t kHandleObjectMask = 0x00000000ffffffff;

constexpr DcHandle makeHandle(uint64_t objectId, uint64_t typeId, uint64_t contextId)
{
    return objectId | (typeId << 32) | (contextId << 40);
}

constexpr uint32_t getHandleObjectId(DcHandle h)
{
    return static_cast<uint32_t>(h & kHandleObjectMask);
}

constexpr uint32_t getHandleTypeId(DcHandle h)
{
    return static_cast<uint32_t>((h & kHandleTypeMask) >> 32);
}

constexpr uint32_t getHandleContextId(DcHandle h)
{
    return static_cast<uint32_t>(h >> 40);
}

/**
 * @class Bucket
 * @brief A container for managing objects with unique IDs
 * @details
 * Provides a way to store, retrieve, and remove objects using unique IDs.
 * Takes ownership of the objects and manages their lifetime.
 *
 * @tparam T The type of objects stored in the bucket
 */
template <class T>
class Bucket
{
public:
    /**
     * @brief Adds an object to the bucket
     * @details Takes ownership of the object and assigns it a unique ID
     *
     * @param[in] obj The object to add, transferred as an rvalue reference
     * @return The unique ID assigned to the object
     */
    uint32_t add(std::unique_ptr<T>&& obj)
    {
        uint32_t id = ++mNextId;
        mDict[id] = std::move(obj);
        return id;
    }

    /**
     * @brief Gets an object by its ID
     * @details Returns a pointer to the object if found, or nullptr if not found
     *
     * @param[in] id The ID of the object to retrieve
     * @return Pointer to the object, or nullptr if not found
     */
    T* get(uint32_t id) const
    {
        auto it = mDict.find(id);
        if (it != mDict.end())
        {
            return it->second.get();
        }
        else
        {
            return nullptr;
        }
    }

    /**
     * @brief Removes an object by its ID
     * @details If the object is found, it is removed and destroyed
     *
     * @param[in] id The ID of the object to remove
     */
    void remove(uint32_t id)
    {
        auto it = mDict.find(id);
        if (it != mDict.end())
        {
            mDict.erase(it);
        }
    }

    /**
     * @brief Clears all objects from the bucket
     * @details Removes and destroys all objects
     */
    void clear()
    {
        mDict.clear();
    }

private:
    // can convert this to a generational index if needed
    std::unordered_map<uint32_t, std::unique_ptr<T>> mDict;

    uint32_t mNextId = 0;
};

}
}
}
