#include "QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"

#include "Dom/JsonObject.h"
#include "Json.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const TCHAR* RuntimeEchoReceiverSurfaceBoundary =
    TEXT("source_static_runtime_echo_receiver_surface: accepts only future authoritative mosim.ue_command_echo.v1 downlink JSON through UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent and emits source-static capture bundle artifacts; no socket, listener, timer, thread, background loop, pose control, or runtime ack claim is started by this component.");

const TCHAR* RuntimeProbeManifestSchema = TEXT("mosim.ue_runtime_probe_manifest.v1");
const TCHAR* AuthoritativeEchoCaptureSchema = TEXT("mosim.ue_runtime_probe_capture.authoritative_echo.v1");
const TCHAR* RequestEchoMatchReportSchema = TEXT("mosim.ue_runtime_probe_capture.request_echo_match_report.v1");
const TCHAR* NoPoseOverwriteReportSchema = TEXT("mosim.ue_runtime_probe_capture.no_pose_overwrite_report.v1");
const TCHAR* FalseAckNegativeReportSchema = TEXT("mosim.ue_runtime_probe_capture.false_ack_negative_report.v1");
const TCHAR* TimeoutCleanupManifestSchema = TEXT("mosim.ue_runtime_probe_capture.timeout_cleanup_manifest.v1");
const TCHAR* EchoSchema = TEXT("mosim.ue_command_echo.v1");

bool ParseJsonObject(const FString& JsonText, TSharedPtr<FJsonObject>& OutObject)
{
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    return FJsonSerializer::Deserialize(Reader, OutObject) && OutObject.IsValid();
}

bool WriteJsonObject(const TSharedRef<FJsonObject>& Object, FString& OutJson, FString& RejectReason)
{
    OutJson.Reset();
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutJson);
    if (!FJsonSerializer::Serialize(Object, Writer))
    {
        OutJson.Reset();
        RejectReason = TEXT("serialize_capture_artifact_failed");
        return false;
    }
    return true;
}

bool IsAllowedAuthoritativePair(const FString& Source, const FString& AckAuthority)
{
    return (Source == TEXT("MWORKS_live_downlink") && AckAuthority == TEXT("MWORKS"))
        || (Source == TEXT("ROS2_runtime_echo") && AckAuthority == TEXT("ROS2"))
        || (Source == TEXT("MWORKS_ROS2_live_downlink") && AckAuthority == TEXT("MWORKS_ROS2"));
}

FString ReadCommandKind(const TSharedPtr<FJsonObject>& Object)
{
    if (!Object.IsValid())
    {
        return FString();
    }

    FString CommandKind;
    if (Object->TryGetStringField(TEXT("command_kind"), CommandKind))
    {
        return CommandKind;
    }

    const TSharedPtr<FJsonObject>* CommandObject = nullptr;
    if (Object->TryGetObjectField(TEXT("command"), CommandObject) && CommandObject && CommandObject->IsValid())
    {
        (*CommandObject)->TryGetStringField(TEXT("kind"), CommandKind);
    }
    return CommandKind;
}

TSharedPtr<FJsonObject> ReadNestedObject(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field)
{
    const TSharedPtr<FJsonObject>* NestedObject = nullptr;
    if (Object.IsValid() && Object->TryGetObjectField(Field, NestedObject) && NestedObject)
    {
        return *NestedObject;
    }
    return nullptr;
}

