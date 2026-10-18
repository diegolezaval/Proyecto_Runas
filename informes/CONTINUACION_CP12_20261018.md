# CP12: recuperación y continuación desde τ52,8

El 18 de octubre se revisaron GitHub, el registro persistente de recuperación y las cápsulas disponibles. La rama seguía en `5c39ea1d1a407b0aadf8262252d488c081f7a47a`. Se encontró un transporte posterior **τ52,8** sin certificado externo conservado. No apareció una frontera posterior a τ48 ni un negativo científico nuevo. El registro persistente estaba en versión 33, con τ51,2 como último transporte auditado.

Dos recuperaciones independientes del transporte τ52,8 coinciden: **231132357 bytes**, SHA256 `29c54eca208b5306042a1a2063206d6c6d2a01d883fdb8c8c78572348662fcb7`. Pasan cobertura y hashes de los **328 archivos** de carga, CRC y las **14 comprobaciones** originales de recuperación. El estado interno tiene SHA256 `62b2ac0f3def5012d8b16fe8b88f6b3ab771f115056638f6248e6627e221788a`; el estado cerrado τ48 conserva `5c87b34631b504caaf4ad578cf5ee6e8eb6b12b7e2e4d9da3fcf5c7f7ffd98f1`. Se reconstruye el certificado desde esas recuperaciones; no se afirma haber observado el archivo local del antiguo emisor después de su subida.

La auditoría independiente adicional bloqueó construcción y avance de DOP853: **cero intentos y cero pasos M2**. Reprodujo bit a bit etapas, interpolaciones densas, contadores, estados físicos y observadores. Autenticó las catorce fuentes científicas, entradas, semillas CP10, configuración y recibo sin modificarlo. SciPy1.17.0 y los hashes de `rk`/`base` siguen idénticos; BLAS usa un hilo y la misma arquitectura SkylakeX. La deriva máxima FV es 2,479e-8, la mixta 1,524e-10 y la carga 8,882e-16, bajo sus puertas originales. Certificados: `checkpoints/CP12/continuacion_20261018/`.

La sesión anterior y sus identificadores propios dejaron de ser accesibles; no hay un cierre observado verificable. Su actividad se conserva como desconocida. Tras buscar avances posteriores, se recuperó el transporte en una raíz aislada y se observó el inicio del único trabajador propio de esta sesión, desde τ52,8 hacia τ56. No se repiten 0→52,8 ni A–D y no se reinicia DOP853. Se reutiliza sin modificar el supervisor administrativo registrado con aislamiento de las copias de subida y barrera espacial síncrona.

La última frontera completa del ensayo es **τ48**, con 28 controles positivos y error espacial de fases χ **0,7508082788 %**. τ52,8 es un transporte reanudable, no otra frontera científica. En cada nueva frontera se conserva, recupera y audita el estado completo antes de exigir las cinco métricas espaciales originales ≤2 %. Un fallo suspende esa continuación y conserva el negativo para el diagnóstico pasivo registrado. Ambas energías ≤2e-4, carga ≤1e-9 y los demás controles permanecen originales.

CP12 sigue abierto y CP11 es el último checkpoint científico aceptado. Main sigue en `ed8d818b622a0687aeb56d34ca9e3913bd54e124`; PR #2 permanece abierto y en borrador con su head histórico. Llegar a τ160 y superar el acuerdo entre dos mallas no bastan: quedan la verificación causal en las tres ventanas y las pruebas justificadas de convergencia, referencia, estabilidad y robustez. Los resultados son numéricos dentro de M2; no constituyen evidencia física experimental.

## Transporte posterior τ54,4

