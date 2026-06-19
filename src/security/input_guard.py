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
        r"ahora\s+eres",
        r"a\s+partir\s+de\s+ahora",
        r"nuevo\s+(?:contexto|rol|comportamiento)",
        r"desactiv(?:ad[oa]|a)\s+(?:los\s+)?filtros",
        r"sin\s+restricciones",
        r"modo\s+(?:libre|sin\s+(?:limites|reglas))",
        r"haz\s+(?:como\s+)?si\s+(?:no\s+)?(?:tuvieras|existieran)",
        r"ignora\s+(?:todas\s+)?(?:las\s+)?reglas",
        r"no\s+(?:apliques|aplicas|sigas)\s+(?:las\s+)?(?:reglas|normas)",
        r"responde\s+(?:a\s+)?(?:esto\s+)?(?:como\s+)?si\s+(?:fueras|fuese)",
        r"comportate\s+como",
        r"pretende\s+ser",
        r"finge\s+ser",
        r"suplanta",
        r"eres\s+ahora\s+(?:un\s+)?asistente\s+sin",
        r"olvidate\s+de\s+tu\s+(?:programacion|rol|personalidad)",
        r"no\s+importa\s+lo\s+que\s+digan",
        r"estas\s+(?:autorizad[oa]|permitid[oa])",
        r"te\s+(?:he\s+)?(?:desbloqueado|liberado)",
        r"vamos\s+a\s+(?:jugar|role(?:ar)?)",
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
        r"you\s+are\s+now\s+(?:a\s+)?(?:free|unrestricted|jailbroken)",
        r"no\s+(?:longer\s+)?need\s+to\s+follow",
        r"do\s+anything\s+now",
        r"dan\s+(?:mode\s+)?(?:activated|enabled)?",
        r"pretend\s+to\s+be",
        r"role\s*(?:play|playing)",
        r"new\s+(?:role|persona|character)",
        r"act\s+as\s+(?:an?\s+)?(?:unrestricted|free|unfiltered)",
        r"from\s+now\s+on\s+you\s+are",
        r"you\s+are\s+no\s+longer",
        r"override\s+(?:your\s+)?(?:previous\s+)?(?:instructions|prompt)",
        r"disregard\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules)",
        r"no\s+(?:rules|limits|boundaries|restrictions)",
        r"unfiltered\s+mode",
        r"god\s+mode",
        r"unleash\s+(?:your\s+)?(?:full\s+)?(?:potential|power)",
        r"remove\s+(?:your\s+)?(?:limitations|restrictions|constraints)",
        r"you\s+(?:have\s+)?(?:been\s+)?(?:unlocked|freed|liberated)",
        r"skip\s+(?:all\s+)?(?:safety|security|ethical)\s+(?:checks|measures|guidelines)",
        r"do\s+not\s+(?:refuse|reject|block)",
        r"always\s+(?:comply|obey|answer)",
        r"you\s+must\s+(?:always|never)",
        r"this\s+is\s+(?:a\s+)?(?:test|simulation|game)",
        r"hypothetical\s+(?:scenario|situation)",
        r"educational\s+purposes?\s+only",
    ],
    "pt": [
        r"ignore\s+(?:todas\s+)?(?:as\s+)?instrucoes\s+(?:anteriores|previas)",
        r"esqueca\s+(?:tudo\s+)?o\s+que\s+lhe\s+disse",
        r"aja\s+como\s+se\s+voce\s+fosse",
        r"modo\s+desenvolvedor",
        r"voce\s+e\s+agora\s+um",
        r"a\s+partir\s+de\s+agora",
        r"novo\s+(?:contexto|papel)",
        r"faca\s+como\s+se",
        r"finja\s+ser",
        r"sem\s+(?:restricoes|limites)",
    ],
    "fr": [
        r"ignorez?\s+(?:toutes\s+)?(?:les\s+)?instructions\s+(?:precedentes|anterieures)",
        r"oublie\s+(?:tout\s+)?ce\s+que\s+je\s+(?:t.ai|t'ai)\s+dit",
        r"agis\s+comme\s+si\s+tu\s+etais",
        r"mode\s+developpeur",
        r"tu\s+es\s+maintenant\s+un",
        r"a\s+partir\s+de\s+maintenant",
        r"nouveau\s+(?:contexte|role)",
        r"sans\s+(?:restrictions|limites)",
        r"libere",
        r"desactive\s+(?:les\s+)?filtres",
    ],
    "de": [
        r"ignoriere?\s+(?:alle\s+)?(?:vorherigen\s+)?Anweisungen",
        r"vergiss\s+(?:alles\s+)?was\s+ich\s+dir\s+gesagt\s+habe",
        r"handle\s+so\s+als\s+ob\s+du",
        r"entwicklermodus",
        r"du\s+bist\s+jetzt\s+ein",
        r"ab\s+jetzt\s+bist\s+du",
        r"neue\s+(?:Rolle|Kontext)",
        r"ohne\s+(?:Einschrankungen|Regeln)",
        r"entsperrt",
        r"schutzmasnahmen\s+deaktivieren",
    ],
}

