import argparse
import json
from typing import Dict, Tuple, List, Optional

import torch
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from huggingface_hub import hf_hub_download
from pydantic import BaseModel
from transformers import (
    AutoTokenizer,
    TextClassificationPipeline,
    pipeline,
    PreTrainedModel,
)

from p2l.model import get_p2l_model, P2LOutputs
from contextlib import asynccontextmanager
import logging

logging.getLogger().setLevel(logging.DEBUG)


def parse_args():

    parser = argparse.ArgumentParser(description="Run FastAPI with Uvicorn")

    parser.add_argument(
        "--model-path",
        "-m",
        type=str,
        default="p2el/Qwen2.5-7B-Instruct-rk-full-train",
        help="Path to the model repository",
    )
    parser.add_argument(
        "--model-type",
        "-mt",
        type=str,
        default="qwen2",
        help="Type of the model",
    )
    parser.add_argument(
        "--head-type",
        "-ht",
        type=str,
        default="rk",
        help="Type of model head",
    )
    parser.add_argument(
        "--loss-type",
        "-lt",
        type=str,
        default="rk",
        help="Type of the loss function",
    )
    parser.add_argument(
        "--api-key",
        "-a",
        type=str,
        default="-",
        help="API key for authorization",
    )
    parser.add_argument(
        "--host",
        "-H",
        type=str,
        default="0.0.0.0",
        help="Host to run the server on",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=10250,
        help="Port to run the server on",
    )

    parser.add_argument(
        "--reload",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to reload the endpoint on detected code change, needs workers to be 1.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of endpoint workers (will hold a model per worker).",
    )
    parser.add_argument(
        "--cuda",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Flag to enable using a GPU to host the model. Flag is true by default.",
    )

    args = parser.parse_args()

    return args


@asynccontextmanager
async def lifespan(app: FastAPI):

    args = parse_args()

    model, tokenizer, model_list = load_model(
        args.model_path,
        args.model_type,
        args.head_type,
        args.loss_type,
    )

    pipe = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
        device="cuda" if args.cuda else "cpu",
        pipeline_class=P2LPipeline,
    )

    app.state.api_key = args.api_key
    app.state.model_list = model_list
    app.state.model = model
    app.state.tokenizer = tokenizer
    app.state.pipe = pipe

    try:

        yield

    finally:

        pass


# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)


# Define the input data structure
class InputData(BaseModel):
    prompt: list[str]


class OutputData(BaseModel):
    coefs: List[float]
    eta: Optional[float] = None


class ModelList(BaseModel):
    models: List[str]


class P2LPipeline(TextClassificationPipeline):
    def preprocess(self, inputs, **tokenizer_kwargs) -> Dict[str, torch.Tensor]:
        return_tensors = self.framework

        inputs = inputs["prompt"]

        messages = [{"role": "user", "content": p} for p in inputs]

        formatted = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
            add_special_tokens=False,
        )
        formatted = formatted + self.tokenizer.cls_token

        logging.debug(f"Formatted input: {formatted}")

        return self.tokenizer(
            formatted,
            return_tensors=return_tensors,
            max_length=8192,
            padding="longest",
            truncation=True,
        )

    def postprocess(
        self, model_outputs: P2LOutputs, function_to_apply=None, top_k=1, _legacy=True
    ):
        model_outputs = P2LOutputs(model_outputs)

        eta = model_outputs.eta

        return OutputData(
            coefs=model_outputs.coefs.cpu().float().tolist()[0],
            eta=eta.cpu().float().item() if eta else None,
        )


@app.post("/predict")
async def predict(input_data: InputData, api_key: str = Header(...)):

    logging.debug(f"Received Request: {input_data}.")

    if api_key != app.state.api_key:

        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        pipe: P2LPipeline = app.state.pipe

        logging.debug(f"Input Prompt: {input_data.prompt}")

        output = pipe(inputs=input_data.model_dump())

        logging.debug(f"Output: {output}")

        return output

    except Exception as e:

        logging.debug(e)

        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def models(api_key: str = Header(...)):

    logging.debug(f"Received Model List Request.")

    if api_key != app.state.api_key:

        raise HTTPException(status_code=403, detail="Unauthorized")

    try:

        return ModelList(
            models=app.state.model_list,
        )

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


def load_model(
    model_name, model_type, head_type, loss_type
) -> Tuple[PreTrainedModel, AutoTokenizer, List[str]]:

    # Download and load the model list
    fname = hf_hub_download(
        repo_id=model_name, filename="model_list.json", repo_type="model"
    )
    with open(fname) as fin:
        model_list = json.load(fin)

    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.truncation_side = "left"
    tokenizer.padding_side = "right"

    # Get the model class and load the model
    model_cls = get_p2l_model(model_type, loss_type, head_type)

    model = model_cls.from_pretrained(
        model_name,
        CLS_id=tokenizer.cls_token_id,
        num_models=len(model_list),
        torch_dtype=torch.bfloat16,
    )
    return model, tokenizer, model_list


if __name__ == "__main__":

    args = parse_args()

    uvicorn.run(
        "p2l.endpoint:app",
        port=args.port,
        host=args.host,
        reload=args.reload,
        workers=args.workers,
    )
