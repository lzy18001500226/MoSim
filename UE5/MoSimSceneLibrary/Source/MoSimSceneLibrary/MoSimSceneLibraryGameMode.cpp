#include "MoSimSceneLibraryGameMode.h"

#include "Components/LightComponent.h"
#include "Components/SkyLightComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/SkyLight.h"
#include "Engine/World.h"
#include "Dom/JsonObject.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "HAL/PlatformFileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "MworksReviewCameraPawn.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackActor.h"
#include "QuadrotorMworksUdpReceiverComponent.h"

AMoSimSceneLibraryGameMode::AMoSimSceneLibraryGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
    DefaultPawnClass = AMworksReviewCameraPawn::StaticClass();
}

void AMoSimSceneLibraryGameMode::BeginPlay()
{
    Super::BeginPlay();

    const bool bSceneReviewOnly = FParse::Param(FCommandLine::Get(), TEXT("MoSimSceneReview"));
    const bool bSimulationReview = FParse::Param(FCommandLine::Get(), TEXT("MoSimSimulationReview"));
    bSceneReviewModeActive = bSceneReviewOnly || bSimulationReview;
    const bool bDisablePreviewMap =
        bSceneReviewOnly || bSimulationReview || FParse::Param(FCommandLine::Get(), TEXT("MoSimNoPreviewMap"));
    const bool bDisablePlayback =
        bSceneReviewOnly || FParse::Param(FCommandLine::Get(), TEXT("MoSimNoPlayback"));
    FParse::Value(FCommandLine::Get(), TEXT("MoSimPlaybackActorCount="), PlaybackActorCount);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimPlaybackBaseUdpPort="), PlaybackBaseUdpPort);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimObservabilityRunId="), ObservabilityRunId);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimUeReceiverMetrics="), UeReceiverMetricsOutputPath);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimUeFrameMetrics="), UeFrameMetricsOutputPath);
    FrameMetricsWindowStartSeconds = FPlatformTime::Seconds();
    bFactoryCalibrationFrameEnabled = FParse::Param(FCommandLine::Get(), TEXT("MoSimFactoryCalibrationFrame"));
    FParse::Value(FCommandLine::Get(), TEXT("MoSimFactoryCalibrationCsv="), FactoryCalibrationCsvPath);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimFactoryCalibrationMarkerCsv="), FactoryCalibrationMarkerCsvPath);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimFactoryCalibrationLineThickness="), FactoryCalibrationLineThickness);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimFactoryCalibrationLifetime="), FactoryCalibrationDrawLifetimeSeconds);
    FactoryCalibrationLineThickness = FMath::Max(1.0f, FactoryCalibrationLineThickness);
    FactoryCalibrationDrawLifetimeSeconds = FMath::Max(0.05f, FactoryCalibrationDrawLifetimeSeconds);
    if (bFactoryCalibrationFrameEnabled)
    {
        LoadFactoryCalibrationFrame();
        LoadFactoryCalibrationMarkers();
    }
    bFactoryGazeboOverlayEnabled = FParse::Param(FCommandLine::Get(), TEXT("MoSimFactoryGazeboOverlay"));
    FParse::Value(FCommandLine::Get(), TEXT("MoSimFactoryGazeboOverlayCsv="), FactoryGazeboOverlayCsvPath);
    FParse::Value(FCommandLine::Get(), TEXT("MoSimFactoryGazeboOverlayZOffsetCm="), FactoryGazeboOverlayZOffsetCm);
    if (bFactoryGazeboOverlayEnabled)
    {
        LoadFactoryGazeboOverlay();
    }

    if (!bSpawnDefaultRendererActors)
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS renderer auto-spawn disabled."));
        return;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        UE_LOG(LogTemp, Error, TEXT("MWORKS renderer GameMode has no valid world."));
        return;
    }

    FActorSpawnParameters SpawnParameters;
    SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    if (bSpawnDefaultReviewLighting)
    {
        if (FParse::Param(FCommandLine::Get(), TEXT("MoSimDayReview")))
        {
            bForceDaylightReviewExposure = !FParse::Param(FCommandLine::Get(), TEXT("MoSimNoDayReviewExposure"));
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSunIntensity="), ReviewSunIntensity);
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSkyLightIntensity="), ReviewSkyLightIntensity);
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewExposureBias="), ReviewExposureBias);
        }
        else
        {
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSunIntensity="), ReviewSunIntensity);
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSkyLightIntensity="), ReviewSkyLightIntensity);
        }
        SpawnDefaultReviewLighting(World, SpawnParameters);
    }

    if (bSceneReviewModeActive)
    {
        EnforceSceneReviewCamera(World);
    }

    if (bDisablePreviewMap)
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS preview map auto-spawn disabled by command line."));
    }
    else if (DefaultRenderMapJson.IsEmpty())
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS preview map auto-spawn skipped because DefaultRenderMapJson is empty."));
    }
    else
    {
        SpawnedMapActor = World->SpawnActor<AQuadrotorMworksMapActor>(
            AQuadrotorMworksMapActor::StaticClass(),
            MapActorLocation,
            FRotator::ZeroRotator,
            SpawnParameters);

        if (SpawnedMapActor)
        {
#if WITH_EDITOR
            SpawnedMapActor->SetActorLabel(TEXT("MWORKS_Render_Map"));
#endif
            SpawnedMapActor->RenderMapJson = DefaultRenderMapJson;
            SpawnedMapActor->LoadRenderMapSummary();
            UE_LOG(LogTemp, Display, TEXT("MWORKS renderer spawned map actor with map json: %s"), *DefaultRenderMapJson);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("MWORKS renderer failed to spawn map actor."));
        }
    }

    if (bDisablePlayback)
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS playback actor auto-spawn disabled by command line."));
    }
    else
    {
        const int32 ClampedPlaybackActorCount = FMath::Max(1, PlaybackActorCount);
        SpawnedPlaybackActors.Reset();
        for (int32 Index = 0; Index < ClampedPlaybackActorCount; ++Index)
        {
            AQuadrotorMworksPlaybackActor* PlaybackActor = World->SpawnActor<AQuadrotorMworksPlaybackActor>(
                AQuadrotorMworksPlaybackActor::StaticClass(),
                PlaybackActorLocation + PlaybackActorSpacing * Index,
                FRotator::ZeroRotator,
                SpawnParameters);

            if (PlaybackActor)
            {
#if WITH_EDITOR
                PlaybackActor->SetActorLabel(FString::Printf(TEXT("MWORKS_Quadrotor_Playback_%d"), Index + 1));
#endif
                PlaybackActor->MapActor = SpawnedMapActor;
                if (PlaybackActor->Receiver)
                {
                    PlaybackActor->Receiver->StopReceiver();
                    PlaybackActor->Receiver->ListenPort = PlaybackBaseUdpPort + Index;
                    PlaybackActor->Receiver->ObservabilityRunId = ObservabilityRunId;
                    PlaybackActor->Receiver->MetricsOutputPath = Index == 0 ? UeReceiverMetricsOutputPath : FString();
                    PlaybackActor->Receiver->StartReceiver();
                }
                SpawnedPlaybackActors.Add(PlaybackActor);
                if (Index == 0)
                {
                    SpawnedPlaybackActor = PlaybackActor;
                }
                UE_LOG(
                    LogTemp,
                    Display,
                    TEXT("MWORKS renderer spawned playback actor %d/%d udp_port=%d and linked map actor."),
                    Index + 1,
                    ClampedPlaybackActorCount,
                    PlaybackBaseUdpPort + Index);
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("MWORKS renderer failed to spawn playback actor %d."), Index + 1);
            }
        }
    }
}

void AMoSimSceneLibraryGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!UeFrameMetricsOutputPath.IsEmpty() && DeltaSeconds > 0.0f)
    {
        FrameMetricsTotalSeconds += DeltaSeconds;
        FrameMetricsMaxSeconds = FMath::Max(FrameMetricsMaxSeconds, static_cast<double>(DeltaSeconds));
        ++FrameMetricsCount;
        if (DeltaSeconds >= 0.05f)
        {
            ++FrameMetricsHitchCount;
        }
        const double WindowSeconds = FPlatformTime::Seconds() - FrameMetricsWindowStartSeconds;
        if (WindowSeconds >= 5.0)
        {
            WriteFrameTimingMetrics(WindowSeconds);
        }
    }

    if (bSceneReviewModeActive)
    {
        EnforceSceneReviewCamera(GetWorld());
    }
    if (bFactoryCalibrationFrameEnabled)
    {
        DrawFactoryCalibrationFrame(GetWorld());
    }
    if (bFactoryGazeboOverlayEnabled)
    {
        DrawFactoryGazeboOverlay(GetWorld());
    }
}

void AMoSimSceneLibraryGameMode::WriteFrameTimingMetrics(double WindowSeconds)
{
    TSharedRef<FJsonObject> Metrics = MakeShared<FJsonObject>();
    Metrics->SetStringField(TEXT("schema"), TEXT("mosim.unreal_frame_timing.v1"));
    Metrics->SetStringField(TEXT("run_id"), ObservabilityRunId);
    Metrics->SetNumberField(TEXT("window_s"), WindowSeconds);
    Metrics->SetNumberField(TEXT("ue_fps"), FrameMetricsCount / FMath::Max(WindowSeconds, 0.001));
    Metrics->SetNumberField(TEXT("ue_frame_ms_mean"), 1000.0 * FrameMetricsTotalSeconds / FMath::Max(1, FrameMetricsCount));
    Metrics->SetNumberField(TEXT("ue_frame_ms_max"), 1000.0 * FrameMetricsMaxSeconds);
    Metrics->SetNumberField(TEXT("hitch_count_50ms"), FrameMetricsHitchCount);
    TArray<TSharedPtr<FJsonValue>> Unavailable;
    Unavailable.Add(MakeShared<FJsonValueString>(TEXT("ue_game_ms")));
    Unavailable.Add(MakeShared<FJsonValueString>(TEXT("ue_draw_ms")));
    Unavailable.Add(MakeShared<FJsonValueString>(TEXT("ue_gpu_ms")));
    Metrics->SetArrayField(TEXT("unavailable_metrics"), Unavailable);
    Metrics->SetNumberField(TEXT("updated_at_unix"), FDateTime::UtcNow().ToUnixTimestamp());
    FString Json;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
    FJsonSerializer::Serialize(Metrics, Writer);
    const FString AbsolutePath = FPaths::ConvertRelativePathToFull(UeFrameMetricsOutputPath);
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
    PlatformFile.CreateDirectoryTree(*FPaths::GetPath(AbsolutePath));
    const FString TemporaryPath = AbsolutePath + TEXT(".tmp");
    if (FFileHelper::SaveStringToFile(Json, *TemporaryPath))
    {
        if (PlatformFile.FileExists(*AbsolutePath))
        {
            PlatformFile.DeleteFile(*AbsolutePath);
        }
        PlatformFile.MoveFile(*AbsolutePath, *TemporaryPath);
    }
    FrameMetricsWindowStartSeconds = FPlatformTime::Seconds();
    FrameMetricsTotalSeconds = 0.0;
    FrameMetricsMaxSeconds = 0.0;
    FrameMetricsCount = 0;
    FrameMetricsHitchCount = 0;
}

