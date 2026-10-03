# Canal, Memoria, Intercambio térmico y Semilla: resultado de aceptación

## 16.1. P-04 Canal: geometría y respuesta que sí se pueden calcular

El trazado canónico consta de N₁, T₁ y R₁, con puertos A, B y U. Sus longitudes se integran a partir de los segmentos y curvas Bézier racionales de `datos/geometria.json`. El recorrido plano A–B mide 8.176790797 unidades gráficas y la rama de control desde la bifurcación mide 1.593850866. Con la escala geométrica adoptada de 10 mm por unidad, son \(L=0.081767908\) m y \(L_U=0.015938509\) m. Un levantamiento tridimensional con rampas modificaría esas longitudes.

Esto fija una geometría de ejes. No fija la solución transversal de los campos, el perfil material que la confina ni los terminales físicos. En el vacío homogéneo, el operador transversal libre no tiene un modo localizado sobre ese eje: un modo guiado requiere un fondo o una frontera adicional calculada.

La solución radial del capítulo 14 prueba que M2 puede sostener un estado cargado localizado. No lo transforma en una guía curva. El capítulo 18 da el paso adicional: resuelve un tubo recto autosostenido de M2 y encuentra una inestabilidad longitudinal, por lo que rechaza esa realización como guía operacional. La alternativa homogénea de presión nula da \(c_s=1.4999\times10^8\) m/s. La densidad que ajusta sólo \(10^7\) m/s tiene \(p/\rho=-0.0771611\), por lo que incorpora una exigencia de confinamiento mecánico que el grafo no resuelve.

### Respuesta exacta del grafo condicionado

El anterior modelo de tres terminales abiertos con continuidad, conservación de derivadas salientes e igual impedancia tiene matriz de unión

\[
S_J=\tfrac23\mathbf1\mathbf1^T-I_3.
\tag{16.1}
\]

Los tramos sin bifurcaciones añaden fases. Para excitación desde A, \(|S_{BA}|^2=4/9\), \(|S_{UA}|^2=4/9\), \(|S_{AA}|^2=1/9\). La potencia que sale por U no es absorción; confundirla con pérdida material sería incorrecto. El valor \(4/9\) tampoco es una limitación universal de Canal: depende de cómo se termina U.

Si U se cierra con una terminación Neumann ideal, de reflexión unitaria, la fase de retorno a la bifurcación es \(\rho=e^{2ikL_U}\). Eliminar U da

\[
r=\frac{\rho-1}{\rho+3},\qquad
t=\frac{2(1+\rho)}{3+\rho},\qquad
\mathcal T=\frac{4\cos^2(kL_U)}{1+3\cos^2(kL_U)}.
\tag{16.2}
\]

En \(kL_U=n\pi\), \(\mathcal T=1\). En \(kL_U=(n+1/2)\pi\), \(\mathcal T=0\). Se ha derivado así una condición de funcionamiento y una de fallo **del grafo** sin inventar otra constante fundamental. El terminal es una configuración permitida, pero su realización todavía no está deducida de M2.

Con la velocidad R1 impuesta, pérdida intrínseca nula y una resonancia central, el límite de reflexión igual a \(1-e^{-\alpha L}=8.17676\times10^{-6}\) permite una semibanda de 571070.9 Hz. A ±500 kHz la reflexión es \(6.26815\times10^{-6}\). Esto podría satisfacer esa tolerancia de reflexión en el modelo ideal. Si además existe absorción, ésta consume parte del presupuesto; no se cuenta dos veces como si la reflexión fuera gratuita.

El retardo de grupo en la resonancia es

\[
\tau_g=(L+L_U/2)/v,
\tag{16.3}
\]

que da 8.973716 ns con \(v=10^7\) m/s, frente a 8.176791 ns de recorrido directo. El almacenamiento en la rama auxiliar modifica la respuesta aun cuando la transmisión central sea perfecta.

### Resultado completo de P-04

![Contraste del grafo con la condición del exterior M2](../graficos/M2_terminal_y_canal.svg)

