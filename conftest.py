import sys
import warnings

from unittest.mock import MagicMock, patch

# Suprime DeprecationWarning de faiss (SwigPyPacked/SwigPyObject/swigvarlink)
# en Python 3.12+. Es un problema conocido de faiss-cpu 1.13.x, no de nuestro codigo.
warnings.filterwarnings("ignore", message="builtin type SwigPyPacked has no __module__")
warnings.filterwarnings("ignore", message="builtin type SwigPyObject has no __module__")
warnings.filterwarnings("ignore", message="builtin type swigvarlink has no __module__")

# Suprime deprecation de LangGraph: create_react_agent se movio a langchain.agents
# pero la ruta nueva aun no existe en la version instalada de langchain.
warnings.filterwarnings("ignore", message="create_react_agent has been moved")

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
