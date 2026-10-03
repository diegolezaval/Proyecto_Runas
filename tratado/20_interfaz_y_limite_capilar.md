# 20 · De los campos a la interfaz y al régimen capilar

## 20.1. Alcance y clasificación

Se mantiene el sector escalar clásico aislado de M2, con el mismo conjunto Θ de `datos/theta_comun.json`. No se añaden paredes materiales, disipación, fuerzas externas ni parámetros propios de una primordial. La existencia física del sector interactuante completo sigue siendo una **hipótesis**; las identidades siguientes son **resultados analíticos condicionados a la acción M2**. Los perfiles y espectros son **resultados numéricos**. Las leyes capilares son **aproximaciones asintóticas**, contrastadas con esos perfiles y espectros. No constituyen una validación experimental ni un dispositivo preparado y controlable.

Esta derivación conecta explícitamente potencial, ecuación de estado, tensión superficial, equilibrio de objetos finitos y modos. La interfaz es una solución de los campos; su tensión no es un valor asignado para sostener una geometría.

## 20.2. Variables y coexistencia

Se usan las unidades adimensionales del capítulo 13, con \(\Phi=e^{i\mu t}f\), \(\chi=z\), \(s=f^2\). En este capítulo \(\mu\) designa la frecuencia del estado y \(\varpi\) una frecuencia de perturbación. El potencial común es

\[
 V=f^2+99f^4+5000z^2+Gzf^2+50z^2f^2,
 \qquad G=100\sqrt{200}.
\]

Minimizarlo respecto de un mediador **homogéneo** da exactamente

\[
 z_*(s)=-\frac{Gs}{10000+100s},\qquad
 U(s)=s-s^2+\frac{s^3}{1+s/100}.
\]

Esta eliminación es exacta para el potencial homogéneo. Sustituirla en una interfaz con gradientes es una aproximación distinta. La coexistencia con vacío satisface

\[
 U'(s_0)=\mu_0^2=\frac{U(s_0)}{s_0},\qquad
 s_0=0.5037815259212,\quad\mu_0=0.8652988688304.
\]

Para este benchmark se verifica la factorización

\[
 W_{\rm eff}(s)=U(s)-\mu_0^2s
 =\frac{0.99\,s(s-s_0)^2}{1+s/100}\geq0.
\]

Además,

\[
 V(f,z)-\mu_0^2f^2=W_{\rm eff}(f^2)
 +\frac{10000+100f^2}{2}[z-z_*(f^2)]^2.
\]

Por tanto, los dos extremos de la interfaz son mínimos degenerados del potencial a frecuencia fija. No son dos vacíos estáticos de la teoría: uno contiene un campo complejo rotante y carga.

## 20.3. Ecuación de estado e inercia derivadas

Convenciones corregidas en E01: signatura (−+++), fase e^{+iμt}, carga positiva para μ>0. La expresión histórica con signos de otra signatura permanece en el ZIP 4.1 archivado. Esta corrección no cambia las ecuaciones ni las cifras de los solucionadores. Véase el capítulo 23.

Escribiendo \(\Phi=\sqrt{s}\,e^{i\theta}\), el límite de gradientes lentos tiene

\[
 X=-\partial_\alpha\theta\partial^\alpha\theta,\qquad
 P(X)=Xs(X)-U(s(X)),\qquad U'(s)=X.
\]

La derivación requiere la rama local con \(U''>0\) y que los modos de amplitud puedan eliminarse a esas escalas. No vale dentro de toda la interfaz ni cerca de una pérdida de estabilidad de la rama. De la acción se obtienen

\[
 j^\alpha=-2s\partial^\alpha\theta,\quad
 T^{\alpha\beta}=2s\partial^\alpha\theta\partial^\beta\theta+g^{\alpha\beta}P,
\]
\[
 n=2\mu s,\quad p=\mu^2s-U(s),\quad
 \epsilon=\mu^2s+U(s),\quad
 w_b\equiv\epsilon+p=2\mu^2s,
\]
\[
 c_s^2=\frac{sU''}{sU''+2\mu^2}.
\]

En coexistencia, \(n_0=0.8718431690345\), \(w_{b0}=0.7544049079630\) y \(c_s^2=0.2503136782638\). La densidad de inercia de un flujo lento es **la entalpía \(w_b\)** en unidades \(c=1\), porque \(T^{0i}=w_b v^i+O(v^3)\). No se sustituye por la densidad de carga ni se introduce un factor de ajuste. En SI la densidad de masa inercial es \(w_b/c^2\).

