#include "QuadrotorMworksUdpReceiverComponent.h"

#include "Common/UdpSocketBuilder.h"
#include "Dom/JsonObject.h"
#include "Async/Async.h"
#include "Misc/FileHelper.h"
#include "HAL/RunnableThread.h"
#include "HAL/PlatformTime.h"
#include "HAL/PlatformFileManager.h"
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
    bLoggedFirstFrame = false;
    ReceiveRateWindowStartSeconds = 0.0;
    ReceivedFramesInWindow = 0;
    SequenceGapsInWindow = 0;
    ReceivedPayloadBytesInWindow = 0;
    LastReceivedSequence = TNumericLimits<int32>::Min();
    ActiveStreamId.Reset();
    LastAcceptedFrameSeconds = 0.0;
    LastRejectedFrameLogSeconds = 0.0;

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

    const double NowSeconds = FPlatformTime::Seconds();
    if (!Frame.StreamId.IsEmpty())
    {
        if (ActiveStreamId.IsEmpty())
        {
            ActiveStreamId = Frame.StreamId;
            LastReceivedSequence = TNumericLimits<int32>::Min();
        }
        else if (Frame.StreamId != ActiveStreamId)
        {
            if (NowSeconds - LastAcceptedFrameSeconds <= StreamTakeoverTimeoutSeconds)
            {
                if (NowSeconds - LastRejectedFrameLogSeconds >= 5.0)
                {
                    UE_LOG(LogTemp, Warning, TEXT("MoSim UE rejected competing UDP stream=%s active=%s"), *Frame.StreamId, *ActiveStreamId);
                    LastRejectedFrameLogSeconds = NowSeconds;
                }
                return;
            }
            UE_LOG(LogTemp, Display, TEXT("MoSim UE UDP stream takeover old=%s new=%s"), *ActiveStreamId, *Frame.StreamId);
            ActiveStreamId = Frame.StreamId;
            LastReceivedSequence = TNumericLimits<int32>::Min();
        }
        if (LastReceivedSequence != TNumericLimits<int32>::Min() && Frame.Sequence <= LastReceivedSequence)
        {
            if (NowSeconds - LastRejectedFrameLogSeconds >= 5.0)
            {
                UE_LOG(LogTemp, Warning, TEXT("MoSim UE rejected non-monotonic UDP frame stream=%s seq=%d last_seq=%d"), *ActiveStreamId, Frame.Sequence, LastReceivedSequence);
                LastRejectedFrameLogSeconds = NowSeconds;
            }
            return;
        }
    }
    LastAcceptedFrameSeconds = NowSeconds;
    if (ReceiveRateWindowStartSeconds <= 0.0)
    {
        ReceiveRateWindowStartSeconds = NowSeconds;
    }
    ++ReceivedFramesInWindow;
    ReceivedPayloadBytesInWindow += Data->Num();
    if (LastReceivedSequence != TNumericLimits<int32>::Min() && Frame.Sequence > LastReceivedSequence + 1)
    {
        SequenceGapsInWindow += Frame.Sequence - LastReceivedSequence - 1;
    }
    LastReceivedSequence = Frame.Sequence;
    const double RateElapsedSeconds = NowSeconds - ReceiveRateWindowStartSeconds;
    if (RateElapsedSeconds >= 5.0)
    {
        const int32 ExpectedFrames = ReceivedFramesInWindow + SequenceGapsInWindow;
        const double DropRate = ExpectedFrames > 0
            ? static_cast<double>(SequenceGapsInWindow) / static_cast<double>(ExpectedFrames)
            : 0.0;
        const double PayloadBytesPerSecond = ReceivedPayloadBytesInWindow / RateElapsedSeconds;
        const double WireBytesPerSecond =
            (ReceivedPayloadBytesInWindow + static_cast<int64>(ReceivedFramesInWindow) * 28) / RateElapsedSeconds;
        UE_LOG(
            LogTemp,
            Display,
            TEXT("MoSim UE UDP receive rate=%.1fHz sequence_gaps=%d last_seq=%d bytes=%d"),
            ReceivedFramesInWindow / RateElapsedSeconds,
            SequenceGapsInWindow,
            LastReceivedSequence,
            Data->Num());
        if (!MetricsOutputPath.IsEmpty())
        {
            TSharedRef<FJsonObject> Metrics = MakeShared<FJsonObject>();
            Metrics->SetStringField(TEXT("schema"), TEXT("mosim.gazebo_ue_receiver_metrics.v1"));
            Metrics->SetStringField(TEXT("run_id"), !Frame.RunId.IsEmpty() ? Frame.RunId : ObservabilityRunId);
            Metrics->SetStringField(TEXT("stream_id"), ActiveStreamId);
            Metrics->SetStringField(TEXT("link_id"), TEXT("gazebo_ue_display"));
            Metrics->SetStringField(TEXT("measurement_point"), TEXT("unreal_udp_receiver"));
            Metrics->SetNumberField(TEXT("window_s"), RateElapsedSeconds);
            Metrics->SetNumberField(TEXT("receive_rate_hz"), ReceivedFramesInWindow / RateElapsedSeconds);
            Metrics->SetNumberField(TEXT("received_frames"), ReceivedFramesInWindow);
            Metrics->SetNumberField(TEXT("sequence_gap_count"), SequenceGapsInWindow);
            Metrics->SetNumberField(TEXT("receiver_drop_rate"), DropRate);
            Metrics->SetNumberField(
                TEXT("avg_payload_bytes"),
                static_cast<double>(ReceivedPayloadBytesInWindow) / FMath::Max(1, ReceivedFramesInWindow));
            Metrics->SetNumberField(TEXT("payload_bytes_per_s"), PayloadBytesPerSecond);
            Metrics->SetNumberField(TEXT("estimated_ipv4_udp_wire_bytes_per_s"), WireBytesPerSecond);
            Metrics->SetNumberField(TEXT("updated_at_unix"), FDateTime::UtcNow().ToUnixTimestamp());
            Metrics->SetStringField(TEXT("claim_boundary"), TEXT("UE receiver-side rate and sequence loss only; one-way UDP does not provide RTT."));
            FString Json;
            const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
            FJsonSerializer::Serialize(Metrics, Writer);
            const FString AbsolutePath = FPaths::ConvertRelativePathToFull(MetricsOutputPath);
            IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
            PlatformFile.CreateDirectoryTree(*FPaths::GetPath(AbsolutePath));
            const FString TemporaryPath = AbsolutePath + TEXT(".tmp");
            if (FFileHelper::SaveStringToFile(Json, *TemporaryPath))
            {
                if (PlatformFile.FileExists(*AbsolutePath))
                {
                    PlatformFile.DeleteFile(*AbsolutePath);
                }
                PlatformFile.MoveFile(*AbsolutePath, *TemporaryPath);
            }
        }
        ReceiveRateWindowStartSeconds = NowSeconds;
        ReceivedFramesInWindow = 0;
        SequenceGapsInWindow = 0;
        ReceivedPayloadBytesInWindow = 0;
    }

    if (!bLoggedFirstFrame)
    {
        bLoggedFirstFrame = true;
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Quadrotor MWORKS UDP first frame: scene=%s map=%s seq=%d t=%.3f position_m=(%.3f, %.3f, %.3f) rpy_rad=(%.3f, %.3f, %.3f) coordinate_policy=%s local_map_cells=%d local_map_evidence=%s lidar_points=%d lidar_evidence=%s local_plan_points=%d local_plan_evidence=%s"),
            *Frame.SceneId,
            *Frame.MapId,
            Frame.Sequence,
            Frame.TimeSeconds,
            Frame.PositionMeters.X,
            Frame.PositionMeters.Y,
            Frame.PositionMeters.Z,
            Frame.RotationRadians.X,
            Frame.RotationRadians.Y,
            Frame.RotationRadians.Z,
            *Frame.CoordinatePolicy,
            Frame.LocalKnownMap.Cells.Num(),
            Frame.LocalKnownMap.bEvidenceBacked ? TEXT("true") : TEXT("false"),
            Frame.LidarPoints.PointsMeters.Num(),
            Frame.LidarPoints.bEvidenceBacked ? TEXT("true") : TEXT("false"),
            Frame.LocalPlanPointsMeters.Num(),
            Frame.bLocalPlanEvidenceBacked ? TEXT("true") : TEXT("false"));
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
    FString Schema;
    Root->TryGetStringField(TEXT("schema"), Schema);

    if (Schema.StartsWith(TEXT("mosim.ue_render_frame.")))
    {
        Root->TryGetStringField(TEXT("scene_id"), OutFrame.SceneId);
        Root->TryGetStringField(TEXT("map_id"), OutFrame.MapId);
        Root->TryGetStringField(TEXT("vehicle_id"), OutFrame.VehicleId);
        Root->TryGetStringField(TEXT("stream_id"), OutFrame.StreamId);
        Root->TryGetStringField(TEXT("run_id"), OutFrame.RunId);
        OutFrame.CoordinatePolicy = TEXT("mworks_world_m_z_up");
        OutFrame.Sequence = static_cast<int32>(Root->GetIntegerField(TEXT("sequence")));
        OutFrame.TimeSeconds = Root->GetNumberField(TEXT("timestamp_ros_s"));
        OutFrame.PositionMeters = ParseVector3(Root, TEXT("position_m"), FVector::ZeroVector);
        OutFrame.RotationRadians = ParseVector3(Root, TEXT("rpy_rad_display_source"), FVector::ZeroVector);
        OutFrame.ReferencePositionMeters = ParseVector3(Root, TEXT("reference_position_m"), OutFrame.PositionMeters);
        OutFrame.Status.ControllerMode = Root->GetStringField(TEXT("controller_profile"));
        OutFrame.Status.PlannerState = Root->GetStringField(TEXT("planner_profile"));
        OutFrame.Status.SafetyState = TEXT("display_only");
        OutFrame.Status.EvidenceLevel = TEXT("factory_l2_ue_render_frame_replay");
        OutFrame.Status.Notes = TEXT("mosim.ue_render_frame.v1 display-only one-way replay");
        OutFrame.Overlays.SceneLabel = OutFrame.SceneId;
        OutFrame.Overlays.MapLabel = OutFrame.MapId;
        OutFrame.bLocalPlanRenderOnly = true;
        OutFrame.bLocalPlanEvidenceBacked = false;
        OutFrame.bLocalPlanValid = false;
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
        OutFrame.bIsValid = true;
        return true;
    }

    if (Type != TEXT("frame"))
    {
        return false;
    }

    if (!Schema.StartsWith(TEXT("quadrotor.unreal_state.")))
    {
        return false;
    }

    Root->TryGetStringField(TEXT("scene_id"), OutFrame.SceneId);
    Root->TryGetStringField(TEXT("map_id"), OutFrame.MapId);
    Root->TryGetStringField(TEXT("coordinate_policy"), OutFrame.CoordinatePolicy);
    Root->TryGetStringField(TEXT("stream_id"), OutFrame.StreamId);
    Root->TryGetStringField(TEXT("run_id"), OutFrame.RunId);
    OutFrame.Sequence = static_cast<int32>(Root->GetIntegerField(TEXT("seq")));
    OutFrame.TimeSeconds = Root->GetNumberField(TEXT("t"));

    const TSharedPtr<FJsonObject>* Uav = nullptr;
    if (Root->TryGetObjectField(TEXT("uav"), Uav) && Uav && Uav->IsValid())
    {
        (*Uav)->TryGetStringField(TEXT("id"), OutFrame.VehicleId);
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

    const TSharedPtr<FJsonObject>* LidarPoints = nullptr;
    if (Root->TryGetObjectField(TEXT("lidar_points"), LidarPoints) && LidarPoints && LidarPoints->IsValid())
    {
        (*LidarPoints)->TryGetStringField(TEXT("schema"), OutFrame.LidarPoints.Schema);
        (*LidarPoints)->TryGetStringField(TEXT("coordinate_frame"), OutFrame.LidarPoints.CoordinateFrame);
        (*LidarPoints)->TryGetStringField(TEXT("source"), OutFrame.LidarPoints.Source);
        (*LidarPoints)->TryGetBoolField(TEXT("render_only"), OutFrame.LidarPoints.bRenderOnly);
        (*LidarPoints)->TryGetBoolField(TEXT("evidence_backed"), OutFrame.LidarPoints.bEvidenceBacked);

        const TArray<TSharedPtr<FJsonValue>>* Points = nullptr;
        if ((*LidarPoints)->TryGetArrayField(TEXT("points_m"), Points) && Points)
        {
            OutFrame.LidarPoints.PointsMeters.Reset();
            for (const TSharedPtr<FJsonValue>& PointValue : *Points)
            {
                const TArray<TSharedPtr<FJsonValue>>* PointArray = nullptr;
                if (PointValue.IsValid() && PointValue->TryGetArray(PointArray) && PointArray && PointArray->Num() >= 3)
                {
                    OutFrame.LidarPoints.PointsMeters.Add(FVector(
                        (*PointArray)[0]->AsNumber(),
                        (*PointArray)[1]->AsNumber(),
                        (*PointArray)[2]->AsNumber()));
                }
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
