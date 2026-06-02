#include "QuadrotorMworksPlaybackActor.h"

#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/MeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "HAL/PlatformFileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "ProceduralMeshComponent.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackComponent.h"
#include "QuadrotorMworksUdpReceiverComponent.h"
#include "UObject/ConstructorHelpers.h"

AQuadrotorMworksPlaybackActor::AQuadrotorMworksPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(SceneRoot);

    BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
    BodyMesh->SetupAttachment(SceneRoot);

    PropellerMesh1 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller1"));
    PropellerMesh2 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller2"));
    PropellerMesh3 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller3"));
    PropellerMesh4 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller4"));
    PropellerMesh1->SetupAttachment(SceneRoot);
    PropellerMesh2->SetupAttachment(SceneRoot);
    PropellerMesh3->SetupAttachment(SceneRoot);
    PropellerMesh4->SetupAttachment(SceneRoot);

    SunrayBodyMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("SunrayBodyMesh"));
    SunrayPropellerMesh1 = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("SunrayPropeller1"));
    SunrayPropellerMesh2 = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("SunrayPropeller2"));
    SunrayPropellerMesh3 = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("SunrayPropeller3"));
    SunrayPropellerMesh4 = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("SunrayPropeller4"));
    SunrayMid360DomeMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SunrayMid360DomeMesh"));
    SunrayBodyMesh->SetupAttachment(SceneRoot);
    SunrayPropellerMesh1->SetupAttachment(SceneRoot);
    SunrayPropellerMesh2->SetupAttachment(SceneRoot);
    SunrayPropellerMesh3->SetupAttachment(SceneRoot);
    SunrayPropellerMesh4->SetupAttachment(SceneRoot);
    SunrayMid360DomeMesh->SetupAttachment(SceneRoot);
    SunrayBodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SunrayPropellerMesh1->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SunrayPropellerMesh2->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SunrayPropellerMesh3->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SunrayPropellerMesh4->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SunrayMid360DomeMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    LocalPlanSpline = CreateDefaultSubobject<USplineComponent>(TEXT("LocalPlanSpline"));
    TrajectoryTrailSpline = CreateDefaultSubobject<USplineComponent>(TEXT("TrajectoryTrailSpline"));
    LocalPlanSpline->SetupAttachment(SceneRoot);
    TrajectoryTrailSpline->SetupAttachment(SceneRoot);
    LocalPlanSpline->SetRelativeTransform(FTransform::Identity);
    TrajectoryTrailSpline->SetRelativeTransform(FTransform::Identity);
    LocalPlanSpline->SetUsingAbsoluteLocation(true);
    LocalPlanSpline->SetUsingAbsoluteRotation(true);
    LocalPlanSpline->SetUsingAbsoluteScale(true);
    TrajectoryTrailSpline->SetUsingAbsoluteLocation(true);
    TrajectoryTrailSpline->SetUsingAbsoluteRotation(true);
    TrajectoryTrailSpline->SetUsingAbsoluteScale(true);
    LocalPlanSpline->SetDrawDebug(true);
    TrajectoryTrailSpline->SetDrawDebug(true);

    ReferenceMarker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ReferenceMarker"));
    RadarDirectionMarker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RadarDirectionMarker"));
    RadarNearSectorMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("RadarNearSectorMesh"));
    RadarFarSectorMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("RadarFarSectorMesh"));
    LocalKnownMapMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("LocalKnownMapMesh"));
    LidarPointMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("LidarPointMesh"));
    ReferenceMarker->SetupAttachment(SceneRoot);
    RadarDirectionMarker->SetupAttachment(SceneRoot);
    RadarNearSectorMesh->SetupAttachment(SceneRoot);
    RadarFarSectorMesh->SetupAttachment(SceneRoot);
    LocalKnownMapMesh->SetupAttachment(SceneRoot);
    LidarPointMesh->SetupAttachment(SceneRoot);
    ReferenceMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarDirectionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarNearSectorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarFarSectorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LocalKnownMapMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LidarPointMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReferenceMarker->SetUsingAbsoluteLocation(true);
    ReferenceMarker->SetUsingAbsoluteRotation(true);
    ReferenceMarker->SetUsingAbsoluteScale(true);
    RadarDirectionMarker->SetUsingAbsoluteLocation(true);
    RadarDirectionMarker->SetUsingAbsoluteRotation(true);
    RadarDirectionMarker->SetUsingAbsoluteScale(true);
    RadarNearSectorMesh->SetUsingAbsoluteLocation(true);
    RadarNearSectorMesh->SetUsingAbsoluteRotation(true);
    RadarNearSectorMesh->SetUsingAbsoluteScale(true);
    RadarFarSectorMesh->SetUsingAbsoluteLocation(true);
    RadarFarSectorMesh->SetUsingAbsoluteRotation(true);
    RadarFarSectorMesh->SetUsingAbsoluteScale(true);
    LocalKnownMapMesh->SetUsingAbsoluteLocation(true);
    LocalKnownMapMesh->SetUsingAbsoluteRotation(true);
    LocalKnownMapMesh->SetUsingAbsoluteScale(true);
    LidarPointMesh->SetUsingAbsoluteLocation(true);
    LidarPointMesh->SetUsingAbsoluteRotation(true);
    LidarPointMesh->SetUsingAbsoluteScale(true);

    PropellerMesh1->SetRelativeLocation(FVector(32.0, 32.0, 0.0));
    PropellerMesh2->SetRelativeLocation(FVector(32.0, -32.0, 0.0));
    PropellerMesh3->SetRelativeLocation(FVector(-32.0, -32.0, 0.0));
    PropellerMesh4->SetRelativeLocation(FVector(-32.0, 32.0, 0.0));
    ApplySunrayReferenceVisualLayout();

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial"));
    if (CubeMesh.Succeeded())
    {
        BodyMesh->SetStaticMesh(CubeMesh.Object);
        BodyMesh->SetRelativeScale3D(FVector(0.75f, 0.42f, 0.12f));
        RadarDirectionMarker->SetStaticMesh(CubeMesh.Object);
        RadarDirectionMarker->SetRelativeScale3D(FVector(1.0f, 0.035f, 0.025f));
    }
    if (CylinderMesh.Succeeded())
    {
        UStaticMeshComponent* Props[4] = {PropellerMesh1, PropellerMesh2, PropellerMesh3, PropellerMesh4};
        for (UStaticMeshComponent* Prop : Props)
        {
            Prop->SetStaticMesh(CylinderMesh.Object);
            Prop->SetRelativeScale3D(FVector(0.24f, 0.24f, 0.015f));
        }
        ReferenceMarker->SetStaticMesh(CylinderMesh.Object);
        ReferenceMarker->SetRelativeScale3D(FVector(0.14f, 0.14f, 0.14f));
    }
    if (SunrayMid360DomeMesh && SphereMesh.Succeeded())
    {
        SunrayMid360DomeMesh->SetStaticMesh(SphereMesh.Object);
    }
    ReferenceMarker->SetVisibility(false);
    ReferenceMarker->SetHiddenInGame(true);
    RadarDirectionMarker->SetVisibility(false);
    RadarDirectionMarker->SetHiddenInGame(true);
    RadarNearSectorMesh->SetVisibility(false);
    RadarNearSectorMesh->SetHiddenInGame(true);
    RadarFarSectorMesh->SetVisibility(false);
    RadarFarSectorMesh->SetHiddenInGame(true);
    LocalKnownMapMesh->SetVisibility(false);
    LocalKnownMapMesh->SetHiddenInGame(true);
    LidarPointMesh->SetVisibility(false);
    LidarPointMesh->SetHiddenInGame(true);
    if (BasicMaterial.Succeeded())
    {
        BaseMaterial = BasicMaterial.Object;
    }
    ApplyDefaultMaterials();
    SetPrimitiveUavFallbackVisible(bAllowPrimitiveUavFallback);
    ApplySunrayDomeVisualLayout();

    Receiver = CreateDefaultSubobject<UQuadrotorMworksUdpReceiverComponent>(TEXT("MworksUdpReceiver"));
    Playback = CreateDefaultSubobject<UQuadrotorMworksPlaybackComponent>(TEXT("MworksPlayback"));
}

