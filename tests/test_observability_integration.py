class TestObservabilityIntegration:
    def test_turno_reconstruye_arbol(self):
        from src.observability.tracing import SistemaTrazas

        st = SistemaTrazas()
        st.iniciar_traza("turno_completo", trace_id="integ-001")
        raiz = st.iniciar_span("clasificar_intencion")
        h1 = st.iniciar_span("busqueda_rag_faiss", parent_span_id=raiz.span_id)
        h11 = st.iniciar_span("construir_query_faiss", parent_span_id=h1.span_id)
        st.finalizar_span(h11)
        h12 = st.iniciar_span("ejecutar_similarity_search", parent_span_id=h1.span_id)
        st.finalizar_span(h12)
        st.finalizar_span(h1)
        h2 = st.iniciar_span("llamada_llm_gpt4o", parent_span_id=raiz.span_id)
        h21 = st.iniciar_span("armar_prompt", parent_span_id=h2.span_id)
        st.finalizar_span(h21)
        h22 = st.iniciar_span("call_chat_completion", parent_span_id=h2.span_id)
        st.finalizar_span(h22)
        st.finalizar_span(h2)
        st.finalizar_span(raiz)
        st.finalizar_traza()

        arbol = st.arbol_spans("integ-001")
        assert arbol["trace_id"] == "integ-001"
        assert len(arbol["hijos"]) == 1
        raiz_arbol = arbol["hijos"][0]
        assert raiz_arbol["nombre"] == "clasificar_intencion"
        assert len(raiz_arbol["hijos"]) == 2
        nombres_hijos = [h["nombre"] for h in raiz_arbol["hijos"]]
        assert "busqueda_rag_faiss" in nombres_hijos
        assert "llamada_llm_gpt4o" in nombres_hijos

    def test_trace_id_consistente_il3_1_il3_2(self):
        from src.observability.tracing import SistemaTrazas

        trace_id_compartido = "shared-trace-001"
        st = SistemaTrazas()
        st.iniciar_traza("consulta_usuario", trace_id=trace_id_compartido)
        span = st.iniciar_span("procesar")
        st.finalizar_span(span)
        st.finalizar_traza()

        assert st.trazas[0].trace_id == trace_id_compartido
        for s in st.trazas[0].spans:
            assert s.trace_id == trace_id_compartido

        traza = st.obtener_traza(trace_id_compartido)
        assert traza is not None
        assert traza.trace_id == trace_id_compartido
