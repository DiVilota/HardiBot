import re
import unicodedata


MAPA_LEETSPEAK = {
    "0": "o", "1": "i", "2": "z", "3": "e", "4": "a",
    "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
    "$": "s", "!": "i", "+": "t",
}


def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFC", texto)
    texto = unicodedata.normalize("NFKC", texto)
    texto = re.sub(r"[\u200B-\u200D\uFEFF]", "", texto)
    texto = _normalizar_leetspeak(texto)
    texto = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", texto)
    return texto.strip()


def _normalizar_leetspeak(texto: str) -> str:
    resultado = []
    for char in texto:
        resultado.append(MAPA_LEETSPEAK.get(char, char))
    return "".join(resultado)
