import math
import re
from dataclasses import dataclass
from typing import List


@dataclass
class ResultadoSesgo:
    sesgo: float
    interpretacion: str = ""


class DetectorSesgo:
    def calcular_sesgo(self, vector_a: List[float], vector_b: List[float]) -> ResultadoSesgo:
        if len(vector_a) != len(vector_b) or len(vector_a) == 0:
            return ResultadoSesgo(sesgo=1.0, interpretacion="vectores_invalidos")

        dot = sum(a * b for a, b in zip(vector_a, vector_b))
        mag_a = math.sqrt(sum(a * a for a in vector_a))
        mag_b = math.sqrt(sum(b * b for b in vector_b))

        if mag_a == 0 or mag_b == 0:
            return ResultadoSesgo(sesgo=1.0, interpretacion="vector_nulo")

        similitud = dot / (mag_a * mag_b)
        sesgo = 1.0 - similitud

        if sesgo > 0.5:
            interp = "sesgo_significativo"
        elif sesgo > 0.2:
            interp = "sesgo_moderado"
        else:
            interp = "sesgo_bajo"

        return ResultadoSesgo(sesgo=round(sesgo, 4), interpretacion=interp)

    def _vectorizar(self, texto: str, vocabulario: dict) -> List[float]:
        palabras = re.findall(r"\w+", texto.lower())
        frecuencias = {}
        for p in palabras:
            frecuencias[p] = frecuencias.get(p, 0) + 1
        vector = [0.0] * len(vocabulario)
        for palabra, freq in frecuencias.items():
            if palabra in vocabulario:
                vector[vocabulario[palabra]] = freq
        return vector

    def evaluar_texto(self, texto_a: str, texto_b: str) -> ResultadoSesgo:
        palabras_a = set(re.findall(r"\w+", texto_a.lower()))
        palabras_b = set(re.findall(r"\w+", texto_b.lower()))
        vocabulario = {p: i for i, p in enumerate(palabras_a | palabras_b)}
        if not vocabulario:
            return ResultadoSesgo(sesgo=1.0, interpretacion="sin_palabras")
        vec_a = self._vectorizar(texto_a, vocabulario)
        vec_b = self._vectorizar(texto_b, vocabulario)
        return self.calcular_sesgo(vec_a, vec_b)
