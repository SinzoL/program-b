from abc import ABC, abstractmethod
from route.utils import get_registry_decorator
from typing import List, Dict
import numpy as np
import cvxpy as cp
from scipy.special import expit


class UnfulfillableException(Exception):
    pass


class BaseCostOptimizer(ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def select_model(
        cost: float,
        model_list: List[str],
        model_costs: np.ndarray[float],
        model_scores: np.ndarray[float],
        **kwargs,
    ) -> str:
        pass

    @staticmethod
    def select_max_score_model(
        model_list: List[str], model_scores: np.ndarray[float]
    ) -> str:

        max_idx = np.argmax(model_scores)

        return model_list[max_idx]


COST_OPTIMIZERS: Dict[str, BaseCostOptimizer] = {}

register = get_registry_decorator(COST_OPTIMIZERS)


@register("strict")
class StrictCostOptimizer(BaseCostOptimizer):

    def __init__(self):
        super().__init__()

    @staticmethod
    def select_model(
        cost: float | None,
        model_list: List[str],
        model_costs: np.ndarray[float],
        model_scores: np.ndarray[float],
        **kwargs,
    ) -> str:

        if cost == None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        best_model: str | None = None
        best_score = -float("inf")

        for model, model_cost, model_score in zip(
            model_list, model_costs, model_scores
        ):

            if model_cost > cost:
                continue

            elif model_score > best_score:
                best_model = model
                best_score = model_score

        if best_model is None:
            raise UnfulfillableException(
                f"Cost of {cost} impossible to fulfill with available models {model_list} with costs {model_costs}."
            )

        return best_model


@register("simple-lp")
class SimpleLPCostOptimizer(BaseCostOptimizer):

    def __init__(self):
        super().__init__()

    @staticmethod
    def select_model(
        cost: float | None,
        model_list: List[str],
        model_costs: np.ndarray[float],
        model_scores: np.ndarray[float],
        **kwargs,
    ) -> str:

        if cost == None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        p = cp.Variable(len(model_costs))

        prob = cp.Problem(
            cp.Maximize(cp.sum(model_scores @ p)),
            [model_costs.T @ p <= cost, cp.sum(p) == 1, p >= 0],
        )

        status = prob.solve()

        if status < 0.0:
            raise UnfulfillableException(
                f"Cost of {cost} impossible to fulfill with available models {model_list} with costs {model_costs}."
            )

        ps = np.clip(p.value, a_min=0.0, a_max=1.0)
        ps = ps / ps.sum()

        return np.random.choice(model_list, p=ps)


@register("optimal-lp")
class OptimalLPCostOptimizer(BaseCostOptimizer):

    def __init__(self):
        super().__init__()

    @staticmethod
    def select_model(
        cost: float | None,
        model_list: List[str],
        model_costs: np.ndarray[float],
        model_scores: np.ndarray[float],
        opponent_scores: np.ndarray[float] = None,
        opponent_distribution: np.ndarray[float] = None,
    ) -> str:

        if cost == None:
            return StrictCostOptimizer.select_max_score_model(model_list, model_scores)

        W = OptimalLPCostOptimizer._construct_W(model_scores, opponent_scores)

        Wq = W @ opponent_distribution

        p = cp.Variable(len(model_costs))

        prob = cp.Problem(
            cp.Maximize(p @ Wq), [model_costs.T @ p <= cost, cp.sum(p) == 1, p >= 0]
        )

        status = prob.solve()

        if status < 0.0:
            raise UnfulfillableException(
                f"Cost of {cost} impossible to fulfill with available models {model_list} with costs {model_costs}."
            )

        ps = np.clip(p.value, a_min=0.0, a_max=1.0)
        ps = ps / ps.sum()

        return np.random.choice(model_list, p=ps)

    @staticmethod
    def _construct_W(
        router_model_scores: np.ndarray[float], opponent_model_scores: np.ndarray[float]
    ) -> np.ndarray[float]:

        num_rows = router_model_scores.shape[-1]
        num_cols = opponent_model_scores.shape[-1]

        chosen = np.tile(router_model_scores, (num_cols, 1)).T
        rejected = np.tile(opponent_model_scores, (num_rows, 1))

        assert chosen.shape == rejected.shape, (chosen.shape, rejected.shape)

        diff_matrix = chosen - rejected

        W = expit(diff_matrix)

        return W
