#pragma once

#include "CoreMinimal.h"
#include "QuadrotorMworksTypes.generated.h"

USTRUCT(BlueprintType)
struct FQuadrotorMworksFrame
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS")
    FString SceneId;

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
    TArray<FVector> LocalPlanPointsMeters;

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
    bool bIsValid = false;
};
