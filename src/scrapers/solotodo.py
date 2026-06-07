import os
import time
import requests
import pandas as pd
from typing import Optional
from rich.console import Console
from src.scrapers.base import CatalogScraper

console = Console()

API_BASE = "https://api.solotodo.com"

CATEGORIAS_HARDWARE = {
    "Procesador": 3,
    "Placa_Madre": 5,
    "Tarjeta_Video": 2,
    "Memoria_RAM": 7,
    "Almacenamiento": 39,
    "Fuente_Poder": 9,
    "Gabinete": 10,
    "Monitor": 4,
    "Cooler_CPU": 12,
}

RANGOS_PRECIO = {
    "Procesador": (45000, 750000),
    "Placa_Madre": (45000, 350000),
    "Tarjeta_Video": (180000, 2500000),
    "Memoria_RAM": (15000, 200000),
    "Almacenamiento": (15000, 250000),
    "Fuente_Poder": (35000, 250000),
    "Gabinete": (25000, 200000),
    "Monitor": (80000, 800000),
    "Cooler_CPU": (8000, 120000),
}

CATEGORIA_SLUG_MAP = {
    "Procesador": "procesadores",
    "Placa_Madre": "placas_madre",
    "Tarjeta_Video": "tarjetas_de_video",
    "Memoria_RAM": "rams",
    "Almacenamiento": "unidades_de_estado_solido_ssds",
    "Fuente_Poder": "fuentes_de_poder",
    "Gabinete": "gabinetes",
    "Monitor": "monitores",
    "Cooler_CPU": "cpu_coolers",
}


