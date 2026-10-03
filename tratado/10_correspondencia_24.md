# Correspondencia de las 24 primordiales

Cada fila enlaza una responsabilidad del catálogo con grados físicos y coeficientes. La última columna impide confundir una verificación parcial con la construcción completa.

| Primordial | Mecanismo | Sector comprobado | Requisito pendiente de realización |
|---|---|---|---|
| P-01 Semilla | Preparación paramétrica y selección de modos | Umbral lineal de bombeo | Derivar modulación manual, saturación, forma y autonomía. |
| P-02 Anclaje | Gradiente de portal con referencia y realimentación | Fuerza como derivada de energía; controlador R1 reducido | Resolver perfil con retroacción y límites de fuerza; el fluido homogéneo no es un sólido. |
| P-03 Recinto | Barrera y superficie controlada | Balances y mecanismo de barrera | Calcular perfiles de frontera, tasas de fuga y estabilidad ante presión. |
| P-04 Canal | Modo transversal ligado y propagación longitudinal | Matriz de dispersión del grafo ideal P-04 | Derivar confinamiento 3D, coeficientes y diafonía desde M2. |
| P-05 Captador solar | Transducción radiativa y motor de trabajo | Convertidor resonante; ciclo de tres niveles | Obtener niveles y tasas de M2; integrar todo el espectro, ángulos y pérdidas. |
| P-06 Reserva | Estado fuera de equilibrio y descarga permitida | Familia radial y dE/dQ; balance R1 | Demostrar densidad útil y ciclo de descarga; no equiparar energía ligada y energía utilizable. |
| P-07 Compuerta | Desintonía o barrera modulada | Grafo ideal y mecanismo de umbral modal | Calcular modulación y margen de cierre para el glifo real. |
| P-08 Distribuidor | Dispersión de unión adaptada | Nexo: reflexión 1/9 y salidas 4/9; grafo P-08 | Realizar la adaptación física y su banda. |
| P-09 Sensor | Acoplamiento de observable a modo de lectura | Contrato de medida y relación respuesta–ruido | Derivar modalidad concreta, sensibilidad y calibración espacial. |
| P-10 Selector | Identificación a partir de medidas y memoria | Contrato de identificación; base modal lógica condicional | Implementar cálculo completo y tasa de identificación errónea. |
| P-11 Memoria | Biestabilidad alimentada o barrera pasiva | Dos atractores, autovalores y escritura/borrado numéricos | Derivar K y pérdidas del glifo; calcular fallos bajo ruido. Las dos realizaciones no se mezclan. |
| P-12 Comparador | No linealidad regenerativa con entradas diferenciales | Biestabilidad modal como mecanismo | Resolver suma diferencial, fan-out y margen de ruido. |
| P-13 Retardo | Propagación dispersiva o registro y reproducción | Fase de grafo y contrato causal | Calcular ancho de banda, distorsión y error temporal. |
| P-14 Reloj | Oscilación sostenida con saturación | Mecanismo formulado; no ciclo límite específico calculado | Derivar ganancia, saturación y ruido del glifo. |
| P-15 Secuenciador | Red física de estados lógicos | Máquinas de estados R1; soporte modal parcial | Construir la red física completa y probar tiempos, ruido y recuperación. |
| P-16 Puente | Dos familias modales con solapamiento pequeño | Dos componentes en grafo ideal | Calcular acoplamiento real 3D; el cero topológico no prueba diafonía cero. |
| P-17 Luz | Transferencia de energía a modos radiativos | Conversión de dos modos reversible bajo condiciones | Derivar terminal, niveles y eficiencia espectral. |
| P-18 Intercambio térmico | Máquina térmica de modos y baños | Motor de tres niveles y balances R1 | Realizar ciclo refrigerador específico y conductancias desde M2. |
| P-19 Impulso | Gradiente de energía modulado | Derivada analítica frente a numérica | Resolver actuación y reacción simultáneas bajo carga. |
| P-20 Polarización | Distribución de carga y respuesta electromagnética | Relación epsilon, mu, impedancia y química | Resolver terminales reales y estados de materia; los lazos no fijan una tensión. |
| P-21 Vibración | Actuación periódica sobre un modo mecánico | Mecanismo de fuerza y oscilador reducido | Derivar acoplamiento acústico, carga y amplitud estable. |
| P-22 Separación | Diferencias microscópicas de transporte | Balance detallado de dos estados abstractos | Calcular selectividad y recuperación de una mezcla concreta. |
| P-23 Reacción | Modificación de superficies y barreras químicas | Relación entre portales y escalas atómicas; balance detallado | Resolver una reacción real con su cinética y selectividad. |
| P-24 Ensamblaje | Control de transporte, colocación y unión | Cadena física formulada y balances de material | Calcular proceso material específico y errores; el plano no garantiza fabricación. |

## Regla común de reducción

Para variables accesibles a y modos internos b, el operador dinámico linealizado se particiona como \(D(\omega)\). La eliminación exacta lineal produce

\[D_{ef}(\omega)=D_{aa}-D_{ab}D_{bb}^{-1}D_{ba}.\]

La inversa debe ser retardada. Sus polos introducen resonancias, memoria y pérdidas cuando se acopla a un continuo. Una ley macroscópica constante sólo aproxima esta respuesta en una banda. Las mismas integrales que fijan ganancia y transporte afectan ruido, reflexión y retroacción.

## Composición y uso sencillo

La interfaz de usuario conserva tarea, región y consigna. La implementación elige un estado y una receta cuyos terminales estén identificados. La automatización administra el mecanismo microscópico y sus recursos; no reemplaza el mecanismo por el significado de una orden.
