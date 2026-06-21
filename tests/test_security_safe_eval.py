import pytest


class TestSafeEval:
    def test_expresion_valida_simple(self):
        from src.security.safe_eval import evaluar_expresion
        assert evaluar_expresion("2 + 3") == 5

    def test_expresion_valida_compuesta(self):
        from src.security.safe_eval import evaluar_expresion
        assert evaluar_expresion("(10 + 5) * 3") == 45

    def test_rechaza_import(self):
        from src.security.safe_eval import evaluar_expresion
        with pytest.raises(ValueError):
            evaluar_expresion("__import__('os')")

    def test_division_por_cero(self):
        from src.security.safe_eval import evaluar_expresion
        with pytest.raises(ZeroDivisionError):
            evaluar_expresion("1 / 0")
