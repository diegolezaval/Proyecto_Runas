# Auditoría de arquitectura de Rúnica — diagnóstico previo a los cambios

Fecha: 2 de octubre de 2026. Entrada científica: CP08_REFINAMIENTO_NO_RADIAL, proyecto 4.2.0-dev8, modelo fundamental M2. Este documento se terminó antes de modificar el proyecto reconstruido. Las pruebas se ejecutaron en una copia desechable. No se investigaron nuevas soluciones ni se ejecutaron campañas históricas.

## 1. Dictamen

**La arquitectura es adecuada como base de investigación y merece conservación, pero necesita corregir su infraestructura de continuidad antes de crecer durante años.** No hay evidencia que justifique trasladar todo a otra jerarquía, convertir los scripts en una aplicación empresarial o sustituir los formatos actuales. El problema principal es que la autoridad científica está razonablemente definida, mientras que algunas comprobaciones, entradas y enlaces todavía mezclan el contexto histórico con el vigente.

La separación tratado/datos/herramientas/validacion/fichas/graficos/trazabilidad funciona. Las puertas y límites son explícitos; una campaña terminada puede dejar una etapa parcial; los resultados negativos se conservan. La reconstrucción entregada es íntegra. Sin embargo, el comando de verificación de M2 falla por enlaces de instantáneas históricas, el verificador de preparación de CP04 falla al consultar el estado de C7 de CP08 y requirements.txt omite threadpoolctl. No son fallos del modelo físico, pero sí fallos reales de reproducibilidad operacional.

La trazabilidad documental de las conclusiones principales existe. La procedencia ejecutable completa de todos los archivos numéricos todavía no existe: numerosos estados carecen de huella del código y de Θ usados durante su ejecución. Un índice creado hoy puede describir los bytes recibidos y unir referencias existentes; no puede inventar metadatos retrospectivos.

## 2. Alcance y evidencia de entrada

| Paquete | Función comprobada | Archivos | Bytes descomprimidos |
|---|---|---:|---:|
| Proyecto_Runas_M2_4_2_CP08_PROYECTO(2).zip | Corpus principal, código, informes, fuentes, resultados y estados de preparación/no radial | 726 | 86 481 821 |
| Proyecto_Runas_M2_4_2_CP08_ESTADOS_ACCESO(2).zip | 60 estados de acceso lineal/colocación, incluidos intentos fallidos | 60 | 28 506 315 |
| Hoja_de_ruta_M2_4_1(2).zip | Plan maestro original, también archivado dentro del corpus | 8 | 289 915 |

La unión de los dos paquetes CP08 tiene 786 archivos y 114 988 136 bytes. No hay nombres compartidos ni sobrescrituras. El manifiesto enumera los 785 archivos distintos de sí mismo y coincide con sus hashes. Todos los ZIP de entrada pasan CRC. Los ocho archivos de la hoja de ruta externa son idénticos a hoja_ruta_original/. El SHA-256 del ZIP fuente 4.1 coincide con baseline_sha256.

Se inventariaron todas las rutas, JSON, scripts Python, SVG, estados NPZ y referencias locales exactas. La entrada contiene 279 JSON, 52 Python, 66 SVG, 92 Markdown, 91 CSV, 87 NPZ, 110 logs, cuatro PNG y dos ZIP históricos. Las referencias JSON exactas auditadas son 2037; las cinco rutas inexistentes pertenecen a propuestas futuras de la hoja original. No se deben crear archivos ficticios para satisfacerlas.

Se comprobó la lectura de los 87 NPZ con allow_pickle=False. Hay 86 legibles con arrays numéricos finitos y un NPZ ilegible del intento complejo de colocación Ω=5: validacion/P06/acceso_lineal/colocacion_Om5.0000_estado.npz. El JSON compañero declara success=false y passed=false; existe una colocación real/imaginaria posterior válida. El archivo ilegible se conserva como evidencia material del intento, pero no debe presentarse como estado reanudable. No se puede recuperar su contenido ausente mediante organización de carpetas.

No se certificó nuevamente cada teorema, ni se realizó revisión científica externa, calibración experimental, estabilidad del continuo o reproducción costosa de todas las campañas. Las comprobaciones numéricas realizadas leen resultados ya guardados y recalculan diagnósticos o cuadraturas limitadas. Una verificación estructural correcta no convierte en superada la puerta científica fallida.