## 20.4. Pared plana de ambos campos

La interfaz plana en coexistencia satisface

\[
 f''=(1-\mu_0^2+198f^2+Gz+50z^2)f,
 \qquad z''=10000z+Gf^2+100zf^2,
\]

con \((f,z)\to(\sqrt{s_0},z_*(s_0))\) a la izquierda y \((0,0)\) a la derecha. Multiplicar por las derivadas y sumar da la primera integral

\[
 f'^2+\tfrac12z'^2=V-\mu_0^2f^2\equiv W.
\]

La tensión superficial es el exceso de energía **a potencial químico fijo**, o exceso de \(E-\mu_0 Q\) por área:

\[
 \tau=\int_{-\infty}^{\infty}(f'^2+\tfrac12z'^2+W)\,dx
 =\int_{-\infty}^{\infty}(2f'^2+z'^2)\,dx.
\]

El segundo integrando es la diferencia entre tensiones normal y tangencial. Así, \(\tau\) conecta un perfil microscópico con una fuerza macroscópica. El cálculo completo da

\[
 \boxed{\tau\simeq0.1265742605132}.
\]

La diferencia relativa entre las dos últimas resoluciones es aproximadamente \(3\times10^{-12}\); no es una cota certificada del error total. El residuo máximo de la primera integral de la última solución es \(1.1\times10^{-13}\).

Hay además un control variacional independiente. Descartar el término no negativo del mediador y su gradiente da una cota inferior al ínfimo de la tensión. Restringir las curvas a \(z=z_*(f^2)\) da una cota superior de prueba:

\[
 2\int_0^{\sqrt{s_0}}\sqrt{W_{\rm eff}(f^2)}\,df
 \leq\tau_{\min}\leq
 2\int_0^{\sqrt{s_0}}\sqrt{Z(f)W_{\rm eff}(f^2)}\,df,
\]
\[
 Z(f)=1+\tfrac12\left(\frac{dz_*}{df}\right)^2
 =1+\frac{2f^2G^2M^4}{(M^2+Hf^2)^4},\qquad H=100.
\]

Los valores son 0.1261560149751 y 0.1265742687755. El perfil completo queda entre ambos. La coincidencia casi completa con la cota de prueba explica por qué la aproximación adiabática con cinética inducida funciona bien aquí. No demuestra unicidad ni certifica que la solución numérica sea el mínimo global. Descartar también la cinética inducida subestima la tensión en aproximadamente 0.33 %.

## 20.5. Equilibrio curvo sin presión impuesta

Sea \(d=3\) para una esfera y \(d=2\) para la sección de un tubo recto, con \(S_2=4\pi\), \(S_1=2\pi\). La energía y carga del segundo caso son por longitud. Definimos

\[
 I=S_{d-1}\int r^{d-1}f^2\,dr,\quad Q=2\mu I,
\]
\[
 E=\mu^2 I+S_{d-1}\int r^{d-1}
 [f'^2+\tfrac12z'^2+V]dr.
\]

La virial exacta es \((d-2)T+d(U_{\rm int}-\mu^2 I)=0\), donde \(T\) es la energía de gradientes y \(U_{\rm int}\) la integral de \(V\). La conservación del tensor de tensiones da, también exactamente,

\[
 T_{rr}=f'^2+\tfrac12z'^2-(V-\mu^2f^2),\qquad
 \frac{dT_{rr}}{dr}=-\frac{d-1}{r}(2f'^2+z'^2),
\]
\[
 T_{rr}(0)-T_{rr}(L)
 =(d-1)\int_0^L\frac{2f'^2+z'^2}{r}\,dr.
\]

El integrando es regular en el origen. En el límite de interfaz delgada, \(T_{rr}(0)\to p\), \(T_{rr}(\infty)=0\), y se obtiene la ley de Laplace, sin agregar una fuerza:

\[
 p\simeq\frac{(d-1)\tau}{R}.
\]

Para comparar objetos finitos se usa el radio equimolar **definido** por

\[
 U'(s_b)=\mu^2,\qquad R_e=\left(\frac{dI}{S_{d-1}s_b}\right)^{1/d}.
\]