void AMoSimSceneLibraryGameMode::LoadFactoryCalibrationFrame()
{
    FactoryCalibrationSegments.Reset();
    if (FactoryCalibrationCsvPath.IsEmpty())
    {
        FactoryCalibrationCsvPath = FPaths::ConvertRelativePathToFull(
            FPaths::ProjectDir(),
            TEXT("../../Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_segments.csv"));
    }
    else if (FPaths::IsRelative(FactoryCalibrationCsvPath))
    {
        FactoryCalibrationCsvPath = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), FactoryCalibrationCsvPath);
    }

    FString CsvText;
    if (!FFileHelper::LoadFileToString(CsvText, *FactoryCalibrationCsvPath))
    {
        UE_LOG(LogTemp, Error, TEXT("MoSim Factory calibration CSV missing: %s"), *FactoryCalibrationCsvPath);
        return;
    }

    TArray<FString> Lines;
    CsvText.ParseIntoArrayLines(Lines, true);
    for (int32 LineIndex = 1; LineIndex < Lines.Num(); ++LineIndex)
    {
        TArray<FString> Columns;
        Lines[LineIndex].ParseIntoArray(Columns, TEXT(","), false);
        if (Columns.Num() < 19)
        {
            continue;
        }

        FMoSimFactoryCalibrationSegment Segment;
        Segment.StartUnrealCm = FVector(
            FCString::Atof(*Columns[9]),
            FCString::Atof(*Columns[10]),
            FCString::Atof(*Columns[11]));
        Segment.EndUnrealCm = FVector(
            FCString::Atof(*Columns[12]),
            FCString::Atof(*Columns[13]),
            FCString::Atof(*Columns[14]));
        const FLinearColor LinearColor(
            FCString::Atof(*Columns[15]),
            FCString::Atof(*Columns[16]),
            FCString::Atof(*Columns[17]),
            FCString::Atof(*Columns[18]));
        Segment.Color = LinearColor.ToFColor(true);
        FactoryCalibrationSegments.Add(Segment);
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Factory calibration frame loaded: csv=%s segments=%d"),
        *FactoryCalibrationCsvPath,
        FactoryCalibrationSegments.Num());
}

