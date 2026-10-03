# Correspondencia microscópica y macroscópica

Edición 3.0.0. Este capítulo desarrolla la cadena de cálculo entre la acción del campo y los dispositivos. Se mantienen las geometrías canónicas. Se corrige la interpretación de sus prestaciones: una cifra de ingeniería no se transforma en una constante microscópica por insertarla en una tabla.

## MM.1. Qué constituye un cierre físico

Un dispositivo queda derivado cuando se proporcionan conjuntamente su acción, parámetros, estado preparado, condiciones de contorno, excitaciones accesibles, respuesta de los terminales y evolución frente a perturbaciones. La cadena es

\[
(S,\Theta,\text{entorno},\text{preparación})
\longrightarrow\Phi_0
\longrightarrow\mathcal L_{\rm fluctuaciones}
\longrightarrow\text{modos y acoplamientos}
\longrightarrow\text{respuesta y límites}.
\]

La última flecha no puede usarse a la inversa como demostración de las anteriores. Es posible resolver un problema inverso para buscar parámetros; la solución debe regresar después a las ecuaciones originales y satisfacerlas.

En esta edición se desarrollan las ecuaciones de esa cadena, se resuelven sectores concretos y se asigna a cada primordial un mecanismo. La geometría por sí sola sigue sin imponer una función semántica. El nombre «Memoria» no añade estados metastables al Hamiltoniano; el nombre «Captador» no crea absorción.

Se emplean cuatro estados de evidencia: **derivación analítica**, **verificación numérica de un sector**, **realización condicional** y **no establecido**. Una realización condicional contiene un mecanismo y condiciones precisas, pero no equivale a un dispositivo completo obtenido de la acción en tres dimensiones. La física microscópica conjunta de las veinticuatro primordiales todavía no está cerrada. El objetivo de rigor impide sustituir ese resultado por una declaración de completitud.

## MM.2. Problema microscópico bien definido

Se conserva la acción escalar compleja del capítulo 4, con el mismo potencial sextico y las mismas funciones \(A(s),B(s)\). En el régimen de laboratorio de este capítulo se toma \(\xi=0\), fondo aproximadamente plano y orden clásico; las correcciones de teoría efectiva se separan. Se usan \(c=\hbar=1\) salvo conversiones expresas a SI.

La especificación de un experimento requiere \(\Phi(t_0,\mathbf x)\), \(\dot\Phi(t_0,\mathbf x)\), campos electromagnéticos que satisfagan Gauss y ausencia de monopolos, estado de materia, condiciones de frontera y fuentes físicas. Una orden del controlador no reemplaza estas condiciones.

La energía escalar es

\[
H_\Phi=\int d^3x\,[|\dot\Phi|^2+|\nabla\Phi|^2+U(|\Phi|^2)].
\]

El potencial adoptado es positivo fuera del vacío para la desigualdad del capítulo 4. La energía electromagnética, expresada mediante \(\mathbf D\) y \(\mathbf B_{em}\), es

\[
H_{em}=\int d^3x\left[\frac{\mathbf D^2}{2\epsilon_0 B(s)}+
\frac{B(s)\mathbf B_{em}^2}{2\mu_0}\right].
\]

Se utiliza \(\mathbf B_{em}\) para distinguir inducción magnética de la función de acoplamiento \(B(s)\). La positividad de \(B\) asegura energía electromagnética positiva en este sector. No prueba estabilidad del estado acoplado: las derivadas de \(A,B\), la materia y el bombeo pueden alterar el espectro.

La versión cuántica se define por cuantización de los campos y un regulador a una escala declarada. Como la acción contiene operadores no renormalizables y funciones no polinómicas, es una teoría efectiva. Una solución clásica no suministra automáticamente una teoría válida a todas las energías ni una estimación de los coeficientes de todos los operadores omitidos. La escala de corte física no puede ser mayor que una escala de interacción fuerte que aparezca antes.

## MM.3. Del potencial a un fluido de campo

Escribamos \(\Phi=\sqrt s\,e^{i\theta}\). La lagrangiana escalar es

\[
\mathcal L=-\frac{(\partial s)^2}{4s}+sX-U(s),\qquad
X=-\partial_\mu\theta\partial^\mu\theta.
\]

