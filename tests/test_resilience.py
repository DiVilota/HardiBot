import time

class TestResilience:
    def test_retry_exito(self):
        from src.scalability.resilience import RetryConBackoff
        llamadas = 0

        def funcion():
            nonlocal llamadas
            llamadas += 1
            if llamadas < 2:
                raise ValueError("Fallo")
            return "exito"

        retry = RetryConBackoff(max_reintentos=3, base=0.01)
        resultado = retry.ejecutar(funcion)
        assert resultado == "exito"
        assert llamadas == 2

    def test_retry_fracaso(self):
        from src.scalability.resilience import RetryConBackoff
        llamadas = 0

        def funcion():
            nonlocal llamadas
            llamadas += 1
            raise ValueError("Error")

        retry = RetryConBackoff(max_reintentos=3, base=0.01)
        resultado = retry.ejecutar(funcion)
        assert resultado is None
        assert llamadas == 3

    def test_retry_backoff_tiempo(self):
        from src.scalability.resilience import RetryConBackoff
        inicio = time.time()
        llamadas = 0

        def funcion():
            nonlocal llamadas
            llamadas += 1
            raise ValueError("Error")

        retry = RetryConBackoff(max_reintentos=3, base=0.02)
        retry.ejecutar(funcion)
        elapsed = time.time() - inicio
        assert elapsed >= 0.02

    def test_circuit_breaker_cerrado(self):
        from src.scalability.resilience import CircuitBreaker
        cb = CircuitBreaker(umbral=3, recovery=0.05)
        assert cb.estado == "cerrado"

    def test_circuit_breaker_abre(self):
        from src.scalability.resilience import CircuitBreaker
        cb = CircuitBreaker(umbral=2, recovery=0.05)

        def falla():
            raise ValueError("Error")

        for _ in range(2):
            try:
                cb.ejecutar(falla)
            except ValueError:
                pass
        assert cb.estado == "abierto"

    def test_circuit_breaker_recovery(self):
        from src.scalability.resilience import CircuitBreaker
        cb = CircuitBreaker(umbral=2, recovery=0.05)

        def falla():
            raise ValueError("Error")

        def ok():
            return "ok"

        for _ in range(2):
            try:
                cb.ejecutar(falla)
            except ValueError:
                pass
        assert cb.estado == "abierto"

        time.sleep(0.06)
        resultado = cb.ejecutar(ok)
        assert resultado == "ok"
        assert cb.estado == "cerrado"

    def test_cadena_fallback_primero_exitoso(self):
        from src.scalability.resilience import CadenaFallback

        def ok():
            return "ok"

        def noop():
            return "noop"

        cadena = CadenaFallback()
        resultado = cadena.ejecutar([ok, noop])
        assert resultado == "ok"

    def test_cadena_fallback_segundo_exitoso(self):
        from src.scalability.resilience import CadenaFallback

        def falla():
            raise ValueError("Error")

        def ok():
            return "ok"

        cadena = CadenaFallback()
        resultado = cadena.ejecutar([falla, ok])
        assert resultado == "ok"

    def test_cadena_fallback_todos_fallan(self):
        from src.scalability.resilience import CadenaFallback

        def falla():
            raise ValueError("Error")

        cadena = CadenaFallback()
        resultado = cadena.ejecutar([falla, falla])
        assert resultado is None
