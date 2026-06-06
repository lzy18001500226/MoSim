"""Conversation memory management for PentestAgent."""

from typing import Awaitable, Callable, List, Optional

SUMMARY_PROMPT = """Summarize the following conversation segment for a penetration testing agent.
The summary will be used to continue the security assessment, so preserve all critical operational details.

What to preserve:
- Discovered targets (IPs, domains, hostnames) and network topology
- Services, versions, and technologies identified (keep exact version strings)
- Open ports and running services with specific details
- Vulnerabilities found or suspected (CVEs, misconfigurations, weaknesses)
- Credentials, tokens, API keys, or authentication details discovered
- Attack vectors attempted and their outcomes (success or failure)
- System architecture and relationships between hosts
- Important error messages or behaviors that may indicate vulnerabilities
- Current testing strategy and next planned steps

Compression approach:
- Consolidate redundant or repetitive findings into single statements
- Reduce verbose tool output while maintaining key technical findings
- Keep technical precision: exact paths, URLs, parameters, version numbers
- Remove conversational back-and-forth but preserve decisions made

Conversation segment:
{conversation}

Provide a concise technical summary:"""


class ConversationMemory:
    """Manages conversation history with token limits and summarization."""

    def __init__(
        self,
        max_tokens: int = 128000,
        reserve_ratio: float = 0.8,
        recent_to_keep: int = 10,
        summarize_threshold: float = 0.6,
    ):
        """
        Initialize conversation memory.

        Args:
            max_tokens: Maximum context tokens
            reserve_ratio: Ratio of tokens to use (leave room for response)
            recent_to_keep: Number of recent messages to keep in full
            summarize_threshold: Summarize when history exceeds this ratio of budget
        """
        self.max_tokens = max_tokens
        self.reserve_ratio = reserve_ratio
        self.recent_to_keep = recent_to_keep
        self.summarize_threshold = summarize_threshold
        self._encoder = None
        self._cached_summary: Optional[str] = None
        self._summarized_count: int = 0

    @property
    def encoder(self):
        """Lazy load the tokenizer."""
        if self._encoder is None:
            try:
                import tiktoken

                self._encoder = tiktoken.get_encoding("cl100k_base")
            except ImportError:
                self._encoder = None
        return self._encoder

    def _count_tokens_with_litellm(self, text: str, model: str) -> Optional[int]:
        """Try to count tokens using litellm for better accuracy."""
        try:
            import litellm

            count = litellm.token_counter(model=model, text=text)
            return int(count)
        except Exception:
            return None

    @property
    def token_budget(self) -> int:
        """Available tokens for history."""
        return int(self.max_tokens * self.reserve_ratio)

    def get_messages(self, messages: List[dict]) -> List[dict]:
        """
        Get messages that fit within token limit (sync, no summarization).
        Falls back to truncation if over budget.

        Args:
            messages: Full conversation history

        Returns:
            Messages that fit within the token budget
        """
        if not messages:
            return []

        # If we have a cached summary, prepend it
        if self._cached_summary and len(messages) > self._summarized_count:
            result = [
                {
                    "role": "system",
                    "content": f"Previous conversation summary:\n{self._cached_summary}",
                }
            ]
            # Add messages after the summarized portion
            recent = messages[self._summarized_count :]
            result.extend(
                self._truncate_to_fit(
                    recent, self.token_budget - self._count_tokens(result[0])
                )
            )
            return result

        return self._truncate_to_fit(messages, self.token_budget)

    async def get_messages_with_summary(
        self, messages: List[dict], llm_call: Callable[[str], Awaitable[str]]
    ) -> List[dict]:
        """
        Get messages, summarizing older ones if needed.

        Args:
            messages: Full conversation history
            llm_call: Async function to call LLM for summarization

        Returns:
            Messages with older ones summarized if over threshold
        """
        if not messages:
            return []

        total_tokens = self.get_total_tokens(messages)
        threshold_tokens = int(self.token_budget * self.summarize_threshold)

        # Check if we need to summarize
        if total_tokens <= threshold_tokens:
            return messages

        # Don't summarize if we don't have enough messages
        if len(messages) <= self.recent_to_keep:
            return self._truncate_to_fit(messages, self.token_budget)

        # Split messages: older to summarize, recent to keep
        split_point = len(messages) - self.recent_to_keep
        older = messages[:split_point]
        recent = messages[-self.recent_to_keep :]

        # Check if we already summarized these messages
        if split_point <= self._summarized_count and self._cached_summary:
            result = [
                {
                    "role": "system",
                    "content": f"Previous conversation summary:\n{self._cached_summary}",
                }
            ]
            result.extend(recent)
            return result

        # Summarize older messages
        summary = await self._summarize(older, llm_call)

        # Cache the summary
        self._cached_summary = summary
        self._summarized_count = split_point

        # Build result
        result = [
            {"role": "system", "content": f"Previous conversation summary:\n{summary}"}
        ]
        result.extend(recent)

        return result

    async def _summarize(
        self, messages: List[dict], llm_call: Callable[[str], Awaitable[str]]
    ) -> str:
        """
        Summarize a list of messages using chunked approach for better granularity.

        Args:
            messages: Messages to summarize
            llm_call: Async function to call LLM

        Returns:
            Summary string
        """
        if not messages:
            return "[No messages to summarize]"

        # Use chunked summarization for better context preservation
        # Process in chunks of 8-12 messages for balance between detail and efficiency
        chunk_size = 10
        summaries = []

        for i in range(0, len(messages), chunk_size):
            chunk = messages[i : i + chunk_size]
            conversation_text = self._format_for_summary(chunk)
            prompt = SUMMARY_PROMPT.format(conversation=conversation_text)

            try:
                chunk_summary = await llm_call(prompt)
                if chunk_summary and chunk_summary.strip():
                    summaries.append(chunk_summary.strip())
            except Exception as e:
                # Log failure but continue with other chunks
                summaries.append(
                    f"[{len(chunk)} messages from segment {i // chunk_size + 1} - summary failed: {e}]"
                )

        # Combine chunk summaries
        if not summaries:
            return f"[{len(messages)} earlier messages - all summarization attempts failed]"

        # If we have multiple summaries, join them with context markers
        if len(summaries) == 1:
            return summaries[0]
        else:
            combined = "\n\n".join(
                f"Segment {i + 1}: {summary}" for i, summary in enumerate(summaries)
            )
            return combined

    def _format_for_summary(self, messages: List[dict]) -> str:
        """Format messages as text for summarization."""
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Preserve more content for tool outputs (they contain findings)
            # but still limit to avoid overwhelming the summarizer
            max_length = 4000 if role == "tool" else 2000
            if len(content) > max_length:
                # For tool outputs, try to preserve beginning and end
                if role == "tool":
                    half = max_length // 2
                    content = (
                        content[:half]
                        + f"\n...[{len(content) - max_length} chars truncated]...\n"
                        + content[-half:]
                    )
                else:
                    content = content[:max_length] + "...[truncated]"

            if role == "user":
                lines.append(f"User: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
            elif role == "tool":
                tool_name = msg.get("name", "tool")
                lines.append(f"Tool ({tool_name}): {content}")
            elif role == "system":
                # Skip system messages in summarization input
                continue

        return "\n\n".join(lines)

    def _truncate_to_fit(self, messages: List[dict], budget: int) -> List[dict]:
        """Truncate messages from the beginning to fit budget."""
        total_tokens = 0
        result = []

        for msg in reversed(messages):
            msg_tokens = self._count_tokens(msg)
            if total_tokens + msg_tokens > budget:
                break
            result.insert(0, msg)
            total_tokens += msg_tokens

        return result

    def _count_tokens(self, message: dict) -> int:
        """Count tokens in a message."""
        content = message.get("content", "")

        if isinstance(content, str):
            if self.encoder:
                return len(self.encoder.encode(content))
            else:
                return int(len(content.split()) * 1.3)

        return 0

    def get_total_tokens(self, messages: List[dict]) -> int:
        """Get total token count for messages."""
        return sum(self._count_tokens(msg) for msg in messages)

    def fits_in_context(self, messages: List[dict]) -> bool:
        """Check if messages fit in context window."""
        return self.get_total_tokens(messages) <= self.token_budget

    def clear_summary_cache(self):
        """Clear the cached summary (call when conversation is cleared)."""
        self._cached_summary = None
        self._summarized_count = 0

    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            "max_tokens": self.max_tokens,
            "token_budget": self.token_budget,
            "summarize_threshold": int(self.token_budget * self.summarize_threshold),
            "recent_to_keep": self.recent_to_keep,
            "has_summary": self._cached_summary is not None,
            "summarized_message_count": self._summarized_count,
        }
