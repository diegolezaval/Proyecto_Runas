# Aplicación del criterio al catálogo

## 17.1. Decisión de extensión

Se evalúan las 24 funciones bajo el mismo criterio físico. **Ninguna tiene todavía una realización completa demostrada.** El inventario localiza la primera obstrucción identificada; los capítulos 20 y 21 añaden una interfaz y leyes capilares comunes, y revisan la corriente axial y los recursos compartidos. No se introducen coeficientes propios de una función para obtener su aceptación.

Los valores R1 permanecen como objetivos de diseño revisables; las funciones se someten a la teoría y pueden corregirse, sustituirse o descartarse. Las casillas falsas significan falta de demostración, y los resultados negativos se registran aparte. Ninguna fila habilita un intervalo operativo, umbral de daño, tasa de error o capacidad no calculados. Cero aceptaciones no significa que las ecuaciones prohíban todas las funciones; significa que ninguna satisface la cadena exigida con la evidencia disponible.

## 17.2. Familias y resultado por primordial

### transporte

| Primordial | Primer eslabón sin demostración de dispositivo | Resultado o razón | Evidencia |
|---|---|---|---|
| P-04 Canal | Estabilidad de la guia | El Q-tubo libre de dos campos tiene una banda longitudinal creciente; el extremo fisico no se ha derivado. | 18; 16.1; 20.6; 21.1 |
| P-08 Distribuidor | Guias y uniones | La matriz de grafo presupone modos transversales e impedancias; no hay solucion M2 de la union. | 16.1 |
| P-13 Retardo | Dispersion y almacenamiento | El retardo depende de dispersion y resonancias; longitud/v no demuestra ruido, ancho de banda ni perdidas M2. | 16.1 |
| P-16 Puente | Aislamiento espacial | Dos componentes desconectados del grafo no prueban diafonia nula en los campos 3D. | 13.7; 15.6 |

### informacion / control

| Primordial | Primer eslabón sin demostración de dispositivo | Resultado o razón | Evidencia |
|---|---|---|---|
| P-07 Compuerta | Control fisico | No se ha obtenido de M2 un estado de compuerta con contraste, trabajo de control y ruido calculados. | 15.6 |
| P-09 Sensor | Acoplamiento de medida | Ganancia, retroaccion y correlaciones de ruido no estan determinadas por el trazo. | 15.6 |
| P-10 Selector | Observable del objetivo | El selector necesita un acoplamiento material que distinga objetivos y cuantifique falsos positivos. | 13.2; 15.6 |
| P-11 Memoria | Estados y barrera | La fase U(1) tiene barrera cero; Kerr, disipacion y escritura del ensayo anterior no fueron derivados de esta geometria. | 16.2 |
| P-12 Comparador | No linealidad y lectura | No se ha derivado el umbral de decision, su transductor ni su distribucion de error. | 15.6 |
| P-14 Reloj | Oscilacion y referencia | Una frecuencia modal no demuestra un reloj alimentado con estabilidad, arranque y difusion de fase calculados. | 14.5; 15.6 |
| P-15 Secuenciador | Estados y transiciones | La maquina de estados operacional no especifica estados microscopicos ni tasas de transicion. | 13.1; 15.6 |

### mecanica

| Primordial | Primer eslabón sin demostración de dispositivo | Resultado o razón | Evidencia |
|---|---|---|---|
| P-02 Anclaje | Fuerza y referencia | No hay perfil material con retroaccion que derive fuerza, rigidez y reaccion del anclaje. | 13.3; 15.6 |
| P-03 Recinto | Frontera y especies | La curva no fija barreras de cada especie, presion soportada ni tasas de fuga. | 13.7; 15.6 |
| P-19 Impulso | Momento y actuador | No hay solucion campo-materia que derive impulso, potencia, reaccion y saturacion. | 13.3; 15.6 |
| P-21 Vibración | Elasticidad y perdida | El modo cuadrupolar calculado no es un actuador material; falta acoplamiento, amortiguamiento y esfuerzo maximo. | 14.5; 15.3; 20.6 |

### energia / termica

