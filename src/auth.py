import os
import json
import hashlib
import secrets

USUARIOS_PATH = "data/usuarios.json"

ADMIN_DEFAULT = {
    "email": "admin@hardibot.cl",
    "nombre": "Admin Summit",
    "rol": "admin",
}

_OLAS = None


def _cargar():
    global _OLAS
    if _OLAS is not None:
        return _OLAS
    os.makedirs(os.path.dirname(USUARIOS_PATH), exist_ok=True)
    if not os.path.exists(USUARIOS_PATH):
        _OLAS = _inicializar()
        _guardar(_OLAS)
    else:
        with open(USUARIOS_PATH, "r", encoding="utf-8") as f:
            _OLAS = json.load(f)
    return _OLAS


def _guardar(data):
    global _OLAS
    _OLAS = data
    with open(USUARIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _inicializar():
    salt = secrets.token_hex(16)
    pwd = "summit2025"
    h = hashlib.pbkdf2_hmac("sha256", pwd.encode(), salt.encode(), 200000)
    return {
        "usuarios": {
            ADMIN_DEFAULT["email"]: {
                "nombre": ADMIN_DEFAULT["nombre"],
                "rol": ADMIN_DEFAULT["rol"],
                "password_hash": h.hex(),
                "salt": salt,
                "created_at": "auto",
            }
        }
    }


def _hash_password(password: str, salt: str = None) -> tuple:
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200000)
    return h.hex(), salt


def verificar(email: str, password: str) -> dict:
    data = _cargar()
    usuario = data.get("usuarios", {}).get(email)
    if not usuario:
        return None
    h, _ = _hash_password(password, usuario["salt"])
    if h == usuario["password_hash"]:
        return {"email": email, "nombre": usuario["nombre"], "rol": usuario["rol"]}
    return None


def agregar_admin(email: str, password: str, nombre: str):
    data = _cargar()
    h, salt = _hash_password(password)
    data["usuarios"][email] = {
        "nombre": nombre,
        "rol": "admin",
        "password_hash": h,
        "salt": salt,
        "created_at": _now(),
    }
    _guardar(data)
    return data["usuarios"][email]


def _now():
    from datetime import datetime
    return datetime.now().isoformat()
