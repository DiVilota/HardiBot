import pytest


class TestDashboardMetrics:
    def test_metrica_sin_api_key(self, monkeypatch):
        from src.observability import get_dashboard_metrics
        monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
        monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

        resultado = get_dashboard_metrics()
        assert resultado is None or resultado.get("status") == "no_api_key"

    def test_estimar_ahorro_con_metricas_ok(self):
        from src.observability import estimar_ahorro_tokens
        metricas = {
            "status": "ok",
            "total_tokens": 5000,
            "prompt_tokens": 3000,
            "completion_tokens": 2000,
        }
        ahorro = estimar_ahorro_tokens(metricas)
        assert ahorro is not None
        assert ahorro["ahorro_estimado_tokens"] > 0
        assert ahorro["total_tokens_ejecutados"] == 5000

    def test_estimar_ahorro_sin_metricas(self):
        from src.observability import estimar_ahorro_tokens
        assert estimar_ahorro_tokens({"status": "error"}) is None
        assert estimar_ahorro_tokens({"status": "empty"}) is None

    def test_format_run_invalido(self):
        from src.observability import _format_run
        class RunMock:
            pass
        r = RunMock()
        r.start_time = None
        r.end_time = None
        r.id = "test123"
        r.name = "test_run"
        r.total_tokens = 100
        r.prompt_tokens = 50
        r.completion_tokens = 50
        r.error = None

        formateado = _format_run(r)
        assert formateado["run_id"] == "test123"
        assert formateado["name"] == "test_run"
        assert formateado["latency"] is None
