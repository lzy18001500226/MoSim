#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "Interfaces/IPv4/IPv4Endpoint.h"
#include "QuadrotorMworksTypes.h"
#include "QuadrotorMworksUdpCommandSenderComponent.generated.h"

class FSocket;

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorMworksUdpCommandSenderComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorMworksUdpCommandSenderComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Command")
    FString RemoteAddress = TEXT("127.0.0.1");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Command")
    int32 RemotePort = 5015;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Command")
    FString RunId = TEXT("ue_experiment_console");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Command")
    FString RequestedBy = TEXT("ue_experiment_console");

    UFUNCTION(BlueprintCallable, Category = "MWORKS Command")
    FQuadrotorMworksCommandResult SendCommand(
        const FString& CommandKind,
        const FString& PayloadJson,
        const FQuadrotorMworksCommandGuard& Guard);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Command")
    FQuadrotorMworksCommandResult BuildCommandPacket(
        const FString& CommandKind,
        const FString& PayloadJson,
        const FQuadrotorMworksCommandGuard& Guard) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Command")
    bool BuildPendingRequestCaptureJson(
        const FQuadrotorMworksCommandResult& CommandResult,
        FString& PendingRequestCaptureJson,
        FString& RejectReason) const;

protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    bool EnsureSocket();
    bool IsAllowedCommandKind(const FString& CommandKind) const;
    bool IsForbiddenCommandKind(const FString& CommandKind) const;
    bool RequiresRos2Ack(const FString& CommandKind) const;
    FString MakeRequestId() const;

    FSocket* SenderSocket = nullptr;
    mutable int32 Sequence = 0;
};