| Eslabón | Resultado |
|---|---|
| Geometría | Ejes y longitudes calculados; confinamiento físico sin solución |
| M2 y \(\Theta_s\) común | Ecuaciones fijadas, sin parámetros nuevos de Canal |
| Campo de Canal | No se dispone de una solución 3D con los tres terminales |
| Modos y coeficientes | Hay modos de Q-ball y del Q-tubo libre; el tubo tiene una banda creciente. Los del grafo presuponen una guía estable |
| Propagación | Respuesta exacta del grafo condicionada a velocidad, paredes y terminales |
| Pérdidas, saturación y ruido | No derivadas para la guía; \(\alpha\), potencia máxima y SNR siguen siendo metas |
| Preparación | No se ha generado ese estado desde una fuente física |
| Función R1 | **No aceptada como derivada** |

La potencia de 100 kW que resulta de multiplicar área por flujo máximo R1 es una especificación, no un límite de ruptura deducido. Sin el campo transversal y su respuesta no lineal no se puede asignar un umbral de saturación, radio de curvatura seguro, calentamiento, fuga o probabilidad de error.

## 16.2. P-11 Memoria: derivación permitida y exclusión de una codificación

P-11 tiene un ciclo y un puerto externo. Un ciclo geométrico puede producir resonancias, pero no implica dos estados estables, una barrera energética ni operaciones de escritura y lectura. En un sistema lineal conservativo con un único canal abierto y sin otros sumideros, la dispersión estacionaria es unitaria y \(|S|=1\); la energía almacenada transitoriamente y la fase de reflexión no constituyen por sí mismas una memoria digital estable.

### El coeficiente de Kerr debe salir del campo

Para ilustrar la reducción correcta, supóngase que ya existe un modo espacial \(u\) de frecuencia \(\Omega_0\), normalizado por \(\int|u|^2d^3x=1\). En régimen débil, la eliminación estática del mediador a orden cuártico produce

\[
C_4=\lambda_0\int|u|^4d^3x-
\frac{g^2}{2}\langle |u|^2,(-\nabla^2+M^2)^{-1}|u|^2\rangle.
\tag{16.4}
\]

Las condiciones de frontera del inverso son las del mediador real del dispositivo. Con la convención de un modo de carga \(\Phi=a u/\sqrt{2\Omega_0}\), \(n=|a|^2\), el término clásico \((K/2)n^2\) tiene

\[
K=C_4/(2\Omega_0^2).
\tag{16.5}
\]

Esta expresión es una reducción débil y estática; un fondo cargado intenso necesita la proyección completa de sus modos y el mediador dinámico. No identifica los parámetros del ensayo Kerr previo.

Para un dominio cuyo operador \(-\nabla^2\) sea no negativo,

\[
-\lambda\int|u|^4\le C_4\le\lambda_0\int|u|^4.
\tag{16.6}
\]

El núcleo cuártico de una componente de densidad de número de onda \(k\) es \(\lambda_0-g^2/[2(M^2+k^2)]\). En el benchmark cambia de signo en \(k/m=100/\sqrt{99}=10.050378\). El tamaño y el perfil del modo importan; no se puede fijar \(K=1\) para Memoria y declarar que M2 lo predice. Al no existir aún el modo de P-11, (16.4) no se puede convertir en un número propio de esa geometría.

### Dos fases globales no proporcionan la barrera R1

En el sistema aislado U(1), los estados \(\Phi_\theta=e^{i\theta}\Phi_0\) tienen exactamente la misma energía para todo \(\theta\). La trayectoria entre \(\theta=0\) y \(\theta=\pi\) tiene barrera cero. Los portales que dependen sólo de \(s\) tampoco distinguen su fase global sin una referencia adicional.

Por tanto, esa codificación concreta **no produce** la barrera R1 de \(60k_BT\): a 300 K, \(60k_BT=2.48517\times10^{-19}\) J = 1.55112 eV. Esto no excluye memoria por amplitud, carga, geometría, interferencia con una referencia o alimentación externa; esas realizaciones requieren demostrar otros estados y operaciones.

