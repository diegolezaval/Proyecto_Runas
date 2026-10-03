# Auditoría de arquitectura de Rúnica — CP09

Fecha: 2 de octubre de 2026. Entrada científica: CP08_REFINAMIENTO_NO_RADIAL, proyecto 4.2.0-dev8, modelo fundamental M2. Las secciones 1–12 contienen el diagnóstico terminado antes de modificar el proyecto reconstruido; su versión previa intacta se conserva en trazabilidad/arquitectura/DIAGNOSTICO_PREVIO.md. Las secciones 13–17 registran la aplicación y comprobación. Las pruebas se ejecutaron en copias desechables. No se investigaron nuevas soluciones ni se ejecutaron campañas históricas.

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

## 13. Cambios aplicados y arquitectura resultante

La entrega es **CP09_AUDITORIA_ARQUITECTURA, versión del proyecto 4.2.0-dev9**. El último checkpoint científico sigue siendo **CP08_REFINAMIENTO_NO_RADIAL**. El modelo fundamental continúa siendo M2, y el esquema de continuidad previo se conserva. Se añadió una coordenada de esquema arquitectónico 1.0.0. CP09 no cierra etapas, abre campañas ni modifica puertas o conclusiones.

| Intervención compatible | Archivos y efecto concreto | Hallazgos atendidos |
|---|---|---|
| Entrada y navegación | LEEME.md explica objetivo, autoridades y comandos; README.md remite a esa entrada; ARQUITECTURA.md describe roles, entorno, generadores y continuidad | A01, A03, A16, A17 |
| Estado como vista | generar_continuidad.py produce ESTADO_ACTUAL.md desde los registros vigentes y comprueba desactualización con --comprobar; M2_RESULTADO.md remite al estado sin repetir una cabecera CP08 | A02, A03 |
| Contexto histórico | rutas_documentales.py interpreta únicamente las raíces de instantáneas declaradas; verificar_m2 y verificar_continuidad lo utilizan. Los enlaces actuales rotos siguen fallando | A04, A05 |
| Verificación CP04 | verificar_preparacion_m2.py consulta el progreso congelado de CP04 para su puerta histórica C7, y declara ese contexto. La puerta vigente se comprueba por separado | A06 |
| Comprobaciones sin contaminar el corpus | Continuidad es de sólo lectura por defecto; --salida es explícito. regresion_estructural.py ejecuta verificadores y generadores que escriben únicamente en una copia temporal | A07 |
| Empaquetado común | checkpoint.py verifica y empaqueta; empaquetar.py es una entrada compatible al mismo código. Lee la identidad del progreso/versiones, excluye ejecución recursivamente, rechaza temporales científicos y enlaces externos, comprueba cobertura y genera ZIP determinista | A08, A09, A10 |
| Entorno explícito | requirements.txt añade threadpoolctl==3.6.0; verificar_entorno.py comprueba pins y compatibilidad POSIX del adaptativo | A11 |
| Trazabilidad derivada | datos/arquitectura.json declara roles y enlaces sin copiar conclusiones; generar_continuidad.py produce el índice bidireccional desde evidencia, linaje, registro, progreso y esos metadatos | A12, A13, A16 |
| Seguridad del destino de un estado | continuar_no_radial_adaptativo.py bloquea por el destino efectivo del tag, de modo que configuraciones distintas que redondean al mismo nombre compartan bloqueo. Conserva cálculo, nombre y configuración; sigue rechazando reutilización incompatible | A14 |
| Nota exploratoria C7 | Se añade un aviso de antecedente y enlaces a los resultados posteriores; el texto original y su ruta se conservan | A15 |
| Registro administrativo | VERSIONES.json, estado_progreso.json y enmienda A06 identifican la auditoría, su alcance y sus enlaces; los 33 registros de etapa no cambian | A17 |
| Git local | .gitignore excluye sólo artefactos de ejecución; .gitattributes preserva bytes y finales de línea. No se activa LFS ni se crea/publica repositorio remoto | A22 |
| Diagnóstico y recibos | Informe, diagnóstico previo, inventario original, paquetes de entrada, logs de pruebas base, registro de cambios y comprobaciones estructurales/figuras/Git | A18 y conservación general |

