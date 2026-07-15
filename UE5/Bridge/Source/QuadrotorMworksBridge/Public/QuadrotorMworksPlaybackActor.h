#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProceduralMeshComponent.h"
#include "QuadrotorMworksPlaybackActor.generated.h"

class UQuadrotorMworksPlaybackComponent;
class UQuadrotorRotorAudioComponent;
class UQuadrotorMworksUdpReceiverComponent;
class UMaterialInterface;
class UProceduralMeshComponent;
class USceneComponent;
class USplineComponent;
class UStaticMeshComponent;
class AQuadrotorMworksMapActor;

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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    USceneComponent* AcceptedPropellerRoot = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    TArray<USceneComponent*> AcceptedPropellerPivots;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    TArray<UStaticMeshComponent*> AcceptedPropellerMeshes;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    USplineComponent* LocalPlanSpline = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    USplineComponent* TrajectoryTrailSpline = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UProceduralMeshComponent* LocalPlanLineMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UProceduralMeshComponent* TrajectoryTrailLineMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UStaticMeshComponent* ReferenceMarker = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UStaticMeshComponent* RadarDirectionMarker = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UProceduralMeshComponent* RadarNearSectorMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UProceduralMeshComponent* RadarFarSectorMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UProceduralMeshComponent* LocalKnownMapMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    UProceduralMeshComponent* LidarPointMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UQuadrotorMworksUdpReceiverComponent* Receiver = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UQuadrotorMworksPlaybackComponent* Playback = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Audio")
    UQuadrotorRotorAudioComponent* RotorAudio = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    UMaterialInterface* BaseMaterial = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor ReferenceColor = FLinearColor(1.0f, 0.88f, 0.1f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor RadarColor = FLinearColor(0.0f, 0.75f, 1.0f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor RadarFarColor = FLinearColor(0.72f, 0.84f, 0.88f, 0.55f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor LocalKnownFreeColor = FLinearColor(0.10f, 0.80f, 0.32f, 0.45f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor LocalKnownOccupiedColor = FLinearColor(1.0f, 0.15f, 0.08f, 0.82f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor LidarPointColor = FLinearColor(0.0f, 0.95f, 1.0f, 0.95f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor LocalPlanColor = FLinearColor(0.0f, 1.0f, 0.1f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor TrajectoryTrailColor = FLinearColor(1.0f, 0.05f, 0.02f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    bool bUseDaeDerivedVehicleVisual = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FString SunrayDaeDerivedStaticMeshPath = TEXT("/Game/Sunray150/sunray150_with_mid360_textured_body.sunray150_with_mid360_textured_body");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FString SunrayDaeDerivedSourceAssetPath = TEXT("../../UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured_body.fbx");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FVector SunrayDaeDerivedVisualScale = FVector(1.0f, 1.0f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FRotator SunrayDaeDerivedVisualRotation = FRotator(0.0f, 90.0f, 0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FVector SunrayDaeDerivedVisualLocation = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    bool bLogSunrayVisualDiagnostics = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray|Propeller")
    bool bAnimateAcceptedPropellers = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray|Propeller", meta = (ClampMin = "1.0"))
    float PropellerRawCommandScale = 1000.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray|Propeller", meta = (ClampMin = "0.0"))
    float PropellerIdleVisualDegreesPerSecond = 720.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray|Propeller", meta = (ClampMin = "0.0"))
    float PropellerMaxVisualDegreesPerSecond = 2160.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Review")
    bool bLogFirstAppliedFrameDiagnostics = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bUpdateVisualHelpers = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowReferenceMarker = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowRadarSectorMesh = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowLocalKnownMapMesh = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowLidarPointMesh = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowLocalPlan = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowTrajectoryTrail = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "1"))
    int32 MaxSplinePoints = 2400;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "0.0"))
    float LocalPlanLineThicknessPixels = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "0.0"))
    float TrajectoryTrailLineThicknessPixels = 1.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    float TrajectoryLineHeightOffsetCentimeters = 6.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "3"))
    int32 RadarSectorSegments = 32;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    float RadarSectorHeightOffsetCentimeters = 5.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    float LocalKnownMapHeightOffsetCentimeters = 8.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "2.0"))
    float LocalKnownMapCellSizeCentimeters = 38.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    float LidarPointHeightOffsetCentimeters = 18.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "2.0"))
    float LidarPointSizeCentimeters = 24.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Map")
    AQuadrotorMworksMapActor* MapActor = nullptr;

    UFUNCTION(BlueprintCallable, Category = "MWORKS")
    void ApplyDefaultMaterials();

protected:
    virtual void BeginPlay() override;
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void Tick(float DeltaSeconds) override;

private:
    bool LoadSunrayDaeDerivedVisualAsset();
    bool LoadAcceptedPropellerAssets();
    void ApplyMaterialColor(UMeshComponent* Component, const FLinearColor& Color, int32 MaterialIndex = 0) const;
    void ApplySunrayDaeDerivedVisualLayout() const;
    void LogVisualComponentDiagnostics(const TCHAR* Label, const UMeshComponent* Component) const;
    void LogFirstAppliedFrameDiagnosticsIfNeeded();
    void UpdateVisualHelpers() const;
    void UpdateAcceptedPropellers(float DeltaSeconds);
    void UpdateMapSelection() const;
    void UpdateSplineFromPoints(USplineComponent* Spline, const TArray<FVector>& Points) const;
    void UpdateLineStripMesh(UProceduralMeshComponent* Mesh, const TArray<FVector>& Points, const FLinearColor& Color, float WidthCentimeters) const;
    void DrawDebugLineStrip(const TArray<FVector>& Points, const FLinearColor& Color, float ThicknessPixels) const;
    void UpdateRadarSectorMesh() const;
    void UpdateLocalKnownMapMesh() const;
    void UpdateLidarPointMesh() const;
    void AppendCellQuad(
        TArray<FVector>& Vertices,
        TArray<int32>& Triangles,
        TArray<FVector>& Normals,
        TArray<FVector2D>& UVs,
        TArray<FLinearColor>& VertexColors,
        TArray<FProcMeshTangent>& Tangents,
        const FVector& Center,
        const FLinearColor& Color,
        float SizeCentimeters,
        float HeightOffsetCentimeters) const;
    void BuildSectorMesh(UProceduralMeshComponent* Mesh, float InnerRadiusCm, float OuterRadiusCm, const FLinearColor& Color) const;
    mutable bool bLoggedFirstAppliedFrameDiagnostics = false;
    TArray<float> AcceptedPropellerAnglesDegrees;
    double ApplyRateWindowStartSeconds = 0.0;
    int32 AppliedTicksInWindow = 0;
    int32 UniqueFramesAppliedInWindow = 0;
    int32 LastAppliedSequence = TNumericLimits<int32>::Min();
};
