"""Test buscar_web tool from core.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core import _buscar_web, _buscar_catalogo_local, app_state

print("=== Test _buscar_web ===")
resultado = _buscar_web.invoke({"query": "Ryzen 5 5600G precio Chile"})
print(f"Result type: {type(resultado).__name__}")
print(f"Result length: {len(str(resultado))}")
print(f"Result preview: {str(resultado)[:300]}")
print()

print("=== Test _buscar_catalogo_local ===")
resultado2 = _buscar_catalogo_local.invoke({"query": "Ryzen 5"})
print(f"Result type: {type(resultado2).__name__}")
print(f"Result length: {len(str(resultado2))}")
print(f"Result preview: {str(resultado2)[:300]}")
