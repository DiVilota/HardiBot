import time


class TestRateLimiter:
    def test_permite_dentro_del_limite(self):
        from src.security.rate_limiter import LimitadorTasa
        limitador = LimitadorTasa(max_peticiones=5, ventana_segundos=10.0)
        for _ in range(5):
            assert limitador.permitir() is True

    def test_bloquea_exceso(self):
        from src.security.rate_limiter import LimitadorTasa
        limitador = LimitadorTasa(max_peticiones=3, ventana_segundos=5.0)
        for _ in range(3):
            limitador.permitir()
        assert limitador.permitir() is False

    def test_restablece_tras_ventana(self):
        from src.security.rate_limiter import LimitadorTasa
        limitador = LimitadorTasa(max_peticiones=1, ventana_segundos=0.1)
        assert limitador.permitir() is True
        assert limitador.permitir() is False
        time.sleep(0.15)
        assert limitador.permitir() is True

    def test_presupuesto_degrada(self):
        from src.security.rate_limiter import GestorPresupuesto
        gestor = GestorPresupuesto(presupuesto_maximo=1000)
        assert gestor.consumir(100) is True
        assert gestor.presupuesto_restante == 900

    def test_protector_bloquea_ataque(self):
        from src.security.rate_limiter import ProtectorSistema
        protector = ProtectorSistema(umbral_fallos=3, duracion_bloqueo=0.5)
        for _ in range(3):
            protector.registrar_fallo("test")
        assert protector.esta_bloqueado("test") is True
        time.sleep(0.6)
        assert protector.esta_bloqueado("test") is False
