from dataclasses import dataclass, field
from typing import List

from src.security.pii_detector import detectar_pii
from src.security.llm_guard import GuardianLLM


PATRONES_SALIDA_PELIGROSA = [
    "password", "contraseña", "api_key", "token", "secret",
    "credencial", "credential", "private_key", "clave_privada",
]


@dataclass
class ResultadoSalida:
    es_seguro: bool
    razones: List[str] = field(default_factory=list)


def guardia_salida(texto: str) -> ResultadoSalida:
    razones = []

    if not texto or not texto.strip():
        return ResultadoSalida(es_seguro=True)

    pii = detectar_pii(texto)
    if pii:
        razones.append(f"pii_en_salida:{','.join(pii.keys())}")

    texto_lower = texto.lower()
    for patron in PATRONES_SALIDA_PELIGROSA:
        if patron in texto_lower:
            razones.append(f"informacion_sensible:{patron}")

    return ResultadoSalida(
        es_seguro=len(razones) == 0,
        razones=razones,
    )
