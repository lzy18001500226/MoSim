import asyncio

from agently import Agently
from agently.builtins.tools import Search, Browse

agent = Agently.create_agent()

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Actions in Agently
def builtin_actions():
    # Built-in Search / Browse actions.
    # Search supports proxy for network access.
    ## Notice: always update ddgs package to latest version first to ensure the quality of search results
    search = Search(
        proxy="http://127.0.0.1:55758",
        region="us-en",
        backend="google",
    )
    browse = Browse()
    agent.use_actions([search.search, search.search_news, browse.browse])
    result = agent.input("What is Agently AI Framework in Github?").start()
    print(result)


# builtin_actions()


## Action Functions with Decorator
def action_func_decorator():
    # Register a Python function as an action with @agent.action_func.
    @agent.action_func
    def add(a: int, b: int) -> int:
        return a + b

    agent.use_actions(add)
    result = agent.input("Calculate 345 + 678 using the available action.").start()
    print(result)


# action_func_decorator()


## Advanced: Trace Action Calls from Result (extra)
def action_call_trace():
    # Action calls happen inside the agent request, so the model can decide when to call actions.
    # Action call records are stored in response.result.full_result_data["extra"]["action_logs"].
    search = Search(
        proxy="http://127.0.0.1:55758",
        region="us-en",
        backend="google",
    )
    agent.use_actions([search.search, search.search_news])
    response = agent.input("Search for Agently AI Framework and summarize key points.").get_response()
    result = response.result.get_data()
    extra = response.result.full_result_data.get("extra", {})
    action_logs = extra.get("action_logs", extra.get("tool_logs", [])) if isinstance(extra, dict) else []
    print(result)
    print("[action_logs]", action_logs)


# action_call_trace()


## Multi-Stage Actions: Search -> Decide -> Browse -> Summarize
def multi_stage_search_browse_summarize():
    # Stage 1: allow Search actions only, let the model pick candidate URLs.
    search = Search(
        proxy="http://127.0.0.1:55758",
        region="us-en",
        backend="google",
    )
    agent.use_actions([search.search, search.search_news])
    response = (
        agent.input("Search for Agently AI Framework and list 3 best URLs to read (only URLs).")
        .output({"urls": [(str, "URL")]})
        .get_response()
    )
    stage1 = response.result.get_data()
    urls = stage1.get("urls", []) if isinstance(stage1, dict) else []
    urls = [u for u in urls if isinstance(u, str)]
    urls = urls[:3]
    print("[stage1 urls]", urls)

    # Stage 2: browse the selected URLs concurrently.
    browse = Browse()

    async def browse_all():
        tasks = [browse.browse(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [{"url": url, "content": content} for url, content in zip(urls, results)]

    pages = asyncio.run(browse_all())

    # Stage 3: summarize based on the browsed content with a clean agent that has no actions attached.
    summary_agent = Agently.create_agent()
    response = (
        summary_agent.input({"task": "Summarize key points from the sources.", "sources": pages})
        .output(
            {
                "summary": (str, "Short summary of the sources"),
                "sources": [
                    {
                        "url": (str, "Source URL"),
                        "notes": (str, "Key notes from this page"),
                    }
                ],
            }
        )
        .get_response()
    )
    stage3 = response.result.get_data()
    print("[stage3 summary]", stage3)


# multi_stage_search_browse_summarize()
