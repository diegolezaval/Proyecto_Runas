# Procedimientos y casos de dimensionamiento

## C.1. De la preparación a la luz

La interfaz pide «iluminar esta región» y una potencia óptica. La receta enlaza Semilla, fuente o Reserva, Canal, Compuerta, Sensor, control y Luz. El controlador verifica destino luminoso, fuente y ruta térmica; prueba a baja potencia, aumenta hasta la consigna y registra la respuesta. Al terminar, cierra la entrada, vacía el canal y mantiene el control durante la retirada.

La primera preparación desde el régimen inactivo sigue siendo una propiedad constitutiva sin protocolo microscópico derivado. R1 especifica su presupuesto objetivo: 5 J incorporados, 2 W transferidos, 0.05 W de mantenimiento y 0.25 s posteriores de asentamiento. El tiempo ideal resultante es \(5/(2-0.05)+0.25=2.814\) s, si el acoplamiento supuesto alcanza esas tasas. No constituye una demostración de que un gesto concreto aporte la excitación requerida. El uso cotidiano parte de una Semilla ya asentada.

Para una lámpara de 6 W ópticos con rendimiento 0.6, el emisor recibe 10 W y disipa 4 W. A 10 m de distancia, el Canal recibe \(10e^{0.001}=10.010005\) W, pierde 0.010005 W y consume otros 0.1 W de mantenimiento. Se asignan 0.05 W a Semilla y 0.5 W al conjunto de control y terminales del ejemplo. La fuente debe entregar 10.660005 W, sin incluir el servicio propio de Reserva si ésta alimenta el sistema.

Un captador de 0.02 m² recibe 20 W solares. Convierte 16 W, consume 0.04 W y deja 15.96 W disponibles. De ellos, 10.660005 W alimentan la lámpara y sus servicios; 5.299995 W quedan disponibles para carga o exportación. El balance externo del conjunto es: 6 W de luz útil, 8.700005 W de calor local y 5.299995 W exportados. Su suma es 20 W. Si la luz termina absorbida dentro de la habitación, esos 6 W también se vuelven calor de la habitación; no se cuentan simultáneamente como salida del mismo volumen.

La energía de preparación del ejemplo se contabiliza aparte: 5 J de Semilla, 10 J de Canal, 4 J de película captadora y un presupuesto adoptado de 20 J para emisor, control y terminales: 39 J en total. Estos últimos 20 J son una asignación del ejemplo, no un coeficiente obtenido de la acción. Un soporte mecánico nuevo, un radiador desplegado o una Reserva nueva añaden sus propias energías. La mesa y los terminales térmicos preexistentes son condiciones de este montaje.

## C.2. Crecimiento de una instalación

El captador inicial de 25 cm² requiere 0.5 J de película y produce 1.995 W netos bajo el Sol del caso. Si 0.05 W mantienen Semilla y el resto se reinvierte, \(\dot A=(798A-0.05)/200\), mientras no domine el límite del frente. La solución es

\[
A(t)=A_*+(A_0-A_*)e^{3.99t},\qquad A_*=0.05/798.
\]

El área crítica \(A_*\) marca el punto donde este presupuesto sólo mantiene Semilla. La tasa exponencial es una consecuencia ideal de la ley adoptada, no un crecimiento ilimitado: sombra, calor, cableado, apoyo y velocidad de borde se vuelven dominantes. Este caso supone un sustrato, acceso óptico y evacuación preexistentes. Construir toda la infraestructura requiere programar sus consumos en paralelo o antes de cada expansión.

Una instalación de 100 m² entrega hasta 79.8 kW en esas condiciones y descarga 20.2 kW térmicos antes de las cargas. Los enlaces y el sumidero deben dimensionarse a ese nivel. La interrupción de irradiancia se atiende con reservas o reducción de servicio; el área no produce esa potencia de noche.

## C.3. Reserva, elevación y recuperación

Una celda de un litro contiene hasta 1 MJ útil y 50 kJ estructurales. Durante descarga constante \(P_d\), si no hay recarga:

\[
E(t)=\left(E_0+\frac{P_d/\eta_d+P_0}{k}\right)e^{-kt}
-\frac{P_d/\eta_d+P_0}{k}.
\]

La duración hasta \(E=0\) se calcula invirtiendo esta expresión. No se usa simplemente \(E_0/P_d\) cuando importan servicio, fuga o eficiencia.

