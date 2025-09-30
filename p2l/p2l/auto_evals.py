import argparse
import json
import os
import io
import warnings
import math
from tqdm import tqdm
import time
import copy

import torch
import pandas as pd
import numpy as np
from datasets import load_dataset, load_from_disk
from huggingface_hub import hf_hub_download, upload_file, list_repo_files

from model import HeadOutputs
from auto_eval_utils import (
    registered_simple_metrics,
    registered_aggr_metrics,
    registered_helpers,
)


def parse_model_list(hf_model, local_path):
    if not hf_model and not local_path:
        raise ValueError("Either model repo or local model list must be provided.")

    model_list_path = local_path
    # if no local path, try getting from model_repo
    if not model_list_path:
        model_list_path = hf_hub_download(
            repo_id=hf_model, filename="model_list.json", repo_type="model"
        )

    model_list = pd.read_json(model_list_path, lines=False).iloc[:, 0].tolist()
    return np.array(model_list)


def change_beta_model_list(df, old_list, new_list):
    old_list = old_list.tolist()
    old_to_new = [old_list.index(model) for model in new_list]
    betas_array = np.array(df["betas"].to_list())

    betas_array = betas_array[:, old_to_new]
    return betas_array.tolist()


def parse_eval_output_data(
    model_repo,
    local_eval_path,
    local_checkpoint_path,
    hf_checkpoint_repo,
    hf_checkpoint_file,
    loss_type,
    model_list,
    remove_last_hidden_json,
):
    ret_df, ret_model_list = None, None
    if local_checkpoint_path or hf_checkpoint_repo:
        path = local_checkpoint_path
        if not path:
            if not hf_checkpoint_file:
                raise ValueError(
                    "Must provide checkpoint file along with checkpoint repo"
                )
            path = hf_hub_download(
                repo_id=hf_checkpoint_repo,
                filename=hf_checkpoint_file,
                repo_type="dataset",
            )

        df = pd.read_json(path)

        # caching json w/o last hidden layer
        if remove_last_hidden_json and local_checkpoint_path:
            if "last_hidden_state" in df.columns:
                df = df.drop(columns=["last_hidden_state"])
                df.to_json(local_checkpoint_path)

        df = df.rename(columns={"coefs": "betas"})

        # data is stored with nested lists for both etas and betas only in checkpoint data
        # df['eta'] = np.array(df['eta'].to_list()).flatten()
        df["eta"] = df["eta"].apply(lambda x: x[0] if isinstance(x, list) else x)
        df["betas"] = df["betas"].apply(lambda x: x[0] if isinstance(x, list) else x)

        val_model_list = get_model_list_from_df(df)
        # only betas need to be adjusted since labels are correct
        df["betas"] = change_beta_model_list(df, model_list, val_model_list)

        ret_df, ret_model_list = df, val_model_list

    elif local_eval_path:
        ret_df, ret_model_list = pd.read_json(local_eval_path, lines=True), model_list

    elif model_repo:
        files = list_repo_files(repo_id=model_repo, repo_type="model")
        if "eval_output.jsonl" not in files:
            raise FileNotFoundError(
                f"'eval_output.jsonl' not found in the hf repository'{model_repo}'."
            )
        path = hf_hub_download(
            repo_id=model_repo, filename="eval_output.jsonl", repo_type="model"
        )
        ret_df, ret_model_list = pd.read_json(path, lines=True), model_list
    else:
        raise ValueError("need to provide path for eval output data")

    preprocess_func = registered_helpers[loss_type]["preprocess_data"]
    ret_df = preprocess_func(data=ret_df)

    return ret_df, ret_model_list


