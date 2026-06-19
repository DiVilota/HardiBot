import time
import json
import os


class TestTracing:
    def test_span_duracion(self):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas()
        st.iniciar_traza("test")
        span = st.iniciar_span("op_test")
        time.sleep(0.01)
        st.finalizar_span(span)

        assert span.estado == "EXITOSO"
        assert span.duracion_ms > 0
        assert span.span_id is not None
        assert span.trace_id is not None

    def test_jerarquia_padre_hijo(self):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas()
        st.iniciar_traza("jerarquia")
        padre = st.iniciar_span("padre")
        hijo = st.iniciar_span("hijo", parent_span_id=padre.span_id)
        st.finalizar_span(hijo)
        st.finalizar_span(padre)

        assert hijo.parent_span_id == padre.span_id
        assert padre.parent_span_id is None

    def test_arbol_spans(self):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas()
        st.iniciar_traza("arbol_test")
        raiz = st.iniciar_span("raiz")
        h1 = st.iniciar_span("hijo1", parent_span_id=raiz.span_id)
        h2 = st.iniciar_span("hijo2", parent_span_id=raiz.span_id)
        st.finalizar_span(h1)
        st.finalizar_span(h2)
        st.finalizar_span(raiz)
        st.finalizar_traza()

        arbol = st.arbol_spans(st.trazas[0].trace_id)
        assert arbol["trace_id"] == st.trazas[0].trace_id
        assert len(arbol["hijos"]) == 1
        assert arbol["hijos"][0]["nombre"] == "raiz"
        assert len(arbol["hijos"][0]["hijos"]) == 2

    def test_cascada_temporal(self):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas()
        st.iniciar_traza("cascada")
        s1 = st.iniciar_span("primero")
        time.sleep(0.005)
        s2 = st.iniciar_span("segundo", parent_span_id=s1.span_id)
        st.finalizar_span(s2)
        st.finalizar_span(s1)
        st.finalizar_traza()

        cascada = st.cascada_temporal(st.trazas[0].trace_id)
        assert len(cascada) >= 2
        assert cascada[0]["nombre"] == "primero"
        assert cascada[0]["nivel"] == 0

    def test_guardar_jsonl(self, tmp_path):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas(log_dir=str(tmp_path))
        st.iniciar_traza("guardado_test")
        span = st.iniciar_span("span_test")
        st.finalizar_span(span)
        st.finalizar_traza()
        st.guardar()

        log_path = os.path.join(str(tmp_path), "trazas.jsonl")
        assert os.path.exists(log_path)
        with open(log_path, "r") as f:
            linea = f.readline().strip()
            assert linea
            entry = json.loads(linea)
            assert entry["trace_id"] == st.trazas[0].trace_id
            assert len(entry["spans"]) == 1
            assert entry["spans"][0]["nombre"] == "span_test"

    def test_cargar_trazas(self, tmp_path):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas(log_dir=str(tmp_path))
        st.iniciar_traza("carga_test")
        span = st.iniciar_span("span_a")
        st.finalizar_span(span)
        st.finalizar_traza()
        st.guardar()

        cargadas = SistemaTrazas.cargar_trazas(log_dir=str(tmp_path))
        assert len(cargadas) == 1
        assert cargadas[0]["nombre"] == "carga_test"
