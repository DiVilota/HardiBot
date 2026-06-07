from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class CatalogScraper(ABC):
    """Interfaz base para generadores de catálogo."""

    REQUIRED_COLUMNS = ["Categoria", "Marca", "Modelo", "Especificaciones", "Precio_CLP", "Stock"]

    @abstractmethod
    def generar(self, output_path: str, max_por_categoria: Optional[int] = None) -> str:
        ...

    def validar_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Columna requerida '{col}' no encontrada en los datos generados")
        df["Precio_CLP"] = pd.to_numeric(df["Precio_CLP"], errors="coerce").fillna(0).astype(int)
        return df
