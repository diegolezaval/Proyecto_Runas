# Modelo microscópico M1: ecuaciones, estabilidad y correspondencia

Este capítulo conserva las derivaciones de la aproximación M1. La extensión escalar principal M2 y las correspondencias posteriores se desarrollan en los capítulos 08–10 del proyecto.

## M.1. Convenciones y alcance

Se usa la signatura métrica \((-+++ )\), unidades \(c=\hbar=1\) en este capítulo y \(M_{\rm Pl}^{-2}=8\pi G\). En las especificaciones de ingeniería se emplea SI. El campo complejo tiene dimensión de masa, \(s=|\Phi|^2\) dimensión dos y \(U\) dimensión cuatro. La amplitud no es una densidad de energía: esa densidad se calcula con derivadas, potencial y acoplamientos. Una frecuencia angular se convierte mediante \(E=\hbar\omega\), nunca mediante \(h\omega\).

El conjunto común de parámetros es

\[
\Theta=(m_r,\lambda,\kappa,\Lambda,a,b,s_A,s_B,\xi(\mu),c_i(\mu)).
\]

Los \(c_i\) son coeficientes de operadores efectivos a un orden declarado. No se reajusta \(\Theta\) para cada primordial. Las funciones macroscópicas pertenecen a estados, geometrías, terminales y protocolos diferentes de una misma teoría candidata.

La acción del tratado determina ecuaciones de movimiento. No determina por sí sola el procedimiento de fabricación, el estado inicial ni las condiciones de contorno. La especificación R1 añade leyes constitutivas operacionales. La compatibilidad conjunta entre esas leyes y un único \(\Theta\) **no está demostrada**. Esta separación impide confundir una ecuación plausible con una realización física establecida.

## M.2. Variación y balances locales

Escribiendo \(F_g=M_{\rm Pl}^2-2\xi s\), la ecuación gravitatoria clásica es

\[
F_gG_{\mu\nu}=T^{\Phi,0}_{\mu\nu}+T^{\rm EM}_{\mu\nu}+T^m_{\mu\nu}
+\nabla_\mu\nabla_\nu F_g-g_{\mu\nu}\Box F_g+T^{\rm ct}_{\mu\nu},
\]

\[
T^{\Phi,0}_{\mu\nu}=\partial_\mu\Phi^*\partial_\nu\Phi+
\partial_\nu\Phi^*\partial_\mu\Phi-g_{\mu\nu}
(\partial_\rho\Phi^*\partial^\rho\Phi+U),
\]

\[
T^{\rm EM}_{\mu\nu}=B\left(F_{\mu\rho}F_\nu{}^\rho-
\tfrac14g_{\mu\nu}F_{\alpha\beta}F^{\alpha\beta}\right).
\]

\(T^{\rm ct}\) se incorpora de acuerdo con los operadores realmente retenidos; no representa una fuerza libre. Para \(\xi=0\), sin correcciones y en región plana, la densidad escalar positiva es

\[
u_\Phi=|\dot\Phi|^2+|\nabla\Phi|^2+U(s).
\]

Con \(\xi\ne0\), asignar energía entre sector escalar y geométrico depende de la convención; no se debe usar esta expresión aislada como tensor completo. La identidad de Bianchi y las ecuaciones de materia producen la conservación covariante conjunta. No hay una energía gravitatoria local tensorial única para una geometría arbitraria.

En laboratorio, sobre un volumen fijo que incluya estructura y terminales:

\[
\frac{dE_V}{dt}=-\oint_{\partial V}\mathbf S_{\rm tot}\cdot\mathbf n\,dA,
\quad
\frac{d\mathbf p_V}{dt}=-\oint_{\partial V}\boldsymbol\Pi_{\rm tot}\mathbf n\,dA.
\]

Las entradas eléctricas, mecánicas, químicas, luminosas y térmicas son contribuciones de ese flujo. Un soporte transmite reacción; la energía perdida por amortiguamiento pasa a calor. En un volumen móvil se incluyen el transporte debido al borde y su trabajo. El balance de entropía es independiente:

