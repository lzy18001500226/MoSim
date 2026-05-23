#include "MworksReviewCameraPawn.h"

#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Components/InputComponent.h"
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
        SetReviewInputMode(PlayerController);
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS review camera active. Controls: hold RMB+mouse look, WASD move, Q/E down/up, arrows look, Shift fast, Ctrl slow."));
}

void AMworksReviewCameraPawn::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);

    if (APlayerController* PlayerController = Cast<APlayerController>(NewController))
    {
        SetReviewInputMode(PlayerController);
    }
}

void AMworksReviewCameraPawn::PawnClientRestart()
{
    Super::PawnClientRestart();

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        SetReviewInputMode(PlayerController);
    }
}

void AMworksReviewCameraPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ApplyReviewInput(DeltaSeconds);
}

void AMworksReviewCameraPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    check(PlayerInputComponent);
    PlayerInputComponent->BindAxis(TEXT("MworksReviewMoveForward"), this, &AMworksReviewCameraPawn::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MworksReviewMoveRight"), this, &AMworksReviewCameraPawn::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("MworksReviewMoveUp"), this, &AMworksReviewCameraPawn::MoveUp);
    PlayerInputComponent->BindAxis(TEXT("MworksReviewTurn"), this, &AMworksReviewCameraPawn::TurnKeyboard);
    PlayerInputComponent->BindAxis(TEXT("MworksReviewLookUp"), this, &AMworksReviewCameraPawn::LookUpKeyboard);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &AMworksReviewCameraPawn::MouseTurn);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &AMworksReviewCameraPawn::MouseLookUp);

    UE_LOG(LogTemp, Display, TEXT("MWORKS review camera input bindings installed."));
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

    const float PolledForwardAxis = AxisFromKeys(PlayerController, EKeys::W, EKeys::S);
    const float PolledRightAxis = AxisFromKeys(PlayerController, EKeys::D, EKeys::A);
    const float PolledUpAxis = AxisFromKeys(PlayerController, EKeys::E, EKeys::Q);
    const float ForwardAxis = FMath::Abs(MoveForwardAxis) > KINDA_SMALL_NUMBER ? MoveForwardAxis : PolledForwardAxis;
    const float RightAxis = FMath::Abs(MoveRightAxis) > KINDA_SMALL_NUMBER ? MoveRightAxis : PolledRightAxis;
    const float UpAxis = FMath::Abs(MoveUpAxis) > KINDA_SMALL_NUMBER ? MoveUpAxis : PolledUpAxis;

    FVector Move =
        ForwardAxis * Forward +
        RightAxis * Right +
        UpAxis * Up;

    bool bMoved = false;
    if (!Move.IsNearlyZero())
    {
        Move.Normalize();
        AddActorWorldOffset(Move * MoveSpeedCmPerSec * SpeedScale * DeltaSeconds, false);
        bMoved = true;
    }

    const float PolledTurnAxis = AxisFromKeys(PlayerController, EKeys::Right, EKeys::Left);
    const float PolledLookUpAxis = AxisFromKeys(PlayerController, EKeys::Up, EKeys::Down);
    const float KeyboardTurnAxis = FMath::Abs(TurnKeyboardAxis) > KINDA_SMALL_NUMBER ? TurnKeyboardAxis : PolledTurnAxis;
    const float KeyboardLookAxis = FMath::Abs(LookUpKeyboardAxis) > KINDA_SMALL_NUMBER ? LookUpKeyboardAxis : PolledLookUpAxis;
    float YawDelta = KeyboardTurnAxis * KeyboardLookDegPerSec * DeltaSeconds;
    float PitchDelta = KeyboardLookAxis * KeyboardLookDegPerSec * DeltaSeconds;

    if (PlayerController->IsInputKeyDown(EKeys::RightMouseButton) || PlayerController->IsInputKeyDown(EKeys::LeftMouseButton))
    {
        float MouseDeltaX = 0.0f;
        float MouseDeltaY = 0.0f;
        PlayerController->GetInputMouseDelta(MouseDeltaX, MouseDeltaY);
        YawDelta += (MouseTurnAxis + MouseDeltaX) * MouseLookSensitivityDeg;
        PitchDelta -= (MouseLookUpAxis + MouseDeltaY) * MouseLookSensitivityDeg;
    }

    bool bRotated = false;
    if (FMath::Abs(YawDelta) > KINDA_SMALL_NUMBER || FMath::Abs(PitchDelta) > KINDA_SMALL_NUMBER)
    {
        FRotator NewRotation = GetActorRotation();
        NewRotation.Yaw += YawDelta;
        NewRotation.Pitch = FMath::Clamp(NewRotation.Pitch + PitchDelta, -89.0f, 89.0f);
        NewRotation.Roll = 0.0f;
        SetActorRotation(NewRotation);
        bRotated = true;
    }

    LogReviewCameraMotionIfNeeded(bMoved, bRotated);
}

void AMworksReviewCameraPawn::SetReviewInputMode(APlayerController* PlayerController)
{
    if (!PlayerController)
    {
        return;
    }

    PlayerController->SetViewTarget(this);
    PlayerController->bShowMouseCursor = false;
    PlayerController->bEnableClickEvents = false;
    PlayerController->bEnableMouseOverEvents = false;
    PlayerController->SetIgnoreMoveInput(false);
    PlayerController->SetIgnoreLookInput(false);

    FInputModeGameOnly InputMode;
    InputMode.SetConsumeCaptureMouseDown(false);
    PlayerController->SetInputMode(InputMode);
}

void AMworksReviewCameraPawn::MoveForward(float Value)
{
    MoveForwardAxis = Value;
}

void AMworksReviewCameraPawn::MoveRight(float Value)
{
    MoveRightAxis = Value;
}

void AMworksReviewCameraPawn::MoveUp(float Value)
{
    MoveUpAxis = Value;
}

void AMworksReviewCameraPawn::TurnKeyboard(float Value)
{
    TurnKeyboardAxis = Value;
}

void AMworksReviewCameraPawn::LookUpKeyboard(float Value)
{
    LookUpKeyboardAxis = Value;
}

void AMworksReviewCameraPawn::MouseTurn(float Value)
{
    MouseTurnAxis = Value;
}

void AMworksReviewCameraPawn::MouseLookUp(float Value)
{
    MouseLookUpAxis = Value;
}

void AMworksReviewCameraPawn::LogReviewCameraMotionIfNeeded(bool bMoved, bool bRotated)
{
    if (!bMoved && !bRotated)
    {
        return;
    }

    const UWorld* World = GetWorld();
    const double NowSeconds = World ? World->GetTimeSeconds() : 0.0;
    if (NowSeconds - LastMotionLogTimeSeconds < 0.75)
    {
        return;
    }
    LastMotionLogTimeSeconds = NowSeconds;

    const FVector Location = GetActorLocation();
    const FRotator Rotation = GetActorRotation();
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS review camera input accepted moved=%d rotated=%d location=(%.1f, %.1f, %.1f) rotation=(pitch=%.1f, yaw=%.1f, roll=%.1f)"),
        bMoved ? 1 : 0,
        bRotated ? 1 : 0,
        Location.X,
        Location.Y,
        Location.Z,
        Rotation.Pitch,
        Rotation.Yaw,
        Rotation.Roll);
}
