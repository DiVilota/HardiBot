class TestModelRouter:
    def test_simple_rapido(self):
        from src.scalability.model_router import clasificar_complejidad, NIVEL_RAPIDO
        nivel = clasificar_complejidad("Hola que es una RAM?")
        assert nivel == NIVEL_RAPIDO

    def test_estandar(self):
        from src.scalability.model_router import clasificar_complejidad, NIVEL_ESTANDAR
        nivel = clasificar_complejidad("Analiza las diferencias entre AMD e Intel en 2025")
        assert nivel == NIVEL_ESTANDAR

    def test_avanzado(self):
        from src.scalability.model_router import clasificar_complejidad, NIVEL_AVANZADO
        nivel = clasificar_complejidad("Evalua la arquitectura de un sistema multi-paso con razonamiento complejo")
        assert nivel == NIVEL_AVANZADO

    def test_palabras_clave_estandar(self):
        from src.scalability.model_router import clasificar_complejidad, NIVEL_ESTANDAR
        nivel = clasificar_complejidad("Compara el rendimiento de estos componentes")
        assert nivel == NIVEL_ESTANDAR

    def test_seleccionar_modelo_rapido(self):
        from src.scalability.model_router import seleccionar_modelo
        modelo = seleccionar_modelo("Hola mundo")
        assert modelo.nombre == "gpt-4o-mini"