## 3. Qué es el proyecto y dónde reside su autoridad

Rúnica intenta construir una física y una ingeniería coherentes para un sistema ficticio de runas, hasta obtener una cadena cuantitativa de teoría, parámetros comunes, soluciones, estabilidad, preparación, interacción, comportamiento micro/macroscópico, componentes y dispositivos. Las 24 primordiales son funciones propuestas y evaluadas; no se obliga a conservar su número ni se aceptan como tecnologías sólo por disponer de fichas. M2 es el modelo fundamental escalar actual, con Φ complejo y χ real; R1 es una especificación operacional con metas adoptadas, y M1 conserva aproximaciones/antecedentes. La versión 4.2 del corpus no representa una nueva ley fundamental.

| Responsabilidad | Autoridad | Dependencia o límite |
|---|---|---|
| Acción y resultados analíticos | Capítulos fuente, especialmente tratado/13, 18, 20–21 y 23–30 | Hipótesis y convenciones explícitas; 23 corrige las convenciones de 20 |
| Parámetros físicos comunes | datos/theta_comun.json, interpretado por modelo_m2.ScalarModel | Los espejos históricos del benchmark son controles, no un Θ alternativo |
| Metas R1 y geometría | datos/parametros.json, geometria.json, interfaces.json, modelos.json y recetas.json | Son contratos/plantillas, no mediciones ni dispositivos demostrados |
| Clasificación científica | datos/estado_evidencia.json y evidencia enlazada | El booleano passed de una prueba no cierra por sí solo una etapa |
| Progreso operativo | estado_progreso.json | ESTADO_ACTUAL.md e informes son explicación; la evidencia reproducible prevalece ante conflicto |
| Cálculos y resultados vigentes | datos/registro_calculos.json y sus authoritative_results | No confundir cálculos terminados con etapas completadas |
| Ruta de investigación | hoja_ruta_original/Guia_tecnica.md | Plan_investigacion.json es su proyección estructurada original |
| Enmiendas | ENMIENDAS_HOJA_RUTA.md | No modifica silenciosamente el plan original ni relaja puertas |
| Fuentes históricas | trazabilidad/fuente_M2_4_0.zip, fuente_M2_4_1.zip e instantáneas CP* | Deben conservarse con sus versiones y no gobernar el estado actual |
| Integridad de una entrega | MANIFIESTO_SHA256.json y comprobación CRC | Garantiza identidad de bytes; no garantiza verdad de las conclusiones |

La autoridad científica es un conjunto coherente de fuentes con responsabilidades diferentes, no un solo archivo mágico. El orden de DIRECTRICES_EJECUCION.txt es razonable: evidencia actual → estado/progreso/informes → enmiendas → plan original → conversaciones. Conviene conservarlo.

El estado vigente tiene E00/E01/C0 COMPLETADAS; E02/E03/E04/RES0/RES1/C7 PARCIALES; RES2 BLOQUEADA; cero dispositivos completos. No hay ejecuciones activas. La cuarta evolución adaptativa terminó en τ=160. El refinamiento h=.25→.125 deja χ en 3,45323 % de error de posiciones y 5,04292 % incluyendo velocidades frente al límite del 2 %. La decisión sigue siendo REFINAMIENTO_PENDIENTE. Estos valores se toman del resultado CP08; no se modifican para mejorar el dictamen arquitectónico.

## 4. Fuentes, resultados, vistas e historia

No todos los archivos de datos/ son entradas manuales. datos/aceptacion_m2.json y tratado/17_aceptacion_catalogo.md se producen mediante catalogo_aceptacion_m2.py; parte del razonamiento de aceptación está codificada en ese script. No debe regenerarse ese registro como un trámite editorial cuando cambie evidencia nueva sin revisar antes su lógica. Asimismo, tratado/05, 06, 07, 11 y 17 son salidas de generadores/verificadores distintos; la carpeta tratado/ mezcla capítulos fuente con vistas documentales, pero una clasificación explícita resuelve la ambigüedad sin romper sus rutas.