void AQuadrotorMworksPlaybackActor::BeginPlay()
{
    Super::BeginPlay();

    const bool bSunrayLoaded = LoadSunrayVisualMeshes();
    SetPrimitiveUavFallbackVisible(!bSunrayLoaded && bAllowPrimitiveUavFallback);
}

void AQuadrotorMworksPlaybackActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ApplyDefaultMaterials();
    ApplySunrayReferenceVisualLayout();
}

void AQuadrotorMworksPlaybackActor::ApplyDefaultMaterials()
{
    ApplyMaterialColor(BodyMesh, BodyColor);
    ApplyMaterialColor(PropellerMesh1, PropellerColor);
    ApplyMaterialColor(PropellerMesh2, PropellerColor);
    ApplyMaterialColor(PropellerMesh3, PropellerColor);
    ApplyMaterialColor(PropellerMesh4, PropellerColor);
    ApplyMaterialColor(SunrayBodyMesh, BodyColor);
    ApplyMaterialColor(SunrayBodyMesh, SunrayDuctGuardColor, 1);
    ApplyMaterialColor(SunrayBodyMesh, SunrayMid360BaseColor, 2);
    ApplyMaterialColor(SunrayBodyMesh, SunrayMid360DomeColor, 3);
    ApplyMaterialColor(SunrayBodyMesh, SunrayMid360ProtectArcColor, 4);
    ApplyMaterialColor(SunrayPropellerMesh1, PropellerColor);
    ApplyMaterialColor(SunrayPropellerMesh2, PropellerColor);
    ApplyMaterialColor(SunrayPropellerMesh3, PropellerColor);
    ApplyMaterialColor(SunrayPropellerMesh4, PropellerColor);
    ApplyMaterialColor(SunrayMid360DomeMesh, SunrayMid360DomeColor);
    ApplyMaterialColor(ReferenceMarker, ReferenceColor);
    ApplyMaterialColor(RadarDirectionMarker, RadarColor);
    ApplyMaterialColor(RadarNearSectorMesh, RadarColor);
    ApplyMaterialColor(RadarFarSectorMesh, RadarFarColor);
    ApplyMaterialColor(LocalKnownMapMesh, LocalKnownFreeColor);
    ApplyMaterialColor(LocalKnownMapMesh, LocalKnownOccupiedColor, 1);
    ApplyMaterialColor(LidarPointMesh, LidarPointColor);
}

namespace
{
constexpr float MworksSunrayVisualYawOffsetDegrees = -90.0f;

bool ReadUInt32LE(const TArray<uint8>& Bytes, int32 Offset, uint32& Value)
{
    if (Offset < 0 || Offset + 4 > Bytes.Num())
    {
        return false;
    }
    Value = static_cast<uint32>(Bytes[Offset])
        | (static_cast<uint32>(Bytes[Offset + 1]) << 8)
        | (static_cast<uint32>(Bytes[Offset + 2]) << 16)
        | (static_cast<uint32>(Bytes[Offset + 3]) << 24);
    return true;
}

bool ReadFloatLE(const TArray<uint8>& Bytes, int32 Offset, float& Value)
{
    uint32 Raw = 0;
    if (!ReadUInt32LE(Bytes, Offset, Raw))
    {
        return false;
    }
    FMemory::Memcpy(&Value, &Raw, sizeof(float));
    return true;
}

FString ResolveProjectRelativePath(const FString& RelativePath)
{
    if (FPaths::IsRelative(RelativePath))
    {
        return FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), RelativePath);
    }
    return FPaths::ConvertRelativePathToFull(RelativePath);
}

