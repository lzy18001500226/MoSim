#include "QuadrotorMworksUdpReceiverComponent.h"

#include "Common/UdpSocketBuilder.h"
#include "Dom/JsonObject.h"
#include "Async/Async.h"
#include "Misc/FileHelper.h"
#include "HAL/RunnableThread.h"
#include "Interfaces/IPv4/IPv4Address.h"
#include "Json.h"
#include "Serialization/ArrayReader.h"
#include "Sockets.h"
#include "SocketSubsystem.h"

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

    OutFrame.SceneId = Root->GetStringField(TEXT("scene_id"));
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

    const TSharedPtr<FJsonObject>* Perception = nullptr;
    if (Root->TryGetObjectField(TEXT("perception"), Perception) && Perception && Perception->IsValid())
    {
        (*Perception)->TryGetNumberField(TEXT("near_radius_m"), OutFrame.RadarNearRadiusMeters);
        (*Perception)->TryGetNumberField(TEXT("far_radius_m"), OutFrame.RadarFarRadiusMeters);
        (*Perception)->TryGetNumberField(TEXT("fov_deg"), OutFrame.RadarFovDegrees);
    }

    OutFrame.bIsValid = true;
    return true;
}
