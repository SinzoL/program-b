from typing import Dict, Callable, List
import requests
import json


def get_registry_decorator(registry: Dict) -> Callable:

    def register(name: str):

        def decorator(cls: Callable):

            assert (
                not name in registry
            ), f"No duplicate registry names. '{name}' was registerd more than once."

            registry[name] = cls

            return cls

        return decorator

    return register


def query_p2l_endpoint(
    prompt: list[str], base_url: str, api_key: str
) -> Dict[str, List]:

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    payload = {"prompt": prompt}

    try:
        response = requests.post(
            f"{base_url}/predict", headers=headers, data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        return result

    except Exception as err:

        raise err


def get_p2l_endpoint_models(base_url: str, api_key: str) -> List[str]:

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    try:
        response = requests.get(f"{base_url}/models", headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["models"]

    except Exception as err:
        print(f"An error occurred: {err}")
