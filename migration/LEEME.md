# Migración autorizada de CP10

Rama auxiliar operativa; no es una fuente científica. main y el tag CP10 deben terminar en 47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81, con los 938 archivos originales.

El usuario autorizó el 2026-10-03 el arranque provisional con el README original y su sustitución controlada. Commit de arranque preservado en esta rama: 436fb01ac4656171da31603a306587d6cba559f9. El ejecutor aborta si main contiene cambios ajenos.

El borrador privado cp10-transferencia aloja el ZIP autoritativo y su bundle como medios de transporte. La Release CP10 sólo se publica después de clonar realmente GitHub, comprobar la integridad, recibos, estados y regresiones, recompilar la fuerza C, regenerar las vistas y reproducir exactamente el ZIP.

No se cambian parámetros, conclusiones, puertas científicas ni rutas; no se ejecuta CP11. El workflow sólo usa contents:write del token efímero nativo del repositorio y se dispara por cambios de su archivo en esta rama.
