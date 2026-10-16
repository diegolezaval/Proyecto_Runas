# CP12 · Transportes mixtos recuperados

Último reloj del observador recuperado y rehidratado: **τ=44.8**. Los tiempos físicos reales, balances y contadores están en cada certificado. Estos estados internos permiten continuar DOP853 sin resembrar ni partir un paso adaptativo.

| Reloj | Bytes del ZIP | SHA256 |
|---|---:|---|
| 0.4 | 204098285 | `fc7e044658650e8c3fbb731c942192b387bcc31f0455b5731368f675f38ac21c` |
| 1.6 | 203934316 | `7b069c111340596a258252bd3fee767835d62078d74fecf0a459042214661c55` |
| 3.2 | 203910964 | `14f597dee11e5a6a7e473992f1a7a88f431f217d0b90ca71a99ae2199ca1f3f9` |
| 4.8 | 203957944 | `883b97fe1e0c327ebe8aa1aa25cfa31a5e177df42ca3802a21ba1014b5f0f0a5` |
| 6.4 | 203985299 | `227c2a4361b05574dbb9b071beafa0e9672f4aa08e1af2bb8f0a65c27e368adb` |
| 9.6 | 229607879 | `5e173cbd5244fbb4e114b755c96a6e9cf7659334e07e840d55c306984bf25b3f` |
| 11.2 | 229631946 | `f9d1944405c615876adee7d37c35cc97ad33c54cab2ee82a4add2a8d7fe3a4dd` |
| 12.8 | 229655330 | `3bc6afe37b5d4dd69b1d4219dcda3b80edb6cb57c957e908aa6cd08667fe80e8` |
| 14.4 | 229683299 | `1e40dfd025a7f23ecd078722c9a38c0c280f5e4328fd7ebf7c328b14557155f8` |
| 17.6 | 229885860 | `4b21f74b226bfcfa40127178e54ccbab31ad98265c8878ddd95f6b5f83118315` |
| 19.2 | 229921341 | `be2c441d3b3680f06dc3336673a095f1081192e10eaf969d98036363bbdc09f5` |
| 20.8 | 229950463 | `208854c1eb4859fc765ac79fafa2b65cd5c55b2a1be632fa293f2f47d7db03ac` |
| 22.4 | 229984255 | `832d7afb4e988f037ef0e2c46b373d845b4b689eaaff7a50ff7817317103477e` |
| 25.6 | 230174758 | `fb187e35ed1fc216ef6d752ffec15fadbcac3ff616cad08b7168387cc22993ba` |
| 27.2 | 230195437 | `c0a0671c2787049af4478f59b45988a7c41d0dc112134a283cbf97dd763b4775` |
| 28.8 | 230275138 | `b48c0b5e6040c0092c5bfca8da20b6303e36eb718095e2c15a1b49296dde07f1` |
| 30.4 | 230296645 | `75dcffacc457a6eace93821350cf767cb497a23ac173bdbb37f04b9c8f84c8ec` |
| 33.6 | 230492070 | `da1835f8cf4033907eb6ccc5e23faa60a439ee36fc0a81b5c76713116763adc3` |
| 35.2 | 230526018 | `5a65dfae5738c5124e875aa443143d3dbc382cca15b41af464d75cc551015e41` |
| 36.8 | 230552183 | `d72c9495bf570c9d69803690f516aa4dc569a70faf3a6b053aa31b5a7e0ab641` |
| 38.4 | 230586825 | `12ecda3bf5f3218ce4e5b953f0c60ab0e1271926423ef513674e2b760e510a86` |
| 41.6 | 230754121 | `44b0e6759d727736dea20a3da69f476e89db445b88d825280fb6492034f9f4f3` |
| 43.2 | 230784495 | `85728a49622094cd623d0a779e4da90b7af7952da034c16a02901f548b8e0e73` |
| 44.8 | 230818087 | `b265fab20ac9a129386039d479066de424563759c2f28c0ae6d50d4d396578bf` |

Cada cápsula completa supera cobertura/tamaños/hashes y la auditoría independiente de rehidratación con cero pasos M2. El contraste preregistrado .4→.41 coincide bit a bit; su trabajo diagnóstico se registra separadamente. No se repiten A–D ni campañas certificadas.

