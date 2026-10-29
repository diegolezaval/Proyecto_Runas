# Rúnica: panorama global, límites y prioridades de continuación

Revisión del 29 de octubre de 2026. Documento de orientación y análisis; no sustituye protocolos, evidencia reproducible, puertas ni registros científicos. No declara una etapa nueva completada.

## 1. Diagnóstico general

Rúnica es un programa de construcción de una física para un mundo ficticio y de una ingeniería que debe derivarse de esa física. Su objetivo es que las runas puedan utilizarse de forma sencilla dentro del mundo, mientras su funcionamiento interno tiene estados, recursos, preparación, límites y causas explícitas.

El proyecto ya tiene un núcleo matemático, una tradición documental, geometrías reproducibles, campañas numéricas, resultados negativos y una hoja de ruta con dependencias. El avance más sólido está en la definición del sector escalar común y en preguntas delimitadas sobre sus soluciones. La cadena que convierte ese sector en dispositivos sigue abierta. El registro no acepta ninguna de las 24 funciones como dispositivo completamente derivado.

La prioridad inmediata es consolidar la continuidad y proseguir el ensayo P3 desde su transporte íntegro de τ11,2. La finalidad de esa tarea es resolver una dificultad numérica que bloquea evidencia de estabilidad; no constituye por sí misma la creación de una primordial. A medio plazo hay que volver a conectar ese trabajo con preparación, acceso, receptor y ciclo, para evitar que el programa se reduzca indefinidamente a una sucesión de correcciones del mismo ensayo.

## 2. Alcance real de esta revisión

Se inventariaron los árboles completos, sin truncación, de estas referencias:

| Línea | Referencia examinada | Archivos del árbol | Tamaño lógico de sus archivos |
| --- | --- | ---: | ---: |
| Base aceptada `main` | `90e8fcffbba65629a1628f435d3c3240832fe9c4` | 1048 | 135097606 bytes |
| Investigación P3 | `9f7baa9cb80d8dcb0878110306d4fac25e1ad2fd` | 2552 | 412864800 bytes |
| Continuación histórica anterior | `3ed272c1c567c39b357ac76b366f66c6ad9c1fa0` | 2159 | 323730162 bytes |

Estos tamaños no son el tamaño físico del repositorio Git ni incluyen toda su historia y Releases. Los árboles comparten objetos y no deben sumarse para estimar almacenamiento real. Las cifras corresponden a esas referencias, anteriores a incorporar este informe.

Se recopilaron y cotejaron 317 archivos de texto, 3240024 bytes. Sus identidades Git coinciden con los árboles de origen. La selección incluye los 31 capítulos del tratado, las 24 fichas, los planes y estados estructurados, los informes de la base, los informes posteriores CP12, las herramientas de la base y las variantes relevantes de P3. Se analizaron sintácticamente 80 archivos Python de `herramientas/` entre ambas líneas: 71 en la base aceptada y nueve variantes o incorporaciones de P3; no hubo errores de sintaxis. Las copias históricas capturadas no se cuentan como herramientas actuales independientes.

Se revisaron el contenido y las dependencias del programa, sus afirmaciones centrales, los contratos del catálogo y las decisiones numéricas. La revisión no consiste en certificar línea a línea cada prueba matemática histórica, volver a ejecutar todas las campañas ni validar de nuevo todos los binarios del repositorio. No se ejecutó evolución científica. Los [controles de lectura](../trazabilidad/panorama_20261029/COMPROBACIONES.json) y el [índice de fuentes consultadas](../trazabilidad/panorama_20261029/FUENTES_CONSULTADAS.json) permiten distinguir lo comprobado de lo no repetido.

## 3. Qué intenta construir el proyecto

El corpus distingue runodinámica, runografía e ingeniería rúnica. La primera define campos y leyes; la segunda define escritura, geometría y composición; la tercera necesita demostrar dispositivos y operaciones. La interfaz propuesta permite preparar o recuperar una Semilla, trazar o llamar una receta, identificar una referencia accesible, elegir una consigna y activar. La complejidad se aloja en la instalación preparada.

La cadena de desarrollo es teoría → soluciones → modos y estabilidad → preparación → coeficientes y contactos → componentes → dispositivo → integración → operación. Los ejemplos de luz, calor, movimiento, separación, química, reparación o fabricación son objetivos y contratos en distintos grados de desarrollo. No se convierten en capacidades demostradas porque tengan una ficha o un balance dimensional correcto.

La civilización propuesta utiliza energía, carga, materia e información disponibles. La captación solar, reservas, redes y recuperación explican la escala pretendida. No se plantea una cuota universal de energía asociada al cuerpo del operador. El principio de información física tampoco permite obtener detalles ausentes mediante una plantilla genérica.

Una consecuencia de diseño importante es que el campo no reconoce automáticamente un símbolo por su nombre. Una inscripción debe preparar una configuración o imponer una interacción física. El puente entre la geometría del trazo y la solución material/campo que la sostiene sigue siendo parte del trabajo pendiente.

Fuentes: [tratado conceptual](../tratado/01_tratado.md), [directrices de desarrollo](../DIRECTRICES_DESARROLLO.md) y [contratos operacionales](../tratado/03_especificacion_operacional.md).

## 4. Núcleo físico: qué es M2

M2 utiliza un campo complejo Φ y un mediador real χ. En el sector escalar clásico aislado:

\[
\mathcal L_s=-|\partial\Phi|^2-\frac12(\partial\chi)^2-V,
\qquad s=|\Phi|^2,
\]

\[
V=m^2s+\lambda_0s^2+\frac12M^2\chi^2+g\chi s+\frac12h\chi^2s.
\]

