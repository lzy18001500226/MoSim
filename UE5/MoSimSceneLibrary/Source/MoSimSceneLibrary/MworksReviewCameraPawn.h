#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "MworksReviewCameraPawn.generated.h"

class UCameraComponent;
class USceneComponent;

UCLASS()
class MOSIMSCENELIBRARY_API AMworksReviewCameraPawn : public APawn
{
    GENERATED_BODY()

public:
    AMworksReviewCameraPawn();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
    virtual void PossessedBy(AController* NewController) override;
    virtual void PawnClientRestart() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    FVector InitialCameraLocation = FVector(-3600.0, -2800.0, 1450.0);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Review Camera")
    FRotator InitialCameraRotation = FRotator(-20.0, 38.0, 0.0);

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
    void SetReviewInputMode(class APlayerController* PlayerController);
    void MoveForward(float Value);
    void MoveRight(float Value);
    void MoveUp(float Value);
    void TurnKeyboard(float Value);
    void LookUpKeyboard(float Value);
    void MouseTurn(float Value);
    void MouseLookUp(float Value);
    void LogReviewCameraMotionIfNeeded(bool bMoved, bool bRotated);

    float MoveForwardAxis = 0.0f;
    float MoveRightAxis = 0.0f;
    float MoveUpAxis = 0.0f;
    float TurnKeyboardAxis = 0.0f;
    float LookUpKeyboardAxis = 0.0f;
    float MouseTurnAxis = 0.0f;
    float MouseLookUpAxis = 0.0f;
    double LastMotionLogTimeSeconds = -1000.0;
};
