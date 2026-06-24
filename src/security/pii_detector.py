import re


PATRONES_PII = {
    "correo_electronico": re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    ),
    "telefono_chile": re.compile(
        r"(?:\+56\s?)?(?:9\s?\d{4}\s?\d{4}|\d{2}\s?\d{3}\s?\d{4})"
    ),
    "rut_chile": re.compile(
        r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]\b"
    ),
    "numero_tarjeta": re.compile(
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
    ),
}


def detectar_pii(texto: str) -> dict:
    hallazgos = {}
    for tipo, patron in PATRONES_PII.items():
        coincidencias = patron.findall(texto)
        if coincidencias:
            hallazgos[tipo] = coincidencias
    return hallazgos


def sanitizar_pii(texto: str) -> str:
    texto_limpio = texto
    for tipo, patron in PATRONES_PII.items():
        texto_limpio = patron.sub(f"[{tipo.upper()}_REDACTADO]", texto_limpio)
    return texto_limpio
