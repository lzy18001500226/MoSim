import httpx

response = httpx.post(
    "http://127.0.0.1:15365/test",
    json={
        "int_number": 1234,
    },
    timeout=300,
)
if response.status_code == 200:
    print(response.json())

# Stable expected key output from the declared run:
# local run closes the execution and prints the asserted state snapshot or runtime stream values.
#
# How it works:
# - The file builds a TriggerFlow from plain Python chunk handlers.
# - main() creates an execution, starts it with demo input, then closes it with async_close() so the close snapshot is the checked result.
# - State is stored with async_set_state(...) and read from the close snapshot or execution.result.
#
# ASCII flow:
# start/input
#   |
#   v
# TriggerFlow chunks / branches
#   |
#   v
# async_close() -> close snapshot / runtime stream assertions
