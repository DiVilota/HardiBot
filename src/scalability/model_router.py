from src.scalability.token_estimator import estimar_tokens, ConfigModelo, MODELOS_DISPONIBLES

NIVEL_RAPIDO = 0
NIVEL_ESTANDAR = 1
NIVEL_AVANZADO = 2

_PALABRAS_CLAVE_AVANZADO = {
    "arquitectura", "estrategia", "multi-paso", "razonamiento",
    "complejo", "profundo", "investiga",
}

_PALABRAS_CLAVE_ESTANDAR = {
    "analiza", "compara", "evalua", "explica", "describe",
    "detalla", "diferencia", "recomienda", "sugiere",
}


def clasificar_complejidad(prompt: str) -> int:
    if not prompt or not prompt.strip():
        return NIVEL_RAPIDO

    tokens = estimar_tokens(prompt)
    prompt_lower = prompt.lower()
    palabras = set(prompt_lower.split())

    if tokens > 100 or palabras & _PALABRAS_CLAVE_AVANZADO:
        return NIVEL_AVANZADO

    if tokens > 30 or palabras & _PALABRAS_CLAVE_ESTANDAR:
        return NIVEL_ESTANDAR

    return NIVEL_RAPIDO


def seleccionar_modelo(prompt: str) -> ConfigModelo:
    nivel = clasificar_complejidad(prompt)
    if nivel == NIVEL_AVANZADO:
        return MODELOS_DISPONIBLES["avanzado"]
    if nivel == NIVEL_ESTANDAR:
        return MODELOS_DISPONIBLES["estandar"]
    return MODELOS_DISPONIBLES["rapido"]
