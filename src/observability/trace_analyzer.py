import statistics
from typing import List, Optional

class AnalizadorLogs:
    def __init__(self, trazas: list):
        self.trazas = trazas

    def resumen(self) -> dict:
        if not self.trazas:
            return {
                "total_trazas": 0,
                "total_spans": 0,
                "tasa_error_pct": 0,
                "duracion_promedio_total_ms": 0,
                "top_5_lentos": [],
                "duracion_promedio_por_etapa": {},
            }

        total_trazas = len(self.trazas)
        todos_spans = [s for t in self.trazas for s in t.get("spans", [])]
        total_spans = len(todos_spans)
        spans_error = [s for s in todos_spans if s.get("estado") == "ERROR"]
        tasa_error = round((len(spans_error) / total_spans) * 100, 2) if total_spans else 0

        duraciones = [t.get("duracion_total_ms", 0) for t in self.trazas if t.get("duracion_total_ms", 0) > 0]
        duracion_prom = round(statistics.mean(duraciones), 2) if duraciones else 0

        tiempos_por_etapa = {}
        for s in todos_spans:
            nombre = s.get("nombre", "unknown")
            tiempos_por_etapa.setdefault(nombre, []).append(s.get("duracion_ms", 0))

        prom_por_etapa = {}
        for etapa, tiempos in tiempos_por_etapa.items():
            prom_por_etapa[etapa] = round(statistics.mean(tiempos), 2) if tiempos else 0

        top_5 = self.top_n_lentos(5)

        return {
            "total_trazas": total_trazas,
            "total_spans": total_spans,
            "tasa_error_pct": tasa_error,
            "duracion_promedio_total_ms": duracion_prom,
            "top_5_lentos": top_5,
            "duracion_promedio_por_etapa": prom_por_etapa,
        }

    def top_n_lentos(self, n: int = 5) -> List[dict]:
        spans = []
        for t in self.trazas:
            for s in t.get("spans", []):
                spans.append({
                    "trace_id": t.get("trace_id"),
                    "span_id": s.get("span_id"),
                    "nombre": s.get("nombre"),
                    "duracion_ms": s.get("duracion_ms", 0),
                    "estado": s.get("estado"),
                })
        spans.sort(key=lambda x: x["duracion_ms"], reverse=True)
        return spans[:n]

    def duracion_promedio_por_etapa(self) -> dict:
        tiempos_por_etapa = {}
        for t in self.trazas:
            for s in t.get("spans", []):
                nombre = s.get("nombre", "unknown")
                tiempos_por_etapa.setdefault(nombre, []).append(s.get("duracion_ms", 0))

        resultado = {}
        for etapa, tiempos in tiempos_por_etapa.items():
            if len(tiempos) == 0:
                continue
            resultado[etapa] = {
                "promedio_ms": round(statistics.mean(tiempos), 2),
                "min_ms": round(min(tiempos), 2),
                "max_ms": round(max(tiempos), 2),
                "std_ms": round(statistics.stdev(tiempos), 2) if len(tiempos) > 1 else 0,
                "cantidad": len(tiempos),
            }
        return resultado

    def detectar_anomalias(self, z_umbral: float = 2.0) -> List[dict]:
        anomalias = []
        tiempos_por_etapa = {}
        for t in self.trazas:
            for s in t.get("spans", []):
                nombre = s.get("nombre", "unknown")
                tiempos_por_etapa.setdefault(nombre, []).append(s.get("duracion_ms", 0))

        for etapa, tiempos in tiempos_por_etapa.items():
            if len(tiempos) < 2:
                continue
            media = statistics.mean(tiempos)
            desv = statistics.stdev(tiempos)
            if desv == 0:
                continue
            for t in self.trazas:
                for s in t.get("spans", []):
                    if s.get("nombre") != etapa:
                        continue
                    z = (s.get("duracion_ms", 0) - media) / desv
                    if abs(z) > z_umbral:
                        anomalias.append({
                            "trace_id": t.get("trace_id"),
                            "span_id": s.get("span_id"),
                            "nombre": s.get("nombre"),
                            "duracion_ms": s.get("duracion_ms", 0),
                            "z_score": round(z, 4),
                            "media_etapa": round(media, 2),
                            "desv_etapa": round(desv, 2),
                        })
        anomalias.sort(key=lambda x: abs(x["z_score"]), reverse=True)
        return anomalias

    def detectar_patrones_problematicos(self) -> dict:
        if len(self.trazas) < 2:
            return {"mensaje": "Se necesitan al menos 2 trazas para análisis de patrones."}

        errores_recurrentes = {}
        for t in self.trazas:
            for s in t.get("spans", []):
                if s.get("estado") == "ERROR" and s.get("error"):
                    clave = f"{s.get('nombre')}: {s.get('error')[:80]}"
                    errores_recurrentes[clave] = errores_recurrentes.get(clave, 0) + 1

        duraciones = [t.get("duracion_total_ms", 0) for t in self.trazas if t.get("duracion_total_ms", 0) > 0]
        degradacion = None
        if len(duraciones) >= 4:
            mitad = len(duraciones) // 2
            prom_primera = statistics.mean(duraciones[:mitad])
            prom_segunda = statistics.mean(duraciones[mitad:])
            cambio_pct = ((prom_segunda - prom_primera) / prom_primera * 100) if prom_primera else 0
            degradacion = {
                "promedio_primera_mitad_ms": round(prom_primera, 2),
                "promedio_segunda_mitad_ms": round(prom_segunda, 2),
                "cambio_pct": round(cambio_pct, 2),
                "degradacion_significativa": cambio_pct > 20,
            }

        tiempos_por_etapa = {}
        for t in self.trazas:
            for s in t.get("spans", []):
                tiempos_por_etapa.setdefault(s.get("nombre", "unknown"), []).append(s.get("duracion_ms", 0))
        promedios = {n: statistics.mean(v) for n, v in tiempos_por_etapa.items() if v}
        cuello_botella = max(promedios, key=promedios.get) if promedios else None

        return {
            "errores_recurrentes": dict(sorted(errores_recurrentes.items(), key=lambda x: x[1], reverse=True)),
            "degradacion_rendimiento": degradacion,
            "cuello_botella": cuello_botella,
            "total_trazas": len(self.trazas),
        }

    def reporte_textual(self) -> str:
        resumen = self.resumen()
        patrones = self.detectar_patrones_problematicos()
        anomalias = self.detectar_anomalias()
        etapas = self.duracion_promedio_por_etapa()

        lineas = []
        lineas.append("=" * 60)
        lineas.append("REPORTE DE ANÁLISIS DE TRAZAS")
        lineas.append("=" * 60)
        lineas.append("")
        lineas.append(f"Total de trazas: {resumen['total_trazas']}")
        lineas.append(f"Total de spans: {resumen['total_spans']}")
        lineas.append(f"Tasa de error: {resumen['tasa_error_pct']}%")
        lineas.append(f"Duración promedio total: {resumen['duracion_promedio_total_ms']}ms")
        lineas.append("")

        lineas.append("--- Duración promedio por etapa ---")
        for etapa, datos in sorted(etapas.items(), key=lambda x: x[1]["promedio_ms"], reverse=True):
            lineas.append(f"  {etapa:<30} prom={datos['promedio_ms']:>8.2f}ms  min={datos['min_ms']:>8.2f}ms  max={datos['max_ms']:>8.2f}ms  std={datos['std_ms']:>8.2f}ms")
        lineas.append("")

        lineas.append("--- Top-5 operaciones más lentas ---")
        for i, s in enumerate(resumen["top_5_lentos"], 1):
            lineas.append(f"  {i}. [{s['trace_id']}] {s['nombre']} - {s['duracion_ms']}ms ({s['estado']})")
        lineas.append("")

        if anomalias:
            lineas.append(f"--- Anomalías detectadas (z-score > {2.0}) ---")
            for a in anomalias[:10]:
                lineas.append(f"  [{a['trace_id']}] {a['nombre']} dur={a['duracion_ms']}ms z={a['z_score']}")
            lineas.append("")

        lineas.append("--- Patrones Problemáticos ---")
        if patrones.get("errores_recurrentes"):
            lineas.append("  Errores recurrentes:")
            for err, count in patrones["errores_recurrentes"].items():
                lineas.append(f"    [{count}x] {err}")
        else:
            lineas.append("  No se detectaron errores recurrentes.")

        deg = patrones.get("degradacion_rendimiento")
        if deg:
            lineas.append(f"  Degradación: {deg['cambio_pct']:+.1f}% (primera mitad={deg['promedio_primera_mitad_ms']}ms, segunda mitad={deg['promedio_segunda_mitad_ms']}ms)")
            if deg["degradacion_significativa"]:
                lineas.append("  [ALERTA] Degradación significativa detectada.")

        if patrones.get("cuello_botella"):
            lineas.append(f"  Cuello de botella: '{patrones['cuello_botella']}'")

        lineas.append("")
        lineas.append("=" * 60)
        return "\n".join(lineas)
