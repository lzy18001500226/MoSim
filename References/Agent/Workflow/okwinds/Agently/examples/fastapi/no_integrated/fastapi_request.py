import asyncio
import httpx
import time


async def request(index: int, user_input: str):
    start_time = time.time()
    print(
        f"No.{ index } Start:",
        start_time,
    )
    client = httpx.AsyncClient()
    response = await client.get(
        "http://127.0.0.1:8000/chat",
        params={"user_input": user_input},
        timeout=None,
    )
    print(f"No.{ index } Response:", response.content.decode())
    end_time = time.time()
    print(
        f"No.{ index } End:",
        end_time,
    )


async def main():
    tasks = []
    for i in range(5):
        await asyncio.sleep(0.5)
        tasks.append(
            asyncio.create_task(
                request(
                    i + 1,
                    "What is “奇变偶不变，符号看象限”?",
                )
            )
        )
    await asyncio.gather(*tasks)


asyncio.run(main())

# Stable expected key output from the declared run:
# with fastapi_server.py running, five concurrent requests print No.1..No.5 Start/Response/End lines and each response contains model text.
#
# How it works:
# - The client schedules five httpx requests half a second apart.
# - Each request calls the manual /chat route exposed by fastapi_server.py.
# - Stable output is the concurrent request/response ordering, not exact model wording.
#
# ASCII flow:
# asyncio tasks
#   |
#   v
# httpx GET /chat
#   |
#   v
# manual FastAPI server
#   |
#   v
# printed responses
