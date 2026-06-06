"""Shared agent component initialization logic.

Used by both the TUI and the MCP server so the startup sequence is defined
in exactly one place.  Callers supply an optional *on_progress* callback
that receives ``(level: str, message: str)`` notifications; if omitted the
messages are silently discarded.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Callable, Optional


async def build_agent_components(
    target: Optional[str] = None,
    scope: Optional[list[str]] = None,
    model: Optional[str] = None,
    docker: bool = False,
    no_rag: bool = False,
    no_mcp: bool = False,
    on_progress: Optional[Callable[[str, str], None]] = None,
    after_mcp_load: Optional[Callable[[], None]] = None,
    prebuilt_rag=None,
) -> dict[str, Any]:
    """Build every shared agent component in the standard order.

    Returns a dict with keys:
        ``agent``           – PentestAgentAgent instance
        ``runtime``         – DockerRuntime or LocalRuntime
        ``rag_engine``      – RAGEngine (or None)
        ``all_tools``       – list of all registered Tool objects
        ``mcp_manager``     – MCPManager (or None)
        ``rag_doc_count``   – int
        ``mcp_server_count``– int
        ``model``           – resolved model string
    """
    from ..agents.pa_agent import PentestAgentAgent
    from ..knowledge import RAGEngine
    from ..llm import LLM, ModelConfig
    from ..tools import get_all_tools, register_tool_instance

    scope = list(scope or [])

    def _log(msg: str, level: str = "info") -> None:
        if on_progress:
            on_progress(level, msg)

    # ------------------------------------------------------------------
    # 1. RAG Engine
    # ------------------------------------------------------------------
    rag_engine: Optional[RAGEngine] = None
    rag_doc_count = 0

    if prebuilt_rag is not None:
        rag_engine = prebuilt_rag
        rag_doc_count = rag_engine.get_document_count()
        _log(f"RAG engine ready — {rag_doc_count} documents indexed.")
    elif not no_rag:
        local_knowledge = Path("knowledge")
        bundled_path = Path(__file__).parent.parent / "knowledge" / "sources"
        knowledge_path: Optional[Path] = None

        if local_knowledge.exists() and any(local_knowledge.rglob("*.*")):
            knowledge_path = local_knowledge
        elif bundled_path.exists():
            knowledge_path = bundled_path

        if knowledge_path:
            try:
                embeddings_setting = os.getenv("PENTESTAGENT_EMBEDDINGS", "").lower()
                if embeddings_setting == "local":
                    use_local = True
                elif embeddings_setting == "openai":
                    use_local = False
                else:
                    use_local = not os.getenv("OPENAI_API_KEY")

                rag_engine = RAGEngine(
                    knowledge_path=knowledge_path,
                    use_local_embeddings=use_local,
                )
                await asyncio.to_thread(rag_engine.index)
                rag_doc_count = rag_engine.get_document_count()
                _log(f"RAG engine ready — {rag_doc_count} documents indexed.")
            except Exception as exc:
                _log(f"RAG engine failed, continuing without it: {exc}", "warning")
                rag_engine = None

    # ------------------------------------------------------------------
    # 2. Runtime
    # ------------------------------------------------------------------
    if docker:
        from ..runtime.docker_runtime import DockerRuntime

        runtime: Any = DockerRuntime()
        _log("Using DockerRuntime.")
    else:
        from ..runtime.runtime import LocalRuntime

        runtime = LocalRuntime()
        _log("Using LocalRuntime.")

    await runtime.start()

    # ------------------------------------------------------------------
    # 3. Model / LLM
    # ------------------------------------------------------------------
    if not model:
        model = os.getenv("PENTESTAGENT_MODEL")
    if not model:
        raise RuntimeError(
            "No model configured. Pass --model or set PENTESTAGENT_MODEL."
        )

    llm = LLM(
        model=model,
        config=ModelConfig(temperature=0.7),
        rag_engine=rag_engine,
    )
    _log(f"LLM initialised: {model}")

    # ------------------------------------------------------------------
    # 4. Tools
    # ------------------------------------------------------------------
    all_tools = get_all_tools()
    _log(f"Built-in tools loaded: {len(all_tools)}")

    # ------------------------------------------------------------------
    # 5. Primary PentestAgentAgent
    # ------------------------------------------------------------------
    agent = PentestAgentAgent(
        llm=llm,
        tools=all_tools,
        runtime=runtime,
        target=target,
        scope=scope,
        rag_engine=rag_engine,
    )
    _log(f"PentestAgentAgent ready — target={target} scope={scope}")

    # ------------------------------------------------------------------
    # 6. External MCP servers (background task)
    # ------------------------------------------------------------------
    mcp_manager = None
    mcp_server_count = 0

    if not no_mcp:
        try:
            from ..mcp import MCPManager

            mcp_manager = MCPManager()
            mcp_server_count = len(mcp_manager.list_configured_servers())

            async def _load_mcp() -> None:
                try:
                    tools = await mcp_manager.connect_all()
                    agent.add_tools(tools)
                    for tool in tools:
                        register_tool_instance(tool)
                    _log(f"External MCP tools loaded: {len(tools)}")
                    if after_mcp_load:
                        after_mcp_load()
                except Exception as exc:
                    _log(f"External MCP connect failed: {exc}", "warning")

            asyncio.get_event_loop().create_task(_load_mcp())
            _log(f"External MCP servers: {mcp_server_count} configured.")
        except Exception as exc:
            _log(f"MCPManager unavailable: {exc}", "warning")

    return {
        "agent": agent,
        "runtime": runtime,
        "rag_engine": rag_engine,
        "all_tools": all_tools,
        "mcp_manager": mcp_manager,
        "rag_doc_count": rag_doc_count,
        "mcp_server_count": mcp_server_count,
        "model": model,
    }
