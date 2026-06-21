import time

class TestCacheSemantico:
    def setup_method(self):
        from src.scalability.cache_semantico import CacheSemantico
        self.cache = CacheSemantico(umbral=0.85, ttl=3600)

    def test_cosine_similarity(self):
        sim = self.cache._similitud_coseno("procesador ryzen 5", "procesador ryzen 7")
        assert 0.0 < sim <= 1.0

    def test_guardar_y_hit_semantico(self):
        self.cache.guardar("procesador ryzen 5 precio", "respuesta ryzen")
        resultado = self.cache.buscar("precio procesador ryzen 5")
        assert resultado is not None
        assert resultado == "respuesta ryzen"

    def test_miss_por_baja_similitud(self):
        self.cache.guardar("procesador intel i7", "respuesta intel")
        resultado = self.cache.buscar("memoria ram ddr5 precio")
        assert resultado is None

    def test_ttl_expirado(self):
        from src.scalability.cache_semantico import CacheSemantico
        cache = CacheSemantico(umbral=0.85, ttl=0)
        cache.guardar("procesador", "respuesta")
        resultado = cache.buscar("procesador")
        assert resultado is None

    def test_normalizar_texto(self):
        texto = self.cache._normalizar("Hola Mundo!!! 123")
        assert texto == "hola mundo 123"

    def test_tokens_ahorrados(self):
        self.cache.guardar("producto x precio", "respuesta x")
        self.cache.buscar("producto x precio")
        entrada = self.cache.entradas[list(self.cache.entradas.keys())[0]]
        assert entrada.accesos == 1
        assert entrada.tokens_ahorrados > 0