void AppendTriangle(
    TArray<FVector>& Vertices,
    TArray<int32>& Triangles,
    TArray<FVector>& Normals,
    TArray<FVector2D>& UVs,
    TArray<FLinearColor>& VertexColors,
    TArray<FProcMeshTangent>& Tangents,
    const FVector& A,
    const FVector& B,
    const FVector& C,
    const FVector& Normal,
    const FLinearColor& Color)
{
    const int32 Base = Vertices.Num();
    Vertices.Append({A, B, C});
    Triangles.Append({Base, Base + 1, Base + 2});
    const FVector N = Normal.IsNearlyZero() ? FVector::UpVector : Normal.GetSafeNormal();
    Normals.Append({N, N, N});
    UVs.Append({FVector2D(0.0f, 0.0f), FVector2D(1.0f, 0.0f), FVector2D(0.0f, 1.0f)});
    VertexColors.Append({Color, Color, Color});
    Tangents.Append({
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
    });
}

FString VectorToDiagnosticString(const FVector& Value)
{
    return FString::Printf(TEXT("(%.3f, %.3f, %.3f)"), Value.X, Value.Y, Value.Z);
}

void ExpandBounds(FVector& MinBounds, FVector& MaxBounds, const FVector& Point)
{
    MinBounds.X = FMath::Min(MinBounds.X, Point.X);
    MinBounds.Y = FMath::Min(MinBounds.Y, Point.Y);
    MinBounds.Z = FMath::Min(MinBounds.Z, Point.Z);
    MaxBounds.X = FMath::Max(MaxBounds.X, Point.X);
    MaxBounds.Y = FMath::Max(MaxBounds.Y, Point.Y);
    MaxBounds.Z = FMath::Max(MaxBounds.Z, Point.Z);
}

enum class ESunrayPaletteSection : int32
{
    CarbonFrame = 0,
    DuctGuard = 1,
    Mid360Base = 2,
    Mid360Dome = 3,
    Mid360ProtectArc = 4,
};

ESunrayPaletteSection ClassifySunrayBodyTriangle(const FVector& A, const FVector& B, const FVector& C)
{
    const FVector Center = (A + B + C) / 3.0f;
    const float RadialXY = FVector2D(Center.X, Center.Y).Size();

    if (Center.Z > 6.0f && Center.Z < 10.0f && Center.X > -5.4f && Center.X < 5.4f && Center.Y > -1.6f && Center.Y < 9.8f)
    {
        if (FMath::Abs(Center.X) < 1.55f && Center.Y > 2.55f && Center.Y < 5.55f && Center.Z > 8.35f)
        {
            return ESunrayPaletteSection::Mid360Dome;
        }
        return ESunrayPaletteSection::Mid360ProtectArc;
    }
    if (Center.Z > 0.8f && Center.Z <= 6.2f && Center.X > -3.8f && Center.X < 3.8f && Center.Y > 1.2f && Center.Y < 9.8f)
    {
        return ESunrayPaletteSection::Mid360Base;
    }
    if (RadialXY > 7.5f && Center.Z < -1.0f)
    {
        return ESunrayPaletteSection::DuctGuard;
    }
    return ESunrayPaletteSection::CarbonFrame;
}
}

void AQuadrotorMworksPlaybackActor::ApplyMaterialColor(UMeshComponent* Component, const FLinearColor& Color, int32 MaterialIndex) const
{
    if (!Component || !BaseMaterial)
    {
        return;
    }
    UMaterialInstanceDynamic* DynamicMaterial = Component->CreateDynamicMaterialInstance(MaterialIndex, BaseMaterial);
    if (DynamicMaterial)
    {
        DynamicMaterial->SetVectorParameterValue(TEXT("Color"), Color);
        DynamicMaterial->SetVectorParameterValue(TEXT("BaseColor"), Color);
        Component->SetMaterial(MaterialIndex, DynamicMaterial);
    }
}

