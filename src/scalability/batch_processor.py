import heapq
import time
from dataclasses import dataclass, field
from typing import Any

PRIORIDAD_CRITICA = 0
PRIORIDAD_ALTA = 1
PRIORIDAD_NORMAL = 2
PRIORIDAD_BAJA = 3


@dataclass(order=True)
class Solicitud:
    prioridad: int
    timestamp: float = field(default_factory=time.time)
    id: str = ""
    pregunta: str = ""


class ProcesadorLotes:
    def __init__(self, tamano_lote: int = 5):
        self.tamano_lote = tamano_lote
        self.cola: list[Solicitud] = []
        self._contador_id = 0

    def agregar(self, solicitud: Solicitud):
        heapq.heappush(self.cola, solicitud)

    def _siguiente(self):
        if not self.cola:
            return None
        return heapq.heappop(self.cola)

    def obtener_lote(self):
        lote = []
        for _ in range(self.tamano_lote):
            if not self.cola:
                break
            lote.append(heapq.heappop(self.cola))
        return lote

    def procesar_lote(self, funcion_procesar) -> list[Any]:
        lote = self.obtener_lote()
        resultados = []
        for solicitud in lote:
            try:
                resultado = funcion_procesar(solicitud.pregunta)
                resultados.append({"id": solicitud.id, "exito": True, "resultado": resultado})
            except Exception as e:
                resultados.append({"id": solicitud.id, "exito": False, "error": str(e)})
        return resultados

    def procesar_todo(self, funcion_procesar) -> list[Any]:
        resultados = []
        while self.cola:
            resultados.extend(self.procesar_lote(funcion_procesar))
        return resultados

    def resumen(self) -> dict:
        prioridades = {}
        for s in self.cola:
            nombre = {0: "CRITICA", 1: "ALTA", 2: "NORMAL", 3: "BAJA"}.get(s.prioridad, "DESCONOCIDA")
            prioridades[nombre] = prioridades.get(nombre, 0) + 1
        return {
            "total_solicitudes": len(self.cola),
            "por_prioridad": prioridades,
            "tamano_lote": self.tamano_lote,
        }

    def vaciar(self):
        self.cola.clear()
