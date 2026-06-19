class TestOutputGuard:
    def test_detecta_pii_en_salida(self):
        from src.security.output_guard import guardia_salida
        resultado = guardia_salida("el email es test@example.com")
        assert resultado.es_seguro is False

    def test_permite_salida_segura(self):
        from src.security.output_guard import guardia_salida
        resultado = guardia_salida("El Ryzen 5 cuesta $150.000")
        assert resultado.es_seguro is True

    def test_maneja_json(self):
        from src.security.output_guard import guardia_salida
        resultado = guardia_salida('{"producto": "Ryzen 5", "precio": 150000}')
        assert resultado.es_seguro is True

    def test_salida_vacia(self):
        from src.security.output_guard import guardia_salida
        resultado = guardia_salida("")
        assert resultado.es_seguro is True
