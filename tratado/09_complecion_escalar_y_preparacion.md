# Extensión microscópica M2: mediador, preparación y motor

## M2.1. Cambio de teoría y alcance

La versión M1 utilizaba un potencial sextico efectivo. M2 introduce **un único mediador escalar real \(\chi\)**, común a todos los dispositivos, para obtener ese potencial mediante eliminación de un grado de libertad. No se añade un campo distinto para cada función. La simetría global U(1) de \(\Phi\) se conserva; \(\chi\) es neutro bajo ella.

La extensión resuelve un problema preciso: el origen clásico de la atracción cuártica y la estabilización del potencial. No resuelve por sí misma los portales a materia, el arranque manual ni el diseño de todos los estados tridimensionales. «Compleción» en este capítulo se refiere al **sector potencial escalar**, no a una teoría cuántica completa de todos los sectores.

Los resultados de MM.3–MM.5 basados en \(\hat U=\hat s-\hat s^2+\hat s^3\) corresponden a M1. En M2 se sustituye ese potencial por el que sigue y se incluye la dinámica del mediador. Las identidades generales de conservación, proyección, fuerza y respuesta permanecen aplicables con el Hamiltoniano correspondiente.

## M2.2. Acción y potencial comunes

En laboratorio plano, la parte escalar de M2 es

\[
\mathcal L_{M2}=-\partial_\mu\Phi^*\partial^\mu\Phi
-\tfrac12\partial_\mu\chi\partial^\mu\chi-V(s,\chi),
\]

\[
V=m_r^2s+\lambda_0s^2+\tfrac12M_\chi^2\chi^2
+g_\chi\chi s+\tfrac12h_\chi\chi^2s.
\]

\(g_\chi\) tiene dimensión de masa; \(\lambda_0,h_\chi\) son adimensionales. Se toman \(\lambda_0>0\), \(h_\chi>0\), \(M_\chi^2>0\). Los términos \(-B(s)F^2/4\) y \(S_m[A^2(s)g,\psi]\) se mantienen como portales efectivos de M1. Sus parámetros todavía necesitan una identificación conjunta; la ampliación del potencial no los determina.

Las ecuaciones escalares, antes de añadir los términos de portal, son

\[
\Box\Phi-[m_r^2+2\lambda_0s+g_\chi\chi+\tfrac12h_\chi\chi^2]\Phi=0,
\]

\[
\Box\chi-M_\chi^2\chi-g_\chi s-h_\chi\chi s=0.
\]

El tensor total añade el término canónico de \(\chi\) y el potencial compartido se cuenta una sola vez. El intercambio de energía entre los dos campos es interno. La carga U(1) procede de \(\Phi\); el mediador no permite destruirla.

Este potencial tiene operadores de dimensión no mayor que cuatro. Para un tratamiento cuántico renormalizado hay que incluir todos los contraterminos permitidos, incluidos términos de \(\chi\) que no estén protegidos por una simetría. El ensayo fija a cero los coeficientes adicionales en la aproximación clásica; no demuestra que permanezcan nulos al cambiar de escala. Los portales no polinómicos continúan limitando el carácter efectivo del modelo completo.

## M2.3. Eliminación exacta del mediador estático

A \(s\) fijo, el mínimo respecto de \(\chi\) es

\[
\chi_*(s)=-\frac{g_\chi s}{M_\chi^2+h_\chi s}.
\]

El potencial se puede escribir como una suma positiva más el potencial reducido:

\[
V=\tfrac12(M_\chi^2+h_\chi s)[\chi-\chi_*(s)]^2+U_{ef}(s),
\]

\[
U_{ef}=m_r^2s+\lambda_0s^2-
\frac{g_\chi^2s^2}{2(M_\chi^2+h_\chi s)}.
\]

Al expandir para \(h_\chi s/M_\chi^2\ll1\):

\[
U_{ef}=m_r^2s-\lambda s^2+
\frac{g_\chi^2h_\chi}{2M_\chi^4}s^3+O(s^4),
\quad \lambda=\frac{g_\chi^2}{2M_\chi^2}-\lambda_0.
\]

Así, el signo negativo del término cuártico y el positivo del sextico tienen un origen común. El coeficiente sextico no se elige después de forma independiente.

Se adopta para el ensayo

\[
\lambda_0=99\lambda,\quad M_\chi=100m_r,\quad
 g_\chi=M_\chi\sqrt{200\lambda},\quad
 h_\chi=\frac{\lambda M_\chi^2}{100m_r^2}.
\]

Con \(\hat s=\lambda s/m_r^2\), resulta exactamente

\[
\hat U_{ef}=\hat s-\hat s^2+
\frac{\hat s^3}{1+\hat s/100}.
\]