Las cinco coordenadas fundamentales son Θs=(m,M,λ₀,g,h). La combinación λ=g²/(2M²)−λ₀ es derivada. La frecuencia de un estado, su carga, geometría, malla y tolerancias no son nuevas constantes fundamentales.

El benchmark fija m=1, M=100, λ₀=0,099, g≈44,72135955 y h=0,1 en sus unidades declaradas. Se usan c=ℏ=1 y signatura −+++. Las fuentes vigentes de convenciones son el capítulo 23 y `datos/convenciones.json`; los capítulos antiguos deben leerse junto a sus correcciones.

El sector admite energía y carga U(1) conservadas, y el corpus presenta argumentos de coercividad, vacío estable, existencia global de Cauchy y causalidad bajo hipótesis explícitas. Estas afirmaciones no equivalen a estabilidad de cualquier configuración ni a un dispositivo realizable.

Los portales hacia materia y electromagnetismo están definidos como posibilidades comunes, pero el benchmark numérico usa a=b=0. En ese benchmark no está demostrada conversión rúnica directa desde luz o materia. Una ampliación interactuante necesita parámetros y dinámica compartidos, no un acoplamiento elegido para cada función.

Fuentes: [M2 común](../tratado/13_M2_comun_y_teoremas.md), [convenciones](../tratado/23_convenciones_y_espacio_fundamental.md), [Θ](../datos/theta_comun.json).

## 5. Resultados que merece la pena conservar y reutilizar

### Sector común y soluciones

La reproducción E00 y la formulación E01 están cerradas dentro de su alcance declarado. Hay soluciones cargadas de dos campos, perfiles refinados, energías y cargas contrastadas, Hessianos restringidos y análisis modal. La rama de Reserva incluye 23 soluciones y controles negativos. Las identidades angulares permiten razonar sobre todos los índices angulares de determinados estados exactos, con hipótesis más fuertes que inspeccionar unas raíces de una matriz numérica.

Existe una conexión micro→macro delimitada: una interfaz de ambos campos, su tensión y aproximaciones capilares contrastadas para gotas y tubos. Su valor científico está en derivar propiedades comunes y cuantificar dónde dejan de funcionar las aproximaciones. No sustituye un dispositivo completo.

### Preparación condicionada

La preparación radial CP04 conserva un ensayo largo desde un paquete gaussiano ya cargado. En el caso fino se retiene aproximadamente 90,132 % de la carga del núcleo y la desviación tardía del perfil es aproximadamente 1,124 %. Es evidencia de asentamiento radial condicionado, no una Semilla que se origine desde recursos ordinarios ni una prueba de estabilidad 3D. No hay motivo para repetir esa preparación al comenzar un chat nuevo.

### Acceso a Reserva

El capítulo 29 desarrolla dispersión lineal entre bandas con flujo de energía y carga. Las nueve frecuencias ensayadas incluyen una ganancia energética máxima muestreada de aproximadamente 0,157 % en Ω=2,3. La ganancia no es una eficiencia de un ciclo ni un máximo global. La onda incidente es un recurso ya preparado; el cálculo con fondo fijo no demuestra su retroacción finita, la recepción o la recarga.

Esta ruta hace razonable considerar Reserva como candidata al primer dispositivo numérico completo una vez resueltas sus dependencias. Es una recomendación de prioridad, no una aceptación nueva ni una garantía de éxito.

Fuentes: capítulos [14](../tratado/14_espectro_y_dinamica_M2.md), [20](../tratado/20_interfaz_y_limite_capilar.md), [25](../tratado/25_carta_validez_y_rama_reserva.md), [26](../tratado/26_preparacion_radial_condicionada.md) y [29](../tratado/29_acceso_lineal_a_reserva.md).

## 6. Resultados negativos que delimitan el diseño

1. **Canal libre:** el Q-tubo positivo ensayado tiene una banda de inestabilidad longitudinal. La corriente axial uniforme y ciertas clases con arrollamiento o periodicidad no eliminan el problema bajo sus hipótesis. No se debe volver a explorar la misma clase con otro nombre.
2. **Cadenas estacionarias:** los resultados condicionados de los capítulos 27 y 30 excluyen determinadas cadenas finitas localizadas sin nodos. Una fase espacial suave no las rescata por sí sola. Nodos, dinámica, soportes o fuentes cambian las hipótesis, pero necesitan su propio análisis.
3. **Memoria por fase global:** dos fases U(1) de un estado aislado no tienen barrera energética entre ellas. Ese esquema no demuestra retención digital. Otra codificación debe resolver sus estados, lectura, escritura y ruido.
4. **Semilla desde cero clásico:** una modulación multiplicativa no hace abandonar el cero clásico exacto. Un bombeo neutro U(1) no crea carga neta aislada. Fuentes cargadas, pares o fluctuaciones requieren modelos distintos y balances explícitos.
5. **Reserva:** energía total ligada y energía útil recuperable son magnitudes diferentes. Liberar toda la carga como ondas libres puede exigir trabajo adicional; el receptor forma parte del problema.
6. **Materia y luz:** el benchmark desacoplado no demuestra captación solar, emisión, fuerza material o química rúnica. La termodinámica y las matrices de grafos no suplen el contacto físico ausente.

Las exclusiones son útiles porque evitan gastar cálculo en familias ya descartadas. No demuestran agotamiento de M2 ni justifican introducir M3 por una discrepancia numérica.

Fuentes: capítulos [16](../tratado/16_pruebas_de_dispositivo.md), [18](../tratado/18_guia_y_terminal_desde_M2.md), [21](../tratado/21_corriente_clasificacion_y_cierre.md), [24](../tratado/24_exclusiones_tubulares_y_busqueda.md), [27](../tratado/27_simetria_estacionaria_y_cadenas_finitas.md) y [30](../tratado/30_fase_estacionaria_sin_nodos.md).