No se identifica exactamente con el radio de tensión superficial; su diferencia produce correcciones de curvatura. A carga grande,

\[
 R_Q=\left(\frac{dQ}{S_{d-1}n_0}\right)^{1/d},\qquad
 E=\mu_0Q+S_{d-1}\tau R_Q^{d-1}+O(R_Q^{d-2}).
\]

Una sola tensión predice ambas familias. Se verifican diez estados, con radios de norma \(R_N=8,16,32,64,128\) en ambas dimensiones. \(R_N\) parametriza \(I=S_{d-1}s_0R_N^d/d\); es una condición de estado, no un nuevo parámetro fundamental. Los residuos de virial, norma y balance de tensiones se conservan en JSON. La derivada de estados próximos verifica además \(dE/dQ=\mu\).

## 20.6. Modos capilares

A velocidades pequeñas, longitudes de onda grandes respecto del espesor de interfaz y frecuencias suficientemente menores que \(c_s/R\), el flujo interior es casi incompresible. Con \(\mathbf v=\nabla\psi\), se tienen \(\nabla^2\psi=0\), \(w_{b0}\partial_t\psi=-\delta p\) y la condición cinemática \(\partial_t\eta=\partial_r\psi\). Las condiciones de interfaz proceden de la conservación del tensor anterior.

Para una esfera, \(\psi\propto r^\ell Y_{\ell m}\) y
\(\delta p=\tau(\ell-1)(\ell+2)\eta/R^2\). Resulta

\[
 \boxed{\varpi_\ell^2\simeq
 \frac{\tau}{w_{b0}R^3}\ell(\ell-1)(\ell+2)},\qquad\ell\geq2.
\]

\(\ell=1\) es la traslación, no un oscilador de restitución. \(\ell=0\) necesita compresibilidad y la restricción de carga. No queda cubierto por esta fórmula.

Para un tubo axisimétrico, \(\psi\propto I_0(kr)e^{ikz+\sigma t}\),
\(\delta p=\tau(k^2-R^{-2})\eta\). Por tanto,

\[
 \boxed{\sigma^2\simeq\frac{\tau}{w_{b0}R^3}
 x(1-x^2)\frac{I_1(x)}{I_0(x)}},\qquad x=kR.
\]

Hay crecimiento para \(0<x<1\). El umbral tiende a \(k_cR=1\); cuando \(x\ll1\),

\[
 \sigma^2\simeq\frac{\tau k^2}{2w_{b0}R},\qquad
 c_L^2\simeq-\frac{\tau}{2w_{b0}R}.
\]

La velocidad de sonido del interior homogéneo tiene cuadrado positivo, mientras que la respuesta longitudinal del **tubo con sección libre** tiene cuadrado negativo. Son perturbaciones diferentes: la segunda permite redistribuir carga y cambiar el área de la interfaz. No hay contradicción entre ambos resultados. La derivada \(q/(\mu\,dq/d\mu)\) contrasta independientemente ese signo y su escala.

## 20.7. Contraste con el espectro microscópico

Se diagonaliza el generador completo de las tres perturbaciones reales, incluyendo el mediador y los términos giroscópicos del capítulo 14. No se inserta la fórmula capilar en ese operador. Para esferas se estudia \(\ell=2\); para tubos, \(kR_e=0.6\). Se usan cinco pasos entre 0.1 y 0.00625 y extrapolación de los autovalores cuadrados en \(h^2\). Se publican también las muestras gruesas.

| \(R_N\) | Error de frecuencia esférica respecto de la predicción | Error de crecimiento tubular | \(k_cR_e\) tubular |
|---:|---:|---:|---:|
| 16 | −1.2823 % | −4.1932 % | 0.951094 |
| 32 | −0.6109 % | −2.4392 % | 0.972355 |
| 64 | −0.3076 % | −1.3092 % | 0.985302 |
| 128 | −0.1540 % | −0.6778 % | 0.992419 |

Los errores disminuyen al aumentar el radio, como requiere la aproximación. Para \(R_N=128\), la frecuencia cuadrupolar extrapolada es aproximadamente 0.000801901 y la tasa tubular 0.0000935785. Sus diferencias entre dos extrapolaciones sucesivas son inferiores a \(2\times10^{-7}\) y \(5\times10^{-6}\), respectivamente, en términos relativos. Son estimaciones de discretización, no intervalos rigurosos.

