import os
import pandas as pd
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from rich.console import Console

console = Console()
load_dotenv(override=True)

CATALOGO_POR_DEFECTO = "data/catalogo_hardware.csv"


class HardiBotRAG:
    def __init__(self, data_path: str = CATALOGO_POR_DEFECTO):
        self.data_path = data_path
        self.vector_store = None

        try:
            self.embeddings = OpenAIEmbeddings(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("GITHUB_TOKEN"),
                model="text-embedding-3-small"
            )
        except Exception as e:
            console.print(f"[red]Error al cargar Embeddings: {e}[/red]")

    def construir_indice(self):
        console.print("[dim]⚙️ Iniciando ingesta de datos (RAG)...[/dim]")

        if not os.path.exists(self.data_path):
            console.print(f"[red]❌ No se encontró el catálogo en: {self.data_path}[/red]")
            return False

        df = pd.read_csv(self.data_path)
        documents = []

        for _, row in df.iterrows():
            chunk_content = (
                f"Componente: {row['Categoria']}\n"
                f"Producto: {row['Marca']} {row['Modelo']}\n"
                f"Especificaciones Técnicas: {row['Especificaciones']}\n"
                f"Precio: ${row['Precio_CLP']} CLP\n"
                f"Disponibilidad de Stock: {row['Stock']}"
            )

            doc = Document(
                page_content=chunk_content,
                metadata={"categoria": row['Categoria'], "marca": row['Marca']}
            )
            documents.append(doc)

        try:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            console.print(f"[bold green]✅ Índice Vectorial FAISS creado: {len(documents)} productos indexados.[/bold green]")
            return True
        except Exception as e:
            console.print(f"[bold red]❌ Error al vectorizar: {e}[/bold red]")
            return False

    def recargar(self, data_path: str = None):
        if data_path:
            self.data_path = data_path
        return self.construir_indice()

    def recuperar_contexto(self, query: str, top_k: int = 5) -> str:
        if not self.vector_store:
            console.print("[yellow]⚠️ Índice vacío. Construyendo índice primero...[/yellow]")
            self.construir_indice()

        resultados = self.vector_store.similarity_search(query, k=top_k)

        contexto = "\n---\n".join([doc.page_content for doc in resultados])
        return contexto

    @property
    def total_productos(self) -> int:
        if os.path.exists(self.data_path):
            return sum(1 for _ in open(self.data_path)) - 1
        return 0


if __name__ == "__main__":
    motor = HardiBotRAG()
    exito = motor.construir_indice()

    if exito:
        print("\n--- TEST DE RECUPERACIÓN ---")
        busqueda = "Quiero una tarjeta de video barata para jugar en 1080p"
        print(f"Query: '{busqueda}'\n")

        resultados = motor.recuperar_contexto(busqueda)
        print("Resultados recuperados por FAISS:")
        print(resultados)
