"""Genera catalogos demo para Ferreteria y Repuestos."""
import csv
import os

BASE = "data"

FERRETERIA = [
    ('Herramienta_Manual', 'Stanley', 'Martillo de Una 16oz', 'Mango de fibra de vidrio, cabeza forjada', 14990, 'Alta'),
    ('Herramienta_Manual', 'Stanley', 'Destornillador Phillips #2', 'Punta cruz, mango ergonomico 6"', 5990, 'Alta'),
    ('Herramienta_Manual', 'Stanley', 'Destornillador Plano 5/16"', 'Punta plana, mango ergonomico 6"', 5490, 'Alta'),
    ('Herramienta_Manual', 'Stanley', 'Llave Ajustable 10"', 'Acero al carbono, cromo vanadio', 18990, 'Media'),
    ('Herramienta_Manual', 'Stanley', 'Cinta Metrica 5m', 'Cinta de acero 25mm, freno deslizante', 9990, 'Alta'),
    ('Herramienta_Manual', 'Stanley', 'Nivel de burbuja 24"', 'Aluminio reforzado 3 imanes', 15990, 'Media'),
    ('Herramienta_Manual', 'Stanley', 'Cierra Manual 18T', 'Hoja de acero al carbono 20"', 12990, 'Media'),
    ('Herramienta_Manual', 'Pretul', 'Juego de Llaves Allen', '9 piezas metricas 1.5-10mm', 8990, 'Alta'),
    ('Herramienta_Manual', 'Pretul', 'Cortafrio 6"', 'Acero al cromo vanadio', 7990, 'Alta'),
    ('Herramienta_Manual', 'Belzer', 'Alicate de Presion 10"', 'Acero niquelado, ajuste rapido', 14990, 'Media'),
    ('Herramienta_Manual', 'Belzer', 'Alicate Universal 8"', 'Acero al carbono con aislante', 12990, 'Alta'),
    ('Herramienta_Electrica', 'Bosch', 'Taladro Percutor GSB 550', '550W 13mm mandril automatico', 59990, 'Alta'),
    ('Herramienta_Electrica', 'Bosch', 'Atornillador Inalambrico GSR 120LI', '12V 2.0Ah bateria Li-Ion', 69990, 'Alta'),
    ('Herramienta_Electrica', 'Bosch', 'Amoladora Angular GWS 750', '750W disco 4.5" guarda protectora', 45990, 'Media'),
    ('Herramienta_Electrica', 'Bosch', 'Sierra Circular PKS 55', '1200W 160mm profundidad 55mm', 89990, 'Baja'),
    ('Herramienta_Electrica', 'Makita', 'Taladro Percutor HP1630', '680W 13mm velocidad variable', 54990, 'Media'),
    ('Herramienta_Electrica', 'Makita', 'Atornillador Impacto DTW700', '18V 200Nm inalambrico', 119990, 'Media'),
    ('Herramienta_Electrica', 'Makita', 'Lijadora Orbital BO5041', '300W base 1/4 hoja', 49990, 'Media'),
    ('Herramienta_Electrica', 'Makita', 'Cepillo Electrico 1900B', '850W ancho 82mm profundidad 3mm', 79990, 'Baja'),
    ('Herramienta_Electrica', 'Dewalt', 'Taladro Percutor DCD778', '20V Brushless 2.0Ah', 119990, 'Alta'),
    ('Herramienta_Electrica', 'Black+Decker', 'Caladora KS700', '500W corte biselado 45', 32990, 'Alta'),
    ('Material_Construccion', 'Hidralit', 'Cemento Gris 42.5kg', 'Cemento Portland grado 42.5 para construccion general', 8990, 'Alta'),
    ('Material_Construccion', 'Hidralit', 'Estuco 25kg', 'Estuco interior/exterior bolsa 25kg', 5990, 'Alta'),
    ('Material_Construccion', 'Volcan', 'Yeso Carton 1.20x2.40m', 'Placa estandar 15mm para tabiques', 12990, 'Alta'),
    ('Material_Construccion', 'Volcan', 'Plancha de Fibrocemento 4mm', 'Panel 1.20x2.40m resistente al agua', 15990, 'Media'),
    ('Material_Construccion', 'Melon', 'Hormigon Seco 25kg', 'Preparado listo para usar en obras menores', 7990, 'Alta'),
    ('Material_Construccion', 'PVC', 'Tuberia PVC 110mm x 3m', 'Tuberia desague sanitario 110mm', 8990, 'Alta'),
    ('Material_Construccion', 'PVC', 'Codo PVC 110mm 90', 'Codo sanitario 110mm x 90 grados', 2490, 'Alta'),
    ('Ceramica_Piso', 'Vives', 'Ceramica Piso 45x45', 'Esmaltada trafico alto beige caja 1.62m2', 15990, 'Media'),
    ('Ceramica_Piso', 'Vives', 'Cermico Muro 33x33', 'Blanco brillante caja 1.5m2', 12990, 'Alta'),
    ('Ceramica_Piso', 'Sodimac', 'Piso Flotante 7mm', 'Laminado roble natural 1.28m2 por caja', 21990, 'Media'),
    ('Pintura', 'Tricolor', 'Esmalte Sintetico Blanco 1L', 'Esmalte sintetico blanco brillante 1L', 10990, 'Alta'),
    ('Pintura', 'Tricolor', 'Latex Interior Blanco 4L', 'Latex lavable mate interior 4L', 19990, 'Alta'),
    ('Pintura', 'Tricolor', 'Barniz Marino 1L', 'Barniz poliuretano altra resistencia', 15990, 'Media'),
    ('Pintura', 'Tricolor', 'Pintura Asfaltica 1L', 'Impermeabilizante base asfalto', 12990, 'Media'),
    ('Pintura', 'Tricolor', 'Thinner 1L', 'Solvente sintetico 1L', 5990, 'Alta'),
    ('Fontaneria', 'Fanal', 'Llave de Paso 1/2"', 'Llave paso recta PVC 1/2"', 4990, 'Alta'),
    ('Fontaneria', 'Fanal', 'Adaptador PVC 1/2"', 'Adaptador hembra PPR 1/2"', 1590, 'Alta'),
    ('Fontaneria', 'Fanal', 'Teflon 1/2" x 10m', 'Cinta teflon para sellar roscas', 1490, 'Alta'),
    ('Fontaneria', 'Fanal', 'Sellador Silicona 300ml', 'Silicona transparente multiuso 300ml', 4990, 'Alta'),
    ('Fontaneria', 'Fanal', 'Flexible Sanitario 40cm', 'Manguera flexible acero trenzado 40cm', 3990, 'Alta'),
    ('Electricidad', 'Tecno', 'Cable THHN 14 AWG x 100m', 'Cable electrico cobre 14 AWG 100m', 24990, 'Alta'),
    ('Electricidad', 'Tecno', 'Interruptor Simple 10A', 'Interruptor luz blanco empotrar 10A', 3490, 'Alta'),
    ('Electricidad', 'Tecno', 'Enchufe Universal 16A', 'Toma corriente blanco con tapa', 3990, 'Alta'),
    ('Electricidad', 'Tecno', 'Portalámpara Standard', 'Portalampra E27 blanco baquelita', 1490, 'Alta'),
    ('Electricidad', 'Philips', 'Ampolleta LED 9W E27', 'LED 9W 800lm luz calida 3000K', 4990, 'Alta'),
    ('Electricidad', 'Philips', 'Ampolleta LED 15W E27', 'LED 15W 1500lm luz blanco neutro', 6990, 'Alta'),
    ('Fijacion_Seguridad', 'Fischer', 'Tarugo Universal 6mm x 30', 'Tarugo nylon expansión universal pack 10', 1490, 'Alta'),
    ('Fijacion_Seguridad', 'Fischer', 'Anclaje Quimico 300ml', 'Resina epoxi para fijaciones estructurales', 24990, 'Media'),
    ('Fijacion_Seguridad', 'Fischer', 'Martillo W2', 'Martillo electrico pistola fijacion', 59990, 'Baja'),
    ('Equipo_Seguridad', '3M', 'Casco de Seguridad', 'Casco proteccion UV ajustable clase E', 14990, 'Alta'),
    ('Equipo_Seguridad', '3M', 'Guantes Latex Talla L', 'Guantes uso rudo recubiertos latex', 4990, 'Alta'),
    ('Equipo_Seguridad', '3M', 'Lentes Proteccion Transparente', 'Lentes seguridad antiempaño policarbonato', 5990, 'Alta'),
    ('Equipo_Seguridad', '3M', 'Mascarilla N95', 'Respirador desechable N95 (10und)', 11990, 'Media'),
    ('Jardineria', 'Einhell', 'Cortacesped Electrico', '1200W ancho corte 36cm bolsa 30L', 79990, 'Media'),
    ('Jardineria', 'Einhell', 'Desmalezador Electrico', '500W cabezal semiautomatico 30cm', 49990, 'Media'),
    ('Jardineria', 'Einhell', 'Motosierra Electrica', '1800W barra 16" con freno de cadena', 59990, 'Baja'),
    ('Jardineria', 'Tramontina', 'Bate de Jardin', 'Bate jardin acero carbono mango 50cm', 9990, 'Alta'),
    ('Jardineria', 'Tramontina', 'Tijeras Podar', 'Tijeras de podar bypass acero alto carbono', 15990, 'Alta'),
    ('Jardineria', 'Tramontina', 'Rastrillo Metalico', 'Rastrillo jardin 12 puas mango 140cm', 12990, 'Media'),
]