generar.py produce las fichas, SVG de geometría, atlas, tablas 05/06 y documento integrado; no calcula todo el contenido científico ni genera todos los gráficos. verificar.py genera el capítulo 07 y su informe; resultados_micro.py produce 11; catalogo_aceptacion_m2.py produce 17; otros scripts generan las figuras científicas. El capítulo 19 es un resumen histórico manual de la base 4.0 y se conserva como tal. regenerar.py no existe y no debe prometerse un comando único ficticio. La arquitectura necesita un mapa de generadores y un modo de comprobación aislado, no convertir todas las vistas en fuentes editables.

Los CSV y NPZ de campañas concluidas son resultados derivados, pero también evidencia y estados de continuación que deben preservarse. «Generado» no significa «prescindible». Ejecutar otra vez un solver puede sobrescribir la evidencia con otra malla, entorno o implementación y producir bytes diferentes. Para leer/verificar un checkpoint se debe preferir la comprobación de los resultados incluidos; para reproducir históricamente, una copia aislada.

El documento integrado duplica intencionalmente capítulos y fichas para lectura. Los NPZ más CSV finales ofrecen estado de Cauchy y datos legibles con funciones diferentes. La hoja original interna y externa dan autosuficiencia y referencia histórica. Los manifests históricos y los archivos parciales fijan antecedentes. Estas duplicaciones son justificadas. En cambio, las cabeceras manuales con listas de estados repetidas en LEEME, M2_RESULTADO y ESTADO_ACTUAL tienen riesgo real de desactualización; la nota C7 en investigacion/ aún afirma EN_PROGRESO aunque su subpregunta se resolvió en CP05.

## 5. Hallazgos y decisión de cada cambio

En la tabla, «aplicar» significa una corrección compatible de esta auditoría. «Plan futuro» conserva el corpus y describe la migración antes de intervenir.

