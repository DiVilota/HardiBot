import os
import json
import tempfile
import pytest
import requests
import pandas as pd
from unittest.mock import patch, MagicMock
from src.scrapers.base import CatalogScraper
from src.scrapers.synthetic import SyntheticCatalogGenerator
from src.scrapers.knasta import KnastaScraper, CATEGORIAS_KNASTA


class TestBaseScraper:
    def setup_method(self):
        self.scraper = SyntheticCatalogGenerator()

    def test_validar_dataframe_con_columnas_correctas(self):
        df = pd.DataFrame([{
            "Categoria": "Procesador",
            "Marca": "AMD",
            "Modelo": "Ryzen 5 5600G",
            "Especificaciones": "6 nucleos, 3.9 GHz",
            "Precio_CLP": 150000,
            "Stock": "Alta",
        }])
        result = self.scraper.validar_dataframe(df)
        assert len(result) == 1
        assert result["Precio_CLP"].iloc[0] == 150000

    def test_validar_dataframe_precio_string_a_int(self):
        df = pd.DataFrame([{
            "Categoria": "Procesador",
            "Marca": "AMD",
            "Modelo": "Ryzen 5",
            "Especificaciones": "6 nucleos",
            "Precio_CLP": "150000",
            "Stock": "Alta",
        }])
        result = self.scraper.validar_dataframe(df)
        assert int(result["Precio_CLP"].iloc[0]) == 150000

    def test_validar_dataframe_falta_columna(self):
        df = pd.DataFrame([{
            "Categoria": "Procesador",
            "Marca": "AMD",
        }])
        with pytest.raises(ValueError, match="no encontrada"):
            self.scraper.validar_dataframe(df)

    def test_validar_dataframe_remueve_nan_precio(self):
        df = pd.DataFrame([{
            "Categoria": "Procesador",
            "Marca": "AMD",
            "Modelo": "Ryzen 5",
            "Especificaciones": "6 nucleos",
            "Precio_CLP": None,
            "Stock": "Alta",
        }])
        result = self.scraper.validar_dataframe(df)
        assert result["Precio_CLP"].iloc[0] == 0


class TestSyntheticScraper:
    def test_genera_catalogo_basico(self):
        gen = SyntheticCatalogGenerator()
        path = gen.generar(
            os.path.join(tempfile.gettempdir(), "test_synthetic.csv"),
            max_por_categoria=2,
        )
        assert os.path.exists(path)
        df = pd.read_csv(path)
        assert len(df) > 0
        for col in CatalogScraper.REQUIRED_COLUMNS:
            assert col in df.columns

    def test_genera_categorias_multiples(self):
        gen = SyntheticCatalogGenerator()
        path = gen.generar(
            os.path.join(tempfile.gettempdir(), "test_synthetic2.csv"),
            max_por_categoria=3,
        )
        df = pd.read_csv(path)
        categorias = df["Categoria"].unique()
        assert len(categorias) >= 5

    def test_precios_en_rango_razonable(self):
        gen = SyntheticCatalogGenerator()
        path = gen.generar(
            os.path.join(tempfile.gettempdir(), "test_synthetic3.csv"),
            max_por_categoria=5,
        )
        df = pd.read_csv(path)
        assert df["Precio_CLP"].min() > 0
        assert df["Precio_CLP"].max() < 5_000_000


class TestKnastaScraper:
    NEXT_DATA_TEMPLATE = {
        "props": {
            "pageProps": {
                "initialData": {
                    "count": 3,
                    "total_pages": 1,
                    "products": [
                        {
                            "title": "Procesador AMD Ryzen 5 5600G 6-Core 3.9GHz",
                            "brand": "AMD",
                            "current_price": 150000,
                            "is_premium": True,
                            "url": "/producto/ryzen-5",
                        },
                        {
                            "title": "Procesador Intel Core i5-12400F 6-Core 2.5GHz",
                            "brand": "Intel",
                            "current_price": 130000,
                            "is_premium": False,
                            "url": "/producto/i5-12400f",
                        },
                        {
                            "title": "Procesador AMD Athlon 3000G",
                            "brand": None,
                            "current_price": 50000,
                            "is_premium": False,
                            "url": "/producto/athlon-3000g",
                        },
                    ],
                }
            }
        }
    }

    def _make_response(self, status_code=200, next_data=None):
        if next_data is None:
            next_data = self.NEXT_DATA_TEMPLATE
        mock = MagicMock()
        mock.status_code = status_code
        mock.text = '<script id="__NEXT_DATA__" type="application/json">{}</script>'.format(
            json.dumps(next_data)
        )
        return mock

    def test_genera_catalogo_desde_html(self):
        scraper = KnastaScraper()

        with patch.object(scraper.session, "get", return_value=self._make_response()):
            path = scraper.generar(
                os.path.join(tempfile.gettempdir(), "test_knasta_mock.csv"),
                max_por_categoria=2,
            )

        assert os.path.exists(path)
        df = pd.read_csv(path)
        assert len(df) == 2
        assert "AMD" in df["Marca"].values

    def test_precios_son_enteros(self):
        scraper = KnastaScraper()

        with patch.object(scraper.session, "get", return_value=self._make_response()):
            path = scraper.generar(
                os.path.join(tempfile.gettempdir(), "test_knasta_int.csv"),
                max_por_categoria=5,
            )

        df = pd.read_csv(path)
        assert df["Precio_CLP"].dtype in ("int64", "int32")

    def test_stock_es_valor_valido(self):
        scraper = KnastaScraper()

        with patch.object(scraper.session, "get", return_value=self._make_response()):
            path = scraper.generar(
                os.path.join(tempfile.gettempdir(), "test_knasta_stock.csv"),
                max_por_categoria=5,
            )

        df = pd.read_csv(path)
        for stock in df["Stock"]:
            assert stock in ("Alta", "Media", "Baja")

    def test_categorias_tienen_mapping(self):
        scraper = KnastaScraper()
        assert len(CATEGORIAS_KNASTA) == 7
        assert "Procesador" in CATEGORIAS_KNASTA
        assert "Tarjeta_Video" in CATEGORIAS_KNASTA
        assert "Monitor" in CATEGORIAS_KNASTA

    def test_pagina_con_error_devuelve_fallback(self):
        scraper = KnastaScraper()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")

        with patch.object(scraper.session, "get", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Knasta"):
                scraper.generar(
                    os.path.join(tempfile.gettempdir(), "test_knasta_fail.csv"),
                    max_por_categoria=2,
                )
