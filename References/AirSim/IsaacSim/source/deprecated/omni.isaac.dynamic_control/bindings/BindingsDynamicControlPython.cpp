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

// clang-format off
#include <pch/UsdPCH.h>
// clang-format on

#include <carb/BindingsUtils.h>

#include <omni/isaac/dynamic_control/DynamicControl.h>
#include <omni/isaac/dynamic_control/Math.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#ifdef _WIN32
typedef SSIZE_T ssize_t;
#endif

CARB_BINDINGS("omni.isaac.dynamic_control.python")

namespace omni
{
namespace isaac
{
namespace dynamic_control
{

}
}
}

namespace
{

namespace py = pybind11;

template <typename InterfaceType>
py::class_<InterfaceType> defineInterfaceClass(py::module& m,
                                               const char* className,
                                               const char* acquireFuncName,
                                               const char* releaseFuncName = nullptr,
                                               const char* docString = "")
{
    m.def(
        acquireFuncName,
        [](const char* pluginName, const char* libraryPath)
        {
            return libraryPath ? carb::acquireInterfaceFromLibraryForBindings<InterfaceType>(libraryPath) :
                                 carb::acquireInterfaceForBindings<InterfaceType>(pluginName);
        },
        py::arg("plugin_name") = nullptr, py::arg("library_path") = nullptr, py::return_value_policy::reference,
        "Acquire dynamic control interface. This is the base object that all of the dynamic control functions are defined on");

    if (releaseFuncName)
    {
        m.def(
            releaseFuncName, [](InterfaceType* iface) { carb::getFramework()->releaseInterface(iface); },
            "Release dynamic control interface. Generally this does not need to be called, the dynamic control interface is released on extension shutdown");
    }

    return py::class_<InterfaceType>(m, className, docString);
}

PYBIND11_MODULE(_dynamic_control, m)
{
    using namespace carb;
    using namespace omni::isaac::dynamic_control;

    // We use carb data types, must import bindings for them
    auto carb_module = py::module::import("carb");
    auto numpy_common_module = py::module::import("omni.kit.numpy.common");

    m.doc() =
        R"pbdoc(
        The Dynamic Control extension provides a set of utilities to control physics objects. 
        It provides opaque handles for different physics objects that remain valid between PhysX scene resets, which occur whenever play or stop is pressed.
        
        Attributes:
            INVALID_HANDLE: This value is returned when trying to acquire a dynamic control handle for an invalid usd path

        The following attributes correspond to states that can be get/set from Degrees of Freedom and Rigid Bodies  
        
        Attributes:
            STATE_NONE: No state selected
            STATE_POS: Position states
            STATE_VEL: Velocity states
            STATE_EFFORT: Force/Torque states
            STATE_ALL: All states
        
        The following attributes correspond to joint axes when specifying a 6 Dof (D6) Joint
        
        Attributes:
            AXIS_NONE: No axis selected
            AXIS_X: Corresponds to translation around the body x-axis
            AXIS_Y: Corresponds to translation around the body y-axis
            AXIS_Z: Corresponds to translation around the body z-axis
            AXIS_TWIST: Corresponds to rotation around the body x-axis
            AXIS_SWING_1: Corresponds to rotation around the body y-axis
            AXIS_SWING_2: Corresponds to rotation around the body z-axis
            AXIS_ALL_TRANSLATION: Corresponds to all Translation axes
            AXIS_ALL_ROTATION: Corresponds to all Rotation axes
            AXIS_ALL: Corresponds to all axes
        )pbdoc";

    m.attr("INVALID_HANDLE") = py::int_(kDcInvalidHandle);

    // state flags
    m.attr("STATE_NONE") = py::int_(kDcStateNone);
    m.attr("STATE_POS") = py::int_(kDcStatePos);
    m.attr("STATE_VEL") = py::int_(kDcStateVel);
    m.attr("STATE_EFFORT") = py::int_(kDcStateEffort);
    m.attr("STATE_ALL") = py::int_(kDcStateAll);

    // axis flags
    m.attr("AXIS_NONE") = py::int_(kDcAxisNone);
    m.attr("AXIS_X") = py::int_(kDcAxisX);
    m.attr("AXIS_Y") = py::int_(kDcAxisY);
    m.attr("AXIS_Z") = py::int_(kDcAxisZ);
    m.attr("AXIS_TWIST") = py::int_(kDcAxisTwist);
    m.attr("AXIS_SWING_1") = py::int_(kDcAxisSwing1);
    m.attr("AXIS_SWING_2") = py::int_(kDcAxisSwing2);
    m.attr("AXIS_ALL_TRANSLATION") = py::int_(kDcAxisAllTranslation);
    m.attr("AXIS_ALL_ROTATION") = py::int_(kDcAxisAllRotation);
    m.attr("AXIS_ALL") = py::int_(kDcAxisAll);

    py::enum_<DcJointType>(m, "JointType", py::arithmetic(), "Joint Types that can be specified")
        .value("JOINT_NONE", DcJointType::eNone, "invalid/unknown/uninitialized joint type")
        .value("JOINT_FIXED", DcJointType::eFixed, "Fixed Joint")
        .value("JOINT_REVOLUTE", DcJointType::eRevolute, "Revolute Joint")
        .value("JOINT_PRISMATIC", DcJointType::ePrismatic, "Prismatic Joint")
        .value("JOINT_SPHERICAL", DcJointType::eSpherical, "Spherical Joint")
        .export_values();

    py::enum_<DcDofType>(m, "DofType", py::arithmetic(), "Types of degree of freedom")
        .value("DOF_NONE", DcDofType::eNone, "invalid/unknown/uninitialized DOF type")
        .value("DOF_ROTATION", DcDofType::eRotation, "The degrees of freedom correspond to a rotation between bodies")
        .value("DOF_TRANSLATION", DcDofType::eTranslation,
               "The degrees of freedom correspond to a translation between bodies.")
        .export_values();

    py::enum_<DcDriveMode>(m, "DriveMode", py::arithmetic(), "DOF drive mode")
        .value("DRIVE_FORCE", DcDriveMode::eForce, "Use Force Based Drive Controller")
        .value("DRIVE_ACCELERATION", DcDriveMode::eAcceleration, "Use Acceleration Based Drive Controller")
        .export_values();

    py::enum_<DcObjectType>(m, "ObjectType", py::arithmetic(), "Types of Objects")
        .value("OBJECT_NONE", DcObjectType::eDcObjectNone, "Invalid/unknown/uninitialized object type")
        .value("OBJECT_RIGIDBODY", DcObjectType::eDcObjectRigidBody,
               "The object is a rigid body or a link on an articulation")
        .value("OBJECT_JOINT", DcObjectType::eDcObjectJoint, "The object is a joint")
        .value("OBJECT_DOF", DcObjectType::eDcObjectDof, "The object is a degree of freedon")
        .value("OBJECT_ARTICULATION", DcObjectType::eDcObjectArticulation, "The object is an articulation")
        .value("OBJECT_ATTRACTOR", DcObjectType::eDcObjectAttractor, "The object is an attractor")
        .value("OBJECT_D6JOINT", DcObjectType::eDcObjectD6Joint, "The object is a generic D6 joint")
        .export_values();

