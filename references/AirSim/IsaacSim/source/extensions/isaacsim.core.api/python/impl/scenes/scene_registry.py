# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from isaacsim.core.api.materials.deformable_material import DeformableMaterial
from isaacsim.core.api.materials.deformable_material_view import DeformableMaterialView
from isaacsim.core.api.materials.particle_material import ParticleMaterial
from isaacsim.core.api.materials.particle_material_view import ParticleMaterialView
from isaacsim.core.api.robots.robot import Robot
from isaacsim.core.api.robots.robot_view import RobotView
from isaacsim.core.api.sensors.base_sensor import BaseSensor
from isaacsim.core.api.sensors.rigid_contact_view import RigidContactView
from isaacsim.core.prims import (
    Articulation,
    ClothPrim,
    DeformablePrim,
    GeometryPrim,
    ParticleSystem,
    RigidPrim,
    SingleArticulation,
    SingleClothPrim,
    SingleDeformablePrim,
    SingleGeometryPrim,
    SingleParticleSystem,
    SingleRigidPrim,
    SingleXFormPrim,
    XFormPrim,
)


class SceneRegistry(object):
    """Class to keep track of the different types of objects added to the scene

    Example:

    .. code-block:: python

        >>> from isaacsim.core.api.scenes import SceneRegistry
        >>>
        >>> scene_registry = SceneRegistry()
        >>> scene_registry
        <isaacsim.core.api.scenes.scene_registry.SceneRegistry object at 0x...>
    """

    def __init__(self) -> None:
        self._rigid_objects = dict()
        self._geometry_objects = dict()
        self._articulated_systems = dict()
        self._robots = dict()
        self._xforms = dict()
        self._sensors = dict()
        self._xform_prim_views = dict()
        self._deformable_prims = dict()
        self._deformable_prim_views = dict()
        self._deformable_materials = dict()
        self._deformable_material_views = dict()
        self._cloth_prims = dict()
        self._cloth_prim_views = dict()
        self._particle_systems = dict()
        self._particle_system_views = dict()
        self._particle_materials = dict()
        self._particle_material_views = dict()
        self._geometry_prim_views = dict()
        self._rigid_prim_views = dict()
        self._rigid_contact_views = dict()
        self._articulated_views = dict()
        self._robot_views = dict()

        self._all_object_dicts = [
            self._rigid_objects,
            self._geometry_objects,
            self._articulated_systems,
            self._robots,
            self._xforms,
            self._sensors,
            self._xform_prim_views,
            self._deformable_prims,
            self._deformable_prim_views,
            self._deformable_materials,
            self._deformable_material_views,
            self._cloth_prims,
            self._cloth_prim_views,
            self._particle_systems,
            self._particle_system_views,
            self._particle_materials,
            self._particle_material_views,
            self._geometry_prim_views,
            self._rigid_prim_views,
            self._rigid_contact_views,
            self._articulated_views,
            self._robot_views,
        ]
        return

    @property
    def articulated_systems(self) -> dict:
        """Registered ``SingleArticulation`` objects"""
        return self._articulated_systems

    @property
    def rigid_objects(self) -> dict:
        """Registered ``SingleRigidPrim`` objects"""
        return self._rigid_objects

    @property
    def rigid_prim_views(self) -> dict:
        """Registered ``RigidPrim`` objects"""
        return self._rigid_prim_views

    @property
    def rigid_contact_views(self) -> dict:
        """Registered ``RigidContactView`` objects"""
        return self._rigid_contact_views

    @property
    def geometry_prim_views(self) -> dict:
        """Registered ``GeometryPrim`` objects"""
        return self._geometry_prim_views

    @property
    def articulated_views(self) -> dict:
        """Registered ``Articulation`` objects"""
        return self._articulated_views

    @property
    def robot_views(self) -> dict:
        """Registered ``RobotView`` objects"""
        return self._robot_views

    @property
    def robots(self) -> dict:
        """Registered ``Robot`` objects"""
        return self._robots

    @property
    def xforms(self) -> dict:
        """Registered ``SingleXFormPrim`` objects"""
        return self._xforms

    @property
    def sensors(self) -> dict:
        """Registered ``BaseSensor`` (and derived) objects"""
        return self._sensors

    @property
    def xform_prim_views(self) -> dict:
        """Registered ``XFormPrim`` objects"""
        return self._xform_prim_views

    @property
    def deformable_prims(self) -> dict:
        """Registered ``SingleDeformablePrim`` objects"""
        return self._deformable_prims

    @property
    def deformable_prim_views(self) -> dict:
        """Registered ``DeformablePrim`` objects"""
        return self._deformable_prim_views

    @property
    def deformable_materials(self) -> dict:
        """Registered ``DeformableMaterial`` objects"""
        return self._deformable_materials

    @property
    def deformable_material_views(self) -> dict:
        """Registered ``DeformableMaterialView`` objects"""
        return self._deformable_material_views

    @property
    def cloth_prims(self) -> dict:
        """Registered ``SingleClothPrim`` objects"""
        return self._cloth_prims

    @property
    def cloth_prim_views(self) -> dict:
        """Registered ``ClothPrim`` objects"""
        return self._cloth_prim_views

    @property
    def particle_systems(self) -> dict:
        """Registered ``SingleParticleSystem`` objects"""
        return self._particle_systems

    @property
    def particle_system_views(self) -> dict:
        """Registered ``ParticleSystem`` objects"""
        return self._particle_system_views

    @property
    def particle_materials(self) -> dict:
        """Registered ``ParticleMaterial`` objects"""
        return self._particle_materials

    @property
    def particle_material_views(self) -> dict:
        """Registered ``particle_material_view`` objects"""
        return self._particle_material_views

    # TODO: add if name exists check uniqueness
    def add_rigid_object(self, name: str, rigid_object: SingleRigidPrim) -> None:
        """Register a ``SingleRigidPrim`` (or subclass) object

        Args:
            name (str): object name
            rigid_object (SingleRigidPrim): object
        """
        self._rigid_objects[name] = rigid_object
        return

    def add_rigid_prim_view(self, name: str, rigid_prim_view: RigidPrim) -> None:
        """Register a ``RigidPrim`` (or subclass) object

        Args:
            name (str): object name
            rigid_prim_view (RigidPrim): object
        """
        self._rigid_prim_views[name] = rigid_prim_view
        return

    def add_rigid_contact_view(self, name: str, rigid_contact_view: RigidContactView) -> None:
        """Register a ``RigidContactView`` (or subclass) object

        Args:
            name (str): object name
            rigid_contact_view (RigidContactView): object
        """
        self._rigid_contact_views[name] = rigid_contact_view
        return

    def add_articulated_system(self, name: str, articulated_system: SingleArticulation) -> None:
        """Register a ``SingleArticulation`` (or subclass) object

        Args:
            name (str): object name
            articulated_system (SingleArticulation): object
        """
        self._articulated_systems[name] = articulated_system
        return

    def add_articulated_view(self, name: str, articulated_view: Articulation) -> None:
        """Register a ``Articulation`` (or subclass) object

        Args:
            name (str): object name
            articulated_view (Articulation): object
        """
        self._articulated_views[name] = articulated_view
        return

    def add_geometry_object(self, name: str, geometry_object: SingleGeometryPrim) -> None:
        """Register a ``SingleGeometryPrim`` (or subclass) object

        Args:
            name (str): object name
            geometry_object (SingleGeometryPrim): object
        """
        self._geometry_objects[name] = geometry_object
        return

    def add_geometry_prim_view(self, name: str, geometry_prim_view: GeometryPrim) -> None:
        """Register a ``GeometryPrim`` (or subclass) object

        Args:
            name (str): object name
            geometry_prim_view (GeometryPrim): object
        """
        self._geometry_prim_views[name] = geometry_prim_view
        return

    def add_robot(self, name: str, robot: Robot) -> None:
        """Register a ``Robot`` (or subclass) object

        Args:
            name (str): object name
            robot (Robot): object
        """
        self._robots[name] = robot
        return

    def add_robot_view(self, name: str, robot_view: RobotView) -> None:
        """Register a ``RobotView`` (or subclass) object

        Args:
            name (str): object name
            robot_view (RobotView): object
        """
        self._robot_views[name] = robot_view
        return

    def add_xform_view(self, name: str, xform_prim_view: XFormPrim) -> None:
        """Register a ``XFormPrim`` (or subclass) object

        Args:
            name (str): object name
            xform_prim_view (XFormPrim): object
        """
        self._xform_prim_views[name] = xform_prim_view
        return

    def add_deformable(self, name: str, deformable: SingleDeformablePrim) -> None:
        """Register a ``SingleDeformablePrim`` (or subclass) object

        Args:
            name (str): object name
            deformable (SingleDeformablePrim): object
        """
        self._deformable_prims[name] = deformable
        return

    def add_deformable_view(self, name: str, deformable_prim_view: DeformablePrim) -> None:
        """Register a ``DeformablePrim`` (or subclass) object

        Args:
            name (str): object name
            deformable_prim_view (DeformablePrim): object
        """
        self._deformable_prim_views[name] = deformable_prim_view
        return

    def add_deformable_material(self, name: str, deformable_material: DeformableMaterial) -> None:
        """Register a ``DeformableMaterial`` (or subclass) object

        Args:
            name (str): object name
            deformable_material (DeformableMaterial): object
        """
        self._deformable_materials[name] = deformable_material
        return

    def add_deformable_material_view(self, name: str, deformable_material_view: DeformableMaterialView) -> None:
        """Register a ``DeformableMaterialView`` (or subclass) object

        Args:
            name (str): object name
            deformable_material_view (DeformableMaterialView): object
        """
        self._deformable_material_views[name] = deformable_material_view
        return

    def add_cloth(self, name: str, cloth: SingleClothPrim) -> None:
        """Register a ``SingleClothPrim`` (or subclass) object

        Args:
            name (str): object name
            cloth (SingleClothPrim): object
        """
        self._cloth_prims[name] = cloth
        return

    def add_cloth_view(self, name: str, cloth_prim_view: ClothPrim) -> None:
        """Register a ``ClothPrim`` (or subclass) object

        Args:
            name (str): object name
            cloth_prim_view (ClothPrim): object
        """
        self._cloth_prim_views[name] = cloth_prim_view
        return

    def add_particle_system(self, name: str, particle_system: SingleParticleSystem) -> None:
        """Register a ``SingleParticleSystem`` (or subclass) object

        Args:
            name (str): object name
            particle_system (ParticleSystem): object
        """
        self._particle_systems[name] = particle_system
        return

    def add_particle_system_view(self, name: str, particle_system_view: ParticleSystem) -> None:
        """Register a ``ParticleSystem`` (or subclass) object

        Args:
            name (str): object name
            particle_system_view (ParticleSystem): object
        """
        self._particle_system_views[name] = particle_system_view
        return

    def add_particle_material(self, name: str, particle_material: ParticleMaterial) -> None:
        """Register a ``ParticleMaterial`` (or subclass) object

        Args:
            name (str): object name
            particle_material (ParticleMaterial): object
        """
        self._particle_materials[name] = particle_material
        return

    def add_particle_material_view(self, name: str, particle_material_view: ParticleMaterialView) -> None:
        """Register a ``ParticleMaterialView`` (or subclass) object

        Args:
            name (str): object name
            particle_material_view (ParticleMaterialView): object
        """
        self._particle_material_views[name] = particle_material_view
        return

    def add_xform(self, name: str, xform: SingleXFormPrim) -> None:
        """Register a ``SingleXFormPrim`` (or subclass) object

        Args:
            name (str): object name
            robot (Robot): object
        """
        self._xforms[name] = xform
        return

    def add_sensor(self, name: str, sensor: BaseSensor) -> None:
        """Register a ``BaseSensor`` (or subclass) object

        Args:
            name (str): object name
            sensor (BaseSensor): object
        """
        self._sensors[name] = sensor

        return

    def name_exists(self, name: str) -> bool:
        """Check if an object exists in the registry by its name

        Args:
            name (str): object name

        Returns:
            bool: whether the object is registered or not

        Example:

        .. code-block:: python

            >>> # given a registered ground plane named 'default_ground_plane'
            >>> scene_registry.name_exists("default_ground_plane")
            True
        """
        for object_dict in self._all_object_dicts:
            if name in object_dict:
                return True
        return False

    def remove_object(self, name: str) -> None:
        """Remove and object from the registry

        .. note::

            This method will only remove the object from the internal registry.
            The wrapped object will not be removed from the USD stage

        Args:
            name (str): object name

        Raises:
            Exception: If the name doesn't exist in the registry

        Example:

        .. code-block:: python

            >>> # given a registered ground plane named 'default_ground_plane'
            >>> scene_registry.remove_object("default_ground_plane")
        """
        for object_dict in self._all_object_dicts:
            if name in object_dict:
                del object_dict[name]
                return
        raise Exception("Cannot remove object {} from the scene since it doesn't exist".format(name))

    def get_object(self, name: str) -> SingleXFormPrim:
        """Get a registered object by its name if exists otherwise None

        Args:
            name (str): object name

        Returns:
            SingleXFormPrim: the object if it exists otherwise None

        Example:

        .. code-block:: python

            >>> # given a registered ground plane named 'default_ground_plane'
            >>> scene_registry.get_object("default_ground_plane")
            <isaacsim.core.api.objects.ground_plane.GroundPlane object at 0x...>
        """
        for object_dict in self._all_object_dicts:
            if name in object_dict:
                return object_dict[name]
        return None
