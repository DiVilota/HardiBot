from src.config import get_model_config, get_langsmith_config


class TestConfig:
    def test_model_config_defaults(self):
        config = get_model_config()
        assert config["model"] == "gpt-4o"
        assert 0 <= config["temperature"] <= 2
        assert config["max_tokens"] > 0

    def test_langsmith_config_structure(self):
        config = get_langsmith_config()
        assert "api_key" in config
        assert "project" in config
        assert "endpoint" in config
        assert "tracing" in config
