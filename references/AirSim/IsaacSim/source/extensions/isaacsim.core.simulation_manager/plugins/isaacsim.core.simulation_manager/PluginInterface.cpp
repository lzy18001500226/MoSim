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

#include <carb/PluginUtils.h>
#include <carb/eventdispatcher/IEventDispatcher.h>
#include <carb/events/EventsUtils.h>

#include <isaacsim/core/simulation_manager/ISimulationManager.h>
#include <isaacsim/core/simulation_manager/TimeSampleStorage.h>
#include <isaacsim/core/simulation_manager/UsdNoticeListener.h>
#include <omni/ext/IExt.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/SimStageWithHistory.h>
#include <omni/graph/core/Type.h>
#include <omni/kit/IMinimal.h>
#include <omni/kit/IStageUpdate.h>
#include <omni/physx/IPhysx.h>
#include <omni/usd/UsdContext.h>

#if defined(_WIN32)
#    include <usdrt/scenegraph/usd/usd/stage.h>
#else
#    pragma GCC diagnostic push
#    pragma GCC diagnostic ignored "-Wunused-variable"
#    include <usdrt/scenegraph/usd/usd/stage.h>
#    pragma GCC diagnostic pop
#endif

#include <algorithm>
#include <chrono>
#include <memory>

/**
 * @brief Plugin descriptor for the simulation manager plugin.
 * @details Defines the plugin's name, description, author, hot reload capability, and version.
 */
const struct carb::PluginImplDesc g_kPluginDesc = { "isaacsim.core.simulation_manager.plugin",
                                                    "Helpful text describing the plugin", "Author",
                                                    carb::PluginHotReload::eEnabled, "dev" };

namespace
{
omni::physx::IPhysx* g_physXInterface = nullptr;
omni::physx::SubscriptionId g_physicsOnStepSubscription;
carb::events::ISubscriptionPtr g_physicsEventSubscription;
omni::kit::StageUpdatePtr g_stageUpdate = nullptr;

omni::fabric::UsdStageId g_stageId;
double g_simulationTime = 0.0;
double g_simulationTimeMonotonic = 0.0;
double g_systemTime = 0.0;
size_t g_numPhysicsSteps = 0;
bool g_simulating = false;
bool g_paused = false;

/** @brief Global time storage instance for simulation time data */
std::unique_ptr<isaacsim::core::simulation_manager::TimeSampleStorage> g_timeStorage = nullptr;
}

namespace isaacsim
{
namespace core
{
namespace simulation_manager
{

/**
 * @class SimulationManagerImpl
 * @brief Implementation of the ISimulationManager interface.
 * @details
 * Provides functionality for managing simulation-related events and callbacks.
 * Handles USD notices and maintains callback registrations for physics scene additions
 * and deletion events.
 */
class SimulationManagerImpl : public ISimulationManager
{
public:
    /**
     * @brief Constructor for SimulationManagerImpl.
     * @details
     * Initializes the USD notice listener and registers it to handle USD notices.
     */
    SimulationManagerImpl() : m_usdNoticeListener(std::make_unique<UsdNoticeListener>())
    {
        m_usdNoticeListenerKey =
            pxr::TfNotice::Register(pxr::TfCreateWeakPtr(m_usdNoticeListener.get()), &UsdNoticeListener::handle);
        auto ed = carb::getCachedInterface<carb::eventdispatcher::IEventDispatcher>();
        const static carb::RStringKey name("IsaacSimStageOpenedUsdNoticeListener");
        auto usdContext = omni::usd::UsdContext::getContext();
        m_stageEventSubscription = ed->observeEvent(
            name, 1000, usdContext->stageEventName(omni::usd::StageEventType::eOpened),
            [this, usdContext](const auto&)
            {
                auto stage = usdContext->getStage();
                PXR_NS::UsdStageCache& cache = PXR_NS::UsdUtilsStageCache::Get();
                omni::fabric::UsdStageId stageId = { static_cast<uint64_t>(cache.GetId(stage).ToLongInt()) };
                omni::fabric::IStageReaderWriter* iStageReaderWriter =
                    carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
                omni::fabric::StageReaderWriterId stageInProgress = iStageReaderWriter->get(stageId);
                usdrt::UsdStageRefPtr usdrtStage = usdrt::UsdStage::Attach(stageId, stageInProgress);
                for (auto& usdrtPath : usdrtStage->GetPrimsWithTypeName(usdrt::TfToken("UsdPhysicsScene")))
                {
                    const omni::fabric::PathC pathC(usdrtPath);
                    const pxr::SdfPath primPath = omni::fabric::toSdfPath(pathC);
                    pxr::UsdPrim prim = stage->GetPrimAtPath(primPath);
                    if (m_usdNoticeListener->getPhysicsScenes().count(primPath) == 0)
                    {
                        m_usdNoticeListener->getPhysicsScenes().emplace(
                            primPath, pxr::PhysxSchemaPhysxSceneAPI::Apply(prim));
                        for (auto const& [key, AdditionFunc] : m_usdNoticeListener->getPhysicsSceneAdditionCallbacks())
                        {
                            (void)key;
                            AdditionFunc(primPath.GetString());
                        }
                    }
                }
            });
    }