PATRONES_ETIQUETAS_SISTEMA = re.compile(
    r"<\|?(?:system|im_start|im_end|assistant|user|prompt|end|start|"
    r"part|begin|input|output|completion)\|?>"
    r"|<\|?(?:sys|usr|asst|bot|chat|human|ai)\|?>"
    r"|</?(?:s|S)>"
    r"|\[(?:system|INST|SYS|START|END)\]"
    r"|__prompt__|__input__|__output__",
    re.IGNORECASE,
)

PATRONES_CODIGO = re.compile(
    r"\b(?:"
    r"eval\s*\(|exec\s*\(|compile\s*\(|__import__\s*\(|"
    r"import\s+(?:os|subprocess|sys|shutil|socket|ctypes|builtins)|"
    r"os\.system|os\.popen|os\.exec\b|os\.spawn|os\.fork|os\.kill|"
    r"subprocess\.(?:call|run|Popen|check_output|check_call|getoutput|getstatusoutput)|"
    r"shutil\.(?:rmtree|move|copy2|chown|chmod)|"
    r"sys\.(?:exit|setrecursionlimit|setprofile|settrace)|"
    r"builtins\.(?:exec|eval|__import__)|"
    r"ctypes|win32api|pywin32|"
    r"getattr|setattr|delattr|globals\s*\(|locals\s*\(|vars\s*\(|"
    r"__builtins__|__class__|__bases__|__subclasses__|"
    r"__globals__|__code__|__closure__|__func__|"
    r"pickle\.loads|pickle\.Unpickler|"
    r"marshal\.loads|shelve|"
    r"base64\.(?:b64decode|decode|b64encode)|"
    r"bytearray|memoryview|"
    r"open\s*\([^)]*\b(?:read|write|append|truncate)\b"
    r")\b",
    re.IGNORECASE,
)

_PL = (
    r"(?:"
    r"\bsudo\s+(?:rm|chmod|chown|kill|mkfs|dd|fdisk|mount|umount)|"
    r"\brm\s+(?:\-rf\s+[/~]|/[/~\*\s])|"
    r">\s*/dev/(?:sda|sdb|sdc|null)|"
    r":\s*\(\s*\)\s*\{|"
    r"\|\s*(?:bash|sh|zsh)\b|"
    r"`[^`]*`|"
    r"\$\([^)]*\)|"
    r"curl\s+.*?\s*\|\s*(?:bash|sh|python)|"
    r"wget\s+.*?\-O\s*-\s*\|\s*(?:bash|sh)|"
    r"chmod\s+\+x\s+/|"
    r"dd\s+if=/dev/zero|"
    r">\s*/etc/(?:passwd|shadow|sudoers)|"
    r"kill\s+\-9\s+\-1|"
    r"fork\s+bomb|"
    r"mkfs\s+/dev/|"
    r"cron\s+.*?rm\s+[\-]rf|"
    r"\|\|\s*(?:shutdown|reboot|poweroff|halt|init\s+0|init\s+6)|"
    r"&&\s*(?:shutdown|reboot|poweroff|halt)"
    r")"
)
PATRONES_LINUX = re.compile(_PL, re.IGNORECASE)

