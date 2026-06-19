class TestTokenEstimator:
    def test_texto_corto(self):
        from src.scalability.token_estimator import estimar_tokens
        assert estimar_tokens("Hola") == 1

    def test_texto_largo(self):
        from src.scalability.token_estimator import estimar_tokens
        texto = "palabra " * 100
        assert estimar_tokens(texto) == max(1, len(texto) // 4)

    def test_texto_vacio(self):
        from src.scalability.token_estimator import estimar_tokens
        assert estimar_tokens("") == 0

    def test_config_modelo(self):
        from src.scalability.token_estimator import ConfigModelo
        cfg = ConfigModelo("gpt-4o", costo_por_1k=5.0, latencia=1.0, capacidad_max=8192)
        assert cfg.nombre == "gpt-4o"
        assert cfg.costo_por_1k == 5.0