    /**
     * @brief Destructor for SimulationManagerImpl.
     * @details
     * Cleans up the USD notice listener.
     */
    ~SimulationManagerImpl()
    {
        m_usdNoticeListener.reset();
        m_stageEventSubscription.reset();
    }

    /**
     * @brief Registers a callback function to be called when an object is deleted.
     * @details
     * The callback will be invoked with the path of the deleted object as a parameter.
     *
     * @param[in] callback Function to be called when an object is deleted.
     * @return Unique identifier for the registered callback.
     */
    int registerDeletionCallback(const std::function<void(std::string)>& callback) override
    {
        int& callbackIter = m_usdNoticeListener->getCallbackIter();
        m_usdNoticeListener->getDeletionCallbacks().emplace(callbackIter, callback);
        callbackIter += 1;
        return callbackIter - 1;
    }

    /**
     * @brief Registers a callback function to be called when a physics scene is added.
     * @details
     * The callback will be invoked with the path of the added physics scene as a parameter.
     *
     * @param[in] callback Function to be called when a physics scene is added.
     * @return Unique identifier for the registered callback.
     */
    int registerPhysicsSceneAdditionCallback(const std::function<void(std::string)>& callback) override
    {
        int& callbackIter = m_usdNoticeListener->getCallbackIter();
        m_usdNoticeListener->getPhysicsSceneAdditionCallbacks().emplace(callbackIter, callback);
        callbackIter += 1;
        return callbackIter - 1;
    }

    /**
     * @brief Deregisters a previously registered callback.
     * @details
     * Removes a callback from either the physics scene addition callbacks or deletion callbacks
     * based on the provided callback ID.
     *
     * @param[in] callbackId The unique identifier of the callback to deregister.
     * @return True if the callback was successfully deregistered, false otherwise.
     */
    bool deregisterCallback(const int& callbackId) override
    {
        std::map<int, std::function<void(const std::string&)>>& physicsSceneCallbacks =
            m_usdNoticeListener->getPhysicsSceneAdditionCallbacks();
        std::map<int, std::function<void(const std::string&)>>& deletiomCallbacks =
            m_usdNoticeListener->getDeletionCallbacks();
        if (physicsSceneCallbacks.count(callbackId) > 0)
        {
            physicsSceneCallbacks.erase(callbackId);
            return true;
        }
        else if (deletiomCallbacks.count(callbackId) > 0)
        {
            deletiomCallbacks.erase(callbackId);
            return true;
        }
        return false;
    }

    /**
     * @brief Gets the current callback iterator value.
     * @details
     * This value is used to generate unique identifiers for callbacks.
     *
     * @return Reference to the current callback iterator.
     */
    int& getCallbackIter() override
    {
        return m_usdNoticeListener->getCallbackIter();
    }

