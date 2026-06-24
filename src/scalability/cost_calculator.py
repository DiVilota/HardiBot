from collections import defaultdict

PRECIOS = {
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "o1": {"input": 15.0, "output": 60.0},
}

NIVEL_INFO = "INFO"
NIVEL_WARNING = "WARNING"
NIVEL_CRITICAL = "CRITICAL"


class CalculadorCostos:
    def __init__(self, presupuesto_diario: float = 100.0):
        self.presupuesto_diario = presupuesto_diario
        self._registros: list[dict] = []

    def registrar(self, modelo: str, tokens_in: int, tokens_out: int):
        precios = PRECIOS.get(modelo, PRECIOS["gpt-4o"])
        costo = (tokens_in / 1000 * precios["input"]) + (tokens_out / 1000 * precios["output"])
        self._registros.append({
            "modelo": modelo,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "costo": round(costo, 6),
        })

    def total_gastado(self) -> float:
        return round(sum(r["costo"] for r in self._registros), 4)

    def proyectar_costos(self, consultas_por_dia: int) -> dict:
        if not self._registros:
            return {"estimado_diario": 0.0, "promedio_por_consulta": 0.0}
        promedio = sum(r["costo"] for r in self._registros) / len(self._registros)
        return {
            "estimado_diario": round(promedio * consultas_por_dia, 2),
            "promedio_por_consulta": round(promedio, 4),
        }

    def comparar_modelos(self) -> dict:
        por_modelo = defaultdict(lambda: {"consultas": 0, "costo_total": 0.0, "tokens_in": 0, "tokens_out": 0})
        for r in self._registros:
            m = por_modelo[r["modelo"]]
            m["consultas"] += 1
            m["costo_total"] += r["costo"]
            m["tokens_in"] += r["tokens_in"]
            m["tokens_out"] += r["tokens_out"]
        return dict(por_modelo)

    def evaluar_alertas(self, gasto_actual: float) -> list[dict]:
        alertas = []
        porcentaje = (gasto_actual / self.presupuesto_diario) * 100
        if porcentaje >= 100:
            alertas.append({"nivel": NIVEL_CRITICAL, "mensaje": f"Presupuesto agotado: {porcentaje:.0f}%", "porcentaje": porcentaje})
        elif porcentaje >= 80:
            alertas.append({"nivel": NIVEL_WARNING, "mensaje": f"Presupuesto casi agotado: {porcentaje:.0f}%", "porcentaje": porcentaje})
        elif porcentaje >= 50:
            alertas.append({"nivel": NIVEL_INFO, "mensaje": f"Presupuesto al {porcentaje:.0f}%", "porcentaje": porcentaje})
        return alertas

    def resumen(self) -> dict:
        return {
            "total_gastado": self.total_gastado(),
            "presupuesto_diario": self.presupuesto_diario,
            "uso_presupuesto": round((self.total_gastado() / self.presupuesto_diario) * 100, 1) if self.presupuesto_diario > 0 else 0,
            "total_consultas": len(self._registros),
        }
