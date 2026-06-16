import os
import json
from datetime import datetime


SESIONES_DIR = "data/sesiones"


def _asegurar_directorio():
    os.makedirs(SESIONES_DIR, exist_ok=True)


def guardar_sesion(session_id: str, persona_id: str, messages: list, tool_history: list, carrito_items: list):
    _asegurar_directorio()
    path = os.path.join(SESIONES_DIR, f"{session_id}.json")
    data = {
        "session_id": session_id,
        "persona_id": persona_id,
        "actualizado": datetime.now().isoformat(),
        "messages": messages,
        "tool_history": tool_history,
        "carrito_items": carrito_items,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cargar_sesion(session_id: str) -> dict:
    path = os.path.join(SESIONES_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def listar_sesiones() -> list:
    _asegurar_directorio()
    sesiones = []
    for filename in os.listdir(SESIONES_DIR):
        if filename.endswith(".json"):
            path = os.path.join(SESIONES_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sesiones.append({
                "session_id": data.get("session_id", filename[:-5]),
                "persona_id": data.get("persona_id", ""),
                "actualizado": data.get("actualizado", ""),
                "mensajes": len(data.get("messages", [])),
            })
    sesiones.sort(key=lambda s: s["actualizado"], reverse=True)
    return sesiones


def eliminar_sesion(session_id: str):
    path = os.path.join(SESIONES_DIR, f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