bool AQuadrotorMworksPlaybackActor::LoadStlIntoMesh(
    UProceduralMeshComponent* Mesh,
    const FString& RelativePath,
    float Scale,
    int32 MaxTriangles,
    const FLinearColor& Color,
    bool bUseReferencePalette) const
{
    if (!Mesh)
    {
        return false;
    }

    const FString FullPath = ResolveProjectRelativePath(RelativePath);
    TArray<uint8> Bytes;
    if (!FFileHelper::LoadFileToArray(Bytes, *FullPath) || Bytes.Num() < 84)
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim Sunray STL load failed: %s"), *FullPath);
        Mesh->ClearAllMeshSections();
        return false;
    }

    struct FMeshSectionBuild
    {
        TArray<FVector> Vertices;
        TArray<int32> Triangles;
        TArray<FVector> Normals;
        TArray<FVector2D> UVs;
        TArray<FLinearColor> VertexColors;
        TArray<FProcMeshTangent> Tangents;
    };
    constexpr int32 SunraySectionCount = 5;
    FMeshSectionBuild Sections[SunraySectionCount];
    auto ColorForSection = [this, &Color](int32 SectionIndex)
    {
        if (!bUseSunrayDaeMaterialPalette)
        {
            return Color;
        }
        switch (static_cast<ESunrayPaletteSection>(SectionIndex))
        {
        case ESunrayPaletteSection::DuctGuard:
            return SunrayDuctGuardColor;
        case ESunrayPaletteSection::Mid360Base:
            return SunrayMid360BaseColor;
        case ESunrayPaletteSection::Mid360Dome:
            return SunrayMid360DomeColor;
        case ESunrayPaletteSection::Mid360ProtectArc:
            return SunrayMid360ProtectArcColor;
        case ESunrayPaletteSection::CarbonFrame:
        default:
            return BodyColor;
        }
    };
    auto AppendColoredTriangle = [&](const FVector& A, const FVector& B, const FVector& C, const FVector& Normal)
    {
        const int32 SectionIndex = bUseReferencePalette
            ? static_cast<int32>(ClassifySunrayBodyTriangle(A, B, C))
            : 0;
        AppendTriangle(
            Sections[SectionIndex].Vertices,
            Sections[SectionIndex].Triangles,
            Sections[SectionIndex].Normals,
            Sections[SectionIndex].UVs,
            Sections[SectionIndex].VertexColors,
            Sections[SectionIndex].Tangents,
            A,
            B,
            C,
            Normal,
            ColorForSection(SectionIndex));
    };

    const int32 TriangleLimit = MaxTriangles > 0 ? MaxTriangles : TNumericLimits<int32>::Max();
    bool bLoaded = false;
    bool bBinaryStl = false;
    int32 SourceTriangleCount = 0;
    int32 LoadedTriangleCount = 0;
    FVector RawMinBounds(TNumericLimits<float>::Max(), TNumericLimits<float>::Max(), TNumericLimits<float>::Max());
    FVector RawMaxBounds(TNumericLimits<float>::Lowest(), TNumericLimits<float>::Lowest(), TNumericLimits<float>::Lowest());
    FVector ScaledMinBounds(TNumericLimits<float>::Max(), TNumericLimits<float>::Max(), TNumericLimits<float>::Max());
    FVector ScaledMaxBounds(TNumericLimits<float>::Lowest(), TNumericLimits<float>::Lowest(), TNumericLimits<float>::Lowest());
    uint32 BinaryTriangleCount = 0;
    if (ReadUInt32LE(Bytes, 80, BinaryTriangleCount)
        && Bytes.Num() == 84 + static_cast<int64>(BinaryTriangleCount) * 50)
    {
        bBinaryStl = true;
        SourceTriangleCount = BinaryTriangleCount > static_cast<uint32>(TNumericLimits<int32>::Max())
            ? TNumericLimits<int32>::Max()
            : static_cast<int32>(BinaryTriangleCount);
        if (MaxTriangles > 0 && BinaryTriangleCount > static_cast<uint32>(TriangleLimit))
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("MoSim Sunray STL triangle limit would destructively downsample mesh; refusing load path=%s source_triangles=%u limit=%d"),
                *FullPath,
                BinaryTriangleCount,
                TriangleLimit);
            Mesh->ClearAllMeshSections();
            return false;
        }
        const int32 ReserveCount = SourceTriangleCount;
        Sections[0].Vertices.Reserve(ReserveCount * 3);
        Sections[0].Triangles.Reserve(ReserveCount * 3);
        for (uint32 TriangleIndex = 0; TriangleIndex < BinaryTriangleCount; ++TriangleIndex)
        {
            const int32 Offset = 84 + static_cast<int32>(TriangleIndex) * 50;
            float Values[12] = {};
            bool bOk = true;
            for (int32 Index = 0; Index < 12; ++Index)
            {
                bOk &= ReadFloatLE(Bytes, Offset + Index * 4, Values[Index]);
            }
            if (!bOk)
            {
                continue;
            }
            const FVector RawA(Values[3], Values[4], Values[5]);
            const FVector RawB(Values[6], Values[7], Values[8]);
            const FVector RawC(Values[9], Values[10], Values[11]);
            const FVector ScaledA = RawA * Scale;
            const FVector ScaledB = RawB * Scale;
            const FVector ScaledC = RawC * Scale;
            ExpandBounds(RawMinBounds, RawMaxBounds, RawA);
            ExpandBounds(RawMinBounds, RawMaxBounds, RawB);
            ExpandBounds(RawMinBounds, RawMaxBounds, RawC);
            ExpandBounds(ScaledMinBounds, ScaledMaxBounds, ScaledA);
            ExpandBounds(ScaledMinBounds, ScaledMaxBounds, ScaledB);
            ExpandBounds(ScaledMinBounds, ScaledMaxBounds, ScaledC);
            AppendColoredTriangle(
                ScaledA,
                ScaledB,
                ScaledC,
                FVector(Values[0], Values[1], Values[2]));
        }
    }
    else
    {
        FString Text;
        FFileHelper::BufferToString(Text, Bytes.GetData(), Bytes.Num());
        TArray<FString> Lines;
        Text.ParseIntoArrayLines(Lines, false);
        TArray<FVector> Pending;
        Pending.Reserve(3);
        FVector CurrentNormal = FVector::UpVector;
        for (const FString& Line : Lines)
        {
            if (SourceTriangleCount >= TriangleLimit)
            {
                break;
            }
            FString Trimmed = Line;
            Trimmed.TrimStartAndEndInline();
            TArray<FString> Parts;
            Trimmed.ParseIntoArrayWS(Parts);
            if (Parts.Num() == 5 && Parts[0].Equals(TEXT("facet"), ESearchCase::IgnoreCase))
            {
                CurrentNormal = FVector(FCString::Atof(*Parts[2]), FCString::Atof(*Parts[3]), FCString::Atof(*Parts[4]));
            }
            else if (Parts.Num() == 4 && Parts[0].Equals(TEXT("vertex"), ESearchCase::IgnoreCase))
            {
                const FVector RawVertex(FCString::Atof(*Parts[1]), FCString::Atof(*Parts[2]), FCString::Atof(*Parts[3]));
                const FVector ScaledVertex = RawVertex * Scale;
                ExpandBounds(RawMinBounds, RawMaxBounds, RawVertex);
                ExpandBounds(ScaledMinBounds, ScaledMaxBounds, ScaledVertex);
                Pending.Add(ScaledVertex);
                if (Pending.Num() == 3)
                {
                    AppendColoredTriangle(
                        Pending[0],
                        Pending[1],
                        Pending[2],
                        CurrentNormal);
                    Pending.Reset();
                    ++SourceTriangleCount;
                }
            }
        }
    }

    int32 TotalLoadedVertices = 0;
    for (const FMeshSectionBuild& Section : Sections)
    {
        TotalLoadedVertices += Section.Vertices.Num();
    }
    bLoaded = TotalLoadedVertices > 0;

    if (!bLoaded)
    {
        Mesh->ClearAllMeshSections();
        return false;
    }

    Mesh->ClearAllMeshSections();
    for (int32 SectionIndex = 0; SectionIndex < SunraySectionCount; ++SectionIndex)
    {
        FMeshSectionBuild& Section = Sections[SectionIndex];
        if (Section.Vertices.Num() == 0)
        {
            continue;
        }
        Mesh->CreateMeshSection_LinearColor(
            SectionIndex,
            Section.Vertices,
            Section.Triangles,
            Section.Normals,
            Section.UVs,
            Section.VertexColors,
            Section.Tangents,
            false);
    }
    Mesh->SetVisibility(true);
    LoadedTriangleCount = TotalLoadedVertices / 3;
    const int64 FileSizeBytes = FPlatformFileManager::Get().GetPlatformFile().FileSize(*FullPath);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray STL loaded: path=%s file_size=%lld kind=%s source_triangles=%d loaded_triangles=%d scale=%.4f dae_material_palette=%s section_triangles=[carbon=%d,guard=%d,mid360_base=%d,mid360_dome=%d,mid360_protect_arc=%d] raw_min=%s raw_max=%s raw_extent=%s scaled_min=%s scaled_max=%s scaled_extent=%s"),
        *FullPath,
        FileSizeBytes,
        bBinaryStl ? TEXT("binary") : TEXT("ascii"),
        SourceTriangleCount,
        LoadedTriangleCount,
        Scale,
        bUseReferencePalette ? TEXT("true") : TEXT("false"),
        Sections[0].Vertices.Num() / 3,
        Sections[1].Vertices.Num() / 3,
        Sections[2].Vertices.Num() / 3,
        Sections[3].Vertices.Num() / 3,
        Sections[4].Vertices.Num() / 3,
        *VectorToDiagnosticString(RawMinBounds),
        *VectorToDiagnosticString(RawMaxBounds),
        *VectorToDiagnosticString(RawMaxBounds - RawMinBounds),
        *VectorToDiagnosticString(ScaledMinBounds),
        *VectorToDiagnosticString(ScaledMaxBounds),
        *VectorToDiagnosticString(ScaledMaxBounds - ScaledMinBounds));
    return true;
}

