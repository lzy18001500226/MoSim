#include "QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"

#include "Dom/JsonObject.h"
#include "Json.h"
#include "Serialization/JsonSerializer.h"

namespace
{
const TCHAR* CommandEchoSchema = TEXT("mosim.ue_command_echo.v1");

TSharedPtr<FJsonObject> ParseJsonObject(const FString& PayloadJson)
{
    TSharedPtr<FJsonObject> JsonObject;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(PayloadJson);
    if (!FJsonSerializer::Deserialize(Reader, JsonObject) || !JsonObject.IsValid())
    {
        return nullptr;
    }
    return JsonObject;
}

FString GetStringField(const TSharedPtr<FJsonObject>& Object, const FString& FieldName)
{
    FString Value;
    if (Object.IsValid())
    {
        Object->TryGetStringField(FieldName, Value);
    }
    return Value;
}
}

UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::IsCommandEchoPacketJson(
    const FString& EchoJson,
    FString& RejectReason) const
{
    RejectReason.Reset();
    const TSharedPtr<FJsonObject> EchoObject = ParseJsonObject(EchoJson);
    if (!EchoObject.IsValid())
    {
        RejectReason = TEXT("invalid_echo_json");
        return false;
    }

    if (GetStringField(EchoObject, TEXT("schema")) != CommandEchoSchema)
    {
        RejectReason = TEXT("unsupported_echo_schema");
        return false;
    }

    return true;
}

bool UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent::ApplyCommandEchoJsonToState(
    const FString& EchoJson,
    UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
    FQuadrotorMworksExperimentConsoleCommandState& OutState,
    FString& RejectReason) const
{
    RejectReason.Reset();
    if (!StateComponent)
    {
        RejectReason = TEXT("missing_state_component");
        return false;
    }

    if (!IsCommandEchoPacketJson(EchoJson, RejectReason))
    {
        return false;
    }

    return StateComponent->ApplyCommandEchoJson(EchoJson, OutState, RejectReason);
}
