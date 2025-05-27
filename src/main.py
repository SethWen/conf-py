from dataclasses import dataclass
import os
import json
from typing import Any, Dict, Optional, TypeVar, Callable

T = TypeVar("T")


def snakify(key: str) -> str:
    """Convert camelCase or PascalCase to snake_case"""
    return "".join(["_" + c.lower() if c.isupper() else c for c in key]).lstrip("_")


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
class XConfOptions:
    config: Dict[str, Any]
    merge_env_options: Optional[MergeEnvOptions] = None


def merge_env(obj: Dict[str, Any], options: MergeEnvOptions) -> None:
    prefix = options.prefix
    separator = options.separator

    for key in list(obj.keys()):
        value = obj[key]
        if isinstance(value, dict):
            # If it's a dictionary, recursively process it
            merge_env(
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
                    merge_env(
                            item,
                            MergeEnvOptions(
                                prefix=f"{prefix.upper()}{separator}{key}{separator}{index}"
                                if prefix
                                else f"{key}{separator}{index}",
                                separator=separator,
                    ))
                else:
                    env_key = (
                    f"{prefix.upper()}{separator}{snakify(key).upper()}{separator}{index}"
                    if prefix
                    else f"{snakify(key).upper()}{separator}{index}"
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
                    value[index] = parser(os.environ[env_key], env_key)
                    pass    
        else:
            env_key = (
                f"{prefix.upper()}{separator}{snakify(key).upper()}"
                if prefix
                else snakify(key).upper()
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
    def __init__(self, options: XConfOptions):
        self._conf = options.config.copy()
        if options.merge_env_options:
            merge_env(self._conf, options.merge_env_options)

    def get(self, key: str) -> T:
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

    def display(self) -> None:
        print(json.dumps(self._conf, indent=2))


# Example usage:
if __name__ == "__main__":
    # Set some environment variables for testing
    os.environ["APP__DATABASE__HOST"] = "localhost"
    os.environ["APP__DATABASE__PORT"] = "5432"
    os.environ["APP__FEATURES__ENABLED"] = "true"
    os.environ["APP__NUMBERS__0"] = "8"

    config = {
        "database": {
            "host": "default_host",
            "port": 1234,
            "credentials": {"username": "user", "password": "pass"},
        },
        "features": {"enabled": False},
        "numbers": [1, 2, 3],
    }

    options = XConfOptions(
        config=config, merge_env_options=MergeEnvOptions(prefix="app", separator="__")
    )

    conf = Conf(options)
    # conf.display()
    print(conf.get("database.host"))  # Should print "localhost"
    print(conf.get("database.port"))  # Should print 5432
    print(conf.get("features.enabled"))  # Should print True
    print(conf.get("numbers.0"))  # Should print 1
    print(conf.get("numbers.1"))  # Should print 2
    print(conf.get("not_found"))  # Should print 2
    print(conf.get("not.exists"))
