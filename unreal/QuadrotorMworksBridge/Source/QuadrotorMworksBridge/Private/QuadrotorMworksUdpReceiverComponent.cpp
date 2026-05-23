#include "QuadrotorMworksUdpReceiverComponent.h"

#include "Common/UdpSocketBuilder.h"
#include "Dom/JsonObject.h"
#include "Async/Async.h"
#include "Misc/FileHelper.h"
#include "HAL/RunnableThread.h"
#include "Interfaces/IPv4/IPv4Address.h"
#include "Common/UdpSocketReceiver.h"
#include "Json.h"
#include "Serialization/ArrayReader.h"
#include "Sockets.h"
#include "SocketSubsystem.h"

namespace
{
FIntVector ParseIntVector3(const TSharedPtr<FJsonObject>& Object, const FString& FieldName, const FIntVector& Fallback)
{
    if (!Object.IsValid())
    {
        return Fallback;
    }

    const TArray<TSharedPtr<FJsonValue>>* Array = nullptr;
    if (!Object->TryGetArrayField(FieldName, Array) || !Array || Array->Num() < 3)
    {
        return Fallback;
    }

    return FIntVector(
        static_cast<int32>((*Array)[0]->AsNumber()),
        static_cast<int32>((*Array)[1]->AsNumber()),
        static_cast<int32>((*Array)[2]->AsNumber()));
}
}

UQuadrotorMworksUdpReceiverComponent::UQuadrotorMworksUdpReceiverComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UQuadrotorMworksUdpReceiverComponent::BeginPlay()
{
    Super::BeginPlay();
    if (bAutoStart)
    {
        StartReceiver();
    }
}

void UQuadrotorMworksUdpReceiverComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopReceiver();
    Super::EndPlay(EndPlayReason);
}

bool UQuadrotorMworksUdpReceiverComponent::StartReceiver()
{
    StopReceiver();

    FIPv4Address Address;
    if (!FIPv4Address::Parse(ListenAddress, Address))
    {
        Address = FIPv4Address::Any;
    }

    const FIPv4Endpoint Endpoint(Address, static_cast<uint16>(ListenPort));
    Socket = FUdpSocketBuilder(TEXT("QuadrotorMworksUdpReceiver"))
                 .AsNonBlocking()
                 .AsReusable()
                 .BoundToEndpoint(Endpoint)
                 .WithReceiveBufferSize(ReceiveBufferSizeBytes);

    if (!Socket)
    {
        UE_LOG(LogTemp, Error, TEXT("Quadrotor MWORKS UDP receiver failed to bind %s:%d"), *ListenAddress, ListenPort);
        return false;
    }

    Receiver = MakeShared<FUdpSocketReceiver>(Socket, FTimespan::FromMilliseconds(5), TEXT("QuadrotorMworksUdpReceiverThread"));
    Receiver->OnDataReceived().BindUObject(this, &UQuadrotorMworksUdpReceiverComponent::HandleDatagram);
    Receiver->Start();
    UE_LOG(LogTemp, Display, TEXT("Quadrotor MWORKS UDP receiver listening on %s:%d"), *ListenAddress, ListenPort);
    return true;
}

void UQuadrotorMworksUdpReceiverComponent::StopReceiver()
{
    if (Receiver.IsValid())
    {
        Receiver->Stop();
        Receiver.Reset();
    }

    if (Socket)
    {
        Socket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);
        Socket = nullptr;
    }
}

FQuadrotorMworksFrame UQuadrotorMworksUdpReceiverComponent::GetLatestFrame() const
{
    FScopeLock Lock(&FrameMutex);
    return LatestFrame;
}

bool UQuadrotorMworksUdpReceiverComponent::HasFrame() const
{
    FScopeLock Lock(&FrameMutex);
    return LatestFrame.bIsValid;
}

void UQuadrotorMworksUdpReceiverComponent::HandleDatagram(const FArrayReaderPtr& Data, const FIPv4Endpoint& Endpoint)
{
    if (!Data.IsValid() || Data->Num() <= 0)
    {
        return;
    }

    FString Text;
    FFileHelper::BufferToString(Text, Data->GetData(), Data->Num());

    FQuadrotorMworksFrame Frame;
    if (!ParseFrameJson(Text, Frame))
    {
        return;
    }

    AsyncTask(ENamedThreads::GameThread, [this, Frame]()
    {
        {
            FScopeLock Lock(&FrameMutex);
            LatestFrame = Frame;
        }
        OnFrameReceived.Broadcast(Frame);
    });
}