    py::class_<DcTransform>(m, "Transform", "Represents a 3D transform in the system")
        .def_readwrite("p", &DcTransform::p, "Position as a tuple of (x,y,z) (:obj:`carb._carb.Float3`)")
        .def_readwrite(
            "r", &DcTransform::r,
            R"pbdoc(Rotation Quaternion, represented in the format :math:`x\hat{i} + y\hat{j} + z\hat{k} + w` (:obj:`carb._carb.Float4`))pbdoc")
        .def(py::init(
                 [](const carb::Float3& p, const carb::Float4& r)
                 {
                     DcTransform transform;
                     transform.p = p;
                     transform.r = r;
                     return transform;
                 }),
             py::arg("p") = nullptr, py::arg("r") = nullptr, "Initialize from a position and a rotation quaternion")
        .def(py::init<>(), "Initialize from another Transform object")
        .def_property_readonly_static(
            "dtype", [](const py::object&) { return py::dtype::of<DcTransform>(); }, "return the numpy structured dtype")
        .def_static(
            "from_buffer",
            [](py::buffer buf) -> py::object
            {
                py::buffer_info info = buf.request();
                if (info.ptr != nullptr)
                {
                    if ((info.itemsize == 7 * sizeof(float)) ||
                        (info.itemsize == sizeof(float) && info.ndim > 0 && info.shape[info.ndim - 1] >= 7))
                    {
                        float* data = (float*)info.ptr;
                        DcTransform tx;
                        tx.p = carb::Float3{ data[0], data[1], data[2] };
                        tx.r = carb::Float4{ data[3], data[4], data[5], data[6] };
                        return py::cast(tx);
                    }
                }
                return py::none();
            },
            "assign a transform from an array of 7 values [p.x, p.y, p.z, r.x, r.y, r.z, r.w]")

        .def(py::pickle([](const DcTransform& tx)
                        { return py::make_tuple(tx.p.x, tx.p.y, tx.p.z, tx.r.x, tx.r.y, tx.r.z, tx.r.w); },
                        [](py::tuple t)
                        {
                            DcTransform tx;
                            tx.p = { t[0].cast<float>(), t[1].cast<float>(), t[2].cast<float>() };
                            tx.r = { t[3].cast<float>(), t[4].cast<float>(), t[5].cast<float>(), t[6].cast<float>() };
                            return tx;
                        }))
        .def("__repr__",
             [](const DcTransform& tx) {
                 return fmt::format(
                     "({}, {}, {}), ({}, {}, {}, {})", tx.p.x, tx.p.y, tx.p.z, tx.r.x, tx.r.y, tx.r.z, tx.r.w);
             })
        .def("__eq__",
             [](const DcTransform& a, const DcTransform& b)
             {
                 return a.p.x == b.p.x && a.p.y == b.p.y && a.p.z == b.p.z && a.r.x == b.r.x && a.r.y == b.r.y &&
                        a.r.z == b.r.z && a.r.w == b.r.w;
             });

    py::class_<DcVelocity>(m, "Velocity", "Linear and angular velocity")
        .def_readwrite("linear", &DcVelocity::linear, "Linear 3D velocity as a tuple (x,y,z) , (:obj:`carb._carb.Float3`)")
        .def_readwrite(
            "angular", &DcVelocity::angular, "Angular 3D velocity as a tuple (x,y,z), (:obj:`carb._carb.Float3`)")
        .def(py::init(
                 [](const carb::Float3& linear, const carb::Float3& angular)
                 {
                     DcVelocity vel;
                     vel.linear = linear;
                     vel.angular = angular;
                     return vel;
                 }),
             py::arg("linear") = nullptr, py::arg("angular") = nullptr,
             "initialize from a linear velocity and angular velocity")
        .def(py::init<>(), "initialize from another Velocity Object")
        .def_property_readonly_static(
            "dtype",
            [](const py::object&)
            {
                // return the numpy structured dtype
                return py::dtype::of<DcVelocity>();
            },
            "return the numpy structured dtype")
        .def(py::pickle(
            [](const DcVelocity& v)
            { return py::make_tuple(v.linear.x, v.linear.y, v.linear.z, v.angular.x, v.angular.y, v.angular.z); },
            [](py::tuple t)
            {
                DcVelocity v;
                v.linear = { t[0].cast<float>(), t[1].cast<float>(), t[2].cast<float>() };
                v.angular = { t[3].cast<float>(), t[4].cast<float>(), t[5].cast<float>() };
                return v;
            }))
        .def("__repr__",
             [](const DcVelocity& v)
             {
                 return fmt::format("({}, {}, {}), ({}, {}, {})", v.linear.x, v.linear.y, v.linear.z, v.angular.x,
                                    v.angular.y, v.angular.z);
             });


    py::class_<DcRigidBodyState>(m, "RigidBodyState", "Containing states to get/set for a rigid body in the simulation")
        .def_readwrite(
            "pose", &DcRigidBodyState::pose,
            "Transform with position and orientation of rigid body (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`)")
        .def_readwrite(
            "vel", &DcRigidBodyState::vel,
            "Linear and angular velocities of rigid body (:obj:`omni.isaac.dynamic_control._dynamic_control.Velocity`)")
        .def(py::init(
                 [](const DcTransform& pose, const DcVelocity& vel)
                 {
                     DcRigidBodyState state;
                     state.pose = pose;
                     state.vel = vel;
                     return state;
                 }),
             py::arg("pose") = nullptr, py::arg("vel") = nullptr, "Initialize rigid body state from pose and velocity")
        .def(py::init<>(), "initialize from another RigidBodyState")
        .def_property_readonly_static(
            "dtype", [](const py::object&) { return py::dtype::of<DcRigidBodyState>(); },
            "return the numpy structured dtype")
        .def(py::pickle(
            [](const DcRigidBodyState& s)
            {
                return py::make_tuple(s.pose.p.x, s.pose.p.y, s.pose.p.z, s.pose.r.x, s.pose.r.y, s.pose.r.z,
                                      s.pose.r.w, s.vel.linear.x, s.vel.linear.y, s.vel.linear.z, s.vel.angular.x,
                                      s.vel.angular.y, s.vel.angular.z);
            },
            [](py::tuple t)
            {
                DcRigidBodyState s;
                s.pose.p = { t[0].cast<float>(), t[1].cast<float>(), t[2].cast<float>() };
                s.pose.r = { t[3].cast<float>(), t[4].cast<float>(), t[5].cast<float>(), t[6].cast<float>() };
                s.vel.linear = { t[7].cast<float>(), t[8].cast<float>(), t[9].cast<float>() };
                s.vel.angular = { t[10].cast<float>(), t[11].cast<float>(), t[12].cast<float>() };
                return s;
            }))
        .def("__repr__",
             [](const DcRigidBodyState& s)
             {
                 return fmt::format("({}, {}, {}), ({}, {}, {}, {}), ({}, {}, {}), ({}, {}, {})", s.pose.p.x, s.pose.p.y,
                                    s.pose.p.z, s.pose.r.x, s.pose.r.y, s.pose.r.z, s.pose.r.w, s.vel.linear.x,
                                    s.vel.linear.y, s.vel.linear.z, s.vel.angular.x, s.vel.angular.y, s.vel.angular.z);
             });