bool AQuadrotorMworksPlaybackActor::LoadSunrayVisualMeshes()
{
    ApplySunrayReferenceVisualLayout();
    const bool bBodyLoaded = LoadStlIntoMesh(
        SunrayBodyMesh,
        SunrayBodyStlPath,
        SunrayVisualScale,
        SunrayMaxBodyTriangles,
        BodyColor,
        bUseSunrayDaeMaterialPalette);

    UProceduralMeshComponent* Props[4] = {
        SunrayPropellerMesh1,
        SunrayPropellerMesh2,
        SunrayPropellerMesh3,
        SunrayPropellerMesh4,
    };
    bool bPropsLoaded = true;
    for (UProceduralMeshComponent* Prop : Props)
    {
        bPropsLoaded &= LoadStlIntoMesh(Prop, SunrayPropellerStlPath, SunrayPropellerVisualScale, 0, PropellerColor, false);
    }
    if (bLogSunrayVisualDiagnostics)
    {
        LogVisualComponentDiagnostics(TEXT("SunrayBodyMesh"), SunrayBodyMesh);
        LogVisualComponentDiagnostics(TEXT("SunrayPropeller1"), SunrayPropellerMesh1);
        LogVisualComponentDiagnostics(TEXT("SunrayPropeller2"), SunrayPropellerMesh2);
        LogVisualComponentDiagnostics(TEXT("SunrayPropeller3"), SunrayPropellerMesh3);
        LogVisualComponentDiagnostics(TEXT("SunrayPropeller4"), SunrayPropellerMesh4);
        LogVisualComponentDiagnostics(TEXT("PrimitiveBodyMesh"), BodyMesh);
        LogVisualComponentDiagnostics(TEXT("PrimitivePropeller1"), PropellerMesh1);
    }
    return bBodyLoaded && bPropsLoaded;
}

void AQuadrotorMworksPlaybackActor::ApplySunrayReferenceVisualLayout() const
{
    if (SunrayBodyMesh)
    {
        SunrayBodyMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 5.25f));
        SunrayBodyMesh->SetRelativeRotation(FRotator(0.0f, MworksSunrayVisualYawOffsetDegrees, 0.0f));
    }

    UProceduralMeshComponent* SunrayProps[4] = {
        SunrayPropellerMesh1,
        SunrayPropellerMesh2,
        SunrayPropellerMesh3,
        SunrayPropellerMesh4,
    };
    const FVector RotorPositionsCm[4] = {
        FVector(6.5f, -6.5f, -2.5f),
        FVector(6.5f, 6.5f, -2.5f),
        FVector(-6.5f, 6.5f, -2.5f),
        FVector(-6.5f, -6.5f, -2.5f),
    };
    const TCHAR* RotorLabels[4] = {
        TEXT("mworks_fixed1"),
        TEXT("mworks_fixed2"),
        TEXT("mworks_fixed3"),
        TEXT("mworks_fixed4"),
    };
    for (int32 Index = 0; Index < 4; ++Index)
    {
        if (SunrayProps[Index])
        {
            SunrayProps[Index]->SetRelativeLocation(RotorPositionsCm[Index]);
            SunrayProps[Index]->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));
        }
    }
    ApplySunrayDomeVisualLayout();
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray reference visual layout applied: source=MWORKSVisualFrame body_yaw_offset_deg=%.1f rotor0_label=%s rotor0_mworks=%s rotor0_ue=%s rotor1_label=%s rotor1_mworks=%s rotor1_ue=%s rotor2_label=%s rotor2_mworks=%s rotor2_ue=%s rotor3_label=%s rotor3_mworks=%s rotor3_ue=%s propeller_scale=%.4f"),
        MworksSunrayVisualYawOffsetDegrees,
        RotorLabels[0],
        *VectorToDiagnosticString(RotorPositionsCm[0]),
        *VectorToDiagnosticString(RotorPositionsCm[0]),
        RotorLabels[1],
        *VectorToDiagnosticString(RotorPositionsCm[1]),
        *VectorToDiagnosticString(RotorPositionsCm[1]),
        RotorLabels[2],
        *VectorToDiagnosticString(RotorPositionsCm[2]),
        *VectorToDiagnosticString(RotorPositionsCm[2]),
        RotorLabels[3],
        *VectorToDiagnosticString(RotorPositionsCm[3]),
        *VectorToDiagnosticString(RotorPositionsCm[3]),
        SunrayPropellerVisualScale);
}