Elevar 100 kg un metro aumenta la energía gravitatoria en 981 J. Con rendimiento mecánico 0.9 exige 1090 J en el actuador y disipa 109 J. Si esa energía viene de Reserva con \(\eta_d=0.98\), consume 1112.245 J de carga útil, además de mantenimiento, pérdidas de Canal y control. Al descender lentamente, una recuperación global del 80 % devuelve 784.8 J a la carga útil y disipa 196.2 J en la cadena de retorno. El ciclo consume 327.445 J netos antes de servicios; coincide con 109+22.245+196.2 J de pérdidas. La recuperación no vuelve rentable un ciclo cerrado de elevación.

El soporte de referencia añade 200 kJ de preparación y 2 W de mantenimiento. Una fuerza estática de 981 N almacena unos 48.118 J elásticos. Preparar el soporte cuesta mucho más que levantar esa carga un metro; reutilizarlo evita repetir el coste. La fuente de reacción y la región donde se distribuye su presión forman parte de la receta.

Para una bajada de emergencia de un metro a velocidad limitada, la energía potencial se disipa o recupera. Una asignación local de 50 J para control durante 10 s a 5 W cubre ese servicio, pero no demuestra capacidad de soportar la carga si se destruye el elemento mecánico. Se separan pérdida de comunicación, pérdida de fuente y rotura estructural.

## C.4. Calefacción, enfriamiento y congelación

Para un objeto homogéneo de capacidad \(C\) con pérdidas lineales \(G(T-T_a)\):

\[
C\dot T=P_h-G(T-T_a).
\]

Un kilogramo de agua con \(C=4184\) J/K, calentador de 100 W, entorno a 20 °C y \(G=2\) W/K alcanza 40 °C en unos 1068.65 s. La energía suministrada es 106.865 kJ: 83.68 kJ aumentan la energía térmica del agua y unos 23.185 kJ se transfieren al entorno. Se supone mezcla suficiente y no evaporación significativa. No se equipara la lectura de un punto con la temperatura de todo el volumen sin esa condición.

En régimen a 40 °C, el servicio necesita 40 W. Un sensor con incertidumbre de 0.05 K y controlador con histéresis de ±0.1 K, actualizado cada 1 ms, puede presupuestar una banda de ±0.2 K bajo este modelo: el cambio máximo por muestra es menor que \(2.4\times10^{-5}\) K. Gradientes, inercia del sensor y retardo del actuador deben quedar dentro del margen restante. Si no se verifica esa condición, el objetivo de precisión no está satisfecho.

Congelar un kilogramo de agua desde 20 °C hasta hielo a 0 °C exige extraer 417.18 kJ con los calores adoptados. Para rechazo reversible a 293.15 K, el trabajo mínimo es

\[
W_{min}=mc_p\left[T_h\ln\frac{T_i}{T_f}-(T_i-T_f)\right]
+mL_f\left(\frac{T_h}{T_f}-1\right),
\]

con \(T_i=T_h=293.15\) K y \(T_f=273.15\) K. Resulta aproximadamente 27.41 kJ. Con mitad del COP de Carnot y terminales ideales, son unos 54.82 kJ y se rechazan unos 472.00 kJ. Los terminales finitos incrementan el trabajo y alargan el proceso. Esta cifra no se mezcla con el radiador a 400 K de otro caso: elevar la temperatura de rechazo cambia el cálculo.

## C.5. Materia ambiental y ruta química

Separación modifica composición; Reacción cambia especies; Ensamblaje organiza las especies obtenidas. Una cadena completa identifica alimentación, productos, residuos, energía libre, calor y cinética. El flujo molar de cada elemento y la carga se conservan. Para una red de reacciones \(\dot{\mathbf n}=N\mathbf v+\mathbf f\), la matriz estequiométrica \(N\) satisface \(AN=0\), donde \(A\) cuenta átomos por especie. A temperatura y presión dadas, \(\Delta_rG=\sum_i\nu_i\mu_i\) y una reacción espontánea aislada cumple \(v\Delta_rG\le0\); un proceso impulsado incluye el trabajo suministrado.

Como caso de contabilidad, \(CO_2(g)\rightarrow C(\mathrm{grafito})+O_2(g)\) requiere aproximadamente 394.389 kJ/mol de trabajo reversible estándar a 298.15 K. Para un gramo de carbono, usando 12.011 g/mol, son unos 32.84 kJ y se producen aproximadamente 2.664 g de oxígeno. A 420 ppm, 25 °C y una atmósfera, el volumen ideal de aire que contiene ese carbono es unos 4.85 m³, suponiendo captura total. Si se captura una fracción \(f\), el volumen aumenta como \(1/f\).

