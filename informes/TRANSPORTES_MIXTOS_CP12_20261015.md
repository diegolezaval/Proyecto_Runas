# CP12 · Transportes mixtos recuperados

Último reloj del observador recuperado y rehidratado: **τ=6.4**. Los tiempos físicos reales, balances y contadores están en cada certificado. Estos estados internos permiten continuar DOP853 sin resembrar ni partir un paso adaptativo.

| Reloj | Bytes del ZIP | SHA256 |
|---|---:|---|
| 0.4 | 204098285 | `fc7e044658650e8c3fbb731c942192b387bcc31f0455b5731368f675f38ac21c` |
| 1.6 | 203934316 | `7b069c111340596a258252bd3fee767835d62078d74fecf0a459042214661c55` |
| 3.2 | 203910964 | `14f597dee11e5a6a7e473992f1a7a88f431f217d0b90ca71a99ae2199ca1f3f9` |
| 4.8 | 203957944 | `883b97fe1e0c327ebe8aa1aa25cfa31a5e177df42ca3802a21ba1014b5f0f0a5` |
| 6.4 | 203985299 | `227c2a4361b05574dbb9b071beafa0e9672f4aa08e1af2bb8f0a65c27e368adb` |

Cada cápsula completa supera cobertura/tamaños/hashes y la auditoría independiente de rehidratación con cero pasos M2. El contraste preregistrado .4→.41 coincide bit a bit; su trabajo diagnóstico se registra separadamente. No se repiten A–D ni campañas certificadas.

Las fronteras científicas siguen cada ocho unidades. Se mantienen ambas energías ≤2e-4, carga ≤1e-9, identidades, observadores, cinco métricas espaciales ≤2 %, eliminación del mecanismo y pruebas adicionales de convergencia/estabilidad/robustez. Un transporte no las sustituye.

CP12 permanece abierto y CP11 sigue aceptado. La producción conserva sus paradas y negativos. Main, PR #2 y las 33 etapas permanecen intactos. Recuperar primero el transporte o frontera válido más avanzado usando RECUPERAR.md; no volver a τ0 si existe un estado posterior.

## Incidentes administrativos conservados

El primer intento de respaldar τ=1.6 incluyó copias transitorias ajenas a la carga canónica y produjo un paquete de 608 504 980 bytes, cuya preparación de envío falló. La evidencia completa del fallo, estados y controles se conserva en el paquete canónico negativo de 425 146 306 bytes, SHA256 `c1ebfd444baed4efb025eb9f47121b57141e5650ee9145a846828ae7b4abdc9d`, recuperado con sus 110 archivos verificados. No fallaron las puertas físicas.

La primera prueba del adaptador sobre la extracción recuperada incluyó además un manifiesto raíz heredado y generó una entrada duplicada. La comprobación lo rechazó antes de M2 y se conserva como intento administrativo inválido. La selección fue corregida y registrada en `19c8b2b2eb40052ae81fc66e5ccc7acc76607348`; las funciones numéricas conservan AST idéntico y el serializador es byte a byte el mismo.

El nuevo respaldo τ=1.6 tiene 203 934 316 bytes y SHA256 `7b069c111340596a258252bd3fee767835d62078d74fecf0a459042214661c55`; sus 124 archivos y rehidratación independiente pasan. El NPZ conserva SHA256 `5776cceadd2ca07b94a25e4171791b068ed4205de06ac286564f4e6ef5869061`, y el recibo también quedó idéntico. Se reanudó el paso DOP853 existente: 296 pasos aceptados y 3974 evaluaciones vivas por malla. No se repitió 0→1.6.

Máximos hasta ese respaldo: energía FV 2.876830996e-9/6.949043563e-10; energía mixta 4.626332650e-11/4.619737926e-11; carga 6.661338148e-16/4.440892099e-16. Los cierres y Parseval pasan sus criterios originales. Son balances de un prefijo corto; la puerta espacial final y las demás dependencias CP12 siguen pendientes.

Para recuperar este respaldo, usar las fuentes capturadas de `conservacion_canonica_v2` del commit registrado y la guía `RECUPERAR.md`. Recuperar primero cualquier transporte o frontera posterior; no volver a τ0 si existe un estado más avanzado.
