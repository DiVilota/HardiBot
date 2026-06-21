class TestPiiDetector:
    def test_detecta_email(self):
        from src.security.pii_detector import detectar_pii
        resultado = detectar_pii("mi correo es user@example.com")
        assert "correo_electronico" in resultado
        assert "user@example.com" in resultado["correo_electronico"]

    def test_detecta_rut(self):
        from src.security.pii_detector import detectar_pii
        resultado = detectar_pii("mi RUT es 12.345.678-9")
        assert "rut_chile" in resultado

    def test_detecta_telefono(self):
        from src.security.pii_detector import detectar_pii
        resultado = detectar_pii("llamame al +56 9 1234 5678")
        assert "telefono_chile" in resultado

    def test_detecta_tarjeta(self):
        from src.security.pii_detector import detectar_pii
        resultado = detectar_pii("mi tarjeta es 1234-5678-9012-3456")
        assert "numero_tarjeta" in resultado

    def test_sanitizar_pii(self):
        from src.security.pii_detector import sanitizar_pii
        texto = "email: test@example.com"
        limpio = sanitizar_pii(texto)
        assert "test@example.com" not in limpio
        assert "REDACTADO" in limpio
