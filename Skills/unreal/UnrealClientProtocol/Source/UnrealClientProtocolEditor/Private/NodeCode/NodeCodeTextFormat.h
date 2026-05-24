// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"
#include "NodeCode/NodeCodeTypes.h"

class FNodeCodeTextFormat
{
public:
	static FString DocumentToText(const FNodeCodeDocumentIR& Document);
	static FNodeCodeDocumentIR ParseDocument(const FString& Text);

	static FString SectionToText(const FNodeCodeSectionIR& Section);
	static FNodeCodeSectionIR ParseSection(const FString& Text, const FString& Type, const FString& Name);

	static FString DiffResultToJson(const FNodeCodeDiffResult& Result);

	static void ValidateGraph(FNodeCodeGraphIR& Graph, TArray<FString>& OutWarnings);

private:
	static FString GraphToText(const FNodeCodeGraphIR& IR);
	static FString PropertiesToText(const TMap<FString, FString>& Properties);

	static void ParseGraphLines(const TArray<FString>& Lines, FNodeCodeGraphIR& OutGraph);
	static void ParsePropertyLines(const TArray<FString>& Lines, TMap<FString, FString>& OutProperties);

	static bool ParseNodeLine(const FString& Line, FNodeCodeNodeIR& OutNode);
	static bool ParseLinkLine(const FString& Line, const FString& OwnerNodeIndex, FNodeCodeLinkIR& OutLink);
};