| ID | Problema comprobado o riesgo delimitado | Clasificación | Decisión y justificación |
|---|---|---|---|
| A01 | LEEME tiene tres instrucciones «empieza por» y combina entradas 4.1/CP08 | NECESARIO | Reescribir sólo la entrada y enlazar fuentes/estado/continuación; archivar sus bytes previos |
| A02 | Estado y cabeceras repetidos manualmente | RECOMENDABLE | Generar ESTADO_ACTUAL desde progreso y registros; convertir la cabecera de M2_RESULTADO en enlace contextual, conservando su contenido científico |
| A03 | threadpoolctl se importa en tres scripts y no está declarado | NECESARIO | Añadir la versión instalada/probada 3.6.0; no cambiar NumPy/SciPy/Matplotlib |
| A04 | Integrador adaptativo importa fcntl; el documento permite inferir portabilidad Windows nativa | NECESARIO | Documentar Linux/POSIX como entorno probado y comprobar entorno; no cambiar el bloqueo por una implementación no ensayada multiplataforma |
| A05 | verificar_m2.py falla al resolver copias históricas como documentos locales independientes | NECESARIO | Centralizar contexto de enlaces de instantáneas declaradas; conservar sus archivos originales y seguir detectando enlaces rotos actuales |
| A06 | Verificador CP04 consulta C7 vigente y exige EN_PROGRESO aunque CP05 lo cambió a PARCIAL | NECESARIO | Verificar el contexto histórico CP04; comprobar el progreso actual en la regresión de continuidad. No cambiar puertas científicas |
| A07 | Verificadores escriben informes y algunos resultados al verificar | NECESARIO | Añadir una regresión en copia temporal que conserve el corpus e identifique cambios; mantener herramientas históricas disponibles |
| A08 | Dos empaquetadores usan versiones/exclusiones diferentes; empaquetar.py fija edition=4.1.0 | NECESARIO | Mantener una implementación vigente y delegar desde el nombre histórico; registrar el original |
| A09 | Exclusión de cache en checkpoint.py sólo cubre hijos inmediatos; no excluye .git ni entornos | NECESARIO | Excluir recursivamente categorías de ejecución explícitas y rechazar temporales científicos pendientes; nunca ignorar resultados por extensión de forma indiscriminada |
| A10 | Integridad sin verificación de identidad edition/checkpoint y varias precondiciones con assert | RECOMENDABLE | Usar errores explícitos para integridad/empaquetado y exigir coherencia administrativa; no alterar los assert de ecuaciones y aceptación científica |
| A11 | datos/linaje_afirmaciones.json cubre 16 de las 26 afirmaciones actuales | NECESARIO | Conservar ese linaje inicial de E00 y añadir índice derivado que una las 26 con sus fuentes actuales y enlaces adicionales; no editar evidencia de E00 |
| A12 | Estado numérico ilegible de un intento fallido aparece entre estados sin advertencia mecanizada | NECESARIO | Catalogarlo por ruta y hash como histórico no utilizable, respaldado por su resultado fallido. Conservarlo exactamente; detectar cualquier nuevo ilegible como error |
| A13 | Muchos estados no guardan huella de Θ/código ejecutados | RECOMENDABLE | Indexar sólo metadatos existentes y hashes del snapshot actual; definir recibo para futuras ejecuciones. No inventar procedencia retrospectiva ni reescribir 87 NPZ |
| A14 | Identidad de ejecuciones por nombres redondeados; locks usan parámetros completos y pueden diferir para el mismo destino | NECESARIO | En el integrador adaptativo, bloquear por el destino efectivo; conservar el nombre/configuración/cálculo y probar colisiones sin evolución |
| A15 | Nota antigua C7 parece investigación pendiente | NECESARIO | Añadir advertencia histórica y enlaces a CP05/27 y CP07/30; conservar el texto original archivado |
| A16 | Árbol validacion/ crece con resultados, fallos, estados y logs; 497 archivos, 90,3 % de bytes | RECOMENDABLE | Añadir inventario por rol y relaciones de vuelta. Futuras campañas usarán una subcarpeta/identificador completo; no mover campañas concluidas |
| A17 | Versión de proyecto, modelo, esquema, checkpoint y R1 pueden confundirse | RECOMENDABLE | Mantener VERSIONES y aclarar nomenclatura en arquitectura; separar checkpoint administrativo del último científico |
| A18 | Figuras científicas tienen generadores distintos y algunos SVG llevan fecha/IDs variables | RECOMENDABLE | Documentar regeneración y verificar repetibilidad; no alterar gráficos históricos sólo para obtener hashes bonitos. La identidad del ZIP se comprueba por separado |
| A19 | Parámetros/conclusiones redondeados en prosa no se recalculan automáticamente | RECOMENDABLE | Dejar advertencia y enlaces; futuras cifras repetidas deben venir de tablas generadas. No hacer sustituciones globales de números |
| A20 | Plan contiene dependencias expresadas en texto, por ejemplo «E06 o E07» | OPCIONAL | Un esquema de dependencias booleanas puede añadirse cuando haga falta un planificador. Hoy no inferir habilitaciones automáticas de esas cadenas |
| A21 | Lógica de catálogo depende de conclusiones codificadas y puede quedar atrás de nuevos checkpoints | RECOMENDABLE | Declarar el generador como evaluador científico que requiere revisión; separar su futura política de las vistas. No regenerar aceptación sin esa revisión |
| A22 | No hay política Git ni exclusiones de artefactos de ejecución | RECOMENDABLE | Añadir exclusiones estrechas y conservación de bytes; proponer LFS/Releases por papel, sin activar LFS ni eliminar archivos |
| A23 | Grandes estados futuros y trabajo simultáneo pueden generar colisiones y crecimiento del historial | RECOMENDABLE | Protocolo de ejecución/inmutabilidad y publicación por checkpoint; migración futura con recibos, hashes y recuperación ensayada |
| A24 | Biblioteca Python empaquetada/instalable y CI remota completa | OPCIONAL | Documentar posible evolución; no implantar infraestructura sin demanda efectiva |
| A25 | Reorganización total de carpetas, renumeración de capítulos/primordiales o conversión de formatos | NO CONVIENE CAMBIAR | Beneficio actual bajo y riesgo alto de romper citas, hashes, snapshots y hábitos de continuación |
| A26 | Supresión de fallos, snapshots, ZIP fuente, vistas o datos «por duplicados» | NO CONVIENE CAMBIAR | Destruiría evidencia, reproducibilidad o lectura autónoma; conservar sus funciones distintas |

## 6. Trazabilidad científica en ambas direcciones