def add_labels_to_data(data, loss_type, model_list):
    if loss_type == "bt":
        data = data[~data["winner"].isin(["tie", "tie (bothbad)"])]

    def create_labels(row):
        winner = row["winner"]
        model_a = row["model_a"]
        model_b = row["model_b"]

        model_a_idx = np.where(model_list == model_a)[0][0]
        model_b_idx = np.where(model_list == model_b)[0][0]

        tie_bb_label = 2 if loss_type == "bag" else 1
        if winner == "model_a":
            return np.array([model_a_idx, model_b_idx, 0])
        elif winner == "model_b":
            return np.array([model_b_idx, model_a_idx, 0])
        elif winner == "tie":
            return np.array([model_a_idx, model_b_idx, 1])
        else:
            return np.array([model_a_idx, model_b_idx, tie_bb_label])

    data["labels"] = data.apply(create_labels, axis=1)
    return data


# only use if completely necessary
def get_model_list_from_df(df):
    return np.array(sorted(pd.concat([df["model_a"], df["model_b"]]).unique()))


def parse_train_data(hf_data, local_path, loss_type, train_model_list):
    if not hf_data and not local_path:
        warnings.warn(
            "No train data provided, marginal model type will not work if specified"
        )
        return

    if local_path:
        if local_path.endswith(".jsonl"):
            data = pd.read_json(local_path, lines=True)

        else:
            data = load_from_disk(local_path)["train"].to_pandas()
    else:
        data = load_dataset(hf_data, split="train").to_pandas()

    return add_labels_to_data(data, loss_type, train_model_list)


def parse_arena_data(path, initial_rating=1000, BASE=10, SCALE=400):
    if not path:
        warnings.warn("Ground truth arena data not passed in, some metrics not work")
        return

    df = pd.read_csv(path)
    # removes to avoid duplicates since not every model has a style_controlled ranking
    df = df[df["style_control"] == False]
    # ELO to beta using what eval_p2l.ipynb used
    df["beta"] = (df["rating"] - initial_rating) / (SCALE * math.log(BASE))

    pivot = df.pivot(index="model_name", columns="category", values="beta").reindex(
        model_list
    )

    if pivot.isnull().any().any():
        missing_models = pivot[pivot.isnull().any(axis=1)].index.tolist()
        warnings.warn("Model not included in arena leaderboard:" + str(missing_models))

    category_to_betas = {
        category: torch.tensor(pivot[category].values, dtype=torch.float)
        for category in pivot.columns
    }
    return category_to_betas


# NOTE: Only accepts certain categories, needs to be manually added
def filter_battle_data(battles, category):
    if battles is None:
        return None
    # expect category key by itself or key=value
    key_val_pair = category.split("=")
    key = key_val_pair[0]
    val = key_val_pair[1] if len(key_val_pair) == 2 else True
    val = bool(val) if val in ["True", "true", "False", "false"] else val

    try:
        # no filtering
        if key == "all":
            return battles
        # no nesting
        if key == "language" or key == "is_code":
            return battles[battles[key] == val]
        # nested ones need specific cases
        if key == "math":
            return battles[
                battles["category_tag"].apply(lambda x: x["math_v0.1"]["math"])
            ]
        if key == "complexity":
            return battles[
                battles["category_tag"].apply(
                    lambda x: x["criteria_v0.1"]["complexity"]
                )
            ]
        if key == "creative_writing":
            return battles[
                battles["category_tag"].apply(
                    lambda x: x["creative_writing_v0.1"]["creative_writing"]
                )
            ]
        if key == "hard":
            return battles[
                battles["category_tag"].apply(
                    lambda x: sum(x["criteria_v0.1"].values()) >= 6
                )
            ]

        # Category not found
        return None
    except:
        return None


# NOTE: Only accepts certain categories, needs to be manually added
def get_arena_rankings(data, category):
    if data is None:
        return None

    key_val_pair = category.split("=")
    key = key_val_pair[0]
    val = key_val_pair[1] if len(key_val_pair) == 2 else True
    val = bool(val) if val in ["True", "true", "False", "false"] else val

    try:
        # no filtering
        if key == "all":
            return data["full"]
        # no nesting
        if key == "language":
            return data[val.lower()]
        if key == "is_code":
            return data["coding"]
        if key == "math":
            return data["math"]
        if key == "hard":
            return data["hard_6"]
        if key == "creative_writing":
            return data["creative_writing"]

        return None
    except:
        return None


