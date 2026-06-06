from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import numpy as np

if TYPE_CHECKING:
    from manager import MCPServer

    from ..runtime import Runtime
    from ..tools import Tool

from ..knowledge import (
    EmbeddingCache,
    batch_cosine_similarity,
    get_embeddings,
)

_DEFAULT_TOP_K = 20
_TOOL_LIMIT = 128


class ToolIndex:
    """
    Vector index over a tool catalogue using LiteLLM embeddings.
    Embeddings are computed once at build time and cached.
    """

    def __init__(
        self,
        tools: List["Tool"],
        embedding_model: str = "text-embedding-3-small",
        cache: Optional[EmbeddingCache] = None,
    ):
        self.tools = tools
        self.embedding_model = embedding_model
        self.cache = cache or EmbeddingCache(max_size=len(tools) + 256)
        self._matrix: Optional[np.ndarray] = None  # shape (N, D)

    # ------------------------------------------------------------------
    @staticmethod
    def _tool_text(tool: "Tool") -> str:
        return f"{tool.name} {tool.description}"

    # ------------------------------------------------------------------
    def build(self) -> None:
        """Embed every tool, using the cache to skip already-computed ones."""
        texts = [self._tool_text(t) for t in self.tools]

        # Separate cached from uncached
        cached_map: dict[str, np.ndarray] = {}
        uncached_texts: List[str] = []

        for text in texts:
            hit = self.cache.get(text)
            if hit is not None:
                cached_map[text] = hit
            else:
                uncached_texts.append(text)

        # Batch-embed only what's missing
        if uncached_texts:
            new_embeddings = get_embeddings(uncached_texts, model=self.embedding_model)
            for text, emb in zip(uncached_texts, new_embeddings, strict=False):
                self.cache.set(text, emb)
                cached_map[text] = emb

        # Assemble matrix in original tool order
        self._matrix = np.stack([cached_map[t] for t in texts], axis=0)

    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = _DEFAULT_TOP_K) -> List["Tool"]:
        """Return the top_k tools most relevant to *query*."""
        if self._matrix is None:
            self.build()

        assert self._matrix is not None, "ToolIndex.build() failed to populate _matrix"

        # Embed query (check cache first)
        q_emb = self.cache.get(query)
        if q_emb is None:
            q_emb = get_embeddings([query], model=self.embedding_model)[0]
            self.cache.set(query, q_emb)

        scores = batch_cosine_similarity(q_emb, self._matrix)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.tools[i] for i in top_indices]


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------


def create_mcp_rag_optimizer(
    all_tools: List["Tool"],
    server: "MCPServer",
    embedding_model: str = "text-embedding-3-small",
    top_k: int = _DEFAULT_TOP_K,
) -> "Tool":
    """
    Return a single 'rag_optimizer' Tool that searches the full tool
    catalogue via embedding similarity and stages the top-K matches
    in the runtime for the next LLM turn.

    Args:
        all_tools:        Full catalogue of MCP tools (may exceed 128).
        embedding_model:  LiteLLM-compatible embedding model name.
        top_k:            Default number of tools to retrieve.

    Returns:
        One Tool the orchestrator should send when len(tools) > 128.
    """
    from ..tools import Tool, ToolSchema

    index = ToolIndex(tools=all_tools, embedding_model=embedding_model)
    index.build()  # eager — avoids latency on first LLM call

    tool_name = f"mcp_{server.name}_rag_optimizer"

    server_context = (
        f" This server provides: {server.config.description}."
        if getattr(server.config, "description", None)
        else ""
    )

    tool_description = (
        f"Search all available tools from the '{server.name}' MCP server "
        f"using a list of focused, single-purpose natural-language queries. "
        f"{server_context}"
        f"Pass one query per capability you need — results are merged and deduplicated. "
        f"Call this when you don't know which tool to use. "
        f"The best matching tools will be injected into your next turn so you can call them directly."
    )

    # Mutable state shared between execute_rag_optimizer and metadata
    state: dict = {"retrieved_top_k_tools": []}

    # ------------------------------------------------------------------
    async def execute_rag_optimizer(arguments: dict, runtime: "Runtime") -> str:
        raw_queries = arguments.get("queries", [])
        requested_k: int = int(arguments.get("top_k", top_k))

        queries = [q.strip() for q in raw_queries if isinstance(q, str) and q.strip()]
        if not queries:
            return "Error: 'queries' must be a non-empty list of strings."

        requested_k = max(1, min(requested_k, _TOOL_LIMIT))

        # Search per query, then deduplicate preserving best-rank-first order
        seen: set[str] = set()
        merged: list = []
        for q in queries:
            for tool in index.search(q, top_k=requested_k):
                if tool.name not in seen:
                    seen.add(tool.name)
                    merged.append((q, tool))

        state["retrieved_top_k_tools"] = [t for _, t in merged]

        lines = [
            f"Found {len(merged)} unique tools across {len(queries)} queries. "
            "They will be available alongside this tool in your next turn.\n"
        ]
        current_q = None
        for q, t in merged:
            if q != current_q:
                lines.append(f"\n[Query: '{q}']")
                current_q = q
            lines.append(f"  • {t.name} — {t.description[:120]}")

        return "\n".join(lines)

    schema = ToolSchema(
        type="object",
        properties={
            "queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "List of focused, single-purpose queries — one per capability you need. "
                    "Each query should describe exactly one tool's job. "
                    "GOOD: ['list open ports on a host', 'get process memory usage'] "
                    "BAD:  ['list ports and memory and CPU and disk']. "
                    "More focused queries = higher retrieval accuracy."
                ),
            },
            "top_k": {
                "type": "integer",
                "description": (
                    f"How many tools to retrieve per query (1–{_TOOL_LIMIT}). "
                    f"Defaults to {top_k}. Total results may be up to queries × top_k (deduplicated)."
                ),
            },
        },
        required=["queries"],
    )

    return Tool(
        name=tool_name,
        description=tool_description,
        schema=schema,
        execute_fn=execute_rag_optimizer,
        category="meta",
        metadata={
            "total_tools_indexed": all_tools,
            "embedding_model": embedding_model,
            "default_top_k": top_k,
            "is_rag_optimizer": True,
            "top_k_tools": state,
        },
    )
