# Corrección del cierre de publicación CP11

En el primer clon remoto de la rama científica (commit `8b8ba86d0b1e8bcb8f32bcb320a76d4968318676`), la verificación de publicación reprodujo los tres diagnósticos válidos byte por byte. El trabajador terminó con código 0 y el recibo quedó `COMPLETADA`; el proceso padre terminó con código 1 al imprimir `receipt_path.relative_to(ROOT)` para una ruta externa autorizada. No fue un fallo de los diagnósticos ni una interrupción de su ejecución.

Se corrige exclusivamente la referencia que se imprime: relativa para recibos internos y absoluta para recibos externos. La identidad, el prerregistro, la captura de fuentes, los hashes, el cierre duradero y las decisiones científicas conservan su comportamiento. Los recibos científicos previos conservan el código que utilizaron. El adaptador original de CP10 se preserva en `trazabilidad/CP10_entrada/herramientas/ejecutar_con_procedencia.py`.

`herramientas/probar_recibo_externo_CP11.py` comprueba cierre, integridad y reutilización sin modificar el recibo mediante un trabajador JSON sintético en temporales. Se incorpora a la regresión. No ejecuta M2. El comprobante estructural anterior se conserva como `validacion/arquitectura/regresion_CP11_pre_publicacion.json`; el comprobante vigente se regenera después de la corrección.

El log y el recibo del intento externo se conservan con los comprobantes de publicación, fuera del corpus científico: son evidencia del transporte y cierre, no una dependencia para reproducir CP11. Se requiere otro clon remoto del commit corregido antes de integrar el PR. No se modifica ningún resultado, parámetro, tolerancia, puerta ni autoridad científica.
