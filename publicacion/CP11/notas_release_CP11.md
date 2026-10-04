CP11 cierra el diagnóstico radial de χ sobre los estados autoritativos de CP10. Integrado mediante [PR #1](https://github.com/diegolezaval/Proyecto_Runas/pull/1) en `ed8d818b622a0687aeb56d34ca9e3913bd54e124`, sin eludir la protección de main.

La puerta científica original sigue **REFINAMIENTO_PENDIENTE (2 %)**: la diferencia espacial de campo y velocidad es 5,12639 %. Los controles declarados descartan un cruce artificial por interpolación/métrica. El 99,9725 % de la diferencia cuadrática se concentra en componentes k > 4 del operador FV. La propagación libre inicial y la corrección modal congelada no bastan. Falta la historia temporal para atribuir el presupuesto integrado al operador radial o a la fuente acoplada; se detiene la continuación automática ante esa ambigüedad. No se afirma inestabilidad física, aceptación del continuo ni agotamiento de M2. No se inicia CP12.

**Checkpoint completo:** 1047 archivos, con estados, resultados negativos, historia, prerregistros, recibos, fuentes y vistas. Los 938 archivos originales CP10 son recuperables por hashes. No hay movimientos, renombrados o eliminaciones. M2, Θ y las puertas permanecen; cero pasos nuevos de evolución M2.

El clon remoto científico permanece limpio y reproduce los tres diagnósticos válidos byte por byte; pasan 23 comprobaciones y 15 controles estructurales. Se conserva el intento aritmético fallido y el primer cierre de publicación fallido. La referencia longdouble mantiene las ecuaciones y la tolerancia algebraica. Las limitaciones de backend/CPU y precisión extendida están documentadas; la verificación científica de referencia no se sustituye por un runner genérico.

Descargar **Proyecto_Runas_M2_4_2_CP11_DIAGNOSTICO_RADIAL_CHI.zip** y extraerlo. Comenzar por `LEEME.md` y `ESTADO_ACTUAL.md`; comandos de verificación y siguiente condición científica en `informes/ENTREGA_11_DIAGNOSTICO_RADIAL_CHI.md`. El ZIP incluye todos los complementos necesarios, sin descargas externas para reconstruir el checkpoint.

ZIP: **85.069.747 bytes**. SHA-256: `dafff205020e32b8b7128ccdb10a3288aad17691f1d1c4e5a486031f1e6389b0`.

Adjuntos adicionales: comprobante del clon, regresión, reproducción de diagnósticos y recibos de publicación. La publicación vuelve a clonar el commit integrado, verifica el manifiesto, reproduce el ZIP idéntico con Python 3.12.14/zlib 1.3.2 y comprueba por SHA-256 las descargas de los adjuntos y del ZIP publicado. `Acta_publicacion_CP11.json` documenta el tag anotado y ese cierre. La rama administrativa `publicacion/cp11` no se integra a main.
