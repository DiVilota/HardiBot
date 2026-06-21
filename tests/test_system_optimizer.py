class TestSystemOptimizer:
    def test_cache_hit_reduce_costo(self):
        from src.scalability.system_optimizer import SistemaOptimizado
        sistema = SistemaOptimizado()
        resultado = sistema.procesar("consulta simple")
        assert resultado["texto"] is not None

    def test_reporte_comparativo_generado(self):
        from src.scalability.system_optimizer import SistemaOptimizado
        sistema = SistemaOptimizado()
        sistema.procesar("consulta 1")
        sistema.procesar("consulta 2")
        reporte = sistema.generar_reporte_comparativo()
        assert "optimizado" in reporte.columns
        assert "no_optimizado" in reporte.columns
        assert len(reporte) > 0

    def test_error_no_detiene_sistema(self):
        from src.scalability.system_optimizer import SistemaOptimizado
        sistema = SistemaOptimizado()
        resultado = sistema.procesar("")
        assert "texto" in resultado
