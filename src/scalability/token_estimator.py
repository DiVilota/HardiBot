from dataclasses import dataclass


@dataclass
class ConfigModelo:
    nombre: str
    costo_por_1k: float
    latencia: float
    capacidad_max: int


MODELOS_DISPONIBLES = {
    "rapido": ConfigModelo("gpt-4o-mini", costo_por_1k=0.15, latencia=0.5, capacidad_max=16384),
    "estandar": ConfigModelo("gpt-4o", costo_por_1k=5.0, latencia=1.5, capacidad_max=8192),
    "avanzado": ConfigModelo("o1", costo_por_1k=15.0, latencia=5.0, capacidad_max=32768),
}


def estimar_tokens(texto: str) -> int:
    if not texto:
        return 0
    return max(1, len(texto) // 4)
