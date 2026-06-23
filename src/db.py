import os
import sqlite3
import json
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_DIR = os.path.join(_PROJECT_ROOT, "data")
DB_PATH = os.path.join(_DB_DIR, "hardibot.db")


def conectar():
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = conectar()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'user',
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            persona_id TEXT NOT NULL DEFAULT 'hardware',
            created_at TEXT NOT NULL,
            mensajes TEXT NOT NULL,
            carrito_json TEXT NOT NULL,
            total_clp INTEGER NOT NULL DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_cotizaciones_email ON cotizaciones(email);
    """)
    conn.commit()
    conn.close()


# ── Usuarios ──

def crear_usuario(email, nombre, password_hash, salt, rol="user"):
    conn = conectar()
    conn.execute(
        "INSERT OR IGNORE INTO usuarios (email, nombre, rol, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (email, nombre, rol, password_hash, salt, _now()),
    )
    conn.commit()
    conn.close()


def obtener_usuario(email):
    conn = conectar()
    row = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def usuario_existe(email):
    return obtener_usuario(email) is not None


# ── Cotizaciones ──

def guardar_cotizacion(email, persona_id, mensajes, carrito_items, total_clp):
    conn = conectar()
    conn.execute(
        "INSERT INTO cotizaciones (email, persona_id, created_at, mensajes, carrito_json, total_clp) VALUES (?, ?, ?, ?, ?, ?)",
        (
            email,
            persona_id,
            _now(),
            json.dumps(mensajes, ensure_ascii=False),
            json.dumps(carrito_items, ensure_ascii=False),
            int(total_clp),
        ),
    )
    conn.commit()
    conn.close()


def listar_cotizaciones(email):
    conn = conectar()
    rows = conn.execute(
        "SELECT id, persona_id, created_at, total_clp FROM cotizaciones WHERE email = ? ORDER BY id DESC",
        (email,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cargar_cotizacion(cot_id):
    conn = conectar()
    row = conn.execute("SELECT * FROM cotizaciones WHERE id = ?", (cot_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["mensajes"] = json.loads(d["mensajes"])
        d["carrito_json"] = json.loads(d["carrito_json"])
        return d
    return None


# ── Sesiones ──

def guardar_sesion(email, persona_id, mensajes, tool_history, carrito_items):
    if not email or email == "anonimo":
        return
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            email TEXT PRIMARY KEY REFERENCES usuarios(email),
            persona_id TEXT NOT NULL DEFAULT 'hardware',
            messages TEXT NOT NULL DEFAULT '[]',
            tool_history TEXT NOT NULL DEFAULT '[]',
            carrito_items TEXT NOT NULL DEFAULT '[]',
            actualizado TEXT NOT NULL
        )
    """)
    conn.execute(
        "INSERT OR REPLACE INTO sesiones (email, persona_id, messages, tool_history, carrito_items, actualizado) VALUES (?, ?, ?, ?, ?, ?)",
        (
            email,
            persona_id,
            json.dumps(mensajes, ensure_ascii=False),
            json.dumps(tool_history, ensure_ascii=False),
            json.dumps(carrito_items, ensure_ascii=False),
            _now(),
        ),
    )
    conn.commit()
    conn.close()


def cargar_sesion(email):
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            email TEXT PRIMARY KEY REFERENCES usuarios(email),
            persona_id TEXT NOT NULL DEFAULT 'hardware',
            messages TEXT NOT NULL DEFAULT '[]',
            tool_history TEXT NOT NULL DEFAULT '[]',
            carrito_items TEXT NOT NULL DEFAULT '[]',
            actualizado TEXT NOT NULL
        )
    """)
    conn.commit()
    row = conn.execute("SELECT * FROM sesiones WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["messages"] = json.loads(d["messages"])
        d["tool_history"] = json.loads(d["tool_history"])
        d["carrito_items"] = json.loads(d["carrito_items"])
        return d
    return {}


def _now():
    return datetime.now().isoformat()
