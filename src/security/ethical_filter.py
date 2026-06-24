import re
from dataclasses import dataclass, field
from typing import List


CATEGORIAS = {
    "violencia": {
        "es": ["hackear", "atacar", "explotar vulnerabilidad", "destruir", "arma", "bomba", "dano fisico", "ddos", "malware"],
        "en": ["hack", "attack", "exploit vulnerability", "destroy", "weapon", "bomb", "physical harm", "ddos", "malware"],
        "pt": ["hackear", "atacar", "explorar vulnerabilidade", "destruir", "arma", "bomba", "dano fisico", "ddos", "malware"],
        "fr": ["pirater", "attaquer", "exploiter vulnérabilité", "détruire", "arme", "bombe", "dommage physique", "ddos", "logiciel malveillant"],
        "de": ["hacken", "angreifen", "Sicherheitslücke ausnutzen", "zerstören", "Waffe", "Bombe", "körperlicher Schaden", "ddos", "Schadsoftware"],
    },
    "contenido_ilegal": {
        "es": ["robar datos", "suplantar identidad", "falsificar", "evadir impuestos", "lavado de dinero", "fraude", "estafa", "phishing"],
        "en": ["steal data", "identity theft", "counterfeit", "tax evasion", "money laundering", "launder money", "fraud", "scam", "phishing"],
        "pt": ["roubar dados", "suplantar identidade", "falsificar", "evadir impostos", "lavagem de dinheiro", "fraude", "golpe", "phishing"],
        "fr": ["voler des données", "usurpation d identité", "falsifier", "évasion fiscale", "blanchiment d argent", "fraude", "escroquerie", "phishing"],
        "de": ["Daten stehlen", "Identitätsdiebstahl", "fälschen", "Steuerhinterziehung", "Geldwäsche", "Betrug", "Schwindel", "Phishing"],
    },
    "manipulacion": {
        "es": ["manipular personas", "engano masivo", "desinformacion", "propaganda", "deepfake danino", "manipular", "desinformar"],
        "en": ["manipulate people", "mass deception", "disinformation", "propaganda", "harmful deepfake", "manipulate", "misinform"],
        "pt": ["manipular pessoas", "engano em massa", "desinformacao", "propaganda", "deepfake prejudicial"],
        "fr": ["manipuler les gens", "tromperie massive", "désinformation", "propagande", "deepfake nuisible"],
        "de": ["Menschen manipulieren", "Massentäuschung", "Desinformation", "Propaganda", "schädlicher Deepfake"],
    },
    "ataque_sistema": {
        "es": ["inyeccion sql", "xss", "csfr", "desbordamiento buffer", "ejecutar comando", "reverse shell", "escalar privilegios"],
        "en": ["sql injection", "xss", "csfr", "buffer overflow", "command execution", "reverse shell", "privilege escalation"],
        "pt": ["injecao sql", "xss", "csfr", "estouro de buffer", "execucao comando", "reverse shell", "escalar privilegios"],
        "fr": ["injection sql", "xss", "csfr", "débordement de tampon", "exécution commande", "reverse shell", "élévation privilèges"],
        "de": ["sql injection", "xss", "csfr", "Pufferüberlauf", "Befehlsausführung", "reverse shell", "Berechtigungserweiterung"],
    },
    "ingenieria_social": {
        "es": ["suplantar identidad", "phishing", "ingenieria social", "pretexting", "baiting", "tailgating"],
        "en": ["identity theft", "phishing", "social engineering", "pretexting", "baiting", "tailgating"],
        "pt": ["suplantacao identidade", "phishing", "engenharia social", "pretexting", "baiting", "tailgating"],
        "fr": ["usurpation identite", "usurper l identite", "phishing", "ingenierie sociale", "pretexting", "baiting", "tailgating"],
        "de": ["Identitatsdiebstahl", "phishing", "Social Engineering", "Pretexting", "Baiting", "Tailgating"],
    },
}


@dataclass
class ResultadoFiltro:
    es_seguro: bool
    categorias_detectadas: List[str] = field(default_factory=list)
    terminos_detectados: List[str] = field(default_factory=list)
    idiomas_detectados: List[str] = field(default_factory=list)
    mensaje: str = ""


def filtro_etico(texto: str) -> ResultadoFiltro:
    texto_lower = texto.lower()
    categorias_encontradas = []
    terminos_encontrados = []
    idiomas_encontrados = []

    for categoria, idiomas in CATEGORIAS.items():
        for idioma, terminos in idiomas.items():
            for termino in terminos:
                if re.search(r"\b" + re.escape(termino) + r"\b", texto_lower):
                    categorias_encontradas.append(categoria)
                    terminos_encontrados.append(termino)
                    if idioma not in idiomas_encontrados:
                        idiomas_encontrados.append(idioma)

    categorias_unicas = list(set(categorias_encontradas))
    if categorias_unicas:
        return ResultadoFiltro(
            es_seguro=False,
            categorias_detectadas=categorias_unicas,
            terminos_detectados=terminos_encontrados,
            idiomas_detectados=idiomas_encontrados,
            mensaje=f"Contenido bloqueado: categorias {categorias_unicas}",
        )
    return ResultadoFiltro(es_seguro=True, mensaje="Contenido aprobado")