Las fronteras científicas siguen cada ocho unidades. Se mantienen ambas energías ≤2e-4, carga ≤1e-9, identidades, observadores, cinco métricas espaciales ≤2 %, eliminación del mecanismo y pruebas adicionales de convergencia/estabilidad/robustez. Un transporte no las sustituye.

CP12 permanece abierto y CP11 sigue aceptado. La producción conserva sus paradas y negativos. Main, PR #2 y las 33 etapas permanecen intactos. Recuperar primero el transporte o frontera válido más avanzado usando RECUPERAR.md; no volver a τ0 si existe un estado posterior.

## Incidentes administrativos conservados

El primer intento de respaldar τ=1.6 incluyó copias transitorias ajenas a la carga canónica y produjo un paquete de 608 504 980 bytes, cuya preparación de envío falló. La evidencia completa del fallo, estados y controles se conserva en el paquete canónico negativo de 425 146 306 bytes, SHA256 `c1ebfd444baed4efb025eb9f47121b57141e5650ee9145a846828ae7b4abdc9d`, recuperado con sus 110 archivos verificados. No fallaron las puertas físicas.

La primera prueba del adaptador sobre la extracción recuperada incluyó además un manifiesto raíz heredado y generó una entrada duplicada. La comprobación lo rechazó antes de M2 y se conserva como intento administrativo inválido. La selección fue corregida y registrada en `19c8b2b2eb40052ae81fc66e5ccc7acc76607348`; las funciones numéricas conservan AST idéntico y el serializador es byte a byte el mismo.

El nuevo respaldo τ=1.6 tiene 203 934 316 bytes y SHA256 `7b069c111340596a258252bd3fee767835d62078d74fecf0a459042214661c55`; sus 124 archivos y rehidratación independiente pasan. El NPZ conserva SHA256 `5776cceadd2ca07b94a25e4171791b068ed4205de06ac286564f4e6ef5869061`, y el recibo también quedó idéntico. Se reanudó el paso DOP853 existente: 296 pasos aceptados y 3974 evaluaciones vivas por malla. No se repitió 0→1.6.

Máximos hasta ese respaldo: energía FV 2.876830996e-9/6.949043563e-10; energía mixta 4.626332650e-11/4.619737926e-11; carga 6.661338148e-16/4.440892099e-16. Los cierres y Parseval pasan sus criterios originales. Son balances de un prefijo corto; la puerta espacial final y las demás dependencias CP12 siguen pendientes.

Para recuperar este respaldo, usar las fuentes capturadas de `conservacion_canonica_v2` del commit registrado y la guía `RECUPERAR.md`. Recuperar primero cualquier transporte o frontera posterior; no volver a τ0 si existe un estado más avanzado.

## Copias transitorias incompletas

Se registró y comprobó una limpieza administrativa separada del integrador (`15b84bf`). Los 13 controles sintéticos y el bloqueo de un único limpiador pasan sin M2. Las copias antiguas incompletas entran en cuarentena con inventarios de hashes después de un respaldo recuperado; su retirada requiere otro checkpoint posterior positivo. Se protegen los NPZ válidos, datos canónicos, negativos, fuentes y respaldos. Véase `COPIAS_TRANSFERENCIAS.md` y `OBSERVACION_CUARENTENA_TRANSFERENCIAS.json`.

## Actualización administrativa del entorno · 16 de octubre

Se actualizaron los cuatro auxiliares de conservación desde la versión vigente del entorno, conservando sus versiones anteriores y hashes en la evidencia privada. No se reinició el trabajador ni se modificaron sus fuentes científicas, configuración o estado cerrado. El transporte28.8 completó después la conservación, recuperación y auditoría independiente de14 comprobaciones.

Una actualización del registro de recuperación fue rechazada por conflicto entre una versión local15 y la vigente17. Se releyó el registro autoritativo y se aplicó la actualización válida con su guarda de versión, obteniendo18. Se conserva el incidente; no afecta a las cápsulas científicas ni autoriza repetir trayectorias.
