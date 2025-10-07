import argparse
from p2l.model import get_p2l_model, P2LOutputs
from transformers import pipeline, TextClassificationPipeline, AutoTokenizer
from huggingface_hub import hf_hub_download
from datasets import load_dataset
import torch
from typing import Dict
import pandas as pd
import os
import json
from tqdm.auto import tqdm
from torch.utils.data import Dataset
from glob import glob


class P2LPipeline(TextClassificationPipeline):
    def preprocess(self, inputs, **tokenizer_kwargs) -> Dict[str, torch.Tensor]:
        return_tensors = self.framework

        messages = [{"role": "user", "content": inputs}]

        formatted = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
            add_special_tokens=False,
        )

        formatted = formatted + self.tokenizer.cls_token

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
        gamma = model_outputs.gamma


        return dict(
            coefs=model_outputs.coefs.cpu().float().numpy(),
            eta=eta.cpu().float().numpy() if eta else None,
            gamma=gamma.cpu().float().numpy() if gamma else None,
            last_hidden_state=model_outputs.last_hidden_state.cpu().float().numpy(),
        )


class ListDataset(Dataset):
    def __init__(self, original_list):
        self.original_list = original_list

    def __len__(self):
        return len(self.original_list)

    def __getitem__(self, i):
        return self.original_list[i]


def main(args, local_file=None):

    os.makedirs(args.output_dir, exist_ok=True)

    dataset = load_dataset(args.dataset, split=args.dataset_split)
    
    if local_file:
        fname = os.path.join(local_file, "model_list.json")
    else:
        fname = hf_hub_download(
            repo_id=args.model_path, filename="model_list.json", repo_type="model"
        )

    with open(fname) as fin:
        model_list = json.load(fin)

    model_cls = get_p2l_model(args.model_type, args.loss_type, args.head_type)

    if local_file:
        tokenizer = AutoTokenizer.from_pretrained(local_file, local_files_only=True)
        model = model_cls.from_pretrained(
            local_file,
            CLS_id=tokenizer.cls_token_id,
            num_models=len(model_list),
            dtype=torch.bfloat16,
            local_files_only=True,
        )
    else:
        tokenizer = AutoTokenizer.from_pretrained(args.model_path)
        model = model_cls.from_pretrained(
            args.model_path,
            CLS_id=tokenizer.cls_token_id,
            num_models=len(model_list),
            torch_dtype=torch.bfloat16,
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"

    pipe = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
        device=device,
        pipeline_class=P2LPipeline,
    )

    prompts = ListDataset(dataset["prompt"])

    with torch.no_grad():
        outputs = [
            out
            for out in tqdm(
                pipe(prompts, batch_size=args.batch_size), total=len(prompts)
            )
        ]

    df = dataset.to_pandas()

    outputs_df = pd.DataFrame.from_records(outputs)

    if args.drop_hidden:

        outputs_df = outputs_df.drop("last_hidden_state", axis=1)

    df = pd.concat((df, outputs_df), axis=1)

    if local_file:
        fname = local_file.split("/")[-1] + ".json"
    else:
        fname = args.model_path.split("/")[-1] + ".json"
    fpath = os.path.join(args.output_dir, fname)
    df.to_json(fpath, orient="records", indent=4, force_ascii=False)

    if args.output_hf_path:
        from datasets import Dataset

        df = pd.read_json(fpath)
        hf_dataset = Dataset.from_pandas(df)
        hf_dataset.push_to_hub(args.output_hf_path, private=True)
        print("Results pushed to hub!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-path", "-m", type=str, default=None, help="Huggingface model path"
    )
    parser.add_argument(
        "--training-output-dir", "-t", type=str, default=None
    )
    parser.add_argument(
        "--dataset", "-d", type=str, required=True, help="Huggingface dataset path"
    )
    parser.add_argument("--output-hf-path", "-oh", type=str, default=None)
    parser.add_argument(
        "--dataset-split",
        "-ds",
        type=str,
        default="train",
        help="Huggingface dataset split",
    )
    parser.add_argument(
        "--model-type",
        "-mt",
        type=str,
        default="qwen2",
        help="Model type (qwen2, llama, etc)",
    )
    parser.add_argument(
        "--head-type",
        "-ht",
        type=str,
        default="bt",
        help="Head type (Bradely Terry, Rao-Kupper, etc)",
    )
    parser.add_argument(
        "--loss-type",
        "-lt",
        type=str,
        default="bt",
        help="Loss type (Bradely Terry, Rao-Kupper, etc)",
    )
    parser.add_argument("--batch-size", "-bs", type=int, default=1, help="Batch size")
    parser.add_argument("--output-dir", "-od", type=str, default="outputs")
    parser.add_argument("--drop-hidden", action=argparse.BooleanOptionalAction, default=False)

    args = parser.parse_args()

    if args.training_output_dir:
        for file in glob(os.path.join(args.training_output_dir, "*")):
            main(args, file)
    else:
        main(args)
