from fastapi import FastAPI
from pydantic import BaseModel
from flow import run_flow

app = FastAPI()


class TestData(BaseModel):
    int_number: int


@app.post("/test")
async def test(data: TestData):
    return await run_flow(data.int_number)


if __name__ == "__main__":
    import uvicorn

    print("Start serving on port 15365...")
    uvicorn.run(app, host="0.0.0.0", port=15365)

# Stable expected key output from the declared run:
# POST /test with {"int_number": 3} returns {"group_1": 3, "group_2": 15, "initial_number": 3}.
#
# How it works:
# - The file starts a service/demo wrapper around an Agently provider.
# - Requests are converted into Agent or TriggerFlow calls and streamed or returned through the service route.
# - Stable behavior is the route/UI startup and the response shape, not exact model prose.
#
# ASCII flow:
# HTTP POST /test
#   |
#   v
# run_flow(int_number)
#   |
#   v
# TriggerFlow batch multipliers
#   |
#   v
# JSON response from execution state
