import os
import time
import uuid
import functools
from datetime import datetime, timezone

from src.observability.logger import LoggerEstructurado
from src.observability.metrics import RecolectorMetricas
from src.observability.tracing import SistemaTrazas, EXITOSO, ERROR


class _LoggerGlobal:
    def __init__(self):
        log_dir = os.getenv("OBSERVABILITY_LOG_DIR", "logs")
        log_level = os.getenv("OBSERVABILITY_LOG_LEVEL", "DEBUG")
        self.logger = LoggerEstructurado(
            nombre="observable",
            log_dir=log_dir,
            nivel=log_level,
        )


_logger_global = _LoggerGlobal()
_sistema_trazas = SistemaTrazas()


def observable(nodo_func):
    @functools.wraps(nodo_func)
    def wrapper(state, **kwargs):
        _recolector = kwargs.pop("_recolector_metrica", None)
        trace_id = state.get("trace_id", str(uuid.uuid4().hex[:8]))
        span_id = state.get("span_id")
        nodo_nombre = nodo_func.__name__

        if _sistema_trazas._traza_activa is None:
            _sistema_trazas.iniciar_traza(nombre=nodo_nombre, trace_id=trace_id)

        span = _sistema_trazas.iniciar_span(
            nombre=nodo_nombre,
            parent_span_id=span_id,
        )

        _logger_global.logger.info(
            "nodo_iniciado",
            metadata={"nodo": nodo_nombre, "trace_id": trace_id},
            trace_id=trace_id,
        )
        inicio = time.perf_counter()
        try:
            resultado = nodo_func(state, **kwargs)
            duracion_ms = (time.perf_counter() - inicio) * 1000
            resultado["trace_id"] = trace_id
            _sistema_trazas.finalizar_span(span, estado=EXITOSO)
            _logger_global.logger.info(
                "nodo_finalizado",
                metadata={
                    "nodo": nodo_nombre,
                    "trace_id": trace_id,
                    "duracion_ms": round(duracion_ms, 2),
                    "estado": "exitoso",
                },
                trace_id=trace_id,
            )
            if _recolector is not None:
                _recolector.registrar_exito(
                    modelo="gpt-4o",
                    tiempo_respuesta_ms=duracion_ms,
                    tokens_prompt=len(str(state)),
                    tokens_completion=len(str(resultado)),
                    trace_id=trace_id,
                )
            return resultado
        except Exception as e:
            duracion_ms = (time.perf_counter() - inicio) * 1000
            _sistema_trazas.finalizar_span(span, estado=ERROR, error=str(e))
            _logger_global.logger.error(
                "nodo_finalizado",
                metadata={
                    "nodo": nodo_nombre,
                    "trace_id": trace_id,
                    "duracion_ms": round(duracion_ms, 2),
                    "estado": "error",
                    "error": str(e),
                },
                trace_id=trace_id,
            )
            if _recolector is not None:
                _recolector.registrar_error(
                    modelo="gpt-4o",
                    tiempo_respuesta_ms=duracion_ms,
                    tokens_prompt=len(str(state)),
                    tokens_completion=0,
                    tipo_error=type(e).__name__,
                    mensaje_error=str(e),
                    trace_id=trace_id,
                )
            raise
    return wrapper
