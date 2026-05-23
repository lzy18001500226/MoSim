#include "MworksReviewCameraPawn.h"

#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

AMworksReviewCameraPawn::AMworksReviewCameraPawn()
{
    PrimaryActorTick.bCanEverTick = true;
    AutoPossessPlayer = EAutoReceiveInput::Player0;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    RootComponent = SceneRoot;

    ReviewCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ReviewCamera"));
    ReviewCamera->SetupAttachment(SceneRoot);
    ReviewCamera->bUsePawnControlRotation = false;
}

void AMworksReviewCameraPawn::BeginPlay()
{
    Super::BeginPlay();

    SetActorLocationAndRotation(InitialCameraLocation, InitialCameraRotation);

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        PlayerController->SetViewTarget(this);
        PlayerController->bShowMouseCursor = false;
        PlayerController->SetInputMode(FInputModeGameOnly());
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS review camera active. Controls: hold RMB+mouse look, WASD move, Q/E down/up, arrows look, Shift fast, Ctrl slow."));
}

void AMworksReviewCameraPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ApplyReviewInput(DeltaSeconds);
}

float AMworksReviewCameraPawn::AxisFromKeys(APlayerController* PlayerController, const FKey& PositiveKey, const FKey& NegativeKey) const
{
    if (!PlayerController)
    {
        return 0.0f;
    }

    const float Positive = PlayerController->IsInputKeyDown(PositiveKey) ? 1.0f : 0.0f;
    const float Negative = PlayerController->IsInputKeyDown(NegativeKey) ? 1.0f : 0.0f;
    return Positive - Negative;
}

void AMworksReviewCameraPawn::ApplyReviewInput(float DeltaSeconds)
{
    APlayerController* PlayerController = Cast<APlayerController>(GetController());
    if (!PlayerController)
    {
        return;
    }

    float SpeedScale = 1.0f;
    if (PlayerController->IsInputKeyDown(EKeys::LeftShift) || PlayerController->IsInputKeyDown(EKeys::RightShift))
    {
        SpeedScale *= FastMoveMultiplier;
    }
    if (PlayerController->IsInputKeyDown(EKeys::LeftControl) || PlayerController->IsInputKeyDown(EKeys::RightControl))
    {
        SpeedScale *= SlowMoveMultiplier;
    }

    const FRotator Rotation = GetActorRotation();
    const FVector Forward = Rotation.Vector();
    const FVector Right = FRotationMatrix(Rotation).GetScaledAxis(EAxis::Y);
    const FVector Up = FVector::UpVector;

    FVector Move =
        AxisFromKeys(PlayerController, EKeys::W, EKeys::S) * Forward +
        AxisFromKeys(PlayerController, EKeys::D, EKeys::A) * Right +
        AxisFromKeys(PlayerController, EKeys::E, EKeys::Q) * Up;

    if (!Move.IsNearlyZero())
    {
        Move.Normalize();
        AddActorWorldOffset(Move * MoveSpeedCmPerSec * SpeedScale * DeltaSeconds, false);
    }

    float YawDelta = AxisFromKeys(PlayerController, EKeys::Right, EKeys::Left) * KeyboardLookDegPerSec * DeltaSeconds;
    float PitchDelta = AxisFromKeys(PlayerController, EKeys::Up, EKeys::Down) * KeyboardLookDegPerSec * DeltaSeconds;

    if (PlayerController->IsInputKeyDown(EKeys::RightMouseButton) || PlayerController->IsInputKeyDown(EKeys::LeftMouseButton))
    {
        float MouseDeltaX = 0.0f;
        float MouseDeltaY = 0.0f;
        PlayerController->GetInputMouseDelta(MouseDeltaX, MouseDeltaY);
        YawDelta += MouseDeltaX * MouseLookSensitivityDeg;
        PitchDelta -= MouseDeltaY * MouseLookSensitivityDeg;
    }

    if (FMath::Abs(YawDelta) > KINDA_SMALL_NUMBER || FMath::Abs(PitchDelta) > KINDA_SMALL_NUMBER)
    {
        FRotator NewRotation = GetActorRotation();
        NewRotation.Yaw += YawDelta;
        NewRotation.Pitch = FMath::Clamp(NewRotation.Pitch + PitchDelta, -89.0f, 89.0f);
        NewRotation.Roll = 0.0f;
        SetActorRotation(NewRotation);
    }
}
