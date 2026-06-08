#include "QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"

namespace
{
const TCHAR* RuntimeEchoReceiverSurfaceBoundary =
    TEXT("source_static_runtime_echo_receiver_surface: accepts only future authoritative mosim.ue_command_echo.v1 downlink JSON through UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent; no socket, listener, timer, thread, background loop, pose control, or runtime ack claim is started by this component.");
}

UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::ValidateAuthoritativeRuntimeCommandEchoDownlinkJson(
    const FString& EchoJson,
    UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent* CommandEchoReceiver,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (!CommandEchoReceiver)
    {
        RejectReason = TEXT("missing_command_echo_receiver");
        return false;
    }

    return CommandEchoReceiver->IsAuthoritativeRuntimeCommandEchoPacketJson(EchoJson, RejectReason);
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::IngestAuthoritativeRuntimeCommandEchoDownlinkJson(
    const FString& EchoJson,
    UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent* CommandEchoReceiver,
    UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
    FQuadrotorMworksExperimentConsoleCommandState& OutState,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (!CommandEchoReceiver)
    {
        RejectReason = TEXT("missing_command_echo_receiver");
        return false;
    }

    if (!StateComponent)
    {
        RejectReason = TEXT("missing_state_component");
        return false;
    }

    return CommandEchoReceiver->ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState(
        EchoJson,
        StateComponent,
        OutState,
        RejectReason);
}

FString UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::GetSourceStaticReceiverBoundary() const
{
    return RuntimeEchoReceiverSurfaceBoundary;
}
