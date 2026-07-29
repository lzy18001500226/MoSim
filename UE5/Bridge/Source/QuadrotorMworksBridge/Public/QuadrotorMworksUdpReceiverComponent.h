#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "Common/UdpSocketReceiver.h"
#include "Interfaces/IPv4/IPv4Endpoint.h"
#include "QuadrotorMworksTypes.h"
#include "QuadrotorMworksUdpReceiverComponent.generated.h"

class FUdpSocketReceiver;
class FSocket;
class FInternetAddr;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FQuadrotorMworksFrameReceived, const FQuadrotorMworksFrame&, Frame);

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorMworksUdpReceiverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorMworksUdpReceiverComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP")
    FString ListenAddress = TEXT("0.0.0.0");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP")
    int32 ListenPort = 5005;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP")
    int32 ReceiveBufferSizeBytes = 2 * 1024 * 1024;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP")
    bool bAutoStart = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP")
    double StreamTakeoverTimeoutSeconds = 1.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP|Observability")
    FString ObservabilityRunId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS UDP|Observability")
    FString MetricsOutputPath;

    UPROPERTY(BlueprintAssignable, Category = "MWORKS UDP")
    FQuadrotorMworksFrameReceived OnFrameReceived;

    UFUNCTION(BlueprintCallable, Category = "MWORKS UDP")
    bool StartReceiver();

    UFUNCTION(BlueprintCallable, Category = "MWORKS UDP")
    void StopReceiver();

    UFUNCTION(BlueprintCallable, Category = "MWORKS UDP")
    FQuadrotorMworksFrame GetLatestFrame() const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS UDP")
    bool HasFrame() const;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void HandleDatagram(const FArrayReaderPtr& Data, const FIPv4Endpoint& Endpoint);
    bool ParseFrameJson(const FString& Text, FQuadrotorMworksFrame& OutFrame) const;
    FVector ParseVector3(const TSharedPtr<FJsonObject>& Object, const FString& FieldName, const FVector& Fallback) const;

    FSocket* Socket = nullptr;
    TSharedPtr<FUdpSocketReceiver> Receiver;
    bool bLoggedFirstFrame = false;
    double ReceiveRateWindowStartSeconds = 0.0;
    int32 ReceivedFramesInWindow = 0;
    int32 SequenceGapsInWindow = 0;
    int64 ReceivedPayloadBytesInWindow = 0;
    int32 LastReceivedSequence = TNumericLimits<int32>::Min();
    FString ActiveStreamId;
    double LastAcceptedFrameSeconds = 0.0;
    double LastRejectedFrameLogSeconds = 0.0;

    mutable FCriticalSection FrameMutex;
    FQuadrotorMworksFrame LatestFrame;
};
