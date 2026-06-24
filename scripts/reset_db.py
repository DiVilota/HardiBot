import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.db import conectar, DB_PATH
from src.auth import _asegurar_tablas


def main():
    print("ADVERTENCIA: Esto borrara TODOS los usuarios, cotizaciones y sesiones.")
    confirm = input("Escribi 'si' para confirmar: ").strip().lower()
    if confirm != "si":
        print("Cancelado.")
        return

    conn = conectar()
    conn.execute("DELETE FROM cotizaciones")
    conn.execute("DROP TABLE IF EXISTS sesiones")
    conn.execute("DELETE FROM usuarios")
    conn.commit()
    conn.close()

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    _asegurar_tablas()
    print("OK. BD reseteada. Admin default: admin@hardibot.cl / summit2025")


if __name__ == "__main__":
    main()