El oscilador Kerr alimentado anterior tenía dos atractores para coeficientes elegidos. M2 aislado es hamiltoniano; en una truncación cerrada, el flujo conserva volumen de fase y no genera dos atractores asintóticos disipativos con cuencas abiertas. Un subsistema sí puede perder energía hacia radiación o un baño: sus tasas deben salir de (15.9), con el ruido correspondiente. Una excitación aditiva de un modo cargado requiere contabilizar la fuente de carga; no se obtiene automáticamente de una modulación neutra de \(|\Phi|^2\).

Para un proceso térmico de equilibrio con barrera conocida, el modelo de Arrhenius daría \(\tau=\tau_0e^{\Delta E/k_BT}\). Los valores R1 \(\tau_0=10^{-12}\) s y \(\Delta E=60k_BT\) arrojan \(1.14201\times10^{14}\) s, pero ni esa barrera ni el prefactor han sido derivados. En una memoria alimentada fuera del equilibrio, la tasa de escape necesita la dinámica estocástica o el espectro del generador abierto; no basta insertar una barrera térmica.

El límite \(k_BT\ln2=2.87098\times10^{-21}\) J para un borrado lógico irreversible ideal a 300 K es una cota termodinámica, no una predicción de consumo, rapidez o fidelidad. **P-11 no satisface el criterio completo**, y no se publican como resultados su retención, densidad de bits, tasa de error, tolerancia a ruido o tiempo de escritura.

## 16.3. P-18 Intercambio térmico: transporte y trabajo

Se requiere distinguir tres cosas: conducción pasiva entre dos contactos térmicos, refrigeración con trabajo externo y conversión de calor en trabajo. Un ciclo de tres niveles con energías y tasas escogidas no demuestra ninguna realización concreta de P-18 mediante M2.

La geometría de P-18 tiene un puerto de trabajo/control y un ciclo. Los contactos caliente y frío pueden ser superficies del cuerpo del dispositivo, pero sus Hamiltonianos y acoplamientos deben especificarse: no nacen de etiquetar el puerto como «térmico». En el benchmark escalar desacoplado, la conductancia **rúnica hacia materia ordinaria** es cero. Una materia que conduzca calor por sus interacciones ordinarias no convierte ese cero en un efecto rúnico derivado.

### Conductancia derivable de una transmisión

Para transporte bosónico pasivo, balístico y lineal entre reservorios térmicos,

\[
\dot Q=\sum_n\int_{\Omega_{n,min}}^\infty
\frac{d\Omega}{2\pi}\hbar\Omega\,
\mathcal T_n(\Omega)[n_B(\Omega,T_h)-n_B(\Omega,T_c)].
\tag{16.7}
\]

\(\mathcal T_n\) debe calcularse del problema de campos y contactos. Un canal independiente sin brecha y con transmisión unitaria tiene

\[
G_Q=\pi^2k_B^2T/(3h_P),
\tag{16.8}
\]

donde \(h_P\) es la constante de Planck, para distinguirla del acoplamiento escalar \(h\). A 300 K, \(G_Q=2.83929\times10^{-10}\) W/K. Una conductancia pasiva de 100 W/K requiere al menos \(3.52200\times10^{11}\) canales ideales equivalentes en este marco. No se trata de la capacidad de un solo modo del grafo.

Como contraste, si cada canal tiene la brecha de vacío ilustrativa de 1 eV y transmisión perfecta por encima de ella,

\[
G_{gap}=\frac{k_B^2T}{h_P}
\int_{\Delta/(k_BT)}^\infty
\frac{x^2e^{-x}}{(1-e^{-x})^2}dx.
\tag{16.9}
\]

Para \(\Delta/(k_BT)=38.681727\), se obtiene \(G_{gap}=2.15888\times10^{-24}\) W/K por canal. Alcanzar 100 W/K requeriría \(4.63204\times10^{25}\) de esos canales ideales. Una fase condensada puede tener modos colectivos sin brecha; materia real aporta otros modos; una bomba activa tiene otro balance. Por eso este contraste no es una exclusión universal de P-18, pero sí impide atribuir la conductancia R1 a un único modo masivo de vacío.

