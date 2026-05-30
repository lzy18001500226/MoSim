import asyncio

from agently import TriggerFlow

flow = TriggerFlow(name="basic-flow")


async def say_hello(data):
    greeting = f"Hello, {data.input}"
    await data.async_set_state("greeting", greeting)
    return data.input


async def say_bye(data):
    farewell = f"Bye, {data.input}"
    await data.async_set_state("farewell", farewell)
    return data.input


flow.to(say_hello).to(say_bye)


async def main():
    execution = flow.create_execution()
    await execution.async_start("Agently")
    state = await execution.async_close()
    assert state["greeting"] == "Hello, Agently"
    assert state["farewell"] == "Bye, Agently"
    print(state)


asyncio.run(main())

# Stable expected key output from the declared run:
# state["greeting"] == "Hello, Agently" and state["farewell"] == "Bye, Agently".
#
# How it works:
# The simplest two-chunk linear chain.  say_hello and say_bye both receive "Agently"
# because each returns data.input unchanged.  async_set_state writes to the shared
# execution state dict; async_close() returns the final snapshot.
#
# Flow:
# async_start("Agently")
#   |
#   v
# say_hello  ->  state["greeting"] = "Hello, Agently"  (returns "Agently")
#   |
#   v
# say_bye    ->  state["farewell"] = "Bye, Agently"
#   |
# async_close()  ->  {"greeting": "Hello, Agently", "farewell": "Bye, Agently"}