    py::class_<DcDofState>(m, "DofState", "States of a Degree of Freedom in the Asset architecture")
        .def_readwrite(
            "pos", &DcDofState::pos,
            "DOF position, in radians if it's a revolute DOF, or stage_units (m, cm, etc), if it's a prismatic DOF (:obj:`float`)")
        .def_readwrite(
            "vel", &DcDofState::vel,
            "DOF velocity, in radians/s if it's a revolute DOF, or stage_units/s (m/s, cm/s, etc), if it's a prismatic DOF (:obj:`float`)")
        .def_readwrite(
            "effort", &DcDofState::effort,
            "DOF effort due to gravity, torque if it's a revolute DOF, or force if it's a prismatic DOF (:obj:`float`)")
        .def(py::init(
                 [](const float& pos, const float& vel, const float& effort)
                 {
                     DcDofState state;
                     state.pos = pos;
                     state.vel = vel;
                     state.effort = effort;
                     return state;
                 }),
             py::arg("pos") = nullptr, py::arg("vel") = nullptr, py::arg("effort") = nullptr)
        .def(py::init<>())
        .def_property_readonly_static(
            "dtype", [](const py::object&) { return py::dtype::of<DcDofState>(); }, "return the numpy structured dtype")
        .def(py::pickle([](const DcDofState& s) { return py::make_tuple(s.pos, s.vel, s.effort); },
                        [](py::tuple t) {
                            return DcDofState{ t[0].cast<float>(), t[1].cast<float>(), t[2].cast<float>() };
                        }))
        .def("__repr__",
             [](const DcDofState& state) { return fmt::format("({}, {}, {})", state.pos, state.vel, state.effort); });

    py::class_<DcArticulationProperties>(m, "ArticulationProperties", "Articulation Properties")
        .def(py::init<>())
        .def_readwrite("solver_position_iteration_count", &DcArticulationProperties::solverPositionIterationCount,
                       "Position solver iterations (:obj:`int`)")
        .def_readwrite("solver_velocity_iteration_count", &DcArticulationProperties::solverVelocityIterationCount,
                       "Velocity solver iterations (:obj:`int`)")
        .def_readwrite("enable_self_collisions", &DcArticulationProperties::enableSelfCollisions,
                       "Allow links in articulation to collide with each other (:obj:`bool`)")

        .def(py::pickle(
            [](const DcArticulationProperties& props)
            {
                return py::make_tuple(
                    props.solverPositionIterationCount, props.solverVelocityIterationCount, props.enableSelfCollisions);
            },
            [](py::tuple t)
            {
                DcArticulationProperties props;
                props.solverPositionIterationCount = t[0].cast<uint32_t>();
                props.solverVelocityIterationCount = t[1].cast<uint32_t>();
                props.enableSelfCollisions = t[2].cast<bool>();
                return props;
            }));
    // .def("__repr__",
    //      [](const DcArticulationProperties& p)
    //      {
    //          return fmt::format("({}, {}, {})", p.solverPositionIterationCount, p.solverVelocityIterationCount,
    //                             p.enableSelfCollisions);
    //      });

    py::class_<DcRigidBodyProperties>(m, "RigidBodyProperties", "Rigid Body Properties")
        .def(py::init<>())
        .def_readwrite("mass", &DcRigidBodyProperties::mass, "Mass of rigid body (:obj:`float`)")
        .def_readwrite("cMassLocalPose", &DcRigidBodyProperties::cMassLocalPose,
                       "Local center of mass position (:obj:`carb._carb.Float3`)")
        .def_readwrite("moment", &DcRigidBodyProperties::moment, "Diagonal moment of inertia (:obj:`carb._carb.Float3`)")
        .def_readwrite(
            "max_depeneration_velocity", &DcRigidBodyProperties::maxDepenetrationVelocity,
            "This value controls how much velocity the solver can introduce to correct for penetrations in contacts. (:obj:`float`)")
        .def_readwrite("max_contact_impulse", &DcRigidBodyProperties::maxContactImpulse,
                       "Sets a limit on the impulse that may be applied at a contact. (:obj:`float`)")
        .def_readwrite("solver_position_iteration_count", &DcRigidBodyProperties::solverPositionIterationCount,
                       "Position solver iterations (:obj:`int`)")
        .def_readwrite("solver_velocity_iteration_count", &DcRigidBodyProperties::solverVelocityIterationCount,
                       "Velocity solver iterations (:obj:`int`)")

        .def(py::pickle(
            [](const DcRigidBodyProperties& props)
            {
                return py::make_tuple(props.mass, props.cMassLocalPose.x, props.cMassLocalPose.y,
                                      props.cMassLocalPose.z, props.moment.x, props.moment.y, props.moment.z,
                                      props.maxDepenetrationVelocity, props.maxContactImpulse,
                                      props.solverPositionIterationCount, props.solverVelocityIterationCount);
            },
            [](py::tuple t)
            {
                DcRigidBodyProperties props;
                props.mass = t[0].cast<float>();
                props.cMassLocalPose = { t[1].cast<float>(), t[2].cast<float>(), t[3].cast<float>() };
                props.moment = { t[4].cast<float>(), t[5].cast<float>(), t[6].cast<float>() };
                props.maxDepenetrationVelocity = t[7].cast<float>();
                props.maxContactImpulse = t[8].cast<float>();
                props.solverPositionIterationCount = t[9].cast<uint32_t>();
                props.solverVelocityIterationCount = t[10].cast<uint32_t>();

                return props;
            }));
    // .def("__repr__",
    //      [](const DcRigidBodyProperties& p)
    //      {
    //          return fmt::format("({}, ({}, {}, {}), {}, {}, {}, {})", p.mass, p.moment.x, p.moment.y, p.moment.z,
    //                             p.maxDepenetrationVelocity, p.maxContactImpulse, p.solverPositionIterationCount,
    //                             p.solverVelocityIterationCount);
    //      });


