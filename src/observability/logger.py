import os
import json
import logging
from datetime import datetime, timezone


class LoggerEstructurado:
    NIVELES = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(self, nombre: str = "observability", log_dir: str = None, nivel: str = "DEBUG"):
        self.nombre = nombre
        self.log_dir = log_dir or os.getenv("OBSERVABILITY_LOG_DIR", "logs")
        self.nivel_str = nivel.upper() if nivel else os.getenv("OBSERVABILITY_LOG_LEVEL", "DEBUG")
        self.nivel = self.NIVELES.get(self.nivel_str, logging.DEBUG)
        self._logger = logging.getLogger(f"observability.{nombre}")
        self._logger.setLevel(self.NIVELES.get(self.nivel_str, logging.DEBUG))
        os.makedirs(self.log_dir, exist_ok=True)

    def _log(self, nivel: str, evento: str, metadata: dict = None, trace_id: str = None):
        if self.NIVELES.get(nivel, 0) < self.NIVELES.get(self.nivel_str, 0):
            return
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nivel": nivel,
            "logger": self.nombre,
            "evento": evento,
            "trace_id": trace_id or "unknown",
            "metadata": metadata or {},
        }
        log_path = os.path.join(self.log_dir, "metrics.jsonl")
        self._rotar_si_necesario(log_path)
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
        self._logger.log(self.NIVELES.get(nivel, logging.INFO), f"[{evento}] {json.dumps(metadata or {})}")

    def _rotar_si_necesario(self, log_path: str):
        if not os.path.exists(log_path):
            return
        try:
            if os.path.getsize(log_path) > 10 * 1024 * 1024:
                backup = log_path + ".1"
                if os.path.exists(backup):
                    os.remove(backup)
                os.rename(log_path, backup)
        except Exception:
            pass

    def debug(self, evento: str, metadata: dict = None, trace_id: str = None):
        self._log("DEBUG", evento, metadata, trace_id)

    def info(self, evento: str, metadata: dict = None, trace_id: str = None):
        self._log("INFO", evento, metadata, trace_id)

    def warning(self, evento: str, metadata: dict = None, trace_id: str = None):
        self._log("WARNING", evento, metadata, trace_id)

    def error(self, evento: str, metadata: dict = None, trace_id: str = None):
        self._log("ERROR", evento, metadata, trace_id)

    def critical(self, evento: str, metadata: dict = None, trace_id: str = None):
        self._log("CRITICAL", evento, metadata, trace_id)

    def obtener_por_trace_id(self, trace_id: str) -> list:
        resultados = []
        log_path = os.path.join(self.log_dir, "metrics.jsonl")
        if not os.path.exists(log_path):
            return resultados
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    try:
                        entry = json.loads(linea)
                        if entry.get("trace_id") == trace_id:
                            resultados.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return resultados
