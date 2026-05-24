// MIT License - Copyright (c) 2025 Italink

#pragma once

#include "CoreMinimal.h"

enum class ENodeCodeSectionFormat : uint8
{
	Graph,
	Properties,
	RawText
};

struct FNodeCodeNodeIR
{
	FString Index;
	FString ClassName;
	FGuid Guid;
	TMap<FString, FString> Properties;
	UObject* SourceObject = nullptr;
};

struct FNodeCodeLinkIR
{
	FString FromNodeIndex;
	FString FromOutputName;
	FString ToNodeIndex;
	FString ToInputName;
	bool bToGraphOutput = false;
};

struct FNodeCodeGraphIR
{
	TArray<FNodeCodeNodeIR> Nodes;
	TArray<FNodeCodeLinkIR> Links;
};

struct FNodeCodeSectionIR
{
	FString Type;
	FString Name;
	ENodeCodeSectionFormat Format = ENodeCodeSectionFormat::Graph;

	FNodeCodeGraphIR Graph;
	TMap<FString, FString> Properties;
	FString RawText;

	FString GetHeader() const
	{
		if (Name.IsEmpty())
		{
			return FString::Printf(TEXT("[%s]"), *Type);
		}
		return FString::Printf(TEXT("[%s:%s]"), *Type, *Name);
	}
};

struct FNodeCodeDocumentIR
{
	TArray<FNodeCodeSectionIR> Sections;
};

namespace NodeCodeUtils
{
	static constexpr int32 Base62IdLen = 22;
	static const TCHAR Base62Chars[] = TEXT("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ");

	inline FString GuidToBase62(const FGuid& G)
	{
		uint64 Hi = (static_cast<uint64>(G.A) << 32) | static_cast<uint64>(G.B);
		uint64 Lo = (static_cast<uint64>(G.C) << 32) | static_cast<uint64>(G.D);

		TCHAR Buf[Base62IdLen + 1];
		Buf[Base62IdLen] = 0;

		for (int32 i = Base62IdLen - 1; i >= 0; --i)
		{
			uint64 Remainder = 0;

			// 128-bit division by 62: divide (Hi:Lo) by 62
			Remainder = Hi % 62;
			Hi = Hi / 62;
			uint64 Combined = (Remainder << 32) | (Lo >> 32);
			uint64 QHi32 = Combined / 62;
			Remainder = Combined % 62;
			Combined = (Remainder << 32) | (Lo & 0xFFFFFFFF);
			uint64 QLo32 = Combined / 62;
			Remainder = Combined % 62;

			Lo = (QHi32 << 32) | QLo32;

			Buf[i] = Base62Chars[Remainder];
		}

		return FString(Base62IdLen, Buf);
	}

	inline FGuid Base62ToGuid(const FString& Str)
	{
		if (Str.Len() != Base62IdLen) return FGuid();

		uint64 Hi = 0, Lo = 0;

		for (int32 i = 0; i < Base62IdLen; ++i)
		{
			TCHAR Ch = Str[i];
			int32 Val;
			if (Ch >= '0' && Ch <= '9') Val = Ch - '0';
			else if (Ch >= 'a' && Ch <= 'z') Val = 10 + (Ch - 'a');
			else if (Ch >= 'A' && Ch <= 'Z') Val = 36 + (Ch - 'A');
			else return FGuid();

			// 128-bit multiply by 62 then add: (Hi:Lo) = (Hi:Lo)*62 + Val
			uint64 LoLo = (Lo & 0xFFFFFFFF) * 62;
			uint64 LoHi = (Lo >> 32) * 62 + (LoLo >> 32);
			Lo = ((LoHi & 0xFFFFFFFF) << 32) | (LoLo & 0xFFFFFFFF);
			Hi = Hi * 62 + (LoHi >> 32);

			Lo += Val;
			if (Lo < static_cast<uint64>(Val)) Hi++;
		}

		return FGuid(
			static_cast<uint32>(Hi >> 32),
			static_cast<uint32>(Hi & 0xFFFFFFFF),
			static_cast<uint32>(Lo >> 32),
			static_cast<uint32>(Lo & 0xFFFFFFFF)
		);
	}

	inline bool IsBase62Id(const FString& Id)
	{
		return Id.Len() == Base62IdLen;
	}

	inline bool IsNewNodeId(const FString& Id)
	{
		return Id.StartsWith(TEXT("new"));
	}

	inline FString EncodeSpaces(const FString& InStr)
	{
		return InStr.Replace(TEXT(" "), TEXT("_"));
	}

	inline bool MatchName(const FString& Encoded, const FString& Original)
	{
		if (Encoded == Original)
		{
			return true;
		}
		return Encoded.Replace(TEXT("_"), TEXT(" ")) == Original
			|| Encoded == Original.Replace(TEXT(" "), TEXT("_"));
	}

	inline bool ParseSectionHeader(const FString& Header, FString& OutType, FString& OutName)
	{
		FString Inner = Header;
		if (!Inner.RemoveFromStart(TEXT("[")) || !Inner.RemoveFromEnd(TEXT("]")))
		{
			return false;
		}
		Inner.TrimStartAndEndInline();
		int32 ColonPos;
		if (Inner.FindChar(':', ColonPos))
		{
			OutType = Inner.Left(ColonPos);
			OutName = Inner.Mid(ColonPos + 1);
		}
		else
		{
			OutType = Inner;
			OutName.Empty();
		}
		return !OutType.IsEmpty();
	}
}

struct FNodeCodeDiffResult
{
	TArray<FString> NodesAdded;
	TArray<FString> NodesRemoved;
	TArray<FString> NodesModified;
	TArray<FString> LinksAdded;
	TArray<FString> LinksRemoved;
	TArray<FString> CompileErrors;
};