## 7. Las 33 etapas: cuánto está cerrado

Los estados generales coinciden entre `main` y P3: **3 COMPLETADAS, 6 PARCIALES y 24 BLOQUEADAS**. Las completadas son E00, E01 y C0. Las parciales son E02, E03, E04, C7, RES0 y RES1.

No es correcto convertir 3/33 en un porcentaje de trabajo terminado. Las etapas tienen costes, ramificaciones y condiciones de cierre muy diferentes; una campaña puede producir mucho conocimiento sin completar una etapa general.

| Frente parcial | Qué existe | Qué impide su cierre general |
| --- | --- | --- |
| E02: validez | Dominios condicionados, sensibilidades y límites de aproximaciones | Región robusta conjunta, errores de reducciones, tiempo, amplitud y límites de la teoría |
| E03: soluciones y estabilidad | Perfiles, identidades, espectros y evoluciones finitas | Convergencia suficiente y cobertura de perturbaciones y estabilidad necesaria para la función |
| E04: preparación | Asentamiento radial condicionado | Fuente de los recursos iniciales, región de preparación y apagado |
| C7: estructuras compuestas | Exclusiones analíticas condicionadas | Candidato superviviente con existencia, estabilidad y encaminamiento demostrados |
| RES0: rama y energía accesible | Rama, balances y acceso lineal parcial | Estabilidad útil, dominio robusto y accesibilidad finita |
| RES1: preparar Reserva | Estado cargado y preparación radial | Procedencia de la carga y energía, estabilidad y protocolo reproducible completo |

E08 es el hito de un primer dispositivo numérico de extremo a extremo. Las etapas posteriores de repertorio, redes, fabricación, operación y manuales dependen de dispositivos concretos. No se desbloquean por ampliar documentación. El apéndice A conserva el mapa completo de las 33 etapas.

## 8. Las 24 primordiales

El catálogo distingue geometría, contrato y realización. Tiene 24 funciones evaluadas y cero aceptaciones de dispositivo completo. Las casillas falsas significan falta de demostración; los negativos específicos deben leerse aparte.

| Familia | Funciones | Dependencia principal compartida |
| --- | --- | --- |
| Energía y térmica | Semilla, Captador solar, Reserva, Luz, Intercambio térmico, Polarización | Preparación, fuente/receptor y conversión materia/EM con balances y ruido |
| Transporte | Canal, Distribuidor, Retardo, Puente | Guía física estable, terminales, dispersión, pérdidas y diafonía |
| Información y control | Compuerta, Sensor, Selector, Memoria, Comparador, Reloj, Secuenciador | Estados distinguibles, lectura/escritura, transducción, referencia y error |
| Mecánica | Anclaje, Recinto, Impulso, Vibración | Tensor de tensiones, reacción, contacto material y límites de esfuerzo |
| Materia y química | Separación, Reacción, Ensamblaje | Hamiltoniano material común, selectividad, transporte, cinética y errores |

El número 24 es un catálogo revisable. Fusionar funciones exige redundancia física demostrada; añadir una función exige un expediente. P-22, P-23 y P-24 ya están incluidas en la evaluación y no deben volver a excluirse por una instrucción histórica.

Las geometrías racionales, sus puertos y SVG están bien especificados como objetos de escritura y composición. El paso pendiente es hacer que esa configuración corresponda a un estado y a interacciones derivados de la teoría. La exactitud del dibujo no certifica el estado físico.

Fuente: [aceptación del catálogo](../tratado/17_aceptacion_catalogo.md) y [registro estructurado](../datos/aceptacion_m2.json). El apéndice B enumera las 24 funciones y sus primeras obstrucciones.

## 9. Qué significa la secuencia CP01…CP12

| Entrega | Aporte principal | Alcance que debe conservarse |
| --- | --- | --- |
| CP01 | Reproducción independiente | Cierra E00; no acepta dispositivos |
| CP02 | Convenciones y cinco coordenadas | Cierra E01 en el sector declarado |
| CP03 | Exclusiones C0, validez y rama | Cierra C0; E02/E03/RES0 siguen parciales |
| CP04 | Preparación radial larga | Preparación condicionada; E04/RES1 parciales |
| CP05 | Simetría y cadenas finitas | Descarta una subclase; C7 sigue parcial |
| CP06 | Evolución no radial y controles | Resultados finitos y problemas de resolución |
| CP07 | Acceso lineal y refinamiento | Subpreguntas resueltas; ciclo y estabilidad general abiertos |
| CP08 | Refinamiento no radial | Persiste una discrepancia de χ; no hay cierre de etapa |
| CP09 | Auditoría de arquitectura | Mejora continuidad y procedencia; no añade física |
| CP10 | Discriminación espacio/tiempo | Control temporal positivo, acuerdo espacial insuficiente |
| CP11 | Diagnóstico radial de χ | Último checkpoint aceptado; causa acoplada aún no separable con las historias antiguas |
| CP12 | Presupuesto causal y ensayos de corrección | Investigación abierta; incluye negativos y el actual P3 |

Un número de checkpoint no es un nivel del modelo fundamental. M2 no se convierte en M3 porque exista CP12 o una versión `4.2.0-dev11` del proyecto.

## 10. Problema científico que mantiene abierto CP12

El obstáculo inmediato no es una deriva grande de energía o carga: es la comparación espacial de χ, incluyendo velocidades, entre resoluciones. Unos balances excelentes pueden coexistir con una fase espacial insuficientemente convergente.

El CP12 original conservó la evolución hasta τ160 y reprodujo CP10. La discrepancia espacial de fases χ fue **5,126390964 %**, por encima del límite original del 2 %. El presupuesto pasivo indicó suficiencia del canal operador χ acoplado en tres ventanas, condicionada a las historias guardadas; no certificó una causa física única.

