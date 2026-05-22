// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include "isaacsim/core/includes/UsdUtilities.h"

#include <isaacsim/sensors/physics/IPhysicsSensor.h>
#include <omni/fabric/FabricUSD.h>

#include <OgnIsaacReadContactSensorDatabase.h>


namespace isaacsim
{
namespace sensors
{
namespace physics
{

class OgnIsaacReadContactSensor
{
public:
    static void initInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        auto& state =
            OgnIsaacReadContactSensorDatabase::sPerInstanceState<OgnIsaacReadContactSensor>(nodeObj, instanceId);

        state.m_contactSensorInterface = carb::getCachedInterface<ContactSensorInterface>();

        if (!state.m_contactSensorInterface)
        {
            CARB_LOG_ERROR("Failed to acquire isaacsim::sensors::physics interface");
            return;
        }
    }

    static bool compute(OgnIsaacReadContactSensorDatabase& db)
    {
        auto& state = db.perInstanceState<OgnIsaacReadContactSensor>();

        const auto& prim = db.inputs.csPrim();
        const char* primPath;

        auto& inContact = db.outputs.inContact();
        auto& value = db.outputs.value();
        auto& sensorTime = db.outputs.sensorTime();

        if (!prim.empty())
        {
            primPath = omni::fabric::toSdfPath(prim[0]).GetText();
        }
        else
        {
            inContact = false;
            value = 0;
            sensorTime = 0.0f;
            db.logError("Invalid contact sensor prim");
            return false;
        }

        CsReading sensorReading = state.m_contactSensorInterface->getSensorReading(primPath, db.inputs.useLatestData());

        if (sensorReading.isValid)
        {
            inContact = sensorReading.inContact;
            value = sensorReading.value;
            sensorTime = sensorReading.time;
        }
        else
        {
            inContact = false;
            value = 0;
            sensorTime = 0.0f;
            db.logWarning("no valid sensor reading, is the sensor enabled?");
            db.outputs.execOut() = kExecutionAttributeStateDisabled;
            return false;
        }
        db.outputs.execOut() = kExecutionAttributeStateEnabled;
        return true;
    }

private:
    ContactSensorInterface* m_contactSensorInterface = nullptr;
};


REGISTER_OGN_NODE()
} // sensor
} // graph
} // omni
