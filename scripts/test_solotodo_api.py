"""Debug: probar endpoints de SoloTodo API para encontrar el parametro correcto"""
import requests
import json

VARIANTS = [
    {"name": "product", "val": "product"},
    {"name": "product__id", "val": "product__id"},
    {"name": "product_id", "val": "product_id"},
    {"name": "products", "val": "products"},
    {"name": "producto", "val": "producto"},
]
BASES = ["https://api.solotodo.com", "https://publicapi.solotodo.com"]
CAT_ID = 2  # Tarjetas de Video

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

for base in BASES:
    print(f"\n{'='*60}")
    print(f"Base: {base}")
    print(f"{'='*60}")

    # 1. Obtener productos
    try:
        r = requests.get(
            f"{base}/products/",
            params={"categories": CAT_ID, "page_size": 3, "format": "json"},
            headers=headers,
            timeout=15,
        )
        print(f"Products: {r.status_code}")
        data = r.json()
        products = data.get("results", [])
        print(f"  Encontrados: {len(products)}")
    except Exception as e:
        print(f"  Products error: {e}")
        continue

    for p in products[:2]:
        pid = p["id"]
        name = p.get("name", "?")[:60]
        print(f"\n  Producto {pid}: {name}")

        # 2. Probar cada variante de parametro
        for v in VARIANTS:
            try:
                e = requests.get(
                    f"{base}/entities/",
                    params={v["val"]: pid, "is_visible": "True", "page_size": 1, "format": "json"},
                    headers=headers,
                    timeout=10,
                )
                ents = e.json().get("results", [])
                valid = False
                ext_url = ""
                if ents:
                    ext = ents[0].get("external_url", "")
                    ext_url = ext[:80] if ext else "NO_URL"
                    # Verificar que el entity pertenece al producto
                    prod_ref = ents[0].get("product", {})
                    if isinstance(prod_ref, dict):
                        ep_id = prod_ref.get("id")
                        if ep_id == pid:
                            valid = True

                status = "OK" if valid else "WRONG"
                print(f"    {v['name']:>12}: {e.status_code} {status} len={len(ents)} | {ext_url}")
            except Exception as ex:
                print(f"    {v['name']:>12}: ERROR {ex}")

print("\nDone.")
