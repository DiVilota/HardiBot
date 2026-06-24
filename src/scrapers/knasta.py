import os
import time
import re
import json
import random
import requests
import pandas as pd
from typing import Optional
from src.scrapers.base import CatalogScraper

BASE_URL = "https://knasta.cl"

CATEGORIAS_KNASTA = {
    "Procesador": ("hardware/componentes/procesadores", "Procesador"),
    "Tarjeta_Video": ("hardware/componentes/tarjetas-de-video", "Tarjeta de Video"),
    "Placa_Madre": ("hardware/componentes/placas-madre", "Placa Madre"),
    "Memoria_RAM": ("hardware/componentes/memorias-ram", "Memoria RAM"),
    "Almacenamiento": ("hardware/componentes/discos-duros-pendrives-y-micro-sd", "Almacenamiento"),
    "Fuente_Poder": ("hardware/componentes/fuentes-de-poder", "Fuente de Poder"),
    "Monitor": ("tecnologia/computacion/monitores", "Monitor"),
}


class KnastaScraper(CatalogScraper):
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/120.0",
            "Accept": "text/html",
        })

    def _fetch_category_page(self, path: str, page: int = 1) -> dict:
        url = f"{BASE_URL}/results/{path}?page={page}&page_size=32&order=price_asc"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        m = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
            r.text,
            re.DOTALL,
        )
        if not m:
            raise RuntimeError(f"No se encontraron datos en la pagina: {url}")
        data = json.loads(m.group(1))
        return data["props"]["pageProps"]["initialData"]

    def _extraer_modelo(self, title: str, brand: str) -> str:
        if brand and title.lower().startswith(brand.lower()):
            return title[len(brand):].strip()
        return title

    def _estimar_stock(self, producto: dict) -> str:
        if producto.get("is_premium"):
            return "Alta"
        return random.choices(["Alta", "Media", "Baja"], weights=[0.3, 0.4, 0.3])[0]

    def generar(self, output_path: str, max_por_categoria: Optional[int] = None) -> str:
        random.seed(42)
        todas_filas = []

        for categoria_nombre, (path, etiqueta) in CATEGORIAS_KNASTA.items():
            print(f"  Knasta: {etiqueta}...")
            try:
                primera = self._fetch_category_page(path, page=1)
                total_paginas = primera.get("total_pages", 1)
                products = list(primera.get("products", []))

                print(f"    -> {primera.get('count', 0)} productos, {total_paginas} paginas")

                paginas_a_scrapear = min(total_paginas, 3)
                for pg in range(2, paginas_a_scrapear + 1):
                    try:
                        data = self._fetch_category_page(path, page=pg)
                        products.extend(data.get("products", []))
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"    [pagina {pg} fallo: {e}]")

                limit = max_por_categoria or 9999
                for prod in products[:limit]:
                    title = prod.get("title", "")
                    marca = prod.get("brand", "")
                    modelo = self._extraer_modelo(title, marca)
                    precio = prod.get("current_price")
                    if precio is None:
                        continue

                    especs = title
                    todas_filas.append({
                        "Categoria": categoria_nombre,
                        "Marca": marca,
                        "Modelo": modelo[:120] if modelo else title[:120],
                        "Especificaciones": especs[:200],
                        "Precio_CLP": int(precio),
                        "Stock": self._estimar_stock(prod),
                    })

                time.sleep(0.5)
            except Exception as e:
                print(f"  [Error en {categoria_nombre}: {e}]")

        if not todas_filas:
            raise RuntimeError("No se obtuvieron productos de Knasta.")

        df = pd.DataFrame(todas_filas)
        df = df.drop_duplicates(subset=["Marca", "Modelo", "Precio_CLP"])
        df = self.validar_dataframe(df)
        df.to_csv(output_path, index=False)
        print(f"  Catalogo Knasta guardado: {output_path} ({len(df)} productos)")
        return output_path