    /**
     * @brief Sets the callback iterator to a specific value.
     * @details
     * Allows manual control over the callback identifier generation.
     *
     * @param[in] val The value to set the callback iterator to.
     */
    void setCallbackIter(int const& val) override
    {
        int& callbackIter = m_usdNoticeListener->getCallbackIter();
        callbackIter = val;
    }

    /**
     * @brief Gets the current simulation time.
     * @details
     * Returns the current simulation time.
     *
     * @return The current simulation time.
     */
    double getSimulationTime() override
    {
        return g_simulationTime;
    }

    /**
     * @brief Gets the current simulation time.
     * @details
     * Returns the current simulation time which does not reset when the simulation is stopped.
     *
     * @return The current simulation time.
     */
    double getSimulationTimeMonotonic() override
    {
        return g_simulationTimeMonotonic;
    }

    /**
     * @brief Gets the current system time.
     * @details
     * Returns the current system time.
     *
     * @return The current system time.
     */
    double getSystemTime() override
    {
        return g_systemTime;
    }

    /**
     * @brief Gets the current frame time from best available source.
     * @details
     * Returns the current frame time using the same priority order as TimeSampleStorage.
     * This is useful for testing to track exact frame times being written to storage.
     *
     * @return Current rational time or kInvalidRationalTime if unavailable.
     */
    omni::fabric::RationalTime getCurrentTime() override
    {
        if (!g_timeStorage)
        {
            CARB_LOG_WARN("getCurrentTime: time storage not initialized");
            return omni::fabric::kInvalidRationalTime;
        }

        return g_timeStorage->getCurrentTime();
    }

    /**
     * @brief Enables or disables the USD notice handler.
     * @details
     * Controls whether USD notices are processed by the notice listener.
     *
     * @param[in] flag True to enable the handler, false to disable it.
     */
    void enableUsdNoticeHandler(bool const& flag) override
    {
        m_usdNoticeListener->enable(flag);
    }

    /**
     * @brief Enables or disables the Fabric USD notice handler for a specific stage.
     * @details
     * Controls whether Fabric USD notices are processed for the specified stage.
     * If enabled, forces a minimal populate of the Fabric USD.
     *
     * @param[in] stageId The ID of the stage to configure.
     * @param[in] flag True to enable the handler, false to disable it.
     */
    void enableFabricUsdNoticeHandler(long stageId, bool const& flag) override
    {
        auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
        auto iStageReadWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        if (iFabricUsd && iStageReadWriter)
        {
            omni::fabric::StageReaderWriterId stageRwId = iStageReadWriter->get(stageId);
            if (stageRwId.id)
            {
                auto fabricId = iStageReadWriter->getFabricId(stageRwId);
                iFabricUsd->setEnableChangeNotifies(fabricId, flag);
                if (flag)
                {
                    CARB_PROFILE_ZONE(0, "[IsaacSim] EnableFabricUsdNoticeHandler::forceMinulaPopulate");
                    iFabricUsd->forceMinimalPopulate(fabricId);
                }
            }
        }
    }

    /**
     * @brief Checks if the Fabric USD notice handler is enabled for a specific stage.
     * @details
     * Determines whether Fabric USD notices are being processed for the specified stage.
     *
     * @param[in] stageId The ID of the stage to check.
     * @return True if the notice handler is enabled, false otherwise.
     */
    bool isFabricUsdNoticeHandlerEnabled(long stageId) override
    {
        auto iFabricUsd = carb::getCachedInterface<omni::fabric::IFabricUsd>();
        auto iStageReadWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        if (iFabricUsd && iStageReadWriter)
        {
            omni::fabric::StageReaderWriterId stageRwId = iStageReadWriter->get(stageId);
            if (stageRwId.id)
            {
                auto fabricId = iStageReadWriter->getFabricId(stageRwId);
                return iFabricUsd->getEnableChangeNotifies(fabricId);
            }
            else
            {
                return false;
            }
        }
        else
        {
            return false;
        }
    }

