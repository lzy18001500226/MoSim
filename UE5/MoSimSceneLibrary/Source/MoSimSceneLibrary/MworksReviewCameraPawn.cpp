#include "MworksReviewCameraPawn.h"

#include "Camera/CameraComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Components/InputComponent.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Engine/HitResult.h"
#include "Framework/Application/SlateApplication.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

AMworksReviewCameraPawn::AMworksReviewCameraPawn()
{
    PrimaryActorTick.bCanEverTick = true;
    AutoPossessPlayer = EAutoReceiveInput::Player0;

    CollisionRoot = CreateDefaultSubobject<USphereComponent>(TEXT("CollisionRoot"));
    CollisionRoot->InitSphereRadius(ReviewCollisionRadiusCm);
    CollisionRoot->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    CollisionRoot->SetCollisionObjectType(ECC_Pawn);
    CollisionRoot->SetCollisionResponseToAllChannels(ECR_Block);
    CollisionRoot->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
    CollisionRoot->SetGenerateOverlapEvents(false);
    CollisionRoot->SetCanEverAffectNavigation(false);
    RootComponent = CollisionRoot;

    ReviewCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ReviewCamera"));
    ReviewCamera->SetupAttachment(CollisionRoot);
    ReviewCamera->bUsePawnControlRotation = false;

    ReviewHeadLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("ReviewHeadLight"));
    ReviewHeadLight->SetupAttachment(ReviewCamera);
    ReviewHeadLight->SetRelativeLocation(FVector::ZeroVector);
    ReviewHeadLight->SetUseInverseSquaredFalloff(false);
    ReviewHeadLight->SetLightFalloffExponent(2.0f);
    ReviewHeadLight->SetInverseExposureBlend(1.0f);
    ReviewHeadLight->SetIntensity(ReviewHeadLightIntensity);
    ReviewHeadLight->SetAttenuationRadius(ReviewHeadLightAttenuationRadius);
    ReviewHeadLight->SetCastShadows(false);
    ReviewHeadLight->SetLightColor(FLinearColor::White);
}

void AMworksReviewCameraPawn::BeginPlay()
{
    Super::BeginPlay();

    ApplySceneDefaultCameraPreset();
    ApplyCommandLineOverrides();
    if (CollisionRoot)
    {
        CollisionRoot->SetSphereRadius(ReviewCollisionRadiusCm, true);
        CollisionRoot->SetCollisionEnabled(bEnableReviewCollision ? ECollisionEnabled::QueryOnly : ECollisionEnabled::NoCollision);
    }
    SetActorLocationAndRotation(InitialCameraLocation, InitialCameraRotation);
    if (ReviewHeadLight)
    {
        ReviewHeadLight->SetVisibility(bEnableHeadLightInDayReview, true);
        ReviewHeadLight->SetIntensity(ReviewHeadLightIntensity);
        ReviewHeadLight->SetAttenuationRadius(ReviewHeadLightAttenuationRadius);
    }

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        ApplyReviewInputMode(PlayerController);
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS review camera active at location=(%.1f, %.1f, %.1f) rotation=(pitch=%.1f, yaw=%.1f, roll=%.1f) head_light=%s. Controls: N near, M far, arrows orbit, Q cycle formation/UAV views."),
        InitialCameraLocation.X,
        InitialCameraLocation.Y,
        InitialCameraLocation.Z,
        InitialCameraRotation.Pitch,
        InitialCameraRotation.Yaw,
        InitialCameraRotation.Roll,
        bEnableHeadLightInDayReview ? TEXT("true") : TEXT("false"));

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS review camera collision %s radius=%.1f cm strict_sweep=%s. Movement sweep prevents visual review from passing through collidable scene geometry."),
        bEnableReviewCollision ? TEXT("enabled") : TEXT("disabled"),
        ReviewCollisionRadiusCm,
        bUseStrictReviewCollisionSweep ? TEXT("true") : TEXT("false"));
}

void AMworksReviewCameraPawn::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);

    if (APlayerController* PlayerController = Cast<APlayerController>(NewController))
    {
        ApplyReviewInputMode(PlayerController);
    }
}

void AMworksReviewCameraPawn::PawnClientRestart()
{
    Super::PawnClientRestart();

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        ApplyReviewInputMode(PlayerController);
    }
}

void AMworksReviewCameraPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bFollowTarget && (FollowTarget || FollowTargets.Num() > 0))
    {
        ApplyFollowTarget(DeltaSeconds);
    }
    else
    {
        ApplyReviewInput(DeltaSeconds);
    }
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
    PlayerInputComponent->BindAxis(TEXT("MworksReviewZoom"), this, &AMworksReviewCameraPawn::AdjustFollowDistance);
    PlayerInputComponent->BindAction(TEXT("MworksReviewCycleTarget"), IE_Pressed, this, &AMworksReviewCameraPawn::CycleFollowView);
    PlayerInputComponent->BindAction(TEXT("MworksReviewZoomIn"), IE_Pressed, this, &AMworksReviewCameraPawn::ZoomFollowIn);
    PlayerInputComponent->BindAction(TEXT("MworksReviewZoomOut"), IE_Pressed, this, &AMworksReviewCameraPawn::ZoomFollowOut);
    PlayerInputComponent->BindAction(TEXT("MworksReviewOrbitLeft"), IE_Pressed, this, &AMworksReviewCameraPawn::NudgeFollowLeft);
    PlayerInputComponent->BindAction(TEXT("MworksReviewOrbitRight"), IE_Pressed, this, &AMworksReviewCameraPawn::NudgeFollowRight);
    PlayerInputComponent->BindAction(TEXT("MworksReviewOrbitUp"), IE_Pressed, this, &AMworksReviewCameraPawn::NudgeFollowUp);
    PlayerInputComponent->BindAction(TEXT("MworksReviewOrbitDown"), IE_Pressed, this, &AMworksReviewCameraPawn::NudgeFollowDown);
    PlayerInputComponent->BindAction(TEXT("MworksReviewReleasePointer"), IE_Pressed, this, &AMworksReviewCameraPawn::ReleaseReviewPointer);

    UE_LOG(LogTemp, Display, TEXT("MWORKS review camera input bindings installed."));
}

void AMworksReviewCameraPawn::ApplySceneDefaultCameraPreset()
{
    const UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    const FString MapName = World->GetMapName();
    if (MapName.Contains(TEXT("Demonstration")))
    {
        InitialCameraLocation = FVector(-5733.0f, 2423.0f, 280.0f);
        InitialCameraRotation = FRotator(-12.0f, 0.0f, 0.0f);
    }
    else if (MapName.Contains(TEXT("DerelictCorridor")))
    {
        InitialCameraLocation = FVector(8704.0f, -2240.0f, 220.0f);
        InitialCameraRotation = FRotator(-8.0f, 90.0f, 0.0f);
    }
}

