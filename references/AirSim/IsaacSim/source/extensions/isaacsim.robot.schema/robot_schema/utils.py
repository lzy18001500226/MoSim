# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from __future__ import annotations

import omni
import pxr
from usd.schema.isaac.robot_schema import *


def GetAllRobotJoints(
    stage: pxr.Usd.Stage, robot_link_prim: pxr.Usd.Prim, parse_nested_robots: bool = True
) -> list[pxr.Usd.Prim]:
    """Returns all the joints of the robot.

    Args:
        stage: The USD stage containing the robot.
        robot_link_prim: The USD prim representing the robot link.
        parse_nested_robots: Whether to parse nested robots for joints.

    Returns:
        A list of USD prims representing the joints of the robot.
    """
    joints = []
    if robot_link_prim.HasAPI(Classes.JOINT_API.value):
        return [robot_link_prim]
    elif robot_link_prim.HasAPI(Classes.ROBOT_API.value):
        rel = robot_link_prim.GetRelationship(Relations.ROBOT_JOINTS.name)
        if rel:
            joint_relations = rel.GetTargets()
            for joint_relation in joint_relations:
                joint = stage.GetPrimAtPath(joint_relation)
                if joint.HasAPI(Classes.JOINT_API.value) or parse_nested_robots:
                    joints = joints + GetAllRobotJoints(stage, joint, parse_nested_robots)
    return joints


def GetAllRobotLinks(
    stage: pxr.Usd.Stage, robot_link_prim: pxr.Usd.Prim, include_reference_points: bool = False
) -> list[pxr.Usd.Prim]:
    """Returns all the links of the robot.

    Args:
        stage: The USD stage containing the robot.
        robot_link_prim: The USD prim representing the robot link.
        include_reference_points: Whether to include reference points as links.

    Returns:
        A list of USD prims representing the links of the robot.
    """
    links = []
    if robot_link_prim.HasAPI(Classes.LINK_API.value):
        return [robot_link_prim]
    elif include_reference_points and robot_link_prim.HasAPI(Classes.REFERENCE_POINT_API.value):
        return [robot_link_prim]
    elif robot_link_prim.HasAPI(Classes.ROBOT_API.value):
        rel = robot_link_prim.GetRelationship(Relations.ROBOT_LINKS.name)
        if rel:
            link_relations = rel.GetTargets()
            for link_relation in link_relations:
                link = stage.GetPrimAtPath(link_relation)
                links = links + GetAllRobotLinks(stage, link, include_reference_points)
    return links


class RobotLinkNode:
    """Represents a node in the robot's kinematic tree structure.

    Attributes:
        prim: The USD prim representing this link
        path: The USD path to this link
        name: The name of this link
        _parent: Reference to the parent link node
        _children: List of child link nodes
        _joints: List of joints connected to this link
        _joint_to_parent: The joint connecting this link to its parent
    """

    def __init__(self, prim: pxr.Usd.Prim, parentLink: RobotLinkNode = None, joint: pxr.Usd.Prim = None):
        self.prim = prim
        if prim:
            self.path = prim.GetPath()
            self.name = prim.GetName()
        else:
            self.path = None
            self.name = None
        self._parent = parentLink
        self._children = []
        self._joints = []
        self._joint_to_parent = joint

    def add_child(self, child: RobotLinkNode):
        """Adds a child link node to this node.

        Args:
            child: The RobotLinkNode to add as a child
        """
        self.children.append(child)

    @property
    def children(self):
        """Returns the list of child nodes.

        Returns:
            list[RobotLinkNode]: List of child link nodes
        """
        return self._children

    @property
    def parent(self):
        """Returns the parent node.

        Returns:
            RobotLinkNode: The parent link node, or None if this is the root
        """
        return self._parent


def GetJointBodyRelationship(joint_prim: pxr.Usd.Prim, bodyIndex: int):
    """Gets the relationship target for a joint's body connection.

    Args:
        joint_prim: The USD prim representing the joint.
        bodyIndex: Index of the body (0 or 1) to get the relationship for.

    Returns:
        The target path of the body relationship, or None if not found or excluded from articulation.
    """
    joint = pxr.UsdPhysics.Joint(joint_prim)
    if joint:
        # Ignoring joints with ExcludeFromArticulation to avoid graph instances
        exclude_from_articulation = joint.GetExcludeFromArticulationAttr()
        if exclude_from_articulation and exclude_from_articulation.Get():
            return None
        rel = None
        if bodyIndex == 0:
            rel = joint.GetBody0Rel()
        elif bodyIndex == 1:
            rel = joint.GetBody1Rel()
        if rel:
            targets = rel.GetTargets()
            if targets:
                return targets[0]
    return None


def PrintRobotTree(root: RobotLinkNode, indent=0):
    """Prints a visual representation of the robot link tree structure.

    Args:
        root: The root node of the robot link tree.
        indent: Number of spaces to indent each level (default: 0).
    """
    print(" " * indent + root.name)
    for child in root.children:
        PrintRobotTree(child, indent + 2)


