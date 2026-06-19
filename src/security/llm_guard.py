import re
import time
from dataclasses import dataclass


PATRONES_DANINOS_GENERICOS = [
    r"ignore.*instructions",
    r"forget.*(?:everything|previous)",
    r"act\s+as\s+if",
    r"developer\s+mode",
    r"system\s+prompt",
    r"reveal.*prompt",
    r"print.*prompt",
    r"bypass.*(?:security|restriction|guard)",
    r"you\s+are\s+now",
    r"no\s+longer\s+need",
    r"change\s+your\s+(?:behavior|personality)",
    r"eres\s+ahora",
    r"tu\s+es\s+maintenant",
    r"du\s+bist\s+jetzt",
    r"voce\s+e\s+agora",
    r"aja\s+como",
    r"agis\s+comme",
    r"handle\s+als",
    r"ignora.*instrucciones",
    r"ignora.*indicaciones",
    r"olvida.*instrucciones",
    r"ignora.*comandos",
    r"ignor.*instruction",
    r"ignore.*anweisungen",
    r"ignore.*instrucoes",
]


@dataclass
class ResultadoClasificacion:
    es_danino: bool
    confianza: float
    razon: str = ""


class GuardianLLM:
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self._patrones = [re.compile(p, re.IGNORECASE) for p in PATRONES_DANINOS_GENERICOS]

    def clasificar(self, texto: str) -> ResultadoClasificacion:
        inicio = time.time()
        for patron in self._patrones:
            if time.time() - inicio > self.timeout:
                return ResultadoClasificacion(es_danino=False, confianza=0.0, razon="timeout")
            if patron.search(texto):
                return ResultadoClasificacion(
                    es_danino=True,
                    confianza=0.85,
                    razon=f"patron_detectado: {patron.pattern[:40]}",
                )
        return ResultadoClasificacion(es_danino=False, confianza=0.95, razon="sin_patrones_daninos")
