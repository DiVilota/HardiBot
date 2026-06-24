import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.auth import agregar_admin

if len(sys.argv) < 4:
    print("Uso: python scripts/add_admin.py <email> <password> <nombre>")
    print("Ej:   python scripts/add_admin.py ignacio@hardibot.cl secreto123 \"Ignacio Chacon\"")
    sys.exit(1)

email = sys.argv[1]
password = sys.argv[2]
nombre = sys.argv[3]

admin = agregar_admin(email, password, nombre)
print(f"Admin agregado: {admin['nombre']} ({email}) - Rol: {admin['rol']}")
