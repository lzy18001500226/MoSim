#include "QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"

#include "Dom/JsonObject.h"
#include "Json.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const TCHAR* CommandEchoSchema = TEXT("mosim.ue_command_echo.v1");

TSharedPtr<FJsonObject> ParseJsonObject(const FString& PayloadJson)
{
    TSharedPtr<FJsonObject> JsonObject;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(PayloadJson);
    if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
    {
        return nullptr;
    }
    return JsonObject;
}

FString GetStringField(const TSharedPtr<FJsonObject>& Object, const FString& FieldName)
{
    FString Value;
    if (Object.IsValid())
    {
        Object->TryGetStringField(FieldName, Value);
    }
    return Value;
}

bool HasNumberField(const TSharedPtr<FJsonObject>& Object, const FString& FieldName)
{
    double Value = 0.0;
    return Object.IsValid() && Object->TryGetNumberField(FieldName, Value);
}

FString GetCommandKind(const TSharedPtr<FJsonObject>& Object)
{
    FString CommandKind = GetStringField(Object, TEXT("command_kind"));
    if (!CommandKind.IsEmpty())
    {
        return CommandKind;
    }

    const TSharedPtr<FJsonObject>* CommandObject = nullptr;
    if (Object.IsValid() && Object->TryGetObjectField(TEXT("command"), CommandObject) && CommandObject && CommandObject->IsValid())
    {
        (*CommandObject)->TryGetStringField(TEXT("kind"), CommandKind);
    }
    return CommandKind;
}

bool IsEchoStatus(const FString& Status)
{
    return Status == TEXT("accepted") || Status == TEXT("rejected");
}

bool IsForbiddenCommandKind(const FString& CommandKind)
{
    return CommandKind == TEXT("pose_override")
        || CommandKind == TEXT("teleport")
        || CommandKind == TEXT("set_uav_pose")
        || CommandKind == TEXT("actor_transform")
        || CommandKind == TEXT("keyboard_pose");
}

bool IsAuthoritativeLiveEchoSource(const FString& Source, const FString& AckAuthority)
{
    return (Source == TEXT("MWORKS_live_downlink") && AckAuthority == TEXT("MWORKS"))
        || (Source == TEXT("ROS2_runtime_echo") && AckAuthority == TEXT("ROS2"))
        || (Source == TEXT("MWORKS_ROS2_live_downlink") && AckAuthority == TEXT("MWORKS_ROS2"));
}
}

UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::IsCommandEchoPacketJson(
    const FString& EchoJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    const TSharedPtr<FJsonObject> EchoObject = ParseJsonObject(EchoJson);
    if (!EchoObject.IsValid())
    {
        RejectReason = TEXT("invalid_echo_json");
        return false;
    }

    if (GetStringField(EchoObject, TEXT("schema")) != CommandEchoSchema)
    {
        RejectReason = TEXT("unsupported_echo_schema");
        return false;
    }

    return true;
}

bool UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::IsAuthoritativeRuntimeCommandEchoPacketJson(
    const FString& EchoJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    const TSharedPtr<FJsonObject> EchoObject = ParseJsonObject(EchoJson);
    if (!EchoObject.IsValid())
    {
        RejectReason = TEXT("invalid_echo_json");
        return false;
    }

    if (GetStringField(EchoObject, TEXT("schema")) != CommandEchoSchema)
    {
        RejectReason = TEXT("unsupported_echo_schema");
        return false;
    }

    const FString Status = GetStringField(EchoObject, TEXT("status"));
    if (!IsEchoStatus(Status))
    {
        RejectReason = TEXT("unsupported_echo_status");
        return false;
    }

    if (GetStringField(EchoObject, TEXT("run_id")).IsEmpty() || GetStringField(EchoObject, TEXT("request_id")).IsEmpty())
    {
        RejectReason = TEXT("missing_run_id_or_request_id");
        return false;
    }

    if (!HasNumberField(EchoObject, TEXT("seq")))
    {
        RejectReason = TEXT("missing_seq");
        return false;
    }

    if (!HasNumberField(EchoObject, TEXT("time_s")))
    {
        RejectReason = TEXT("missing_timestamp");
        return false;
    }

    const FString CommandKind = GetCommandKind(EchoObject);
    if (CommandKind.IsEmpty())
    {
        RejectReason = TEXT("missing_command_kind");
        return false;
    }

    if (IsForbiddenCommandKind(CommandKind))
    {
        RejectReason = TEXT("forbidden_pose_command");
        return false;
    }

    const FString NoPoseOverwriteStatus = GetStringField(EchoObject, TEXT("no_pose_overwrite_status"));
    if (NoPoseOverwriteStatus != TEXT("pass"))
    {
        RejectReason = TEXT("no_pose_overwrite_not_pass");
        return false;
    }

    const FString EchoSource = GetStringField(EchoObject, TEXT("source"));
    const FString AckAuthority = GetStringField(EchoObject, TEXT("ack_authority"));
    if (!IsAuthoritativeLiveEchoSource(EchoSource, AckAuthority))
    {
        RejectReason = TEXT("source_authority_mismatch");
        return false;
    }

    return true;
}

bool UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::ApplyCommandEchoJsonToState(
    const FString& EchoJson,
    UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
    FQuadrotorMworksExperimentConsoleCommandState& OutState,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (!StateComponent)
    {
        RejectReason = TEXT("missing_state_component");
        return false;
    }

    if (!IsCommandEchoPacketJson(EchoJson, RejectReason))
    {
        return false;
    }

    return StateComponent->ApplyCommandEchoJson(EchoJson, OutState, RejectReason);
}

bool UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState(
    const FString& EchoJson,
    UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
    FQuadrotorMworksExperimentConsoleCommandState& OutState,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (!StateComponent)
    {
        RejectReason = TEXT("missing_state_component");
        return false;
    }

    if (!IsAuthoritativeRuntimeCommandEchoPacketJson(EchoJson, RejectReason))
    {
        return false;
    }

    return StateComponent->ApplyCommandEchoJson(EchoJson, OutState, RejectReason);
}
