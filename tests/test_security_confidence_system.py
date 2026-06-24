class TestConfidenceSystem:
    def test_auto_confianza_alta(self):
        from src.security.confidence_system import SistemaConfianza
        sistema = SistemaConfianza()
        resultado = sistema.evaluar(0.95)
        assert resultado.nivel.name == "AUTO"

    def test_escalar_confianza_media(self):
        from src.security.confidence_system import SistemaConfianza
        sistema = SistemaConfianza()
        resultado = sistema.evaluar(0.65)
        assert resultado.nivel.name == "ESCALAR"

    def test_rechazar_confianza_baja(self):
        from src.security.confidence_system import SistemaConfianza
        sistema = SistemaConfianza()
        resultado = sistema.evaluar(0.3)
        assert resultado.nivel.name == "RECHAZAR"