### Pérdidas, ruido y umbrales

La respuesta térmica cerca del equilibrio también puede expresarse como

\[
G=\frac1{k_BT^2}\int_0^\infty
\langle J_Q(t)J_Q(0)\rangle_{eq}\,dt,
\tag{16.10}
\]

en el límite clásico y con la corriente, proyección de equilibrio y contactos apropiados; el caso cuántico requiere su correlación de Kubo. Sin el Hamiltoniano y el estado de ambos contactos no se conoce esa correlación. Elegir \(G=100\) W/K y luego calcular calor transferido no deriva \(G\).

Para refrigeración entre \(T_c<T_h\), el balance da \(P=\dot Q_h-\dot Q_c\), y la segunda ley exige \(\mathrm{COP}=\dot Q_c/P\le T_c/(T_h-T_c)\) bajo las hipótesis térmicas usuales. La igualdad es reversible, con potencia finita no garantizada. El valor «mitad de Carnot» de R1 es una meta; no una consecuencia de \(\Theta_s\).

Sin contactos derivados no se obtienen potencia máxima, temperaturas de fallo, irreversibilidad, fluctuaciones térmicas ni tiempo de llegada a consigna. **P-18 no queda aceptada**. Sus balances son consistentes como contratos; no constituyen el dispositivo solicitado.

## 16.4. P-01 Semilla: de datos iniciales a operación

La evolución de la Q-ball del capítulo 14 empieza con un campo y una carga ya presentes. El arranque físico necesita especificar una fuente, el estado inicial de todos los sectores, el flujo de carga, el trabajo entregado, el criterio de selección espacial y la saturación. Ninguno de esos elementos se reemplaza por usar el perfil final como dato inicial del solucionador.

La unicidad de la solución clásica conserva el estado \(\Phi=0\) bajo bombeo multiplicativo si también \(\dot\Phi=0\); la simetría U(1) conserva la carga total. Un esquema paramétrico lineal con modulación prescrita puede amplificar perturbaciones. Su umbral no demuestra que un gesto material genere esa modulación ni que seleccione la forma de Canal.

La cota energética del caso R1 es

\[
t_{carga}\ge\frac{5\,\mathrm J}{2\,\mathrm W-0.05\,\mathrm W}
=2.56410\,\mathrm s.
\tag{16.11}
\]

Sumar los 0.25 s adoptados de asentamiento da 2.81410 s. Sólo tiene sentido si los 2 W están realmente transferidos al sector rúnico. Con portales nulos la potencia transferida desde materia es cero y la cota no proporciona un arranque. Con portales no nulos hay que calcularla. La energía almacenada y el flujo de carga deben ser compatibles simultáneamente; aportar julios no garantiza preparar la carga y la geometría deseadas.

Los fallos demostrados son el arranque clásico desde cero por una fuerza exclusivamente multiplicativa y la creación de carga neta aislada mediante una fuente U(1)-invariante. La preparación cuántica, térmica o por terminales cargados no está descartada, pero **no ha sido derivada en el dispositivo**. P-01 no queda aceptada.

## 16.5. Qué decisión se sigue del criterio solicitado

Ninguna de las cuatro pruebas satisface todos los eslabones. En consecuencia, no se extrapola éxito a las otras primordiales. El capítulo 17 aplica la misma regla al catálogo y marca qué dependencias bloquean cada función. Es un resultado de evaluación, no una promesa de que añadir una ficha resolverá el problema.

El objetivo «M2 común → geometría → estado → comportamiento → R1» continúa sin demostración. Esta edición aporta teoremas, soluciones, espectros, dinámica y contrastes reproducibles que permiten identificar exactamente qué parte está establecida y qué inferencia no se puede hacer. No presenta esa diferencia como un cierre obtenido.