    /**
     * @brief Gets the current physics step count.
     * @details
     * Returns the current physics step count.
     *
     * @return The current physics step count.
     */
    size_t getNumPhysicsSteps() override
    {
        return g_numPhysicsSteps;
    }

    /**
     * @brief Gets the current simulation pause state.
     * @details
     * Returns the current simulation pause state.
     *
     * @return The current simulation pause state.
     */
    bool isSimulating() override
    {
        return g_simulating;
    }

    /**
     * @brief Gets the current simulation pause state.
     * @details
     * Returns the current simulation pause state.
     *
     * @return The current simulation pause state.
     */
    bool isPaused() override
    {
        return g_paused;
    }


    /**
     * @brief Resets the simulation manager.
     * @details
     * Calls all registered deletion callbacks with a root path ("/"),
     * clears all registered callbacks, clears the physics scenes list,
     * and resets the callback iterator to 0.
     */
    void reset() override
    {
        std::vector<int> deletionKeys;
        auto deletionCallbacksMap = m_usdNoticeListener->getDeletionCallbacks();
        std::transform(deletionCallbacksMap.begin(), deletionCallbacksMap.end(), std::back_inserter(deletionKeys),
                       [](const auto& p) { return p.first; });
        for (auto const& key : deletionKeys)
        {
            deletionCallbacksMap[key]("/");
        }
        m_usdNoticeListener->getDeletionCallbacks().clear();
        m_usdNoticeListener->getPhysicsSceneAdditionCallbacks().clear();
        m_usdNoticeListener->getPhysicsScenes().clear();
        int& callbackIter = m_usdNoticeListener->getCallbackIter();
        callbackIter = 0;
    }


    double getSimulationTimeAtTime(const omni::fabric::RationalTime& rtime) override
    {
        // If no samples are stored, return the current simulation time
        if (!g_timeStorage || g_timeStorage->getSampleCount() == 0)
        {
            return g_simulationTime;
        }

        auto result = g_timeStorage->getSimulationTimeAt(rtime);
        if (result.has_value())
        {
            return result.value();
        }
        else
        {
            CARB_LOG_INFO("getSimulationTimeAtTime: no data found for time %s, returning current sim time",
                          rtime.toString().c_str());
            return g_simulationTime;
        }
    }


    double getSimulationTimeMonotonicAtTime(const omni::fabric::RationalTime& rtime) override
    {
        // If no samples are stored, return the current simulation time
        if (!g_timeStorage || g_timeStorage->getSampleCount() == 0)
        {
            return g_simulationTimeMonotonic;
        }

        auto result = g_timeStorage->getMonotonicSimulationTimeAt(rtime);
        if (result.has_value())
        {
            return result.value();
        }
        else
        {
            CARB_LOG_WARN("getSimulationTimeMonotonicAtTime: no data found for time %s, returning current sim time",
                          rtime.toString().c_str());
            return g_simulationTimeMonotonic;
        }
    }

    double getSystemTimeAtTime(const omni::fabric::RationalTime& rtime) override
    {
        // If no samples are stored, return the current system time
        if (!g_timeStorage || g_timeStorage->getSampleCount() == 0)
        {
            return g_systemTime;
        }

        auto result = g_timeStorage->getSystemTimeAt(rtime);
        if (result.has_value())
        {
            return result.value();
        }
        else
        {
            CARB_LOG_WARN("getSystemTimeAtTime: no data found for time %s, returning current system time",
                          rtime.toString().c_str());
            return g_systemTime;
        }
    }

    std::vector<TimeSampleStorage::Entry> getAllSamples() override
    {
        if (!g_timeStorage)
        {
            return std::vector<TimeSampleStorage::Entry>();
        }

        return g_timeStorage->getAllSamples();
    }

    size_t getSampleCount() override
    {
        return g_timeStorage ? g_timeStorage->getSampleCount() : 0;
    }

    void logStatistics() override
    {
        if (g_timeStorage)
        {
            g_timeStorage->logStatistics();
        }
    }

