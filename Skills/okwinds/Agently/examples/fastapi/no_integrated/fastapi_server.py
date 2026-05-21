import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

from fastapi import FastAPI
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": os.environ["QIANFAN_BASE_URL"],
        "model": "ernie-lite-8k",
        "model_type": "chat",
        "auth": os.environ["QIANFAN_API_KEY"],
    },
)

agent = Agently.create_agent()
agent.role("You are a helpful assistant", always=True)

app = FastAPI()


@app.get("/chat")
async def chat(user_input: str):
    return await agent.input(user_input).async_start()

# Stable expected key output from the declared run:
# GET /chat?user_input=Hello returns HTTP 200 with a model-generated text body when Qianfan settings are configured.
#
# How it works:
# - The FastAPI route calls agent.input(user_input).async_start() directly.
# - Provider credentials come from QIANFAN_BASE_URL and QIANFAN_API_KEY.
# - This is a manual FastAPI integration reference, separate from FastAPIHelper examples.
#
# ASCII flow:
# HTTP GET /chat
#   |
#   v
# FastAPI route function
#   |
#   v
# Agently Agent async_start()
#   |
#   v
# model text response
