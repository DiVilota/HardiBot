import hashlib
import secrets
from src.db import init_db, obtener_usuario, crear_usuario, usuario_existe

ADMIN_DEFAULT_EMAIL = "admin@hardibot.cl"
ADMIN_DEFAULT_NAME = "Admin Summit"
ADMIN_DEFAULT_PASSWORD = "summit2026"
ADMIN_DEFAULT_ROL = "admin"


def _crear_admin_default():
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", ADMIN_DEFAULT_PASSWORD.encode(), salt.encode(), 200000)
    crear_usuario(ADMIN_DEFAULT_EMAIL, ADMIN_DEFAULT_NAME, h.hex(), salt, ADMIN_DEFAULT_ROL)


def _asegurar_tablas():
    init_db()
    if not usuario_existe(ADMIN_DEFAULT_EMAIL):
        _crear_admin_default()


def verificar(email: str, password: str) -> dict:
    """Login: retorna dict con email, nombre, rol o None."""
    _asegurar_tablas()
    usuario = obtener_usuario(email)
    if not usuario:
        return None
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), usuario["salt"].encode(), 200000)
    if h.hex() == usuario["password_hash"]:
        return {"email": email, "nombre": usuario["nombre"], "rol": usuario["rol"]}
    return None


def registrar(email: str, password: str, nombre: str) -> dict:
    """Registro publico: crea usuario con rol=user. Retorna dict o None si ya existe."""
    _asegurar_tablas()
    if usuario_existe(email):
        return None
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200000)
    crear_usuario(email, nombre, h.hex(), salt, "user")
    return {"email": email, "nombre": nombre, "rol": "user"}


def agregar_admin(email: str, password: str, nombre: str):
    """CLI: crea admin."""
    _asegurar_tablas()
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200000)
    crear_usuario(email, nombre, h.hex(), salt, "admin")
    return obtener_usuario(email)