El índice contiene 26 afirmaciones, 700 artefactos del ámbito científico/documental y diez relaciones de generador. Se mantienen las 16 entradas originales del linaje de E00 y se añaden enlaces derivados hacia las afirmaciones posteriores. Hay 226 artefactos con enlace directo a alguna afirmación y 474 sin ese enlace directo; estos últimos pueden tener relaciones con etapas, campañas o generadores. No se presenta una asociación por carpeta como prueba de una conclusión. El índice distingue categorías de enlace, conserva la procedencia del enlace y declara expresamente que un hash del snapshot actual no es un recibo del código usado históricamente.

La arquitectura objetivo ya está aplicada en su parte mínima: las mismas carpetas y rutas científicas, una entrada clara, un mapa de responsabilidades y verificaciones compatibles. No se crean carpetas vacías para modelos/dispositivos/experimentos futuros ni un nuevo registro manual de verdad científica. La ampliación de identificadores y recibos se reserva para próximas campañas, antes de una migración de las antiguas.

## 14. Mapa de edición, conservación y migración

**Movimientos: cero. Renombrados: cero. Eliminaciones de archivos originales: cero.** Cada ruta original continúa existiendo. Catorce archivos de entrada reciben una edición compatible, y el manifiesto raíz se regenera como decimoquinta modificación. Antes de editar se guardó una copia exacta de los quince. La siguiente tabla es un mapa de copias históricas, no una redirección que obligue a cambiar las rutas científicas.

| Ruta original, que continúa vigente | Copia histórica exacta anterior a la edición | Motivo de la edición |
|---|---|---|
| LEEME.md | trazabilidad/CP08_arquitectura_entrada/LEEME.md | Entrada única y descubrimiento |
| ESTADO_ACTUAL.md | trazabilidad/CP08_arquitectura_entrada/ESTADO_ACTUAL.md | Vista generada del estado vigente |
| M2_RESULTADO.md | trazabilidad/CP08_arquitectura_entrada/M2_RESULTADO.md | Eliminar sólo duplicación de cabecera de progreso |
| VERSIONES.json | trazabilidad/CP08_arquitectura_entrada/VERSIONES.json | Identidad administrativa y esquema arquitectónico |
| estado_progreso.json | trazabilidad/CP08_arquitectura_entrada/estado_progreso.json | Registrar CP09 sin cambiar etapas ni próximos objetivos científicos |
| ENMIENDAS_HOJA_RUTA.md | trazabilidad/CP08_arquitectura_entrada/ENMIENDAS_HOJA_RUTA.md | Añadir A06; hoja original intacta |
| requirements.txt | trazabilidad/CP08_arquitectura_entrada/requirements.txt | Declarar dependencia utilizada |
| herramientas/checkpoint.py | trazabilidad/CP08_arquitectura_entrada/herramientas/checkpoint.py | Integridad y empaquetado común |
| herramientas/empaquetar.py | trazabilidad/CP08_arquitectura_entrada/herramientas/empaquetar.py | Compatibilidad con el empaquetador común |
| herramientas/verificar_continuidad.py | trazabilidad/CP08_arquitectura_entrada/herramientas/verificar_continuidad.py | Contexto de enlaces y lectura por defecto |
| herramientas/verificar_m2.py | trazabilidad/CP08_arquitectura_entrada/herramientas/verificar_m2.py | Contexto de enlaces históricos |
| herramientas/verificar_preparacion_m2.py | trazabilidad/CP08_arquitectura_entrada/herramientas/verificar_preparacion_m2.py | Puertas de CP04 en CP04 |
| herramientas/continuar_no_radial_adaptativo.py | trazabilidad/CP08_arquitectura_entrada/herramientas/continuar_no_radial_adaptativo.py | Bloqueo por destino; integración sin cambios |
| investigacion/C7_notas_EN_PROGRESO.md | trazabilidad/CP08_arquitectura_entrada/investigacion/C7_notas_EN_PROGRESO.md | Marcar el alcance histórico |
| MANIFIESTO_SHA256.json | trazabilidad/CP08_arquitectura_entrada/MANIFIESTO_SHA256.json | Cobertura e identidad de la nueva entrega |

trazabilidad/arquitectura/cambios_CP09.json enumera altas y ediciones, hashes anteriores, hashes actuales de las ediciones y copias de recuperación. El manifiesto raíz proporciona los hashes finales de todos los archivos entregados; se excluye a sí mismo para evitar autorreferencia. El registro nuevo no sustituye ni reescribe trazabilidad/cambios_archivos.json, que sigue siendo histórico.

