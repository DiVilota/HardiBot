import pytest


class TestMetricaLlamada:
    def test_registro_exitoso(self):
        from src.observability.metrics import RecolectorMetricas
        recolector = RecolectorMetricas()
        metrica = recolector.registrar_exito(
            modelo="gpt-4o",
            tiempo_respuesta_ms=150.5,
            tokens_prompt=100,
            tokens_completion=50,
            trace_id="trace-001",
        )
        assert metrica.exitosa is True
        assert metrica.modelo == "gpt-4o"
        assert metrica.tiempo_respuesta_ms == 150.5
        assert metrica.tokens_prompt == 100
        assert metrica.tokens_completion == 50
        assert metrica.tokens_total == 150
        assert metrica.costo_estimado_usd > 0
        assert metrica.trace_id == "trace-001"

    def test_registro_fallido(self):
        from src.observability.metrics import RecolectorMetricas
        recolector = RecolectorMetricas()
        metrica = recolector.registrar_error(
            modelo="gpt-4o",
            tiempo_respuesta_ms=200.0,
            tokens_prompt=50,
            tokens_completion=0,
            tipo_error="timeout",
            mensaje_error="La solicitud tardó demasiado",
            trace_id="trace-002",
        )
        assert metrica.exitosa is False
        assert metrica.tipo_error == "timeout"
        assert metrica.mensaje_error == "La solicitud tardó demasiado"
        assert metrica.costo_estimado_usd >= 0

    def test_resumen_con_datos(self):
        from src.observability.metrics import RecolectorMetricas
        recolector = RecolectorMetricas()
        recolector.registrar_exito("gpt-4o", 100, 50, 50, "t1")
        recolector.registrar_exito("gpt-4o", 200, 100, 100, "t2")
        recolector.registrar_exito("gpt-4o", 300, 150, 150, "t3")
        resumen = recolector.resumen()
        assert resumen["total_llamadas"] == 3
        assert resumen["avg_latencia_ms"] == 200.0
        assert resumen["max_latencia_ms"] == 300.0
        assert resumen["tasa_error_pct"] == 0.0
        assert resumen["tokens_totales"] == 600

    def test_resumen_vacio(self):
        from src.observability.metrics import RecolectorMetricas
        recolector = RecolectorMetricas()
        resumen = recolector.resumen()
        assert resumen["total_llamadas"] == 0

    def test_calculo_costos(self):
        from src.observability.metrics import RecolectorMetricas, PRECIOS
        recolector = RecolectorMetricas()
        metrica = recolector.registrar_exito("gpt-4o", 100, 1_000_000, 100_000, "t1")
        precio_prompt = PRECIOS["gpt-4o"]["prompt"] / 1_000_000 * 1_000_000
        precio_completion = PRECIOS["gpt-4o"]["completion"] / 1_000_000 * 100_000
        esperado = round(precio_prompt + precio_completion, 6)
        assert metrica.costo_estimado_usd == esperado

    def test_p95_correcto(self, tmp_path):
        from src.observability.metrics import RecolectorMetricas
        import os
        recolector = RecolectorMetricas()
        for i in range(1, 101):
            recolector.registrar_exito("gpt-4o", float(i), 10, 10, f"t{i}")
        resumen = recolector.resumen()
        import pytest
        assert resumen["p95_latencia_ms"] == pytest.approx(95.0, abs=0.1)

    def test_a_dataframe(self):
        import pandas as pd
        from src.observability.metrics import RecolectorMetricas
        recolector = RecolectorMetricas()
        recolector.registrar_exito("gpt-4o", 100, 50, 50, "t1")
        recolector.registrar_exito("gpt-4", 200, 100, 100, "t2")
        df = recolector.a_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == [
            "timestamp", "modelo", "tiempo_respuesta_ms",
            "tokens_prompt", "tokens_completion", "tokens_total",
            "costo_estimado_usd", "exitosa", "tipo_error",
            "mensaje_error", "trace_id",
        ]
