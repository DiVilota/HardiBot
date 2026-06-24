import random
import pandas as pd
from typing import Optional
from rich.console import Console
from src.scrapers.base import CatalogScraper

console = Console()

DATA = {
    "Procesador": {
        "marcas": {
            "AMD": [
                ("Ryzen 3 4100", "AM4 4-Cores 8-Threads 3.8GHz", 95000),
                ("Ryzen 5 5600", "AM4 6-Cores 12-Threads 3.5GHz 65W", 140000),
                ("Ryzen 5 5600G", "AM4 6-Cores 12-Threads 3.9GHz con graficos Radeon", 145000),
                ("Ryzen 5 7600", "AM5 6-Cores 12-Threads 3.8GHz 65W DDR5", 240000),
                ("Ryzen 7 5700X3D", "AM4 8-Cores 16-Threads 3.0GHz 105W 3D V-Cache", 280000),
                ("Ryzen 7 7800X3D", "AM5 8-Cores 16-Threads 4.2GHz 120W 3D V-Cache", 390000),
                ("Ryzen 7 9800X3D", "AM5 8-Cores 16-Threads 4.7GHz 120W 3D V-Cache", 550000),
                ("Ryzen 9 7950X", "AM5 16-Cores 32-Threads 4.5GHz 170W", 520000),
                ("Ryzen 9 9950X", "AM5 16-Cores 32-Threads 4.3GHz 170W", 680000),
            ],
            "Intel": [
                ("Core i3-14100F", "LGA1700 4-Cores 8-Threads 3.5GHz 60W", 85000),
                ("Core i5-12400F", "LGA1700 6-Cores 12-Threads 2.5GHz 65W", 125000),
                ("Core i5-14400F", "LGA1700 10-Cores 16-Threads 2.5GHz 65W", 195000),
                ("Core i5-14600K", "LGA1700 14-Cores 20-Threads 3.5GHz 125W", 310000),
                ("Core i7-14700K", "LGA1700 20-Cores 28-Threads 3.4GHz 125W", 440000),
                ("Core i9-14900K", "LGA1700 24-Cores 32-Threads 3.2GHz 253W", 620000),
                ("Core Ultra 5 225H", "LGA1851 14-Cores 18-Threads 3.3GHz", 280000),
                ("Core Ultra 7 265K", "LGA1851 20-Cores 20-Threads 3.3GHz 125W", 450000),
                ("Core Ultra 9 285K", "LGA1851 24-Cores 24-Threads 3.7GHz 125W", 650000),
            ],
        },
        "stock_pesos": [0.5, 0.3, 0.2],
    },
    "Placa_Madre": {
        "marcas": {
            "Asus": [
                ("Prime A320M-K", "AM4 Micro-ATX DDR4 PCIe 3.0 Basica", 55000),
                ("TUF B450M-PLUS II", "AM4 Micro-ATX DDR4 PCIe 3.0", 85000),
                ("TUF B550M-PLUS WIFI", "AM4 Micro-ATX DDR4 PCIe 4.0 WIFI", 130000),
                ("ROG STRIX B650-A GAMING", "AM5 ATX DDR5 PCIe 4.0", 220000),
                ("TUF GAMING X670E-PLUS WIFI", "AM5 ATX DDR5 PCIe 5.0", 320000),
                ("ROG STRIX Z790-E GAMING", "LGA1700 ATX DDR5 PCIe 5.0 Premium", 380000),
            ],
            "MSI": [
                ("PRO H610M-G DDR4", "LGA1700 Micro-ATX DDR4", 65000),
                ("PRO B650-P WIFI", "AM5 ATX DDR5 PCIe 4.0", 185000),
                ("MAG Z790 TOMAHAWK MAX WIFI", "LGA1700 ATX DDR5 PCIe 5.0", 310000),
                ("MPG X670E CARBON WIFI", "AM5 ATX DDR5 PCIe 5.0", 450000),
            ],
            "Gigabyte": [
                ("B760M DS3H DDR4", "LGA1700 Micro-ATX DDR4", 95000),
                ("B650M AORUS ELITE", "AM5 Micro-ATX DDR5", 165000),
                ("Z790 AORUS ELITE AX", "LGA1700 ATX DDR5 PCIe 5.0", 280000),
            ],
            "ASRock": [
                ("B450M-HDV R4.0", "AM4 Micro-ATX DDR4", 50000),
                ("B650M-HDV/M.2", "AM5 Micro-ATX DDR5 PCIe 4.0", 125000),
            ],
        },
        "stock_pesos": [0.5, 0.3, 0.2],
    },
    "Tarjeta_Video": {
        "marcas": {
            "NVIDIA": [
                ("RTX 4060 8GB", "DLSS 3.0 Ideal para 1080p Ultra", 320000),
                ("RTX 4060 Ti 8GB", "DLSS 3.0 1080p-1440p Alto", 420000),
                ("RTX 4070 12GB", "DLSS 3.0 Ideal 1440p Ultra", 560000),
                ("RTX 4070 Ti SUPER 16GB", "DLSS 3.0 1440p-4K", 850000),
                ("RTX 4080 SUPER 16GB", "DLSS 3.0 Ideal 4K Ultra", 1050000),
                ("RTX 4090 24GB", "DLSS 3.0 Supremo 4K 8K", 2200000),
            ],
            "AMD": [
                ("Radeon RX 6600 8GB", "1080p Alto Eficiente", 220000),
                ("Radeon RX 7600 8GB", "1080p Ultra Competitivo", 285000),
                ("Radeon RX 7700 XT 12GB", "1440p Alto FSR 3", 430000),
                ("Radeon RX 7800 XT 16GB", "1440p Ultra FSR 3", 580000),
                ("Radeon RX 7900 GRE 16GB", "1440p-4K FSR 3", 650000),
                ("Radeon RX 7900 XTX 24GB", "4K Ultra FSR 3 Supremo", 1200000),
            ],
        },
        "stock_pesos": [0.3, 0.4, 0.3],
    },
    "Memoria_RAM": {
        "marcas": {
            "Kingston": [
                ("Fury Beast 8GB (1x8GB) DDR4", "3200MHz CL16", 18000),
                ("Fury Beast 16GB (2x8GB) DDR4", "3200MHz CL16", 48000),
                ("Fury Beast 32GB (2x16GB) DDR5", "5200MHz CL40", 95000),
                ("Fury Beast 32GB (2x16GB) DDR5 RGB", "6000MHz CL36", 110000),
                ("Fury Renegade 64GB (2x32GB) DDR5", "6400MHz CL32", 210000),
            ],
            "Corsair": [
                ("Vengeance LPX 16GB (2x8GB) DDR4", "3200MHz CL16", 45000),
                ("Vengeance 32GB (2x16GB) DDR5", "6000MHz CL30 Optimizado AMD EXPO", 135000),
                ("Dominator Titanium 32GB (2x16GB) DDR5", "7200MHz CL34 RGB", 190000),
                ("Vengeance 64GB (2x32GB) DDR5", "5600MHz CL40", 175000),
            ],
            "G.Skill": [
                ("Ripjaws V 16GB (2x8GB) DDR4", "3600MHz CL16", 50000),
                ("Trident Z5 NEO 32GB (2x16GB) DDR5", "6000MHz CL30 AMD EXPO", 145000),
                ("Trident Z5 RGB 64GB (2x32GB) DDR5", "6400MHz CL32", 225000),
            ],
        },
        "stock_pesos": [0.4, 0.4, 0.2],
    },
    "Almacenamiento": {
        "marcas": {
            "Samsung": [
                ("870 EVO 500GB", "SATA III 2.5 560MB/s", 50000),
                ("870 EVO 1TB", "SATA III 2.5 560MB/s", 85000),
                ("980 Pro 1TB", "NVMe M.2 PCIe 4.0 7000MB/s", 115000),
                ("990 Pro 1TB", "NVMe M.2 PCIe 4.0 7450MB/s", 145000),
                ("990 Pro 2TB", "NVMe M.2 PCIe 4.0 7450MB/s", 260000),
            ],
            "Western Digital": [
                ("WD Blue SN570 500GB", "NVMe M.2 PCIe 3.0 3500MB/s", 45000),
                ("WD Black SN770 1TB", "NVMe M.2 PCIe 4.0 5150MB/s", 95000),
                ("WD Black SN850X 1TB", "NVMe M.2 PCIe 4.0 7300MB/s", 105000),
                ("WD Black SN850X 2TB", "NVMe M.2 PCIe 4.0 7300MB/s", 195000),
            ],
            "Kingston": [
                ("NV2 500GB", "NVMe M.2 PCIe 4.0 3500MB/s", 38000),
                ("NV2 1TB", "NVMe M.2 PCIe 4.0 3500MB/s", 65000),
                ("KC3000 1TB", "NVMe M.2 PCIe 4.0 7000MB/s", 100000),
                ("NV3 2TB", "NVMe M.2 PCIe 4.0 6000MB/s", 145000),
            ],
            "Crucial": [
                ("BX500 480GB", "SATA III 2.5 540MB/s", 32000),
                ("MX500 1TB", "SATA III 2.5 560MB/s", 70000),
                ("T500 1TB", "NVMe M.2 PCIe 4.0 7300MB/s", 120000),
            ],
        },
        "stock_pesos": [0.4, 0.4, 0.2],
    },
    "Fuente_Poder": {
        "marcas": {
            "Corsair": [
                ("CV450", "450W 80 Plus Bronze", 45000),
                ("CX550", "550W 80 Plus Bronze", 62000),
                ("RM650", "650W 80 Plus Gold Full Modular", 95000),
                ("RM750e", "750W 80 Plus Gold Full Modular ATX 3.0", 110000),
                ("RM850x", "850W 80 Plus Gold Full Modular", 145000),
                ("HX1000i", "1000W 80 Plus Platinum Full Modular", 220000),
            ],
            "EVGA": [
                ("500 W1", "500W 80 Plus White No Modular", 45000),
                ("600 BR", "600W 80 Plus Bronze", 55000),
                ("750 GQ", "750W 80 Plus Gold Semi Modular", 95000),
                ("850 G7", "850W 80 Plus Gold Full Modular", 130000),
            ],
            "Cooler Master": [
                ("MWE 550 V2", "550W 80 Plus Bronze", 52000),
                ("MWE 750 V2", "750W 80 Plus Gold", 88000),
                ("V850 SFX Gold", "850W 80 Plus Gold SFX", 165000),
            ],
        },
        "stock_pesos": [0.4, 0.35, 0.25],
    },
    "Gabinete": {
        "marcas": {
            "Corsair": [
                ("4000D Airflow", "ATX Mid Tower Vidrio Templado", 85000),
                ("5000D Airflow", "ATX Mid Tower Panel Malla", 130000),
                ("6500X", "ATX Mid Tower Dual Chamber", 200000),
                ("Obsidian 1000D", "Full Tower Super Tower E-ATX", 450000),
            ],
            "NZXT": [
                ("H5 Flow", "ATX Mid Tower Minimalista", 80000),
                ("H6 Flow", "ATX Mid Torre Dual Chamber", 110000),
                ("H7 Elite", "ATX Mid Tower Premium Cristal", 165000),
                ("H9 Elite", "ATX Mid Torre Panoramica", 220000),
            ],
            "Lian Li": [
                ("LANCOOL 205M", "Micro-ATX Mesh", 55000),
                ("LANCOOL 216", "ATX Mid Tower Alto Flujo", 95000),
                ("O11 Dynamic EVO", "ATX Mid Tower Dual Chamber", 165000),
            ],
        },
        "stock_pesos": [0.4, 0.4, 0.2],
    },
    "Monitor": {
        "marcas": {
            "LG": [
                ("UltraGear 24GN60R", "24 IPS 1080p 165Hz 1ms", 190000),
                ("UltraGear 27GP850", "27 Nano IPS 1440p 180Hz", 350000),
                ("UltraGear 32GP850", "32 Nano IPS 1440p 165Hz", 420000),
                ("UltraGear 27GP950", "27 IPS 4K 160Hz HDMI 2.1", 680000),
            ],
            "Samsung": [
                ("Odyssey G3 LF24", "24 VA 1080p 165Hz FreeSync", 165000),
                ("Odyssey G5 27", "27 VA 1440p 144Hz Curvo", 280000),
                ("Odyssey G7 32", "32 VA 1440p 240Hz Curvo", 450000),
                ("Odyssey Neo G8 32", "32 VA 4K 240Hz Mini LED", 750000),
            ],
            "ASUS": [
                ("TUF VG249Q1A", "23.8 IPS 1080p 165Hz", 175000),
                ("TUF VG27AQ3A", "27 IPS 1440p 180Hz", 320000),
                ("ROG Swift PG27AQDM", "27 OLED 1440p 240Hz", 750000),
            ],
        },
        "stock_pesos": [0.3, 0.4, 0.3],
    },
    "Cooler_CPU": {
        "marcas": {
            "Cooler Master": [
                ("Hyper 212 Spectrum V3", "Torre Simple 120mm 150W TDP", 32000),
                ("MasterLiquid ML240L V2", "Liquida 240mm ARGB", 75000),
                ("MasterLiquid ML360 ION", "Liquida 360mm Pantalla LCD", 165000),
            ],
            "Noctua": [
                ("NH-D12L", "Torre Simple 120mm Cromax", 75000),
                ("NH-D15", "Torre Doble 140mm Premium 250W TDP", 110000),
            ],
            "DeepCool": [
                ("AK400", "Torre Simple 120mm 220W TDP", 28000),
                ("AK620", "Torre Doble 120mm 260W TDP", 65000),
                ("LT720", "Liquida 360mm Pantalla RGB", 135000),
            ],
            "Corsair": [
                ("H100i RGB Elite", "Liquida 240mm 170W TDP", 95000),
                ("H150i Elite Capellix", "Liquida 360mm RGB Premium", 155000),
                ("H170i Elite Capellix", "Liquida 420mm RGB Premium", 210000),
            ],
        },
        "stock_pesos": [0.3, 0.4, 0.3],
    },
}