\[
\dot S_V=\sum_k\frac{\dot Q_k}{T_k}+\dot S_{\rm materia}+\dot S_i,
\qquad \dot S_i\ge0.
\]

La conservación de energía es el primer principio termodinámico; la restricción sobre \(\dot S_i\) pertenece al segundo.

## M.3. Acoplamientos y efectos simultáneos

Para las funciones adoptadas:

\[
\alpha_m(s)=\frac{a s_A}{(s+s_A)^2},\qquad
\frac{B'}B=\frac{4b s_B(s_B-s)}{(s+s_B)^3}.
\]

En una región aproximadamente homogénea, al normalizar el término cinético electromagnético, \(\alpha_{\rm EM,ef}\propto B^{-1}\) si la carga del lagrangiano se mantiene fija. Por tanto,

\[
\delta\ln\alpha_{\rm EM}=-\delta\ln B.
\]

Modificar \(B\) afecta espectros, enlaces, respuesta dieléctrica y química; no sólo la luz de un terminal. El extremo de \(B\) en \(s=s_B\) hace que \(B'=0\), pero no que \(B=1\). Una ventana con poca sensibilidad diferencial no garantiza una materia ordinaria intacta. Análogamente, \(A\) modifica la respuesta de las masas en el marco usado. Todo diseño debe calcular ambos efectos y los gradientes que ejercen fuerzas.

Para que una operación preserve un proceso químico, la condición pertinente es \(|\delta E_{\rm enlace}|\ll\Delta E_{\rm tolerada}\), con tolerancia específica del proceso. No se adopta un porcentaje universal válido para electrónica, organismos y reacciones nucleares. Un perfil que no proporcione esa evaluación no está habilitado para la aplicación correspondiente.

## M.4. Vacío, carga y estructuras neutras

La condición \(\lambda^2\Lambda^2<4\kappa m_r^2\) mantiene \(U(s)>0\) para \(s>0\). Una estructura estática, aislada y localizada, sustentada únicamente por gradiente escalar y este potencial en tres dimensiones no tiene un mínimo de energía por cambio de escala. Si \(\Phi_\ell(\mathbf x)=\Phi(\mathbf x/\ell)\), entonces \(E(\ell)=\ell E_\nabla+\ell^3E_U\); su derivada no puede anularse con ambos términos positivos.

Así, el dibujo cerrado no estabiliza por sí mismo una red neutra. Las realizaciones operacionales usan estados oscilantes mantenidos, confinamiento, terminales y realimentación con energía contabilizada. Al cortar alimentación dejan de estar garantizadas. Las configuraciones de carga no nula pueden admitir estabilidad a carga fija; desde un sistema inicialmente neutro, la carga opuesta debe quedar en otro lugar. Dos objetos de cargas opuestas no son automáticamente una memoria estable: pueden interactuar y aniquilarse.

Se distinguen tres pruebas: existencia de una solución, estabilidad frente a perturbaciones y accesibilidad mediante preparación. Ninguna sustituye a las otras.

## M.5. Ensayo radial reproducible

Para el sector aislado \(a=b=\xi=0\), se adopta

\[
\Phi=\frac{m_r}{\sqrt\lambda}f(x)e^{i\omega t},\quad
x=m_rr,\quad \hat\omega=\omega/m_r,
\quad \hat U=f^2-f^4+f^6.
\]

El coeficiente séxtico adimensional es \(g_6=\kappa m_r^2/(\lambda^2\Lambda^2)=1\). Se obtiene

\[
f''+\frac2x f'=(1-\hat\omega^2)f-2f^3+3f^5,
\qquad f'(0)=0,\quad f(\infty)=0.
\]

El intervalo de existencia candidato es \(\sqrt{3/4}<\hat\omega<1\). El solucionador utiliza dos dominios y dos tolerancias para comprobar que la frontera artificial no controla el resultado. Se registran amplitud central, residuo, energía, carga y perfil radial. Las integrales son

\[
I=4\pi\int x^2f^2dx,\ G=4\pi\int x^2(f')^2dx,\ V=4\pi\int x^2\hat U\,dx,
\]

\[
\hat Q=2\hat\omega I,\qquad \hat E=\hat\omega^2I+G+V,
\qquad G+3V-3\hat\omega^2 I=0.
\]

En unidades físicas \(E=(m_r/\lambda)\hat E\), \(Q=\hat Q/\lambda\); así \(E/(m_rQ)=\hat E/\hat Q\). El ensayo no fija \(m_r\) en eV, ni transforma sus resultados en julios de Reserva. La comprobación \(E<m_rQ\) compara con cuantos libres de la misma carga; no demuestra estabilidad espectral completa ni estabilidad de redes.

Los resultados efectivos están en `validacion/microscopia.json` y en la sección de resultados generada. El perfil permite repetir la integración con otra malla. Este ensayo es una comprobación del sector escalar, no de las veinticuatro funciones.

## M.6. Teoría efectiva y control del truncamiento

Un régimen perturbativo requiere \(k/\Lambda\ll1\), \(|\Phi|/\Lambda\ll1\), \(|\partial\Phi|/\Lambda^2\ll1\), coeficientes de Wilson controlados y ausencia de nuevos polos en la banda conservada. Los cocientes pequeños son necesarios; sin cotas de los coeficientes omitidos no proporcionan una cota completa del error.

En el ensayo, \(m_r/\Lambda=10^{-3}\), \(\lambda=10^{-3}\), \(\kappa=1\), de modo que \(|\Phi|/\Lambda=0.03162|f|\). Un operador \(c_8s^4/\Lambda^4\), con \(c_8\) de orden uno, está suprimido frente al séxtico por \((c_8/\kappa)s/\Lambda^2\); esta comparación no acota términos con coeficientes anormalmente grandes. La elección \(a=b=0\) hace el ensayo limpio, pero elimina precisamente el intercambio requerido para captación y preparación manual. No se extrapola su éxito a R1.

## M.7. Correspondencia microscópica y macroscópica

Una derivación operacional procede mediante proyección sobre modos de un estado preparado:

\[
\Phi(\mathbf x,t)=\Phi_0(\mathbf x,t;\lambda_a)
+\sum_nq_n(t)u_n(\mathbf x;\lambda_a)+\delta\Phi_\perp.
\]

Aquí \(\lambda_a\) son controles geométricos, distintos del acoplamiento \(\lambda\). Integrar la acción sobre el espacio produce masas modales, rigideces y acoplamientos como integrales de solapamiento. Integrar modos ambientales produce memoria, amortiguamiento y ruido; la aproximación markoviana sólo es válida si sus tiempos de correlación son suficientemente cortos.

La geometría define condiciones de contorno y conectividad, no el significado de una palabra. Para asociar una primordial a una función deben exhibirse: estado base, espectro, puertos observables, respuesta a estímulos, ganancias, saturaciones y protocolo de preparación. Dos dibujos isomorfos pueden comportarse de forma diferente si sus longitudes, curvaturas, terminales o estados difieren. La sola topología no identifica el dispositivo.

La controlabilidad local se estudia sobre \(\dot x=Ax+Bu\), por ejemplo mediante el rango de \([B,AB,\ldots,A^{n-1}B]\); la observabilidad usa \([C;CA;\ldots;CA^{n-1}]\). Rango completo no garantiza accesibilidad global bajo límites de energía o actuadores. El problema de preparación es un control óptimo restringido, con coste, tiempo y trayectorias físicamente admisibles.

## M.8. Estado de cierre

El sistema queda especificado como una arquitectura operacional condicionada a leyes constitutivas R1. Quedan formuladas las ecuaciones microscópicas, sus condiciones de validez y una prueba radial reproducible. Permanecen sin resolver: un conjunto \(\Theta\) que realice conjuntamente R1; soluciones tridimensionales de los módulos; su espectro completo; coeficientes de transporte obtenidos de esas soluciones; y el protocolo microscópico de primera preparación manual. Afirmar que estos puntos están demostrados sería atribuir a los cálculos un resultado que no contienen.