El mínimo de \(\hat U_{ef}/\hat s\) es aproximadamente 0.74874213, situado en \(\hat s\simeq0.50378153\). Es positivo. La descomposición cuadrática anterior demuestra entonces que el potencial completo no toma valores menores que el vacío. También proporciona una ventana candidata de frecuencias para estados cargados ligados.

La coincidencia con el sextico es controlada en amplitud por \(\hat s/100\). La eliminación dinámica añade términos derivados de \(\chi_*(s)\), por ejemplo \(-\tfrac12[\chi_*'(s)]^2(\partial s)^2\). Una masa grande no autoriza a descartar esos términos sin evaluar su coeficiente. Este punto se comprueba con el modelo de dos campos completo.

## M2.4. Solución radial de ambos campos

Definimos \(f=\sqrt\lambda\,\Phi_{amplitud}/m_r\), \(z=\sqrt\lambda\,\chi/m_r\), \(x=m_rr\), \(\hat M=100\), \(\hat g=100\sqrt{200}\), \(\hat h=100\). Para \(\Phi\propto e^{i\omega t}\), el sistema radial es

\[
f''+\frac2x f'=\left[1-\hat\omega^2+198f^2+
\hat g z+\tfrac12\hat h z^2\right]f,
\]

\[
z''+\frac2x z'=\hat M^2z+\hat g f^2+\hat h zf^2,
\]

con derivadas nulas en el origen y campos que decaen en el borde remoto. La integración incluye los gradientes de ambos campos.

Para \(\hat\omega=0.9\), se obtienen

| Magnitud adimensional | Resultado aproximado |
|---|---:|
| Amplitud central \(f(0)\) | 0.74601921 |
| Mediador central \(z(0)\) | −0.07827167 |
| Energía \(\hat E\) | 2525.65891 |
| Carga \(\hat Q\) | 2745.77392 |
| \(\hat E/\hat Q\) | 0.91983498 |
| Residuo virial relativo | \(1.1\times10^{-11}\) |
| Cambio relativo de energía entre dominios | \(2.0\times10^{-9}\) |

Los dominios usados tienen radios 50 y 60 en unidades \(1/m_r\). La solución reducida que conserva sólo \(U_{ef}\) y omite la cinética inducida del mediador difiere en energía alrededor de 0.943 % **a la misma frecuencia**, y tiene otra carga. Esa diferencia no compara energías a carga fija; mide el error de esa simplificación para el problema resuelto.

El resultado verifica existencia numérica, balances y convergencia de esta familia radial. No demuestra estabilidad espectral completa, estabilidad de uniones ni que un dibujo pueda prepararla. Los perfiles y el código permiten repetir y ampliar la comprobación.

### Operador de perturbaciones de M2

Para \(\Phi=e^{i\omega t}[f+(u+iv)/\sqrt2]\) y \(\chi=\chi_0+\zeta\), el sistema lineal aislado es

\[
\ddot u-2\omega\dot v+L_u u+C_{u\chi}\zeta=0,\quad
\ddot v+2\omega\dot u+L_vv=0,\quad
\ddot\zeta+L_\chi\zeta+C_{u\chi}u=0,
\]

\[
L_v=-\nabla^2+m_r^2+2\lambda_0f^2+g_\chi\chi_0+
\tfrac12h_\chi\chi_0^2-\omega^2,\quad L_u=L_v+4\lambda_0f^2,
\]

\[
L_\chi=-\nabla^2+M_\chi^2+h_\chi f^2,\qquad
C_{u\chi}=\sqrt2f(g_\chi+h_\chi\chi_0).
\]

La notación \(L_vv\) significa \(L_v\,v\). Para un sector angular de índice \(\ell\), el operador radial incluye \(\ell(\ell+1)/r^2\). Éste es el problema que debe resolver una prueba espectral de M2; no se reemplaza por el Hessiano de M1. El mediador pesado puede eliminarse de forma aproximada sólo si las frecuencias y gradientes lo permiten; su eliminación produce una respuesta dependiente de frecuencia.

## M2.5. Preparación paramétrica: umbral comprobable

Para un modo neutro de amplitud \(q\), una modulación obtenida de los portales puede reducirse, cerca del inicio y bajo sus hipótesis, a

\[
\ddot q+2\gamma\dot q+\omega_0^2[1+h_p\cos(2\omega_0t)]q=0.
\]

El exponente de crecimiento aproximado en resonancia es \(\mu\simeq h_p\omega_0/4-\gamma\), con modulación pequeña. La versión con desintonía necesita el problema de Floquet correspondiente. El paquete integra la matriz fundamental durante un periodo, sin inferir crecimiento sólo del aspecto de una curva.

Con \(\omega_0=1\), \(\gamma=0.02\), el caso \(h_p=0.04\) decae y el caso \(h_p=0.12\) crece. La no linealidad debe saturar ese crecimiento dentro de un dominio estable antes de convertirlo en preparación útil. El ensayo es lineal y no demuestra dicha saturación.

El bombeo preserva la simetría del campo si procede de una modulación multiplicativa de masa. Una solución exactamente nula sigue siendo nula; fluctuaciones físicas proporcionan la semilla de amplitud. Nada de esto establece que el cuerpo produzca \(h_p\) y \(\omega_0\) adecuados: ése sigue siendo el cálculo específico que falta para el primer arranque manual.

## M2.6. Motor microscópico para convertir calor radiativo en trabajo

Para precisar qué requiere Captador solar, se añade un **modelo de ciclo**, sin afirmar todavía que sus niveles hayan sido obtenidos de M2. Un centro tiene energías \(0,E_c,E_h\). La transición \(0\leftrightarrow E_h\) se acopla al reservorio luminoso; \(0\leftrightarrow E_c\), al sumidero; \(E_h\leftrightarrow E_c\), a un campo coherente de trabajo con energía de cuanto \(E_w=E_h-E_c\).

Con reservorios térmicos ideales, \(n_j=[\exp(E_j/k_BT_j)-1]^{-1}\). Las tasas térmicas de subida y bajada son \(\gamma_j n_j\) y \(\gamma_j(n_j+1)\), respetando balance detallado. Tras eliminar coherencias bajo una aproximación declarada, la transición inducida coherentemente puede representarse por tasas estimuladas simétricas \(k_w\). Se conserva su interpretación como intercambio con el campo de trabajo; un baño caliente añadido con tasas simétricas no sería automáticamente trabajo.

La comprobación también resuelve la ecuación de Lindblad estacionaria completa para la matriz de densidad de tres niveles, con Hamiltoniano de trabajo \(H_w/\hbar=\Omega(|1\rangle\langle2|+|2\rangle\langle1|)\) en el marco resonante. Sin desfasaje puro adicional,

\[
\Gamma_{12}=\tfrac12[\gamma_h(n_h+1)+\gamma_c(n_c+1)],\qquad
k_w=2\Omega^2/\Gamma_{12}.
\]

Eliminar la coherencia en el estado estacionario da exactamente las ecuaciones de poblaciones usadas para este modelo. Usar esa eliminación durante un transitorio requiere además una separación de tiempos. La prueba compara poblaciones, positividad de la matriz de densidad y potencia extraída del Hamiltoniano coherente, evitando identificar una pérdida térmica arbitraria con trabajo.

Si \(p_0,p_1,p_2\) son las poblaciones, las corrientes son

\[
J_h=\gamma_h[n_hp_0-(n_h+1)p_2],\qquad
J_c=\gamma_c[(n_c+1)p_1-n_cp_0],
\]

\[
J_w=k_w(p_2-p_1).
\]

En estado estacionario \(J_h=J_c=J_w=J\), por lo que

\[
\dot Q_h=E_hJ,\quad \dot Q_c=E_cJ,\quad
P_w=(E_h-E_c)J,\quad \eta_{ciclo}=1-E_c/E_h.
\]

La producción de entropía es \(J(E_c/T_c-E_h/T_h)\). El régimen motor exige la desigualdad compatible con Carnot.

El ensayo toma \(E_h=2\) eV, \(E_c=0.4\) eV, \(T_h=5778\) K y \(T_c=300\) K. Al resolver las poblaciones obtiene corriente motora positiva, conservación de energía y entropía positiva; la eficiencia del ciclo es 80 %. Las tasas se expresan en una unidad temporal común adoptada, por lo que no se deduce una potencia por metro cuadrado.

Este 80 % es consecuencia del cociente de niveles elegido. No es el 80 % de todo el captador R1: aún faltan la realización de los niveles, la absorción angular y espectral, el campo coherente, los canales de pérdida y los servicios. La radiación solar no se sustituye sin más por un baño isotrópico que llene todos los modos. La temperatura utilizada es una idealización de brillo del ejemplo, no un balance completo de radiación incidente.

## M2.7. Lo establecido y lo que permanece abierto

M2 proporciona un origen explícito del potencial efectivo y una solución numérica del sistema que lo origina. La correspondencia añade respuesta de grafos, memoria alimentada, umbral paramétrico, fuerzas de portal, balance cinético y un motor microscópico condicionado. Estos resultados sustituyen varios supuestos verbales por cálculos verificables.

Todavía no existe en el paquete un conjunto único de parámetros y estados que realice simultáneamente las 24 funciones y todas las metas R1. En particular, no se han resuelto las guías y uniones tridimensionales con sus terminales, su preparación autónoma y su comportamiento ambiental. Declarar cerrados esos puntos exigiría cálculos y resultados adicionales, no un cambio de redacción.
