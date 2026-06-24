import time
import random


class RetryConBackoff:
    def __init__(self, max_reintentos: int = 3, base: float = 1.0, factor: float = 2.0, jitter: bool = True):
        self.max_reintentos = max_reintentos
        self.base = base
        self.factor = factor
        self.jitter = jitter

    def ejecutar(self, funcion, **kwargs):
        ultimo_error = None
        for intento in range(1, self.max_reintentos + 1):
            try:
                return funcion(**kwargs)
            except Exception as e:
                ultimo_error = e
                if intento < self.max_reintentos:
                    espera = self.base * (self.factor ** (intento - 1))
                    if self.jitter:
                        espera += random.uniform(0, espera * 0.1)
                    time.sleep(espera)
        return None


class CircuitBreaker:
    def __init__(self, umbral: int = 3, recovery: float = 30.0):
        self.umbral = umbral
        self.recovery = recovery
        self.fallos = 0
        self.ultimo_fallo = 0.0
        self.estado = "cerrado"

    def ejecutar(self, funcion, **kwargs):
        if self.estado == "abierto":
            if (time.time() - self.ultimo_fallo) > self.recovery:
                self.estado = "semi-abierto"
            else:
                raise RuntimeError("CircuitBreaker abierto")

        try:
            resultado = funcion(**kwargs)
            if self.estado == "semi-abierto":
                self.estado = "cerrado"
                self.fallos = 0
            return resultado
        except Exception as e:
            self.fallos += 1
            self.ultimo_fallo = time.time()
            if self.fallos >= self.umbral:
                self.estado = "abierto"
            raise

    def reset(self):
        self.fallos = 0
        self.estado = "cerrado"
        self.ultimo_fallo = 0.0


class CadenaFallback:
    def __init__(self):
        self._modelos = []

    def ejecutar(self, funciones: list) -> str | None:
        for i, func in enumerate(funciones):
            try:
                resultado = func()
                if resultado is not None:
                    return resultado
            except Exception:
                continue
        return None
