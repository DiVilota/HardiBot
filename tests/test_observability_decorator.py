class TestObservableDecorator:
    def test_no_altera_retorno(self):
        from src.observability.decorator import observable
        llamados = []

        @observable
        def nodo_prueba(state):
            llamados.append(state)
            return {"resultado": "ok", "contador": state.get("contador", 0) + 1}

        state = {"contador": 0, "mensajes": []}
        resultado = nodo_prueba(state)
        assert resultado["resultado"] == "ok"
        assert resultado["contador"] == 1

    def test_genera_trace_id(self):
        from src.observability.decorator import observable

        @observable
        def nodo_prueba(state):
            return {"resultado": "ok"}

        state = {"mensajes": []}
        resultado = nodo_prueba(state)
        assert "trace_id" in resultado

    def test_reusa_trace_id_existente(self):
        from src.observability.decorator import observable

        @observable
        def nodo_prueba(state):
            return {"resultado": "ok"}

        state = {"trace_id": "mi-trace-existente", "mensajes": []}
        resultado = nodo_prueba(state)
        assert resultado["trace_id"] == "mi-trace-existente"

    def test_loggea_inicio_y_fin(self, tmp_path):
        import os
        import json
        from src.observability.decorator import observable, _logger_global

        log_dir = tmp_path / "logs_decorator"
        from src.observability.logger import LoggerEstructurado
        _logger_global.logger = LoggerEstructurado(
            nombre="decorator_test", log_dir=str(log_dir), nivel="DEBUG"
        )

        @observable
        def nodo_prueba(state):
            return {"resultado": "ok"}

        nodo_prueba({"mensajes": []})
        log_file = os.path.join(str(log_dir), "metrics.jsonl")
        with open(log_file) as f:
            lineas = [json.loads(l) for l in f.readlines()]
        eventos = [l["evento"] for l in lineas]
        assert "nodo_iniciado" in eventos
        assert "nodo_finalizado" in eventos

    def test_registra_metrica(self, tmp_path):
        from src.observability.decorator import observable, _logger_global
        from src.observability.logger import LoggerEstructurado
        from src.observability.metrics import RecolectorMetricas
        import os, json

        log_dir = tmp_path / "logs_metrica"
        _logger_global.logger = LoggerEstructurado(
            nombre="decorator_metric_test", log_dir=str(log_dir), nivel="DEBUG"
        )

        recolector_global = RecolectorMetricas()

        @observable
        def nodo_prueba(state):
            return {"resultado": "ok"}

        nodo_prueba({"mensajes": []}, _recolector_metrica=recolector_global)
        resumen = recolector_global.resumen()
        assert resumen["total_llamadas"] >= 1