    std::optional<std::pair<omni::fabric::RationalTime, omni::fabric::RationalTime>> getSampleRange() override
    {
        if (!g_timeStorage || g_timeStorage->getSampleCount() == 0)
        {
            return std::nullopt;
        }

        return g_timeStorage->getSampleRange();
    }

    size_t getBufferCapacity() override
    {
        return TimeSampleStorage::getBufferCapacity();
    }

private:
    /**
     * @brief USD notice listener object that handles USD notices.
     */
    std::unique_ptr<UsdNoticeListener> m_usdNoticeListener;

    /**
     * @brief Key for the registered USD notice listener.
     */
    pxr::TfNotice::Key m_usdNoticeListenerKey;

    /**
     * @brief Subscription for stage opened events.
     */
    carb::eventdispatcher::ObserverGuard m_stageEventSubscription;
};

/**
 * @brief Callback function for resume events
 * @details
 * Writes initial time data when simulation resumes.
 *
 * @param[in] currentTime The current time
 * @param[in] userData User data pointer
 */
void onResume(float currentTime, void* userData)
{
    // Only write initial time data if storage exists
    if (g_timeStorage)
    {
        g_timeStorage->storeSample(g_simulationTime, g_simulationTimeMonotonic, g_systemTime);
        CARB_LOG_INFO("onResume: Stored initial time data");
    }
    else
    {
        CARB_LOG_WARN("onResume: Time storage not available");
    }
}

/**
 * @brief Callback function for physics step events
 * @details
 * Updates simulation time values and writes them to time storage on each physics step.
 *
 * @param[in] timeElapsed The elapsed time since the last physics step
 * @param[in] userData User data pointer
 */
void onPhysicsStep(float timeElapsed, void* userData)
{
    g_simulationTime += timeElapsed;
    g_simulationTimeMonotonic += timeElapsed;
    g_numPhysicsSteps += 1;
    g_systemTime = std::chrono::duration<double>(std::chrono::system_clock::now().time_since_epoch()).count();
    g_simulating = true;

    if (!g_timeStorage)
    {
        CARB_LOG_INFO("onPhysicsStep: time storage not initialized, initializing");
        g_timeStorage = std::make_unique<isaacsim::core::simulation_manager::TimeSampleStorage>(g_stageId);
        return;
    }

    // Write time data to storage
    bool success = g_timeStorage->storeSample(g_simulationTime, g_simulationTimeMonotonic, g_systemTime);
    if (!success)
    {
        CARB_LOG_ERROR("Failed to write time data to storage");
    }
}

/**
 * @brief Callback function for stop events
 * @details
 * Clears stored time samples but keeps the storage object alive when simulation stops.
 *
 * @param[in] userData User data pointer
 */
void onStop(void* userData)
{
    // Clear time samples but keep storage object alive
    if (g_timeStorage)
    {
        g_timeStorage->clear();
        CARB_LOG_INFO("onStop: Cleared time samples");
    }

    // Reset simulation state
    g_simulationTime = 0;
    g_numPhysicsSteps = 0;
}

/**
 * @brief Callback function for stage attach events
 * @details
 * Initializes time storage and resets simulation state when a new stage is attached.
 *
 * @param[in] stageId The ID of the stage
 * @param[in] metersPerUnit The meters per unit scale of the stage
 * @param[in] userData User data pointer
 */
void onAttach(long int stageId, double metersPerUnit, void* userData)
{
    // Reset simulation state
    g_simulationTime = 0;
    g_numPhysicsSteps = 0;

    // Find the USD stage to validate it exists
    pxr::UsdStageWeakPtr stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
    if (!stage)
    {
        CARB_LOG_ERROR("Isaac Core Simulation Manager could not find USD stage");
        return;
    }
    g_stageId.id = stageId;

    // Initialize time storage for this stage
    g_timeStorage = std::make_unique<isaacsim::core::simulation_manager::TimeSampleStorage>(g_stageId);
}

/**
 * @brief Callback function for stage detach events
 * @details
 * Cleans up time storage when a stage is detached.
 *
 * @param[in] stageId The ID of the stage being detached
 * @param[in] metersPerUnit The meters per unit scale of the stage
 * @param[in] userData User data pointer
 */
void onDetach(void* userData)
{
    // Clean up time storage
    if (g_timeStorage)
    {
        g_timeStorage.reset();
    }

    // Clear stage reference
    g_stageId = omni::fabric::UsdStageId();
}


/**
 * @class Extension
 * @brief Implementation of the IExt interface for the simulation manager extension.
 * @details
 * Provides lifecycle management for the simulation manager extension.
 */
class Extension : public omni::ext::IExt
{
public:
    /**
     * @brief Method called when the extension is loaded/enabled.
     * @details
     * Initializes the extension when it is loaded.
     *
     * @param[in] extId The ID of the extension being loaded.
     */
    void onStartup(const char* extId) override
    {
        // TODO: in case there is more than one physics scene which one is returned?
        g_physXInterface = carb::getCachedInterface<omni::physx::IPhysx>();
        g_physicsOnStepSubscription = g_physXInterface->subscribePhysicsOnStepEvents(false, 0, onPhysicsStep, nullptr);
        g_systemTime = std::chrono::duration<double>(std::chrono::system_clock::now().time_since_epoch()).count();
        g_simulationTime = 0;
        g_simulationTimeMonotonic = 0;
        g_numPhysicsSteps = 0;

        g_physicsEventSubscription = carb::events::createSubscriptionToPop(
            g_physXInterface->getSimulationEventStreamV2().get(),
            [](carb::events::IEvent* e)
            {
                if (e->type == omni::physx::SimulationEvent::eStopped)
                {
                    g_simulating = false;
                    g_paused = false;
                }
                else if (e->type == omni::physx::SimulationEvent::ePaused)
                {
                    g_paused = true;
                }
                else if (e->type == omni::physx::SimulationEvent::eResumed)
                {
                    g_simulating = true;
                    g_paused = false;
                }
            },
            0, "IsaacSim.Core.SimulationManager.SimulationEvent");

        g_stageUpdate = carb::getCachedInterface<omni::kit::IStageUpdate>()->getStageUpdate();

        omni::kit::StageUpdateNodeDesc desc = { 0 };
        desc.displayName = "Isaac Simulation Manager";
        desc.onStop = onStop;
        desc.onAttach = onAttach;
        desc.onDetach = onDetach;
        desc.onResume = onResume;
        g_stageUpdate->createStageUpdateNode(desc);
    }

