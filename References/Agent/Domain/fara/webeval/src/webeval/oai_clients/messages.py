"""Native message and result types for webeval clients."""

import io
import base64
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

ToolSchema = Dict[str, Any]
Tool = ToolSchema


@dataclass
class LLMMessage:
    content: "str | List[Dict[str, Any]]"
    source: str = "user"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SystemMessage(LLMMessage):
    source: str = "system"


@dataclass
class UserMessage(LLMMessage):
    source: str = "user"


@dataclass
class AssistantMessage(LLMMessage):
    source: str = "assistant"


@dataclass
class ImageObj:
    """Image wrapper for handling screenshots and images."""

    image: Image.Image

    @classmethod
    def from_pil(cls, image: Image.Image) -> "ImageObj":
        return cls(image=image)

    @classmethod
    def from_base64(cls, b64: str) -> "ImageObj":
        return cls(image=Image.open(io.BytesIO(base64.b64decode(b64))))

    def to_base64(self) -> str:
        buffered = io.BytesIO()
        self.image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def resize(self, size: Tuple[int, int]) -> Image.Image:
        return self.image.resize(size)


@dataclass
class RequestUsage:
    """Token usage statistics for a single model call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    num_calls: int = 1

    def __add__(self, other: "RequestUsage") -> "RequestUsage":
        return RequestUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            reasoning_tokens=self.reasoning_tokens + other.reasoning_tokens,
            num_calls=self.num_calls + other.num_calls,
        )

    def get_cost(self, prompt_price: float, completion_price: float) -> float:
        return (self.prompt_tokens * prompt_price) + (
            self.completion_tokens * completion_price
        )


@dataclass
class ModelResponse:
    content: str
    usage: RequestUsage = field(default_factory=RequestUsage)


@dataclass
class CreateResult:
    """Result from a chat completion call.

    ``content`` is the textual response. The provider's full message
    object is preserved in ``message`` for callers that need tool calls
    or other structured fields.
    """

    content: Any
    usage: RequestUsage = field(default_factory=RequestUsage)
    finish_reason: Optional[str] = None
    cached: bool = False
    message: Any = None
    tool_calls: Optional[List[Any]] = None


@dataclass
class FunctionCall:
    id: str
    name: str
    arguments: Dict[str, Any]


def message_to_openai_format(message: LLMMessage) -> Dict[str, Any]:
    """Convert an :class:`LLMMessage` to an OpenAI chat-completion dict."""
    role = (
        "system"
        if isinstance(message, SystemMessage)
        else "assistant"
        if isinstance(message, AssistantMessage)
        else "user"
    )

    if isinstance(message.content, list):
        content_parts: List[Dict[str, Any]] = []
        for item in message.content:
            if isinstance(item, ImageObj):
                b64 = item.to_base64()
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    }
                )
            elif isinstance(item, Image.Image):
                b64 = ImageObj.from_pil(item).to_base64()
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    }
                )
            elif isinstance(item, str):
                content_parts.append({"type": "text", "text": item})
            elif isinstance(item, dict):
                content_parts.append(item)
        return {"role": role, "content": content_parts}
    return {"role": role, "content": message.content}
