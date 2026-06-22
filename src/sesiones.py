import os
import json
from datetime import datetime

USUARIOS_DIR = "data/usuarios"


def _asegurar_directorio():
    os.makedirs(USUARIOS_DIR, exist_ok=True)


def guardar_sesion(user_email: str, persona_id: str, messages: list, tool_history: list, carrito_items: list):
    """Guarda el historial de un usuario autenticado."""
    if not user_email or user_email == "anonimo":
        return
    _asegurar_directorio()
    path = os.path.join(USUARIOS_DIR, f"{user_email}.json")
    data = {
        "email": user_email,
        "persona_id": persona_id,
        "actualizado": datetime.now().isoformat(),
        "messages": messages,
        "tool_history": tool_history,
        "carrito_items": carrito_items,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cargar_historial(user_email: str) -> dict:
    """Carga el historial de un usuario autenticado."""
    path = os.path.join(USUARIOS_DIR, f"{user_email}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
