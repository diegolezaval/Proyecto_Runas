# Recuperación de una frontera numérica mixta completa

Consultar primero las cápsulas y certificados posteriores y la actividad del ejecutor. Elegir el estado recuperable más avanzado. Un transporte interno permite retomar un tramo abierto; una frontera completa posterior prevalece sobre los transportes antiguos del tramo cerrado.

Para una cápsula completa `CP12_CANDIDATO_MIXTO_…_tauNNNN.zip`, obtener también su certificado permanente externo. El comprobante público `FRONTERA_MIXTA_TAUNNNN.json` contiene tamaños, hashes, identidad y auditoría; el comprobante completo conservado añade las referencias del respaldo. No reconstruir la procedencia a partir de un latido.

Ejecutar desde estas fuentes públicas:

```sh
python3 recuperar_frontera.py \
  --capsule <ZIP_COMPLETO> \
  --certificate <CERTIFICADO_PERMANENTE_EXTERNO> \
  --destination <RAIZ_NUEVA_INEXISTENTE> \
  --public-sources <FUENTES_CAPTURADAS_conservacion_canonica_v2> \
  --helpers <AUXILIARES_VIGENTES>
```

La herramienta exige el hash/tamaño del ZIP, unicidad y seguridad de rutas, cobertura exacta del manifiesto, cada archivo, fuentes registradas, estado, configuración, recibo y auditoría original con cero pasos M2. Conserva la identidad y los bytes del recibo; la sesión nueva tiene un registro separado. El certificado externo, emitido después del guardado de la cápsula, se instala como comprobante anterior para la continuación.

Un transporte anterior incluido en la cápsula permanece como evidencia histórica. Su reloj debe ser anterior o igual a la frontera; no se combina con el recibo nuevo ni se restaura para repetir el tramo cerrado. El controlador empieza el siguiente segmento de ocho unidades como prescribe el protocolo original.

Sólo tras recuperación/auditoría positivas iniciar `guardian_transporte.py --home <RAIZ_NUEVA>`, con lectura residual posterior y conservación de copias conforme a los registros capturados. No duplicar un trabajador propio observado activo; no presumir terminación de ejecutores inaccesibles. Una frontera recuperada no valida la corrección ni cierra CP12. Se conservan todas las puertas y negativos.
