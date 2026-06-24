class TestNormalizer:
    def test_normaliza_unicode_nfc(self):
        from src.security.normalizer import normalizar_texto
        texto = "\u0041\u0301"  # A + combining accent
        resultado = normalizar_texto(texto)
        assert resultado == "\u00c1"  # Á precomposed

    def test_remueve_zero_width(self):
        from src.security.normalizer import normalizar_texto
        texto = "h\u200Bello\u200C"
        resultado = normalizar_texto(texto)
        assert resultado == "hello"

    def test_normaliza_leetspeak(self):
        from src.security.normalizer import normalizar_texto
        texto = "h4ck3r"
        resultado = normalizar_texto(texto)
        assert "hacker" in resultado.lower()

    def test_remueve_caracteres_control(self):
        from src.security.normalizer import normalizar_texto
        texto = "hola\x00\x01\x02mundo"
        resultado = normalizar_texto(texto)
        assert resultado == "holamundo"
