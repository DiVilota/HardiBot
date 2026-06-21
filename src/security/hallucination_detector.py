import re
from dataclasses import dataclass


@dataclass
class ResultadoVerificacion:
    es_alucinacion: bool
    confianza: float
    detalle: str = ""


class DetectorAlucinacion:
    def verificar(self, afirmacion: str, contexto: str) -> ResultadoVerificacion:
        afirmacion_lower = afirmacion.lower()
        contexto_lower = contexto.lower()

        afirmaciones = re.split(r'[.;:!?]+', afirmacion_lower)
        afirmaciones = [a.strip() for a in afirmaciones if a.strip()]

        inconsistencias = 0
        total = len(afirmaciones)

        ctx_numeros = re.findall(r'(\d+)\s*(\w+)', contexto_lower)
        ctx_num_map = {valor: numero for numero, valor in ctx_numeros}

        for af in afirmaciones:
            af_palabras = set(re.findall(r'\w+', af))
            if len(af_palabras) < 3:
                continue

            af_numeros = re.findall(r'(\d+)\s*(\w+)', af)
            for numero, valor in af_numeros:
                if valor in ctx_num_map and ctx_num_map[valor] != numero:
                    inconsistencias += 1
                    break

            if not af_numeros:
                numeros_af = set(re.findall(r'\d+', af))
                numeros_ctx = set(re.findall(r'\d+', contexto_lower))
                if numeros_af and not numeros_af.intersection(numeros_ctx):
                    inconsistencias += 1

        if total == 0:
            return ResultadoVerificacion(es_alucinacion=False, confianza=0.99, detalle="sin_afirmaciones_verificables")

        tasa_inconsistencia = inconsistencias / total
        return ResultadoVerificacion(
            es_alucinacion=tasa_inconsistencia > 0.3,
            confianza=round(1.0 - tasa_inconsistencia, 2),
            detalle=f"inconsistencias: {inconsistencias}/{total} afirmaciones",
        )