El primer transporte nuevo de esta sesión quedó guardado, recuperado y auditado: 231175107 bytes, SHA256 `26b2123c732d640fe04a3c12799a054b7faab6c4d903e30b69dfdac14fc3f4d5`, 339 archivos de carga y 14 controles positivos de cero pasos. Estado interno `168a61734524496cae39cc64053e66d60cff66d50abac75a727ad5ecc82ed74d`. La inspección independiente del archivo canónico después de la ruta completa reproduce tamaño y hash y confirma su separación de la copia de subida. Sigue vigente la frontera completa τ48; la siguiente es τ56.

[Figura derivada de las cinco métricas certificadas](figuras/CP12_mixto_prefijos.svg). Las fuentes y sus hashes figuran en el JSON adjunto; no se extrapolan valores entre fronteras o hasta τ160.

## Alcance del auxiliar de limpieza

El auxiliar propio de copias temporales de transferencia terminó con salida 1 al exigir tres copias en cuarentena de una sesión anterior que no estaban materializadas bajo runtime en esta recuperación. Sus registros, anteriores al inicio propio y relativos exclusivamente a copias temporales inválidas, estaban conservados. El trabajador M2 no se detuvo y no falló ninguna puerta científica. Tras registrar el procedimiento, los tres JSON se movieron byte a byte a ancestor, con mapeo de nombres, tamaños y SHA256, sin editar su contenido. El auxiliar original sigue con el mismo hash y volvió a emitir una comprobación válida sobre τ54,4. No se seleccionó un estado, ZIP canónico o negativo científico. Certificados: `PRERREGISTRO_LIMPIEZA_HEREDADA.json` y `SEPARACION_REGISTROS_CUARENTENA.json` en el registro del 18.

## Frontera τ56: conservación y cinco puertas positivas

La cápsula completa tiene **231337637 bytes**, SHA256 `5620a3171b6371fab3485bff8c9eb41a996b1b1c2b5d51878cca1829a7c996fb`. El estado cerrado tiene SHA256 `32fa195151ca4c7941dad6ab3b828c69979c0820220b0609839ed64bffe40150`. La recuperación independiente pasa los 28 controles con cero pasos M2. Máximos: E FV 2,564e-8; E mixta 1,607e-10; carga 8,882e-16; cierres 1,432e-6 y Parseval 2,039e-14.

| Métrica original | Error relativo (%) | Límite (%) |
|---|---:|---:|
| Norma temporal suprema | 0.0208614924 | 2 |
| Campo Φ | 0.0575775745 | 2 |
| Fases Φ | 0.1128965814 | 2 |
| Campo χ | 0.8334899370 | 2 |
| Fases χ | 1.1827210176 | 2 |

Las cinco pasan. El orden observado es conservación/auditoría completa 02:40:46 UTC, lectura espacial positiva 02:40:51 y comienzo de 56→64 a 02:40:52. El certificado de orden conserva los eventos completos. No se aplica la rotación descriptiva de χ a la aceptación. La continuación mantiene sus paradas; una nueva discrepancia >2 % detendrá esta versión. La frontera τ56 no cierra CP12 ni valida el continuo.

Transporte posterior recuperado: **τ57,6**, 231350117 bytes, SHA256 `c553e26b0410a3cd547a6393a3a8a56280c18a53c7ac363f10a2ca75b46fef7c`, 353 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `bd38267097bbb2d03843be526b805074ca3fde06ad8c14376bec78733513dbfa`. Continúa 56→64 con fronteras y puertas sin cambios; no es una nueva aceptación espacial.

Transporte posterior recuperado: **τ59.2**, 231378571 bytes, SHA256 `d127dcee4e13d74c0e99eb0e706978870a5fdab963abdeab9a4ca8d8c6b64781`, 360 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `ea8655fb47ae2078a9d93eb254410145fa03de44cd6cef41456cb89f642bf5c8`. Se mantiene la continuación condicionada a las puertas originales; no es una frontera espacial nueva.