REPUESTOS = [
    ('Frenos', 'Bosch', 'Pastillas Freno Delanteras', 'Pastillas ceramicas para auto sedan 2020+', 45990, 'Alta'),
    ('Frenos', 'Bosch', 'Discos Freno Delanteros', 'Disco ventilado 280mm para sedan compacto', 69990, 'Media'),
    ('Frenos', 'Bosch', 'Bomba Freno Maestra', 'Bomba principal frenos 1" para vehiculos livianos', 55990, 'Media'),
    ('Frenos', 'Bosch', 'Liquido Freno DOT4 1L', 'Liquido frenos DOT4 alto rendimiento 1L', 15990, 'Alta'),
    ('Frenos', 'TRW', 'Pastillas Freno Traseras', 'Pastillas semimetálicas para SUV', 49990, 'Alta'),
    ('Frenos', 'TRW', 'Tambor Freno Trasero', 'Tambor freno trasero 200mm para sedan', 44990, 'Baja'),
    ('Frenos', 'NK', 'Flexible Freno Delantero', 'Manguera freno acero trenzado 50cm', 19990, 'Alta'),
    ('Suspension', 'KYB', 'Amortiguador Delantero', 'Amortiguador gas presion para sedan 4p', 89990, 'Media'),
    ('Suspension', 'KYB', 'Amortiguador Trasero', 'Amortiguador gas presion para sedan 4p', 79990, 'Media'),
    ('Suspension', 'Sachs', 'Kit Embrague', 'Kit embrague completo para motor 1.4-2.0', 299990, 'Media'),
    ('Suspension', 'Sachs', 'Espiral Suspension', 'Resorte helicoidal tipo A para sedan', 59990, 'Baja'),
    ('Suspension', 'Monroe', 'Buje Suspension Inferior', 'Buje poliuretano dureza 90A', 25990, 'Media'),
    ('Suspension', 'Monroe', 'Barra Estabilizadora', 'Barra estabilizadora 20mm para sedan', 39990, 'Media'),
    ('Motor', 'Bosch', 'Bujias Encendido Iridium', 'Juego 4 bujias iridium 1.6-2.0', 25990, 'Alta'),
    ('Motor', 'NGK', 'Bujias Standard', 'Juego 4 bujias cobre para motor basico', 12990, 'Alta'),
    ('Motor', 'Bosch', 'Alternador 120A', 'Alternador 120 amperios 12V para sedan', 199990, 'Media'),
    ('Motor', 'Bosch', 'Motor Partida 1.4kW', 'Motor partida 12V 1.4kW para sedan/hatchback', 159990, 'Media'),
    ('Motor', 'Bosch', 'Correa Distribucion Kit', 'Kit distribucion completo incluye tensor', 89990, 'Alta'),
    ('Motor', 'Gates', 'Correa Alternador', 'Correa serpentina 5PK 1730 para motor 2.0', 15990, 'Alta'),
    ('Motor', 'Valeo', 'Radiador Motor', 'Radiador aluminio para motor 1.6-2.0 automatico', 129990, 'Baja'),
    ('Motor', 'Valeo', 'Sensor Temperatura', 'Sensor temperatura refrigerante standard', 19990, 'Alta'),
    ('Filtros', 'Mann', 'Filtro Aceite', 'Filtro aceite rosca 3/4" para motor bencinero', 9990, 'Alta'),
    ('Filtros', 'Mann', 'Filtro Aire', 'Filtro aire panel cuadrado 30x20cm', 14990, 'Alta'),
    ('Filtros', 'Mann', 'Filtro Habitaculo', 'Filtro cabina carbon activado 25x20cm', 12990, 'Alta'),
    ('Filtros', 'Mann', 'Filtro Combustible', 'Filtro bencina rosca 1/2" standard', 8990, 'Alta'),
    ('Filtros', 'Bosch', 'Filtro Aceite Premium', 'Filtro aceite alto rendimiento sintetico', 14990, 'Media'),
    ('Electrico', 'Bosch', 'Bateria Auto 60Ah', 'Bateria 12V 60Ah 540CCA para sedan', 89990, 'Alta'),
    ('Electrico', 'Bosch', 'Bateria Auto 75Ah', 'Bateria 12V 75Ah 680CCA para SUV', 119990, 'Alta'),
    ('Electrico', 'Bosch', 'Sensor Oxigeno Lambda', 'Sensor O2 universal 4 cables', 45990, 'Media'),
    ('Electrico', 'Bosch', 'Bobina Encendido', 'Bobina encendido doble para motor 4 cilindros', 35990, 'Alta'),
    ('Electrico', 'Bosch', 'Cable Bujias Juego', 'Juego cables bujias silicio 4 cilindros', 25990, 'Alta'),
    ('Electrico', 'Hella', 'Faro Delantero Completo', 'Faro halogeno derecho sedan 2018+', 129990, 'Media'),
    ('Electrico', 'Hella', 'Faro LED Neblinero', 'Kit faros niebla LED universal 2 piezas', 59990, 'Alta'),
    ('Electrico', 'Hella', 'Luz Freno LED', 'Lampara LED stop trasera universal 12V', 19990, 'Alta'),
    ('Electrico', 'Hella', 'Bocina Electrica', 'Kit bocina doble tono 12V 110dB', 19990, 'Alta'),
    ('Transmision', 'Mobil', 'Aceite Motor 5W30 4L', 'Aceite sintetico API SP 5W30', 35990, 'Alta'),
    ('Transmision', 'Mobil', 'Aceite Motor 10W40 4L', 'Aceite semisintetico API SL 10W40', 25990, 'Alta'),
    ('Transmision', 'Mobil', 'Aceite Transmision ATF', 'Aceite transmision automatica ATF 1L', 14990, 'Alta'),
    ('Transmision', 'Mobil', 'Refrigerante 50% 4L', 'Refrigerante concentrado verde 50%', 15990, 'Alta'),
    ('Transmision', 'Castrol', 'Aceite Motor 5W40 5L', 'Aceite sintetico premium para turbo', 49990, 'Media'),
    ('Refrigeracion', 'Valeo', 'Compresor AC 12V', 'Compresor aire acondicionado 12V 150cc', 349990, 'Baja'),
    ('Refrigeracion', 'Valeo', 'Condensador AC', 'Condensador AC para sedan compacto', 159990, 'Media'),
    ('Refrigeracion', 'Valeo', 'Evaporador AC', 'Evaporador AC standard 12V', 129990, 'Baja'),
    ('Refrigeracion', 'Valeo', 'Filtro Secador AC', 'Filtro secador aire acondicionado', 29990, 'Media'),
    ('Direccion', 'TRW', 'Terminal Direccion', 'Terminal direccion izquierda para sedan', 25990, 'Alta'),
    ('Direccion', 'TRW', 'Rotula Suspension', 'Rotula suspension inferior para sedan', 22990, 'Alta'),
    ('Direccion', 'TRW', 'Barra Direccion Cremallera', 'Cremallera direccion para sedan 2015+', 249990, 'Baja'),
    ('Escape', 'Bosch', 'Sonda Lambda Universal', 'Sonda O2 universal 4 cables 12V', 45990, 'Media'),
    ('Escape', 'Bosch', 'Catalizador Universal', 'Convertidor catalitico universal 2.5"', 199990, 'Media'),
    ('Escape', 'Walker', 'Silenciador Trasero', 'Silenciador trasero universal 2" acero', 59990, 'Media'),
    ('Carroceria', 'Bosch', 'Limpiaparabrisas Juego', 'Juego limpiaparabrisas 22"+20" standard', 19990, 'Alta'),
    ('Carroceria', 'Bosch', 'Plumillas Limpiaparabrisas', 'Plumilla limpiaparabrisas 22" hoja plana', 14990, 'Alta'),
    ('Carroceria', 'Hella', 'Retrovisor Lateral', 'Retrovisor electrico con calefaccion derecho', 79990, 'Media'),
    ('Carroceria', 'Hella', 'Manilla Puerta Exterior', 'Manilla puerta exterior cromada 4p', 29990, 'Alta'),
]


def guardar_csv(filename, data):
    path = os.path.join(BASE, filename)
    os.makedirs(BASE, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Categoria', 'Marca', 'Modelo', 'Especificaciones', 'Precio_CLP', 'Stock'])
        w.writerows(data)
    print(f"  {path}: {len(data)} productos")


if __name__ == "__main__":
    print("Generando catalogos demo:")
    guardar_csv("catalogo_ferreteria.csv", FERRETERIA)
    guardar_csv("catalogo_repuestos.csv", REPUESTOS)
    print("Listo")
