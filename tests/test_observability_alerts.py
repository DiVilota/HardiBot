class TestSistemaAlertas:
    def test_alerta_se_dispara(self):
        from src.observability.alerts import SistemaAlertas, ReglaAlerta
        from src.observability.metrics import RecolectorMetricas
        sistema = SistemaAlertas()
        sistema.agregar_regla(ReglaAlerta(
            nombre="latencia_alta",
            descripcion="Latencia superior a 5000ms",
            umbral=5000,
            tipo="latencia_ms",
        ))
        recolector = RecolectorMetricas()
        recolector.registrar_exito("gpt-4o", 6000, 100, 100, "t1")
        alertas = sistema.evaluar(recolector)
        assert len(alertas) >= 1

    def test_alerta_no_se_dispara_dentro_de_umbral(self):
        from src.observability.alerts import SistemaAlertas, ReglaAlerta
        from src.observability.metrics import RecolectorMetricas
        sistema = SistemaAlertas()
        sistema.agregar_regla(ReglaAlerta(
            nombre="latencia_alta",
            descripcion="Latencia superior a 5000ms",
            umbral=5000,
            tipo="latencia_ms",
        ))
        recolector = RecolectorMetricas()
        recolector.registrar_exito("gpt-4o", 100, 100, 100, "t1")
        alertas = sistema.evaluar(recolector)
        assert len(alertas) == 0

    def test_severidad_critical(self):
        from src.observability.alerts import SistemaAlertas, ReglaAlerta
        from src.observability.metrics import RecolectorMetricas
        sistema = SistemaAlertas()
        sistema.agregar_regla(ReglaAlerta(
            nombre="latencia_alta",
            descripcion="Latencia superior a 5000ms",
            umbral=5000,
            tipo="latencia_ms",
        ))
        recolector = RecolectorMetricas()
        recolector.registrar_exito("gpt-4o", 10000, 100, 100, "t1")
        alertas = sistema.evaluar(recolector)
        assert any(a.severidad == "CRITICAL" for a in alertas)

    def test_multiples_reglas(self):
        from src.observability.alerts import SistemaAlertas, ReglaAlerta
        from src.observability.metrics import RecolectorMetricas
        sistema = SistemaAlertas()
        sistema.agregar_regla(ReglaAlerta("r1", "latencia", 100, "latencia_ms"))
        sistema.agregar_regla(ReglaAlerta("r2", "tokens", 1000, "tokens_totales"))
        recolector = RecolectorMetricas()
        recolector.registrar_exito("gpt-4o", 200, 600, 600, "t1")
        alertas = sistema.evaluar(recolector)
        assert len(alertas) == 2

    def test_sin_metricas_no_alerta(self):
        from src.observability.alerts import SistemaAlertas, ReglaAlerta
        from src.observability.metrics import RecolectorMetricas
        sistema = SistemaAlertas()
        sistema.agregar_regla(ReglaAlerta("r1", "latencia", 100, "latencia_ms"))
        recolector = RecolectorMetricas()
        alertas = sistema.evaluar(recolector)
        assert len(alertas) == 0
