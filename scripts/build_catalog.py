"""
build_catalog.py - Genera el catálogo de hardware para HardiBot.

Uso:
    python scripts/build_catalog.py                               # Híbrido: Knasta + SoloTodo + sintético
    python scripts/build_catalog.py --source solotodo             # Solo SoloTodo
    python scripts/build_catalog.py --source knasta               # Solo Knasta
    python scripts/build_catalog.py --source synthetic            # Solo sintético
    python scripts/build_catalog.py --max 20                      # 20 productos por categoría
    python scripts/build_catalog.py --output data/mi_catalogo.csv
    python scripts/build_catalog.py --preserve                    # No sobreescribir si ya existe
"""

import os
import sys
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.rule import Rule
from src.scrapers import SoloTodoScraper, SyntheticCatalogGenerator, KnastaScraper
from src.rag_engine import HardiBotRAG

console = Console(no_color=True, force_terminal=False)

CATALOGO_POR_DEFECTO = "data/catalogo_hardware.csv"


def build_catalog(source: str, max_per_category: int, output_path: str, preserve: bool = False):
    if preserve and os.path.exists(output_path):
        console.print(f"[yellow]⚠️ {output_path} ya existe. Saltando (--preserve activo).[/yellow]")
        return

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    console.print(Rule(title="HardiBot - Generador de Catalogo", style="bold green"))
    console.print(f"  Fuente: {source}")
    console.print(f"  Máx por categoría: {max_per_category}")
    console.print(f"  Salida: {output_path}\n")

    if source == "solotodo":
        scraper = SoloTodoScraper()
        scraper.generar(output_path, max_por_categoria=max_per_category)
    elif source == "knasta":
        scraper = KnastaScraper()
        scraper.generar(output_path, max_por_categoria=max_per_category)
    elif source == "synthetic":
        generator = SyntheticCatalogGenerator()
        generator.generar(output_path, max_por_categoria=max_per_category)
    elif source == "hybrid":
        exito = False

        # 1. Knasta (fuente primaria)
        try:
            s = KnastaScraper()
            s.generar(output_path, max_por_categoria=max_per_category)
            console.print("[green]✓ Catálogo generado desde Knasta[/green]")
            exito = True
        except Exception as e:
            console.print(f"[yellow]⚠️ Knasta falló: {e}[/yellow]")

        # 2. SoloTodo (fallback si Knasta no funcionó, complemento si no)
        if not exito:
            try:
                s = SoloTodoScraper()
                s.generar(output_path, max_por_categoria=max_per_category)
                console.print("[green]✓ Catálogo generado desde SoloTodo[/green]")
                exito = True
            except Exception as e:
                console.print(f"[yellow]⚠️ SoloTodo falló: {e}[/yellow]")

        # 3. Sintético (último recurso)
        if not exito:
            console.print("[yellow]→ Usando fallback sintético...[/yellow]")
            generator = SyntheticCatalogGenerator()
            generator.generar(output_path, max_por_categoria=max_per_category)
            exito = True

    with open(output_path, encoding="utf-8") as f:
        total = sum(1 for _ in f) - 1
    console.print(f"\n[bold]Total de productos: {total}[/bold]")

    console.print("\n[bold cyan]⚡ Reconstruyendo índice FAISS...[/bold cyan]")
    rag = HardiBotRAG(data_path=output_path)
    if rag.construir_indice():
        console.print("[bold green]✅ Índice FAISS actualizado exitosamente[/bold green]")
    else:
        console.print("[bold red]❌ Error al reconstruir índice FAISS[/bold red]")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Genera el catálogo de hardware para HardiBot")
    parser.add_argument("--source", choices=["solotodo", "knasta", "synthetic", "hybrid"],
                        default="hybrid", help="Fuente de datos (default: hybrid)")
    parser.add_argument("--max", type=int, default=15,
                        help="Máximo de productos por categoría (default: 15)")
    parser.add_argument("--output", default=CATALOGO_POR_DEFECTO,
                        help=f"Ruta del CSV de salida (default: {CATALOGO_POR_DEFECTO})")
    parser.add_argument("--preserve", action="store_true",
                        help="No sobreescribir si el archivo ya existe")
    args = parser.parse_args()

    build_catalog(args.source, args.max, args.output, preserve=args.preserve)


if __name__ == "__main__":
    main()