def get_subset_prompts(output, labels, size):
    num_prompts = output.coefs.shape[0]
    sampled_indices = torch.randperm(num_prompts)[:size]
    sampled_coefs = output.coefs[sampled_indices, :]

    sampled_eta = None
    if output.eta is not None:
        sampled_eta = output.eta[sampled_indices]

    sampled_labels = labels[sampled_indices, :]
    sampled_output = HeadOutputs(coefs=sampled_coefs, eta=sampled_eta)
    return sampled_output, sampled_labels


def get_subset_prompts_batch(output, labels, size, batch_size):
    num_prompts, num_models = output.coefs.shape
    sampled_indices = torch.randint(low=0, high=num_prompts, size=(batch_size, size))
    sampled_coefs = output.coefs[sampled_indices]

    sampled_eta = None
    if output.eta is not None:
        sampled_eta = output.eta[sampled_indices]
    sampled_labels = labels[sampled_indices]

    sampled_output = HeadOutputs(coefs=sampled_coefs, eta=sampled_eta)

    return sampled_output, sampled_labels


def get_ith_output(output, i):
    betas = output.coefs[i]
    eta = output.eta[i] if output.eta is not None else None
    return HeadOutputs(coefs=betas, eta=eta)


def save_output(results, local_dir, hf_dir, file_name):
    if not local_dir and not hf_dir:
        raise ValueError("Specify a directory for outputs.")

    results["params"]["output_file_name"] = file_name

    file_name += ".json"
    if local_dir:
        path = os.path.join(local_dir, file_name)
        with open(path, "w") as file:
            json.dump(results, file, indent=4, separators=(",", ": "))
    if hf_dir:
        output = json.dumps(results, indent=4, separators=(",", ": "))
        tmp_file = io.BytesIO(output.encode("utf-8"))

        upload_file(
            path_or_fileobj=tmp_file,
            path_in_repo=file_name,
            repo_id=hf_dir,
            repo_type="model",
        )


def simple_metrics(metrics, output, labels, loss_type):
    results = {}

    for metric in tqdm(metrics, desc="Simple Metrics", unit="metrics"):
        metric_dict = registered_simple_metrics[loss_type]
        metric_func = metric_dict[metric]
        metric_val = metric_func(head_output=output, labels=labels, loss_type=loss_type)

        results[metric] = (
            round(metric_val, 4) if isinstance(metric_val, float) else metric_val
        )

    return results


def category_metrics(
    metrics,
    output,
    labels,
    loss_type,
    model_type,
    model_list,
    ground_truth,
    arena_rankings,
):
    results = {}

    aggr_func_model = registered_helpers[model_type]["aggregrate"]
    # our default ground truth is marginal-gt but we can switch to arena or add configurability if desired
    aggr_func_gt = registered_helpers[ground_truth]["aggregrate"]

    model_output = aggr_func_model(
        head_output=output, labels=labels, model_list=model_list, loss_type=loss_type
    )
    gt_output = aggr_func_gt(
        labels=labels,
        model_list=model_list,
        loss_type=loss_type,
        arena_rankings=arena_rankings,
    )

    for metric in tqdm(metrics, desc="Category Metrics", unit="metric"):
        metric_dict = registered_aggr_metrics[loss_type]
        metric_func = metric_dict[metric]
        metric_val = metric_func(
            gt_output=gt_output,
            model_output=model_output,
            model_list=model_list,
            loss_type=loss_type,
            labels=labels,
        )
        results[metric] = (
            round(metric_val, 4) if isinstance(metric_val, float) else metric_val
        )

    return results