El primer ensayo K4 de los tres campos falló tempranamente la puerta de energía FV original. La buena conservación de su propio Hamiltoniano no compensó ese fallo. El posterior ensayo mixto Φ-FV/χ-K4 —P2— llegó a τ80 y falló la puerta espacial con **2,311907990946478 %**. Las otras cuatro métricas pasaron; la última frontera P2 con las cinco positivas es τ72. P2 quedó suspendido y no se reanuda para saltar el negativo.

P3 conserva M2 y la evolución de Φ-FV, y cambia el operador discreto de χ a:

\[
A_3=A_2+\frac{\Delta r^2}{12}A_2^2+\frac{\Delta r^4}{90}A_2^3.
\]

Los coeficientes están fijados por la derivación, no por un ajuste al resultado. La composición mantiene una forma positiva del operador bajo sus hipótesis. Su mejora de dispersión interior plana no convierte el problema radial global en un método de orden seis: persiste un término geométrico de orden dos y la preparación CP04 tiene regularidad C1 relevante para las colas de frecuencia.

Por tanto, ni el paso de F0…F5 ni un par de mallas positivo permiten afirmar convergencia del continuo. También deben preservarse las puertas de energía consistente y FV original por separado.

Fuentes: informes [CP12 original](RESULTADO_CP12_TAU160_20261015.md), [K4](RESULTADO_NEGATIVO_K4_20261015.md), [negativo P2](NEGATIVO_ESPACIAL_MIXTO_TAU80_CP12_20261018.md) y [derivación P3](../checkpoints/CP12/p3_20261018/DERIVACION.md).

## 11. Estado operativo actual: τ11,2 recuperable

Al cerrar la recuperación anterior, la cápsula íntegra de τ11,2 quedó adjuntada a GitHub y su descarga independiente pasó los auditores originales. La última frontera completa aprobada de P3 sigue siendo τ8. τ11,2 es un transporte interno entre fronteras.

| Identidad | Valor |
| --- | --- |
| Rama experimental | `ciencia/cp12-residuo-p3-20261018` |
| Release | `respaldo-cp12-p3-20261027`, experimental |
| Adjunto vigente | `688783601` |
| Archivo | `CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_TRANSPORTE_TAU_000112_TRANSITO_INTENTO02_20261028.zip` |
| Tamaño | 229880902 bytes |
| SHA256 del ZIP | `b0e2b2c1320358a41d2f8910e28fc17e65ec330e27ce8bdcf05e59e93f0fae8d` |
| SHA256 del transporte | `bc129cff71c7558cd0298873fdc816da14e01fdcb4728235b33666a1ecfcf3ac` |
| Contenido | 293 cargas más manifiesto |
| Auditorías de recuperación | 30 de frontera τ8 + 14 de transporte τ11,2; cero construcciones o pasos DOP853 |
| Repetición adicional τ9,6→τ11,2 | Terminada; autorización de un solo uso consumida |
| Próxima frontera completa | τ16, todavía no ejecutada |

Los tiempos internos de los dos solucionadores están ligeramente después de 11,2 por el muestreo denso original; su límite interno sigue siendo 16. Un reinicio desde las matrices observadas y un DOP853 nuevo no equivale a restaurar ese estado interno. Hay que conservar su memoria, observadores, alias y contadores mediante el transporte original.

La desaparición de archivos temporales tras la interrupción no destruyó esta cápsula. El informe físico previo al guardado está dentro del ZIP; algunos documentos administrativos externos se reconstruyeron honestamente desde la cápsula. Esa procedencia está registrada. La igualdad de escalares con una repetición anterior no demuestra identidad binaria con sus bytes perdidos.

Referencias vigentes: [recuperación actual](../RECUPERACION_CP12_ACTUAL.md), [registro canónico](../checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json), [guía de la cápsula](../checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/README.md) y [aceptación pública](../checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/github/ACEPTACION.json).

## 12. Organización y software: fortalezas comprobadas

El repositorio separa fuentes de teoría, parámetros, campañas, evidencia, trazabilidad y vistas. Conserva datos crudos y negativos; usa protocolos previos, hashes, recibos y restricciones de escritor único. Las dependencias NumPy, SciPy, Matplotlib y threadpoolctl están fijadas por versión en `requirements.txt`. Hay verificadores de resultados, regresión estructural aislada y herramientas de empaquetado.

La geometría procede de JSON racional y las fichas, SVG y tratado integrado tienen generadores. Las cifras de una campaña se leen de sus resultados y no deberían copiarse manualmente entre documentos. Esa separación es una base apropiada para una investigación que debe poder retomarse en otro chat.

Los 80 archivos Python analizados sintácticamente no presentaron errores de sintaxis. Eso no prueba corrección matemática, cobertura de pruebas ni que sea seguro ejecutar cualquier script como comando de diagnóstico. `reproducir.py` ejecuta por defecto una reproducción histórica amplia y escribe resultados; no debe utilizarse automáticamente como primera acción. Algunos módulos antiguos también ejecutan trabajo al ser importados. La revisión debe leerlos estáticamente y ejecutar verificadores en copias aisladas según su alcance.

La reproducción exacta del transporte vigente exige además detalles que un `requirements.txt` no expresa: implementación de DOP853, arquitectura BLAS, compilador, banderas y orden del cálculo. Una reproducción científica entre entornos y una continuación exacta del integrador tienen contratos distintos.

Fuentes: [arquitectura](../ARQUITECTURA.md), [protocolo de ejecución](../DIRECTRICES_EJECUCION.txt), [modelo común](../herramientas/modelo_m2.py), [procedencia](../herramientas/ejecutar_con_procedencia.py) y [regresión estructural](../herramientas/regresion_estructural.py).