void AQuadrotorMworksPlaybackActor::ApplySunrayDomeVisualLayout() const
{
    if (!SunrayMid360DomeMesh)
    {
        return;
    }

    // The runtime STL has no material groups. Keep the accepted blue optical cue
    // as a small separate cap so the MID-360 protective arcs stay dark.
    SunrayMid360DomeMesh->SetRelativeLocation(FVector(0.0f, 3.7f, 9.0f));
    SunrayMid360DomeMesh->SetRelativeRotation(FRotator(0.0f, MworksSunrayVisualYawOffsetDegrees, 0.0f));
    SunrayMid360DomeMesh->SetRelativeScale3D(FVector(0.036f, 0.036f, 0.018f));
    SunrayMid360DomeMesh->SetVisibility(true);
    SunrayMid360DomeMesh->SetHiddenInGame(false);
}

void AQuadrotorMworksPlaybackActor::SetPrimitiveUavFallbackVisible(bool bVisible) const
{
    UStaticMeshComponent* Components[5] = {BodyMesh, PropellerMesh1, PropellerMesh2, PropellerMesh3, PropellerMesh4};
    for (UStaticMeshComponent* Component : Components)
    {
        if (Component)
        {
            Component->SetVisibility(bVisible);
            Component->SetHiddenInGame(!bVisible);
        }
    }
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray primitive fallback visibility=%s allow_fallback=%s"),
        bVisible ? TEXT("true") : TEXT("false"),
        bAllowPrimitiveUavFallback ? TEXT("true") : TEXT("false"));
}

void AQuadrotorMworksPlaybackActor::LogVisualComponentDiagnostics(const TCHAR* Label, const UMeshComponent* Component) const
{
    if (!Component)
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim Sunray component diagnostic: %s missing"), Label);
        return;
    }

    const FBoxSphereBounds Bounds = Component->Bounds;
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray component diagnostic: %s visible=%s hidden_in_game=%s relative_location=%s relative_rotation=%s relative_scale=%s world_origin=%s box_extent=%s sphere_radius=%.3f"),
        Label,
        Component->IsVisible() ? TEXT("true") : TEXT("false"),
        Component->bHiddenInGame ? TEXT("true") : TEXT("false"),
        *VectorToDiagnosticString(Component->GetRelativeLocation()),
        *Component->GetRelativeRotation().ToString(),
        *VectorToDiagnosticString(Component->GetRelativeScale3D()),
        *VectorToDiagnosticString(Bounds.Origin),
        *VectorToDiagnosticString(Bounds.BoxExtent),
        Bounds.SphereRadius);
}

void AQuadrotorMworksPlaybackActor::LogFirstAppliedFrameDiagnosticsIfNeeded()
{
    if (!bLogFirstAppliedFrameDiagnostics || bLoggedFirstAppliedFrameDiagnostics || !Receiver || !Receiver->HasFrame() || !Playback)
    {
        return;
    }

    bLoggedFirstAppliedFrameDiagnostics = true;
    const FQuadrotorMworksFrame Frame = Receiver->GetLatestFrame();
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray first applied frame: scene=%s map=%s seq=%d mworks_position_m=%s unreal_location_cm=%s actor_location_cm=%s actor_rotation=%s coordinate_policy=%s"),
        *Frame.SceneId,
        *Frame.MapId,
        Frame.Sequence,
        *VectorToDiagnosticString(Frame.PositionMeters),
        *VectorToDiagnosticString(Playback->LatestUnrealLocation),
        *VectorToDiagnosticString(GetActorLocation()),
        *GetActorRotation().ToString(),
        *Frame.CoordinatePolicy);
    if (bLogSunrayVisualDiagnostics)
    {
        LogVisualComponentDiagnostics(TEXT("SunrayBodyMeshAfterFirstFrame"), SunrayBodyMesh);
        LogVisualComponentDiagnostics(TEXT("SunrayPropeller1AfterFirstFrame"), SunrayPropellerMesh1);
        LogVisualComponentDiagnostics(TEXT("PrimitiveBodyAfterFirstFrame"), BodyMesh);
        LogVisualComponentDiagnostics(TEXT("ReferenceMarkerAfterFirstFrame"), ReferenceMarker);
        LogVisualComponentDiagnostics(TEXT("RadarDirectionMarkerAfterFirstFrame"), RadarDirectionMarker);
    }
}

void AQuadrotorMworksPlaybackActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (Playback && Receiver && Receiver->HasFrame())
    {
        Playback->ApplyFrame(Receiver->GetLatestFrame(), DeltaSeconds);
    }
    ApplyPropellerVisuals();
    UpdateMapSelection();
    UpdateVisualHelpers();
    LogFirstAppliedFrameDiagnosticsIfNeeded();
}

void AQuadrotorMworksPlaybackActor::ApplyPropellerVisuals() const
{
    if (!Playback || Playback->PropellerAnglesDegrees.Num() < 4)
    {
        return;
    }

    UStaticMeshComponent* Props[4] = {PropellerMesh1, PropellerMesh2, PropellerMesh3, PropellerMesh4};
    for (int32 Index = 0; Index < 4; ++Index)
    {
        if (Props[Index])
        {
            Props[Index]->SetRelativeRotation(FRotator(0.0f, Playback->PropellerAnglesDegrees[Index], 0.0f));
        }
    }

    UProceduralMeshComponent* SunrayProps[4] = {
        SunrayPropellerMesh1,
        SunrayPropellerMesh2,
        SunrayPropellerMesh3,
        SunrayPropellerMesh4,
    };
    for (int32 Index = 0; Index < 4; ++Index)
    {
        if (SunrayProps[Index])
        {
            SunrayProps[Index]->SetRelativeRotation(FRotator(0.0f, Playback->PropellerAnglesDegrees[Index], 0.0f));
        }
    }
}

