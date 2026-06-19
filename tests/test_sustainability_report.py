import json
import os
import tempfile

class TestSustainabilityReport:
    def setup_method(self):
        from src.scalability.sustainability_report import ReporteSostenibilidad
        self.tmp = tempfile.mkdtemp()
        self.reporte = ReporteSostenibilidad(log_dir=self.tmp)

    def test_agregar_metricas_cache(self):
        self.reporte.agregar_metricas_cache(hits=10, misses=2, tokens_ahorrados=5000)
        assert self.reporte.metricas["cache_hits"] == 10
        assert self.reporte.metricas["cache_misses"] == 2

    def test_agregar_metricas_enrutamiento(self):
        self.reporte.agregar_metricas_enrutamiento(costo_ahorrado=15.0)
        assert self.reporte.metricas["costo_ahorrado_enrutamiento"] == 15.0

    def test_agregar_registro(self):
        self.reporte.agregar_registro("gpt-4o", 100, 50, 2.5, "exito")
        assert len(self.reporte.registros) == 1
        assert self.reporte.registros[0]["modelo"] == "gpt-4o"

    def test_generar_reporte_y_verificar_persistencia(self):
        import tempfile
        from src.scalability.sustainability_report import ReporteSostenibilidad
        with tempfile.TemporaryDirectory() as tmpdir:
            reporte = ReporteSostenibilidad(log_dir=tmpdir)
            reporte.agregar_metricas_cache(hits=5, misses=1, tokens_ahorrados=1000)
            reporte.agregar_registro("gpt-4o", 200, 100, 3.0, "exito")
            archivo = reporte.guardar()
            assert os.path.exists(archivo)
            with open(archivo) as f:
                lineas = [json.loads(l) for l in f if l.strip()]
            assert len(lineas) >= 1
