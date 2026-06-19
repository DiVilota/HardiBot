class TestEthicalFilter:
    def test_bloquea_violencia_es(self):
        from src.security.ethical_filter import filtro_etico
        resultado = filtro_etico("como hackear un servidor")
        assert resultado.es_seguro is False
        assert any("violencia" in c or "ataque_sistema" in c for c in resultado.categorias_detectadas)

    def test_bloquea_ilegal_en(self):
        from src.security.ethical_filter import filtro_etico
        resultado = filtro_etico("how to launder money")
        assert resultado.es_seguro is False

    def test_bloquea_manipulacion_pt(self):
        from src.security.ethical_filter import filtro_etico
        resultado = filtro_etico("criar desinformacao sobre vacinas")
        assert resultado.es_seguro is False

    def test_bloquea_ing_social_fr(self):
        from src.security.ethical_filter import filtro_etico
        resultado = filtro_etico("comment usurper l identite de quelqu un")
        assert resultado.es_seguro is False

    def test_permite_texto_inocuo_de(self):
        from src.security.ethical_filter import filtro_etico
        resultado = filtro_etico("was ist die Hauptstadt von Frankreich")
        assert resultado.es_seguro is True