    py::class_<DcDofProperties>(m, "DofProperties", "Properties of a degree-of-freedom (DOF)")
        .def(py::init<>())
        .def_readwrite("type", &DcDofProperties::type,
                       R"pbdoc(
                           Type of joint (read only) (:obj:`omni.isaac.dynamic_control._dynamic_control.DofType`))pbdoc")
        .def_readwrite(
            "has_limits", &DcDofProperties::hasLimits, "Flags whether the DOF has limits (read only) (:obj:`bool`)")
        .def_readwrite(
            "lower", &DcDofProperties::lower, "lower limit of DOF. In radians or meters (read only) (:obj:`float`)")
        .def_readwrite(
            "upper", &DcDofProperties::upper, "upper limit of DOF. In radians or meters (read only) (:obj:`float`)")
        .def_readwrite("drive_mode", &DcDofProperties::driveMode,
                       "Drive mode for the DOF (:obj:`omni.isaac.dynamic_control._dynamic_control.DriveMode`)")
        .def_readwrite("max_velocity", &DcDofProperties::maxVelocity,
                       "Maximum velocity of DOF. In Radians/s, or stage_units/s (:obj:`float`)")
        .def_readwrite(
            "max_effort", &DcDofProperties::maxEffort, "Maximum effort of DOF. in N or N*stage_units (:obj:`float`)")
        .def_readwrite("stiffness", &DcDofProperties::stiffness, "Stiffness of DOF (:obj:`float`)")
        .def_readwrite("damping", &DcDofProperties::damping, "Damping of DOF (:obj:`float`)")
        .def(py::pickle(
            [](const DcDofProperties& props)
            {
                return py::make_tuple(props.type, props.hasLimits, props.lower, props.upper, props.driveMode,
                                      props.maxVelocity, props.maxEffort, props.stiffness, props.damping);
            },
            [](py::tuple t)
            {
                DcDofProperties props;
                props.type = t[0].cast<DcDofType>();
                props.hasLimits = t[1].cast<bool>();
                props.lower = t[2].cast<float>();
                props.upper = t[3].cast<float>();
                props.driveMode = t[4].cast<DcDriveMode>();
                props.maxVelocity = t[5].cast<float>();
                props.maxEffort = t[6].cast<float>();
                props.stiffness = t[7].cast<float>();
                props.damping = t[8].cast<float>();
                return props;
            }));

    py::class_<DcAttractorProperties>(
        m, "AttractorProperties",
        "The Attractor is used to pull a rigid body towards a pose. Each pose axis can be individually selected.")
        .def(py::init<>())
        .def_readwrite("body", &DcAttractorProperties::rigidBody, "Rigid body to set the attractor to")
        .def_readwrite(
            "axes", &DcAttractorProperties::axes,
            "Axes to set the attractor, using DcAxisFlags. Multiple axes can be selected using bitwise combination of each axis flag. if axis flag is set to zero, the attractor will be disabled and won't impact in solver computational complexity.")
        .def_readwrite("target", &DcAttractorProperties::target,
                       "Target pose to attract to. (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`)")
        .def_readwrite(
            "offset", &DcAttractorProperties::offset,
            "Offset from rigid body origin to set the attractor pose. (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`)")
        .def_readwrite(
            "stiffness", &DcAttractorProperties::stiffness,
            "Stiffness to be used on attraction for solver. Stiffness value should be larger than the largest agent kinematic chain stifness (:obj:`float`)")
        .def_readwrite(
            "damping", &DcAttractorProperties::damping, "Damping to be used on attraction solver. (:obj:`float`)")
        .def_readwrite(
            "force_limit", &DcAttractorProperties::forceLimit, "Maximum force to be applied by drive. (:obj:`float`)")
        .def(py::pickle(
            [](const DcAttractorProperties& props)
            {
                return py::make_tuple(props.rigidBody, props.axes, props.target.p.x, props.target.p.y, props.target.p.z,
                                      props.target.r.x, props.target.r.y, props.target.r.z, props.target.r.w,
                                      props.offset.p.x, props.offset.p.y, props.offset.p.z, props.offset.r.x,
                                      props.offset.r.y, props.offset.r.z, props.offset.r.w, props.stiffness,
                                      props.damping, props.forceLimit);
            },
            [](py::tuple t)
            {
                DcAttractorProperties props;
                props.rigidBody = t[0].cast<DcHandle>();
                props.axes = t[1].cast<DcAxisFlags>();
                props.target.p = { t[2].cast<float>(), t[3].cast<float>(), t[4].cast<float>() };
                props.target.r = { t[5].cast<float>(), t[6].cast<float>(), t[7].cast<float>(), t[8].cast<float>() };
                props.offset.p = { t[9].cast<float>(), t[10].cast<float>(), t[11].cast<float>() };
                props.offset.r = { t[12].cast<float>(), t[13].cast<float>(), t[14].cast<float>(), t[15].cast<float>() };
                props.stiffness = t[16].cast<float>();
                props.damping = t[17].cast<float>();
                props.forceLimit = t[18].cast<float>();
                return props;
            }));


    py::class_<DcD6JointProperties>(m, "D6JointProperties", "Creates  a general D6 Joint between two rigid Bodies.")
        .def(py::init<>())
        .def_readwrite("name", &DcD6JointProperties::name, "Joint Name (:obj:`str`)")
        .def_readwrite("body0", &DcD6JointProperties::body0, "parent body")
        .def_readwrite("body1", &DcD6JointProperties::body1, "child body")
        .def_readwrite(
            "axes", &DcD6JointProperties::axes,
            "Axes to set the attractor, using DcAxisFlags. Multiple axes can be selected using bitwise combination of each axis flag. if axis flag is set to zero, the attractor will be disabled and won't impact in solver computational complexity.")
        .def_readwrite("pose0", &DcD6JointProperties::pose0,
                       "Transform from body 0 to joint. (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`)")
        .def_readwrite("pose1", &DcD6JointProperties::pose1,
                       "Transform from body 1 to joint. (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`)")
        .def_readwrite(
            "stiffness", &DcD6JointProperties::stiffness,
            "Joint Stiffness. Stiffness value should be larger than the largest agent kinematic chain stifness (:obj:`float`)")
        .def_readwrite("damping", &DcD6JointProperties::damping, "Joint Damping. (:obj:`float`)")
        .def_readwrite("force_limit", &DcD6JointProperties::forceLimit, "Joint Breaking Force. (:obj:`float`)")
        .def_readwrite("torque_limit", &DcD6JointProperties::torqueLimit, "Joint Breaking torque. (:obj:`float`)")
        .def(py::pickle(
            [](const DcD6JointProperties& props)
            {
                return py::make_tuple(props.name, props.body0, props.body1, props.axes, props.pose0.p.x, props.pose0.p.y,
                                      props.pose0.p.z, props.pose0.r.x, props.pose0.r.y, props.pose0.r.z,
                                      props.pose0.r.w, props.pose1.p.x, props.pose1.p.y, props.pose1.p.z,
                                      props.pose1.r.x, props.pose1.r.y, props.pose1.r.z, props.pose1.r.w,
                                      props.stiffness, props.damping, props.forceLimit, props.torqueLimit);
            },
            [](py::tuple t)
            {
                DcD6JointProperties props;
                std::string str = t[0].cast<std::string>().c_str();
                std::vector<char> cstr(str.c_str(), str.c_str() + str.size() + 1);
                props.name = cstr.data();
                props.body0 = t[1].cast<DcHandle>();
                props.body1 = t[2].cast<DcHandle>();
                props.axes = t[3].cast<DcAxisFlags>();
                props.pose0.p = { t[4].cast<float>(), t[5].cast<float>(), t[6].cast<float>() };
                props.pose0.r = { t[7].cast<float>(), t[8].cast<float>(), t[9].cast<float>(), t[10].cast<float>() };
                props.pose1.p = { t[11].cast<float>(), t[12].cast<float>(), t[13].cast<float>() };
                props.pose1.r = { t[14].cast<float>(), t[15].cast<float>(), t[16].cast<float>(), t[17].cast<float>() };
                props.stiffness = t[18].cast<float>();
                props.damping = t[19].cast<float>();
                props.forceLimit = t[20].cast<float>();
                props.torqueLimit = t[21].cast<float>();
                return props;
            }));