## 13. Deuda concreta de continuidad encontrada

### 13.1. Instrucciones activas desactualizadas

El `estado_progreso.json` de P3 mantiene `next_actions` y `next_calculation` sobre un piloto 0→8 en curso y un transporte 0,4. El registro canónico y la aceptación pública ya acreditan τ11,2. Las etapas generales siguen correctamente en CP11/abiertas, pero esos campos de actividad pueden inducir una repetición indebida.

Hay que sincronizar la continuidad operativa desde la evidencia reciente, conservar la historia antigua y regenerar sus vistas. No corresponde marcar E03 o CP12 como completadas para eliminar la discrepancia documental.

### 13.2. Manifiesto general pendiente de reconciliación

En el árbol P3 de referencia, el manifiesto raíz declara 1384 archivos y hay **1167 rutas versionadas adicionales** fuera de su cobertura. Entre los 42 archivos de texto disponibles en esta revisión que sí tienen entrada en ese manifiesto, tres hashes ya no coinciden: `datos/registro_calculos.json`, `estado_progreso.json` y `herramientas/generar_continuidad.py`.

La comparación de cobertura y esos tres hashes es directa. No se ejecutó el verificador completo del árbol ni se descargaron todos sus binarios. El manifiesto raíz no puede presentarse como certificado íntegro del árbol P3 actual. Esto no invalida las cápsulas científicas con manifiestos y recuperaciones propios; sí obliga a delimitar o reconstruir una entrega global verificable.

El arreglo debe preservar el manifiesto anterior y su contexto, reunir el árbol exacto y generar una nueva identidad de entrega. No se deben cambiar a mano hashes para ocultar discrepancias ni tocar fuentes científicas congeladas para hacer pasar una auditoría administrativa. Las incorporaciones documentales de este análisis también deberán entrar en el inventario de la futura entrega global.

### 13.3. Portadas y documentos históricos

La guía de `main`, fechada el 28 de octubre, todavía explica la recuperación de τ9,6 y la pérdida anterior de τ11,2. `MIGRACION_GITHUB.md` describe una preparación histórica anterior a publicar GitHub. Esos textos se conservan como antecedentes; no deben tomarse literalmente como estado de conexión o conservación actual.

Un enlace relativo de la recuperación P3 apuntaba a `GUIA_DEL_PROYECTO.md`, que existe en `main` y no en esa rama. La publicación de este informe corrige ese enlace hacia la rama correcta. No se cambian las ecuaciones ni las fuentes numéricas por esa reparación.

### 13.4. Una entrada humana con autoridad delimitada

Hay 15 ramas y muchos informes legítimos de recuperación. Conviene mantener un mapa claro: base aceptada, ensayo activo, antecedentes suspendidos y respaldos. Las ramas antiguas no se borran por estar inactivas; tampoco se ejecutan como alternativas simultáneas. El índice debe distinguir afirmación científica, estado operativo y artefacto recuperable.

## 14. Qué significa 116/308 y qué no significa

El contador actual **116/308** corresponde a subpartes de 750000 bytes de una prueba administrativa de conservación: `CP12_P3_CAPACIDAD_20261020B.zip`, de 230993842 bytes. Se publicaron las partes 0–115, 87000000 bytes, y el expediente conserva `INCOMPLETO` y recuperación remota completa no verificada.

Ese archivo empaquetaba el ZIP de τ9,6, un inventario y relleno determinista de capacidad. No es un censo de 308 documentos distintos de la Biblioteca original. No puede utilizarse para afirmar que se migró el 37,7 % del proyecto ni que faltan exactamente 192 documentos originales.

El proyecto ya dispone de una ruta posterior comprobada para conservar los ZIP completos en Releases y ha recuperado desde allí τ11,2. Por eso no es necesario terminar aquel transporte abandonado para desbloquear P3. Puede documentarse como una ruta histórica sustituida funcionalmente, manteniendo su estado incompleto y sus bytes. No debe declararse completo ni borrarse sin una decisión justificada.

Para establecer si falta material de la Biblioteca original de la otra cuenta se necesita un inventario real de nombres, identidades, contenidos y ubicación. Los tres ZIP originales recuperados cubren antecedentes concretos y el nuevo τ11,2 permite reanudar el ensayo; eso no prueba que toda la antigua Biblioteca esté trasladada.

La Release experimental examinada contiene ocho adjuntos por aproximadamente 1,47 GB, incluyendo originales, tres pruebas de capacidad, el nuevo transporte y hashes. Es almacenamiento fuera del árbol Git. Los cuatro archivos temporales generados recientemente para el tránsito suman 922584281 bytes; antes de cualquier limpieza hay que comparar sus identidades y sus copias finales verificadas. Esta revisión no elimina archivos.