void AMoSimSceneLibraryGameMode::LoadFactoryCalibrationMarkers()
{
    FactoryCalibrationMarkers.Reset();
    if (FactoryCalibrationMarkerCsvPath.IsEmpty())
    {
        FactoryCalibrationMarkerCsvPath = FPaths::ConvertRelativePathToFull(
            FPaths::ProjectDir(),
            TEXT("../../Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_markers.csv"));
    }
    else if (FPaths::IsRelative(FactoryCalibrationMarkerCsvPath))
    {
        FactoryCalibrationMarkerCsvPath = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), FactoryCalibrationMarkerCsvPath);
    }

    FString CsvText;
    if (!FFileHelper::LoadFileToString(CsvText, *FactoryCalibrationMarkerCsvPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim Factory calibration marker CSV missing: %s"), *FactoryCalibrationMarkerCsvPath);
        return;
    }

    TArray<FString> Lines;
    CsvText.ParseIntoArrayLines(Lines, true);
    const bool bNewCalibrationMarkerFormat = Lines.Num() > 0 && Lines[0].Contains(TEXT("size_x_m"));
    for (int32 LineIndex = 1; LineIndex < Lines.Num(); ++LineIndex)
    {
        TArray<FString> Columns;
        Lines[LineIndex].ParseIntoArray(Columns, TEXT(","), false);
        if (bNewCalibrationMarkerFormat)
        {
            if (Columns.Num() < 19)
            {
                continue;
            }

            FMoSimFactoryCalibrationMarker Marker;
            Marker.Label = Columns[1];
            Marker.UnrealCm = FVector(
                FCString::Atof(*Columns[9]),
                FCString::Atof(*Columns[10]),
                FCString::Atof(*Columns[11]));
            const FLinearColor LinearColor(
                FCString::Atof(*Columns[15]),
                FCString::Atof(*Columns[16]),
                FCString::Atof(*Columns[17]),
                FCString::Atof(*Columns[18]));
            Marker.Color = LinearColor.ToFColor(true);
            Marker.BoxExtentCm = FVector(
                FMath::Max(2.0f, FCString::Atof(*Columns[12]) * 50.0f),
                FMath::Max(2.0f, FCString::Atof(*Columns[13]) * 50.0f),
                FMath::Max(2.0f, FCString::Atof(*Columns[14]) * 50.0f));
            Marker.RadiusCm = Marker.BoxExtentCm.GetMax();
            Marker.bDrawBox = true;
            FactoryCalibrationMarkers.Add(Marker);
        }
        else
        {
            if (Columns.Num() < 12)
            {
                continue;
            }

            FMoSimFactoryCalibrationMarker Marker;
            Marker.Label = Columns[0];
            Marker.UnrealCm = FVector(
                FCString::Atof(*Columns[4]),
                FCString::Atof(*Columns[5]),
                FCString::Atof(*Columns[6]));
            const FLinearColor LinearColor(
                FCString::Atof(*Columns[7]),
                FCString::Atof(*Columns[8]),
                FCString::Atof(*Columns[9]),
                FCString::Atof(*Columns[10]));
            Marker.Color = LinearColor.ToFColor(true);
            Marker.RadiusCm = FMath::Max(2.0f, FCString::Atof(*Columns[11]));
            FactoryCalibrationMarkers.Add(Marker);
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Factory calibration markers loaded: csv=%s markers=%d"),
        *FactoryCalibrationMarkerCsvPath,
        FactoryCalibrationMarkers.Num());
}

void AMoSimSceneLibraryGameMode::DrawFactoryCalibrationFrame(UWorld* World) const
{
    if (!World)
    {
        return;
    }

    for (const FMoSimFactoryCalibrationSegment& Segment : FactoryCalibrationSegments)
    {
        DrawDebugLine(
            World,
            Segment.StartUnrealCm,
            Segment.EndUnrealCm,
            Segment.Color,
            false,
            FactoryCalibrationDrawLifetimeSeconds,
            1,
            FactoryCalibrationLineThickness);
    }
    for (const FMoSimFactoryCalibrationMarker& Marker : FactoryCalibrationMarkers)
    {
        if (Marker.bDrawBox)
        {
            DrawDebugBox(
                World,
                Marker.UnrealCm,
                Marker.BoxExtentCm,
                Marker.Color,
                false,
                FactoryCalibrationDrawLifetimeSeconds,
                1,
                FactoryCalibrationLineThickness);
        }
        else
        {
            DrawDebugSphere(World, Marker.UnrealCm, Marker.RadiusCm, 16, Marker.Color, false, 0.20f, 0, 2.0f);
        }
        DrawDebugLine(
            World,
            Marker.UnrealCm + FVector(0.0f, 0.0f, -30.0f),
            Marker.UnrealCm + FVector(0.0f, 0.0f, 30.0f),
            Marker.Color,
            false,
            FactoryCalibrationDrawLifetimeSeconds,
            1,
            FactoryCalibrationLineThickness);
        if (!Marker.Label.IsEmpty())
        {
            DrawDebugString(
                World,
                Marker.UnrealCm + FVector(0.0f, 0.0f, Marker.RadiusCm + 35.0f),
                Marker.Label,
                nullptr,
                Marker.Color,
                FactoryCalibrationDrawLifetimeSeconds,
                true,
                1.1f);
        }
    }
}

void AMoSimSceneLibraryGameMode::LoadFactoryGazeboOverlay()
{
    FactoryGazeboOverlayPoints.Reset();
    if (FactoryGazeboOverlayCsvPath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim Factory Gazebo overlay CSV path is empty."));
        return;
    }
    if (FPaths::IsRelative(FactoryGazeboOverlayCsvPath))
    {
        FactoryGazeboOverlayCsvPath = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), FactoryGazeboOverlayCsvPath);
    }

    FString CsvText;
    if (!FFileHelper::LoadFileToString(CsvText, *FactoryGazeboOverlayCsvPath))
    {
        UE_LOG(LogTemp, Error, TEXT("MoSim Factory Gazebo overlay CSV missing: %s"), *FactoryGazeboOverlayCsvPath);
        return;
    }

    TArray<FString> Lines;
    CsvText.ParseIntoArrayLines(Lines, true);
    for (int32 LineIndex = 1; LineIndex < Lines.Num(); ++LineIndex)
    {
        TArray<FString> Columns;
        Lines[LineIndex].ParseIntoArray(Columns, TEXT(","), false);
        if (Columns.Num() < 13)
        {
            continue;
        }

        FMoSimFactoryOverlayPoint Point;
        Point.UnrealCm = FVector(
            FCString::Atof(*Columns[5]),
            FCString::Atof(*Columns[6]),
            FCString::Atof(*Columns[7]));
        const FLinearColor LinearColor(
            FCString::Atof(*Columns[8]),
            FCString::Atof(*Columns[9]),
            FCString::Atof(*Columns[10]),
            FCString::Atof(*Columns[11]));
        Point.Color = LinearColor.ToFColor(true);
        Point.Size = FMath::Max(1.0f, FCString::Atof(*Columns[12]));
        FactoryGazeboOverlayPoints.Add(Point);
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Factory Gazebo overlay loaded: csv=%s points=%d"),
        *FactoryGazeboOverlayCsvPath,
        FactoryGazeboOverlayPoints.Num());
}