Una ruta química posible de estudio convierte electroquímicamente \(CO_2\) a CO y después utiliza \(2CO\rightleftharpoons C+CO_2\), reciclando el dióxido de carbono. Los equilibrios de cada etapa, catalizador, selectividad, separación y temperatura se resuelven por separado. Esta ruta identifica transformaciones materiales; no fija una productividad industrial ni demuestra depósito de grafito con la microestructura deseada. El potencial reversible global equivalente es \(\Delta G/(4F)\), aproximadamente 1.022 V, sin sobretensiones ni separación. No se interpreta como tensión suficiente de una celda concreta.

El calor de reacción estándar y el trabajo reversible son distintos: para la descomposición indicada \(\Delta H\approx393.522\) kJ/mol. En el límite reversible isotermo, \(Q=T\Delta S=\Delta H-\Delta G\), ligeramente negativo con estos estados. Un proceso real puede liberar mucho más calor por pérdidas. Reducir la barrera de activación con catálisis cambia la velocidad, no elimina \(\Delta G\).

## C.6. Ensamblaje y permanencia

Un producto se describe mediante composición, geometría, estructura interna, estado de tensiones y tolerancias. La fabricación usa alimentación material, posicionamiento, unión y verificación. La resolución del plano no garantiza resolución del actuador ni de la medida.

Una cadena de ensamblaje define una región pequeña de deposición o unión, comprueba su posición y resistencia, avanza y revisa errores acumulados. Para procesos térmicos se incluye enfriamiento y contracción. Para enlaces químicos se incluyen productos secundarios y difusión. El tiempo queda acotado por caudal material, velocidad de reacción, transporte de calor y tasa de verificación. Un plano de mil millones de posiciones no se ejecuta en un paso por estar guardado en Memoria.

El producto permanece tras retirar el campo sólo si constituye un estado material estable o metaestable bajo las condiciones de servicio. Si la forma depende de tensiones del campo, debe conservar el soporte o transferirse a otra estructura. La aceptación distingue error geométrico, composición, porosidad, defectos y resistencia; no usa el parecido visual como prueba suficiente.

## C.7. Procesos biológicos y nucleares

Las aplicaciones biológicas requieren identificación de tejido, perfusión, transporte de oxígeno y nutrientes, eliminación de residuos, integridad de barreras y función. Mantener una geometría anatómica no demuestra viabilidad. La especificación de una intervención debe declarar variables medibles, incertidumbre y criterios de interrupción definidos para esa aplicación. R1 no proporciona una pauta clínica ni umbrales universales de tejido; no habilita intervenciones sobre personas mediante las cifras mecánicas o térmicas generales.

La restauración funcional necesita información individual conservada. Una plantilla anatómica no reconstruye por sí misma conexiones, estados moleculares o recuerdos perdidos. El programa de reparación usa mediciones y referencias disponibles; los datos ausentes se registran como incertidumbre y no se sustituyen silenciosamente por una persona genérica.

Una reacción nuclear se identifica por núcleo inicial, proyectil, energía y canal. La energía \(Q=(\sum m_{in}-\sum m_{out})c^2\) sólo da el balance; la tasa depende de flujo y sección eficaz, por ejemplo \(R=N_t\int\phi(E)\sigma(E)dE\) en un blanco delgado. Se conservan las cargas y números cuánticos aplicables y se contabilizan productos secundarios y radiación. El catálogo no asigna a Reacción una orden universal de transmutación. R1 no contiene un reactor validado ni un perfil nuclear habilitado: faltan un canal definido y su diseño específico.

## C.8. Uso ordinario y aceptación de recetas

El usuario selecciona tarea, región y consigna. El sistema muestra disponibilidad, progreso y resultado medido. Antes de ejecutar, el integrador debe resolver:

1. La receta existe, las unidades coinciden y su estado inicial es válido.
2. La fuente, la energía de reserva y la potencia satisfacen el programa temporal.
3. Los destinos de calor, materia, momento e información están identificados.
4. Los terminales y la referencia están verificados en la región efectiva.
5. La transición de retirada es posible con los recursos reservados.

El paso a ejecución depende de esas condiciones, no de una confirmación manual de cada ecuación. Si alguna falla, se informa la causa concreta —por ejemplo «sumidero térmico insuficiente»— y se mantiene el estado físicamente compatible. Una interfaz simple significa que estas comprobaciones están automatizadas y sus límites son comprensibles.
