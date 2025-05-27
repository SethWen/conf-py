import pytest
from .conf import Conf, ConfOptions, MergeEnvOptions


class TestConf:
    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):
        """set up test fixtures"""
        self.monkeypatch = monkeypatch
        yield

    def test_env_variables_with_double_underscore_separator(self):
        self.monkeypatch.setenv("MOCK__SERVER__PORT", "6666")
        self.monkeypatch.setenv("MOCK__SERVER__BASE_PATH", "/mockpath")
        self.monkeypatch.setenv("MOCK__LOGS__0__LEVEL", "custom")
        self.monkeypatch.setenv("MOCK__NUMS__0", "8")

        conf = Conf(
            ConfOptions(
                config={
                    "name": "mock",
                    "server": {
                        "port": 8080,
                        "base_path": "/api",
                    },
                    "logs": [
                        {
                            "level": "info",
                            "output": "console",
                        },
                    ],
                    "nums": [1, 2, 3],
                },
                merge_env_options=MergeEnvOptions(prefix="MOCK", separator="__"),
            )
        )

        assert conf.get("name") == "mock"
        assert conf.get("server.port") == 6666
        assert conf.get("server.base_path") == "/mockpath"
        assert conf.get("server") == {"port": 6666, "base_path": "/mockpath"}
        assert conf.get("logs.0.level") == "custom"
        assert conf.get("logs.0") == {"level": "custom", "output": "console"}
        assert conf.get("nums.0") == 8
        assert conf.get("nums.1") == 2

    def test_env_variables_with_double_colon_separator(self):
        self.monkeypatch.setenv("MOCK::SERVER::PORT", "6666")
        self.monkeypatch.setenv("MOCK::SERVER::BASE_PATH", "/mockpath")
        self.monkeypatch.setenv("MOCK::LOGS::0::LEVEL", "custom")
        self.monkeypatch.setenv("MOCK::NUMS::0", "8")

        conf = Conf(
            ConfOptions(
                config={
                    "name": "mock",
                    "server": {
                        "port": 8080,
                        "base_path": "/api",
                    },
                    "logs": [
                        {
                            "level": "info",
                            "output": "console",
                        },
                    ],
                    "nums": [1, 2, 3],
                },
                merge_env_options=MergeEnvOptions(prefix="MOCK", separator="::"),
            )
        )

        assert conf.get("name") == "mock"
        assert conf.get("server.port") == 6666
        assert conf.get("server.base_path") == "/mockpath"
        assert conf.get("server") == {"port": 6666, "base_path": "/mockpath"}
        assert conf.get("logs.0.level") == "custom"
        assert conf.get("logs.0") == {"level": "custom", "output": "console"}
        assert conf.get("nums.0") == 8
        assert conf.get("nums.1") == 2

    def test_initial_values_without_env_options(self):
        conf = Conf(
            ConfOptions(
                config={
                    "name": "original",
                    "server": {
                        "port": 8080,
                        "base_path": "/api",
                    },
                    "logs": [
                        {
                            "level": "info",
                            "output": "console",
                        },
                    ],
                    "nums": [1, 2, 3],
                }
            )
        )

        assert conf.get("name") == "original"
        assert conf.get("server.port") == 8080
        assert conf.get("server.base_path") == "/api"
        assert conf.get("server") == {"port": 8080, "base_path": "/api"}
        assert conf.get("logs.0.level") == "info"
        assert conf.get("logs.0") == {"level": "info", "output": "console"}

    def test_return_none_for_non_existent_key(self):
        conf = Conf(
            ConfOptions(
                config={
                    "name": "mock",
                    "server": {
                        "port": 8080,
                        "base_path": "/api",
                    },
                    "logs": [
                        {
                            "level": "info",
                            "output": "console",
                        },
                    ],
                    "nums": [1, 2, 3],
                }
            )
        )

        assert conf.get("notexist") is None
        assert conf.get("not.exist") is None


    def test_return_true_if_key_exists_or_not_if_not_exist(self):
        conf = Conf(
            ConfOptions(
                config={
                    "name": "mock",
                    "server": {
                        "port": 8080,
                        "base_path": "/api",
                    },
                    "logs": [
                        {
                            "level": "info",
                            "output": "console",
                        },
                    ],
                    "nums": [1, 2, 3],
                }
            )
        )
        assert conf.has("name") is True
        assert conf.has("server.port") is True
        assert conf.has("server.base_path") is True
        assert conf.has("server") is True
        assert conf.has("logs.0.level") is True
        assert conf.has("logs.0") is True
        assert conf.has("nums.0") is True
        assert conf.has("nums.1") is True
        assert conf.has("notexist") is False
        assert conf.has("not.exist") is False

