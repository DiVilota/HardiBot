class TestBatchProcessor:
    def setup_method(self):
        from src.scalability.batch_processor import ProcesadorLotes
        self.procesador = ProcesadorLotes(tamano_lote=2)

    def test_agregar_solicitud(self):
        from src.scalability.batch_processor import Solicitud, PRIORIDAD_NORMAL
        req = Solicitud("1", "consulta", PRIORIDAD_NORMAL)
        self.procesador.agregar(req)
        assert len(self.procesador.cola) == 1

    def test_prioridad_critica_antes_que_baja(self):
        from src.scalability.batch_processor import Solicitud, PRIORIDAD_CRITICA, PRIORIDAD_BAJA
        baja = Solicitud(id="1", pregunta="baja", prioridad=PRIORIDAD_BAJA)
        critica = Solicitud(id="2", pregunta="critica", prioridad=PRIORIDAD_CRITICA)
        self.procesador.agregar(baja)
        self.procesador.agregar(critica)
        siguiente = self.procesador._siguiente()
        assert siguiente.id == "2"

    def test_procesar_lote_por_prioridad(self):
        from src.scalability.batch_processor import Solicitud, PRIORIDAD_ALTA, PRIORIDAD_BAJA
        self.procesador.agregar(Solicitud(id="1", pregunta="baja", prioridad=PRIORIDAD_BAJA))
        self.procesador.agregar(Solicitud(id="2", pregunta="alta", prioridad=PRIORIDAD_ALTA))
        lote = self.procesador.obtener_lote()
        assert len(lote) == 2

    def test_resumen_con_datos(self):
        from src.scalability.batch_processor import Solicitud, PRIORIDAD_NORMAL
        self.procesador.agregar(Solicitud(id="1", pregunta="consulta", prioridad=PRIORIDAD_NORMAL))
        resumen = self.procesador.resumen()
        assert "total_solicitudes" in resumen
        assert resumen["total_solicitudes"] == 1

    def test_procesar_vacio(self):
        lote = self.procesador.obtener_lote()
        assert lote == []

    def test_tamano_lote_respetado(self):
        from src.scalability.batch_processor import Solicitud, PRIORIDAD_NORMAL
        for i in range(5):
            self.procesador.agregar(Solicitud(id=str(i), pregunta=f"q{i}", prioridad=PRIORIDAD_NORMAL))
        lote = self.procesador.obtener_lote()
        assert len(lote) == 2
