import os
import json
import uuid
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, List


EN_PROGRESO = "EN_PROGRESO"
EXITOSO = "EXITOSO"
ERROR = "ERROR"


@dataclass
class Span:
    span_id: str
    nombre: str
    trace_id: str
    parent_span_id: Optional[str] = None
    inicio: Optional[float] = None
    fin: Optional[float] = None
    duracion_ms: float = 0.0
    estado: str = EN_PROGRESO
    atributos: dict = field(default_factory=dict)
    error: Optional[str] = None
    timestamp_inicio: Optional[str] = None
    timestamp_fin: Optional[str] = None

    def iniciar(self):
        self.inicio = time.perf_counter()
        self.timestamp_inicio = datetime.now(timezone.utc).isoformat()
        return self

    def finalizar(self, estado: str = EXITOSO, error: str = None):
        self.fin = time.perf_counter()
        self.timestamp_fin = datetime.now(timezone.utc).isoformat()
        self.duracion_ms = round((self.fin - self.inicio) * 1000, 2)
        self.estado = estado
        if error:
            self.error = error
        return self


@dataclass
class Traza:
    trace_id: str
    nombre: str
    spans: List[Span] = field(default_factory=list)
    timestamp_inicio: Optional[str] = None
    timestamp_fin: Optional[str] = None
    duracion_total_ms: float = 0.0
    estado: str = EN_PROGRESO
    metadata: dict = field(default_factory=dict)


class SistemaTrazas:
    def __init__(self, log_dir: str = None):
        self.trazas: List[Traza] = []
        self._traza_activa: Optional[Traza] = None
        self._spans_activos: dict[str, Span] = {}
        self.log_dir = log_dir or os.getenv("OBSERVABILITY_LOG_DIR", "logs")

    def iniciar_traza(self, nombre: str, trace_id: str = None, **metadata) -> Traza:
        if not trace_id:
            trace_id = str(uuid.uuid4())[:8]
        traza = Traza(
            trace_id=trace_id,
            nombre=nombre,
            timestamp_inicio=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
        self.trazas.append(traza)
        self._traza_activa = traza
        return traza

    def iniciar_span(self, nombre: str, parent_span_id: str = None, **atributos) -> Span:
        if not self._traza_activa:
            raise RuntimeError("No hay traza activa. Llama a iniciar_traza() primero.")
        span = Span(
            span_id=str(uuid.uuid4())[:8],
            nombre=nombre,
            trace_id=self._traza_activa.trace_id,
            parent_span_id=parent_span_id,
            atributos=atributos,
        )
        span.iniciar()
        self._traza_activa.spans.append(span)
        self._spans_activos[span.span_id] = span
        return span

    def finalizar_span(self, span: Span, estado: str = EXITOSO, error: str = None, **atributos_extra):
        span.finalizar(estado=estado, error=error)
        span.atributos.update(atributos_extra)
        self._spans_activos.pop(span.span_id, None)

    def finalizar_traza(self, estado: str = EXITOSO):
        if not self._traza_activa:
            return
        self._traza_activa.timestamp_fin = datetime.now(timezone.utc).isoformat()
        duracion_total = sum(
            s.duracion_ms for s in self._traza_activa.spans if s.parent_span_id is None
        )
        self._traza_activa.duracion_total_ms = round(duracion_total, 2)
        self._traza_activa.estado = estado
        self._traza_activa = None

    def obtener_traza(self, trace_id: str) -> Optional[Traza]:
        for traza in self.trazas:
            if traza.trace_id == trace_id:
                return traza
        return None

    def arbol_spans(self, trace_id: str) -> dict:
        traza = self.obtener_traza(trace_id)
        if not traza:
            return {}
        return self._construir_arbol(traza)

    def _construir_arbol(self, traza: Traza) -> dict:
        span_map = {s.span_id: s for s in traza.spans}
        hijos = {}
        for s in traza.spans:
            parent = s.parent_span_id or "__root__"
            hijos.setdefault(parent, []).append(s.span_id)

        def _nodo(span_id: str) -> dict:
            span = span_map.get(span_id)
            if not span:
                return {}
            return {
                "span_id": span.span_id,
                "nombre": span.nombre,
                "duracion_ms": span.duracion_ms,
                "estado": span.estado,
                "error": span.error,
                "hijos": [_nodo(hid) for hid in hijos.get(span_id, [])],
            }

        raices = [s for s in traza.spans if s.parent_span_id is None]
        return {
            "trace_id": traza.trace_id,
            "nombre": traza.nombre,
            "duracion_total_ms": traza.duracion_total_ms,
            "estado": traza.estado,
            "hijos": [_nodo(s.span_id) for s in raices],
        }

    def cascada_temporal(self, trace_id: str) -> list:
        traza = self.obtener_traza(trace_id)
        if not traza:
            return []
        spans_ordenados = sorted(
            traza.spans,
            key=lambda s: (s.inicio or 0, -(s.duracion_ms or 0)),
        )
        resultado = []
        for s in spans_ordenados:
            nivel = 0
            pid = s.parent_span_id
            while pid:
                nivel += 1
                padre = next((x for x in traza.spans if x.span_id == pid), None)
                pid = padre.parent_span_id if padre else None
            resultado.append({
                "span_id": s.span_id,
                "nombre": s.nombre,
                "parent_span_id": s.parent_span_id,
                "nivel": nivel,
                "inicio_offset_ms": round(((s.inicio or 0) - (traza.spans[0].inicio or 0)) * 1000, 2) if s.inicio else 0,
                "duracion_ms": s.duracion_ms,
                "estado": s.estado,
            })
        return resultado

    def guardar(self, traza: Traza = None):
        if traza is None:
            if not self.trazas:
                return
            traza = self.trazas[-1]
        os.makedirs(self.log_dir, exist_ok=True)
        path = os.path.join(self.log_dir, "trazas.jsonl")
        self._rotar_si_necesario(path)
        entry = {
            "trace_id": traza.trace_id,
            "nombre": traza.nombre,
            "timestamp_inicio": traza.timestamp_inicio,
            "timestamp_fin": traza.timestamp_fin,
            "duracion_total_ms": traza.duracion_total_ms,
            "estado": traza.estado,
            "metadata": traza.metadata,
            "spans": [
                {
                    "span_id": s.span_id,
                    "nombre": s.nombre,
                    "trace_id": s.trace_id,
                    "parent_span_id": s.parent_span_id,
                    "duracion_ms": s.duracion_ms,
                    "estado": s.estado,
                    "atributos": s.atributos,
                    "error": s.error,
                    "timestamp_inicio": s.timestamp_inicio,
                    "timestamp_fin": s.timestamp_fin,
                }
                for s in traza.spans
            ],
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _rotar_si_necesario(self, path: str):
        if not os.path.exists(path):
            return
        try:
            if os.path.getsize(path) > 10 * 1024 * 1024:
                backup = path + ".1"
                if os.path.exists(backup):
                    os.remove(backup)
                os.rename(path, backup)
        except Exception:
            pass

    @staticmethod
    def cargar_trazas(log_dir: str = None) -> List[dict]:
        dir_path = log_dir or os.getenv("OBSERVABILITY_LOG_DIR", "logs")
        path = os.path.join(dir_path, "trazas.jsonl")
        if not os.path.exists(path):
            return []
        trazas = []
        with open(path, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    trazas.append(json.loads(linea))
                except json.JSONDecodeError:
                    continue
        return trazas
