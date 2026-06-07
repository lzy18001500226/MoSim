#include "QuadrotorMworksUdpCommandSenderComponent.h"

#include "Common/UdpSocketBuilder.h"
#include "Dom/JsonObject.h"
#include "Json.h"
#include "Serialization/JsonSerializer.h"
#include "SocketSubsystem.h"
#include "Sockets.h"

namespace
{
const TCHAR* CommandSchema = TEXT("mosim.ue_command.v1");

TSharedPtr<FJsonObject> ParsePayloadObject(const FString& PayloadJson)
{
    if (PayloadJson.TrimStartAndEnd().IsEmpty())
    {
        return MakeShared<FJsonObject>();
    }

    TSharedPtr<FJsonObject> PayloadObject;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(PayloadJson);
    if (!FJsonSerializer::Deserialize(Reader, PayloadObject) || !PayloadObject.IsValid())
    {
        return nullptr;
    }
    return PayloadObject;
}
}

UQuadrotorMworksUdpCommandSenderComponent::UQuadrotorMworksUdpCommandSenderComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UQuadrotorMworksUdpCommandSenderComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (SenderSocket)
    {
        SenderSocket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(SenderSocket);
        SenderSocket = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

FQuadrotorMworksCommandResult UQuadrotorMworksUdpCommandSenderComponent::BuildCommandPacket(
    const FString& CommandKind,
    const FString& PayloadJson,
    const FQuadrotorMworksCommandGuard& Guard) const
{
    FQuadrotorMworksCommandResult Result;

    if (IsForbiddenCommandKind(CommandKind))
    {
        Result.RejectReason = TEXT("forbidden_pose_command");
        return Result;
    }
    if (!IsAllowedCommandKind(CommandKind))
    {
        Result.RejectReason = TEXT("unsupported_command_kind");
        return Result;
    }
    if (!Guard.bRequireMworksAck)
    {
        Result.RejectReason = TEXT("missing_mworks_ack_guard");
        return Result;
    }
    if (RequiresRos2Ack(CommandKind) && !Guard.bRequireRos2Ack)
    {
        Result.RejectReason = TEXT("missing_ros2_ack_guard");
        return Result;
    }

    TSharedPtr<FJsonObject> PayloadObject = ParsePayloadObject(PayloadJson);
    if (!PayloadObject.IsValid())
    {
        Result.RejectReason = TEXT("invalid_payload_json");
        return Result;
    }

    const int32 NextSeq = ++Sequence;
    Result.RequestId = MakeRequestId();

    TSharedRef<FJsonObject> CommandObject = MakeShared<FJsonObject>();
    CommandObject->SetStringField(TEXT("kind"), CommandKind);
    CommandObject->SetObjectField(TEXT("payload"), PayloadObject);

    TSharedRef<FJsonObject> GuardObject = MakeShared<FJsonObject>();
    GuardObject->SetBoolField(TEXT("require_mworks_ack"), Guard.bRequireMworksAck);
    GuardObject->SetBoolField(TEXT("require_ros2_ack"), Guard.bRequireRos2Ack);
    TArray<TSharedPtr<FJsonValue>> GateValues;
    for (const FString& Gate : Guard.RejectIfGateOpen)
    {
        GateValues.Add(MakeShared<FJsonValueString>(Gate));
    }
    GuardObject->SetArrayField(TEXT("reject_if_gate_open"), GateValues);

    TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("schema"), CommandSchema);
    Root->SetStringField(TEXT("type"), TEXT("command"));
    Root->SetStringField(TEXT("run_id"), RunId);
    Root->SetStringField(TEXT("request_id"), Result.RequestId);
    Root->SetNumberField(TEXT("seq"), NextSeq);
    Root->SetNumberField(TEXT("time_s"), FPlatformTime::Seconds());
    Root->SetStringField(TEXT("requested_by"), RequestedBy);
    Root->SetObjectField(TEXT("command"), CommandObject);
    Root->SetObjectField(TEXT("guard"), GuardObject);

    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Result.PacketJson);
    if (!FJsonSerializer::Serialize(Root, Writer))
    {
        Result.PacketJson.Reset();
        Result.RejectReason = TEXT("serialize_failed");
    }
    return Result;
}

FQuadrotorMworksCommandResult UQuadrotorMworksUdpCommandSenderComponent::SendCommand(
    const FString& CommandKind,
    const FString& PayloadJson,
    const FQuadrotorMworksCommandGuard& Guard)
{
    FQuadrotorMworksCommandResult Result = BuildCommandPacket(CommandKind, PayloadJson, Guard);
    if (!Result.RejectReason.IsEmpty() || Result.PacketJson.IsEmpty())
    {
        return Result;
    }
    if (!EnsureSocket())
    {
        Result.RejectReason = TEXT("socket_unavailable");
        return Result;
    }

    FIPv4Address Address;
    if (!FIPv4Address::Parse(RemoteAddress, Address))
    {
        Result.RejectReason = TEXT("invalid_remote_address");
        return Result;
    }

    const FIPv4Endpoint Endpoint(Address, static_cast<uint16>(RemotePort));
    TSharedRef<FInternetAddr> InternetAddr = Endpoint.ToInternetAddr();
    FTCHARToUTF8 PayloadUtf8(*Result.PacketJson);
    int32 BytesSent = 0;
    Result.bSent = SenderSocket->SendTo(
        reinterpret_cast<const uint8*>(PayloadUtf8.Get()),
        PayloadUtf8.Length(),
        BytesSent,
        *InternetAddr);
    if (!Result.bSent)
    {
        Result.RejectReason = TEXT("udp_send_failed");
    }
    return Result;
}

bool UQuadrotorMworksUdpCommandSenderComponent::EnsureSocket()
{
    if (SenderSocket)
    {
        return true;
    }
    SenderSocket = FUdpSocketBuilder(TEXT("QuadrotorMworksUdpCommandSender")).AsReusable().WithSendBufferSize(256 * 1024);
    return SenderSocket != nullptr;
}

bool UQuadrotorMworksUdpCommandSenderComponent::IsAllowedCommandKind(const FString& CommandKind) const
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

bool UQuadrotorMworksUdpCommandSenderComponent::IsForbiddenCommandKind(const FString& CommandKind) const
{
    return CommandKind == TEXT("pose_override")
        || CommandKind == TEXT("teleport")
        || CommandKind == TEXT("set_uav_pose")
        || CommandKind == TEXT("actor_transform")
        || CommandKind == TEXT("keyboard_pose");
}

bool UQuadrotorMworksUdpCommandSenderComponent::RequiresRos2Ack(const FString& CommandKind) const
{
    return CommandKind == TEXT("planner_select")
        || CommandKind == TEXT("sensor_mode")
        || CommandKind == TEXT("scene_switch")
        || CommandKind == TEXT("start_goal_update");
}

FString UQuadrotorMworksUdpCommandSenderComponent::MakeRequestId() const
{
    return FString::Printf(TEXT("ue_cmd_%08d"), Sequence);
}