A ese radio, una malla \(h\simeq0.1\) reduce la frecuencia esférica calculada a 0.000708698 e infla el crecimiento tubular a 0.000143501. Un residuo algebraico pequeño de un autovector no detecta este error espacial. La coincidencia aislada entre una muestra y la fórmula tampoco demuestra convergencia.

La comparación de dominio se realiza a \(R_N=64\), extendiendo el margen de vacío de 30 a 40 y refinando la solución de fondo. El cambio espectral es menor que \(2\times10^{-7}\) relativo. En esferas se informa por separado el pequeño cambio de \(h=L/(N+1)\) entre las dos cajas. No se afirma una cota uniforme del error de dominio para todos los radios ni una clasificación de todo el espectro.

![Convergencia al régimen capilar](../graficos/M2_capilaridad.svg)

## 20.8. Reproducción, unidades y límites

`herramientas/capilaridad_m2.py` lee Θ común y `datos/ensayo_capilaridad.json`. Guarda perfiles, resultados y configuración en `validacion/capilaridad/`. Para la pared se fija la libertad de traslación mediante una condición integral de fase; la frecuencia es una incógnita auxiliar de la caja finita que converge a \(\mu_0\). Esa condición selecciona el origen de coordenadas; no añade una pared física ni una fuerza. Los valores de extremo son los estados asintóticos, aproximados en una caja cuyo tamaño se refina.

Para esferas y tubos se fija la norma y se resuelve \(\mu\) como incógnita. La solución adiabática inicializa Newton, pero las soluciones publicadas satisfacen **ambas ecuaciones**. Ni el inicializador capilar ni el radio de norma determinan de antemano la presión, energía o frecuencia obtenidas.

Con \(E_0=mc^2/\lambda\), \(\ell_0=\hbar c/(mc^2)\), \(t_0=\hbar/(mc^2)\), se recuperan:

| Magnitud | Factor físico multiplicativo |
|---|---|
| Radio | \(\ell_0\) |
| Frecuencia o tasa | \(t_0^{-1}\) |
| Energía esférica | \(E_0\) |
| Energía tubular por longitud | \(E_0/\ell_0\) |
| Tensión superficial | \(E_0/\ell_0^2\) |
| Presión y entalpía volumétrica | \(E_0/\ell_0^3\) |
| Carga esférica | \(1/\lambda\) |
| Carga tubular por longitud | \(1/(\lambda\ell_0)\) |

La variación de carga prueba sensibilidad al **estado**, no robustez frente a todas las constantes de Θ. La variación de \(m\) y \(\lambda\) en esta familia cambia las escalas anteriores; no representa un barrido independiente de \(g,h,M,\lambda_0\). Permanecen abiertos ese barrido, la interfaz a temperatura finita, correcciones cuánticas, curvatura de orden superior, modos no axisimétricos de tubos, dinámica no lineal de fragmentación y estabilidad orbital de las gotas. La fórmula capilar no debe extrapolarse a longitud de onda arbitrariamente corta ni usarse para inferir una velocidad de frente: fuera de su régimen manda M2.

El mecanismo capilar explica y extiende el resultado negativo de P-04; no lo revoca. El resultado es un puente microscópico–macroscópico dentro del sector común. Preparación, contactos materiales, pérdidas, control y transducción medible continúan siendo eslabones diferentes.

## 20.9. Referencias y procedencia de las fórmulas

Qian Chen, [Hydrodynamic and Rayleigh–Plateau instabilities of Q-strings](https://arxiv.org/html/2412.09815v2), estudia la analogía capilar en un modelo de campo complejo con potencial séxtico. Ese trabajo sirve como contraste primario del mecanismo y del umbral, no como dato numérico del M2 de dos campos. Aquí la tensión se calcula con ambos gradientes y la inercia se obtiene de su tensor de energía–momento, sin ajuste.

J. Heeck, A. Rajaraman, R. Riley y C. B. Verhaaren, [Understanding Q-Balls Beyond the Thin-Wall Limit](https://arxiv.org/abs/2009.08462), aporta contexto para distinguir la aproximación de pared delgada de los perfiles completos. Las identidades, los valores y los contrastes de este capítulo se derivan y reproducen en el paquete.
