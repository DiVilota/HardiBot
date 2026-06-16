import os
import tempfile
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


def _crear_csv_temporal():
    path = os.path.join(tempfile.gettempdir(), "test_catalogo_rag.csv")
    df = pd.DataFrame([
        {
            "Categoria": "Procesador",
            "Marca": "AMD",
            "Modelo": "Ryzen 5 5600G",
            "Especificaciones": "6 nucleos, 3.9 GHz, AM4",
            "Precio_CLP": 150000,
            "Stock": "Alta",
        },
        {
            "Categoria": "Tarjeta_Video",
            "Marca": "Nvidia",
            "Modelo": "RTX 3060",
            "Especificaciones": "12GB GDDR6, PCIe 4.0",
            "Precio_CLP": 300000,
            "Stock": "Media",
        },
        {
            "Categoria": "Placa_Madre",
            "Marca": "Asus",
            "Modelo": "B550M-K",
            "Especificaciones": "AM4, DDR4, mATX",
            "Precio_CLP": 85000,
            "Stock": "Baja",
        },
    ])
    df.to_csv(path, index=False)
    return path


class TestHardiBotRAG:
    @patch("src.rag_engine.OpenAIEmbeddings", autospec=True)
    def test_construir_indice_exitoso(self, mock_embeddings):
        from src.rag_engine import HardiBotRAG

        csv_path = _crear_csv_temporal()
        rag = HardiBotRAG(data_path=csv_path)

        with patch("src.rag_engine.FAISS") as mock_faiss:
            mock_faiss.from_documents.return_value = MagicMock()
            result = rag.construir_indice()
            assert result is True
            assert rag.vector_store is not None

    @patch("src.rag_engine.OpenAIEmbeddings", autospec=True)
    def test_construir_indice_csv_no_existe(self, mock_embeddings):
        from src.rag_engine import HardiBotRAG

        rag = HardiBotRAG(data_path="/no/existe/nunca.csv")
        result = rag.construir_indice()
        assert result is False

    @patch("src.rag_engine.OpenAIEmbeddings", autospec=True)
    def test_total_productos(self, mock_embeddings):
        from src.rag_engine import HardiBotRAG

        csv_path = _crear_csv_temporal()
        rag = HardiBotRAG(data_path=csv_path)
        assert rag.total_productos == 3

    @patch("src.rag_engine.OpenAIEmbeddings", autospec=True)
    def test_recuperar_contexto_keyword(self, mock_embeddings):
        from src.rag_engine import HardiBotRAG

        csv_path = _crear_csv_temporal()
        rag = HardiBotRAG(data_path=csv_path)

        with patch("src.rag_engine.FAISS") as mock_faiss:
            mock_faiss.from_documents.return_value = MagicMock()
            rag.construir_indice()

        resultado = rag.recuperar_contexto("Quiero un ryzen economico", top_k=3)
        assert "Ryzen 5" in resultado
        assert "150" in resultado

    @patch("src.rag_engine.OpenAIEmbeddings", autospec=True)
    def test_recuperar_contexto_faiss_fallback(self, mock_embeddings):
        from src.rag_engine import HardiBotRAG

        csv_path = _crear_csv_temporal()
        rag = HardiBotRAG(data_path=csv_path)

        mock_store = MagicMock()
        mock_store.similarity_search.return_value = [
            MagicMock(page_content="Producto: AMD Ryzen 5 5600G\nPrecio: 150000 CLP"),
        ]
        with patch("src.rag_engine.FAISS") as mock_faiss:
            mock_faiss.from_documents.return_value = mock_store
            rag.construir_indice()

        resultado = rag.recuperar_contexto("xyz no existe", top_k=2)
        assert len(resultado) > 0

    @patch("src.rag_engine.OpenAIEmbeddings", autospec=True)
    def test_recargar_cambia_data_path(self, mock_embeddings):
        from src.rag_engine import HardiBotRAG

        csv_path = _crear_csv_temporal()
        rag = HardiBotRAG(data_path=csv_path)

        with patch("src.rag_engine.FAISS") as mock_faiss:
            mock_faiss.from_documents.return_value = MagicMock()
            result = rag.recargar()
            assert result is True