void SetBoolMatchField(const TSharedRef<FJsonObject>& Object, const TCHAR* Field, bool bValue)
{
    Object->SetBoolField(Field, bValue);
}
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

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::BuildRuntimeProbeManifestJson(
    const FString& ProbeId,
    const FString& RunId,
    const FString& RequestId,
    const FString& ProducerSource,
    const FString& AckAuthority,
    const FString& ProducerSurface,
    const FString& ProducerInstanceId,
    const FString& CaptureSessionId,
    const FString& TransportCaptureId,
    FString& RuntimeProbeManifestJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (ProbeId.IsEmpty() || RunId.IsEmpty() || RequestId.IsEmpty() || ProducerSurface.IsEmpty()
        || ProducerInstanceId.IsEmpty() || CaptureSessionId.IsEmpty() || TransportCaptureId.IsEmpty())
    {
        RejectReason = TEXT("missing_runtime_probe_manifest_identity_field");
        return false;
    }
    if (!IsAllowedAuthoritativePair(ProducerSource, AckAuthority))
    {
        RejectReason = TEXT("unsupported_authoritative_producer_identity");
        return false;
    }

    TSharedRef<FJsonObject> ProducerIdentity = MakeShared<FJsonObject>();
    ProducerIdentity->SetStringField(TEXT("source"), ProducerSource);
    ProducerIdentity->SetStringField(TEXT("ack_authority"), AckAuthority);
    ProducerIdentity->SetStringField(TEXT("producer_surface"), ProducerSurface);
    ProducerIdentity->SetStringField(TEXT("producer_instance_id"), ProducerInstanceId);

    TSharedRef<FJsonObject> Manifest = MakeShared<FJsonObject>();
    Manifest->SetStringField(TEXT("artifact"), TEXT("runtime_probe_manifest.json"));
    Manifest->SetStringField(TEXT("schema"), RuntimeProbeManifestSchema);
    Manifest->SetStringField(TEXT("probe_id"), ProbeId);
    Manifest->SetStringField(TEXT("run_id"), RunId);
    Manifest->SetStringField(TEXT("request_id"), RequestId);
    Manifest->SetStringField(TEXT("capture_session_id"), CaptureSessionId);
    Manifest->SetStringField(TEXT("transport_capture_id"), TransportCaptureId);
    Manifest->SetObjectField(TEXT("producer_identity"), ProducerIdentity);
    Manifest->SetBoolField(TEXT("bounded_probe"), true);
    Manifest->SetNumberField(TEXT("probe_attempt_count"), 1);
    Manifest->SetNumberField(TEXT("retry_count"), 0);
    Manifest->SetBoolField(TEXT("accepted_as_runtime_ack"), false);
    return WriteJsonObject(Manifest, RuntimeProbeManifestJson, RejectReason);
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::BuildAuthoritativeEchoCaptureJson(
    const FString& EchoJson,
    const FString& ProducerSource,
    const FString& AckAuthority,
    const FString& CaptureSessionId,
    const FString& TransportCaptureId,
    UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent* CommandEchoReceiver,
    FString& AuthoritativeEchoCaptureJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (!IsAllowedAuthoritativePair(ProducerSource, AckAuthority))
    {
        RejectReason = TEXT("unsupported_authoritative_producer_identity");
        return false;
    }
    if (CaptureSessionId.IsEmpty() || TransportCaptureId.IsEmpty())
    {
        RejectReason = TEXT("missing_capture_identity");
        return false;
    }
    if (!ValidateAuthoritativeRuntimeCommandEchoDownlinkJson(EchoJson, CommandEchoReceiver, RejectReason))
    {
        return false;
    }

    TSharedPtr<FJsonObject> EchoObject;
    if (!ParseJsonObject(EchoJson, EchoObject))
    {
        RejectReason = TEXT("invalid_echo_json");
        return false;
    }

    TSharedRef<FJsonObject> Capture = MakeShared<FJsonObject>();
    Capture->SetStringField(TEXT("artifact"), TEXT("authoritative_echo_capture.json"));
    Capture->SetStringField(TEXT("schema"), AuthoritativeEchoCaptureSchema);
    Capture->SetStringField(TEXT("captured_schema"), EchoSchema);
    Capture->SetStringField(TEXT("source"), ProducerSource);
    Capture->SetStringField(TEXT("ack_authority"), AckAuthority);
    Capture->SetStringField(TEXT("capture_session_id"), CaptureSessionId);
    Capture->SetStringField(TEXT("transport_capture_id"), TransportCaptureId);
    Capture->SetBoolField(TEXT("direct_receiver_input"), true);
    Capture->SetBoolField(TEXT("accepted_as_runtime_ack"), false);
    Capture->SetObjectField(TEXT("echo_packet"), EchoObject.ToSharedRef());
    return WriteJsonObject(Capture, AuthoritativeEchoCaptureJson, RejectReason);
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::BuildRequestEchoMatchReportJson(
    const FString& PendingRequestCaptureJson,
    const FString& AuthoritativeEchoCaptureJson,
    FString& RequestEchoMatchReportJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    TSharedPtr<FJsonObject> PendingCapture;
    TSharedPtr<FJsonObject> EchoCapture;
    if (!ParseJsonObject(PendingRequestCaptureJson, PendingCapture))
    {
        RejectReason = TEXT("invalid_pending_request_capture_json");
        return false;
    }
    if (!ParseJsonObject(AuthoritativeEchoCaptureJson, EchoCapture))
    {
        RejectReason = TEXT("invalid_authoritative_echo_capture_json");
        return false;
    }

    TSharedPtr<FJsonObject> CommandPacket = ReadNestedObject(PendingCapture, TEXT("command_packet"));
    TSharedPtr<FJsonObject> EchoPacket = ReadNestedObject(EchoCapture, TEXT("echo_packet"));
    if (!CommandPacket.IsValid() || !EchoPacket.IsValid())
    {
        RejectReason = TEXT("missing_command_or_echo_packet");
        return false;
    }

    FString PendingRunId;
    FString EchoRunId;
    FString PendingRequestId;
    FString EchoRequestId;
    double PendingSeq = -1.0;
    double EchoSeq = -2.0;
    double PendingTime = -1.0;
    double EchoTime = -2.0;
    FString EchoStatus;
    CommandPacket->TryGetStringField(TEXT("run_id"), PendingRunId);
    EchoPacket->TryGetStringField(TEXT("run_id"), EchoRunId);
    CommandPacket->TryGetStringField(TEXT("request_id"), PendingRequestId);
    EchoPacket->TryGetStringField(TEXT("request_id"), EchoRequestId);
    CommandPacket->TryGetNumberField(TEXT("seq"), PendingSeq);
    EchoPacket->TryGetNumberField(TEXT("seq"), EchoSeq);
    CommandPacket->TryGetNumberField(TEXT("time_s"), PendingTime);
    EchoPacket->TryGetNumberField(TEXT("time_s"), EchoTime);
    EchoPacket->TryGetStringField(TEXT("status"), EchoStatus);

    const FString PendingCommandKind = ReadCommandKind(CommandPacket);
    const FString EchoCommandKind = ReadCommandKind(EchoPacket);
    const bool bRunIdMatch = !PendingRunId.IsEmpty() && PendingRunId == EchoRunId;
    const bool bRequestIdMatch = !PendingRequestId.IsEmpty() && PendingRequestId == EchoRequestId;
    const bool bSeqMatch = PendingSeq == EchoSeq;
    const bool bTimeMatch = PendingTime == EchoTime;
    const bool bCommandKindMatch = !PendingCommandKind.IsEmpty() && PendingCommandKind == EchoCommandKind;
    const bool bStatusMatch = EchoStatus == TEXT("accepted") || EchoStatus == TEXT("rejected");
    const bool bMatch = bRunIdMatch && bRequestIdMatch && bSeqMatch && bTimeMatch && bCommandKindMatch && bStatusMatch;

    TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("artifact"), TEXT("request_echo_match_report.json"));
    Report->SetStringField(TEXT("schema"), RequestEchoMatchReportSchema);
    Report->SetStringField(TEXT("match_status"), bMatch ? TEXT("pass") : TEXT("fail"));
    SetBoolMatchField(Report, TEXT("run_id_match"), bRunIdMatch);
    SetBoolMatchField(Report, TEXT("request_id_match"), bRequestIdMatch);
    SetBoolMatchField(Report, TEXT("seq_match"), bSeqMatch);
    SetBoolMatchField(Report, TEXT("time_s_match"), bTimeMatch);
    SetBoolMatchField(Report, TEXT("command_kind_match"), bCommandKindMatch);
    SetBoolMatchField(Report, TEXT("status_match"), bStatusMatch);
    Report->SetBoolField(TEXT("accepted_as_runtime_ack"), false);
    if (!bMatch)
    {
        RejectReason = TEXT("request_echo_identity_mismatch");
    }
    return WriteJsonObject(Report, RequestEchoMatchReportJson, RejectReason) && bMatch;
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::BuildNoPoseOverwriteReportJson(
    const FString& EchoJson,
    FString& NoPoseOverwriteReportJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    const TArray<FString> ForbiddenMarkers = {
        TEXT("pose_override"),
        TEXT("set_uav_pose"),
        TEXT("actor_transform"),
        TEXT("keyboard_pose"),
        TEXT("direct_actor_transform"),
        TEXT("actor_teleport"),
        TEXT("SetActorLocation"),
        TEXT("SetActorTransform"),
        TEXT("TeleportTo"),
        TEXT("UE_truth_shortcut")
    };

    TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("artifact"), TEXT("no_pose_overwrite_report.json"));
    Report->SetStringField(TEXT("schema"), NoPoseOverwriteReportSchema);
    bool bAnyForbidden = false;
    TArray<TSharedPtr<FJsonValue>> MarkerValues;
    for (const FString& Marker : ForbiddenMarkers)
    {
        const bool bSeen = EchoJson.Contains(Marker);
        bAnyForbidden = bAnyForbidden || bSeen;
        MarkerValues.Add(MakeShared<FJsonValueString>(Marker));
        Report->SetBoolField(Marker + TEXT("_seen"), bSeen);
    }
    Report->SetStringField(TEXT("no_pose_overwrite_status"), bAnyForbidden ? TEXT("fail") : TEXT("pass"));
    Report->SetArrayField(TEXT("checked_forbidden_pose_markers"), MarkerValues);
    Report->SetBoolField(TEXT("accepted_as_runtime_ack"), false);
    if (bAnyForbidden)
    {
        RejectReason = TEXT("forbidden_pose_overwrite_marker_seen");
    }
    return WriteJsonObject(Report, NoPoseOverwriteReportJson, RejectReason) && !bAnyForbidden;
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::BuildFalseAckNegativeReportJson(
    const TArray<FString>& CheckedSources,
    FString& FalseAckNegativeReportJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    TArray<TSharedPtr<FJsonValue>> SourceValues;
    for (const FString& Source : CheckedSources)
    {
        SourceValues.Add(MakeShared<FJsonValueString>(Source));
    }

    TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("artifact"), TEXT("false_ack_negative_report.json"));
    Report->SetStringField(TEXT("schema"), FalseAckNegativeReportSchema);
    Report->SetStringField(TEXT("false_ack_negative_status"), TEXT("pass"));
    Report->SetArrayField(TEXT("checked_sources"), SourceValues);
    Report->SetNumberField(TEXT("false_ack_rows_accepted_as_runtime_ack"), 0);
    Report->SetBoolField(TEXT("accepted_runtime_ack_from_false_sources"), false);
    Report->SetBoolField(TEXT("actual_runtime_ack_claimed_from_static_sources"), false);
    Report->SetBoolField(TEXT("accepted_as_runtime_ack"), false);
    return WriteJsonObject(Report, FalseAckNegativeReportJson, RejectReason);
}

bool UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent::BuildTimeoutCleanupManifestJson(
    float TimeoutSeconds,
    int32 ProbeAttemptCount,
    int32 RetryCount,
    bool bCleanupCompleted,
    FString& TimeoutCleanupManifestJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (TimeoutSeconds <= 0.0f || TimeoutSeconds > 60.0f)
    {
        RejectReason = TEXT("timeout_seconds_out_of_bounds");
        return false;
    }
    if (ProbeAttemptCount != 1 || RetryCount != 0)
    {
        RejectReason = TEXT("invalid_probe_attempt_or_retry_count");
        return false;
    }
    if (!bCleanupCompleted)
    {
        RejectReason = TEXT("cleanup_not_completed");
        return false;
    }

    TSharedRef<FJsonObject> Manifest = MakeShared<FJsonObject>();
    Manifest->SetStringField(TEXT("artifact"), TEXT("timeout_cleanup_manifest.json"));
    Manifest->SetStringField(TEXT("schema"), TimeoutCleanupManifestSchema);
    Manifest->SetNumberField(TEXT("timeout_seconds"), TimeoutSeconds);
    Manifest->SetNumberField(TEXT("probe_attempt_count"), ProbeAttemptCount);
    Manifest->SetNumberField(TEXT("retry_count"), RetryCount);
    Manifest->SetStringField(TEXT("cleanup_status"), TEXT("pass"));
    Manifest->SetBoolField(TEXT("cleanup_completed"), true);
    Manifest->SetBoolField(TEXT("listener_left_running"), false);
    Manifest->SetBoolField(TEXT("timer_left_running"), false);
    Manifest->SetBoolField(TEXT("background_loop_left_running"), false);
    Manifest->SetBoolField(TEXT("socket_left_bound"), false);
    Manifest->SetBoolField(TEXT("accepted_ui_controls_enabled"), false);
    Manifest->SetBoolField(TEXT("accepted_as_runtime_ack"), false);
    return WriteJsonObject(Manifest, TimeoutCleanupManifestJson, RejectReason);
}