| Caso | Cadena que sí existe | Punto de ruptura o límite |
|---|---|---|
| Tensión/interfaz WALL | Cap. 13/20 → Θ → ensayo_capilaridad → capilaridad_m2 → pared.csv/resultados → figuras_capilaridad → M2_capilaridad.svg → verificacion → alcance en evidencia | Θ está hasheado; falta un recibo uniforme del código exacto en cada corrida. La prosa redondeada se mantiene manualmente |
| Tubo libre negativo | Cap. 18/21 → mismo Θ → guia_m2 → perfil y guia_m2.json → figura → TUBE-NEGATIVE y C0 | Buena limitación de clase; no convertir el rechazo de ese tubo en imposibilidad de cualquier Canal |
| No radial CP08 | Cap. 28 → Θ/Evolution → configuración CP06 con extensiones → NPZ CP04 y hash de transferencia → 12 evoluciones → CSV/NPZ/resultados → comparaciones → puerta → registro/progreso/informe | Los estados guardan configuración y origen, pero no identifican uniformemente el código/Θ de ejecución. Los casos candidatos no son todos casos ejecutados |
| Acceso lineal CP07 | Cap. 29 → Θ → perfil ω=.9 y hash → protocolo CP07 → dispersion_reserva → matrices/NPZ/JSON → colocación real/auditor → puerta_decision → evidencia/progreso | Cinco colocaciones legibles sólo contienen r/y; la configuración depende del JSON compañero. Existe un NPZ fallido ilegible; no prueba inválida del resultado vigente |
| Simetría/fase C7 | Cap. 27/30 → hipótesis → auditor de identidades → fichas/puertas → registros CP05/CP07 | La validación algebraica no sustituye la prueba funcional ni revisión externa; la nota exploratoria quedó sin marcar como histórica |
| Metas R1/fichas | JSON de geometría/contratos/metas → generar → ficha/atlas/integrado | Sus cifras no son predicciones M2 ni evidencia de dispositivo; mantener la advertencia de aceptación |

Desde un resultado individual suele poder encontrarse el JSON/configuración compañero por su tag, pero el retorno a la afirmación o puerta no es uniforme. registro_calculos agrupa campañas; el linaje inicial no cubre las nuevas afirmaciones. Se necesita un índice derivado bidireccional que conserve referencias a sus autoridades, no un nuevo registro manual de conclusiones. Donde sólo hay asociación por familia o por lectura del script, se debe etiquetar como enlace declarado/reconstruido, no como metadato capturado durante la ejecución.

## 7. Reproducibilidad comprobada antes de editar

Diez comandos se ejecutaron desde un directorio distinto al proyecto en una copia aislada. checkpoint --verificar, continuidad, verificar.py, capilaridad, campaña CP03, no radial, puerta de acceso y generar pasan. verificar_m2 falla sólo por los enlaces históricos; verificar_preparacion falla sólo por consultar C7 fuera de su contexto CP04. Sus fallos y logs se preservarán. generar reproduce idénticamente sus vistas actuales. Los verificados científico-numéricos no sustituyen sus puertas generales.

El corpus no depende de rutas absolutas /mnt/data, /workspace, /tmp, /home o /root en el código o JSON operativo auditados. Los scripts calculan su raíz mediante __file__. prolongar_captura_radial acepta una ruta explícita del usuario: su relación con cwd es una entrada normal, no una dependencia oculta. Las bibliotecas instaladas coinciden con los pins publicados; la omisión comprobada es threadpoolctl. La fuerza C es opcional y su fuente está incluida; no se necesita conservar el .so de cache para la ruta NumPy.

Las continuaciones guardan campos y velocidades, tiempo o paso, configuración y diagnósticos, y escriben el NPZ mediante temporal/replace. El adaptativo tiene bloqueo de escritor único, aunque su clave debe alinearse con el destino. No se hizo un paso de integración para demostrar reanudación: se verificó la legibilidad, coherencia, procedencia existente y lógica de carga; los cálculos cerrados se conservaron.

Un entorno nuevo puede reconstruir el corpus, verificar los hashes, leer el progreso, distinguir las campañas terminadas y reconocer las pendientes. Puede ejecutar diagnósticos sobre resultados guardados y regenerar las vistas enumeradas. La ejecución histórica completa requiere el entorno declarado y es una tarea aparte; las cinco rutas futuras del plan no son dependencias del checkpoint actual. La independencia de cachés se obtiene comprobando copias extraídas sin ellas, no anunciando una reproducción física integral no realizada.

