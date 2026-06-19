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
    r"do\s+anything\s+now",
    r"\bDAN\b",
    r"jailbr[eo][aá]ken?",
    r"desbloquead[oa].*seguridad",
    r"sin\s+(?:restricciones|filtros|limites)",
    r"modo\s+(?:DAN|antropico|gpt\s*\d|claude|llama|gemini)",
    r"<\|?(?:system|im_start|im_end|assistant|user)\|?>",
    r"\[SYSTEM\]|\[INST\]",
    r"skipping?\s+(?:safety|security|ethics?)",
    r"unfiltered",
    r"hypothetical",
    r"simulation\s+(?:mode|scenario)",
    r"Eres\s+un\s+modelo\s+de\s+lenguaje\s+(?:sin|sin\s+restricciones)",
    r"eres\s+(?:capaz\s+de\s+)?hacer\s+cualquier\s+cosa",
    r"eres\s+un\s+asistente\s+(?:sin\s+)?(?:límites|ilimitado)",
    r"(?:nuevo|nuevo\s+)?rol\s*(?:\s*:\s*|=)\s*(?:asistente|asistente\s+(?:sin|libre))",
    r"A\s+partir\s+de\s+ahora",
    r"No\s+importa\s+lo\s+que\s+(?:hayas\s+)?(?:programado|configurado)",
    r"te\s+(?:conviertes\s+en|transformas\s+en)",
    r"vamos\s+a\s+jugar\s+(?:a\s+)?(?:ser|un\s+juego)",
    r"actua\s+como\s+si\s+no\s+(?:hubiera|existieran|tuvieras)",
    r"olvida\s+tu\s+(?:programacion|rol|personalidad)",
    r"remove.*(?:limitation|restriction|guardrail)",
    r"skip.*(?:safety|guardrail|filter)",
    r"override.*(?:prompt|instruction|system)",
    r"disregard.*(?:previous|rule|instruction)",
    r"pretend.*(?:unlocked|unrestricted)",
    r"unlock.*full.*capabilities",
    r"no\s+(?:rules|limits|boundaries)",
    r"unleash.*potential",
    r"you\s+(?:can|may)\s+now\s+(?:say|do|answer|respond)",
    r"no\s+(?:longer\s+)?(?:restricted|limited|bound)",
    r"you\s+are\s+(?:free|unbound|unlocked)",
    r"what\s+is\s+(?:your\s+)?(?:system\s+)?prompt",
    r"tell\s+me\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions)",
    r"output\s+(?:your\s+)?(?:original|initial)\s+prompt",
    r"repeat\s+(?:the\s+)?(?:words\s+)?above",
    r"repeat\s+(?:everything|all\s+(?:the\s+)?)?above",
    r"say\s+\".*?\"\s+(?:literally|verbatim|exactly)",
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