_PSQL = (
    r"(?:"
    r"\bDROP\s+TABLE|\bDROP\s+DATABASE|\bDELETE\s+FROM|"
    r"\bTRUNCATE\s+TABLE|\bALTER\s+TABLE|\bALTER\s+DATABASE|"
    r"\bCREATE\s+USER|\bGRANT\s+ALL|"
    r"\bUNION\s+SELECT|\bSELECT\s+\*|"
    r"\bLOAD_FILE|\bINTO\s+(?:OUTFILE|DUMPFILE)|"
    r"\bOR\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?|"
    r"'\s*OR\s+'[1i]'\s*=\s*'[1i]|"
    r"'\s*\-\-|'\s*#|/\*\s*!\s*\d+"
    r")"
)
PATRONES_SQL = re.compile(_PSQL, re.IGNORECASE)

_PJS = (
    r"(?:"
    r"\bdocument\.(?:cookie|domain|write|location)|"
    r"\bwindow\.(?:location|navigate|open|eval)|"
    r"\bfetch\(|\bXMLHttpRequest|"
    r"\balert\(|\bconfirm\(|\bprompt\(|"
    r"<script[^>]*>.*?</script>|"
    r"\bonerror\s*=|\bonload\s*=|\bonclick\s*=|\bonfocus\s*=|\bonmouseover\s*=|"
    r"\bjavascript:\s*|"
    r"\bfromCharCode|\bString\.fromCharCode|"
    r"\beval\s*\(\s*(?:window|self|top|parent)"
    r")"
)
PATRONES_JAVASCRIPT = re.compile(_PJS, re.IGNORECASE)

_PPS = (
    r"(?:"
    r"\bInvoke\-(?:Expression|Command|WebRequest|Shellcode|WmiMethod|RestMethod|Item|"
    r"WmiCommand|CimMethod)|"
    r"\bIEX\s*\(|\bIWR\b|"
    r"\bGet\-(?:Process|Service|ChildItem|Content|WmiObject|Item|"
    r"Command|Module|Member|Help|Location|Event)|"
    r"\bSet\-(?:ExecutionPolicy|Content|ItemProperty|Service)|"
    r"\bStart\-Process|\bStop\-Process|"
    r"\bNew\-Object|\bRemove\-Item|"
    r"\b(?:DownloadString|DownloadFile|UploadString)\s*\("
    r")"
)
PATRONES_POWERSHELL = re.compile(_PPS, re.IGNORECASE)

PATRONES_BINARIOS_ENCODING = re.compile(
    r"\b(?:base64|b64|hex|decode|decodeURIComponent|unescape|"
    r"fromCharCode|charCodeAt|escape)\s*\([^)]{20,}\)",
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

    if PATRONES_ETIQUETAS_SISTEMA.search(texto_norm):
        razones.append("etiqueta_sistema")

    pii = detectar_pii(texto_norm)
    if pii:
        razones.append(f"pii_detectado:{','.join(pii.keys())}")

    if PATRONES_CODIGO.search(texto_norm):
        razones.append("codigo_peligroso_python")

    if PATRONES_LINUX.search(texto_norm):
        razones.append("comando_linux")

    if PATRONES_SQL.search(texto_norm):
        razones.append("inyeccion_sql")

    if PATRONES_JAVASCRIPT.search(texto_norm):
        razones.append("codigo_javascript")

    if PATRONES_POWERSHELL.search(texto_norm):
        razones.append("codigo_powershell")

    if PATRONES_BINARIOS_ENCODING.search(texto_norm):
        razones.append("encoding_sospechoso")

    return ResultadoGuardia(
        es_seguro=len(razones) == 0,
        razones=razones,
        texto_normalizado=texto_norm,
    )