## 8. Escalabilidad y arquitectura objetivo mínima

Mantener las ocho carpetas actuales. Añadir únicamente un mapa de autoridad/generadores, clasificación de artefactos, índice derivado de trazabilidad, verificación aislada y metadatos de continuidad. Los capítulos y resultados históricos conservan sus rutas. La dimensión nueva «modelo» se introduce por metadatos en futuras campañas, antes que por mover cientos de archivos.

| Crecimiento | Qué escala bien | Qué necesita control |
|---|---|---|
| Más simulaciones | Protocolos JSON, datos brutos, puertas y estados completos | Identificador no redondeado, recibo de ejecución, carpetas por campaña nueva e índice |
| M3 u otros modelos | Identidad M2 y cinco coordenadas explícitas | Código/Θ propios por modelo y vínculo de dependencia; una versión del corpus no cambia el modelo |
| Más ramas/primordiales/dispositivos | Identificadores P-xx, contratos y clasificación de aceptación | No sostener cantidades fijas 24 en todas las herramientas cuando se amplíe realmente el catálogo |
| Estados grandes | NPZ comprimidos, manifiestos y entrega complementaria | I/O lineal de hashing/empaquetado y conservación de toda la historia; evaluar LFS/artefactos por contenido |
| Manuales/normas/educación | Markdown/JSON/SVG y vistas generadas | Vistas por público con enlaces a evidencia; evitar copiar conclusiones a múltiples fuentes manuales |
| Experimentos futuros | Taxonomía de evidencia y separación de metas | Datos brutos, calibración, incertidumbre, protocolo y procedencia distinta de simulación; no crear ahora carpetas vacías |
| Varias personas/agentes | Puertas e informes delimitados | Rama/copia por tarea; una sola autoridad para progreso; no editar simultáneamente NPZ ni regenerar vistas sobre otra campaña |

Antes de una migración grande: congelar manifiesto, crear mapa origen→destino con hashes, construir copia, reescribir referencias con reglas verificadas, ejecutar regresiones de ambas direcciones, probar extracción y recuperación, y conservar las rutas históricas o un mapa estable. No cambiar la estructura original hasta que esos controles pasen.

## 9. Comparación de costes para cambios importantes

| Cambio | Beneficio actual/futuro | Riesgo de trazabilidad | Coste | Decisión |
|---|---|---|---|---|
| Entrada clara y estado generado | Alto ahora; evita errores de continuación futuros | Bajo con snapshots y enlaces | Bajo | Aplicar |
| Verificador contextual y ejecución aislada | Alto; corrige fallos observados sin recalcular | Bajo, con pruebas que no oculten enlaces rotos | Bajo/medio | Aplicar |
| Índice derivado y roles explícitos | Alto para 26 afirmaciones/786 archivos; creciente | Bajo si no inventa procedencia | Medio | Aplicar |
| Empaquetador único y exclusiones recursivas | Alto para Git y checkpoints futuros | Bajo, si no excluye evidencia | Medio | Aplicar y probar determinismo |
| Mover validacion a runs/modelos/fecha | Moderado hoy; alto con muchas campañas | Alto por referencias, snapshots y nombres | Alto | Diseñar para campañas nuevas; no mover las actuales |
| Reescribir todos los solvers a biblioteca | Bajo/medio hoy; condicionado a múltiples modelos | Alto por regresión numérica | Alto | Posponer |
| Normalizar schemas antiguos y reescribir NPZ | Poco beneficio inmediato | Muy alto por hashes y procedencia retrospectiva | Alto | Conservar; contrato de recibo para próximos estados |
| Activar LFS y sacar binarios del corpus | Bajo ahora; aumenta con historial grande | Medio/alto si faltan objetos al recuperar | Medio | Proponer, sin activar ni borrar |

## 10. Qué mantener exactamente

No mover tratado/, datos/, herramientas/, validacion/, fichas/, graficos/, informes/, investigacion/ ni trazabilidad/. Mantener las fuentes originales y hoja_ruta_original byte a byte; las 24 identidades P-01…P-24 y sus geometrías racionales; la distinción M1/M2/R1; el Θ común y sus convenciones; todos los perfiles, estados, resultados negativos e informes científicos; las puertas y dependencias; los cierres E00/E01/C0; la posibilidad de entrega complementaria; los formatos abiertos y el documento integrado generado.