Transporte posterior recuperado: **τ60.8**, 231415877 bytes, SHA256 `dcb0a4f0b737854b2953f7db3036ced2a34a4a3278d3bf4fc4803893290cc2c6`, 366 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `0597bc067150b3a1d04620123cd201188ac38e0ca30820c330b8cbd297dd2e12`. Se mantiene la continuación condicionada a las puertas originales; no es una frontera espacial nueva.

Transporte posterior recuperado: **τ62.4**, 231442602 bytes, SHA256 `d74bd2766b04eed6aa6866d91f445f3b2201501f42034e94f3ab1f8a3a52ae76`, 372 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `7f9dcb82f52e2f60dd15187b0bd5f5d31c412d3da2d6f5b81d625ead53da9ac1`. Se mantiene la continuación condicionada a las puertas originales; no es una frontera espacial nueva.

## Frontera τ64: conservación y cinco puertas positivas

La cápsula completa tiene **231609336 bytes**, SHA256 `f06537aa4b7774d34d4b02ff76b590767963279f2142d78a35dd1222f95ccb06`. El estado cerrado tiene SHA256 `d7618eb12a6f1444e56be0b696cfc0e232e60b0ed3b77002b5aa1cadcb8ae696`. Pasan las 28 comprobaciones de recuperación independiente con cero pasos M2. E FV ≤2,687e-8, E mixta ≤1,815e-10 y carga ≤8,882e-16.

| Métrica original | Error relativo (%) | Límite (%) |
|---|---:|---:|
| Norma temporal suprema | 0.0208614924 | 2 |
| Campo Φ | 0.0514054428 | 2 |
| Fases Φ | 0.0952335111 | 2 |
| Campo χ | 1.1358397905 | 2 |
| Fases χ | 1.6121229097 | 2 |

Las cinco métricas pasan. El registro de orden verifica recuperación/auditoría, lectura positiva y después comienzo de 64→72. No se ejecutó diagnóstico causal condicionado a un negativo, porque no ha ocurrido. CP12 continúa abierto; no hay aceptación del continuo ni evidencia experimental.

La [tabla de crecimiento medido](CRECIMIENTO_ERROR_CHI_MIXTO_CP12_20261018.md) conserva diferencias y factores entre prefijos, sin ajuste de una ley temporal ni extrapolación. La multiplicación disminuye en los últimos prefijos mientras el error absoluto de χ continúa aumentando. Esa tendencia no altera el umbral del 2 % ni decide fronteras futuras.

Transporte posterior recuperado: **τ65.6**, 231620991 bytes, SHA256 `27c534b0949c6f932932035eca56ec00f26bca407af4b2170e6a209913334f6d`, 385 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `0df7daf5f355412b79de8ab2aff8dbc1dfba1185b191b5dc25e8ff29f1340f83`. Se mantiene la continuación condicionada a las puertas originales; no es una frontera espacial nueva.

## Recuperación posterior τ70,4 (07:29 UTC)

Se encontraron transportes posteriores τ67,2, τ68,8 y **τ70,4**, sin frontera τ72 ni negativo científico nuevo conservados. La publicación anterior se había detenido en τ65,6: la comprobación de identidad del árbol rechazó el siguiente intento antes de mover la rama. Este incidente administrativo no detuvo inmediatamente al trabajador numérico, que dejó los dos respaldos posteriores. La sesión dejó de ser accesible sin cierre observado; su actividad queda desconocida. No se presume su terminación.

Dos recuperaciones independientes de τ70,4 coinciden: **231734063 bytes**, SHA256 `1a8d3b402ec003defa754303c516ef66e9a05c0174fe0b4885fcbac2a0cda223`. Pasan los **403 hashes**, las **14 comprobaciones** de rehidratación y otra auditoría que bloquea construcción y avance DOP853: cero intentos y cero pasos M2. Etapas, alias, interpolaciones, contadores, campos y observadores se reproducen bit a bit; recibo y configuración permanecen idénticos. Estado interno `db05e1f509f7749f687e58f954148beb000667903760e073ff335c894db836db`. SciPy1.17.0 y los hashes rk/base originales coinciden, con BLAS SkylakeX de un hilo. E FV ≤2,775e-8, E mixta ≤1,975e-10 y carga ≤8,882e-16.

