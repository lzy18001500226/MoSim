#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProceduralMeshComponent.h"
#include "QuadrotorMworksPlaybackActor.generated.h"

class UQuadrotorMworksPlaybackComponent;
class UQuadrotorMworksUdpReceiverComponent;
class UMaterialInterface;
class UProceduralMeshComponent;
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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh1 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh2 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh3 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS")
    UStaticMeshComponent* PropellerMesh4 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    UProceduralMeshComponent* SunrayBodyMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    UProceduralMeshComponent* SunrayPropellerMesh1 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    UProceduralMeshComponent* SunrayPropellerMesh2 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    UProceduralMeshComponent* SunrayPropellerMesh3 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    UProceduralMeshComponent* SunrayPropellerMesh4 = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Sunray")
    UStaticMeshComponent* SunrayMid360DomeMesh = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    USplineComponent* LocalPlanSpline = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS|Visualization")
    USplineComponent* TrajectoryTrailSpline = nullptr;

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

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    UMaterialInterface* BaseMaterial = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor BodyColor = FLinearColor(0.015f, 0.016f, 0.018f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor PropellerColor = FLinearColor(0.78f, 0.80f, 0.78f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor SunrayDuctGuardColor = FLinearColor(0.52f, 0.53f, 0.51f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor SunrayMid360BaseColor = FLinearColor(0.60f, 0.60f, 0.58f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor SunrayMid360ProtectArcColor = FLinearColor(0.13f, 0.13f, 0.13f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Material")
    FLinearColor SunrayMid360DomeColor = FLinearColor(0.02f, 0.42f, 0.72f, 1.0f);

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

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FString SunrayBodyStlPath = TEXT("../../References/MWORKS/QuadrotorModel/Resources/Visualization/sunray150_mid360_body.stl");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    FString SunrayPropellerStlPath = TEXT("../../References/MWORKS/QuadrotorModel/Resources/Visualization/sunray150_mid360_propeller.stl");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    float SunrayVisualScale = 3.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    float SunrayPropellerVisualScale = 0.125f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    int32 SunrayMaxBodyTriangles = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    bool bAllowPrimitiveUavFallback = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    bool bLogSunrayVisualDiagnostics = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Sunray")
    bool bUseSunrayDaeMaterialPalette = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Review")
    bool bLogFirstAppliedFrameDiagnostics = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bUpdateVisualHelpers = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowRadarSectorMesh = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowLocalKnownMapMesh = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization")
    bool bShowLidarPointMesh = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS|Visualization", meta = (ClampMin = "1"))
    int32 MaxSplinePoints = 600;

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
    bool LoadSunrayVisualMeshes();
    bool LoadStlIntoMesh(
        UProceduralMeshComponent* Mesh,
        const FString& RelativePath,
        float Scale,
        int32 MaxTriangles,
        const FLinearColor& Color,
        bool bUseReferencePalette) const;
    void ApplyMaterialColor(UMeshComponent* Component, const FLinearColor& Color, int32 MaterialIndex = 0) const;
    void SetPrimitiveUavFallbackVisible(bool bVisible) const;
    void ApplyPropellerVisuals() const;
    void ApplySunrayReferenceVisualLayout() const;
    void ApplySunrayDomeVisualLayout() const;
    void LogVisualComponentDiagnostics(const TCHAR* Label, const UMeshComponent* Component) const;
    void LogFirstAppliedFrameDiagnosticsIfNeeded();
    void UpdateVisualHelpers() const;
    void UpdateMapSelection() const;
    void UpdateSplineFromPoints(USplineComponent* Spline, const TArray<FVector>& Points) const;
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
};
