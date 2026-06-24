class TestTraceAnalyzer:
    def _crear_trazas_fake(self):
        return [
            {
                "trace_id": "t1",
                "nombre": "test",
                "duracion_total_ms": 100,
                "estado": "EXITOSO",
                "spans": [
                    {"span_id": "s1", "nombre": "op_a", "duracion_ms": 50, "estado": "EXITOSO"},
                    {"span_id": "s2", "nombre": "op_b", "duracion_ms": 30, "estado": "EXITOSO"},
                    {"span_id": "s3", "nombre": "op_c", "duracion_ms": 20, "estado": "EXITOSO"},
                ],
            },
            {
                "trace_id": "t2",
                "nombre": "test",
                "duracion_total_ms": 200,
                "estado": "EXITOSO",
                "spans": [
                    {"span_id": "s4", "nombre": "op_a", "duracion_ms": 150, "estado": "EXITOSO"},
                    {"span_id": "s5", "nombre": "op_b", "duracion_ms": 30, "estado": "ERROR", "error": "timeout"},
                    {"span_id": "s6", "nombre": "op_c", "duracion_ms": 20, "estado": "EXITOSO"},
                ],
            },
            {
                "trace_id": "t3",
                "nombre": "test",
                "duracion_total_ms": 80,
                "estado": "EXITOSO",
                "spans": [
                    {"span_id": "s7", "nombre": "op_a", "duracion_ms": 40, "estado": "EXITOSO"},
                    {"span_id": "s8", "nombre": "op_b", "duracion_ms": 25, "estado": "EXITOSO"},
                    {"span_id": "s9", "nombre": "op_c", "duracion_ms": 15, "estado": "EXITOSO"},
                ],
            },
        ]

    def test_resumen(self):
        from src.observability.trace_analyzer import AnalizadorLogs

        analizador = AnalizadorLogs(self._crear_trazas_fake())
        resumen = analizador.resumen()

        assert resumen["total_trazas"] == 3
        assert resumen["total_spans"] == 9
        assert resumen["tasa_error_pct"] > 0
        assert "op_a" in resumen["duracion_promedio_por_etapa"]
        assert len(resumen["top_5_lentos"]) == 5

    def test_top_n_lentos(self):
        from src.observability.trace_analyzer import AnalizadorLogs

        analizador = AnalizadorLogs(self._crear_trazas_fake())
        top = analizador.top_n_lentos(3)

        assert len(top) == 3
        assert top[0]["duracion_ms"] >= top[1]["duracion_ms"]

    def test_duracion_promedio_por_etapa(self):
        from src.observability.trace_analyzer import AnalizadorLogs

        analizador = AnalizadorLogs(self._crear_trazas_fake())
        etapas = analizador.duracion_promedio_por_etapa()

        assert "op_a" in etapas
        assert etapas["op_a"]["promedio_ms"] == 80.0  # (50 + 150 + 40) / 3
        assert etapas["op_a"]["min_ms"] == 40
        assert etapas["op_a"]["max_ms"] == 150
        assert etapas["op_a"]["cantidad"] == 3

    def test_detectar_anomalias(self):
        from src.observability.trace_analyzer import AnalizadorLogs

        analizador = AnalizadorLogs(self._crear_trazas_fake())
        anomalias = analizador.detectar_anomalias(z_umbral=0.5)

        assert len(anomalias) > 0
        for a in anomalias:
            assert "z_score" in a
            assert abs(a["z_score"]) > 0.5

    def test_detectar_patrones_problematicos(self):
        from src.observability.trace_analyzer import AnalizadorLogs

        analizador = AnalizadorLogs(self._crear_trazas_fake())
        patrones = analizador.detectar_patrones_problematicos()

        assert "errores_recurrentes" in patrones
        assert "op_b: timeout" in patrones["errores_recurrentes"] or any(
            "timeout" in k for k in patrones["errores_recurrentes"]
        )
        assert patrones["cuello_botella"] == "op_a"

    def test_reporte_textual(self):
        from src.observability.trace_analyzer import AnalizadorLogs

        analizador = AnalizadorLogs(self._crear_trazas_fake())
        reporte = analizador.reporte_textual()

        assert "REPORTE DE ANÁLISIS DE TRAZAS" in reporte
        assert "total de trazas: 3" in reporte.lower()
        assert "op_a" in reporte