Se conservan **647 archivos científicos o vistas originales** —datos, tratado, validacion, graficos, fichas y hoja_ruta_original— con el mismo SHA-256. También se mantienen los **65 archivos históricos originales de trazabilidad**, los dos ZIP fuente y sus hashes. Los **33 objetos de etapa** de estado_progreso.json son idénticos a los de CP08. Las ecuaciones, Θ, protocolos, umbrales, puertas, CSV, NPZ, figuras, fichas, resultados negativos e informes científicos no se alteran.

La regresión reconstruye los **786 archivos de CP08**: usa la ruta actual si conserva su hash y, cuando fue editada, la copia histórica exacta. El CP08 reconstruido pasa su propia verificación. Esta recuperación no depende de conservar las carpetas de trabajo de la auditoría ni de descargar los paquetes de entrada.

## 15. Comprobaciones después de los cambios

Los recibos están en validacion/arquitectura/. Las pruebas base y sus fallos observados permanecen en trazabilidad/arquitectura/. Las comprobaciones se separan de la aceptación científica.

| Comprobación | Resultado y alcance |
|---|---|
| Entorno | Linux, Python 3.12.14; NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8 y threadpoolctl 3.6.0 coinciden con requirements.txt |
| Regresión estructural | 16 controles pasan; 17 invocaciones tienen el código de salida esperado, incluyendo rechazos deliberados. Se ejecutan fuera de la raíz del proyecto y sobre una copia |
| Verificadores de ciencia guardada | Verificación general: 194 comprobaciones; M2: 38; capilaridad: 52; campaña CP03, preparación CP04, no radial y puerta de acceso completan sus diagnósticos esperados |
| Puerta negativa | El verificador no radial conserva REFINAMIENTO_PENDIENTE y los fallos del refinamiento χ; un retorno de ejecución correcto no cambia la aceptación |
| Independencia de ejecución | No se modifican los bytes de entrada por las pruebas; los informes que escriben verificadores se producen sólo en la copia |
| Vistas principales | generar.py es idempotente sobre geometría, fichas, tablas y documento integrado; la vista de continuidad coincide con sus fuentes |
| Figuras de resultados | Cinco generadores se ejecutan dos veces desde datos guardados, sin campañas. Diez SVG difieren en bytes por metadatos/identificadores; su XML coincide al normalizarlos. Se conservan las figuras originales |
| Estados | Se inspeccionan 87 NPZ: 86 legibles y finitos; el único ilegible se conserva por hash como intento fallido, con su JSON negativo. No se admite como estado válido |
| Continuación cerrada | La llamada adaptativa sobre un cálculo terminado reutiliza el resultado incluido sin pasos de integración. Se rechaza otra configuración para el mismo destino |
| Concurrencia | Dos tags que colisionan comparten identidad de bloqueo; un segundo escritor real es rechazado mientras el primero mantiene el lock |
| Integrador | Comparación AST con la copia CP08: cuerpo numérico igual, salvo extracción de la misma expresión de tag a un helper. No se modifican fuerza, ecuaciones, paso, tolerancias ni criterio de parada |
| Seguridad de integridad | Enlace documental actual roto, NPZ fallido alterado, symlink científico externo y temporal científico pendiente son detectados. La excepción histórica no acepta cualquier archivo ilegible |
| Git | Una prueba en repositorio temporal con core.autocrlf=true conserva bytes tras checkout; datos, estados, logs científicos y ZIP fuente no se ignoran. No hay importación ni publicación remota |
| Conservación | 647 archivos científicos/vistas originales y 65 históricos permanecen idénticos; 33 etapas idénticas; CP08 completo recuperable |
| Entrega | ZIP único autosuficiente con estados y hoja original; comprobación de manifiesto/CRC, extracción nueva y segundo empaquetado binariamente idéntico. El recibo externo Comprobacion_CP09.json registra hashes y resultados finales |

La comparación de figuras usa XML sin metadatos y con IDs normalizados, no render píxel a píxel. No se realizó instalación limpia desde Internet ni provisión de otra máquina: se comprobó el entorno instalado y la extracción en una ruta nueva sin cachés heredadas. No se ejecutaron campañas científicas nuevas ni se hizo un avance de integración para certificar reanudación; se verificaron estados, coherencia, transferencias, rechazo de incompatibilidades y reutilización de un cálculo cerrado. Esos límites impiden presentar esta auditoría como reproducción integral de todos los cálculos o validación de la teoría.

## 16. Riesgos que siguen abiertos y lo que no se cambia

