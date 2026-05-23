#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MworksReviewCameraPawn.generated.h"

class UCameraComponent;
class USceneComponent;

UCLASS()
class MWORKSUNREALRENDERER_API AMworksReviewCameraPawn : public APawn
{
    GENERATED_BODY()

public:
    AMworksReviewCameraPawn();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    FVector InitialCameraLocation = FVector(-3200.0, -2200.0, 1300.0);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    FRotator InitialCameraRotation = FRotator(-22.0, 36.0, 0.0);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    float MoveSpeedCmPerSec = 900.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    float FastMoveMultiplier = 4.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    float SlowMoveMultiplier = 0.25f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    float MouseLookSensitivityDeg = 0.12f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    float KeyboardLookDegPerSec = 70.0f;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS Review Camera")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS Review Camera")
    TObjectPtr<UCameraComponent> ReviewCamera;

private:
    void ApplyReviewInput(float DeltaSeconds);
    float AxisFromKeys(class APlayerController* PlayerController, const FKey& PositiveKey, const FKey& NegativeKey) const;
};
