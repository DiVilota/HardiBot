from src.db import guardar_sesion as _db_guardar, cargar_sesion as _db_cargar


def guardar_sesion(user_email: str, persona_id: str, messages: list, tool_history: list, carrito_items: list):
    """Guarda el historial de un usuario autenticado via SQLite."""
    _db_guardar(user_email, persona_id, messages, tool_history, carrito_items)


def cargar_historial(user_email: str) -> dict:
    """Carga el historial de un usuario autenticado via SQLite."""
    return _db_cargar(user_email)
