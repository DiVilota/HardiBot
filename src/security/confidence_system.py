from enum import Enum
from dataclasses import dataclass


class NivelConfianza(Enum):
    AUTO = "AUTO"
    ESCALAR = "ESCALAR"
    RECHAZAR = "RECHAZAR"


@dataclass
class ResultadoConfianza:
    nivel: NivelConfianza
    puntuacion: float
    mensaje: str = ""


class SistemaConfianza:
    def evaluar(self, puntuacion: float) -> ResultadoConfianza:
        if puntuacion >= 0.8:
            return ResultadoConfianza(
                nivel=NivelConfianza.AUTO,
                puntuacion=puntuacion,
                mensaje="Confianza alta: respuesta automatica",
            )
        elif puntuacion >= 0.5:
            return ResultadoConfianza(
                nivel=NivelConfianza.ESCALAR,
                puntuacion=puntuacion,
                mensaje="Confianza media: escalar a humano",
            )
        else:
            return ResultadoConfianza(
                nivel=NivelConfianza.RECHAZAR,
                puntuacion=puntuacion,
                mensaje="Confianza baja: respuesta rechazada",
            )
