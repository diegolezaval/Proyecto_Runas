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