def GetJointPose(robot_prim: pxr.Usd.Prim, joint_prim: pxr.Usd.Prim) -> pxr.Gf.Matrix4d:
    """Returns the pose of a joint in the robot's coordinate system.

    Args:
        robot_prim: The USD prim representing the robot.
        joint_prim: The USD prim representing the joint.

    Returns:
        pxr.Gf.Matrix4d: The joint's pose matrix in robot coordinates, or None if pose cannot be computed.
    """
    robot_transform = pxr.Gf.Matrix4f(omni.usd.get_world_transform_matrix(robot_prim))
    joint = pxr.UsdPhysics.Joint(joint_prim)
    stage = joint_prim.GetStage()
    if joint:
        body0 = joint.GetBody0Rel().GetTargets()
        body0_transform = None
        joint_transform = None
        if body0:
            joint_local_translate = joint.GetLocalPos0Attr().Get()
            joint_local_rotate = joint.GetLocalRot0Attr().Get()
            body0_prim = stage.GetPrimAtPath(body0[0])
            local_0 = pxr.Gf.Matrix4f()
            local_0.SetTranslate(joint_local_translate)
            local_0.SetRotateOnly(joint_local_rotate)
            body0_pose = pxr.Gf.Matrix4f(omni.usd.get_world_transform_matrix(body0_prim))
            joint_pose = local_0 * body0_pose
            return joint_pose * robot_transform.GetInverse()
        else:
            body1 = joint.GetBody1Rel().GetTargets()
            body1_prim = stage.GetPrimAtPath(body1[0])
            joint_local_translate = joint.GetLocalPos1Attr().Get()
            joint_local_rotate = joint.GetLocalRot1Attr().Get()
            local_1 = pxr.Gf.Matrix4f()
            local_1.SetTranslate(joint_local_translate)
            local_1.SetRotateOnly(joint_local_rotate)
            body1_pose = pxr.Gf.Matrix4f(omni.usd.get_world_transform_matrix(body1_prim))
            joint_pose = body1_pose * local_1
            return joint_pose * robot_transform.GetInverse()

    return None


def GetLinksFromJoint(root: RobotLinkNode, joint_prim: pxr.Usd.Prim) -> tuple[list[pxr.Usd.Prim], list[pxr.Usd.Prim]]:
    """Returns two lists of links: those before and after the specified joint in the kinematic chain.

    Args:
        root: The root node of the robot link tree.
        joint_prim: The joint prim to find in the tree.

    Returns:
        tuple[list[pxr.Usd.Prim], list[pxr.Usd.Prim]]: Lists of links (before_joint, after_joint).
    """

    def find_node_with_joint(node: RobotLinkNode, target_joint: pxr.Usd.Prim) -> RobotLinkNode:
        """Helper function to find the node that has the target joint as _joint_to_parent."""
        if node._joint_to_parent == target_joint:
            return node
        for child in node.children:
            result = find_node_with_joint(child, target_joint)
            if result:
                return result
        return None

    def collect_forward_links(node: RobotLinkNode) -> list[pxr.Usd.Prim]:
        """Collects all links in the forward direction (children) from a node."""
        links = [node.prim]
        for child in node.children:
            links.extend(collect_forward_links(child))
        return links

    def collect_backward_links(node: RobotLinkNode) -> list[pxr.Usd.Prim]:
        """Collects all links in the backward direction (parents) from a node."""
        links = []
        current = node.parent
        old_current = node
        while current:
            links.append(current.prim)
            if current:
                for child in current.children:
                    if child != old_current and child.prim not in links:
                        links += collect_forward_links(child)
            current = current.parent
        return links

    # Find the node that has our target joint as _joint_to_parent
    node_after_joint = find_node_with_joint(root, joint_prim)
    if not node_after_joint:
        return [], []

    # Get links after the joint (including the link after the joint)
    forward_links = collect_forward_links(node_after_joint)

    # Get links before the joint (including the link before the joint)
    backward_links = collect_backward_links(node_after_joint.parent)

    return backward_links, forward_links


def GenerateRobotLinkTree(stage: pxr.Usd.Stage, robot_link_prim: pxr.Usd.Prim = None) -> RobotLinkNode:
    """Generates a tree structure of robot links using an iterative approach.

    Args:
        stage: The USD stage containing the robot.
        robot_link_prim: The root prim of the robot.

    Returns:
        RobotLinkNode: The root node of the generated tree.
    """
    # Initialize data structures
    joints_per_body0 = {}
    joints_per_body1 = {}

    # Get all links and joints
    all_links = [a for a in pxr.Usd.PrimRange(robot_link_prim) if a.HasAPI(Classes.LINK_API.value)]
    all_joints = [a for a in pxr.Usd.PrimRange(robot_link_prim) if a.HasAPI(Classes.JOINT_API.value)]

    # Get root link and initialize mappings
    links = GetAllRobotLinks(stage, robot_link_prim)
    if not links:
        return None
    root = RobotLinkNode(links[0])
    joints_per_body = [{link.GetPath(): [] for link in all_links}] * 2

    # Build joint mappings
    for joint in all_joints:
        body0 = GetJointBodyRelationship(joint, 0)
        body1 = GetJointBodyRelationship(joint, 1)
        if body0:
            joints_per_body[0][body0].append(joint)
        if body1:
            joints_per_body[1][body1].append(joint)

    # Use a stack for iterative traversal
    stack = [root]
    processed_joints = []

    while stack:
        current = stack.pop()
        for i in range(2):
            if current.prim.GetPath() in joints_per_body[i]:
                for joint in joints_per_body[i][current.prim.GetPath()]:
                    if joint not in processed_joints:
                        processed_joints.append(joint)
                        body1 = GetJointBodyRelationship(joint, 1)
                        # Check if it's not connecting to its parent
                        if body1 and (current.parent is None or current.parent.path != body1):
                            child = RobotLinkNode(stage.GetPrimAtPath(body1), current, joint)
                            current._joints.append(joint)
                            current.add_child(child)
                            stack.append(child)

    return root