Fuentes: [estado parcial histórico](../checkpoints/CP12/p3_20261018/conservacion_git_20261022/capacidad/ESTADO.json), [contexto de capacidad](../checkpoints/CP12/p3_20261018/conservacion_git_20261022/ESTADO_VERIFICADO.md) y [Releases](https://github.com/diegolezaval/Proyecto_Runas/releases).

## 15. Riesgos de interpretación que deben evitarse

| Dato real | Inferencia que no está justificada |
| --- | --- |
| Energía y carga muy bien conservadas | La fase, convergencia espacial y función del dispositivo son correctas |
| `passed=true` en un auditor de transporte | P3 quedó validado o CP12 cerrado |
| Dos mallas concuerdan bajo un umbral | Orden asintótico o continuo certificado |
| Mejora interior plana de P3 | Orden radial global seis |
| Espectro de algunas perturbaciones | Estabilidad orbital y operación indefinida |
| Geometría exacta de una ficha | Estado físico que la realiza |
| Energía total de una Q-ball | Energía útil extraíble con un receptor |
| Respuesta lineal con ganancia | Ciclo finito con eficiencia y recarga demostradas |
| Valores R1 | Datos predichos o medidos |
| Modelo clásico bien planteado | Teoría cuántica/material completa |
| Una implementación rechazada | Imposibilidad de la función en todo M2 |

La escala SI usada es ilustrativa. Por ejemplo, τ es tiempo adimensional y τ160 no demuestra retención cotidiana prolongada. Los tiempos internos del ensayo y las capacidades deseadas para la civilización no deben mezclarse.

## 16. Plan inmediato recomendado

**P0. Consolidar el relevo.** Leer este informe y los registros actuales, verificar las ramas, reconciliar las instrucciones operativas antiguas y delimitar el manifiesto global. La base aceptada se conserva. Una auditoría administrativa no recalcula física.

**P1. Recuperar el estado de τ11,2 en el entorno del chat ejecutor.** Descargar el adjunto existente, comprobar su tamaño y SHA256, cobertura de 293 cargas, fuentes y configuración, y pasar los auditores originales sin construcciones o pasos DOP853. Verificar los procesos propios y la ruta de conservación antes de iniciar otro trabajador. No repetir el tramo τ9,6→τ11,2.

**P2. Preparar la continuación hacia τ16.** Usar el estado interno exacto, el límite interno original 16 y los observadores originales. El lanzador de la repetición consumida no sirve como un permiso reutilizable. Cualquier adaptador administrativo nuevo se registra y prueba sin cambiar las fuentes científicas capturadas. La ruta de conservación debe funcionar en el proceso y entorno que realmente vayan a producir los siguientes estados.

**P3. Aplicar las puertas de τ16.** Guardar, recuperar y auditar la frontera completa, y evaluar las cinco métricas espaciales originales sobre la extracción independiente, con límites sin redondear. Si una falla, conservar el negativo y suspender ese candidato. No avanzar hasta τ24 por tener un ZIP bien formado o balances positivos.

**P4. Continuar sólo la rama que siga habilitada.** Si todas las puertas pasan, proseguir por fronteras de ocho unidades hacia el horizonte condicionado τ160 y con transportes permanentes según el protocolo. Cada frontera exige recuperación y decisiones explícitas. No lanzar P4 u otra corrección automáticamente ante un negativo.

## 17. Qué faltaría después de un P3 positivo

Pasar la pareja espacial hasta τ160 sería necesario y valioso, pero no el cierre de CP12. El protocolo exige comparar el presupuesto causal en sus tres ventanas, con reducción de norma del canal operador χ acoplado de al menos 50 % respecto del original en cada ventana, además del resto de puertas.

Después hacen falta pruebas justificadas y prerregistradas de tercera malla y orden observado, referencia independiente, sensibilidad a interpolación, truncamiento angular y caja, estabilidad temporal y robustez. La regularidad C1 de la preparación y el residuo geométrico radial impiden fijar de antemano un orden alto para conseguir aceptación. No se suavizan los datos ni se gira χ para mejorar la comparación.

Si P3 falla, su diagnóstico debe distinguir defecto del esquema, problema de referencia/proyección, preparación, observador o limitación de hipótesis, según los datos. Un nuevo candidato necesita una pregunta que cambie algo informativo. La salida no puede ser una escalera automática de operadores de orden cada vez mayor.

Fuente: [prerregistro original del piloto](../checkpoints/CP12/p3_20261018/PRERREGISTRO_PILOTO.md).

## 18. Programa posterior: volver al primer dispositivo

| Prioridad | Resultado buscado | Condición que lo hace útil |
| --- | --- | --- |
| Validez y estabilidad | Dominio de estados suficientemente respaldado | Permite usar la solución sin presentar un fallo numérico como física |
| Preparación | Producir el estado desde recursos trazables y apagarlo | Evita asumir como entrada el dispositivo ya hecho |
| Reserva finita | Paquete incidente, retroacción, receptor y balance común | Conecta el acceso lineal con energía recuperable |
| Contactos comunes | Intercambio definido dentro de M2 y, cuando proceda, con materia/EM | Debe explicar más de una función y contabilizar recursos |
| Ciclo | Carga, retención, descarga, recepción, recarga y degradación | Primer dispositivo numérico completo con contrato explícito |
| Canal superviviente | Familia fuera de las exclusiones, extremos y señal/potencia | Investigación delimitada; no volver al tubo positivo ya descartado |
| Repertorio | Nuevas funciones basadas en recursos admitidos | Sin una teoría distinta ni constantes ad hoc por primordial |
| Integración | Redes, control y operación conjunta | Márgenes del conjunto y destinos de energía, carga e información |
| Manuales y formación | Enseñar lo realmente establecido | Separar teoría, ingeniería aceptada y propuestas |

Reserva parece una candidata razonable a la primera demostración porque ya tiene una rama localizada, preparación condicionada y acceso lineal. El objetivo inicial puede ser un contrato útil y modesto, revisado explícitamente, sin exigir por conveniencia la cifra R1 histórica. Esto no permite reducir las puertas numéricas originales de una campaña en curso.

Canal sigue siendo una prioridad declarada del plan, pero conviene investigar sólo ramas que cambien hipótesis: estados con nodos, configuraciones dinámicas, contactos o soporte físico explícito, entre otras posibilidades delimitadas. Cambiar la forma dibujada sin resolver el estado no aporta una nueva realización.

M3 permanece como expediente condicional. Se justifica por una carencia fundamental común bien documentada y una extensión con dinámica, límites y predicciones compartidas. No lo justifica por sí solo una mala convergencia de χ, otra geometría, un controlador o el deseo de conservar las 24 funciones.

## 19. Cómo usar dos chats sin volver a perder continuidad

El chat ejecutor debe ser el único escritor de la campaña activa. Este chat puede actuar como consejero: revisar derivaciones, interpretar las puertas, contrastar el próximo objetivo con el plan y auditar entregas ya publicadas. Los chats no comparten automáticamente su contexto ni observan en directo lo que hace el otro.

El repositorio es la memoria común. Al cerrar cada entrega, el ejecutor debe dejar un informe con pregunta, protocolo, resultado positivo o negativo, alcance, puertas, enlaces a artefactos recuperados, commit y siguiente acción. Para pedir consejo basta traer ese enlace, la duda y la decisión propuesta. El consejero puede entonces contrastar la evidencia vigente, sin recibir todo el historial de mensajes.

Conviene que cada informe separe tres estados: científico, operativo y de conservación. «CP11 aceptado / CP12 abierto», «trabajador terminado / objetivo siguiente τ16» y «cápsula τ11,2 recuperada desde GitHub» son hechos distintos. Un único rótulo «completado» pierde esa distinción.

El [texto de relevo](../CONTINUAR_EN_CHAT_NUEVO.md) aplica esta revisión al arranque del nuevo chat. Debe verificarse si hay evidencia posterior antes de ejecutar: este análisis fija el panorama de las referencias indicadas, no congela el futuro.

## 20. Juicio y límites finales

El proyecto tiene un núcleo coherente de objetivos, un modelo común explícito y evidencia científica interna que merece conservarse. Sus resultados negativos han eliminado atajos concretos y su programa identifica dependencias importantes. Eso permite avanzar con un criterio más exigente que acumular fichas o simulaciones.

El cierre pendiente más cercano es una decisión numérica delimitada de P3. El cierre de mayor valor posterior es el primer ciclo de un dispositivo con fuente y receptor. Las demás funciones y la interfaz cotidiana necesitan ese puente físico y operativo. La revisión no permite dar una fecha de finalización ni un porcentaje global defendible.

El objetivo de mundo ficticio sigue siendo válido. No hace falta confundirlo con la comprobación de que estos campos existan en nuestro mundo. Sí hace falta mantener la coherencia interna y no inventar mediciones, fabricación o resultados de campañas para completar etapas.


## Apéndice A. Etapas del programa

Estados generales de las referencias examinadas; el objetivo operativo reciente está en el registro canónico de P3.

| Etapa | Título | Estado | Dependencias registradas |
| --- | --- | --- | --- |
| E00 | Congelar la fuente y establecer una reproducción independiente | COMPLETADA | ZIP4.1 |
| E01 | Fijar la formulación matemática y el espacio fundamental | COMPLETADA | E00 |
| E02 | Determinar dominios de validez, incertidumbre y escalas | PARCIAL | E01 |
| E03 | Consolidar soluciones, espectro completo y dinámica | PARCIAL | E01 |
| E04 | Preparación común, Semilla y apagado | PARCIAL | E03 |
| E05 | Contactos, materia, energía y entorno comunes | BLOQUEADA | E01, E03 |
| E06 | Resolver la decisión física de Canal | BLOQUEADA | E02, E03, C0 |
| E07 | Convertir la Q-ball en Reserva | BLOQUEADA | E02, E03, RES0 |
| E08 | Primera demostración de dispositivo de extremo a extremo | BLOQUEADA | E04, E05, E06 o E07 |
| E09 | Ampliar el repertorio mediante recursos físicos compartidos | BLOQUEADA | E08 |
| E10 | Integración, redes y control | BLOQUEADA | E08, E09 |
| E11 | Identificación, metrología y contraste experimental | BLOQUEADA | E02, E05 para experimentos |
| E12 | Fabricación, tolerancias y mantenimiento | BLOQUEADA | E08, E11 |
| E13 | Operación, interfaz y seguridad | BLOQUEADA | E10, E11, E12 |
| E14 | Consolidar teoría, ingeniería y formación | BLOQUEADA | H.1 |
| C0 | Delimitar el problema antes de gastar simulación | COMPLETADA | E00, E01 |
| C1 | Otras ramas tubulares y perfiles radiales | BLOQUEADA | C0, E03 |
| C2 | Carga temporal, corriente y gradiente axial | BLOQUEADA | C0, C1, E03 |
| C3 | Vorticidad, arrollamiento y momento angular | BLOQUEADA | C0, E03 |
| C4 | Tubos huecos, capas y soporte del mediador existente | BLOQUEADA | C0, C1, E03 |
| C5 | Tubos no uniformes y configuraciones periódicas | BLOQUEADA | C0, E03 |
| C6 | Geometrías finitas, curvas, anillos y superficies | BLOQUEADA | C0, E03, C9 integrado |
| C7 | Estructuras compuestas y confinamiento emergente | PARCIAL | E03, RES0 |
| C8 | Estados dinámicos y control con recursos reales | BLOQUEADA | E03, E04, E05 |
| C9 | Terminación, fuente, receptor y empalmes físicos | BLOQUEADA | candidato C1–C8, E05 |
| C10 | Preparación, potencia, robustez y decisión final | BLOQUEADA | C9, E02, E03, E04, E05 |
| RES0 | Rama estable y energía accesible | PARCIAL | E01, E02, E03 |
| RES1 | Preparar el depósito sin circularidad | PARCIAL | RES0, E04 |
| RES2 | Derivar carga y acceso al estado | BLOQUEADA | RES0, RES1, E05 |
| RES3 | Aislamiento, retención, pérdidas y ruido | BLOQUEADA | RES2, E02, E05 |
| RES4 | Descargar, recuperar y medir el rendimiento neto | BLOQUEADA | RES2, RES3, E05 |
| RES5 | Ciclos repetidos y límites de operación | BLOQUEADA | RES0, RES1, RES2, RES3, RES4 |
| M3 | Expediente de extensión común | BLOQUEADA | B.5, F.1, E01, E02, E05, E11 |

## Apéndice B. Catálogo de funciones

Ninguna está aceptada como dispositivo completo. La columna de obstrucción describe la realización actual; no establece una imposibilidad universal.

| ID | Función | Primera obstrucción | Razón registrada |
| --- | --- | --- | --- |
| P-01 | Semilla | Preparacion | El cero clasico es invariante; el bombeo neutro no crea carga neta aislada. |
| P-02 | Anclaje | Fuerza y referencia | No hay perfil material con retroaccion que derive fuerza, rigidez y reaccion del anclaje. |
| P-03 | Recinto | Frontera y especies | La curva no fija barreras de cada especie, presion soportada ni tasas de fuga. |
| P-04 | Canal | Estabilidad de la guia | El Q-tubo libre de dos campos tiene una banda longitudinal creciente; el extremo fisico no se ha derivado. |
| P-05 | Captador solar | Conversion y fuente | El ciclo de tres niveles usa niveles y tasas no derivados; el benchmark desacoplado no absorbe potencia runica de luz. |
| P-06 | Reserva | Estado, carga y acceso | La Q-ball almacena energia, pero no se ha realizado la geometria de Reserva ni carga/descarga, eficiencia o capacidad R1. |
| P-07 | Compuerta | Control fisico | No se ha obtenido de M2 un estado de compuerta con contraste, trabajo de control y ruido calculados. |
| P-08 | Distribuidor | Guias y uniones | La matriz de grafo presupone modos transversales e impedancias; no hay solucion M2 de la union. |
| P-09 | Sensor | Acoplamiento de medida | Ganancia, retroaccion y correlaciones de ruido no estan determinadas por el trazo. |
| P-10 | Selector | Observable del objetivo | El selector necesita un acoplamiento material que distinga objetivos y cuantifique falsos positivos. |
| P-11 | Memoria | Estados y barrera | La fase U(1) tiene barrera cero; Kerr, disipacion y escritura del ensayo anterior no fueron derivados de esta geometria. |
| P-12 | Comparador | No linealidad y lectura | No se ha derivado el umbral de decision, su transductor ni su distribucion de error. |
| P-13 | Retardo | Dispersion y almacenamiento | El retardo depende de dispersion y resonancias; longitud/v no demuestra ruido, ancho de banda ni perdidas M2. |
| P-14 | Reloj | Oscilacion y referencia | Una frecuencia modal no demuestra un reloj alimentado con estabilidad, arranque y difusion de fase calculados. |
| P-15 | Secuenciador | Estados y transiciones | La maquina de estados operacional no especifica estados microscopicos ni tasas de transicion. |
| P-16 | Puente | Aislamiento espacial | Dos componentes desconectados del grafo no prueban diafonia nula en los campos 3D. |
| P-17 | Luz | Emision electromagnetica | Falta el acoplamiento modal que convierta energia en fotones; b=0 implica conversion directa nula. |
| P-18 | Intercambio térmico | Contactos termicos | No estan definidos los acoplamientos y correlaciones de ambos contactos; se cuantifica el contraste de canales termicos. |
| P-19 | Impulso | Momento y actuador | No hay solucion campo-materia que derive impulso, potencia, reaccion y saturacion. |
| P-20 | Polarización | Respuesta electromagnetica | B escalar uniforme no introduce birrefringencia local; una respuesta anisotropa por geometria exige resolver Maxwell y materia. |
| P-21 | Vibración | Elasticidad y perdida | El modo cuadrupolar calculado no es un actuador material; falta acoplamiento, amortiguamiento y esfuerzo maximo. |
| P-22 | Separación | Selectividad y transporte | Evaluada: faltan Hamiltoniano material, potenciales quimicos de especies y transporte; el benchmark desacoplado no produce separacion runica. |
| P-23 | Reacción | Cinética y balance | Evaluada: faltan superficies de energia, contactos y tasas derivadas de un Hamiltoniano quimico comun. |
| P-24 | Ensamblaje | Transporte y estructura | Evaluada: faltan seleccion de estructura, cinetica y propagacion de errores; depende del mismo contacto material de P-22 y P-23. |

## Apéndice C. Puntos de entrada para el consejero y el ejecutor

- [Relevo completo para un chat nuevo](../CONTINUAR_EN_CHAT_NUEVO.md).
- [Directrices de desarrollo](../DIRECTRICES_DESARROLLO.md) y [ejecución](../DIRECTRICES_EJECUCION.txt).
- [Plan maestro original](../hoja_ruta_original/Guia_tecnica.md) y [contratos de etapas](../hoja_ruta_original/Plan_investigacion.json).
- [Arquitectura y generadores](../ARQUITECTURA.md).
- [Progreso general](../estado_progreso.json), con las discrepancias operativas indicadas en esta revisión.
- [Evidencia del núcleo aceptado](../datos/estado_evidencia.json).
- [Recuperación vigente](../RECUPERACION_CP12_ACTUAL.md) y [registro canónico P3](../checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json).
- [Prerregistro del piloto](../checkpoints/CP12/p3_20261018/PRERREGISTRO_PILOTO.md).
- [Guía de la cápsula τ11,2](../checkpoints/CP12/p3_20261018/retoma_20261028/intento02/ejecucion_controlada/repeticion96_112/README.md).
- [Controles de esta revisión](../trazabilidad/panorama_20261029/COMPROBACIONES.json) e [identidades de sus fuentes](../trazabilidad/panorama_20261029/FUENTES_CONSULTADAS.json).