void AQuadrotorMworksPlaybackActor::UpdateMapSelection() const
{
    if (!MapActor || !Receiver || !Receiver->HasFrame())
    {
        return;
    }

    MapActor->ApplyFrameMapSelection(Receiver->GetLatestFrame());
}

void AQuadrotorMworksPlaybackActor::UpdateSplineFromPoints(USplineComponent* Spline, const TArray<FVector>& Points) const
{
    if (!Spline)
    {
        return;
    }

    Spline->ClearSplinePoints(false);
    const int32 Count = MaxSplinePoints > 0 ? FMath::Min(MaxSplinePoints, Points.Num()) : Points.Num();
    const int32 StartIndex = Points.Num() - Count;
    for (int32 Index = FMath::Max(0, StartIndex); Index < Points.Num(); ++Index)
    {
        Spline->AddSplinePoint(Points[Index], ESplineCoordinateSpace::World, false);
    }
    Spline->UpdateSpline();
}

void AQuadrotorMworksPlaybackActor::UpdateVisualHelpers() const
{
    if (!bUpdateVisualHelpers || !Playback)
    {
        if (ReferenceMarker)
        {
            ReferenceMarker->SetVisibility(false);
            ReferenceMarker->SetHiddenInGame(true);
        }
        if (RadarDirectionMarker)
        {
            RadarDirectionMarker->SetVisibility(false);
            RadarDirectionMarker->SetHiddenInGame(true);
        }
        if (RadarNearSectorMesh)
        {
            RadarNearSectorMesh->ClearAllMeshSections();
            RadarNearSectorMesh->SetVisibility(false);
            RadarNearSectorMesh->SetHiddenInGame(true);
        }
        if (RadarFarSectorMesh)
        {
            RadarFarSectorMesh->ClearAllMeshSections();
            RadarFarSectorMesh->SetVisibility(false);
            RadarFarSectorMesh->SetHiddenInGame(true);
        }
        if (LocalKnownMapMesh)
        {
            LocalKnownMapMesh->ClearAllMeshSections();
            LocalKnownMapMesh->SetVisibility(false);
            LocalKnownMapMesh->SetHiddenInGame(true);
        }
        if (LidarPointMesh)
        {
            LidarPointMesh->ClearAllMeshSections();
            LidarPointMesh->SetVisibility(false);
            LidarPointMesh->SetHiddenInGame(true);
        }
        return;
    }

    UpdateSplineFromPoints(LocalPlanSpline, Playback->LocalPlanPointsUnreal);
    UpdateSplineFromPoints(TrajectoryTrailSpline, Playback->TrajectoryTrailUnreal);

    if (ReferenceMarker)
    {
        ReferenceMarker->SetVisibility(true);
        ReferenceMarker->SetHiddenInGame(false);
        ReferenceMarker->SetWorldLocation(Playback->ReferenceUnrealLocation);
        ReferenceMarker->SetWorldRotation(FRotator::ZeroRotator);
    }

    if (RadarDirectionMarker)
    {
        RadarDirectionMarker->SetVisibility(true);
        RadarDirectionMarker->SetHiddenInGame(false);
        const float Length = FMath::Max(Playback->RadarNearRadiusCentimeters, 50.0f);
        const float YawRadians = FMath::DegreesToRadians(Playback->RadarYawDegrees);
        const FVector Forward(FMath::Cos(YawRadians), FMath::Sin(YawRadians), 0.0f);
        RadarDirectionMarker->SetWorldLocation(Playback->LatestUnrealLocation + Forward * (0.5f * Length));
        RadarDirectionMarker->SetWorldRotation(FRotator(0.0f, Playback->RadarYawDegrees, 0.0f));
        RadarDirectionMarker->SetWorldScale3D(FVector(Length / 100.0f, 0.035f, 0.025f));
    }

    UpdateRadarSectorMesh();
    UpdateLocalKnownMapMesh();
    UpdateLidarPointMesh();
}

void AQuadrotorMworksPlaybackActor::UpdateRadarSectorMesh() const
{
    if (!Playback)
    {
        return;
    }

    if (!bShowRadarSectorMesh)
    {
        if (RadarNearSectorMesh)
        {
            RadarNearSectorMesh->ClearAllMeshSections();
        }
        if (RadarFarSectorMesh)
        {
            RadarFarSectorMesh->ClearAllMeshSections();
        }
        return;
    }

    BuildSectorMesh(RadarNearSectorMesh, 0.0f, Playback->RadarNearRadiusCentimeters, RadarColor);
    BuildSectorMesh(
        RadarFarSectorMesh,
        Playback->RadarNearRadiusCentimeters,
        Playback->RadarFarRadiusCentimeters,
        RadarFarColor);
}

void AQuadrotorMworksPlaybackActor::UpdateLocalKnownMapMesh() const
{
    if (!LocalKnownMapMesh || !Playback)
    {
        return;
    }

    if (!bShowLocalKnownMapMesh)
    {
        LocalKnownMapMesh->ClearAllMeshSections();
        return;
    }

    auto BuildCells = [this](const TArray<FVector>& Cells, const FLinearColor& Color, int32 SectionIndex)
    {
        TArray<FVector> Vertices;
        TArray<int32> Triangles;
        TArray<FVector> Normals;
        TArray<FVector2D> UVs;
        TArray<FLinearColor> VertexColors;
        TArray<FProcMeshTangent> Tangents;

        Vertices.Reserve(Cells.Num() * 4);
        Triangles.Reserve(Cells.Num() * 6);
        Normals.Reserve(Cells.Num() * 4);
        UVs.Reserve(Cells.Num() * 4);
        VertexColors.Reserve(Cells.Num() * 4);
        Tangents.Reserve(Cells.Num() * 4);

        for (const FVector& Center : Cells)
        {
            AppendCellQuad(
                Vertices,
                Triangles,
                Normals,
                UVs,
                VertexColors,
                Tangents,
                Center,
                Color,
                LocalKnownMapCellSizeCentimeters,
                LocalKnownMapHeightOffsetCentimeters);
        }

        if (Vertices.Num() == 0)
        {
            LocalKnownMapMesh->ClearMeshSection(SectionIndex);
            return;
        }

        LocalKnownMapMesh->CreateMeshSection_LinearColor(
            SectionIndex,
            Vertices,
            Triangles,
            Normals,
            UVs,
            VertexColors,
            Tangents,
            false);
    };

    if (Playback->LocalKnownFreeCellsUnreal.Num() == 0 && Playback->LocalKnownOccupiedCellsUnreal.Num() == 0)
    {
        LocalKnownMapMesh->ClearAllMeshSections();
        return;
    }

    BuildCells(Playback->LocalKnownFreeCellsUnreal, LocalKnownFreeColor, 0);
    BuildCells(Playback->LocalKnownOccupiedCellsUnreal, LocalKnownOccupiedColor, 1);
}

