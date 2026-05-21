from pprint import pprint
from typing import Any, cast

from agently import Agently
from agently.core import ExecutionEnvironmentManager
from agently.types.data import ExecutionEnvironmentHandle, ExecutionEnvironmentRequirement
from agently.utils import Settings


class FlakySessionProvider:
    name = "FlakySessionProvider"
    DEFAULT_SETTINGS: dict[str, Any] = {}
    kind = "flaky_session"

    def __init__(self):
        self.ensure_count = 0
        self.release_count = 0

    async def async_ensure(self, *, requirement, policy, existing_handle=None):
        _ = (requirement, policy, existing_handle)
        self.ensure_count += 1
        return cast(ExecutionEnvironmentHandle, {
            "handle_id": f"flaky:{ self.ensure_count }",
            "resource": {"generation": self.ensure_count},
            "status": "ready",
            "meta": {"provider": self.name},
        })

    async def async_health_check(self, handle):
        if handle.get("resource", {}).get("generation") == 1:
            return "unhealthy"
        return "ready"

    async def async_release(self, handle):
        _ = handle
        self.release_count += 1


async def main_async():
    settings = Settings(name="HealthCheckExampleSettings", parent=Agently.settings)
    manager = ExecutionEnvironmentManager(
        plugin_manager=Agently.plugin_manager,
        settings=settings,
        event_center=Agently.event_center,
    )
    provider = FlakySessionProvider()
    manager.register_provider(cast(Any, provider))

    requirement = cast(ExecutionEnvironmentRequirement, {
        "kind": provider.kind,
        "scope": "session",
        "owner_id": "health-check-example",
        "resource_key": "demo",
    })

    first = await manager.async_ensure(requirement)
    second = await manager.async_ensure(requirement)

    print("[FIRST_HANDLE]")
    pprint(first)
    print("[SECOND_HANDLE_AFTER_HEALTH_CHECK]")
    pprint(second)
    print("[PROVIDER_COUNTS]")
    pprint({"ensure_count": provider.ensure_count, "release_count": provider.release_count})

    assert first.get("handle_id") == "flaky:1"
    assert second.get("handle_id") == "flaky:2"
    assert provider.ensure_count == 2
    assert provider.release_count == 1

    await manager.async_release(second)


def main():
    import asyncio

    asyncio.run(main_async())


if __name__ == "__main__":
    main()

# Expected key output:
# [FIRST_HANDLE] has handle_id "flaky:1".
# [SECOND_HANDLE_AFTER_HEALTH_CHECK] has handle_id "flaky:2" because the first reusable handle is unhealthy.
# [PROVIDER_COUNTS] prints {"ensure_count": 2, "release_count": 1}.

# How it works:
# A custom FlakyProvider simulates a reusable handle that becomes unhealthy after first use.
# The first ensure() creates handle "flaky:1" with reuse_strategy="reuse_if_healthy".
# The second ensure() calls the health_check(), which returns False → the handle is discarded
# and a new one "flaky:2" is created.  The release_count stays at 1 because "flaky:1" was
# released when the health check failed, not after second use.
#
# Flow:
# ensure("health_check_demo") -> creates "flaky:1"  (ensure_count=1)
#   |
#   v
# ensure("health_check_demo") -> health_check("flaky:1") returns False
#   -> releases "flaky:1", creates "flaky:2"  (ensure_count=2, release_count=1)
#   |
#   v
# list(scope="execution") -> []  (both released after second ensure)
# provider_counts -> {"ensure_count": 2, "release_count": 1}
