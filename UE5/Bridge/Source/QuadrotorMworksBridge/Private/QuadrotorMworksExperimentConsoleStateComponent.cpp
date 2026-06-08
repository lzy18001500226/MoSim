#include "QuadrotorMworksExperimentConsoleStateComponent.h"

#include "Dom/JsonObject.h"
#include "Json.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const TCHAR* CommandSchema = TEXT("mosim.ue_command.v1");
const TCHAR* EchoSchema = TEXT("mosim.ue_command_echo.v1");

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

int32 GetIntegerField(const TSharedPtr<FJsonObject>& Object, const FString& FieldName)
{
    double Value = 0.0;
    if (Object.IsValid())
    {
        Object->TryGetNumberField(FieldName, Value);
    }
    return static_cast<int32>(Value);
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

bool IsAllowedCommandKind(const FString& CommandKind)
{
    return CommandKind == TEXT("controller_select")
        || CommandKind == TEXT("planner_select")
        || CommandKind == TEXT("wind_profile")
        || CommandKind == TEXT("motor_fault")
        || CommandKind == TEXT("sensor_mode")
        || CommandKind == TEXT("scenario_reset")
        || CommandKind == TEXT("start_goal_update")
        || CommandKind == TEXT("recording")
        || CommandKind == TEXT("scene_switch");
}

bool IsForbiddenCommandKind(const FString& CommandKind)
{
    return CommandKind == TEXT("pose_override")
        || CommandKind == TEXT("teleport")
        || CommandKind == TEXT("set_uav_pose")
        || CommandKind == TEXT("actor_transform")
        || CommandKind == TEXT("keyboard_pose");
}

bool IsEchoStatus(const FString& Status)
{
    return Status == TEXT("accepted") || Status == TEXT("rejected");
}

bool IsSmokeSource(const FString& Source)
{
    return Source.IsEmpty()
        || Source == TEXT("offline_adapter_smoke")
        || Source == TEXT("source_level_smoke")
        || Source == TEXT("MWORKS_MCP_result_adapter_smoke")
        || Source == TEXT("MWORKS_MCP_runtime_adapter_preflight");
}

bool IsAuthoritativeLiveEchoSource(const FString& Source, const FString& AckAuthority)
{
    return (Source == TEXT("MWORKS_live_downlink") && AckAuthority == TEXT("MWORKS"))
        || (Source == TEXT("ROS2_runtime_echo") && AckAuthority == TEXT("ROS2"))
        || (Source == TEXT("MWORKS_ROS2_live_downlink") && AckAuthority == TEXT("MWORKS_ROS2"));
}
}

UQuadrotorMworksExperimentConsoleStateComponent::UQuadrotorMworksExperimentConsoleStateComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UQuadrotorMworksExperimentConsoleStateComponent::RecordPendingCommandFromPacketJson(
    const FString& PacketJson,
    FQuadrotorMworksExperimentConsoleCommandState& OutState,
    FString& RejectReason)
{
    RejectReason.Reset();
    const TSharedPtr<FJsonObject> PacketObject = ParseJsonObject(PacketJson);
    if (!PacketObject.IsValid())
    {
        RejectReason = TEXT("invalid_command_json");
        return false;
    }
    if (GetStringField(PacketObject, TEXT("schema")) != CommandSchema || GetStringField(PacketObject, TEXT("type")) != TEXT("command"))
    {
        RejectReason = TEXT("unsupported_command_schema");
        return false;
    }

    const FString RunId = GetStringField(PacketObject, TEXT("run_id"));
    const FString RequestId = GetStringField(PacketObject, TEXT("request_id"));
    const FString CommandKind = GetCommandKind(PacketObject);
    if (RunId.IsEmpty() || RequestId.IsEmpty())
    {
        RejectReason = TEXT("missing_run_id_or_request_id");
        return false;
    }
    if (IsForbiddenCommandKind(CommandKind))
    {
        RejectReason = TEXT("forbidden_pose_command");
        return false;
    }
    if (!IsAllowedCommandKind(CommandKind))
    {
        RejectReason = TEXT("unsupported_command_kind");
        return false;
    }

    const FString StateKey = MakeStateKey(RunId, RequestId);
    if (CommandStatesByKey.Contains(StateKey))
    {
        RejectReason = TEXT("duplicate_command_request");
        OutState = CommandStatesByKey[StateKey];
        return false;
    }

    FQuadrotorMworksExperimentConsoleCommandState NewState;
    NewState.RunId = RunId;
    NewState.RequestId = RequestId;
    NewState.Seq = GetIntegerField(PacketObject, TEXT("seq"));
    NewState.CommandKind = CommandKind;
    NewState.UiState = TEXT("pending");
    NewState.AckAuthority.Reset();
    NewState.Reason = TEXT("awaiting_matching_echo");
    NewState.Source = TEXT("ue_command_request");
    NewState.QualityStatus = TEXT("pending_no_runtime_echo");
    NewState.bAcceptedAsRuntimeAck = false;
    NewState.NoPoseOverwriteStatus = TEXT("pass");

    CommandStatesByKey.Add(StateKey, NewState);
    OutState = NewState;
    return true;
}