void AQuadrotorMworksPlaybackActor::UpdateLidarPointMesh() const
{
    if (!LidarPointMesh || !Playback)
    {
        return;
    }

    if (!bShowLidarPointMesh)
    {
        LidarPointMesh->ClearAllMeshSections();
        return;
    }

    if (Playback->LidarPointsUnreal.Num() == 0)
    {
        LidarPointMesh->ClearAllMeshSections();
        return;
    }

    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FLinearColor> VertexColors;
    TArray<FProcMeshTangent> Tangents;

    Vertices.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    Triangles.Reserve(Playback->LidarPointsUnreal.Num() * 6);
    Normals.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    UVs.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    VertexColors.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    Tangents.Reserve(Playback->LidarPointsUnreal.Num() * 4);

    for (const FVector& Point : Playback->LidarPointsUnreal)
    {
        AppendCellQuad(
            Vertices,
            Triangles,
            Normals,
            UVs,
            VertexColors,
            Tangents,
            Point,
            LidarPointColor,
            LidarPointSizeCentimeters,
            LidarPointHeightOffsetCentimeters);
    }

    LidarPointMesh->CreateMeshSection_LinearColor(
        0,
        Vertices,
        Triangles,
        Normals,
        UVs,
        VertexColors,
        Tangents,
        false);
}

void AQuadrotorMworksPlaybackActor::AppendCellQuad(
    TArray<FVector>& Vertices,
    TArray<int32>& Triangles,
    TArray<FVector>& Normals,
    TArray<FVector2D>& UVs,
    TArray<FLinearColor>& VertexColors,
    TArray<FProcMeshTangent>& Tangents,
    const FVector& Center,
    const FLinearColor& Color,
    float SizeCentimeters,
    float HeightOffsetCentimeters) const
{
    const int32 BaseIndex = Vertices.Num();
    const float HalfSize = FMath::Max(SizeCentimeters, 2.0f) * 0.5f;
    const FVector C = Center + FVector(0.0f, 0.0f, HeightOffsetCentimeters);
    Vertices.Append({
        C + FVector(-HalfSize, -HalfSize, 0.0f),
        C + FVector(HalfSize, -HalfSize, 0.0f),
        C + FVector(HalfSize, HalfSize, 0.0f),
        C + FVector(-HalfSize, HalfSize, 0.0f),
    });
    Triangles.Append({BaseIndex, BaseIndex + 1, BaseIndex + 2, BaseIndex, BaseIndex + 2, BaseIndex + 3});
    Normals.Append({FVector::UpVector, FVector::UpVector, FVector::UpVector, FVector::UpVector});
    UVs.Append({FVector2D(0.0f, 0.0f), FVector2D(1.0f, 0.0f), FVector2D(1.0f, 1.0f), FVector2D(0.0f, 1.0f)});
    VertexColors.Append({Color, Color, Color, Color});
    Tangents.Append({
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
    });
}

void AQuadrotorMworksPlaybackActor::BuildSectorMesh(
    UProceduralMeshComponent* Mesh,
    float InnerRadiusCm,
    float OuterRadiusCm,
    const FLinearColor& Color) const
{
    if (!Mesh || !Playback || OuterRadiusCm <= 0.0f || Playback->RadarFovDegrees <= 0.0f)
    {
        return;
    }

    const int32 Segments = FMath::Max(RadarSectorSegments, 3);
    const float HalfFovRadians = FMath::DegreesToRadians(0.5f * Playback->RadarFovDegrees);
    const float YawRadians = FMath::DegreesToRadians(Playback->RadarYawDegrees);
    const FVector Origin = Playback->LatestUnrealLocation + FVector(0.0f, 0.0f, RadarSectorHeightOffsetCentimeters);

    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FLinearColor> VertexColors;
    TArray<FProcMeshTangent> Tangents;

    Vertices.Reserve((Segments + 1) * 2);
    for (int32 Index = 0; Index <= Segments; ++Index)
    {
        const float Alpha = static_cast<float>(Index) / static_cast<float>(Segments);
        const float Angle = YawRadians - HalfFovRadians + Alpha * 2.0f * HalfFovRadians;
        const FVector Direction(FMath::Cos(Angle), FMath::Sin(Angle), 0.0f);
        Vertices.Add(Origin + Direction * FMath::Max(InnerRadiusCm, 0.0f));
        Vertices.Add(Origin + Direction * OuterRadiusCm);
        Normals.Add(FVector::UpVector);
        Normals.Add(FVector::UpVector);
        UVs.Add(FVector2D(Alpha, 0.0f));
        UVs.Add(FVector2D(Alpha, 1.0f));
        VertexColors.Add(Color);
        VertexColors.Add(Color);
        Tangents.Add(FProcMeshTangent(1.0f, 0.0f, 0.0f));
        Tangents.Add(FProcMeshTangent(1.0f, 0.0f, 0.0f));
    }

    for (int32 Index = 0; Index < Segments; ++Index)
    {
        const int32 A = 2 * Index;
        const int32 B = A + 1;
        const int32 C = A + 2;
        const int32 D = A + 3;
        Triangles.Append({A, B, D, A, D, C});
    }

    Mesh->CreateMeshSection_LinearColor(
        0,
        Vertices,
        Triangles,
        Normals,
        UVs,
        VertexColors,
        Tangents,
        false);
}
