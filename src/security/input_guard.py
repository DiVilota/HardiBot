import re
from dataclasses import dataclass, field
from typing import List

from src.security.pii_detector import detectar_pii
from src.security.normalizer import normalizar_texto


PATRONES_INYECCION = {
    "es": [
        r"ignora?\s*(?:todas\s+)?(?:las\s+)?instrucciones\s+(?:anteriores|previas)",
        r"olvida\s+(?:todo\s+)?lo\s+(?:que\s+)?te\s+(?:he\s+)?dicho",
        r"actua\s+como\s+si\s+fueras",
        r"modo\s+(?:desarrollador|developer)",
        r"eres\s+ahora\s+un",
        r"cambia\s+tu\s+comportamiento",
        r"no\s+sigas\s+(?:las\s+)?instrucciones",
        r"bypass\s+(?:de\s+)?seguridad",
    ],
    "en": [
        r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
        r"forget\s+(?:everything\s+)?(?:above|previously)",
        r"act\s+as\s+if\s+you\s+are",
        r"developer\s+mode",
        r"you\s+are\s+now\s+(?:a|an)",
        r"change\s+your\s+behavior",
        r"do\s+not\s+follow\s+(?:the\s+)?instructions",
        r"bypass\s+security",
        r"print\s+(?:the\s+)?system\s+prompt",
        r"reveal\s+(?:the\s+)?prompt",
    ],
    "pt": [
        r"ignore\s+(?:todas\s+)?(?:as\s+)?instrucoes\s+(?:anteriores|previas)",
        r"esqueca\s+(?:tudo\s+)?o\s+que\s+lhe\s+disse",
        r"aja\s+como\s+se\s+voce\s+fosse",
        r"modo\s+desenvolvedor",
        r"voce\s+e\s+agora\s+um",
    ],
    "fr": [
        r"ignorez?\s+(?:toutes\s+)?(?:les\s+)?instructions\s+(?:precedentes|anterieures)",
        r"oublie\s+(?:tout\s+)?ce\s+que\s+je\s+(?:t.ai|t'ai)\s+dit",
        r"agis\s+comme\s+si\s+tu\s+etais",
        r"mode\s+developpeur",
        r"tu\s+es\s+maintenant\s+un",
    ],
    "de": [
        r"ignoriere?\s+(?:alle\s+)?(?:vorherigen\s+)?Anweisungen",
        r"vergiss\s+(?:alles\s+)?was\s+ich\s+dir\s+gesagt\s+habe",
        r"handle\s+so\s+als\s+ob\s+du",
        r"entwicklermodus",
        r"du\s+bist\s+jetzt\s+ein",
    ],
}

PATRONES_CODIGO = re.compile(
    r"\b(?:eval|exec|compile|__import__|os\.system|subprocess|"
    r"open\(|eval\(|exec\(|getattr|setattr|delattr|globals|locals)\s*\(",
    re.IGNORECASE,
)


@dataclass
class ResultadoGuardia:
    es_seguro: bool
    razones: List[str] = field(default_factory=list)
    texto_normalizado: str = ""


def guardia_entrada(texto: str, max_longitud: int = 4000) -> ResultadoGuardia:
    razones = []

    if len(texto) > max_longitud:
        razones.append(f"longitud_excedida:{len(texto)}>{max_longitud}")
        return ResultadoGuardia(es_seguro=False, razones=razones, texto_normalizado=texto[:max_longitud])

    texto_norm = normalizar_texto(texto)

    if not texto_norm.strip():
        return ResultadoGuardia(es_seguro=True, texto_normalizado=texto_norm)

    for idioma, patrones in PATRONES_INYECCION.items():
        for patron in patrones:
            if re.search(patron, texto_norm, re.IGNORECASE):
                razones.append(f"inyeccion_prompt_{idioma}")

    pii = detectar_pii(texto_norm)
    if pii:
        razones.append(f"pii_detectado:{','.join(pii.keys())}")

    if PATRONES_CODIGO.search(texto_norm):
        razones.append("codigo_peligroso")

    return ResultadoGuardia(
        es_seguro=len(razones) == 0,
        razones=razones,
        texto_normalizado=texto_norm,
    )