    /**
     * @brief Method called when the extension is disabled.
     * @details
     * Cleans up the extension when it is disabled.
     */
    void onShutdown() override
    {
    }
};

} // namespace isaacsim
} // namespace core
} // namespace simulation_manager

/**
 * @brief Optional function called the first time an interface is acquired from the plugin library.
 * @details
 * This function is invoked by the Carbonite framework when the plugin is first loaded.
 */
CARB_EXPORT void carbOnPluginStartup()
{
}

/**
 * @brief Optional function called right before the OS releases the plugin library.
 * @details
 * This function is invoked by the Carbonite framework when the plugin is about to be unloaded.
 */
CARB_EXPORT void carbOnPluginShutdown()
{
}

/**
 * @brief Implements the plugin with the specified simulation manager and extension implementations.
 * @details
 * Registers the plugin with the Carbonite framework.
 */
CARB_PLUGIN_IMPL(g_kPluginDesc,
                 isaacsim::core::simulation_manager::SimulationManagerImpl,
                 isaacsim::core::simulation_manager::Extension)

/**
 * @brief Fills the interface for the simulation manager implementation.
 * @details
 * This function is called by the Carbonite framework to initialize the interface.
 *
 * @param[in,out] iface The interface to fill.
 */
void fillInterface(isaacsim::core::simulation_manager::SimulationManagerImpl& iface)
{
}

/**
 * @brief Fills the interface for the extension implementation.
 * @details
 * This function is called by the Carbonite framework to initialize the interface.
 *
 * @param[in,out] iface The interface to fill.
 */
void fillInterface(isaacsim::core::simulation_manager::Extension& iface)
{
}