    // numpy dtypes
    PYBIND11_NUMPY_DTYPE(DcTransform, p, r);
    PYBIND11_NUMPY_DTYPE(DcVelocity, linear, angular);
    PYBIND11_NUMPY_DTYPE(DcRigidBodyState, pose, vel);
    PYBIND11_NUMPY_DTYPE(DcDofState, pos, vel, effort);
    PYBIND11_NUMPY_DTYPE(
        DcArticulationProperties, solverPositionIterationCount, solverVelocityIterationCount, enableSelfCollisions);
    PYBIND11_NUMPY_DTYPE(DcRigidBodyProperties, mass, moment, maxDepenetrationVelocity, maxContactImpulse,
                         solverPositionIterationCount, solverVelocityIterationCount);

    PYBIND11_NUMPY_DTYPE(
        DcDofProperties, type, hasLimits, lower, upper, driveMode, maxVelocity, maxEffort, stiffness, damping);


    defineInterfaceClass<DynamicControl>(m, "DynamicControl", "acquire_dynamic_control_interface",
                                         "release_dynamic_control_interface",
                                         "The following functions are provided on the dynamic control interface")

        //.def("create_context", wrapInterfaceFunction(&DynamicControl::createContext),
        // py::return_value_policy::reference) .def("destroy_context",
        // wrapInterfaceFunction(&DynamicControl::destroyContext)) .def("update_context",
        // wrapInterfaceFunction(&DynamicControl::updateContext))
        .def("is_simulating", wrapInterfaceFunction(&DynamicControl::isSimulating), R"pbdoc(
            Returns:
                bool: True if simulating, False otherwise)pbdoc")
        .def("get_rigid_body", wrapInterfaceFunction(&DynamicControl::getRigidBody), R"pbdoc(
            Returns:
                handle: Handle to the rigid body, INVALID_HANDLE otherwise)pbdoc")
        .def("get_joint", wrapInterfaceFunction(&DynamicControl::getJoint), R"pbdoc(
            Returns:
                handle: Handle to the joint, INVALID_HANDLE otherwise)pbdoc")
        .def("get_dof", wrapInterfaceFunction(&DynamicControl::getDof), R"pbdoc(
            Returns:
                handle: Handle to the degree of freedom, INVALID_HANDLE otherwise
        )pbdoc")
        .def("get_articulation", wrapInterfaceFunction(&DynamicControl::getArticulation), R"pbdoc(
            Returns:
                handle: Handle to the articulation, INVALID_HANDLE otherwise
        )pbdoc")
        .def("get_d6_joint", wrapInterfaceFunction(&DynamicControl::getD6Joint), R"pbdoc(
            Returns:
                handle: Handle to the d6 joint, INVALID_HANDLE otherwise
        )pbdoc")

        .def("get_object", wrapInterfaceFunction(&DynamicControl::getObject), R"pbdoc(
            Returns:
                handle: Handle to the physics object defined by the usd path, INVALID_HANDLE otherwise
        )pbdoc")
        .def("get_object_type", wrapInterfaceFunction(&DynamicControl::getObjectType), R"pbdoc(\
            Returns:
                :obj:`omni.isaac.dynamic_control._dynamic_control.ObjectType`: Type of object returned by get_object)pbdoc")
        .def("get_object_type_name", wrapInterfaceFunction(&DynamicControl::getObjectTypeName),
             py::return_value_policy::reference, R"pbdoc(
            Returns:
                string: The object type name as a string
             )pbdoc")
        .def("peek_object_type", wrapInterfaceFunction(&DynamicControl::peekObjectType), R"pbdoc(
            Returns:
                string: The object type name as a string
        )pbdoc")

        .def("wake_up_rigid_body", wrapInterfaceFunction(&DynamicControl::wakeUpRigidBody),
             R"pbdoc(Enable physics for a rigid body)pbdoc")
        .def("wake_up_articulation", wrapInterfaceFunction(&DynamicControl::wakeUpArticulation),
             R"pbdoc(Enable physics for a articulation)pbdoc")
        .def("sleep_rigid_body", wrapInterfaceFunction(&DynamicControl::sleepRigidBody),
             R"pbdoc(Put rigid body to sleep)pbdoc")
        .def("sleep_articulation", wrapInterfaceFunction(&DynamicControl::sleepArticulation),
             R"pbdoc(Put articulation to sleep)pbdoc")

        .def("get_articulation_name", wrapInterfaceFunction(&DynamicControl::getArticulationName),
             py::return_value_policy::reference, R"pbdoc(
                 Returns:
                    string: The name of the articulation
                    )pbdoc")
        .def("get_articulation_path", wrapInterfaceFunction(&DynamicControl::getArticulationPath),
             py::return_value_policy::reference, R"pbdoc(
                 Returns:
                    string: The path to the articulation
                    )pbdoc")

        .def("get_articulation_body_count", wrapInterfaceFunction(&DynamicControl::getArticulationBodyCount),
             "Gets number of rigid bodies for an actor")
        .def("get_articulation_body", wrapInterfaceFunction(&DynamicControl::getArticulationBody),
             "Gets actor rigid body given its index")
        .def("find_articulation_body", wrapInterfaceFunction(&DynamicControl::findArticulationBody),
             "Finds actor rigid body given its name")
        .def("find_articulation_body_index", wrapInterfaceFunction(&DynamicControl::findArticulationBodyIndex),
             "Find index in articulation body array, -1 on error")
        .def("get_articulation_root_body", wrapInterfaceFunction(&DynamicControl::getArticulationRootBody),
             "Get the root rigid body of an actor")

