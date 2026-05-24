// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include "DcPhysx.h"

#include <carb/logging/Log.h>

#include <isaacsim/core/includes/UsdUtilities.h>
#include <omni/physx/IPhysx.h>
#include <omni/physx/IPhysxSceneQuery.h>
#include <omni/usd/UsdContext.h>

using namespace ::physx;
using namespace pxr;


namespace omni
{
namespace isaac
{
namespace dynamic_control
{


DcContext::DcContext(uint32_t ctxId) : mId(ctxId)
{
}

uint32_t DcContext::getId() const
{
    return mId;
}

// DcHandle DcContext::registerRigidBody(const pxr::SdfPath& usdPath);
// DcHandle DcContext::registerJoint(const pxr::SdfPath& usdPath);
// DcHandle DcContext::registerDof(const pxr::SdfPath& usdPath);
// DcHandle DcContext::registerArticulation(const pxr::SdfPath& usdPath);
// DcHandle DcContext::registerD6Joint(const pxr::SdfPath& usdPath);

DcHandle DcContext::addRigidBody(std::unique_ptr<DcRigidBody>&& rb, const pxr::SdfPath& usdPath)
{
    uint32_t id = mRigidBodies.add(std::move(rb));
    DcHandle handle = makeHandle(id, eDcObjectRigidBody, mId);
    mRigidBodyMap[usdPath] = handle;
    mHandleMap[usdPath].insert(handle);
    return handle;
}

DcHandle DcContext::addJoint(std::unique_ptr<DcJoint>&& joint, const pxr::SdfPath& usdPath)
{
    uint32_t id = mJoints.add(std::move(joint));
    DcHandle handle = makeHandle(id, eDcObjectJoint, mId);
    mJointMap[usdPath] = handle;
    mHandleMap[usdPath].insert(handle);
    return handle;
}

DcHandle DcContext::addDof(std::unique_ptr<DcDof>&& dof, const pxr::SdfPath& usdPath)
{
    uint32_t id = mDofs.add(std::move(dof));
    DcHandle handle = makeHandle(id, eDcObjectDof, mId);
    mDofMap[usdPath] = handle;
    mHandleMap[usdPath].insert(handle);
    return handle;
}

DcHandle DcContext::addArticulation(std::unique_ptr<DcArticulation>&& art, const pxr::SdfPath& usdPath)
{
#if 1
    // assign this articulation to the specified usdPath
    uint32_t id = mArticulations.add(std::move(art));
    DcHandle handle = makeHandle(id, eDcObjectArticulation, mId);
    mArticulationMap[usdPath] = handle;
    mHandleMap[usdPath].insert(handle);
#else
    // assign this articulation handle to all the component paths
    DcArticulation* artPtr = art.get();
    uint32_t id = mArticulations.add(std::move(art));
    DcHandle handle = makeHandle(id, eDcObjectArticulation, mId);
    for (auto& path : artPtr->componentPaths)
    {
        mArticulationMap[path] = handle;
        mHandleMap[path].insert(handle);
    }
#endif
    return handle;
}

DcHandle DcContext::addAttractor(std::unique_ptr<DcAttractor>&& attractor, const pxr::SdfPath& usdPath)
{
    uint32_t id = mAttractors.add(std::move(attractor));
    DcHandle handle = makeHandle(id, eDcObjectAttractor, mId);
    mAttractorMap[usdPath] = handle;
    mHandleMap[usdPath].insert(handle);
    return handle;
}

DcHandle DcContext::addD6Joint(std::unique_ptr<DcD6Joint>&& dc_joint, const pxr::SdfPath& usdPath)
{
    uint32_t id = mD6Joints.add(std::move(dc_joint));
    DcHandle handle = makeHandle(id, eDcObjectD6Joint, mId);
    mD6JointMap[usdPath] = handle;
    mHandleMap[usdPath].insert(handle);
    return handle;
}


DcHandle DcContext::getRigidBodyHandle(const pxr::SdfPath& usdPath) const
{
    auto it = mRigidBodyMap.find(usdPath);
    if (it != mRigidBodyMap.end())
    {
        return it->second;
    }
    return kDcInvalidHandle;
}

DcHandle DcContext::getJointHandle(const pxr::SdfPath& usdPath) const
{
    auto it = mJointMap.find(usdPath);
    if (it != mJointMap.end())
    {
        return it->second;
    }
    return kDcInvalidHandle;
}

// HMMM, there could be multiple DOFs at a single USD path (e.g. spherical joint)
DcHandle DcContext::getDofHandle(const pxr::SdfPath& usdPath) const
{
    auto it = mDofMap.find(usdPath);
    if (it != mDofMap.end())
    {
        return it->second;
    }
    return kDcInvalidHandle;
}

DcHandle DcContext::getArticulationHandle(const pxr::SdfPath& usdPath) const
{
    // look up articulation
    auto artIt = mArticulationMap.find(usdPath);
    if (artIt != mArticulationMap.end())
    {
        return artIt->second;
    }

    // is it an articulation link?
    auto bodyIt = mRigidBodyMap.find(usdPath);
    if (bodyIt != mRigidBodyMap.end())
    {
        DcHandle bodyHandle = bodyIt->second;
        DcRigidBody* body = getRigidBody(bodyHandle);
        if (body && body->art)
        {
            return body->art->handle;
        }
    }

    // is it an articulation joint?
    auto jointIt = mJointMap.find(usdPath);
    if (jointIt != mJointMap.end())
    {
        DcHandle jointHandle = jointIt->second;
        DcJoint* joint = getJoint(jointHandle);
        if (joint && joint->art)
        {
            return joint->art->handle;
        }
    }

    return kDcInvalidHandle;
}

DcHandle DcContext::getAttractorHandle(const pxr::SdfPath& usdPath) const
{
    auto it = mAttractorMap.find(usdPath);
    if (it != mAttractorMap.end())
    {
        return it->second;
    }
    return kDcInvalidHandle;
}

DcRigidBody* DcContext::getRigidBody(DcHandle handle) const
{
    if (getHandleContextId(handle) == mId && getHandleTypeId(handle) == eDcObjectRigidBody)
    {
        auto objId = getHandleObjectId(handle);
        return mRigidBodies.get(objId);
    }
    return nullptr;
}

DcJoint* DcContext::getJoint(DcHandle handle) const
{
    if (getHandleContextId(handle) == mId && getHandleTypeId(handle) == eDcObjectJoint)
    {
        auto objId = getHandleObjectId(handle);
        return mJoints.get(objId);
    }
    return nullptr;
}

DcDof* DcContext::getDof(DcHandle handle) const
{
    if (getHandleContextId(handle) == mId && getHandleTypeId(handle) == eDcObjectDof)
    {
        auto objId = getHandleObjectId(handle);
        return mDofs.get(objId);
    }
    return nullptr;
}

DcArticulation* DcContext::getArticulation(DcHandle handle) const
{
    if (getHandleContextId(handle) == mId && getHandleTypeId(handle) == eDcObjectArticulation)
    {
        auto objId = getHandleObjectId(handle);
        return mArticulations.get(objId);
    }
    return nullptr;
}

DcAttractor* DcContext::getAttractor(DcHandle handle) const
{
    if (getHandleContextId(handle) == mId && getHandleTypeId(handle) == eDcObjectAttractor)
    {
        auto objId = getHandleObjectId(handle);
        return mAttractors.get(objId);
    }
    return nullptr;
}

DcD6Joint* DcContext::getD6Joint(DcHandle handle) const
{
    // DC_LOG_INFO("searching for Dc D6 joint handle %ld (%d - %d)", handle,
    // getHandleTypeId(handle),eDcObjectD6Joint);
    if (getHandleContextId(handle) == mId && getHandleTypeId(handle) == eDcObjectD6Joint)
    {
        auto objId = getHandleObjectId(handle);
        return mD6Joints.get(objId);
    }
    return nullptr;
}

void DcContext::removeRigidBody(DcHandle handle)
{
    DcRigidBody* body = getRigidBody(handle);
    if (body)
    {
        auto bodyIt = mRigidBodyMap.find(body->path);
        if (bodyIt != mRigidBodyMap.end())
        {
            mRigidBodyMap.erase(bodyIt);
        }
        auto objId = getHandleObjectId(handle);
        mRigidBodies.remove(objId);
    }
}

void DcContext::removeJoint(DcHandle handle)
{
    DcJoint* joint = getJoint(handle);
    if (joint)
    {
        auto jointIt = mJointMap.find(joint->path);
        if (jointIt != mJointMap.end())
        {
            mJointMap.erase(jointIt);
        }
        auto objId = getHandleObjectId(handle);
        mJoints.remove(objId);
    }
}

/*
// don't remove individual dofs; remove joints instead
void DcContext::removeDof(DcHandle handle)
{
    DcDof* dof = getDof(handle);
    if (dof)
    {
        auto dofIt = mDofMap.find(dof->path);
        if (dofIt != mDofMap.end())
        {
            mDofMap.erase(dofIt);
        }
        auto objId = getHandleObjectId(handle);
        mDofs.remove(objId);
    }
}
*/

void DcContext::removeArticulation(DcHandle handle)
{
    DcArticulation* art = getArticulation(handle);
    if (art)
    {
        auto artIt = mArticulationMap.find(art->path);
        if (artIt != mArticulationMap.end())
        {
            mArticulationMap.erase(artIt);
        }
        auto objId = getHandleObjectId(handle);
        mArticulations.remove(objId);
    }
}

void DcContext::removeAttractor(DcHandle handle)
{
    DcAttractor* att = getAttractor(handle);
    if (att)
    {
        auto attIt = mAttractorMap.find(att->path);
        if (attIt != mAttractorMap.end())
        {
            mAttractorMap.erase(attIt);
        }
        auto objId = getHandleObjectId(handle);
        mAttractors.remove(objId);
    }
}

void DcContext::removeD6Joint(DcHandle handle)
{
    DcD6Joint* joint = getD6Joint(handle);
    if (joint)
    {
        auto jointIt = mD6JointMap.find(joint->path);
        if (jointIt != mD6JointMap.end())
        {
            mD6JointMap.erase(jointIt);
        }
        auto objId = getHandleObjectId(handle);
        mD6Joints.remove(objId);
    }
}

void DcContext::remove(DcHandle handle)
{
    DcObjectType type = (DcObjectType)getHandleTypeId(handle);
    switch (type)
    {
    case DcObjectType::eDcObjectRigidBody:
        removeRigidBody(handle);
        break;
    case DcObjectType::eDcObjectJoint:
        removeJoint(handle);
        break;
    case DcObjectType::eDcObjectArticulation:
        removeArticulation(handle);
        break;
    case DcObjectType::eDcObjectAttractor:
        removeAttractor(handle);
        break;
    case DcObjectType::eDcObjectD6Joint:
        removeD6Joint(handle);
        break;
    default:
        // CARB_LOG_INFO("REMOVING UNKNOWN HANDLE TYPE");
        break;
    }
}

void DcContext::removeUsdPath(const pxr::SdfPath& usdPath)
{
    for (auto it = mHandleMap.begin(); it != mHandleMap.end();)
    {
        if (pxr::SdfPath(it->first).HasPrefix(usdPath))
        {
            for (const auto& h : it->second)
            {
                remove(h);
            }
            it->second.clear();
            it = mHandleMap.erase(it);
        }
        else
        {
            it++;
        }
    }
}

int DcContext::numAttractors() const
{
    return int(mAttractorMap.size());
}

int DcContext::numD6Joints() const
{
    return int(mD6JointMap.size());
}


bool DcContext::refreshPhysicsPointers(DcRigidBody* body, bool verbose)
{
    if (!body)
    {
        return false;
    }

    PxActor* pxActor = static_cast<PxActor*>(physx->getPhysXPtr(body->path, omni::physx::PhysXType::ePTActor));
    if (pxActor)
    {
        PxActorType::Enum type = pxActor->getType();
        if (type == PxActorType::eRIGID_DYNAMIC /*|| type == PxActorType::eARTICULATION_LINK*/)
        {
            body->pxRigidBody = static_cast<PxRigidBody*>(pxActor);
            if (verbose)
            {
                CARB_LOG_INFO("Refreshed body %s\n", body->path.GetString().c_str());
            }
            return true;
        }
    }
    else
    {
        PxArticulationLink* link =
            static_cast<PxArticulationLink*>(physx->getPhysXPtr(body->path, omni::physx::PhysXType::ePTLink));
        if (link)
        {
            body->pxRigidBody = static_cast<PxRigidBody*>(link);
            if (verbose)
            {
                CARB_LOG_INFO("Refreshed articulation link %s\n", body->path.GetString().c_str());
            }
            return true;
        }
    }

    if (verbose)
    {
        CARB_LOG_ERROR("Failed to refresh body %s (no suitable physics object)", body->path.GetString().c_str());
    }

    body->pxRigidBody = nullptr; // invalidate physics pointer

    return false;
}

bool DcContext::refreshPhysicsPointers(DcJoint* joint, bool verbose)
{
    if (!joint)
    {
        return false;
    }

    // we only support articulation joints, for now
    PxArticulationJointReducedCoordinate* pxArticulationJoint = static_cast<PxArticulationJointReducedCoordinate*>(
        physx->getPhysXPtr(joint->path, omni::physx::PhysXType::ePTLinkJoint));

    if (pxArticulationJoint)
    {
        joint->pxArticulationJoint = pxArticulationJoint;

        // update dofs
        for (auto dofHandle : joint->dofs)
        {
            DcDof* dof = getDof(dofHandle);
            if (dof)
            {
                dof->pxArticulationJoint = pxArticulationJoint;
            }
        }

        if (verbose)
        {
            CARB_LOG_INFO("Refreshed joint %s\n", joint->path.GetString().c_str());
        }

        return true;
    }

    if (verbose)
    {
        CARB_LOG_ERROR("Failed to refresh joint %s (no suitable physics object)", joint->path.GetString().c_str());
    }

    // invalidate physics pointer
    joint->pxArticulationJoint = nullptr;

    // invalidate dofs
    for (auto dofHandle : joint->dofs)
    {
        DcDof* dof = getDof(dofHandle);
        if (dof)
        {
            dof->pxArticulationJoint = nullptr;
        }
    }

    return false;
}

bool DcContext::refreshPhysicsPointers(DcArticulation* art, bool verbose)
{
    if (!art)
    {
        return false;
    }
    art->pxArticulationCache = nullptr;
    art->pxArticulation = nullptr;
    art->cacheAge = -1;

    PxArticulationReducedCoordinate* abase = static_cast<PxArticulationReducedCoordinate*>(
        physx->getPhysXPtr(art->path, omni::physx::PhysXType::ePTArticulation));
    if (!abase || abase->getConcreteType() != PxConcreteType::eARTICULATION_REDUCED_COORDINATE)
    {
        if (verbose)
        {
            CARB_LOG_ERROR("Failed to refresh articulation %s", art->path.GetString().c_str());
        }
        return false;
    }

    art->pxArticulation = static_cast<PxArticulationReducedCoordinate*>(abase);
    if (art->pxArticulation->getScene())
    {
        // art->pxArticulation->releaseCache(*art->pxArticulationCache);
        if (art->pxArticulationCache)
        {
            art->pxArticulationCache->release();
        }
        art->pxArticulationCache = art->pxArticulation->createCache();
    }

    if (verbose)
    {
        CARB_LOG_INFO("Refreshed articulation %s\n", art->path.GetString().c_str());
    }

    return true;
}

bool DcContext::refreshPhysicsPointers(DcAttractor* att, bool verbose)
{
    if (!att)
    {
        return false;
    }

    att->pxJoint = nullptr;

    PxJoint* pxJoint = static_cast<PxJoint*>(physx->getPhysXPtr(att->path, omni::physx::PhysXType::ePTJoint));
    if (!pxJoint || pxJoint->getConcreteType() != PxJointConcreteType::eD6)
    {
        if (verbose)
        {
            CARB_LOG_ERROR("Failed to refresh attractor joint %s", att->path.GetString().c_str());
        }
        return false;
    }

    att->pxJoint = static_cast<PxD6Joint*>(pxJoint);
    if (verbose)
    {
        CARB_LOG_INFO("Refreshed attractor joint %s\n", att->path.GetString().c_str());
    }
    return true;
}

bool DcContext::refreshPhysicsPointers(DcD6Joint* d6joint, bool verbose)
{
    if (!d6joint)
    {
        return false;
    }

    d6joint->pxJoint = nullptr;
    // The joint exists in usd stage
    PxJoint* pxJoint = static_cast<PxJoint*>(physx->getPhysXPtr(d6joint->path, omni::physx::PhysXType::ePTJoint));
    if (pxJoint && pxJoint->getConcreteType() == PxJointConcreteType::eD6)
    {
        d6joint->pxJoint = static_cast<PxD6Joint*>(pxJoint);

        if (verbose)
        {
            CARB_LOG_INFO("Refreshed joint %s\n", d6joint->path.GetString().c_str());
        }
        return true;
    }
    // Joint was destroyed as it was not in stage, clear handles:
    d6joint->pxJoint = nullptr;
    return false;
}

void DcContext::refreshPhysicsPointers(bool verbose)
{
    for (const auto& kv : mArticulationMap)
    {
        DcArticulation* art = getArticulation(kv.second);
        if (art)
        {
            // printf("Refreshing articulation %s\n", art->path.GetString().c_str());
            if (!refreshPhysicsPointers(art, verbose))
            {
            }
        }
    }

    for (const auto& kv : mRigidBodyMap)
    {
        DcRigidBody* body = getRigidBody(kv.second);
        if (body)
        {
            // printf("Refreshing rigid body %s\n", body->path.GetString().c_str());
            if (!refreshPhysicsPointers(body, verbose))
            {
            }
        }
    }

    for (const auto& kv : mJointMap)
    {
        DcJoint* joint = getJoint(kv.second);
        if (joint)
        {
            // printf("Refreshing joint %s\n", joint->path.GetString().c_str());
            if (!refreshPhysicsPointers(joint, verbose))
            {
            }
        }
    }

    for (const auto& kv : mAttractorMap)
    {
        DcAttractor* att = getAttractor(kv.second);
        if (att)
        {
            // printf("Refreshing attractor %s\n", att->path.GetString().c_str());
            if (!refreshPhysicsPointers(att, verbose))
            {
            }
        }
    }

    for (const auto& kv : mD6JointMap)
    {
        DcD6Joint* j = getD6Joint(kv.second);
        if (j)
        {
            if (!refreshPhysicsPointers(j, verbose))
            {
            }
        }
    }
}


DcHandle DcContext::registerRigidBody(const pxr::SdfPath& usdPath)
{
    // check if we already have this body
    DcHandle h = getRigidBodyHandle(usdPath);
    if (h != kDcInvalidHandle)
    {
        return h;
    }

    // check if it's a single body
    PxActor* pxActor = static_cast<PxActor*>(physx->getPhysXPtr(usdPath, omni::physx::PhysXType::ePTActor));
    if (pxActor)
    {
        CARB_LOG_INFO("Got %s at %p\n", pxActor->getConcreteTypeName(), static_cast<void*>(pxActor));
        if (pxActor->getType() == PxActorType::eRIGID_DYNAMIC)
        {
            PxRigidDynamic* rd = static_cast<PxRigidDynamic*>(pxActor);
            PxTransform pose = rd->getGlobalPose();
            CARB_LOG_INFO("  Pos: (%f, %f, %f)\n", pose.p.x, pose.p.y, pose.p.z);
            CARB_LOG_INFO("  Rot: (%f, %f, %f, %f)\n", pose.q.x, pose.q.y, pose.q.z, pose.q.w);

            std::unique_ptr<DcRigidBody> body(new DcRigidBody);
            body->ctx = this;
            body->pxRigidBody = rd;
            body->path = usdPath;
            auto stage = omni::usd::UsdContext::getContext()->getStage();
            body->name = isaacsim::core::includes::getName(stage->GetPrimAtPath(usdPath));
            DcRigidBody* bodyPtr = body.get();
            DcHandle bodyHandle = addRigidBody(std::move(body), usdPath);
            bodyPtr->handle = bodyHandle;
            return bodyHandle;
        }
    }
    else
    {
        // check if it's an articulation link
        PxArticulationLink* link =
            static_cast<PxArticulationLink*>(physx->getPhysXPtr(usdPath, omni::physx::PhysXType::ePTLink));
        if (link)
        {
            // register the whole articulation
            registerArticulation(usdPath);
            return getRigidBodyHandle(usdPath);
        }
    }

    CARB_LOG_ERROR("Failed to register rigid body at '%s'", usdPath.GetString().c_str());
    return kDcInvalidHandle;
}

DcHandle DcContext::registerJoint(const pxr::SdfPath& usdPath)
{
    return kDcInvalidHandle;
}

DcHandle DcContext::registerDof(const pxr::SdfPath& usdPath)
{
    return kDcInvalidHandle;
}

DcHandle DcContext::registerArticulation(const pxr::SdfPath& usdPath)
{
    // check if we already have this articulation
    DcHandle h = getArticulationHandle(usdPath);
    if (h != kDcInvalidHandle)
    {
        return h;
    }

    // check if it's an articulation
    PxArticulationReducedCoordinate* abase =
        (PxArticulationReducedCoordinate*)physx->getPhysXPtr(usdPath, omni::physx::PhysXType::ePTArticulation);
    if (abase)
    {
        CARB_LOG_INFO("Got %s at %p\n", abase->getConcreteTypeName(), static_cast<void*>(abase));
    }
    else
    {
        // check if it's an articulation link
        PxArticulationLink* link =
            static_cast<PxArticulationLink*>(physx->getPhysXPtr(usdPath, omni::physx::PhysXType::ePTLink));
        if (link)
        {
            CARB_LOG_INFO("Got %s at %p\n", link->getConcreteTypeName(), static_cast<void*>(link));
            abase = &link->getArticulation();
        }
        else
        {
            // check if it's an articulation joint
            PxArticulationJointReducedCoordinate* joint = static_cast<PxArticulationJointReducedCoordinate*>(
                physx->getPhysXPtr(usdPath, omni::physx::PhysXType::ePTLinkJoint));
            if (joint)
            {
                CARB_LOG_INFO("Got %s at %p\n", joint->getConcreteTypeName(), static_cast<void*>(joint));
                abase = &joint->getChildArticulationLink().getArticulation();
            }
        }
    }
    auto atype = mStage->GetPrimAtPath(SdfPath(usdPath)).GetTypeName();

    if (!abase || abase->getConcreteType() != PxConcreteType::eARTICULATION_REDUCED_COORDINATE ||
        atype == "PhysicsFixedJoint")
    {
        CARB_LOG_WARN("Failed to find articulation at '%s'", usdPath.GetString().c_str());
        return kDcInvalidHandle;
    }

    PxArticulationReducedCoordinate* arc = static_cast<PxArticulationReducedCoordinate*>(abase);
    // arc->setArticulationFlag(PxArticulationFlag::eCOMPUTE_JOINT_FORCES, true);
    /*
    PxU32 posIters, velIters;
    arc->getSolverIterationCounts(posIters, velIters);
    printf("Position iteration counts: %u\n", posIters);
    printf("Velocity iteration counts: %u\n", velIters);
    */

    std::unique_ptr<DcArticulation> art(new DcArticulation);
    art->pxArticulation = arc;
    art->ctx = this;
    art->name = "articulation"; // !!!
    art->componentPaths.insert(usdPath);

    // maps link pointers to body pointers
    std::map<PxArticulationLink*, DcRigidBody*> bodyMap;

    // get links
    PxU32 numLinks = arc->getNbLinks();
    std::vector<PxArticulationLink*> links(numLinks);
    arc->getLinks(links.data(), numLinks);

    art->rigidBodies.resize(numLinks);

    // get the ordering of the links in the articulation cache
    std::vector<PxArticulationLink*> orderedLinks(numLinks);
    for (PxU32 j = 0; j < numLinks; j++)
    {
        PxU32 linkIdx = links[j]->getLinkIndex();
        orderedLinks[linkIdx] = links[j];
    }

    // this is important so that link and DOF traversals are done in articulation cache order
    links = orderedLinks;
    for (PxU32 i = 0; i < numLinks; i++)
    {
        //
        // register link
        //

        CARB_LOG_INFO("Link %u\n", i);
        PxArticulationLink* link = links[i];

        size_t linkId = (size_t)link->userData;
        CARB_LOG_INFO("  Link id: %llu\n", (unsigned long long)linkId);

        std::unique_ptr<DcRigidBody> body(new DcRigidBody);
        body->ctx = this;
        body->pxRigidBody = link;
        body->art = art.get();

        SdfPath linkPath = physx->getPhysXObjectUsdPath(linkId);
        CARB_LOG_INFO("  Link path: %s\n", linkPath.GetString().c_str());
        body->path = linkPath;
        auto stage = omni::usd::UsdContext::getContext()->getStage();
        body->name = isaacsim::core::includes::getName(stage->GetPrimAtPath(linkPath));

        art->componentPaths.insert(body->path);

        DcHandle bodyHandle = addRigidBody(std::move(body), linkPath);
        DcRigidBody* bodyPtr = getRigidBody(bodyHandle);
        bodyPtr->handle = bodyHandle;

        bodyMap[link] = bodyPtr;

        //
        // register joint and dofs
        //

        PxArticulationJointReducedCoordinate* pxJoint =
            static_cast<PxArticulationJointReducedCoordinate*>(link->getInboundJoint());
        if (pxJoint)
        {
            size_t jointId = (size_t)pxJoint->userData;
            CARB_LOG_INFO("  Joint id: %llu\n", (unsigned long long)jointId);

            SdfPath jointPath = physx->getPhysXObjectUsdPath(jointId);
            CARB_LOG_INFO("  Joint path: %s\n", jointPath.GetString().c_str());

            std::unique_ptr<DcJoint> joint(new DcJoint);
            joint->ctx = this;
            joint->pxArticulationJoint = pxJoint;
            joint->art = art.get();
            joint->path = jointPath;
            auto usdStage = omni::usd::UsdContext::getContext()->getStage();
            joint->name = isaacsim::core::includes::getName(usdStage->GetPrimAtPath(jointPath));

            CARB_LOG_INFO("  Joint name: %s\n", joint->name.c_str());

            art->componentPaths.insert(joint->path);

            // joint type
            PxArticulationJointType::Enum jointType = pxJoint->getJointType();
            switch (jointType)
            {
            case PxArticulationJointType::eFIX:
                joint->type = DcJointType::eFixed;
                break;
            case PxArticulationJointType::eREVOLUTE:
                joint->type = DcJointType::eRevolute;
                break;
            case PxArticulationJointType::eREVOLUTE_UNWRAPPED:
                joint->type = DcJointType::eRevolute;
                break;
            case PxArticulationJointType::ePRISMATIC:
                joint->type = DcJointType::ePrismatic;
                break;
            case PxArticulationJointType::eSPHERICAL:
                joint->type = DcJointType::eSpherical;
                break;
            case PxArticulationJointType::eUNDEFINED:
            default:
                joint->type = DcJointType::eNone;
                break;
            }

            DcHandle jointHandle = addJoint(std::move(joint), jointPath);
            DcJoint* jointPtr = getJoint(jointHandle);
            jointPtr->handle = jointHandle;

            if (jointType == PxArticulationJointType::eREVOLUTE ||
                jointType == PxArticulationJointType::eREVOLUTE_UNWRAPPED ||
                jointType == PxArticulationJointType::ePRISMATIC)
            {
                //
                // register dof
                //

                std::unique_ptr<DcDof> dof(new DcDof);
                dof->ctx = this;
                dof->pxArticulationJoint = pxJoint;
                dof->art = art.get();
                dof->joint = jointHandle;
                dof->path = jointPtr->path;
                dof->name = jointPtr->name;
                dof->cacheIdx = art->dofs.size(); // only active dofs end up having cache access
                // art->paths.insert(dof->path); // unnecessary, since dof->path == joint->path

                if (jointType == PxArticulationJointType::eREVOLUTE ||
                    jointType == PxArticulationJointType::eREVOLUTE_UNWRAPPED)
                {
                    dof->type = DcDofType::eRotation;
                    dof->pxAxis = PxArticulationAxis::eTWIST;
                }
                else
                {
                    dof->type = DcDofType::eTranslation;
                    dof->pxAxis = PxArticulationAxis::eX;
                }

                PxArticulationDrive drive = pxJoint->getDriveParams(dof->pxAxis);

                CARB_LOG_INFO("  Drive axis: %d\n", int(dof->pxAxis));
                CARB_LOG_INFO("  Drive type: %d\n", int(drive.driveType));
                CARB_LOG_INFO("  Drive stiffness: %f\n", drive.stiffness);
                CARB_LOG_INFO("  Drive damping: %f\n", drive.damping);
                CARB_LOG_INFO("  Drive maxForce: %f\n", drive.maxForce);

                // get the current drive mode
                switch (drive.driveType)
                {
                case PxArticulationDriveType::eFORCE:
                    dof->driveMode = DcDriveMode::eForce;
                    break;
                case PxArticulationDriveType::eACCELERATION:
                    dof->driveMode = DcDriveMode::eAcceleration;
                    break;
                default:
                    dof->driveMode = DcDriveMode::eAcceleration;
                    break;
                }

#if 0
                printf("  !!! Resetting drive !!!\n");
                stiffness = 0.0f;
                damping = 0.0f;
                pxJoint->setDrive(dof->pxAxis, stiffness, damping, maxForce, driveType);
#endif

                DcHandle dofHandle = addDof(std::move(dof), jointPath);
                DcDof* dofPtr = getDof(dofHandle);
                dofPtr->handle = dofHandle;

                art->dofs.push_back(dofPtr);
                art->dofMap[dofPtr->name] = dofPtr;

                jointPtr->dofs.push_back(dofHandle);
            }

            art->joints.push_back(jointPtr);
            art->jointMap[jointPtr->name] = jointPtr;
        }

        art->rigidBodies[i] = bodyPtr;
        art->rigidBodyMap[bodyPtr->name] = bodyPtr;
    }

    // resolve hierarchy relationships
    for (auto joint : art->joints)
    {
        PxArticulationJointReducedCoordinate* pxJoint = joint->pxArticulationJoint;
        PxArticulationLink* parentLink = &pxJoint->getParentArticulationLink();
        PxArticulationLink* childLink = &pxJoint->getChildArticulationLink();

        DcRigidBody* parentBody = bodyMap[parentLink];
        DcRigidBody* childBody = bodyMap[childLink];

        joint->parentBody = parentBody->handle;
        joint->childBody = childBody->handle;

        childBody->parentJoint = joint->handle;
        parentBody->childJoints.push_back(joint->handle);
    }

    // allocate state caches
    art->rigidBodyStateCache.resize(art->rigidBodies.size());
    art->dofStateCache.resize(art->dofs.size());

    // NOTE: createCache will crash if articulation is not in a scene yet
    if (arc->getScene())
    {
        art->pxArticulationCache = arc->createCache();
        if (!art->pxArticulationCache)
        {
            CARB_LOG_ERROR("Failed to create articulation cache");
        }
    }
    else
    {
        CARB_LOG_WARN(
            "Articulation is not in a physics scene, some functionality is missing, make sure that a physics scene is present and simulation is running");
    }

    // figure out which path this articulation is mapped to in omni.physx
    size_t artId = (size_t)arc->userData;
    SdfPath artPath = physx->getPhysXObjectUsdPath(artId);
    CARB_LOG_INFO("Articulation path is '%s'\n", artPath.GetString().c_str());
    art->path = artPath;

    // DcHandle artHandle = addArticulation(std::move(art), usdPath);
    DcHandle artHandle = addArticulation(std::move(art), artPath);
    DcArticulation* artPtr = getArticulation(artHandle);
    artPtr->handle = artHandle;

    return artHandle;
}

DcHandle DcContext::registerD6Joint(const pxr::SdfPath& usdPath)
{
    DcHandle h = getJointHandle(usdPath);
    if (h != kDcInvalidHandle)
    {
        return h;
    }
    // check if it's a d6joint
    PxD6Joint* joint = static_cast<PxD6Joint*>(physx->getPhysXPtr(SdfPath(usdPath), omni::physx::PhysXType::ePTJoint));
    if (joint)
    {
        std::unique_ptr<DcD6Joint> dcJoint(new DcD6Joint{});
        dcJoint->ctx = this;
        dcJoint->pxJoint = joint;
        dcJoint->path = usdPath;
        DcD6Joint* jointPtr = dcJoint.get();
        DcHandle jointHandle = addD6Joint(std::move(dcJoint), usdPath);
        jointPtr->handle = jointHandle;
        return jointHandle;
    }
    else
    {
        // not supported yet
        return kDcInvalidHandle;
    }
}


}
}
}