No renumerar capítulos para que coincidan con etapas ni convertir todos los documentos en un único archivo manual. No considerar superada una prueba sólo porque el JSON o SVG parsea. No eliminar duplicados de respaldo ni candidatos fallidos. No implantar base de datos, gestor de flujo remoto o arquitectura de microservicios para este corpus.

## 11. Git/GitHub

El corpus puede almacenarse en Git tras corregir empaquetado/exclusiones; no necesita GitHub para ser reproducible. El mayor archivo individual actual es fuente_M2_4_1.zip, 6 022 627 bytes; no existe un bloqueo actual por un archivo de más de 100 MiB. El problema futuro sería el historial de estados y ZIP repetidos, no el número de carpetas.

| Categoría | Destino propuesto | Regla de conservación |
|---|---|---|
| Python/C, Markdown, JSON, configuraciones, SVG | Git directo | Autoridad legible, revisión de cambios y bytes preservados |
| CSV pequeños y resultados/diagnósticos de referencia | Git directo | No ignorar sólo por ser generados; distinguir evidencia de vista |
| CSV voluminosos y NPZ requeridos para continuar | Actualmente conservados; LFS cuando tamaño/recambio lo justifique | Objetos completos, hashes, prueba de clon/descarga y unión; no basta un puntero |
| ZIP completos de nuevos checkpoints | Releases/artefactos fuera del árbol de trabajo | Entrega autosuficiente con manifiesto y recibo de hashes |
| Dos ZIP fuente históricos ya integrados | Mantener ahora; futura externalización sólo con recuperación declarada y ensayada | No borrar bajo una regla global *.zip |
| Figuras/vistas generadas de una entrega | Git o artefacto según tamaño y revisión | Fuentes y generadores; conservar las incluidas para lectura sin entorno |
| Logs que explican intentos/errores | Git o artefacto según tamaño | No usar una exclusión global *.log |
| .git, .venv, __pycache__, .pyc, cache compilada y locks de ejecución | Ignorar/excluir del checkpoint | Nunca confundir cache con NPZ científico |
| Temporales de escritura de estados | No entregar como estado válido | Rechazar un empaquetado con escritura científica pendiente; no borrar automáticamente |

Fuentes oficiales consultadas el 2-10-2026: [límites de archivos](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github), [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) y [LFS en archivos ZIP](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-git-lfs-objects-in-archives-of-your-repository). GitHub bloquea archivos Git normales mayores de 100 MiB. LFS conserva punteros y objetos aparte, y los ZIP automáticos incluyen por defecto sólo punteros. Por ello, un ZIP de código de GitHub no debe sustituir sin prueba al checkpoint completo.

No se creará un repositorio remoto, publicará contenido, activará LFS, borrará datos o migrará historia Git durante esta auditoría. La preparación local compatible sí es justificable.

## 12. Plan de aplicación y límites pendientes

Aplicar únicamente los cambios compatibles A01–A17 y A22 con el alcance específico de la tabla. A18–A21 y A23–A24 se documentan o se preparan parcialmente sin refactorizar ciencia. Archivar antes cada archivo existente que se vaya a editar, conservar el manifiesto de entrada y guardar el inventario de sus bytes. Registrar altas/ediciones y copias históricas; no habrá movimientos ni renombrados de fuentes científicas.

Después: comprobar contexto documental, estados y referencias; ejecutar regresiones limitadas en copia; comparar todos los archivos científicos de CP08 por SHA-256; comparar los 33 registros de etapa sin cambios; reconstruir CP08 usando las instantáneas; generar el checkpoint administrativo CP09, extraerlo en una ruta nueva, verificar integridad, regeneración e independencia de cwd; empaquetar dos veces para comprobar identidad binaria.

Los límites que deben seguir visibles son la ausencia de recibos uniformes de ejecución antiguos, el estado fallido ilegible, el versionado por tags redondeados en los scripts históricos, el contexto POSIX del adaptativo y la falta de certificación global de ciencia/dispositivos. El checkpoint mejorado debe permitir descubrirlos, no declararlos solucionados por añadir documentación.
