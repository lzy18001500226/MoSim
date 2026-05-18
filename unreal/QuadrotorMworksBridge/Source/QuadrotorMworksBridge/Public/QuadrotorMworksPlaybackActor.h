#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "QuadrotorMworksPlaybackActor.generated.h"

class UQuadrotorMworksPlaybackComponent;
class UQuadrotorMworksUdpReceiverComponent;
class UMaterialInterface;
class UStaticMeshComponent;

UCLASS()
class QUADROTORMWORKSBRIDGE_API AQuadrotorMworksPlaybackActor : public AActor
{
    GENERATED_BODY()

public:
    AQuadrotorMworksPlaybackActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    USceneComponent* SceneRoot = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* BodyMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh1 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh2 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh3 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh4 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UQuadrotorMworksUdpReceiverComponent* Receiver = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UQuadrotorMworksPlaybackComponent* Playback = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    UMaterialInterface* BaseMaterial = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor BodyColor = FLinearColor(0.10f, 0.55f, 1.0f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor PropellerColor = FLinearColor(0.05f, 0.05f, 0.05f, 1.0f);

    UFUNCTION(BlueprintCallable, Category = "MWORKS")
    void ApplyDefaultMaterials();

protected:
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void Tick(float DeltaSeconds) override;

private:
    void ApplyPropellerVisuals() const;
};
