import json
import os
import tempfile


class TestLoggerEstructurado:
    def test_formato_json(self, tmp_path):
        from src.observability.logger import LoggerEstructurado
        log_dir = tmp_path / "logs"
        logger = LoggerEstructurado(nombre="test", log_dir=str(log_dir), nivel="DEBUG")
        logger.info("evento_test", {"key": "value"})
        logger_file = os.path.join(str(log_dir), "metrics.jsonl")
        with open(logger_file) as f:
            linea = json.loads(f.readline())
        assert linea["evento"] == "evento_test"
        assert linea["nivel"] == "INFO"
        assert linea["logger"] == "test"
        assert linea["metadata"]["key"] == "value"
        assert "timestamp" in linea
        assert "trace_id" in linea

    def test_filtro_por_nivel(self, tmp_path):
        from src.observability.logger import LoggerEstructurado
        log_dir = tmp_path / "logs"
        logger = LoggerEstructurado(nombre="test_filter", log_dir=str(log_dir), nivel="WARNING")
        logger.debug("no_debe_aparecer")
        logger.warning("si_debe_aparecer")
        logger_file = os.path.join(str(log_dir), "metrics.jsonl")
        with open(logger_file) as f:
            contenidos = [json.loads(l) for l in f.readlines()]
        niveles = [c["nivel"] for c in contenidos]
        assert "WARNING" in niveles
        assert "DEBUG" not in niveles

    def test_filtro_por_trace_id(self, tmp_path):
        from src.observability.logger import LoggerEstructurado
        log_dir = tmp_path / "logs"
        logger = LoggerEstructurado(nombre="test_trace", log_dir=str(log_dir), nivel="DEBUG")
        logger.info("ev1", trace_id="abc")
        logger.info("ev2", trace_id="def")
        logger.info("ev3", trace_id="abc")
        resultados = logger.obtener_por_trace_id("abc")
        assert len(resultados) == 2
        for r in resultados:
            assert r["trace_id"] == "abc"

    def test_no_crashea_sin_archivo(self, tmp_path):
        from src.observability.logger import LoggerEstructurado
        log_dir = tmp_path / "logs_no_permission"
        logger = LoggerEstructurado(nombre="test_no_file", log_dir=str(log_dir), nivel="DEBUG")
        logger.info("deberia_funcar")
        logger_file = os.path.join(str(log_dir), "metrics.jsonl")
        assert os.path.exists(logger_file)

    def test_crea_directorio_automatico(self, tmp_path):
        from src.observability.logger import LoggerEstructurado
        log_dir = tmp_path / "nuevo" / "subdir" / "logs"
        assert not os.path.exists(str(log_dir))
        logger = LoggerEstructurado(nombre="test_auto_dir", log_dir=str(log_dir), nivel="DEBUG")
        logger.info("directorio_creado")
        assert os.path.exists(str(log_dir))
        logger_file = os.path.join(str(log_dir), "metrics.jsonl")
        assert os.path.exists(logger_file)
