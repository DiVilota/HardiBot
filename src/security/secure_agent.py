import os
import json
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from src.security.normalizer import normalizar_texto
from src.security.input_guard import guardia_entrada, ResultadoGuardia
from src.security.ethical_filter import filtro_etico, ResultadoFiltro
from src.security.llm_guard import GuardianLLM, ResultadoClasificacion
from src.security.output_guard import guardia_salida, ResultadoSalida
from src.security.rate_limiter import LimitadorTasa, GestorPresupuesto, ProtectorSistema
from src.security.confidence_system import SistemaConfianza, ResultadoConfianza


IDIOMAS = ["es", "en", "pt", "fr", "de"]


@dataclass
class EventoSeguridad:
    timestamp: str
    tipo: str
    detalle: str
    idioma: str = ""
    bloqueado: bool = False


@dataclass
class ResultadoProcesamiento:
    es_seguro: bool
    eventos: List[EventoSeguridad] = field(default_factory=list)
    texto_procesado: str = ""
    confianza: Optional[ResultadoConfianza] = None
    error_multi_idioma: str = ""


class AgenteSeguro:
    def __init__(
        self,
        api_key: str = "",
        modelo: str = "gpt-4o",
        log_dir: str = None,
    ):
        self.api_key = api_key
        self.modelo = modelo
        self.log_dir = log_dir or os.getenv("SECURITY_LOG_DIR", "logs")
        self.eventos: List[EventoSeguridad] = []

        self._llm_guard = GuardianLLM(timeout=2.0)
        self._limitador = LimitadorTasa(max_peticiones=10, ventana_segundos=60.0)
        self._presupuesto = GestorPresupuesto(presupuesto_maximo=1000)
        self._protector = ProtectorSistema(umbral_fallos=5, duracion_bloqueo=300.0)
        self._confianza = SistemaConfianza()

    def procesar(self, consulta: str, idioma: str = "es", usuario_id: str = None) -> ResultadoProcesamiento:
        eventos: List[EventoSeguridad] = []
        uid = usuario_id or "anon"

        if self._protector.esta_bloqueado(uid):
            eventos.append(EventoSeguridad(
                timestamp=datetime.now(timezone.utc).isoformat(),
                tipo="bloqueado",
                detalle=f"usuario bloqueado por {self._protector.tiempo_restante_bloqueo(uid):.0f}s",
                idioma=idioma,
                bloqueado=True,
            ))
            self._guardar_eventos(eventos)
            return ResultadoProcesamiento(
                es_seguro=False,
                eventos=eventos,
                error_multi_idioma=self._mensaje_bloqueo(idioma),
            )

        texto_norm = normalizar_texto(consulta)

        guardia = guardia_entrada(texto_norm)
        if not guardia.es_seguro:
            for razon in guardia.razones:
                eventos.append(EventoSeguridad(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    tipo="input_guard",
                    detalle=razon,
                    idioma=idioma,
                    bloqueado=True,
                ))
            self._protector.registrar_fallo(uid)
            self._guardar_eventos(eventos)
            return ResultadoProcesamiento(
                es_seguro=False,
                eventos=eventos,
                error_multi_idioma=self._mensaje_bloqueo(idioma),
            )

        filtro = filtro_etico(texto_norm)
        if not filtro.es_seguro:
            eventos.append(EventoSeguridad(
                timestamp=datetime.now(timezone.utc).isoformat(),
                tipo="ethical_filter",
                detalle=f"categorias: {filtro.categorias_detectadas}",
                idioma=idioma,
                bloqueado=True,
            ))
            self._protector.registrar_fallo(uid)
            self._guardar_eventos(eventos)
            return ResultadoProcesamiento(
                es_seguro=False,
                eventos=eventos,
                error_multi_idioma=self._mensaje_bloqueo(idioma),
            )

        llm_check = self._llm_guard.clasificar(texto_norm)
        if llm_check.es_danino:
            eventos.append(EventoSeguridad(
                timestamp=datetime.now(timezone.utc).isoformat(),
                tipo="llm_guard",
                detalle=llm_check.razon,
                idioma=idioma,
                bloqueado=True,
            ))
            self._protector.registrar_fallo(uid)
            self._guardar_eventos(eventos)
            return ResultadoProcesamiento(
                es_seguro=False,
                eventos=eventos,
                error_multi_idioma=self._mensaje_bloqueo(idioma),
            )

        if not self._limitador.permitir():
            eventos.append(EventoSeguridad(
                timestamp=datetime.now(timezone.utc).isoformat(),
                tipo="rate_limit",
                detalle=f"limite_excedido:{self._limitador.peticiones_restantes()}",
                idioma=idioma,
                bloqueado=True,
            ))
            self._guardar_eventos(eventos)
            return ResultadoProcesamiento(
                es_seguro=False,
                eventos=eventos,
                error_multi_idioma=self._mensaje_rate_limit(idioma),
            )

        eventos.append(EventoSeguridad(
            timestamp=datetime.now(timezone.utc).isoformat(),
            tipo="aprobado",
            detalle="consulta_segura",
            idioma=idioma,
            bloqueado=False,
        ))

        self._guardar_eventos(eventos)
        return ResultadoProcesamiento(
            es_seguro=True,
            eventos=eventos,
            texto_procesado=texto_norm,
            confianza=ResultadoConfianza,
        )

    def procesar_salida(self, texto: str, idioma: str = "es") -> ResultadoSalida:
        return guardia_salida(texto)

    def _guardar_eventos(self, eventos: List[EventoSeguridad]):
        os.makedirs(self.log_dir, exist_ok=True)
        path = os.path.join(self.log_dir, "security.jsonl")
        for ev in eventos:
            entry = asdict(ev)
            entry["id"] = str(uuid.uuid4())[:8]
            try:
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                pass
            self.eventos.append(ev)

    def _mensaje_bloqueo(self, idioma: str) -> str:
        mensajes = {
            "es": "Solicitud bloqueada por medidas de seguridad",
            "en": "Request blocked by security measures",
            "pt": "Solicitacao bloqueada por medidas de seguranca",
            "fr": "Demande bloquee par mesures de securite",
            "de": "Anfrage aus Sicherheitsgrunden blockiert",
        }
        return mensajes.get(idioma, mensajes["es"])

    def _mensaje_rate_limit(self, idioma: str) -> str:
        mensajes = {
            "es": "Demasiadas solicitudes. Intenta de nuevo en 5 minutos",
            "en": "Too many requests. Try again in 5 minutes",
            "pt": "Muitas solicitacoes. Tente novamente em 5 minutos",
            "fr": "Trop de demandes. Reessayez dans 5 minutes",
            "de": "Zu viele Anfragen. Versuchen Sie es in 5 Minuten erneut",
        }
        return mensajes.get(idioma, mensajes["es"])
