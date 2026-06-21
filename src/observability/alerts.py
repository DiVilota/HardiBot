from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Optional

from src.observability.metrics import RecolectorMetricas


@dataclass
class ReglaAlerta:
    nombre: str
    descripcion: str
    umbral: float
    tipo: str


@dataclass
class Alerta:
    timestamp: str
    regla: str
    severidad: str
    valor_actual: float
    umbral: float
    mensaje: str


class SistemaAlertas:
    def __init__(self):
        self.reglas: List[ReglaAlerta] = []
        self._agregar_reglas_default()

    def _agregar_reglas_default(self):
        defaults = [
            ReglaAlerta("latencia_alta", "Latencia promedio superior a 5s", 5000, "latencia_ms"),
            ReglaAlerta("tasa_error_alta", "Tasa de error superior a 10%", 10, "tasa_error_pct"),
            ReglaAlerta("tokens_excesivos", "Total de tokens superior a 50k", 50000, "tokens_totales"),
            ReglaAlerta("costo_elevado", "Costo total superior a $0.10 USD", 0.10, "costo_usd"),
        ]
        self.reglas.extend(defaults)

    def agregar_regla(self, regla: ReglaAlerta):
        self.reglas.append(regla)

    def evaluar(self, recolector: RecolectorMetricas) -> List[Alerta]:
        resumen = recolector.resumen()
        if resumen["total_llamadas"] == 0:
            return []
        alertas: List[Alerta] = []
        for regla in self.reglas:
            valor = self._obtener_valor(resumen, regla.tipo)
            if valor is None:
                continue
            if valor > regla.umbral:
                if valor > regla.umbral * 1.5:
                    severidad = "CRITICAL"
                else:
                    severidad = "WARNING"
                alertas.append(Alerta(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    regla=regla.nombre,
                    severidad=severidad,
                    valor_actual=valor,
                    umbral=regla.umbral,
                    mensaje=f"{regla.descripcion}: {valor} (umbral: {regla.umbral})",
                ))
        return alertas

    def _obtener_valor(self, resumen: dict, tipo: str) -> Optional[float]:
        mapping = {
            "latencia_ms": "avg_latencia_ms",
            "tasa_error_pct": "tasa_error_pct",
            "tokens_totales": "tokens_totales",
            "costo_usd": "costo_total_usd",
        }
        key = mapping.get(tipo)
        if key is None:
            return None
        return resumen.get(key, 0)