| Primordial | Primer eslabón sin demostración de dispositivo | Resultado o razón | Evidencia |
|---|---|---|---|
| P-01 Semilla | Preparacion | El cero clasico es invariante; el bombeo neutro no crea carga neta aislada. | 13.8; 16.4 |
| P-05 Captador solar | Conversion y fuente | El ciclo de tres niveles usa niveles y tasas no derivados; el benchmark desacoplado no absorbe potencia runica de luz. | 13.2; 16.3 |
| P-06 Reserva | Estado, carga y acceso | La Q-ball almacena energia, pero no se ha realizado la geometria de Reserva ni carga/descarga, eficiencia o capacidad R1. | 14.1; 15.5; 20.5 |
| P-17 Luz | Emision electromagnetica | Falta el acoplamiento modal que convierta energia en fotones; b=0 implica conversion directa nula. | 13.2; 15.6 |
| P-18 Intercambio térmico | Contactos termicos | No estan definidos los acoplamientos y correlaciones de ambos contactos; se cuantifica el contraste de canales termicos. | 16.3 |
| P-20 Polarización | Respuesta electromagnetica | B escalar uniforme no introduce birrefringencia local; una respuesta anisotropa por geometria exige resolver Maxwell y materia. | 17.3 |

### materia / quimica

| Primordial | Primer eslabón sin demostración de dispositivo | Resultado o razón | Evidencia |
|---|---|---|---|
| P-22 Separación | Selectividad y transporte | Evaluada: faltan Hamiltoniano material, potenciales quimicos de especies y transporte; el benchmark desacoplado no produce separacion runica. | 17.4; 21.3 |
| P-23 Reacción | Cinética y balance | Evaluada: faltan superficies de energia, contactos y tasas derivadas de un Hamiltoniano quimico comun. | 17.4; 21.3 |
| P-24 Ensamblaje | Transporte y estructura | Evaluada: faltan seleccion de estructura, cinetica y propagacion de errores; depende del mismo contacto material de P-22 y P-23. | 17.4; 21.3 |

## 17.3. Precisiones transversales

La mecánica necesita un tensor de tensiones y una referencia que reciba la reacción. Un fluido escalar isotrópico carece de módulo de corte estático; un entramado podría adquirir rigidez por su estructura, pero esa estructura debe ser una solución estable y no un módulo de Young asignado después.

En una región homogénea con el portal electromagnético escalar y sin materia polarizable adicional, la lagrangiana es proporcional a B(E²−B_magnético²). En unidades de vacío, ε=B y μ=1/B: su producto vale uno y la velocidad de frente sigue siendo c. El factor escalar cambia la impedancia y el acoplamiento, pero no introduce por sí solo birrefringencia ni distingue las dos polarizaciones. Interfaces y geometrías pueden generar respuesta selectiva; necesitan su solución vectorial y no quedan excluidas por este resultado local.

Los balances de energía, información y entropía son restricciones necesarias compartidas. Cumplirlos no demuestra la existencia de estados de control, actuadores o contactos. De igual modo, un error numérico pequeño en una ecuación reducida no mide el error físico de sustituir un dispositivo por esa ecuación.

## 17.4. P-22, P-23 y P-24

Separación, Reacción y Ensamblaje se incluyen ahora en la revisión de dependencias físicas. El aplazamiento anterior se conserva en la fuente archivada, pero no es una instrucción vigente. El benchmark desacoplado no realiza esas funciones mediante M2; faltan el Hamiltoniano material y los procesos indicados en 21.3. Las fichas siguen siendo especificaciones, sin parámetros de operación validados. El ejemplo abstracto de dos estados no demuestra química ni ensamblaje.

## 17.5. Resultado final de esta evaluación

Se ha establecido un sector M2 escalar común con problema de Cauchy controlado, vacío estable, propagación causal y evidencia numérica reproducible de un estado cargado con modos radiales y no radiales. La prueba directa de guía autosostenida del capítulo 18 obtiene una banda longitudinal inestable. No se han derivado un extremo estable, preparación operacional ni acoplamiento térmico/material común que realicen R1. El catálogo registra 0 dispositivos completamente derivados, 24 evaluados respecto de sus dependencias y ninguno excluido por la antigua instrucción. Ningún resultado condicional se contabiliza como una primordial terminada.
