class TestCacheLLM:
    def setup_method(self):
        from src.scalability.cache_llm import CacheLLM
        self.cache = CacheLLM(max_size=3)

    def test_hash_consistente(self):
        h1 = self.cache._hash("prompt x", "gpt-4o")
        h2 = self.cache._hash("prompt x", "gpt-4o")
        assert h1 == h2
        assert len(h1) == 16

    def test_guardar_y_obtener(self):
        self.cache.guardar("consulta", "gpt-4o", "respuesta")
        assert self.cache.obtener("consulta", "gpt-4o") == "respuesta"

    def test_fifo_eviction(self):
        self.cache.guardar("q1", "m", "r1")
        self.cache.guardar("q2", "m", "r2")
        self.cache.guardar("q3", "m", "r3")
        self.cache.guardar("q4", "m", "r4")
        assert self.cache.obtener("q1", "m") is None
        assert self.cache.obtener("q4", "m") == "r4"

    def test_hit_miss_stats(self):
        self.cache.guardar("q1", "m", "r1")
        self.cache.obtener("q1", "m")
        self.cache.obtener("q2", "m")
        stats = self.cache.estadisticas()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["tasa_acierto"] == 50.0

    def test_cache_vacio_retorna_none(self):
        assert self.cache.obtener("no_existe", "gpt-4o") is None