void AMworksReviewCameraPawn::ApplyCommandLineOverrides()
{
    FString ParsedLocationText;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraLocation="), ParsedLocationText))
    {
        ParsedLocationText.ReplaceInline(TEXT(","), TEXT(" "));
        FVector ParsedLocation = InitialCameraLocation;
        if (ParsedLocation.InitFromString(ParsedLocationText))
        {
            InitialCameraLocation = ParsedLocation;
        }
    }

    FString ParsedRotationText;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraRotation="), ParsedRotationText))
    {
        ParsedRotationText.ReplaceInline(TEXT(","), TEXT(" "));
        FRotator ParsedRotation = InitialCameraRotation;
        if (ParsedRotation.InitFromString(ParsedRotationText))
        {
            InitialCameraRotation = ParsedRotation;
        }
    }

    float ParsedFloat = 0.0f;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraX="), ParsedFloat))
    {
        InitialCameraLocation.X = ParsedFloat;
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraY="), ParsedFloat))
    {
        InitialCameraLocation.Y = ParsedFloat;
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraZ="), ParsedFloat))
    {
        InitialCameraLocation.Z = ParsedFloat;
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraPitch="), ParsedFloat))
    {
        InitialCameraRotation.Pitch = ParsedFloat;
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraYaw="), ParsedFloat))
    {
        InitialCameraRotation.Yaw = ParsedFloat;
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCameraRoll="), ParsedFloat))
    {
        InitialCameraRotation.Roll = ParsedFloat;
    }

    float ParsedMoveSpeed = MoveSpeedCmPerSec;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewMoveSpeed="), ParsedMoveSpeed))
    {
        MoveSpeedCmPerSec = FMath::Max(1.0f, ParsedMoveSpeed);
    }

    bEnableHeadLightInDayReview =
        bEnableHeadLightInDayReview &&
        !FParse::Param(FCommandLine::Get(), TEXT("MoSimNoReviewHeadLight"));

    float ParsedHeadLightIntensity = ReviewHeadLightIntensity;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewHeadLightIntensity="), ParsedHeadLightIntensity))
    {
        ReviewHeadLightIntensity = FMath::Max(0.0f, ParsedHeadLightIntensity);
    }

    float ParsedHeadLightRadius = ReviewHeadLightAttenuationRadius;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewHeadLightRadius="), ParsedHeadLightRadius))
    {
        ReviewHeadLightAttenuationRadius = FMath::Max(100.0f, ParsedHeadLightRadius);
    }

    bEnableReviewCollision =
        bEnableReviewCollision &&
        !FParse::Param(FCommandLine::Get(), TEXT("MoSimNoReviewCollision"));

    float ParsedCollisionRadius = ReviewCollisionRadiusCm;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCollisionRadius="), ParsedCollisionRadius))
    {
        ReviewCollisionRadiusCm = FMath::Max(5.0f, ParsedCollisionRadius);
    }

    bUseStrictReviewCollisionSweep =
        bUseStrictReviewCollisionSweep &&
        !FParse::Param(FCommandLine::Get(), TEXT("MoSimNoStrictReviewCollision"));

    float ParsedStopPadding = ReviewCollisionStopPaddingCm;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewCollisionStopPadding="), ParsedStopPadding))
    {
        ReviewCollisionStopPaddingCm = FMath::Max(0.0f, ParsedStopPadding);
    }

    bFollowTarget = bFollowTarget || FParse::Param(FCommandLine::Get(), TEXT("MoSimFollowPlaybackCamera"));

    FString ParsedFollowOffsetText;
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraOffset="), ParsedFollowOffsetText))
    {
        ParsedFollowOffsetText.ReplaceInline(TEXT(","), TEXT(" "));
        FVector ParsedOffset = FollowOffsetCm;
        if (ParsedOffset.InitFromString(ParsedFollowOffsetText))
        {
            FollowOffsetCm = ParsedOffset;
        }
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraBackCm="), ParsedFloat))
    {
        FollowOffsetCm.Y = FMath::Max(10.0f, ParsedFloat);
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraRightCm="), ParsedFloat))
    {
        FollowOffsetCm.X = ParsedFloat;
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraUpCm="), ParsedFloat))
    {
        FollowOffsetCm.Z = FMath::Max(10.0f, ParsedFloat);
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraPitch="), ParsedFloat))
    {
        FollowPitchDeg = FMath::Clamp(ParsedFloat, -89.0f, 10.0f);
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraLocationInterpSpeed="), ParsedFloat))
    {
        FollowLocationInterpSpeed = FMath::Max(0.0f, ParsedFloat);
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraRotationInterpSpeed="), ParsedFloat))
    {
        FollowRotationInterpSpeed = FMath::Max(0.0f, ParsedFloat);
    }
    if (FParse::Value(FCommandLine::Get(), TEXT("MoSimFollowCameraOrbitSpeed="), ParsedFloat))
    {
        FollowOrbitDegPerSec = FMath::Max(1.0f, ParsedFloat);
    }
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

bool AMworksReviewCameraPawn::ComputeCollisionConstrainedDelta(const FVector& DesiredDelta, FVector& SafeDelta, FHitResult& BlockingHit)
{
    SafeDelta = DesiredDelta;
    BlockingHit = FHitResult();

    if (!bEnableReviewCollision || !bUseStrictReviewCollisionSweep || DesiredDelta.IsNearlyZero())
    {
        return false;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(MworksReviewCameraStrictSweep), false, this);
    QueryParams.bTraceComplex = false;
    QueryParams.AddIgnoredActor(this);

    const FVector Start = GetActorLocation();
    const FVector End = Start + DesiredDelta;
    const FCollisionShape Sphere = FCollisionShape::MakeSphere(ReviewCollisionRadiusCm);

    FCollisionObjectQueryParams ObjectParams;
    ObjectParams.AddObjectTypesToQuery(ECC_WorldStatic);
    ObjectParams.AddObjectTypesToQuery(ECC_WorldDynamic);

    const bool bHitObject = World->SweepSingleByObjectType(
        BlockingHit,
        Start,
        End,
        FQuat::Identity,
        ObjectParams,
        Sphere,
        QueryParams);

    if (!bHitObject)
    {
        FHitResult VisibilityHit;
        const bool bHitVisibility = World->SweepSingleByChannel(
            VisibilityHit,
            Start,
            End,
            FQuat::Identity,
            ECC_Visibility,
            Sphere,
            QueryParams);
        if (bHitVisibility)
        {
            BlockingHit = VisibilityHit;
        }
    }

    if (!BlockingHit.bBlockingHit)
    {
        return false;
    }

    const float DesiredDistance = DesiredDelta.Size();
    const float AllowedDistance = FMath::Max(0.0f, BlockingHit.Distance - ReviewCollisionStopPaddingCm);
    SafeDelta = DesiredDelta.GetSafeNormal() * FMath::Min(DesiredDistance, AllowedDistance);
    return true;
}

void AMworksReviewCameraPawn::SetFollowTarget(AActor* NewFollowTarget)
{
    FollowTarget = NewFollowTarget;
    FollowTargets.Reset();
    FollowViewIndex = 0;
    bFollowTarget = FollowTarget != nullptr;
    LastFollowLogTimeSeconds = -1000.0;
}

void AMworksReviewCameraPawn::SetFollowTargets(const TArray<AActor*>& NewFollowTargets)
{
    TArray<AActor*> ValidTargets;
    for (AActor* Target : NewFollowTargets)
    {
        if (IsValid(Target))
        {
            ValidTargets.Add(Target);
        }
    }

    bool bTargetsChanged = ValidTargets.Num() != FollowTargets.Num();
    if (!bTargetsChanged)
    {
        for (int32 Index = 0; Index < ValidTargets.Num(); ++Index)
        {
            if (FollowTargets[Index] != ValidTargets[Index])
            {
                bTargetsChanged = true;
                break;
            }
        }
    }

    if (bTargetsChanged)
    {
        FollowTargets.Reset(ValidTargets.Num());
        for (AActor* Target : ValidTargets)
        {
            FollowTargets.Add(Target);
        }
        FollowViewIndex = 0;
        LastFollowLogTimeSeconds = -1000.0;
    }

    FollowTarget = nullptr;
    bFollowTarget = FollowTargets.Num() > 0;
}

void AMworksReviewCameraPawn::CycleFollowView()
{
    if (FollowTargets.Num() <= 1)
    {
        return;
    }

    FollowViewIndex = (FollowViewIndex + 1) % (FollowTargets.Num() + 1);
    LastFollowLogTimeSeconds = -1000.0;
    const FString ViewLabel = FollowViewIndex == 0
        ? TEXT("formation_overview")
        : FollowTargets[FollowViewIndex - 1]->GetName();
    UE_LOG(LogTemp, Display, TEXT("MWORKS review camera switched follow view=%s index=%d"), *ViewLabel, FollowViewIndex);
}

bool AMworksReviewCameraPawn::ResolveFollowPose(FVector& TargetLocation, FRotator& TargetRotation, FString& TargetLabel) const
{
    if (FollowTargets.Num() > 0)
    {
        if (FollowViewIndex > 0 && FollowViewIndex <= FollowTargets.Num() && IsValid(FollowTargets[FollowViewIndex - 1]))
        {
            const AActor* SelectedTarget = FollowTargets[FollowViewIndex - 1];
            TargetLocation = SelectedTarget->GetActorLocation();
            TargetRotation = SelectedTarget->GetActorRotation();
            TargetLabel = SelectedTarget->GetName();
            return true;
        }

        FVector LocationSum = FVector::ZeroVector;
        FVector ForwardSum = FVector::ZeroVector;
        int32 ValidCount = 0;
        for (const TObjectPtr<AActor>& Target : FollowTargets)
        {
            if (!IsValid(Target))
            {
                continue;
            }
            LocationSum += Target->GetActorLocation();
            ForwardSum += Target->GetActorForwardVector().GetSafeNormal2D();
            ++ValidCount;
        }
        if (ValidCount == 0)
        {
            return false;
        }

        TargetLocation = LocationSum / static_cast<float>(ValidCount);
        const float FallbackYaw = IsValid(FollowTargets[0]) ? FollowTargets[0]->GetActorRotation().Yaw : 0.0f;
        const float MeanYaw = ForwardSum.IsNearlyZero() ? FallbackYaw : ForwardSum.Rotation().Yaw;
        TargetRotation = FRotator(0.0f, MeanYaw, 0.0f);
        TargetLabel = FString::Printf(TEXT("formation_overview_%d_uavs"), ValidCount);
        return true;
    }

    if (IsValid(FollowTarget))
    {
        TargetLocation = FollowTarget->GetActorLocation();
        TargetRotation = FollowTarget->GetActorRotation();
        TargetLabel = FollowTarget->GetName();
        return true;
    }
    return false;
}

void AMworksReviewCameraPawn::ApplyFollowTarget(float DeltaSeconds)
{
    FVector TargetLocation = FVector::ZeroVector;
    FRotator TargetRotation = FRotator::ZeroRotator;
    FString TargetLabel;
    if (!ResolveFollowPose(TargetLocation, TargetRotation, TargetLabel))
    {
        return;
    }

    ApplyFollowOrbitInput(DeltaSeconds);

    const FRotator FollowYawRotation(0.0f, TargetRotation.Yaw, 0.0f);
    const FVector DesiredLocation = TargetLocation + FollowYawRotation.RotateVector(FollowOffsetCm);
    const FRotator DesiredRotation = (TargetLocation - DesiredLocation).Rotation();

    const FVector NewLocation = FollowLocationInterpSpeed <= 0.0f
        ? DesiredLocation
        : FMath::VInterpTo(GetActorLocation(), DesiredLocation, DeltaSeconds, FollowLocationInterpSpeed);
    const FRotator NewRotation = FollowRotationInterpSpeed <= 0.0f
        ? DesiredRotation
        : FMath::RInterpTo(GetActorRotation(), DesiredRotation, DeltaSeconds, FollowRotationInterpSpeed);

    SetActorLocationAndRotation(NewLocation, NewRotation);

    if (UWorld* World = GetWorld())
    {
        const double NowSeconds = World->GetTimeSeconds();
        if (NowSeconds - LastFollowLogTimeSeconds > 2.0)
        {
            LastFollowLogTimeSeconds = NowSeconds;
            UE_LOG(
                LogTemp,
                Display,
                TEXT("MWORKS review camera following playback target=%s target_location=%s target_yaw=%.2f offset=%s camera_location=%s camera_rotation=%s"),
                *TargetLabel,
                *TargetLocation.ToCompactString(),
                TargetRotation.Yaw,
                *FollowOffsetCm.ToCompactString(),
                *NewLocation.ToCompactString(),
                *NewRotation.ToCompactString());
        }
    }
}

void AMworksReviewCameraPawn::ApplyFollowOrbitInput(float DeltaSeconds)
{
    APlayerController* PlayerController = Cast<APlayerController>(GetController());
    if (!PlayerController || FollowOffsetCm.IsNearlyZero())
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

    const float PolledTurnAxis = AxisFromKeys(PlayerController, EKeys::Right, EKeys::Left);
    const float PolledLookUpAxis = AxisFromKeys(PlayerController, EKeys::Up, EKeys::Down);
    const float OrbitYawAxis = FMath::Abs(TurnKeyboardAxis) > KINDA_SMALL_NUMBER ? TurnKeyboardAxis : PolledTurnAxis;
    const float OrbitElevationAxis = FMath::Abs(LookUpKeyboardAxis) > KINDA_SMALL_NUMBER ? LookUpKeyboardAxis : PolledLookUpAxis;
    float MouseDeltaX = 0.0f;
    float MouseDeltaY = 0.0f;
    if (PlayerController->IsInputKeyDown(EKeys::LeftMouseButton) ||
        PlayerController->IsInputKeyDown(EKeys::RightMouseButton))
    {
        PlayerController->GetInputMouseDelta(MouseDeltaX, MouseDeltaY);
    }
    if (FMath::Abs(OrbitYawAxis) <= KINDA_SMALL_NUMBER &&
        FMath::Abs(OrbitElevationAxis) <= KINDA_SMALL_NUMBER &&
        FMath::Abs(MouseDeltaX) <= KINDA_SMALL_NUMBER &&
        FMath::Abs(MouseDeltaY) <= KINDA_SMALL_NUMBER)
    {
        return;
    }

    const float Radius = FollowOffsetCm.Size();
    const float HorizontalRadius = FVector2D(FollowOffsetCm.X, FollowOffsetCm.Y).Size();
    float AzimuthDeg = FMath::RadiansToDegrees(FMath::Atan2(FollowOffsetCm.Y, FollowOffsetCm.X));
    float ElevationDeg = FMath::RadiansToDegrees(FMath::Atan2(FollowOffsetCm.Z, HorizontalRadius));

    AzimuthDeg -= OrbitYawAxis * FollowOrbitDegPerSec * SpeedScale * DeltaSeconds;
    AzimuthDeg -= MouseDeltaX * FollowMouseOrbitSensitivityDeg;
    ElevationDeg = FMath::Clamp(
        ElevationDeg + OrbitElevationAxis * FollowOrbitDegPerSec * SpeedScale * DeltaSeconds +
            MouseDeltaY * FollowMouseOrbitSensitivityDeg,
        FollowMinElevationDeg,
        FollowMaxElevationDeg);

    const float AzimuthRad = FMath::DegreesToRadians(AzimuthDeg);
    const float ElevationRad = FMath::DegreesToRadians(ElevationDeg);
    const float NewHorizontalRadius = Radius * FMath::Cos(ElevationRad);
    FollowOffsetCm = FVector(
        NewHorizontalRadius * FMath::Cos(AzimuthRad),
        NewHorizontalRadius * FMath::Sin(AzimuthRad),
        Radius * FMath::Sin(ElevationRad));

    if (UWorld* World = GetWorld())
    {
        const double NowSeconds = World->GetTimeSeconds();
        if (NowSeconds - LastFollowOrbitLogTimeSeconds > 0.75)
        {
            LastFollowOrbitLogTimeSeconds = NowSeconds;
            UE_LOG(
                LogTemp,
                Display,
                TEXT("MWORKS review camera follow orbit input yaw_axis=%.1f elevation_axis=%.1f mouse_delta=(%.1f, %.1f) radius_cm=%.2f offset=%s"),
                OrbitYawAxis,
                OrbitElevationAxis,
                MouseDeltaX,
                MouseDeltaY,
                Radius,
                *FollowOffsetCm.ToCompactString());
        }
    }
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
        const FVector DesiredDelta = Move * MoveSpeedCmPerSec * SpeedScale * DeltaSeconds;
        FVector SafeDelta = DesiredDelta;
        FHitResult Hit;
        if (ComputeCollisionConstrainedDelta(DesiredDelta, SafeDelta, Hit) && Hit.bBlockingHit)
        {
            LogReviewCollisionIfNeeded(Hit);
        }
        AddActorWorldOffset(SafeDelta, bEnableReviewCollision, &Hit);
        bMoved = true;
        if (Hit.bBlockingHit)
        {
            LogReviewCollisionIfNeeded(Hit);
        }
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

void AMworksReviewCameraPawn::ApplyReviewInputMode(APlayerController* PlayerController)
{
    if (!PlayerController)
    {
        return;
    }

    PlayerController->SetViewTarget(this);
    PlayerController->bShowMouseCursor = true;
    PlayerController->bEnableClickEvents = false;
    PlayerController->bEnableMouseOverEvents = false;
    PlayerController->SetIgnoreMoveInput(false);
    PlayerController->SetIgnoreLookInput(false);

    if (FSlateApplication::IsInitialized())
    {
        FSlateApplication::Get().ReleaseAllPointerCapture();
    }
    FInputModeGameAndUI InputMode;
    InputMode.SetHideCursorDuringCapture(false);
    InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
    PlayerController->SetInputMode(InputMode);
}

void AMworksReviewCameraPawn::ReleaseReviewPointer()
{
    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        ApplyReviewInputMode(PlayerController);
        UE_LOG(LogTemp, Display, TEXT("MWORKS review camera released pointer capture."));
    }
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

void AMworksReviewCameraPawn::AdjustFollowDistance(float Value)
{
    if (!bFollowTarget || FMath::Abs(Value) <= KINDA_SMALL_NUMBER || FollowOffsetCm.IsNearlyZero())
    {
        return;
    }

    const float CurrentDistance = FollowOffsetCm.Size();
    const float NewDistance = FMath::Clamp(
        CurrentDistance - Value * FollowZoomStepCm,
        FollowMinDistanceCm,
        FollowMaxDistanceCm);
    FollowOffsetCm = FollowOffsetCm.GetSafeNormal() * NewDistance;
}

void AMworksReviewCameraPawn::ZoomFollowIn()
{
    AdjustFollowDistance(1.0f);
}

void AMworksReviewCameraPawn::ZoomFollowOut()
{
    AdjustFollowDistance(-1.0f);
}

void AMworksReviewCameraPawn::NudgeFollowLeft()
{
    OrbitFollowBy(FollowOrbitNudgeDeg, 0.0f);
}

void AMworksReviewCameraPawn::NudgeFollowRight()
{
    OrbitFollowBy(-FollowOrbitNudgeDeg, 0.0f);
}

void AMworksReviewCameraPawn::NudgeFollowUp()
{
    OrbitFollowBy(0.0f, -FollowOrbitNudgeDeg);
}

void AMworksReviewCameraPawn::NudgeFollowDown()
{
    OrbitFollowBy(0.0f, FollowOrbitNudgeDeg);
}

void AMworksReviewCameraPawn::OrbitFollowBy(float AzimuthDeltaDeg, float ElevationDeltaDeg)
{
    if (!bFollowTarget || FollowOffsetCm.IsNearlyZero())
    {
        return;
    }

    const float Radius = FollowOffsetCm.Size();
    const float HorizontalRadius = FVector2D(FollowOffsetCm.X, FollowOffsetCm.Y).Size();
    const float AzimuthDeg = FMath::RadiansToDegrees(FMath::Atan2(FollowOffsetCm.Y, FollowOffsetCm.X)) +
        AzimuthDeltaDeg;
    const float ElevationDeg = FMath::Clamp(
        FMath::RadiansToDegrees(FMath::Atan2(FollowOffsetCm.Z, HorizontalRadius)) + ElevationDeltaDeg,
        FollowMinElevationDeg,
        FollowMaxElevationDeg);
    const float AzimuthRad = FMath::DegreesToRadians(AzimuthDeg);
    const float ElevationRad = FMath::DegreesToRadians(ElevationDeg);
    const float NewHorizontalRadius = Radius * FMath::Cos(ElevationRad);
    FollowOffsetCm = FVector(
        NewHorizontalRadius * FMath::Cos(AzimuthRad),
        NewHorizontalRadius * FMath::Sin(AzimuthRad),
        Radius * FMath::Sin(ElevationRad));
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

void AMworksReviewCameraPawn::LogReviewCollisionIfNeeded(const FHitResult& Hit)
{
    const UWorld* World = GetWorld();
    const double NowSeconds = World ? World->GetTimeSeconds() : 0.0;
    if (NowSeconds - LastCollisionLogTimeSeconds < 0.75)
    {
        return;
    }
    LastCollisionLogTimeSeconds = NowSeconds;

    const AActor* HitActor = Hit.GetActor();
    const FString ActorName = HitActor ? HitActor->GetName() : TEXT("<none>");
    const FVector Location = GetActorLocation();
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS review camera collision blocked actor=%s location=(%.1f, %.1f, %.1f) hit=(%.1f, %.1f, %.1f) normal=(%.2f, %.2f, %.2f)"),
        *ActorName,
        Location.X,
        Location.Y,
        Location.Z,
        Hit.ImpactPoint.X,
        Hit.ImpactPoint.Y,
        Hit.ImpactPoint.Z,
        Hit.ImpactNormal.X,
        Hit.ImpactNormal.Y,
        Hit.ImpactNormal.Z);
}