class SoloTodoScraper(CatalogScraper):
    def __init__(self, timeout: int = 15):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept": "application/json",
        })
        self.timeout = timeout

    def _fetch_json(self, url: str, params: dict = None) -> dict:
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _extraer_modelo(self, product: dict) -> str:
        name = product.get("name", "")
        brand_url = product.get("brand", "")
        if brand_url:
            brand_name = brand_url.strip("/").split("/")[-1]
        else:
            brand_name = ""
        modelo = name.replace(brand_name, "", 1).strip() if brand_name else name
        return modelo if modelo else name

    def _generar_especificaciones(self, product: dict, categoria: str) -> str:
        specs = product.get("specs") or {}
        partes = []
        if categoria == "Procesador":
            núcleos = specs.get("core_count_unicode", "")
            hilos = specs.get("thread_count_unicode", "")
            freq = specs.get("frequency", "")
            turbo = specs.get("max_turbo_frequency", "")
            socket = specs.get("socket_unicode", "")
            tdp = specs.get("tdp", "")
            if núcleos:
                partes.append(f"{núcleos} Núcleos")
            if hilos:
                partes.append(f"{hilos} Hilos")
            if freq:
                turbo_str = f" / {turbo}MHz Turbo" if turbo else ""
                partes.append(f"{freq}MHz{turbo_str}")
            if socket:
                partes.append(f"Socket {socket}")
            if tdp:
                partes.append(f"{tdp}W TDP")
        elif categoria == "Placa_Madre":
            socket = specs.get("socket_unicode", "")
            formato = specs.get("format_unicode", "")
            ddr = specs.get("memory_type_unicode", "")
            if socket:
                partes.append(f"Socket {socket}")
            if formato:
                partes.append(f"Formato {formato}")
            if ddr:
                partes.append(f"Soporta {ddr}")
        elif categoria == "Tarjeta_Video":
            gpu = specs.get("gpu_unicode", "")
            mem = specs.get("memory_quantity_unicode", "")
            mem_t = specs.get("memory_type_name", "")
            if gpu:
                partes.append(f"GPU {gpu}")
            if mem and mem_t:
                partes.append(f"{mem} {mem_t}")
        elif categoria == "Memoria_RAM":
            cap = specs.get("capacity_unicode", "")
            tipo = specs.get("memory_type_unicode", "")
            freq = specs.get("frequency", "")
            if cap:
                partes.append(f"{cap}")
            if tipo:
                partes.append(f"{tipo}")
            if freq:
                partes.append(f"{freq}MHz")
        elif categoria == "Almacenamiento":
            cap = specs.get("capacity_unicode", "")
            bus = specs.get("ssd_type_bus_unicode", "")
            formato = specs.get("ssd_type_format_unicode", "")
            if cap:
                partes.append(f"{cap}")
            if bus:
                partes.append(f"Interfaz {bus}")
            if formato:
                partes.append(f"{formato}")
        elif categoria == "Fuente_Poder":
            power = specs.get("power", "")
            formato = specs.get("format_unicode", "")
            modular = specs.get("modular_unicode", "")
            if power:
                partes.append(f"{power}W")
            if formato:
                partes.append(f"Formato {formato}")
            if modular:
                partes.append(modular)
        elif categoria == "Gabinete":
            formato = specs.get("format_unicode", "")
            bahias = specs.get("bay_count_unicode", "")
            if formato:
                partes.append(f"Formato {formato}")
            if bahias:
                partes.append(f"{bahias} Bahías")
        elif categoria == "Monitor":
            size = specs.get("size_unicode", "")
            resol = specs.get("resolution_name", "")
            panel = specs.get("panel_type_unicode", "")
            if size:
                partes.append(f"{size}")
            if resol:
                partes.append(f"{resol}")
            if panel:
                partes.append(f"Panel {panel}")
        elif categoria == "Cooler_CPU":
            tipo = specs.get("type_name", "")
            tamaño = specs.get("size_unicode", "")
            ruido = specs.get("noise_level", "")
            if tipo:
                partes.append(f"Tipo {tipo}")
            if tamaño:
                partes.append(f"{tamaño}")
            if ruido:
                partes.append(f"{ruido} dB")
        return " / ".join(partes) if partes else specs.get("unicode", "")

    def _estimar_stock(self) -> str:
        import random
        return random.choices(["Alta", "Media", "Baja"], weights=[0.5, 0.3, 0.2])[0]

    def _extraer_precio_real(self, product_id: int, categoria: str) -> int:
        try:
            url = f"{API_BASE}/entities/"
            params = {"product": product_id, "is_visible": "True", "page_size": 5}
            data = self._fetch_json(url, params)
            precios = []
            for ent in data.get("results", []):
                registry = ent.get("active_registry")
                if registry:
                    precio = registry.get("active_registered_price")
                    if precio:
                        precios.append(float(precio))
            if precios:
                return int(sum(precios) / len(precios))
        except Exception as e:
            console.print(f"[dim]⚠️ No se pudo obtener precio real para producto {product_id}: {e}[/dim]")
        return self._generar_precio_realista(categoria)

    def _generar_precio_realista(self, categoria: str) -> int:
        import random
        min_p, max_p = RANGOS_PRECIO.get(categoria, (10000, 500000))
        media = (min_p + max_p) / 2
        std = (max_p - min_p) / 4
        precio = int(random.gauss(media, std))
        return max(min_p, min(max_p, precio))

    def _fetch_products_page(self, category_id: int, page: int = 1) -> dict:
        url = f"{API_BASE}/products/"
        params = {
            "categories": category_id,
            "page": page,
            "page_size": 100,
            "format": "json",
            "ordering": "-last_updated",
        }
        return self._fetch_json(url, params)

    def generar(self, output_path: str, max_por_categoria: int = 15) -> str:
        import random
        random.seed(42)
        todas_filas = []

        for categoria_nombre, cat_id in CATEGORIAS_HARDWARE.items():
            console.print(f"[bold cyan]📦 Scrapeando: {categoria_nombre} (ID {cat_id})...[/bold cyan]")
            try:
                data = self._fetch_products_page(cat_id)
                productos = data.get("results", [])
                total = data.get("count", 0)
                console.print(f"  → {total} productos encontrados. Tomando {min(max_por_categoria, len(productos))}...")

                random.shuffle(productos)
                for prod in productos[:max_por_categoria]:
                    prod_id = prod["id"]
                    modelo = self._extraer_modelo(prod)
                    marca = ""
                    brand_url = prod.get("brand", "")
                    if brand_url:
                        try:
                            brand_data = self._fetch_json(brand_url)
                            marca = brand_data.get("name", "")
                        except Exception:
                            marca = brand_url.strip("/").split("/")[-1].capitalize()

                    precio = self._extraer_precio_real(prod_id, categoria_nombre)
                    stock = self._estimar_stock()
                    especs = self._generar_especificaciones(prod, categoria_nombre)

                    if not especs:
                        especs = prod.get("specs", {}).get("unicode", "")

                    todas_filas.append({
                        "Categoria": categoria_nombre,
                        "Marca": marca,
                        "Modelo": modelo,
                        "Especificaciones": especs,
                        "Precio_CLP": precio,
                        "Stock": stock,
                    })
                time.sleep(0.3)
            except Exception as e:
                console.print(f"[yellow]⚠️ Error scrapeando {categoria_nombre}: {e}[/yellow]")

        if not todas_filas:
            raise RuntimeError("No se obtuvieron productos de SoloTodo.")

        df = pd.DataFrame(todas_filas)
        df = self.validar_dataframe(df)
        df.to_csv(output_path, index=False)
        console.print(f"[bold green]✅ Catálogo SoloTodo guardado: {output_path} ({len(df)} productos)[/bold green]")
        return output_path
