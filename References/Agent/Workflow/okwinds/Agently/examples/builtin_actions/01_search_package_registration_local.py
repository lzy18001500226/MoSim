import os
from pprint import pprint
from typing import Literal, cast

from agently import Agently
from agently.builtins.actions import Search

SearchBackend = Literal["auto", "bing", "duckduckgo", "yahoo", "google", "mullvad_google", "yandex", "wikipedia"]
SearchRegion = Literal[
    "xa-ar", "xa-en", "ar-es", "au-en", "at-de", "be-fr", "be-nl", "br-pt", "bg-bg", "ca-en", "ca-fr",
    "ct-ca", "cl-es", "cn-zh", "co-es", "hr-hr", "cz-cs", "dk-da", "ee-et", "fi-fi", "fr-fr", "de-de",
    "gr-el", "hk-tzh", "hu-hu", "in-en", "id-id", "id-en", "ie-en", "il-he", "it-it", "jp-jp", "kr-kr",
    "lv-lv", "lt-lt", "xl-es", "my-ms", "my-en", "mx-es", "nl-nl", "nz-en", "no-no", "pe-es", "ph-en",
    "ph-tl", "pl-pl", "pt-pt", "ro-ro", "ru-ru", "sg-en", "sk-sk", "sl-sl", "za-en", "es-es", "se-sv",
    "ch-de", "ch-fr", "ch-it", "tw-tzh", "th-th", "tr-tr", "ua-uk", "uk-en", "us-en", "ue-es", "ve-es",
    "vn-vi",
]


def build_agent():
    agent = Agently.create_agent()
    search = Search(
        proxy=os.getenv("SEARCH_PROXY") or None,
        timeout=10,
        backend=cast(SearchBackend, os.getenv("SEARCH_BACKEND", "duckduckgo")),
        region=cast(SearchRegion, os.getenv("SEARCH_REGION", "us-en")),
    )
    agent.use_actions(search)
    return agent


def main():
    agent = build_agent()
    agent_tag = f"agent-{ agent.name }"
    specs = agent.action.get_action_list(tags=[agent_tag])
    print("[REGISTERED_SEARCH_ACTIONS]")
    pprint(
        [
            {
                "action_id": spec.get("action_id"),
                "executor_type": spec.get("executor_type"),
                "component": spec.get("meta", {}).get("component"),
            }
            for spec in specs
            if str(spec.get("action_id", "")).startswith("search")
        ]
    )

    assert {"search", "search_news", "search_wikipedia", "search_arxiv"}.issubset(
        {str(spec.get("action_id")) for spec in specs}
    )

    if os.getenv("RUN_REAL_SEARCH") != "1":
        print("[SKIP_REAL_SEARCH] Set RUN_REAL_SEARCH=1 to call the configured search backend.")
        return

    result = agent.action.execute_action(
        "search",
        {
            "query": os.getenv("SEARCH_QUERY", "Agently Action Runtime"),
            "max_results": 3,
        },
    )
    print("[ACTION_RESULT]")
    pprint(result)


if __name__ == "__main__":
    main()

# Expected key output:
# [REGISTERED_SEARCH_ACTIONS] lists search, search_news, search_wikipedia, and search_arxiv.
# By default the script prints [SKIP_REAL_SEARCH] and does not call the network.
# With RUN_REAL_SEARCH=1, [ACTION_RESULT] contains a real search ActionResult.

# How it works:
# SearchPack from agently.builtins.actions registers a family of search action IDs:
# "search" (general web), "search_news", "search_wikipedia", "search_arxiv".
# agent.use_actions(search_pack) mounts them in the agent's action registry.
# The script inspects the registered specs to verify registration without any network
# call.  Set RUN_REAL_SEARCH=1 to trigger a real search via execute_action().