def random_subset_metrics(
    metrics,
    output,
    labels,
    subset_sizes,
    trials_per_subset,
    loss_type,
    model_type,
    model_list,
):
    results = {}

    aggr_func_model = registered_helpers[model_type]["aggregrate"]
    # our default ground truth is marginal-gt but we can switch to arena or add configurability if desired
    aggr_func_gt = registered_helpers["marginal-gt"]["aggregrate"]

    for idx, size in enumerate(subset_sizes):
        size = int(size)
        subset_results = {metric: 0 for metric in metrics}

        for _ in tqdm(
            range(trials_per_subset[idx]),
            desc=f"Random Subset size {size}",
            unit="trial",
        ):
            sample_output, sample_labels = get_subset_prompts(output, labels, size)

            model_output = aggr_func_model(
                head_output=sample_output,
                labels=sample_labels,
                model_list=model_list,
                loss_type=loss_type,
            )
            gt_output = aggr_func_gt(
                labels=sample_labels, model_list=model_list, loss_type=loss_type
            )

            for metric in metrics:
                metric_dict = registered_aggr_metrics[loss_type]
                metric_func = metric_dict[metric]
                metric_val = metric_func(
                    gt_output=gt_output,
                    model_output=model_output,
                    model_list=model_list,
                    loss_type=loss_type,
                )

                subset_results[metric] += metric_val

        for metric in metrics:
            subset_results[metric] = round(
                subset_results[metric] / trials_per_subset, 4
            )

        results[size] = subset_results

    return results