FVector UQuadrotorMworksUdpReceiverComponent::ParseVector3(
    const TSharedPtr<FJsonObject>& Object,
    const FString& FieldName,
    const FVector& Fallback) const
{
    if (!Object.IsValid())
    {
        return Fallback;
    }

    const TArray<TSharedPtr<FJsonValue>>* Array = nullptr;
    if (!Object->TryGetArrayField(FieldName, Array) || !Array || Array->Num() < 3)
    {
        return Fallback;
    }

    return FVector(
        (*Array)[0]->AsNumber(),
        (*Array)[1]->AsNumber(),
        (*Array)[2]->AsNumber());
}

bool UQuadrotorMworksUdpReceiverComponent::ParseFrameJson(const FString& Text, FQuadrotorMworksFrame& OutFrame) const
{
    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        return false;
    }

    FString Type;
    Root->TryGetStringField(TEXT("type"), Type);
    if (Type != TEXT("frame"))
    {
        return false;
    }

    FString Schema;
    Root->TryGetStringField(TEXT("schema"), Schema);
    if (!Schema.StartsWith(TEXT("quadrotor.unreal_state.")))
    {
        return false;
    }

    Root->TryGetStringField(TEXT("scene_id"), OutFrame.SceneId);
    Root->TryGetStringField(TEXT("map_id"), OutFrame.MapId);
    OutFrame.Sequence = static_cast<int32>(Root->GetIntegerField(TEXT("seq")));
    OutFrame.TimeSeconds = Root->GetNumberField(TEXT("t"));

    const TSharedPtr<FJsonObject>* Uav = nullptr;
    if (Root->TryGetObjectField(TEXT("uav"), Uav) && Uav && Uav->IsValid())
    {
        OutFrame.PositionMeters = ParseVector3(*Uav, TEXT("position_m"), FVector::ZeroVector);
        OutFrame.RotationRadians = ParseVector3(*Uav, TEXT("rpy_rad"), FVector::ZeroVector);

        const TArray<TSharedPtr<FJsonValue>>* Motors = nullptr;
        if ((*Uav)->TryGetArrayField(TEXT("motor_command"), Motors) && Motors)
        {
            OutFrame.MotorCommand.Reset();
            for (const TSharedPtr<FJsonValue>& Value : *Motors)
            {
                OutFrame.MotorCommand.Add(Value->AsNumber());
            }
        }
    }

    const TSharedPtr<FJsonObject>* Reference = nullptr;
    if (Root->TryGetObjectField(TEXT("reference"), Reference) && Reference && Reference->IsValid())
    {
        OutFrame.ReferencePositionMeters = ParseVector3(*Reference, TEXT("position_m"), FVector::ZeroVector);
    }

    const TSharedPtr<FJsonObject>* Mission = nullptr;
    if (Root->TryGetObjectField(TEXT("mission"), Mission) && Mission && Mission->IsValid())
    {
        OutFrame.Mission.StartMeters = ParseVector3(*Mission, TEXT("start_m"), FVector::ZeroVector);
        OutFrame.Mission.GoalMeters = ParseVector3(*Mission, TEXT("goal_m"), FVector::ZeroVector);
        OutFrame.Mission.CurrentGoalMeters = ParseVector3(*Mission, TEXT("current_goal_m"), OutFrame.Mission.GoalMeters);
    }

    const TSharedPtr<FJsonObject>* Perception = nullptr;
    if (Root->TryGetObjectField(TEXT("perception"), Perception) && Perception && Perception->IsValid())
    {
        (*Perception)->TryGetNumberField(TEXT("near_radius_m"), OutFrame.RadarNearRadiusMeters);
        (*Perception)->TryGetNumberField(TEXT("far_radius_m"), OutFrame.RadarFarRadiusMeters);
        (*Perception)->TryGetNumberField(TEXT("fov_deg"), OutFrame.RadarFovDegrees);
        (*Perception)->TryGetNumberField(TEXT("yaw_rad"), OutFrame.RadarYawRadians);
    }

    const TSharedPtr<FJsonObject>* LocalKnownMap = nullptr;
    if (Root->TryGetObjectField(TEXT("local_known_map"), LocalKnownMap) && LocalKnownMap && LocalKnownMap->IsValid())
    {
        (*LocalKnownMap)->TryGetStringField(TEXT("schema"), OutFrame.LocalKnownMap.Schema);
        OutFrame.LocalKnownMap.OriginMeters = ParseVector3(*LocalKnownMap, TEXT("origin_m"), FVector::ZeroVector);
        (*LocalKnownMap)->TryGetNumberField(TEXT("grid_m"), OutFrame.LocalKnownMap.GridMeters);
        (*LocalKnownMap)->TryGetNumberField(TEXT("radius_m"), OutFrame.LocalKnownMap.RadiusMeters);
        (*LocalKnownMap)->TryGetBoolField(TEXT("render_only"), OutFrame.LocalKnownMap.bRenderOnly);
        (*LocalKnownMap)->TryGetBoolField(TEXT("evidence_backed"), OutFrame.LocalKnownMap.bEvidenceBacked);

        const TArray<TSharedPtr<FJsonValue>>* Cells = nullptr;
        if ((*LocalKnownMap)->TryGetArrayField(TEXT("cells"), Cells) && Cells)
        {
            OutFrame.LocalKnownMap.Cells.Reset();
            for (const TSharedPtr<FJsonValue>& CellValue : *Cells)
            {
                if (!CellValue.IsValid())
                {
                    continue;
                }

                const TSharedPtr<FJsonObject> CellObject = CellValue->AsObject();
                if (!CellObject.IsValid())
                {
                    continue;
                }

                FQuadrotorMworksLocalKnownMapCell Cell;
                Cell.Offset = ParseIntVector3(CellObject, TEXT("offset"), FIntVector::ZeroValue);
                CellObject->TryGetStringField(TEXT("state"), Cell.State);
                CellObject->TryGetStringField(TEXT("source"), Cell.Source);
                OutFrame.LocalKnownMap.Cells.Add(Cell);
            }
        }
    }

    const TSharedPtr<FJsonObject>* LocalPlan = nullptr;
    if (Root->TryGetObjectField(TEXT("local_plan"), LocalPlan) && LocalPlan && LocalPlan->IsValid())
    {
        (*LocalPlan)->TryGetStringField(TEXT("source"), OutFrame.LocalPlanSource);
        (*LocalPlan)->TryGetBoolField(TEXT("render_only"), OutFrame.bLocalPlanRenderOnly);
        (*LocalPlan)->TryGetBoolField(TEXT("evidence_backed"), OutFrame.bLocalPlanEvidenceBacked);
        (*LocalPlan)->TryGetBoolField(TEXT("valid"), OutFrame.bLocalPlanValid);

        const TArray<TSharedPtr<FJsonValue>>* Points = nullptr;
        if ((*LocalPlan)->TryGetArrayField(TEXT("points_m"), Points) && Points)
        {
            OutFrame.LocalPlanPointsMeters.Reset();
            for (const TSharedPtr<FJsonValue>& PointValue : *Points)
            {
                const TArray<TSharedPtr<FJsonValue>>* PointArray = nullptr;
                if (PointValue.IsValid() && PointValue->TryGetArray(PointArray) && PointArray && PointArray->Num() >= 3)
                {
                    OutFrame.LocalPlanPointsMeters.Add(FVector(
                        (*PointArray)[0]->AsNumber(),
                        (*PointArray)[1]->AsNumber(),
                        (*PointArray)[2]->AsNumber()));
                }
            }
        }
    }

    const TSharedPtr<FJsonObject>* Status = nullptr;
    if (Root->TryGetObjectField(TEXT("status"), Status) && Status && Status->IsValid())
    {
        (*Status)->TryGetStringField(TEXT("controller_mode"), OutFrame.Status.ControllerMode);
        (*Status)->TryGetStringField(TEXT("planner_state"), OutFrame.Status.PlannerState);
        (*Status)->TryGetStringField(TEXT("safety_state"), OutFrame.Status.SafetyState);
        (*Status)->TryGetStringField(TEXT("evidence_level"), OutFrame.Status.EvidenceLevel);
        (*Status)->TryGetStringField(TEXT("notes"), OutFrame.Status.Notes);
    }

    const TSharedPtr<FJsonObject>* Overlays = nullptr;
    if (Root->TryGetObjectField(TEXT("overlays"), Overlays) && Overlays && Overlays->IsValid())
    {
        (*Overlays)->TryGetStringField(TEXT("scene_label"), OutFrame.Overlays.SceneLabel);
        (*Overlays)->TryGetStringField(TEXT("map_label"), OutFrame.Overlays.MapLabel);

        const TArray<TSharedPtr<FJsonValue>>* QualityFlags = nullptr;
        if ((*Overlays)->TryGetArrayField(TEXT("quality_flags"), QualityFlags) && QualityFlags)
        {
            OutFrame.Overlays.QualityFlags.Reset();
            for (const TSharedPtr<FJsonValue>& FlagValue : *QualityFlags)
            {
                if (FlagValue.IsValid())
                {
                    OutFrame.Overlays.QualityFlags.Add(FlagValue->AsString());
                }
            }
        }
    }

    OutFrame.bIsValid = true;
    return true;
}
