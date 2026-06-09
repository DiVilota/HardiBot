import sys
from unittest.mock import MagicMock, patch

# Parchea la clase HardiBotAppState ANTES de que core.py se importe,
# para evitar la inicializacion real de FAISS + OpenAI durante los tests.
_mock_state = MagicMock()
_mock_state.persona_id = "hardware"
_mock_state.nombre_bot = "HardiBot"
_mock_state.titulo_bot = "Test"
_mock_state.config = {"nombre": "HardiBot", "moneda": "CLP", "titulo": "Test", "catalogo": "data/test.csv"}
_mock_state.carrito = MagicMock()
_mock_state.motor_rag = MagicMock()
_mock_state.llm = MagicMock()
_mock_state.agent = MagicMock()
_mock_state.memoria = MagicMock()
_mock_state.prompt = "prompt de test"
_mock_state.iniciar.return_value = _mock_state

_patcher = patch("src.core.HardiBotAppState", return_value=_mock_state)
_patcher.start()