Si las variaciones son lentas frente al modo radial, se desprecia el primer término sólo en esa aproximación. Entonces \(U'(s)=X\) y

\[
P(X)=s(X)X-U(s(X)),\qquad P_X=s,\qquad P_{XX}=\frac1{U''(s)}.
\]

La presión y densidad de energía del fondo homogéneo son

\[
p=sU'-U,\qquad \rho=sU'+U,
\]

\[
\frac{c_s^2}{c^2}=\frac{sU''}{sU''+2U'},\qquad
K_{bulk}=(\rho+p)\frac{c_s^2}{c^2}.
\]

\(K_{bulk}\) es módulo de compresibilidad, no módulo de Young. Este estado homogéneo tiene módulo cortante estático nulo: es un fluido de campo. Obtener un soporte que conserve una forma requiere confinamiento, estructura inhomogénea o control activo; no basta asignarle un valor de Young.

Para \(\hat U(\hat s)=\hat s-\hat s^2+\hat s^3\), el estado homogéneo no vacío con presión cero está en \(\hat s=1/2\). Allí

\[
\hat\omega^2=3/4,\quad \hat\rho=3/4,\quad
c_s=c/2,\quad K_{bulk}=\rho/4.
\]

Estos resultados se derivan del mismo potencial usado en el ensayo radial. La velocidad de 10⁷ m/s de R1 no es la velocidad de sonido de este estado. Si se intenta obtenerla cambiando únicamente \(s\) en la rama homogénea, resulta \(\hat s\simeq0.3340743\), con \(p/\rho\simeq-0.0767643\). Ese estado necesita sostener tensión y no sustituye al estado libre de presión cero. Un canal con menor velocidad efectiva podría usar dispersión, periodicidad o almacenamiento temporal; debe calcularse su banda y sus pérdidas.

## MM.4. Escalas físicas: qué se puede ajustar y qué no

Con \(g_6=\kappa m_r^2/(\lambda^2\Lambda^2)=1\), el cambio de unidades da

\[
\ell_0=\frac{\hbar c}{m_r},\quad E_0=\frac{m_r}{\lambda},\quad
\rho_0=\frac{m_r^4}{\lambda(\hbar c)^3}.
\]

Aquí \(m_r\) se expresa como energía; \(E_0\) y \(\rho_0\) se convierten después a julios. Como ejemplo de ajuste de una sola propiedad, \(m_r=1\) eV y \(\lambda\simeq1.56391\times10^{-8}\) sitúan el estado de presión cero en \(10^9\) J/m³. Si \(\Lambda=10^6\) eV, corresponde \(\kappa\simeq2.44582\times10^{-4}\). La longitud elemental es 0.197327 µm y \(|\Phi|/\Lambda\simeq0.0056543\) en ese fondo.

Esta elección no es el conjunto \(\Theta\) completo de R1. No fija los portales, la disipación, el vacío en presencia de materia, el arranque ni las tasas de conversión. Además, cambiar \(\lambda\) respecto del ensayo adimensional cambia las cargas y energías físicas aunque conserve la forma adimensional. El ejemplo demuestra cómo conectar unidades; no demuestra simultáneamente todas las prestaciones.

Una densidad de energía total tampoco es densidad de trabajo extraíble. La energía de un estado mínimo a carga fija está ligada a esa carga. Para reservar trabajo debe definirse un estado de referencia accesible, una ruta de descarga y el destino de la carga conservada. La exergía restringida compara estados bajo las mismas leyes de conservación; descargar no consiste en borrar \(Q_r\).

## MM.5. Fluctuaciones: amplitud, fase y estabilidad

Alrededor de \(\Phi_0=f(\mathbf x)e^{i\omega t}\), tomamos

\[
\Phi=e^{i\omega t}\left[f+\frac{u+iv}{\sqrt2}\right].
\]

En el sector aislado, la linealización produce

\[
\ddot u-2\omega\dot v+L_+u=0,\qquad
\ddot v+2\omega\dot u+L_-v=0,
\]

\[
L_-=-\nabla^2+U'(f^2)-\omega^2,\qquad
L_+=L_-+2f^2U''(f^2).
\]

La estabilidad depende del sistema acoplado y de la restricción de carga, no del signo de un operador aislado. La invariancia de fase implica \(L_-f=0\). La invariancia de traslación produce modos neutros cuando no hay frontera o anclaje que la rompa.

En un fondo homogéneo, con \(D=sU''+2\omega^2\), las dos ramas son

\[
\Omega_\pm^2=k^2+D\pm\sqrt{D^2+4\omega^2k^2}.
\]

La rama inferior reproduce el sonido de MM.3 para \(k\to0\); la superior conserva una brecha. Las frecuencias numéricas de la matriz de primer orden coinciden con esta expresión en los puntos ensayados. La velocidad de grupo de una banda y la velocidad causal del frente no deben confundirse.

Para el estado radial de \(\hat\omega=0.9\), la edición anterior verificaba energía y virial. Ahora se añaden estados vecinos y dos mallas del Hessiano radial. Se obtiene \(d\hat E/d\hat Q\simeq0.8999623\), compatible con \(dE/dQ=\omega\), y \(d\hat Q/d\hat\omega\simeq-2.32934\times10^5\). El autovalor inferior de \(L_-\) se acerca a cero al refinar la malla. El autovalor negativo de \(L_+\) no se etiqueta como fallo ni como prueba suficiente de estabilidad: debe tratarse con carga fija y mezcla de fase y amplitud.

Faltan para una prueba espectral completa los sectores angulares, el espectro acoplado completo, perturbaciones finitas y el entorno del dispositivo. Los modos de una esfera no son los modos de una red con cruces.

## MM.6. Proyección modal y coeficientes calculables

Para un estado preparado conocido se expande \(\eta=(u,v)=\sum_iq_i(t)e_i(\mathbf x)+\eta_\perp\). Integrar la acción produce

\[
L_{red}=\tfrac12\dot q^TM\dot q+\dot q^TCq-V(q),
\]

\[
V=\tfrac12q^TKq+\frac{C_{ijk}^{(3)}}{3!}q_iq_jq_k+
\frac{C_{ijkl}^{(4)}}{4!}q_iq_jq_kq_l+\cdots.
\]

\(M\) y \(K\) son integrales de la métrica cinética y del Hessiano sobre los modos; \(C-C^T\) es el acoplamiento giroscópico de fase y amplitud. Los coeficientes de tercer y cuarto orden son integrales de las derivadas funcionales de la energía evaluadas en \(\Phi_0\), no coeficientes escogidos por el nombre del módulo. El Hamiltoniano es

\[
H_{red}=\tfrac12(p-Cq)^TM^{-1}(p-Cq)+V(q).
\]

Un truncamiento a cuarto orden puede perder la estabilidad a gran amplitud del potencial sextico original. Se utiliza únicamente dentro del rango comprobado. Para eliminar modos de alta frecuencia se requiere separación espectral; cerca de una resonancia se incluyen como variables explícitas.

Con una coordenada normalizada a masa uno, potencial \(\omega_c^2q^2/2+c_3q^3/3!+c_4q^4/4!\) y no linealidad débil, la frecuencia dependiente de ocupación tiene, al orden perturbativo indicado,

\[
K_{Kerr}=\hbar\left(\frac{c_4}{8\omega_c^2}-\frac{5c_3^2}{24\omega_c^4}\right).
\]

Así se obtiene un coeficiente de cavidad a partir de un potencial modal. Una derivada cuártica positiva no garantiza \(K_{Kerr}>0\): la corrección cúbica también contribuye. Los modos eliminados pueden añadir otras correcciones.

Para coordenadas geométricas \(\lambda_a\), la fuerza generalizada es \(-\partial H/\partial\lambda_a\). Si las cambia un controlador, el trabajo es \((\partial H/\partial\lambda_a)\dot\lambda_a\). Esta identidad conecta preparación, deformación y energía sin introducir operaciones gratuitas.

## MM.7. Del campo a Tránsito, Repliegue y Nexo

Una guía necesita un modo transversal ligado. En un sector desacoplado, el problema transversal tiene la forma

\[
[-c^2\nabla_\perp^2+V_\perp(\mathbf r_\perp;\Phi_0)]\psi_n
=\Omega_{\perp n}^2\psi_n.
\]

Una banda aislada permite escribir \(\eta\simeq q(\ell,t)\psi_0\), con masa por longitud y rigidez obtenidas por integración transversal. Curvatura, cambios de sección y proximidad de otras guías mezclan modos. En un fondo que rota, se resuelve el problema matricial de MM.5; un único potencial escalar es una aproximación, no la ecuación universal.

Bajo la hipótesis explícita de guías preparadas, se obtiene un grafo métrico:

- **Tránsito:** tramo de guía; su longitud y dispersión producen fase y retardo.
- **Repliegue:** tramo curvado o retorno; modifica longitud y, fuera del límite ideal, mezcla modal y reflexión. No es un rectificador por tener forma angular.
- **Nexo:** región de unión; conserva flujos y tiene una matriz de dispersión determinada por los modos y la impedancia.

En una unión ideal con \(d\) ramas de igual impedancia, continuidad del campo y suma de derivadas salientes nula dan

\[
S_{ij}=\frac2d-\delta_{ij}.
\]

Para tres ramas, una entrada refleja \(1/9\) de la potencia y transmite \(4/9\) a cada salida. No es un divisor perfectamente adaptado. Eliminar la reflexión exige cambiar impedancias, geometría, resonancias o control; se calcula de nuevo la matriz.

El grafo de cada primordial se obtiene de las longitudes Bézier y de las uniones racionales. Sólo se fusionan las uniones declaradas; un cruce dibujado no añade un nodo. En cada arista se propaga la fase \(e^{ikL}\). Las matrices calculadas conservan flujo en el modelo ideal. Los dos componentes de Puente permanecen desacoplados porque así se define el grafo; esto no demuestra que sus campos físicos próximos tengan diafonía nula.

Un glifo de un solo puerto y sin pérdidas devuelve toda la potencia en régimen estacionario. Para que Semilla, Sensor o Memoria absorban, almacenen o midan hay que añadir sus modos internos, pérdidas y terminales. La forma de un lazo no basta. Polarización, sin extremos libres, necesita sus regiones de acoplamiento D, Z₊ y Z₋; no se le inventan puertos geométricos.

## MM.8. Fuerza sobre materia y reacción

Para una partícula ordinaria de masa de referencia \(m\), el acoplamiento conformal da

\[
S_p=-mc\int A(s)\,ds_g.
\]

En un entorno lentamente variable y a velocidad pequeña, la energía de interacción es \(V_m=mc^2[A(s)-1]\) y

\[
\mathbf F=-mc^2\nabla A(s),\qquad
\mathbf a\simeq-c^2\nabla\ln A(s).
\]

La segunda expresión utiliza la inercia local \(mA\) y omite correcciones de velocidad y variación temporal. Para una distribución extendida se integra la densidad material y se resuelve su deformación. El campo siente la retroacción correspondiente a través de la traza de materia.

Una demostración numérica comprueba la fuerza como derivada de energía para un perfil impuesto. Esa comprobación no demuestra que el perfil pueda prepararse. El problema completo debe resolver a la vez campo, materia y fuentes que fijan el perfil. La reacción puede ir a un soporte, otra región de campo, un flujo material o radiación; no desaparece en el controlador.

**Anclaje** aplica realimentación sobre una fuerza de esta clase o sobre un terminal electromagnético. **Impulso** modula su historia temporal. **Vibración** usa una consigna oscilante y el acoplamiento a un medio. Los tres comparten el mecanismo de fuerza; difieren en estado, terminales y ley de control. Para Anclaje, la rigidez activa \(K_{act}\) es producto de ganancia de medida, control y actuación dentro de su banda; no debe confundirse con un módulo de Young del condensado homogéneo.

Un campo que ofrece a una especie una barrera \(\Delta V\) puede participar en Recinto o Separación. El paso depende de distribución térmica, dinámica de colisiones y túnel. En una aproximación térmica clásica, factores del tipo \(e^{-\Delta V/k_BT}\) describen supresión activada; no garantizan impermeabilidad exacta.

## MM.9. Electromagnetismo, radiación y conversión

Con \(s\) constante y sin materia polarizable adicional:

\[
\epsilon=\epsilon_0B(s),\quad\mu=\mu_0/B(s),\quad
n=\sqrt{\epsilon\mu/(\epsilon_0\mu_0)}=1,\quad Z=Z_0/B(s).
\]

El portal modifica impedancia, no una velocidad óptica arbitraria en vacío homogéneo. Una interfaz puede reflejar por cambio de impedancia. Si \(B\) es real, estático y no hay canales inelásticos, esa reflexión y transmisión conservan energía; no existe absorción neta por decreto.

La expansión \(B(s)=B(s_0)+B'(s_0)\delta s+\cdots\) acopla fluctuaciones escalares a \(F^2\). Un campo electromagnético de fondo permite términos bilineales entre una perturbación electromagnética y una escalar; sus acoplamientos son integrales de solapamiento. Sin ese fondo, el término puede representar procesos de varios cuantos y necesita el análisis cinemático correspondiente. Una onda plana electromagnética ideal tiene \(F_{\mu\nu}F^{\mu\nu}=0\); reemplazar la radiación solar por un valor estático arbitrario de \(F^2\) no describe su captación.

Para dos modos resonantes acoplados, uno luminoso \(a\) y uno receptor \(b\), la aproximación de banda estrecha da

\[
\dot a=-\frac\kappa2a-igb+\sqrt{\kappa_e}\,a_{in},\qquad
\dot b=-\frac\gamma2b-iga,
\]

\[
\eta_{transferencia}=\frac{4\mathcal C}{(1+\mathcal C)^2}
\frac{\kappa_e}{\kappa}\frac{\gamma_e}{\gamma},\qquad
\mathcal C=\frac{4g^2}{\kappa\gamma}.
\]

Las tasas totales incluyen salidas útiles y pérdidas. En el ensayo \(\mathcal C=1\), \(\kappa_e/\kappa=0.95\) y \(\gamma_e/\gamma=0.85\), resultando 80.75 % de transferencia de energía. Reflexión, salida y ambas pérdidas suman la entrada. Este resultado tiene condiciones concretas y no deriva el valor de \(g\) desde un glifo.

**Captador solar** necesita además banda espectral, distribución angular y un mecanismo de conversión a trabajo. La transferencia de radiación térmica a otro modo no crea automáticamente una reserva de trabajo coherente. La ergotropía,

\[
\mathcal W(\rho,H)=\operatorname{Tr}(\rho H)-\min_U\operatorname{Tr}(U\rho U^\dagger H),
\]

separa energía y trabajo unitariamente extraíble. La conversión solar completa utiliza el desequilibrio entre fuente, dispositivo y sumidero y debe respetar su entropía. El 80 % de R1 sigue siendo un objetivo de sistema; no se declara demostrado por el 80.75 % de este convertidor monocromático.

**Luz** utiliza el intercambio inverso con modos radiativos y terminales. **Polarización** establece cargas, corrientes o respuesta dieléctrica mediante materia y campos; Maxwell, continuidad de carga y energía de los campos siguen vigentes. La reciprocidad de un acoplamiento pasivo implica que también existe la ruta inversa; una válvula direccional necesita polarización apropiada, modulación o disipación explícitas.

## MM.10. Disipación y temperatura desde grados microscópicos

Un baño armónico explícito puede escribirse

\[
H=\frac{p^2}{2M}+V(q)+\sum_j\left[\frac{p_j^2}{2m_j}+
\frac{m_j\omega_j^2}{2}\left(x_j-\frac{c_jq}{m_j\omega_j^2}\right)^2\right].
\]

La forma cuadrada incluye el contratermino que evita alterar silenciosamente el potencial. Eliminando los osciladores y usando un baño inicialmente térmico condicionado a \(q(0)\), se obtiene

\[
M\ddot q+V'(q)+\int_0^t\Gamma(t-t')\dot q(t')dt'=\xi(t),
\]

\[
\Gamma(t)=\sum_j\frac{c_j^2}{m_j\omega_j^2}\cos\omega_jt,\qquad
\langle\xi(t)\xi(t')\rangle=k_BT\Gamma(|t-t'|)
\]

en el límite clásico del baño. Un baño finito puede devolver energía; la irreversibilidad duradera requiere muchas escalas y el límite temporal apropiado. La fricción instantánea sólo aproxima una memoria de correlación corta. La formulación cuántica usa el espectro de ruido y balance detallado, no ruido blanco clásico a toda frecuencia.

Para una ecuación maestra térmica consistente, las tasas de subir y bajar una energía \(\hbar\omega\) satisfacen \(\gamma_\uparrow/\gamma_\downarrow=e^{-\hbar\omega/k_BT}\). Con los supuestos de acoplamiento débil y generador térmico apropiado, la producción de entropía es no negativa. Asignar tasas locales arbitrarias en un sistema fuertemente acoplado puede violar esa propiedad.

**Intercambio térmico** se realiza conectando modos a dos baños y, si se bombea calor contra gradiente, a trabajo de control. El COP procede del ciclo y de las tasas, no de una propiedad verbal de la runa. R1 proporciona una meta para dicho COP; la teoría anterior no identifica aún un ciclo microscópico único que alcance esa meta en todas sus condiciones.

## MM.11. Medición, lógica y memoria

Un Sensor acopla un observable \(O\) a una coordenada de lectura: \(H_{int}=-gqO\). Su respuesta lineal se calcula con el correlador retardado; el mismo acoplamiento introduce retroacción. La fuerza de señal, la susceptibilidad, el ruido y la disipación no son magnitudes independientes que se puedan optimizar sin restricciones.

Una cavidad no lineal alimentada puede ofrecer dos estados de amplitud. En unidades de su tasa de relajación, el ensayo usa

\[
\dot a=[i(\Delta-K|a|^2)-1/2]a+F,
\qquad F^2=n[(1/2)^2+(\Delta-Kn)^2].
\]

Con \(\Delta=2\), \(K=1\), \(F^2=0.9\), aparecen \(n\simeq0.280735,1.357278,2.361988\). Las ramas inferior y superior son linealmente estables en este modelo; la intermedia es inestable. Los pulsos de escritura llevan de una rama a otra. Se ha integrado la conmutación y comprobado el balance de ocupación.

Este dispositivo es una **memoria alimentada**, diferente de una memoria pasiva con barrera de 60 \(k_BT\). La estabilidad determinista no da una tasa de error bajo ruido. Para esa tasa se necesita el problema de escape estocástico o cuántico en el modelo abierto. La barrera térmica y el presupuesto de R1 no se transfieren automáticamente al ensayo de cavidad.

Una lectura regenerada y un umbral con histéresis dan Comparador y Compuerta. Distribuidor transporta señales y potencia según su matriz. Retardo añade propagación o almacenamiento. Reloj necesita un ciclo límite alimentado o un oscilador con duración y ruido de fase declarados: un lazo pasivo no produce pulsos indefinidamente sin energía inicial o alimentación.

Secuenciador se construye con memoria, comparación y transiciones temporizadas. Selector aplica un criterio de identificación a datos físicos disponibles; no es un filtro de sustancias. La relación con las demás ciencias se mantiene: ninguna puerta lógica sabe algo que sus entradas, su memoria y su programa no contienen.

## MM.12. Química y ensamblaje

En un medio local aproximadamente homogéneo, el Hamiltoniano electrónico no relativista contiene masas \(m_eA\), interacción de Coulomb modificada por \(B\), campos externos y posiciones nucleares. La aproximación de Born–Oppenheimer usa sus autovalores para obtener superficies de energía potencial nuclear.

En el modelo hidrogenoide y en unidades del marco fijado,

\[
a_0\propto B/A,\qquad E_{Ry}\propto A/B^2,
\qquad\delta\ln E_{Ry}=\delta\ln A-2\delta\ln B.
\]

La escala común de masa \(A\) se cancela en ciertas razones locales medidas con materia igualmente acoplada; la constante adimensional electromagnética conserva la variación \(\alpha_{ef}\propto B^{-1}\). No debe confundirse un cambio de unidades del marco con una predicción observable. Gradientes y comparaciones entre regiones requieren el cálculo de transporte y referencia.

Una modificación grande de \(B\) dentro de una molécula altera su química. Para preservar un enlace se exige una tolerancia en la energía y estructura correspondientes; el campo intenso puede necesitar regiones de operación separadas del producto. Las dos funciones de portal dependen del mismo \(s\), de modo que esa separación se debe resolver, no suponer.

Las tasas de una reacción se calculan a partir de superficies, barreras, estados y acoplamientos. La aproximación de estado de transición tiene la forma

\[
k\simeq\kappa_{tr}\frac{k_BT}{h}e^{-\Delta G^\ddagger/(k_BT)},
\]

con factor de transmisión y supuestos definidos. Para un par de estados con el mismo estado de transición y prefactores compatibles, \(k_+/k_-=e^{-\Delta G/(k_BT)}\). El ejemplo numérico incluido verifica esa relación para dos estados abstractos. No pretende ser una cinética del dióxido de carbono.

Separación utiliza diferencias de movilidad, barrera, afinidad o respuesta espectral; Reacción modifica rutas permitidas; Ensamblaje controla posiciones, orientaciones y uniones. Un potencial de control puede cambiar barreras y efectuar trabajo, pero no exime del balance de energía libre ni de los residuos. La velocidad de fabricación requiere tasas y transportes específicos. El producto permanente debe ser estable tras retirar el control.

La biología añade organización funcional e información individual; una teoría de fuerzas no proporciona por sí sola esa información. Los procesos nucleares requieren interacciones y datos nucleares adecuados; el Hamiltoniano electrónico de este capítulo no los deriva.

## MM.13. Preparación, autonomía y control

La ecuación escalar conserva \(\Phi=0\) como solución clásica exacta bajo modulaciones multiplicativas. El inicio necesita fluctuaciones o un estado no nulo. Un bombeo paramétrico puede amplificarlas, pero su tasa debe calcularse con las amplitudes y frecuencias realmente disponibles. La existencia de energía metabólica no demuestra acoplamiento resonante útil.

La preparación de una forma se formula como un problema restringido:

\[
\min_{u(t),\Phi(t)}\int_0^{t_f}P_{fuente}(t)dt,
\]

sujeto a las ecuaciones de campo, límites de actuadores, conservación, región accesible y distancia del estado final a un dominio funcional. El error se mide en energía, geometría y respuesta; no sólo en el dibujo.

Una Semilla preparada puede controlar fuentes locales y copiar estados mediante ondas y realimentación. Para que la receta sea autónoma, la estructura que la sostiene y el controlador deben incluirse en la misma contabilidad. Un perfil impuesto por una función externa representa un ensayo con aparato de preparación, no una demostración de un estado autosostenido.

El primer arranque manual de R1 permanece sin derivación. Completarlo requiere un protocolo físico concreto y verificar que el mismo conjunto de parámetros mantiene estable el entorno ordinario. Añadir un término fuente arbitrario que dibuje cualquier \(\Phi_0\) resolvería formalmente un problema distinto y dejaría sin justificar el mecanismo de ese término.

## MM.14. Cambios operacionales que se desprenden

1. Anclaje usa soporte estructurado o control activo; el condensado homogéneo no recibe un módulo de Young sin derivación.
2. Las tres piezas representan geometría y condiciones modales. La función de cada primordial incluye un estado y terminales declarados.
3. Los nodos incluyen reflexiones e impedancias. La adaptación y la diafonía se calculan.
4. La energía de Reserva se divide entre estructura, carga conservada y exergía accesible. No toda energía ligada es combustible útil.
5. Captación requiere absorción o transferencia inelástica y un ciclo de trabajo; el cambio de impedancia por sí solo no basta.
6. Memoria pasiva y memoria alimentada son realizaciones diferentes, con ruido y consumo diferentes.
7. Los valores R1 se conservan como objetivos de diseño. Se publican por separado los valores deducidos de cada ensayo.
8. La potencia sigue pudiendo ampliarse con infraestructura y paralelismo, pero cada ampliación satisface las propiedades derivadas del mecanismo utilizado.

El resultado es una conexión más precisa entre teoría y catálogo. No es una demostración del conjunto completo: siguen faltando las soluciones tridimensionales preparables de las guías y nodos, los acoplamientos de todos sus terminales, la compatibilidad ambiental y una calibración común que alcance R1.