1. **Procedencia histórica incompleta.** El nuevo índice ayuda a navegar en ambas direcciones, pero no recupera huellas de código/Θ/entorno que nunca se guardaron. El contrato de recibo futuro de ARQUITECTURA.md debe aplicarse al crear la siguiente ejecución. No reescribir estados antiguos para hacerlos parecer mejor documentados.
2. **Identificadores numéricos redondeados.** El adaptativo queda protegido contra escritores con el mismo destino y contra configuración incompatible. La nomenclatura histórica y otros scripts todavía no son un identificador universal de realización; resolverlo al crear campañas nuevas, con mapa y pruebas antes de trasladar las existentes.
3. **Estado fallido ilegible.** Se conserva, se etiqueta y se excluye del conjunto de estados reanudables; no se recuperan sus arrays. El resultado vigente utiliza otros archivos legibles.
4. **Crecimiento de validacion e historia.** Más campañas y estados harán más costosos los manifiestos, los ZIP y el historial Git. Introducir agrupación por campaña nueva y evaluar artefactos/LFS cuando exista una necesidad real y una recuperación probada.
5. **Política de aceptación codificada y prosa manual.** Se documentan los generadores y su alcance; no se revisan automáticamente conclusiones ni se sustituyen números en capítulos. Al cambiar evidencia científica hay que revisar el evaluador y regenerar las vistas afectadas de forma controlada.
6. **Múltiples modelos, primordiales y dispositivos.** La separación de identidades está preparada documentalmente, pero ampliar el catálogo exigirá revisar supuestos de tamaño fijo y dependencias. No crear una abstracción M3 ficticia ni renumerar P-01…P-24 hoy.
7. **Trabajo concurrente.** El lock de NPZ evita una colisión concreta; no convierte el corpus entero en una base multiusuario transaccional. Trabajar en ramas/copias aisladas, integrar cambios revisados y publicar un checkpoint consistente.
8. **Entorno.** El integrador adaptativo requiere POSIX y las dependencias fijadas. No se promete compatibilidad Windows ni equivalencia numérica con cualquier versión de bibliotecas. El empaquetado/integridad básico sólo necesita Python estándar.

Se posponen la reorganización total, biblioteca instalable, CI remota, nuevas carpetas por cada posible dominio, migración a LFS, cambios de formato y externalización de ZIP fuente. El beneficio presente no compensa el coste y riesgo. Se conservan exactamente las carpetas, fuentes, historia, fallos y puertas detallados en la sección 10.

## 17. Handoff del checkpoint

El archivo Proyecto_Runas_M2_4_2_CP09_ARQUITECTURA.zip contiene una sola carpeta Proyecto_Runas/ con el corpus completo. **No necesita los dos ZIP complementarios CP08 ni la hoja de ruta externa para abrirlo o verificarlo.** Los antecedentes y la recuperación de sus 786 archivos están incluidos.

Entrada de una persona o modelo nuevo: LEEME.md → ESTADO_ACTUAL.md → ARQUITECTURA.md. Para una cuestión científica concreta: evidencia/registro de cálculos → capítulo/configuración correspondiente → resultado y puerta; el índice derivado permite volver desde un resultado hacia sus enlaces. El estado actual muestra los cálculos cerrados que no deben repetirse, estados disponibles y acciones científicas pendientes sin comenzarlas en esta auditoría.

Desde Proyecto_Runas/, comprobar:

```bash
python herramientas/checkpoint.py --verificar
python herramientas/verificar_continuidad.py --solo-lectura
python herramientas/verificar_entorno.py --adaptativo
python herramientas/generar_continuidad.py --comprobar
python herramientas/auditar_arquitectura.py
python herramientas/regresion_estructural.py --salida ../regresion_estructural.json
```

Para instalar las dependencias de referencia en un entorno aislado, usar requirements.txt siguiendo ARQUITECTURA.md. Para generar el siguiente checkpoint después de trabajo autorizado, actualizar las vistas de continuidad, ejecutar la regresión en copia y utilizar checkpoint.py --salida con un destino fuera del proyecto. empaquetar.py conserva compatibilidad y usa el mismo proceso. Los ZIP complementarios siguen siendo una opción del empaquetador si vuelven a ser útiles por tamaño.

La decisión científica que permanece vigente es REFINAMIENTO_PENDIENTE. CP09 mejora la continuidad y su comprobación; no constituye una nueva solución, una nueva primordial aceptada ni un dispositivo demostrado.
