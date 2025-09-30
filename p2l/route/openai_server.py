import argparse
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from route.datatypes import (
    ModelConfigContainer,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChunk,
)
from route.chat import CHAT_HANDLERS
from route.routers import ROUTERS, BaseRouter
import uvicorn
import yaml
from contextlib import asynccontextmanager
from typing import List
import logging
import time
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--config", "-c", type=str, required=True)
    parser.add_argument("--router-type", type=str, required=True)
    parser.add_argument("--router-model-name", type=str, default=None)
    parser.add_argument("--router-model-endpoint", type=str, default=None)
    parser.add_argument("--router-api-key", type=str, default="-")
    parser.add_argument("--cost-optimizer", type=str, default="simple-lp")
    parser.add_argument("--port", "-p", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--api-key", type=str, default="-")
    parser.add_argument("--reload", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--workers", type=int, default=1)

    args = parser.parse_args()

    return args


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This context manager is called once at startup and once at shutdown.
    We move all config-loading and router-creation logic here.
    """
    # --- PARSE ARGS & LOAD CONFIG ---

    logging.info(f"Starting up...")

    args = parse_args()

    with open(args.config) as cfile:
        config = yaml.safe_load(cfile)

    model_config_dicts = config["model_configs"]
    model_config_container = ModelConfigContainer(model_config_dicts)

    router_cls = ROUTERS[args.router_type]

    router_kwargs = {
        "router_model_name": args.router_model_name,
        "router_model_endpoint": args.router_model_endpoint,
        "router_api_key": args.router_api_key,
    }

    router = router_cls(model_config_container, args.cost_optimizer, **router_kwargs)

    app.state.router = router
    app.state.model_config_container = model_config_container
    app.state.api_key = args.api_key

    logging.info(f"Finished startup.")

    try:

        yield

    finally:

        pass


app = FastAPI(lifespan=lifespan)

# ====== API Endpoint ======


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    authorization: str = Header(None),
) -> ChatCompletionResponse | ChatCompletionResponseChunk:
    """
    Mimics the OpenAI Chat Completions endpoint (both streaming and non-streaming).
    """

    logging.info(f"{int(time.time())} Recieved Request: {request}")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # Strip out the 'Bearer ' portion to isolate the token
    token = authorization.removeprefix("Bearer ")

    if token != app.state.api_key:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:

        router_output = None
        type = None

        direct_model = request.direct_model

        router: BaseRouter = app.state.router

        messages = request.messages

        if direct_model:

            router_output = router.get_model_direct(direct_model)

        else:

            router_output = router.route(messages, request.cost)

        logging.info(f"{int(time.time())} Router Output: {router_output}")

        type = router_output.chosen_model_config.get_type()

        chat_handler = CHAT_HANDLERS[type]

    except Exception as e:

        logging.info(
            f"{int(time.time())} ***Routing Error Start***\nError Message: {e}\nRouter Output: {router_output}\nChat Handler: {type}\nDirect Model: {direct_model}.***Routing Error End***"
        )

        raise HTTPException(status_code=500, detail=str(e))

    try:

        if request.stream:

            chat_output_chunk = chat_handler.generate_stream(
                messages=messages,
                router_output=router_output,
                temp=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
            )

            return StreamingResponse(chat_output_chunk, media_type="text/event-stream")

        else:

            chat_output = chat_handler.generate(
                messages=messages,
                router_output=router_output,
                temp=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
            )

            return chat_output

    except Exception as e:

        logging.info(
            f"{int(time.time())} ***Endpoint Error Start***\nError Message: {e}\nRouter Output: {router_output}\nChat Handler: {type}.***Endpoint Error End***"
        )

        raise e


@app.get("/v1/models")
async def models(authorization: str = Header(None)) -> List[str]:

    logging.info(f"Recieved Get Request for Models.")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # Strip out the 'Bearer ' portion to isolate the token
    token = authorization.removeprefix("Bearer ")

    if token != app.state.api_key:
        raise HTTPException(status_code=403, detail="Unauthorized")

    router: BaseRouter = app.state.router

    return router.model_list


if __name__ == "__main__":

    args = parse_args()

    uvicorn.run(
        "route.openai_server:app",
        port=args.port,
        host=args.host,
        reload=args.reload,
        workers=args.workers,
    )
