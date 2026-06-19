class TestCostCalculator:
    def setup_method(self):
        from src.scalability.cost_calculator import CalculadorCostos
        self.calc = CalculadorCostos(presupuesto_diario=100.0)

    def test_registrar_y_total(self):
        self.calc.registrar("gpt-4o", tokens_in=1000, tokens_out=500)
        total = self.calc.total_gastado()
        assert total > 0

    def test_proyectar_costos(self):
        self.calc.registrar("gpt-4o", tokens_in=1000, tokens_out=500)
        proy = self.calc.proyectar_costos(consultas_por_dia=100)
        assert proy["estimado_diario"] > 0

    def test_comparar_modelos(self):
        self.calc.registrar("gpt-4o", tokens_in=1000, tokens_out=500)
        self.calc.registrar("gpt-4o-mini", tokens_in=1000, tokens_out=500)
        comparacion = self.calc.comparar_modelos()
        assert "gpt-4o" in comparacion
        assert "gpt-4o-mini" in comparacion

    def test_alerta_50_porciento(self):
        from src.scalability.cost_calculator import NIVEL_INFO
        alertas = self.calc.evaluar_alertas(gasto_actual=60.0)
        assert len(alertas) > 0
        assert alertas[0]["nivel"] == NIVEL_INFO

    def test_alerta_80_porciento(self):
        from src.scalability.cost_calculator import NIVEL_WARNING
        alertas = self.calc.evaluar_alertas(gasto_actual=85.0)
        assert len(alertas) > 0
        assert alertas[0]["nivel"] == NIVEL_WARNING

    def test_resumen(self):
        self.calc.registrar("gpt-4o", tokens_in=1000, tokens_out=500)
        resumen = self.calc.resumen()
        assert "total_gastado" in resumen
        assert "presupuesto_diario" in resumen
