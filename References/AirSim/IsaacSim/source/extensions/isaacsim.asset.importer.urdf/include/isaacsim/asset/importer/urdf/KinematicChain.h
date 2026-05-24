// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include "UrdfTypes.h"

#include <memory>
#include <string>
#include <vector>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace urdf
{
/**
 * @class KinematicChain
 * @brief Represents the kinematic chain of a robot as a tree structure.
 * @details
 * This class builds and manages a tree representation of a robot's kinematic
 * structure, where each node represents a link connected by joints. The tree
 * structure allows for efficient traversal and analysis of the robot's
 * kinematic relationships.
 */
class KinematicChain
{
public:
    /**
     * @struct Node
     * @brief Represents a single node in the kinematic tree.
     * @details
     * Each node represents a link in the robot with its associated parent joint
     * and child nodes (links). This forms a tree structure representing the
     * complete kinematic chain of the robot.
     */
    struct Node
    {
        /**
         * @brief Name of the link represented by this node
         */
        std::string linkName_;

        /**
         * @brief Name of the parent joint connecting this link
         */
        std::string parentJointName_;

        /**
         * @brief Collection of child nodes (links) connected to this node
         */
        std::vector<std::unique_ptr<Node>> childNodes_;

        /**
         * @brief Constructs a new node with specified link and parent joint names
         * @param[in] linkName Name of the link for this node
         * @param[in] parentJointName Name of the parent joint connecting this link
         */
        Node(std::string linkName, std::string parentJointName) : linkName_(linkName), parentJointName_(parentJointName)
        {
        }
    };

    /**
     * @brief Root node of the kinematic tree (base link)
     */
    std::unique_ptr<Node> baseNode;

    /**
     * @brief Default constructor creates an empty kinematic chain
     */
    KinematicChain() = default;

    /**
     * @brief Destructor cleans up the kinematic tree
     */
    ~KinematicChain();

    /**
     * @brief Computes the kinematic chain for a URDF robot description
     * @param[in] urdfRobot URDF robot data structure to build chain from
     * @return True if kinematic chain was successfully computed, false otherwise
     */
    bool computeKinematicChain(const UrdfRobot& urdfRobot);

private:
    /**
     * @brief Recursively finds and builds a node's children
     * @param[in,out] parentNode Parent node to find children for
     * @param[in] urdfRobot URDF robot data structure
     */
    void computeChildNodes(std::unique_ptr<Node>& parentNode, const UrdfRobot& urdfRobot);
};

}
}
}
}
