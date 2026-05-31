#pragma once

#include "CoreMinimal.h"
#include "QuadrotorMworksTypes.generated.h"

USTRUCT(BlueprintType)
struct FQuadrotorMworksMission
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector StartMeters = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector GoalMeters = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector CurrentGoalMeters = FVector::ZeroVector;
};

USTRUCT(BlueprintType)
struct FQuadrotorMworksLocalKnownMapCell
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FIntVector Offset = FIntVector::ZeroValue;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString State;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString Source;
};

USTRUCT(BlueprintType)
struct FQuadrotorMworksLocalKnownMap
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString Schema;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector OriginMeters = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double GridMeters = 0.6;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double RadiusMeters = 6.0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    TArray<FQuadrotorMworksLocalKnownMapCell> Cells;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bRenderOnly = true;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bEvidenceBacked = false;
};

USTRUCT(BlueprintType)
struct FQuadrotorMworksLidarPoints
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString Schema;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString CoordinateFrame = TEXT("ue_world_m_z_up");

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    TArray<FVector> PointsMeters;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString Source;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bRenderOnly = true;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bEvidenceBacked = false;
};

USTRUCT(BlueprintType)
struct FQuadrotorMworksStatus
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString ControllerMode;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString PlannerState;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString SafetyState;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString EvidenceLevel;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString Notes;
};

USTRUCT(BlueprintType)
struct FQuadrotorMworksOverlays
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString SceneLabel;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString MapLabel;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    TArray<FString> QualityFlags;
};

USTRUCT(BlueprintType)
struct FQuadrotorMworksFrame
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString SceneId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString MapId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString CoordinatePolicy = TEXT("mworks_world_m_z_up");

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    int32 Sequence = 0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double TimeSeconds = 0.0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector PositionMeters = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector RotationRadians = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FVector ReferencePositionMeters = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FQuadrotorMworksMission Mission;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FQuadrotorMworksLocalKnownMap LocalKnownMap;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FQuadrotorMworksLidarPoints LidarPoints;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    TArray<FVector> LocalPlanPointsMeters;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString LocalPlanSource;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bLocalPlanRenderOnly = true;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bLocalPlanEvidenceBacked = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bLocalPlanValid = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    TArray<double> MotorCommand;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double RadarNearRadiusMeters = 6.0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double RadarFarRadiusMeters = 9.0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double RadarFovDegrees = 120.0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    double RadarYawRadians = 0.0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FQuadrotorMworksStatus Status;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FQuadrotorMworksOverlays Overlays;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    bool bIsValid = false;
};
