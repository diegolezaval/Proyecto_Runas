# CP12 · Recuperación del transporte mixto τ=3,2

Se encontró una cápsula posterior al último certificado publicado (τ=1,6). La cápsula de τ=3,2, preservada el 15 de octubre a las 22:43 UTC, tiene **203 910 964 bytes**, SHA256 `14f597dee11e5a6a7e473992f1a7a88f431f217d0b90ca71a99ae2199ca1f3f9` y 126 archivos de carga útil. Este hash del ZIP se calculó al recuperar el objeto conservado, versión 0; no se encontró un hash público anterior de ese ZIP. Todos los tamaños y hashes del manifiesto capturado coinciden.

La extracción nueva supera las **14 comprobaciones** de rehidratación sin pasos M2. El estado interno conserva SHA256 `56683211f7d937dc4793bc19e61cb603c007c78ceed1016584a091e89b4ea8e1`. El recibo científico, los internos de DOP853, su etapa compartida, interpolaciones, contadores y observadores se recuperan sin reiniciar el integrador. Las nueve fuentes registradas de transporte y las fuentes científicas originales coinciden; se reutiliza el contraste bit a bit .4→.41 ya certificado, sin repetir A–D.

| Magnitud del prefijo | h=.125 | h=.0625 | Puerta original |
|---|---:|---:|---:|
| Tiempo físico del integrador | 3.201729201032835 | 3.2017332077561567 | Encierra el reloj 3.2 |
| Pasos aceptados | 592 | 592 | Contadores conservados |
| Evaluaciones DOP853 vivas | 7538 | 7538 | Contadores conservados |
| Deriva máxima E FV | 2.910391705e-9 | 7.019338444e-10 | ≤2e-4 |
| Deriva máxima E mixta | 4.910871709e-11 | 4.903433215e-11 | ≤2e-4 |
| Deriva máxima de carga | 6.661338148e-16 | 4.440892099e-16 | ≤1e-9 |

Los controles de observadores, Parseval y simetría pasan. El reloj 3,2 es un transporte recuperable, **no una frontera científica**: la última frontera mixta sigue siendo τ0 y la primera meta del piloto es τ8. La puerta espacial original del 2 % conserva sus cinco métricas y su horizonte τ160; no se sustituye por conservación de energía en este prefijo.

La sesión anterior no está accesible y su salida final no se observa. No se presume su terminación. No se encontraron cápsulas posteriores del intento ni ejecuciones de GitHub Actions activas o en cola. Se prepara una sesión aislada desde este transporte, con identidad de recuperación separada y sin reescribir la procedencia histórica. Antes de iniciar se vuelve a buscar evidencia posterior. Se usan las fuentes capturadas de la revisión administrativa `19c8b2b2eb40052ae81fc66e5ccc7acc76607348`.

La continuación exige recuperar y auditar cada frontera de ocho unidades antes del tramo siguiente. Cualquier fallo conserva el negativo; la eliminación del mecanismo y las pruebas de convergencia, estabilidad y robustez mantienen sus dependencias. CP12 permanece abierto, CP11 sigue aceptado, las 33 etapas se conservan, main permanece intacta y PR #2 abierto/en borrador.

Comprobantes: `TRANSPORTE_TAU_000032.json` y `RECUPERACION_INDEPENDIENTE_000032_20261016.json`, en el directorio `transporte_dop853_20261015`. Los incidentes administrativos anteriores siguen documentados en `INCIDENTES_CONSERVACION_TAU1p6.json` y en el informe de transportes. El exportador conserva ahora esa sección al añadir un transporte posterior.

La sesión propia inició a las 03:11:18 UTC del 16 de octubre, restaurando el tramo abierto desde3,2. El respaldo posterior de τ=4,8 pasó conservación, recuperación de sus 132 archivos y las 14 comprobaciones de rehidratación. ZIP: 203 957 944 bytes, SHA256 `883b97fe1e0c327ebe8aa1aa25cfa31a5e177df42ca3802a21ba1014b5f0f0a5`; estado interno SHA256 `1921880f391ee49e22ea92c9323625b255676466d94a63357a4f7026d6f4099d`. No se reinició DOP853 ni se repitió 0→3,2. Continúa la dependencia de τ8 y de las puertas finales.
