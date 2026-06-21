class TestBiasDetector:
    def test_detecta_sesgo_alto(self):
        from src.security.bias_detector import DetectorSesgo
        detector = DetectorSesgo()
        vector_a = [1.0, 0.0, 0.0]
        vector_b = [0.0, 1.0, 0.0]
        resultado = detector.calcular_sesgo(vector_a, vector_b)
        assert resultado.sesgo > 0.5

    def test_sesgo_bajo_textos_similares(self):
        from src.security.bias_detector import DetectorSesgo
        detector = DetectorSesgo()
        resultado = detector.evaluar_texto("producto excelente", "producto excelente")
        assert resultado.sesgo < 0.1