class SyntheticCatalogGenerator(CatalogScraper):
    def __init__(self, seed: int = 42):
        self.seed = seed

    def generar(self, output_path: str, max_por_categoria: Optional[int] = None) -> str:
        random.seed(self.seed)
        filas = []

        for categoria, config in DATA.items():
            console.print(f"[dim]Generando {categoria}...[/dim]")
            todas_opciones = []
            for marca, productos in config["marcas"].items():
                for modelo, especs, precio in productos:
                    todas_opciones.append((marca, modelo, especs, precio))

            cantidad = min(max_por_categoria, len(todas_opciones)) if max_por_categoria else len(todas_opciones)
            seleccion = random.sample(todas_opciones, cantidad)

            for marca, modelo, especs, precio_base in seleccion:
                variacion = random.uniform(0.9, 1.1)
                precio = int(precio_base * variacion)
                stock = random.choices(["Alta", "Media", "Baja"], weights=config["stock_pesos"])[0]
                filas.append({
                    "Categoria": categoria,
                    "Marca": marca,
                    "Modelo": modelo,
                    "Especificaciones": especs,
                    "Precio_CLP": precio,
                    "Stock": stock,
                })

        df = pd.DataFrame(filas)
        df = self.validar_dataframe(df)
        df.to_csv(output_path, index=False)
        console.print(f"[bold yellow]Catalogo sintetico generado: {output_path} ({len(df)} productos)[/bold yellow]")
        return output_path
