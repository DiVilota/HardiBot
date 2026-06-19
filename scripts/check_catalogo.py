"""Check catalog contents and scraper setup."""
import sys, os, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Check catalog
df = pd.read_csv("data/catalogo_hardware.csv")
print(f"Total productos en catalogo: {len(df)}")
print(f"Categorias: {df['Categoria'].value_counts().to_dict()}")
rams = df[df["Categoria"].str.contains("RAM|Memoria", case=False, na=False)]
print(f"Productos RAM en catalogo: {len(rams)}")
for _, r in rams.iterrows():
    print(f"  {r['Marca']} {r['Modelo']} - ${r['Precio_CLP']:,} CLP".replace(",", "."))

# Check where the catalog comes from - inspect CSV source
print(f"\nOrigen del catalogo: data/catalogo_hardware.csv")
print(f"Primeras 3 filas:\n{df.head(3).to_string()}")

# Check if Knasta scraper is importable and what it would provide
from src.scrapers.knasta import KnastaScraper, CATEGORIAS_KNASTA
print(f"\nCategorias Knasta disponibles: {list(CATEGORIAS_KNASTA.keys())}")
print(f"La categoria 'Memoria_RAM' existe en Knasta: {'Memoria_RAM' in CATEGORIAS_KNASTA}")
