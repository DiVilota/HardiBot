class TestHallucinationDetector:
    def test_detecta_alucinacion(self):
        from src.security.hallucination_detector import DetectorAlucinacion
        detector = DetectorAlucinacion()
        resultado = detector.verificar(
            afirmacion="El Ryzen 5 5600G tiene 12 nucleos",
            contexto="Ryzen 5 5600G: 6 nucleos, 12 hilos",
        )
        assert resultado.es_alucinacion is True

    def test_afirmacion_consistente(self):
        from src.security.hallucination_detector import DetectorAlucinacion
        detector = DetectorAlucinacion()
        resultado = detector.verificar(
            afirmacion="El Ryzen 5 5600G tiene 6 nucleos",
            contexto="Ryzen 5 5600G: 6 nucleos, 12 hilos",
        )
        assert resultado.es_alucinacion is False
