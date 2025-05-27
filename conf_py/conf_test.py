import pytest
from .conf import Conf, ConfOptions, MergeEnvOptions


class TestConf:
    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):
        """在每个测试前后设置和清理环境变量"""
        self.monkeypatch = monkeypatch
        # 测试结束后清理所有我们设置的环境变量
        yield
        # 不需要手动清理，monkeypatch会自动处理

    def test_env_variables_with_double_underscore_separator(self):
        """测试使用双下划线分隔符的环境变量"""
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
        """测试使用双冒号分隔符的环境变量"""
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
        """测试没有提供环境变量选项时返回初始值"""
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
        """测试对于不存在的键返回None"""
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
