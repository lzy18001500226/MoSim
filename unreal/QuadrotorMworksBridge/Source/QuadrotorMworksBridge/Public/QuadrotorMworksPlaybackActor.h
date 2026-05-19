#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "QuadrotorMworksPlaybackActor.generated.h"

class UQuadrotorMworksPlaybackComponent;
class UQuadrotorMworksUdpReceiverComponent;
class UMaterialInterface;
class USplineComponent;
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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    USplineComponent* LocalPlanSpline = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    USplineComponent* TrajectoryTrailSpline = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UStaticMeshComponent* ReferenceMarker = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UStaticMeshComponent* RadarDirectionMarker = nullptr;

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

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor ReferenceColor = FLinearColor(1.0f, 0.88f, 0.1f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor RadarColor = FLinearColor(0.0f, 0.75f, 1.0f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bUpdateVisualHelpers = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "1"))
    int32 MaxSplinePoints = 600;

    UFUNCTION(BlueprintCallable, Category = "MWORKS")
    void ApplyDefaultMaterials();

protected:
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void Tick(float DeltaSeconds) override;

private:
    void ApplyPropellerVisuals() const;
    void UpdateVisualHelpers() const;
    void UpdateSplineFromPoints(USplineComponent* Spline, const TArray<FVector>& Points) const;
};