def aggr_scale_metrics(
    metrics,
    output,
    labels,
    subset_sizes,
    trials_per_subset,
    loss_type,
    model_type,
    model_list,
    arena_rankings,
    gt,
):
    results = {}
    aggr_func_model = registered_helpers[model_type]["aggregrate-batch"]
    # our default ground truth is arena ranking but we can switch to arena or add configurability if desired

    aggr_func_gt = registered_helpers[gt]["aggregrate"]
    gt_output = aggr_func_gt(
        labels=labels,
        model_list=model_list,
        loss_type=loss_type,
        arena_rankings=arena_rankings,
    )

    # TODO: arbitray threshold to limit memory consumption for batching
    # max_prompts_times_samples_squared = 2e4

    for idx, size in enumerate(subset_sizes):
        size = int(size)
        num_samples = int(trials_per_subset[idx])

        subset_results = {metric: 0 for metric in metrics}

        # num_full_mini_batches = int(max(
        #     1, (size * (num_samples ** 2)) // max_prompts_times_samples_squared
        # ))

        num_full_mini_batches = int(max(1, num_samples // 100))

        mini_batch_size = num_samples // num_full_mini_batches
        leftover = num_samples - (num_full_mini_batches * mini_batch_size)

        with tqdm(total=num_samples, desc=f"Aggr Subset Size {size}") as pbar:

            def run_mini_batch(batch_count):
                sample_output, sample_labels = get_subset_prompts_batch(
                    output, labels, size, batch_count
                )
                batch_output = aggr_func_model(
                    head_output=sample_output,
                    labels=sample_labels,
                    model_list=model_list,
                    loss_type=loss_type,
                )

                for cur_output in batch_output:
                    for metric in metrics:
                        metric_dict = registered_aggr_metrics[loss_type]
                        metric_func = metric_dict[metric]
                        metric_val = metric_func(
                            gt_output=gt_output,
                            model_output=cur_output,
                            model_list=model_list,
                            loss_type=loss_type,
                        )
                        subset_results[metric] += metric_val
                    pbar.update(1)

            for _ in range(num_full_mini_batches):
                run_mini_batch(mini_batch_size)

            if leftover > 0:
                run_mini_batch(leftover)

        for metric in metrics:
            subset_results[metric] = round(
                subset_results[metric] / float(trials_per_subset[idx]), 4
            )

        results[size] = subset_results

    return results


def get_metrics(
    val_data, train_data, arena_rankings, val_model_list, train_model_list, args
):
    results = {}
    to_inc = set(args.metrics_to_inc)
    output_label_func = registered_helpers[args.model_type]["output_labels"]
    output, labels = output_label_func(
        val_data=val_data,
        train_data=train_data,
        arena_rankings=arena_rankings,
        loss_type=args.loss_type,
        model_list=val_model_list,
        train_model_list=train_model_list,
    )

    if "simple" in to_inc:
        simple_results = simple_metrics(
            metrics=args.simple_metrics,
            output=output,
            labels=labels,
            loss_type=args.loss_type,
        )
        results["simple_metrics"] = simple_results

    if "category" in to_inc:
        category_results = category_metrics(
            metrics=args.category_metrics,
            loss_type=args.loss_type,
            model_type=args.model_type,
            model_list=val_model_list,
            output=output,
            labels=labels,
            ground_truth=args.ground_truth,
            arena_rankings=arena_rankings,
        )
        results["category_metrics"] = category_results

    if "random_subsets" in to_inc:
        subset_results = random_subset_metrics(
            metrics=args.rand_subset_metrics,
            subset_sizes=args.rand_subset_sizes,
            trials_per_subset=args.rand_num_samples,
            loss_type=args.loss_type,
            model_type=args.model_type,
            model_list=val_model_list,
            output=output,
            labels=labels,
        )
        results["random_subsets"] = subset_results

    if "aggr_scale" in to_inc:
        scale_results = aggr_scale_metrics(
            metrics=args.aggr_scale_metrics,
            subset_sizes=args.aggr_scale_subset_sizes,
            trials_per_subset=args.aggr_scale_num_samples,
            loss_type=args.loss_type,
            model_type=args.model_type,
            model_list=val_model_list,
            output=output,
            labels=labels,
            arena_rankings=arena_rankings,
            gt=args.ground_truth,
        )
        results["aggr_scale"] = scale_results

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # model repo contains model list and potentially, eval data (eval_output.jsonl)
    parser.add_argument("--model_repo", type=str, default=None)
    parser.add_argument("--model_list_path", type=str, default=None)

    # val data is either in model repo, local file, or remotely as checkpoint file
    parser.add_argument("--eval_path", nargs="+", type=str, default=None)
    parser.add_argument("--checkpoint_path", nargs="+", type=str, default=None)
    parser.add_argument("--hf_checkpoint_repo", type=str, default=None)
    parser.add_argument("--hf_checkpoint_file", nargs="+", type=str, default=None)

    parser.add_argument("--output_dir", type=str, default=None)
    parser.add_argument("--hf_output_dir", type=str, default=None)
    parser.add_argument(
        "--output_file_name", type=str, nargs="+", default=["eval_metrics"]
    )

    parser.add_argument("--hf_train_dataset", type=str, default=None)
    parser.add_argument("--train_path", type=str, default=None)

    parser.add_argument("--arena_path", type=str, default=None)

    parser.add_argument("--loss_type", type=str, default="bt", help="bt, bt_tie, rk")
    parser.add_argument(
        "--model_type", type=str, default="p2l", help="p2l, marginal, arena"
    )

    parser.add_argument(
        "--categories",
        nargs="*",
        default=[
            "all",
            "creative_writing",
            "math",
            "language=Chinese",
            "is_code",
            "hard",
        ],
    )

    parser.add_argument(
        "--simple_metrics",
        nargs="*",
        default=[
            "Loss",
            "BCELoss",
            "MSELoss",
            "Accuracy",
            "Tie_Loss",
            "Tie_Accuracy",
            "Tie_bb_Accuracy",
            "Tie_bb_Loss",
            "Mean-BT",
            "Std-BT",
            "Spread-BT",
            "Mean-Spread-BT",
            "Mean-IQR-BT",
            "Mean-Std-BT",
        ],
    )

    parser.add_argument("--train_checkpoints", nargs="+", type=int, default=[])
    parser.add_argument("--checkpoint_size", type=int, default=0)

    # gt is marginal on val
    parser.add_argument(
        "--category_metrics",
        nargs="*",
        default=[
            "Leaderboard",
            "Aggr_Loss",
            "Aggr_BCELoss",
            "Aggr_Tie_Loss",
            "Aggr_Tie_Accuracy",
            "Aggr_Tie_bb_Accuracy",
            "Aggr_Tie_bb_Loss",
            "L1-Dist-Prob",
            "Spearman-lbs",
            "Kendall-lbs",
            "IQR-BT",
            "Std-BT",
            "Spread-BT",
            "Top-k-fraction",
            "Top-k-displace",
        ],
    )

    parser.add_argument(
        "--rand_subset_sizes", nargs="*", default=[250, 500, 1000, 2000]
    )

    parser.add_argument("--rand_num_samples", nargs="*", default=[50, 20, 5, 3])
    parser.add_argument(
        "--rand_subset_metrics",
        nargs="*",
        default=["L1-Dist-Prob", "Spearman-lbs", "Kendall-lbs"],
    )
    # gt is arena leaderboard
    parser.add_argument(
        "--aggr_scale_subset_sizes",
        nargs="*",
        default=[1, 10, 25, 100, 250, 500, 1000, 2000],
    )
    parser.add_argument(
        "--aggr_scale_num_samples",
        nargs="*",
        default=[500, 500, 500, 200, 100, 40, 10, 6],
    )

    parser.add_argument(
        "--aggr_scale_metrics",
        nargs="*",
        default=["L1-Dist-Prob", "Spearman-lbs", "Kendall-lbs"],
    )
    parser.add_argument("--ground_truth", type=str, default="marginal-gt")

    parser.add_argument(
        "--metrics_to_inc",
        nargs="*",
        default=["simple", "category", "random_subsets", "aggr_scale"],
    )

    parser.add_argument("--remove_last_hidden_json", default=True)

    args = parser.parse_args()
    start_time = time.time()
    for idx in range(len(args.output_file_name)):
        results = {}
        results["params"] = copy.deepcopy(vars(args))

        train_model_list = parse_model_list(args.model_repo, args.model_list_path)

        eval_path = args.eval_path[idx] if args.eval_path else None
        checkpoint_path = args.checkpoint_path[idx] if args.checkpoint_path else None
        hf_checkpoint_file = (
            args.hf_checkpoint_file[idx] if args.hf_checkpoint_file else None
        )

        # make sure right params are dumped
        results["params"]["eval_path"] = eval_path
        results["params"]["checkpoint_path"] = checkpoint_path
        results["params"]["hf_checkpoint_file"] = hf_checkpoint_file

        val_data, val_model_list = parse_eval_output_data(
            args.model_repo,
            eval_path,
            checkpoint_path,
            args.hf_checkpoint_repo,
            hf_checkpoint_file,
            args.loss_type,
            train_model_list,
            args.remove_last_hidden_json,
        )

        train_data = parse_train_data(
            args.hf_train_dataset, args.train_path, args.loss_type, train_model_list
        )
        arena_data = parse_arena_data(args.arena_path)

        models = {}
        for category in args.categories:

            cat_val_data = filter_battle_data(val_data, category)
            cat_train_data = filter_battle_data(train_data, category)

            arena_rankings = get_arena_rankings(arena_data, category)

            current_model = str(args.model_type) + "-" + category
            models[current_model] = get_metrics(
                cat_val_data,
                cat_train_data,
                arena_rankings,
                val_model_list,
                train_model_list,
                args,
            )

            # merely for marginal train checkpointing
            for checkpoint in args.train_checkpoints:
                num_data = checkpoint * args.checkpoint_size
                checkpoint_train_data = train_data.head(num_data)

                cat_train_data = filter_battle_data(checkpoint_train_data, category)
                models[current_model + f"-checkpoint-{checkpoint}"] = get_metrics(
                    cat_val_data,
                    cat_train_data,
                    arena_rankings,
                    val_model_list,
                    train_model_list,
                    args,
                )

        results["models"] = models
        save_output(
            results, args.output_dir, args.hf_output_dir, args.output_file_name[idx]
        )

    end_time = time.time()
    total_time = end_time - start_time

    minutes = int(total_time // 60)
    seconds = int(total_time % 60)

    print(f"\nTotal time taken: {minutes} minutes and {seconds} seconds")