void AMoSimSceneLibraryGameMode::DrawFactoryGazeboOverlay(UWorld* World) const
{
    if (!World)
    {
        return;
    }

    for (const FMoSimFactoryOverlayPoint& Point : FactoryGazeboOverlayPoints)
    {
        DrawDebugPoint(
            World,
            Point.UnrealCm + FVector(0.0f, 0.0f, FactoryGazeboOverlayZOffsetCm),
            Point.Size,
            Point.Color,
            false,
            0.20f,
            0);
    }
}

void AMoSimSceneLibraryGameMode::SpawnDefaultReviewLighting(UWorld* World, const FActorSpawnParameters& SpawnParameters)
{
    if (!World)
    {
        return;
    }

    SpawnedReviewSunLight = World->SpawnActor<ADirectionalLight>(
        ADirectionalLight::StaticClass(),
        FVector(0.0f, 0.0f, 3000.0f),
        ReviewSunRotation,
        SpawnParameters);

    if (SpawnedReviewSunLight)
    {
#if WITH_EDITOR
        SpawnedReviewSunLight->SetActorLabel(TEXT("MWORKS_Review_SunLight"));
#endif
        if (ULightComponent* LightComponent = SpawnedReviewSunLight->GetLightComponent())
        {
            LightComponent->SetMobility(EComponentMobility::Movable);
            LightComponent->SetIntensity(ReviewSunIntensity);
            LightComponent->SetLightColor(FLinearColor(1.0f, 0.96f, 0.86f));
            LightComponent->SetCastShadows(false);
        }
    }

    SpawnedReviewSkyLight = World->SpawnActor<ASkyLight>(
        ASkyLight::StaticClass(),
        FVector(0.0f, 0.0f, 1000.0f),
        FRotator::ZeroRotator,
        SpawnParameters);

    if (SpawnedReviewSkyLight)
    {
#if WITH_EDITOR
        SpawnedReviewSkyLight->SetActorLabel(TEXT("MWORKS_Review_SkyLight"));
#endif
        if (USkyLightComponent* SkyComponent = SpawnedReviewSkyLight->GetLightComponent())
        {
            SkyComponent->SetMobility(EComponentMobility::Movable);
            SkyComponent->SetIntensity(ReviewSkyLightIntensity);
            SkyComponent->RecaptureSky();
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS renderer spawned default review lighting: sun=%s sky=%s"),
        SpawnedReviewSunLight ? TEXT("true") : TEXT("false"),
        SpawnedReviewSkyLight ? TEXT("true") : TEXT("false"));

    if (bForceDaylightReviewExposure)
    {
        SpawnedReviewPostProcessVolume = World->SpawnActor<APostProcessVolume>(
            APostProcessVolume::StaticClass(),
            FVector::ZeroVector,
            FRotator::ZeroRotator,
            SpawnParameters);

        if (SpawnedReviewPostProcessVolume)
        {
#if WITH_EDITOR
            SpawnedReviewPostProcessVolume->SetActorLabel(TEXT("MWORKS_Review_Daylight_PostProcess"));
#endif
            SpawnedReviewPostProcessVolume->bUnbound = true;
            SpawnedReviewPostProcessVolume->BlendWeight = 1.0f;
            SpawnedReviewPostProcessVolume->Priority = 10000.0f;
            FPostProcessSettings& Settings = SpawnedReviewPostProcessVolume->Settings;
            Settings.bOverride_AutoExposureMinBrightness = true;
            Settings.bOverride_AutoExposureMaxBrightness = true;
            Settings.bOverride_AutoExposureBias = true;
            Settings.AutoExposureMinBrightness = 2.0f;
            Settings.AutoExposureMaxBrightness = 2.0f;
            Settings.AutoExposureBias = ReviewExposureBias;
            Settings.bOverride_MotionBlurAmount = true;
            Settings.MotionBlurAmount = 0.0f;

            UE_LOG(
                LogTemp,
                Display,
                TEXT("MWORKS renderer forced daylight review exposure: bias=%.2f"),
                ReviewExposureBias);
        }
    }
}

AMworksReviewCameraPawn* AMoSimSceneLibraryGameMode::FindOrSpawnReviewCamera(
    UWorld* World,
    const FActorSpawnParameters& SpawnParameters)
{
    if (!World)
    {
        return nullptr;
    }

    if (IsValid(ActiveReviewCameraPawn))
    {
        return ActiveReviewCameraPawn;
    }

    TArray<AActor*> ExistingReviewPawns;
    UGameplayStatics::GetAllActorsOfClass(World, AMworksReviewCameraPawn::StaticClass(), ExistingReviewPawns);
    for (AActor* Actor : ExistingReviewPawns)
    {
        if (AMworksReviewCameraPawn* ReviewPawn = Cast<AMworksReviewCameraPawn>(Actor))
        {
            ActiveReviewCameraPawn = ReviewPawn;
            return ActiveReviewCameraPawn;
        }
    }

    ActiveReviewCameraPawn = World->SpawnActor<AMworksReviewCameraPawn>(
        AMworksReviewCameraPawn::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParameters);

    if (ActiveReviewCameraPawn)
    {
#if WITH_EDITOR
        ActiveReviewCameraPawn->SetActorLabel(TEXT("MWORKS_Review_Camera"));
#endif
        UE_LOG(LogTemp, Display, TEXT("MWORKS scene-review spawned missing review camera pawn."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MWORKS scene-review failed to spawn review camera pawn."));
    }

    return ActiveReviewCameraPawn;
}

void AMoSimSceneLibraryGameMode::DisableImportedPawnInput(APawn* Pawn, APlayerController* PlayerController) const
{
    if (!Pawn || Pawn == ActiveReviewCameraPawn)
    {
        return;
    }

    Pawn->AutoPossessPlayer = EAutoReceiveInput::Disabled;
    Pawn->AutoReceiveInput = EAutoReceiveInput::Disabled;
    if (PlayerController && Pawn->GetController() == PlayerController)
    {
        Pawn->DisableInput(PlayerController);
    }
}

void AMoSimSceneLibraryGameMode::EnforceSceneReviewCamera(UWorld* World)
{
    if (!World)
    {
        return;
    }

    FActorSpawnParameters SpawnParameters;
    SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AMworksReviewCameraPawn* ReviewPawn = FindOrSpawnReviewCamera(World, SpawnParameters);
    APlayerController* PlayerController = UGameplayStatics::GetPlayerController(World, 0);

    if (!ReviewPawn || !PlayerController)
    {
        return;
    }

    TArray<AActor*> Pawns;
    UGameplayStatics::GetAllActorsOfClass(World, APawn::StaticClass(), Pawns);
    int32 DisabledPawnCount = 0;
    for (AActor* Actor : Pawns)
    {
        APawn* Pawn = Cast<APawn>(Actor);
        if (Pawn && Pawn != ReviewPawn)
        {
            DisableImportedPawnInput(Pawn, PlayerController);
            ++DisabledPawnCount;
        }
    }

    const bool bNeedsPossess = PlayerController->GetPawn() != ReviewPawn;
    if (bNeedsPossess)
    {
        PlayerController->Possess(ReviewPawn);
    }
    ReviewPawn->ApplyReviewInputMode(PlayerController);
    if (FParse::Param(FCommandLine::Get(), TEXT("MoSimFollowPlaybackCamera")))
    {
        TArray<AActor*> FollowActors;
        FollowActors.Reserve(SpawnedPlaybackActors.Num());
        for (AQuadrotorMworksPlaybackActor* PlaybackActor : SpawnedPlaybackActors)
        {
            if (IsValid(PlaybackActor))
            {
                FollowActors.Add(PlaybackActor);
            }
        }
        ReviewPawn->SetFollowTargets(FollowActors);
    }

    const double NowSeconds = World->GetTimeSeconds();
    if (bNeedsPossess || NowSeconds - LastReviewCameraPossessLogTimeSeconds > 5.0)
    {
        LastReviewCameraPossessLogTimeSeconds = NowSeconds;
        const APawn* CurrentPawn = PlayerController->GetPawn();
        const FString PawnName = CurrentPawn ? CurrentPawn->GetName() : TEXT("<none>");
        UE_LOG(
            LogTemp,
            Display,
            TEXT("MWORKS scene-review control enforced: pawn=%s review_pawn=%s disabled_imported_pawns=%d"),
            *PawnName,
            *ReviewPawn->GetName(),
            DisabledPawnCount);
    }
}
