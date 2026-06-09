import pytest
from src.core import operacion_segura, CarritoCompras


class TestOperacionSegura:
    def test_suma(self):
        assert operacion_segura("150000 + 50000") == 200000

    def test_resta(self):
        assert operacion_segura("200000 - 50000") == 150000

    def test_multiplicacion(self):
        assert operacion_segura("3 * 50000") == 150000

    def test_division(self):
        assert operacion_segura("100000 / 2") == 50000.0

    def test_expresion_compuesta(self):
        assert operacion_segura("(100000 + 50000) * 2") == 300000

    def test_floats(self):
        assert operacion_segura("1500.50 + 2500.50") == 4001.0

    def test_rechaza_strings(self):
        with pytest.raises((ValueError, TypeError)):
            operacion_segura("'texto'")

    def test_rechaza_llamadas(self):
        with pytest.raises((ValueError, TypeError)):
            operacion_segura("__import__('os')")


class TestCarritoCompras:
    def setup_method(self):
        self.carrito = CarritoCompras()

    def test_agregar_producto(self):
        resultado = self.carrito.agregar("Ryzen 5 5600G", 1, 150000)
        assert "agregado exitosamente" in resultado
        assert len(self.carrito.items) == 1

    def test_ver_carrito(self):
        self.carrito.agregar("Ryzen 5 5600G", 1, 150000)
        self.carrito.agregar("Placa B550M", 1, 85000)
        resultado = self.carrito.ver()
        assert "precio_total" in resultado
        assert "235000" in resultado

    def test_carrito_vacio(self):
        resultado = self.carrito.ver()
        assert "mensaje" in resultado
        assert "vacío" in resultado or "vac" in resultado

    def test_subtotal_correcto(self):
        self.carrito.agregar("RAM DDR4", 2, 25000)
        item = self.carrito.items[0]
        assert item["subtotal"] == 50000

    def test_limpiar(self):
        self.carrito.agregar("Ryzen 5", 1, 150000)
        self.carrito.limpiar()
        assert len(self.carrito.items) == 0


class TestToolCaptureHandler:
    def setup_method(self):
        from src.core import ToolCaptureHandler
        self.handler = ToolCaptureHandler()

    def test_captura_tool_start(self):
        from langchain_core.callbacks import base
        self.handler.on_tool_start({"name": "buscar_catalogo"}, "Ryzen 5 5600G")
        assert len(self.handler.tool_calls) == 1
        assert self.handler.tool_calls[0]["name"] == "buscar_catalogo"
        assert self.handler.tool_calls[0]["status"] == "running"

    def test_captura_tool_end(self):
        self.handler.on_tool_start({"name": "buscar_catalogo"}, "Ryzen 5")
        self.handler.on_tool_end("Resultado: Ryzen 5 5600G, $150,000 CLP")
        assert self.handler.tool_calls[0]["status"] == "complete"
        assert "Resultado" in self.handler.tool_calls[0]["output"]
        assert self.handler.tool_calls[0]["duration"] is not None

    def test_multiples_herramientas(self):
        self.handler.on_tool_start({"name": "buscar_catalogo"}, "Ryzen 5")
        self.handler.on_tool_end("Encontrado")
        self.handler.on_tool_start({"name": "calcular_presupuesto"}, "150000 + 50000")
        self.handler.on_tool_end("200000")
        assert len(self.handler.tool_calls) == 2
        assert self.handler.tool_calls[0]["name"] == "buscar_catalogo"
        assert self.handler.tool_calls[1]["name"] == "calcular_presupuesto"

    def test_sin_herramientas(self):
        assert len(self.handler.tool_calls) == 0
