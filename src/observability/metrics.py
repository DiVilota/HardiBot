import os
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Optional


PRECIOS = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4": {"prompt": 30.00, "completion": 60.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
}


@dataclass
class MetricaLlamada:
    timestamp: str
    modelo: str
    tiempo_respuesta_ms: float
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    costo_estimado_usd: float
    exitosa: bool
    tipo_error: Optional[str] = None
    mensaje_error: Optional[str] = None
    trace_id: Optional[str] = None


class RecolectorMetricas:
    def __init__(self):
        self.metricas: List[MetricaLlamada] = []

    def _calcular_costo(self, modelo: str, tokens_prompt: int, tokens_completion: int) -> float:
        precios = PRECIOS.get(modelo, {"prompt": 2.50, "completion": 10.00})
        costo_prompt = precios["prompt"] * tokens_prompt / 1_000_000
        costo_completion = precios["completion"] * tokens_completion / 1_000_000
        return round(costo_prompt + costo_completion, 6)

    def registrar_exito(
        self,
        modelo: str,
        tiempo_respuesta_ms: float,
        tokens_prompt: int,
        tokens_completion: int,
        trace_id: str = None,
    ) -> MetricaLlamada:
        tokens_total = tokens_prompt + tokens_completion
        costo = self._calcular_costo(modelo, tokens_prompt, tokens_completion)
        metrica = MetricaLlamada(
            timestamp=datetime.now(timezone.utc).isoformat(),
            modelo=modelo,
            tiempo_respuesta_ms=tiempo_respuesta_ms,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            tokens_total=tokens_total,
            costo_estimado_usd=costo,
            exitosa=True,
            trace_id=trace_id,
        )
        self.metricas.append(metrica)
        return metrica

    def registrar_error(
        self,
        modelo: str,
        tiempo_respuesta_ms: float,
        tokens_prompt: int,
        tokens_completion: int,
        tipo_error: str = None,
        mensaje_error: str = None,
        trace_id: str = None,
    ) -> MetricaLlamada:
        tokens_total = tokens_prompt + tokens_completion
        costo = self._calcular_costo(modelo, tokens_prompt, tokens_completion)
        metrica = MetricaLlamada(
            timestamp=datetime.now(timezone.utc).isoformat(),
            modelo=modelo,
            tiempo_respuesta_ms=tiempo_respuesta_ms,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            tokens_total=tokens_total,
            costo_estimado_usd=costo,
            exitosa=False,
            tipo_error=tipo_error,
            mensaje_error=mensaje_error,
            trace_id=trace_id,
        )
        self.metricas.append(metrica)
        return metrica

    def resumen(self) -> dict:
        if not self.metricas:
            return {
                "total_llamadas": 0,
                "avg_latencia_ms": 0,
                "p50_latencia_ms": 0,
                "p95_latencia_ms": 0,
                "max_latencia_ms": 0,
                "tasa_error_pct": 0,
                "tokens_totales": 0,
                "costo_total_usd": 0,
            }
        tiempos = sorted([m.tiempo_respuesta_ms for m in self.metricas])
        n = len(tiempos)
        errores = sum(1 for m in self.metricas if not m.exitosa)
        tokens_totales = sum(m.tokens_total for m in self.metricas)
        costo_total = sum(m.costo_estimado_usd for m in self.metricas)

        def percentile(data, p):
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f + 1 < len(data) else f
            if c == f:
                return data[f]
            return data[f] + (k - f) * (data[c] - data[f])

        return {
            "total_llamadas": n,
            "avg_latencia_ms": round(sum(tiempos) / n, 2),
            "p50_latencia_ms": round(percentile(tiempos, 50), 2),
            "p95_latencia_ms": round(percentile(tiempos, 95), 2),
            "max_latencia_ms": round(max(tiempos), 2),
            "tasa_error_pct": round((errores / n) * 100, 2),
            "tokens_totales": tokens_totales,
            "costo_total_usd": round(costo_total, 6),
        }

    def a_dataframe(self):
        import pandas as pd
        registros = []
        for m in self.metricas:
            registros.append({
                "timestamp": m.timestamp,
                "modelo": m.modelo,
                "tiempo_respuesta_ms": m.tiempo_respuesta_ms,
                "tokens_prompt": m.tokens_prompt,
                "tokens_completion": m.tokens_completion,
                "tokens_total": m.tokens_total,
                "costo_estimado_usd": m.costo_estimado_usd,
                "exitosa": m.exitosa,
                "tipo_error": m.tipo_error,
                "mensaje_error": m.mensaje_error,
                "trace_id": m.trace_id,
            })
        return pd.DataFrame(registros)