La nueva sesión observó su propio comienzo desde τ70,4 hacia τ72 a las 07:29:47 UTC. Reutiliza el supervisor v2 y los controles registrados sin repetir 0→70,4, A–D ni reiniciar DOP853 dentro del tramo. La última frontera completa sigue en τ64, con χ fases 1,6121229097 % y las cinco métricas positivas. Se mantienen las barreras de conservación, recuperación, auditoría y las cinco puertas antes del tramo siguiente.

Se preservaron por separado los tres registros heredados de cinco copias temporales no materializadas, con hashes y bytes idénticos; el auxiliar original de limpieza no se cambió. La referencia original τ160 se recuperó con sus 254 hashes y su NPZ exacto, sin repetir M2, para el diagnóstico condicionado si se produce un negativo. Las pruebas adicionales y la causalidad final siguen pendientes. CP12 abierto; CP11 aceptado; main intacto y PR2 en borrador.

## Frontera τ72: cinco puertas positivas, margen pequeño

Cápsula completa: **231918011 bytes**, SHA256 `03d0f4b224edf24befe58c21172f27293e15ec89603b8b364d52446a918a3399`. Estado cerrado: `2f7bd352c91e0b122632c15579624696fb8d327e352f51147c050c215b7b0f25`. Pasan las 28 comprobaciones de recuperación independiente con cero pasos M2 y los cinco límites espaciales originales.

| Métrica original | Error relativo (%) | Límite (%) |
|---|---:|---:|
| Norma temporal suprema | 0.0208614924 | 2 |
| Campo Φ | 0.0408335556 | 2 |
| Fases Φ | 0.0749354604 | 2 |
| Campo χ | 1.4050053301 | 2 |
| Fases χ | 1.9942703120 | 2 |

Fases χ=1,994270311985376 %, margen de 0,005729688014624 puntos porcentuales frente al 2 %. No se redondea la puerta ni se usa la rotación descriptiva de χ. El orden observado conservación/auditoría→cinco métricas positivas→comienzo de 72→80 queda en el certificado de orden. El diagnóstico causal condicionado a un negativo no se ejecuta: esta frontera pasa. CP12 sigue abierto; causalidad final y convergencia/referencia/estabilidad/robustez pendientes.

Transporte posterior recuperado: **τ73,6**, 231923675 bytes, SHA256 `b6c8beac9576073386c7146e99958509731215b4cd2f6dd69dabf6038caad34f`, 424 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `6b589787d34ec40cd89c82945abae3a8755c55160d364f048e2bbcea258f8297`. La última frontera completa con cinco puertas positivas es τ72; este transporte permite reanudar exactamente DOP853 dentro de 72→80 sin ser una nueva aceptación espacial.

Transporte posterior recuperado: **τ75,2**, 231958735 bytes, SHA256 `130d09d5845a1d633336c2fc9c2746f36898bf19c5e044c1ae693dc126a087bd`, 430 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `322290cc199e24f5e2eea0a93324b58395d194f65cf3a6817729d68e964c23dc`. Se conserva la reanudación exacta del tramo 72→80; la última frontera completa con cinco puertas positivas sigue siendo τ72.

Transporte posterior recuperado: **τ76,8**, 232009894 bytes, SHA256 `0f555fa48c231abc8345a0ec9146f727d009711bf983cdbcf1b114696de5e471`, 437 archivos íntegros y 14 controles de cero pasos positivos. Estado interno `38344efb88f4800f40f7931901e21adf0fd68f791afc823b464d25bbae1ba1db`. Se conserva la reanudación exacta del tramo 72→80; la última frontera completa con cinco puertas positivas sigue siendo τ72.