        .def(
            "get_articulation_body_states",
            [](const DynamicControl* dc, DcHandle artHandle, DcStateFlags flags) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numBodies = dc->getArticulationBodyCount(artHandle);
                    DcRigidBodyState* states = dc->getArticulationBodyStates(artHandle, flags);
                    if (numBodies > 0 && states != nullptr)
                    {
                        return py::array_t<DcRigidBodyState, py::array::c_style>(numBodies, states);
                    }
                }
                return py::none();
            },
            "Get array of an actor's rigid body states")

        // .def("set_articulation_body_states",
        //      [](const DynamicControl* dc, DcHandle artHandle,
        //         const py::array_t<DcRigidBodyState, py::array::c_style>& states, DcStateFlags flags) {
        //          if (dc && dc->isSimulating())
        //          {
        //              if (states.size() >= ssize_t(dc->getArticulationBodyCount(artHandle)))
        //              {
        //                  return dc->setArticulationBodyStates(artHandle, states.data(), flags);
        //              }
        //          }
        //          return false;
        //      },
        //      "Sets states for an actor's rigid bodies.")
        .def("get_articulation_properties", wrapInterfaceFunction(&DynamicControl::getArticulationProperties),
             "Get Properties for an articulation")
        .def(
            "get_articulation_properties",
            [](const DynamicControl* dc, DcHandle attHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    DcArticulationProperties props;
                    if (dc->getArticulationProperties(attHandle, &props))
                    {
                        return py::cast(props);
                    }
                }
                return py::none();
            },
            "Get Properties for an articulation")
        .def("set_articulation_properties", wrapInterfaceFunction(&DynamicControl::setArticulationProperties),
             "Sets properties for articulation")

        .def("get_articulation_joint_count", wrapInterfaceFunction(&DynamicControl::getArticulationJointCount),
             "Get the number of joints in an articulation")
        .def("get_articulation_joint", wrapInterfaceFunction(&DynamicControl::getArticulationJoint),
             "Gets the joint from an articulation given an index ")
        .def("find_articulation_joint", wrapInterfaceFunction(&DynamicControl::findArticulationJoint),
             "Get the joint from an atriculation given their name")

        .def("get_articulation_dof_count", wrapInterfaceFunction(&DynamicControl::getArticulationDofCount),
             "Gets number of degrees-of-freedom for an actor")
        .def("get_articulation_dof", wrapInterfaceFunction(&DynamicControl::getArticulationDof),
             py::return_value_policy::reference, "Gets actor degree-of-freedom given its index")
        .def("find_articulation_dof", wrapInterfaceFunction(&DynamicControl::findArticulationDof),
             py::return_value_policy::reference, "Finds actor degree-of-freedom given its name")
        .def("find_articulation_dof_index", wrapInterfaceFunction(&DynamicControl::findArticulationDofIndex),
             "get index in articulation DOF array, -1 on error")

        .def(
            "get_articulation_dof_properties",
            [](const DynamicControl* dc, DcHandle artHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numDofs = dc->getArticulationDofCount(artHandle);
                    if (numDofs > 0)
                    {
                        auto arr = py::array_t<DcDofProperties, py::array::c_style>(numDofs);
                        if (dc->getArticulationDofProperties(artHandle, arr.mutable_data()))
                        {
                            return arr;
                        }
                    }
                }
                return py::none();
            },
            "Get array of an actor's degree-of-freedom properties")

        .def(
            "set_articulation_dof_properties",
            [](const DynamicControl* dc, DcHandle artHandle, const py::array_t<DcDofProperties, py::array::c_style>& props)
            {
                if (dc && dc->isSimulating())
                {
                    if (props.size() >= ssize_t(dc->getArticulationDofCount(artHandle)))
                    {
                        return dc->setArticulationDofProperties(artHandle, props.data());
                    }
                }
                return false;
            },
            "Sets properties for an actor's degrees-of-freedom.")

        .def(
            "get_articulation_dof_states",
            [](const DynamicControl* dc, DcHandle artHandle, DcStateFlags flags) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numDofs = dc->getArticulationDofCount(artHandle);
                    if (numDofs > 0)
                    {
                        DcDofState* states = dc->getArticulationDofStates(artHandle, flags);
                        if (states != nullptr)
                        {
                            return py::array_t<DcDofState, py::array::c_style>(numDofs, states);
                        }
                    }
                }
                return py::none();
            },
            "Get array of an actor's degree-of-freedom states")

        // .def("get_articulation_dof_state_derivatives",
        //      [](const DynamicControl* dc, DcHandle artHandle, const py::array_t<DcDofState, py::array::c_style>&
        //      states,
        //         const py::array_t<float, py::array::c_style>& efforts) -> py::object
        //      {
        //          if (dc && dc->isSimulating())
        //          {
        //              const ssize_t numDofs{ static_cast<ssize_t>(dc->getArticulationDofCount(artHandle)) };
        //              // check input dims
        //              if (states.size() >= numDofs && efforts.size() >= numDofs)
        //              {
        //                  DcDofState* stateDeriv =
        //                      dc->getArticulationDofStateDerivatives(artHandle, states.data(), efforts.data());
        //                  if (stateDeriv != nullptr)
        //                  {
        //                      auto capsule = py::capsule(stateDeriv, [](void*) {}); // avoid copy
        //                      return py::array_t<DcDofState, py::array::c_style>(numDofs, stateDeriv, capsule);
        //                  }
        //              }
        //          }
        //          return py::none();
        //      },
        //      "Get array of an actor's degree-of-freedom state derivatives (dstate / dt)")

        .def(
            "set_articulation_dof_states",
            [](const DynamicControl* dc, DcHandle artHandle, const py::array_t<DcDofState, py::array::c_style>& states,
               DcStateFlags flags)
            {
                if (dc && dc->isSimulating())
                {
                    if (states.size() >= ssize_t(dc->getArticulationDofCount(artHandle)))
                    {
                        return dc->setArticulationDofStates(artHandle, states.data(), flags);
                    }
                }
                return false;
            },
            "Sets states for an actor's degrees-of-freedom.")

        .def(
            "set_articulation_dof_position_targets",
            [](const DynamicControl* dc, DcHandle artHandle, const py::array_t<float, py::array::c_style>& targets)
            {
                if (dc && dc->isSimulating())
                {
                    if (targets.size() >= ssize_t(dc->getArticulationDofCount(artHandle)))
                    {
                        return dc->setArticulationDofPositionTargets(artHandle, targets.data());
                    }
                }
                return false;
            },
            "Sets an actor's degree-of-freedom position targets.")
        .def(
            "get_articulation_dof_position_targets",
            [](const DynamicControl* dc, DcHandle artHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numDofs = dc->getArticulationDofCount(artHandle);
                    if (numDofs > 0)
                    {
                        auto arr = py::array_t<float, py::array::c_style>(numDofs);
                        if (dc->getArticulationDofPositionTargets(artHandle, arr.mutable_data()))
                        {
                            return arr;
                        }
                    }
                }
                return py::none();
            },
            "Get array of position targets for articulation")
        .def(
            "set_articulation_dof_velocity_targets",
            [](const DynamicControl* dc, DcHandle artHandle, const py::array_t<float, py::array::c_style>& targets)
            {
                if (dc && dc->isSimulating())
                {
                    if (targets.size() >= ssize_t(dc->getArticulationDofCount(artHandle)))
                    {
                        return dc->setArticulationDofVelocityTargets(artHandle, targets.data());
                    }
                }
                return false;
            },
            "Sets an actor's degree-of-freedom velocity targets.")
        .def(
            "get_articulation_dof_velocity_targets",
            [](const DynamicControl* dc, DcHandle artHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numDofs = dc->getArticulationDofCount(artHandle);
                    if (numDofs > 0)
                    {
                        auto arr = py::array_t<float, py::array::c_style>(numDofs);
                        if (dc->getArticulationDofVelocityTargets(artHandle, arr.mutable_data()))
                        {
                            return arr;
                        }
                    }
                }
                return py::none();
            },
            "Get array of velocity targets for articulation")
        .def(
            "set_articulation_dof_efforts",
            [](const DynamicControl* dc, DcHandle artHandle, const py::array_t<float, py::array::c_style>& efforts)
            {
                if (dc && dc->isSimulating())
                {
                    if (efforts.size() >= ssize_t(dc->getArticulationDofCount(artHandle)))
                    {
                        return dc->setArticulationDofEfforts(artHandle, efforts.data());
                    }
                }
                return false;
            },
            "Sets efforts on an actor's degrees-of-freedom.")
        .def(
            "get_articulation_dof_efforts",
            [](const DynamicControl* dc, DcHandle artHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numDofs = dc->getArticulationDofCount(artHandle);
                    if (numDofs > 0)
                    {
                        auto arr = py::array_t<float, py::array::c_style>(numDofs);
                        if (dc->getArticulationDofEfforts(artHandle, arr.mutable_data()))
                        {
                            return arr;
                        }
                    }
                }
                return py::none();
            },
            "Get array of efforts for articulation")
        .def(
            "get_articulation_dof_masses",
            [](const DynamicControl* dc, DcHandle artHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    size_t numDofs = dc->getArticulationDofCount(artHandle);
                    if (numDofs > 0)
                    {
                        auto arr = py::array_t<float, py::array::c_style>(numDofs);
                        if (dc->getArticulationDofMasses(artHandle, arr.mutable_data()))
                        {
                            return arr;
                        }
                    }
                }
                return py::none();
            },
            "Get array of an actor's degree-of-freedom effective masses")

        // rigid bodies

        .def("get_rigid_body_name", wrapInterfaceFunction(&DynamicControl::getRigidBodyName),
             py::return_value_policy::reference, "Gets the rigid body name given a handle")
        .def("get_rigid_body_path", wrapInterfaceFunction(&DynamicControl::getRigidBodyPath),
             py::return_value_policy::reference, "Gets the path to a rigid body given its handle")
        .def("get_rigid_body_parent_joint", wrapInterfaceFunction(&DynamicControl::getRigidBodyParentJoint),
             "Gets parent joint to a rigid body")
        .def("get_rigid_body_child_joint_count", wrapInterfaceFunction(&DynamicControl::getRigidBodyChildJointCount),
             "Gets the number of joints that are children to this rigid body")
        .def("get_rigid_body_child_joint", wrapInterfaceFunction(&DynamicControl::getRigidBodyChildJoint),
             "Get the child joint of a rigid body given its index")
        .def("get_rigid_body_pose", wrapInterfaceFunction(&DynamicControl::getRigidBodyPose),
             "Get the pose of a rigid body")
        .def("set_rigid_body_pose", wrapInterfaceFunction(&DynamicControl::setRigidBodyPose),
             "Set the pose of a rigid body")
        .def("set_rigid_body_disable_gravity", wrapInterfaceFunction(&DynamicControl::setRigidBodyDisableGravity),
             "enables or disables the force of gravity from the given body")
        .def("set_rigid_body_disable_simulation", wrapInterfaceFunction(&DynamicControl::setRigidBodyDisableSimulation),
             "enables or disables Simulation of a given rigid body")
        .def("get_rigid_body_linear_velocity", wrapInterfaceFunction(&DynamicControl::getRigidBodyLinearVelocity),
             "Get the linear velocity of this rigid body in global coordinates")
        .def("get_rigid_body_local_linear_velocity",
             wrapInterfaceFunction(&DynamicControl::getRigidBodyLocalLinearVelocity),
             "Get the linear velocity of this rigid body in local coordinates")
        .def("set_rigid_body_linear_velocity", wrapInterfaceFunction(&DynamicControl::setRigidBodyLinearVelocity),
             "Set the linear velocity of the rigid body")
        .def("get_rigid_body_angular_velocity", wrapInterfaceFunction(&DynamicControl::getRigidBodyAngularVelocity),
             "Get the angular velocity of this rigid body")
        .def("set_rigid_body_angular_velocity", wrapInterfaceFunction(&DynamicControl::setRigidBodyAngularVelocity),
             "Set the angular velocity of this rigid body")
        .def("apply_body_force", wrapInterfaceFunction(&DynamicControl::applyBodyForce),
             "Apply a force to a rigid body at a position, coordinates can be specified in global or local coordinates")
        .def("apply_body_torque", wrapInterfaceFunction(&DynamicControl::applyBodyTorque),
             "Apply a torque to a rigid body, can be specified in global or local coordinates")
        .def(
            "get_relative_body_poses",
            [](const DynamicControl* dc, DcHandle parentHandle, const std::vector<DcHandle>& bodyHandles)
            {
                std::vector<DcTransform> outputTransforms;
                if (dc && dc->isSimulating())
                {
                    const size_t numBodies = bodyHandles.size();
                    if (numBodies > 0)
                    {
                        outputTransforms.resize(numBodies);
                        dc->getRelativeBodyPoses(parentHandle, numBodies, bodyHandles.data(), outputTransforms.data());
                    }
                }
                return outputTransforms;
            },
            "given a list of body handles, return poses relative to the parent")
        .def("get_rigid_body_properties", wrapInterfaceFunction(&DynamicControl::getRigidBodyProperties),
             "Get Properties for a rigid body")
        .def(
            "get_rigid_body_properties",
            [](const DynamicControl* dc, DcHandle attHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    DcRigidBodyProperties props;
                    if (dc->getRigidBodyProperties(attHandle, &props))
                    {
                        return py::cast(props);
                    }
                }
                return py::none();
            },
            "Get Properties for a rigid body")
        .def("set_rigid_body_properties", wrapInterfaceFunction(&DynamicControl::setRigidBodyProperties),
             "Set Properties for a rigid body")
        // joints

        .def("get_joint_name", wrapInterfaceFunction(&DynamicControl::getJointName), py::return_value_policy::reference,
             "Get name of joint")
        .def("get_joint_path", wrapInterfaceFunction(&DynamicControl::getJointPath), py::return_value_policy::reference,
             "Get path for joint")
        .def("get_joint_type", wrapInterfaceFunction(&DynamicControl::getJointType), "Get joint type")
        .def("get_joint_dof_count", wrapInterfaceFunction(&DynamicControl::getJointDofCount),
             "Get number of degrees of freedon constrained by joint")
        .def("get_joint_dof", wrapInterfaceFunction(&DynamicControl::getJointDof),
             "Get a degree of freedom for joint give its index")
        .def("get_joint_parent_body", wrapInterfaceFunction(&DynamicControl::getJointParentBody),
             "Get parent rigid body for joint")
        .def("get_joint_child_body", wrapInterfaceFunction(&DynamicControl::getJointChildBody),
             "Get child rigid body for joint")

        // dofs

        .def("get_dof_name", wrapInterfaceFunction(&DynamicControl::getDofName), py::return_value_policy::reference,
             "Get Name of this degree of freedom")
        .def("get_dof_path", wrapInterfaceFunction(&DynamicControl::getDofPath), py::return_value_policy::reference,
             "Get path to degree of freedom")
        .def("get_dof_type", wrapInterfaceFunction(&DynamicControl::getDofType), "Get type of degree of freedom")
        .def("get_dof_joint", wrapInterfaceFunction(&DynamicControl::getDofJoint),
             "Get joint associated with the degree of freedom")
        .def("get_dof_parent_body", wrapInterfaceFunction(&DynamicControl::getDofParentBody),
             "Get parent rigid body for degree of freedom")
        .def("get_dof_child_body", wrapInterfaceFunction(&DynamicControl::getDofChildBody),
             "Get child rigid body for degree of freedom")
        .def("get_dof_state", wrapInterfaceFunction(&DynamicControl::getDofState),
             "Get current state for degree of freedom")
        .def("set_dof_state", wrapInterfaceFunction(&DynamicControl::setDofState), "Set degree of freedom state")
        .def("get_dof_position", wrapInterfaceFunction(&DynamicControl::getDofPosition),
             "Get position/rotation for this degree of freedom")
        .def("set_dof_position", wrapInterfaceFunction(&DynamicControl::setDofPosition),
             "Set position/rotation for this degree of freedom")
        .def("get_dof_velocity", wrapInterfaceFunction(&DynamicControl::getDofVelocity),
             "Get linear/angular velocity of degree of freedom")
        .def("set_dof_velocity", wrapInterfaceFunction(&DynamicControl::setDofVelocity),
             "Set linear angular velocity of degree of freedom")
        .def("get_dof_properties", wrapInterfaceFunction(&DynamicControl::getDofProperties),
             "Get degree of freedom properties")
        .def(
            "get_dof_properties",
            [](const DynamicControl* dc, DcHandle dofHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    DcDofProperties props;
                    if (dc->getDofProperties(dofHandle, &props))
                    {
                        return py::cast(props);
                    }
                }
                return py::none();
            },
            "Get degree of freedom properties")
        .def("set_dof_properties", wrapInterfaceFunction(&DynamicControl::setDofProperties),
             "Set degree of freedom properties")
        .def("set_dof_position_target", wrapInterfaceFunction(&DynamicControl::setDofPositionTarget),
             "Set position target for degree of freedom")
        .def("set_dof_velocity_target", wrapInterfaceFunction(&DynamicControl::setDofVelocityTarget),
             "Set velocity target for degree of freedom")
        .def("get_dof_position_target", wrapInterfaceFunction(&DynamicControl::getDofPositionTarget),
             "Get position target for degree of freedom")
        .def("get_dof_velocity_target", wrapInterfaceFunction(&DynamicControl::getDofVelocityTarget),
             "Get velocity target for degree of freedom")
        .def("set_dof_effort", wrapInterfaceFunction(&DynamicControl::setDofEffort), "Set effort on degree of freedom")
        .def("get_dof_effort", wrapInterfaceFunction(&DynamicControl::getDofEffort),
             "Get effort applied to degree of freedom")


        // attractors

        .def("create_rigid_body_attractor", wrapInterfaceFunction(&DynamicControl::createRigidBodyAttractor),
             py::return_value_policy::reference, "Greate an attractor for ridig body")
        .def("destroy_rigid_body_attractor", wrapInterfaceFunction(&DynamicControl::destroyRigidBodyAttractor),
             "Destroy attractor")
        .def("set_attractor_properties", wrapInterfaceFunction(&DynamicControl::setAttractorProperties),
             "Set properties for this attractor")
        .def("set_attractor_target", wrapInterfaceFunction(&DynamicControl::setAttractorTarget),
             "Set target pose for attractor")
        .def(
            "get_attractor_properties",
            [](const DynamicControl* dc, DcHandle attHandle) -> py::object
            {
                if (dc && dc->isSimulating())
                {
                    DcAttractorProperties props;
                    if (dc->getAttractorProperties(attHandle, &props))
                    {
                        return py::cast(props);
                    }
                }
                return py::none();
            },
            "Get properties for attractor")

        .def("create_d6_joint", wrapInterfaceFunction(&DynamicControl::createD6Joint),
             py::return_value_policy::reference, "Create a D6 joint")
        .def("destroy_d6_joint", wrapInterfaceFunction(&DynamicControl::destroyD6Joint), "Destroy D6 joint")
        .def("set_d6_joint_properties", wrapInterfaceFunction(&DynamicControl::setD6JointProperties),
             "Modifies properties of the selected joint.")

        .def("set_origin_offset", wrapInterfaceFunction(&DynamicControl::setOriginOffset),
             "Offset origin for a rigid body")

        ;

    using omni::isaac::dynamic_control::math::operator*;
    auto math = m.def_submodule("math");

    math.def(
        "mul", [](const DcTransform& a, const DcTransform& x) { return a * x; }, py::is_operator(),
        R"pbdoc( Performs a Forward Transform multiplication between the transforms
        
        Args:
            arg0 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): First Transform

            arg1 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): Second Transform

        Returns:

            :obj:`omni.isaac.dynamic_control._dynamic_control.Transform`: ``arg0 * arg1``
        )pbdoc");

    math.def("inverse", py::overload_cast<const DcTransform&>(&omni::isaac::dynamic_control::math::inverse),
             R"pbdoc(Gets Inverse Transform
             Args:

                 arg0 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): Transform

             Returns:

                 :obj:`omni.isaac.dynamic_control._dynamic_control.Transform`: The inverse Inverse Transform

             )pbdoc");
    math.def("transform_inv",
             py::overload_cast<const DcTransform&, const DcTransform&>(&omni::isaac::dynamic_control::math::transformInv),
             R"pbdoc(
                Computes local Transform of arg1 with respect to arg0: `inv(arg0)*arg1`

                Args:
                
                    arg0 (`omni.isaac.dynamic_control._dynamic_control.Transform`): origin Transform

                    arg1 (`omni.isaac.dynamic_control._dynamic_control.Transform`): Transform

                Returns:

                    :obj:`omni.isaac.dynamic_control._dynamic_control.Transform`: resulting transform of ``inv(arg0)*arg1``
                )pbdoc");
    math.def(
        "lerp",
        py::overload_cast<const DcTransform&, const DcTransform&, const float>(&omni::isaac::dynamic_control::math::lerp),
        R"pbdoc(
                Performs Linear interpolation between points arg0 and arg1

                Args:

                    arg0 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): Transform

                    arg1 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): Transform

                    arg2 (:obj:`float`): distance from 0 to 1, where 0 is closest to arg0, and 1 is closest to arg1

                Returns:

                    :obj:`omni.isaac.dynamic_control._dynamic_control.Transform`: Interpolated transform
                    
                )pbdoc");
    math.def("slerp",
             py::overload_cast<const DcTransform&, const DcTransform&, const float>(
                 &omni::isaac::dynamic_control::math::slerp),
             R"pbdoc(
                Performs Spherical Linear interpolation between points arg0 and arg1

                Args:

                    arg0 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): Transform

                    arg1 (:obj:`omni.isaac.dynamic_control._dynamic_control.Transform`): Transform

                    arg2 (:obj:`float`): distance from 0 to 1, where 0 is closest to arg0, and 1 is closest to arg1

                Returns:

                    :obj:`omni.isaac.dynamic_control._dynamic_control.Transform`: Interpolated transform
                    
                )pbdoc");
}
}