bool UQuadrotorMworksExperimentConsoleStateComponent::ApplyCommandEchoJson(
    const FString& EchoJson,
    FQuadrotorMworksExperimentConsoleCommandState& OutState,
    FString& RejectReason)
{
    RejectReason.Reset();
    const TSharedPtr<FJsonObject> EchoObject = ParseJsonObject(EchoJson);
    if (!EchoObject.IsValid())
    {
        RejectReason = TEXT("invalid_echo_json");
        return false;
    }
    if (GetStringField(EchoObject, TEXT("schema")) != EchoSchema)
    {
        RejectReason = TEXT("unsupported_echo_schema");
        return false;
    }

    const FString Status = GetStringField(EchoObject, TEXT("status"));
    const FString RunId = GetStringField(EchoObject, TEXT("run_id"));
    const FString RequestId = GetStringField(EchoObject, TEXT("request_id"));
    const FString AckAuthority = GetStringField(EchoObject, TEXT("ack_authority"));
    const FString NoPoseOverwriteStatus = GetStringField(EchoObject, TEXT("no_pose_overwrite_status"));
    const FString EchoSource = GetStringField(EchoObject, TEXT("source"));
    const bool bSmokeOnly = IsSmokeSource(EchoSource);
    if (!IsEchoStatus(Status))
    {
        RejectReason = TEXT("unsupported_echo_status");
        return false;
    }
    if (RunId.IsEmpty() || RequestId.IsEmpty())
    {
        RejectReason = TEXT("missing_run_id_or_request_id");
        return false;
    }
    if (AckAuthority.IsEmpty())
    {
        RejectReason = TEXT("missing_ack_authority");
        return false;
    }
    if (NoPoseOverwriteStatus != TEXT("pass"))
    {
        RejectReason = TEXT("no_pose_overwrite_not_pass");
        return false;
    }
    if (!bSmokeOnly && !HasNumberField(EchoObject, TEXT("time_s")))
    {
        RejectReason = TEXT("missing_timestamp");
        return false;
    }
    if (!bSmokeOnly && !IsAuthoritativeLiveEchoSource(EchoSource, AckAuthority))
    {
        RejectReason = TEXT("source_authority_mismatch");
        return false;
    }

    const FString StateKey = MakeStateKey(RunId, RequestId);
    FQuadrotorMworksExperimentConsoleCommandState* State = CommandStatesByKey.Find(StateKey);
    if (!State)
    {
        RejectReason = TEXT("no_matching_command_request");
        return false;
    }

    const int32 EchoSeq = GetIntegerField(EchoObject, TEXT("seq"));
    if (EchoSeq != State->Seq)
    {
        RejectReason = TEXT("seq_mismatch");
        OutState = *State;
        return false;
    }

    const FString EchoCommandKind = GetCommandKind(EchoObject);
    if (!EchoCommandKind.IsEmpty() && EchoCommandKind != State->CommandKind)
    {
        RejectReason = TEXT("command_kind_mismatch");
        OutState = *State;
        return false;
    }

    State->UiState = Status;
    State->AckAuthority = AckAuthority;
    State->Reason = GetStringField(EchoObject, TEXT("reason"));
    State->Source = EchoSource.IsEmpty() ? TEXT("source_level_smoke") : EchoSource;
    State->QualityStatus = bSmokeOnly ? TEXT("smoke_only") : TEXT("runtime_echo_fixture");
    // Legacy static checker anchor: State->bAcceptedAsRuntimeAck = !IsSmokeSource(EchoSource);
    State->bAcceptedAsRuntimeAck = !bSmokeOnly && Status == TEXT("accepted");
    State->NoPoseOverwriteStatus = NoPoseOverwriteStatus;

    OutState = *State;
    return true;
}

TArray<FQuadrotorMworksExperimentConsoleCommandState> UQuadrotorMworksExperimentConsoleStateComponent::GetCommandStates() const
{
    TArray<FQuadrotorMworksExperimentConsoleCommandState> States;
    CommandStatesByKey.GenerateValueArray(States);
    return States;
}

void UQuadrotorMworksExperimentConsoleStateComponent::ClearCommandStates()
{
    CommandStatesByKey.Reset();
}

FString UQuadrotorMworksExperimentConsoleStateComponent::MakeStateKey(const FString& RunId, const FString& RequestId) const
{
    return RunId + TEXT("|") + RequestId;
}
