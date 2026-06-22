import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.db import init_db, conectar


def mostrar_usuarios(conn):
    rows = conn.execute(
        "SELECT email, nombre, rol, created_at FROM usuarios ORDER BY created_at"
    ).fetchall()
    print(f"\n{'=' * 60}")
    print(f"  USUARIOS ({len(rows)})")
    print(f"{'=' * 60}")
    if not rows:
        print("  (vacio)")
        return
    for r in rows:
        print(f"  {r['email']:<32s} {r['nombre']:<20s} {r['rol']:<8s} {r['created_at'][:16]}")


def mostrar_cotizaciones(conn):
    rows = conn.execute(
        "SELECT id, email, persona_id, total_clp, created_at FROM cotizaciones ORDER BY id DESC"
    ).fetchall()
    print(f"\n{'=' * 60}")
    print(f"  COTIZACIONES ({len(rows)})")
    print(f"{'=' * 60}")
    if not rows:
        print("  (vacio)")
        return
    for r in rows:
        total = f"${r['total_clp']:,}".replace(",", ".")
        print(f"  #{r['id']:<5d} {r['email']:<32s} {r['persona_id']:<12s} {total:<14s} {r['created_at'][:16]}")


def mostrar_sesiones(conn):
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
    rows = conn.execute(
        "SELECT email, persona_id, LENGTH(messages) as msg_len, actualizado FROM sesiones ORDER BY actualizado DESC"
    ).fetchall()
    print(f"\n{'=' * 60}")
    print(f"  SESIONES ({len(rows)})")
    print(f"{'=' * 60}")
    if not rows:
        print("  (vacio)")
        return
    for r in rows:
        print(f"  {r['email']:<32s} {r['persona_id']:<12s} {r['msg_len']} chars   {r['actualizado'][:16]}")


def main():
    init_db()
    conn = conectar()
    mostrar_usuarios(conn)
    mostrar_cotizaciones(conn)
    mostrar_sesiones(conn)
    conn.close()
    print()


if __name__ == "__main__":
    main()
