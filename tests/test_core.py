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
