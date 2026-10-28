# Infraestructura del intento 02: diagnóstico sin evolución

La aprobación del usuario para repetir de forma acotada τ9,6→τ11,2 ya está registrada. No se ha consumido ni asignado esa repetición adicional.

La recuperación nueva del ZIP original comprobó 229821160 bytes, SHA-256 a71554ff3e213d09cf7365697e4d9c9307e9529478d567ae3f89ccc11e43b959 y las 283 cargas. Pasaron los 30 controles de la frontera τ8 y los 14 del transporte τ9,6, sin construcciones ni pasos DOP853. La cápsula nueva de prueba de capacidad quedó preparada con 230899836 bytes y SHA-256 94608e8a7e8cf49af58de99f2684f1f49dcae2f126f5712c9a8bda7dcda56de7. Todavía no se acredita subida ni recuperación directa.

El usuario informó que terminó la activación oficial de GitHub CLI. La conexión no quedó guardada en el proceso local. Al consultar su sesión de ejecución, el entorno devolvió literalmente: `Network access to "https://api.github.com:443" was blocked by policy.` No se obtiene ni expone ningún token. Ese mensaje no prueba que GitHub haya denegado la aprobación del usuario; tampoco acredita una conexión operativa.

## Alternativa mínima que se registra antes de probarla

El flujo [.github/workflows/p3-infraestructura-20261028.yml](../../../../../../.github/workflows/p3-infraestructura-20261028.yml) usa exclusivamente lectura del repositorio, Python3.12.14 y las versiones originales de NumPy y threadpoolctl. Ejecuta sin cambios el control administrativo existente `trazabilidad/CP12_reconstruccion/comprobar_dispatch_original.py`. No carga ni evoluciona el ensayo P3, no publica cápsulas, no modifica fuentes científicas ni acepta una frontera. Sólo puede comprobar el dispatch real y guardar el resultado de esa ejecución, identificado por run_id e intento.

Se exige SkylakeX, un hilo y ninguna imposición de OPENBLAS_CORETYPE. Las asignaciones de GitHub Actions examinadas en octubre11 dieron Haswell y fueron rechazadas antes de evolucionar. Esa evidencia permanece intacta. Se hace una única comprobación de infraestructura actual para determinar si esta alternativa ofrece un ejecutor compatible. Si falla, no se reasigna repetidamente el trabajo buscando otro procesador ni se rebajan las puertas.

Si pasa, faltarán todavía el compilador y entorno completos originales, la recuperación exacta sin pasos, la prueba completa de publicación desde el proceso, y el registro del nuevo lanzador y su asignación exclusiva antes de todo M2. Este diagnóstico nunca satisface por sí solo esas puertas.

CP11 sigue aceptado; CP12 abierto, P3 sin validar, frontera completa τ8 y transporte permanente τ9,6. P2 no se reanuda. No se repiten CP10, CP12 original, F0…F5 ni P3 τ0→τ9,6.
