from dataclasses import dataclass
import os
import json
from typing import Any, Dict, Optional, Callable
from casefy import snakecase


class Parsers:
    @staticmethod
    def integer(v: str, k: str) -> int:
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"Invalid {k} value: {v}")

    @staticmethod
    def float(v: str, k: str) -> float:
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"Invalid {k} value: {v}")

    @staticmethod
    def boolean(v: str, k: str) -> bool:
        return v.lower() == "true"

    @staticmethod
    def string(v: str, k: str) -> str:
        return v


@dataclass
class MergeEnvOptions:
    prefix: str = ""
    separator: str = "__"


@dataclass
class ConfOptions:
    config: Dict[str, Any]
    merge_env_options: Optional[MergeEnvOptions] = None


def _merge_env(obj: Dict[str, Any], options: MergeEnvOptions) -> None:
    prefix = options.prefix
    separator = options.separator

    for key in list(obj.keys()):
        value = obj[key]
        if isinstance(value, dict):
            # If it's a dictionary, recursively process it
            _merge_env(
                value,
                MergeEnvOptions(
                    prefix=f"{prefix.upper()}{separator}{key}" if prefix else key,
                    separator=separator,
                ),
            )
        elif isinstance(value, list):
            # If it's a list, process each item
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    _merge_env(
                        item,
                        MergeEnvOptions(
                            prefix=f"{prefix.upper()}{separator}{key}{separator}{index}"
                            if prefix
                            else f"{key}{separator}{index}",
                            separator=separator,
                        ),
                    )
                else:
                    env_key = (
                        f"{prefix.upper()}{separator}{snakecase(key).upper()}{separator}{index}"
                        if prefix
                        else f"{snakecase(key).upper()}{separator}{index}"
                    )
                    if env_key in os.environ:
                        basic_type = type(item).__name__
                        if basic_type == "int":
                            basic_type = "integer"
                        elif basic_type == "float":
                            basic_type = "float"
                        elif basic_type == "bool":
                            basic_type = "boolean"
                        elif basic_type == "str":
                            basic_type = "string"

                        parser: Callable[[str, str], Any] = getattr(
                            Parsers, basic_type, Parsers.string
                        )
                        value[index] = parser(os.environ[env_key], env_key)
        else:
            env_key = (
                f"{prefix.upper()}{separator}{snakecase(key).upper()}"
                if prefix
                else snakecase(key).upper()
            )
            if env_key in os.environ:
                basic_type = type(value).__name__
                if basic_type == "int":
                    basic_type = "integer"
                elif basic_type == "float":
                    basic_type = "float"
                elif basic_type == "bool":
                    basic_type = "boolean"
                elif basic_type == "str":
                    basic_type = "string"

                parser: Callable[[str, str], Any] = getattr(
                    Parsers, basic_type, Parsers.string
                )
                obj[key] = parser(os.environ[env_key], env_key)


class Conf:
    def __init__(self, options: ConfOptions):
        self._conf = options.config.copy()
        if options.merge_env_options:
            _merge_env(self._conf, options.merge_env_options)

    def get(self, key: str):
        keys = key.split(".")
        val = self._conf
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            elif isinstance(val, list):
                try:
                    index = int(k)
                    val = val[index]
                except ValueError:
                    # raise ValueError(f"Invalid index: {k}")
                    val = None
            else:
                val = None

        # Return a copy to prevent modification
        if isinstance(val, dict):
            return val.copy()
        elif isinstance(val, list):
            return val.copy()
        else:
            return val

    def has(self, key: str):
        keys = key.split(".")
        val = self._conf
        for k in keys:
            if isinstance(val, dict):
                if k not in val:
                    return False
                val = val.get(k)
            elif isinstance(val, list):
                try:
                    index = int(k)
                    if index >= len(val) or index < 0:
                        return False
                    val = val[index]
                except ValueError:
                    return False
            else:
                return False

        return True

    def display(self) -> None:
        print(json.dumps(self._conf, indent=2))
