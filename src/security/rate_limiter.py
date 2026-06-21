import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List


class LimitadorTasa:
    def __init__(self, max_peticiones: int, ventana_segundos: float):
        self.max_peticiones = max_peticiones
        self.ventana = ventana_segundos
        self.peticiones: List[float] = []
        self._lock = threading.Lock()

    def permitir(self) -> bool:
        ahora = time.time()
        with self._lock:
            self.peticiones = [t for t in self.peticiones if ahora - t < self.ventana]
            if len(self.peticiones) >= self.max_peticiones:
                return False
            self.peticiones.append(ahora)
            return True

    def peticiones_restantes(self) -> int:
        ahora = time.time()
        with self._lock:
            self.peticiones = [t for t in self.peticiones if ahora - t < self.ventana]
            return max(0, self.max_peticiones - len(self.peticiones))


class GestorPresupuesto:
    def __init__(self, presupuesto_maximo: int = 1000):
        self.presupuesto_maximo = presupuesto_maximo
        self.presupuesto_restante = presupuesto_maximo

    def consumir(self, tokens: int) -> bool:
        if tokens > self.presupuesto_restante:
            return False
        self.presupuesto_restante -= tokens
        return True

    def reiniciar(self):
        self.presupuesto_restante = self.presupuesto_maximo


class ProtectorSistema:
    def __init__(self, umbral_fallos: int = 5, duracion_bloqueo: float = 300.0):
        self.umbral_fallos = umbral_fallos
        self.duracion_bloqueo = duracion_bloqueo
        self._fallos: Dict[str, List[float]] = {}
        self._bloqueos: Dict[str, float] = {}
        self._lock = threading.Lock()

    def registrar_fallo(self, clave: str):
        ahora = time.time()
        with self._lock:
            if clave not in self._fallos:
                self._fallos[clave] = []
            self._fallos[clave] = [t for t in self._fallos[clave] if ahora - t < 60.0]
            self._fallos[clave].append(ahora)
            if len(self._fallos[clave]) >= self.umbral_fallos:
                self._bloqueos[clave] = ahora + self.duracion_bloqueo

    def esta_bloqueado(self, clave: str) -> bool:
        ahora = time.time()
        with self._lock:
            if clave in self._bloqueos:
                if ahora < self._bloqueos[clave]:
                    return True
                del self._bloqueos[clave]
            return False

    def tiempo_restante_bloqueo(self, clave: str) -> float:
        ahora = time.time()
        with self._lock:
            if clave in self._bloqueos:
                restante = self._bloqueos[clave] - ahora
                return max(0.0, restante)
            return 0.0
