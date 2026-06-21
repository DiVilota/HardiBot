import json
import os
import time
from datetime import datetime, timezone


class ReporteSostenibilidad:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.metricas = {
            "cache_hits": 0,
            "cache_misses": 0,
            "tokens_ahorrados_cache": 0,
            "costo_ahorrado_enrutamiento": 0.0,
            "latencia_promedio": 0.0,
            "latencia_min": float("inf"),
            "latencia_max": 0.0,
            "total_consultas": 0,
            "total_errores": 0,
        }
        self.registros = []

    def agregar_metricas_cache(self, hits: int = 0, misses: int = 0, tokens_ahorrados: int = 0):
        self.metricas["cache_hits"] += hits
        self.metricas["cache_misses"] += misses
        self.metricas["tokens_ahorrados_cache"] += tokens_ahorrados

    def agregar_metricas_enrutamiento(self, costo_ahorrado: float = 0.0):
        self.metricas["costo_ahorrado_enrutamiento"] += costo_ahorrado

    def agregar_registro(self, modelo: str, tokens_in: int, tokens_out: int, latencia: float, estado: str = "exito"):
        entrada = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modelo": modelo,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latencia": latencia,
            "estado": estado,
        }
        self.registros.append(entrada)
        self.metricas["total_consultas"] += 1
        if estado == "error":
            self.metricas["total_errores"] += 1
        latencias = [r["latencia"] for r in self.registros]
        if latencias:
            self.metricas["latencia_promedio"] = round(sum(latencias) / len(latencias), 2)
            self.metricas["latencia_min"] = round(min(latencias), 2)
            self.metricas["latencia_max"] = round(max(latencias), 2)

    def guardar(self) -> str:
        archivo = os.path.join(self.log_dir, "sustainability.jsonl")
        reporte = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metricas": self.metricas,
            "registros": self.registros[-100:],
        }
        with open(archivo, "a") as f:
            f.write(json.dumps(reporte) + "\n")
        return archivo

    def visualizar(self):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle("Reporte de Sostenibilidad - HardiBot", fontsize=14)

            ax1 = axes[0, 0]
            labels = ["Hits", "Misses"]
            values = [self.metricas["cache_hits"], self.metricas["cache_misses"]]
            ax1.bar(labels, values, color=["green", "red"])
            ax1.set_title("Rendimiento de Cache")

            ax2 = axes[0, 1]
            if self.registros:
                modelos = list(set(r["modelo"] for r in self.registros))
                costos = []
                for m in modelos:
                    costos.append(sum(r.get("tokens_in", 0) + r.get("tokens_out", 0) for r in self.registros if r["modelo"] == m))
                ax2.bar(modelos, costos)
            ax2.set_title("Tokens por Modelo")

            ax3 = axes[1, 0]
            ax3.bar(["Promedio", "Min", "Max"], [
                self.metricas["latencia_promedio"],
                self.metricas["latencia_min"] if self.metricas["latencia_min"] != float("inf") else 0,
                self.metricas["latencia_max"],
            ])
            ax3.set_title("Latencia (s)")

            ax4 = axes[1, 1]
            ax4.axis("off")
            ax4.text(0.1, 0.5, json.dumps(self.metricas, indent=2), fontsize=9, family="monospace", verticalalignment="center")

            plt.tight_layout()
            archivo = os.path.join(self.log_dir, "sustainability_report.png")
            plt.savefig(archivo)
            plt.close()
            return archivo
        except ImportError:
            return None
