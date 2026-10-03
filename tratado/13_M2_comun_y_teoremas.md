# M2 común: definición matemática y alcance demostrado

## 13.1. Resultado y regla de aceptación

**M2 no ha producido todavía un dispositivo P-04, P-11 o P-18 completamente derivado.** Esta edición obtiene nuevos resultados del mismo sistema de dos campos, demuestra propiedades de su problema de Cauchy y ensaya su dinámica. También identifica obstrucciones exactas y contrastes con R1. No convierte los antiguos modelos de grafos, Kerr o tres niveles en realizaciones de M2.

El criterio de aceptación es la conjunción, no la suma, de diez condiciones:

\[
\mathcal A_d=G_d\land\Theta\land C_d\land S_d\land E_d
\land D_d\land N_d\land P_d\land R_d\land V_d.
\]

Aquí figuran geometría física, parámetros comunes identificados, coeficientes derivados, solución, estabilidad, dinámica, pérdidas y ruido, preparación, función R1 y dominio de validez. Un cálculo radial correcto no sustituye a una solución de Canal. Una transmisión unitaria de un grafo no demuestra sus paredes. Un campo inicialmente impuesto no demuestra Semilla. `datos/aceptacion_m2.json` registra el resultado por primordial.

La conclusión negativa tiene un alcance preciso: **la cadena presentada no satisface el criterio**. No es un teorema de inexistencia de todos los dispositivos posibles en cualquier extensión de M2. Las exclusiones matemáticas de este capítulo sí declaran las hipótesis bajo las que se aplican.

## 13.2. Un solo conjunto fundamental

En unidades \(c=\hbar=1\), espacio de Minkowski y signatura \((-+++)\), se fija

\[
\mathcal L_s=-|\partial\Phi|^2-\tfrac12(\partial\chi)^2-V,
\quad s=|\Phi|^2,
\]

\[
V=m^2s+\lambda_0s^2+\tfrac12M^2\chi^2+g\chi s+\tfrac12h\chi^2s.
\tag{13.1}
\]

\(\Phi\) tiene dos componentes reales; \(\chi\) una. No hay un mediador por primordial. El conjunto del sector escalar es

\[
\Theta_s=(m,M,\lambda_0,g,h),\qquad
\lambda\equiv\frac{g^2}{2M^2}-\lambda_0>0.
\]

\(\lambda\) es una combinación derivada; no se cuenta como sexto parámetro independiente. Se conserva el benchmark anterior:

\[
\lambda_0=99\lambda,\quad M=100m,\quad
g=100m\sqrt{200\lambda},\quad h=100\lambda.
\tag{13.2}
\]

Las ecuaciones adimensionales dependen de las mismas razones en todos los ensayos. Para expresar una sola escala ilustrativa en SI se fija \(mc^2=1\) eV y \(\lambda=10^{-3}\), sin ajustar R1. Resulta \(\lambda_0=0.099\), \(Mc^2=100\) eV, \(g=44.72135955\) eV y \(h=0.1\). Esta elección **no** es el ajuste de densidad de M1 del capítulo 08; los dos ejemplos no se pueden mezclar.

El conjunto de la teoría que interactúa con materia tendría que ser

\[
\Theta_{\rm total}=\{\Theta_s,a,b,s_A,s_B,\Theta_{\rm materia},
\Lambda_{\rm EFT},c_i(\mu_0),\text{condiciones de renormalización}\},
\tag{13.3}
\]

con los portales ya definidos

\[
A(s)=\exp\!\left(\frac{as}{s+s_A}\right),\qquad
B(s)=\exp\!\left(\frac{4bss_B}{(s+s_B)^2}\right),
\]

\[
\mathcal L_{\rm EM}=-\tfrac14 B(s)F_{\mu\nu}F^{\mu\nu},\qquad
S_m=S_m[\psi,A^2(s)\eta_{\mu\nu},A_\mu].
\]

Las constantes de materia incluyen las masas y acoplamientos del sector material elegido. La composición, temperatura, presión, orientación cristalina y población de sus estados son datos de configuración; no nuevas leyes fundamentales. Los \(c_i\) describen operadores efectivos omitidos y su orden de truncación. **El proyecto no identifica un valor común de los portales ni una completación EFT con error controlado.** Darles números arbitrarios produciría un candidato adicional, no la demostración solicitada. En el benchmark aislado \(a=b=0\), por lo que la conversión directa con materia y electromagnetismo es exactamente cero.

| Clase | Ejemplos | Regla |
|---|---|---|
| Fundamental común | \(m,M,\lambda_0,g,h,a,b,s_A,s_B\) | La misma definición para todos los dispositivos |
| Geometría | Dimensiones, sección, curvas, material y disposición de contactos | Puede cambiar entre dispositivos; debe entrar en el problema físico |
| Estado | \(Q,E,T\), perfil inicial, fase, frecuencia de rotación \(\omega\) | No se confunde con una constante fundamental |
| Terminales | Fuente y carga, impedancia, temperatura de reservorios | Se especifican con su realización y balance |
| Control | Consigna y forma temporal del bombeo | Su energía y reacción se contabilizan |
| Coeficiente efectivo | \(v_g,K,\kappa,G_{th},D,\Delta E\) | Se calcula; no se usa como entrada para declarar derivación |
| Objetivo | Valores R1 de velocidad, potencia, fidelidad y conductancia | Sirve para aceptar o rechazar el resultado |

La frecuencia \(\hat\omega=0.9\) identifica el estado radial ensayado. No pertenece a \(\Theta_s\). Tampoco pertenecen a \(\Theta_s\) el paso de malla, la tolerancia ni el radio del dominio numérico.

## 13.3. Ecuaciones, conservación y unidades

\[
\ddot\Phi-\nabla^2\Phi+
(m^2+2\lambda_0|\Phi|^2+g\chi+\tfrac12h\chi^2)\Phi=0,
\]

\[
\ddot\chi-\nabla^2\chi+(M^2+h|\Phi|^2)\chi+g|\Phi|^2=0.
\tag{13.4}
\]

Para datos de energía finita en \(\mathbb R^3\), sin flujo por el infinito,

\[
E=\int\!\left(|\dot\Phi|^2+|\nabla\Phi|^2+
\tfrac12\dot\chi^2+\tfrac12|\nabla\chi|^2+V\right)d^3x,
\quad Q=2\int\!\operatorname{Im}(\Phi^*\dot\Phi)d^3x
\tag{13.5}
\]

se conservan. Hay asimismo conservación del momento total. En un subdominio, las variaciones de energía y carga son flujos por su frontera: abrir terminales cambia los balances del subsistema, no la conservación global.

Con \(x=mr\), \(\tau=mt\), \(f=\sqrt\lambda\,|\Phi|/m\), \(z=\sqrt\lambda\chi/m\),

\[
E=\frac{mc^2}{\lambda}\hat E,\quad Q=\frac{\hat Q}{\lambda},\quad
\ell_0=\frac{\hbar c}{mc^2},\quad t_0=\frac{\hbar}{mc^2},\quad
u_0=\frac{(mc^2)^4}{\lambda(\hbar c)^3}.
\tag{13.6}
\]

La escala SI ilustrativa da \(\ell_0=1.97327\times10^{-7}\) m, \(t_0=6.58212\times10^{-16}\) s y \(u_0=2.08522\times10^4\) J/m³. Estas conversiones no son mediciones del campo.

## 13.4. Vacío: demostración clásica global

Completando el cuadrado,

\[
V=\tfrac12(M^2+hs)(\chi-\chi_*(s))^2+U_{ef}(s),
\quad\chi_*=-\frac{gs}{M^2+hs},
\]

\[
U_{ef}=m^2s+\lambda_0s^2-\frac{g^2s^2}{2(M^2+hs)}.
\tag{13.7}
\]

En variables adimensionales, \(\sigma=|f|^2\),

\[
\hat U_{ef}(\sigma)=\sigma-\sigma^2+
\frac{\sigma^3}{1+\sigma/100},\quad
\min_{\sigma\ge0}\frac{\hat U_{ef}}{\sigma}
=1-100(10-\sqrt{99})^2\equiv v_*=0.7487421324>0.
\tag{13.8}
\]

Por tanto \(\hat V\ge v_*|f|^2+5000(z-z_*)^2\), con igualdad cero solamente en \(f=z=0\). No hay vacío de menor energía ni dirección de escape con potencial negativo. Además,

\[
z_*^2\le\frac{\hat g^2}{4\hat M^2\hat h}|f|^2
=\tfrac12|f|^2,
\]

\[
|f|^2\le\hat V/v_*,\qquad
z^2\le\left(4/\hat M^2+1/v_*\right)\hat V.
\tag{13.9}
\]

Así, la energía controla las normas \(H^1\) de los tres campos reales y las normas \(L^2\) de sus velocidades. La conservación de energía demuestra estabilidad de Lyapunov del vacío en esa norma: una energía inicial suficientemente pequeña mantiene pequeña la norma energética para todo tiempo. No implica una cota puntual de amplitud derivada sólo de \(H^1\), ni relajación asintótica.

En el vacío, los modos de Fourier cumplen exactamente

\[
\Omega_\Phi^2=k^2+m^2,\qquad \Omega_\chi^2=k^2+M^2.
\tag{13.10}
\]

No hay masas taquiónicas ni modos de energía cinética negativa en este sector. Esta demostración es clásica. Los lazos cuánticos, los contraterminos y un medio material no están incluidos en ella.

## 13.5. Existencia global del problema de Cauchy escalar

Se toman datos \((\sqrt2\Re\Phi,\sqrt2\Im\Phi,\chi)\in H^1(\mathbb R^3)^3\) y velocidades en \(L^2(\mathbb R^3)^3\). Los términos no lineales de (13.4) son polinomios de grados dos y tres. En tres dimensiones, \(H^1\hookrightarrow L^p\) para \(2\le p\le6\). Por Hölder, los productos cúbicos son \(L^2\) y son localmente Lipschitz de \(H^1\) a \(L^2\); los cuadráticos se controlan con \(L^4\).

La fórmula integral de la ecuación de onda y la estimación de energía construyen una solución local única mediante contracción en \(C_tH^1\cap C_t^1L^2\). El tiempo de existencia local depende de una cota de esa norma. Las desigualdades (13.9) y la conservación de \(E\) dan una cota uniforme, de modo que el argumento local se puede reiterar para todo tiempo finito. Se obtiene una solución global de energía, única en esta clase, con dependencia continua de los datos. La conservación se justifica primero para aproximaciones suaves y después por continuidad.

Esto cierra el problema de Cauchy **del sector escalar clásico aislado con los parámetros (13.2)**. No prueba existencia de cada estado operacional, estabilidad de cada solución, ni validez empírica o cuántica de la teoría. Un problema con paredes, materia o control necesita declarar esas ecuaciones y condiciones de frontera para heredar un resultado análogo.

## 13.6. Causalidad e hiperbolicidad

En los tres campos reales canónicos, el símbolo principal es

\[
P(\xi)=(-\xi_t^2+|\boldsymbol\xi|^2)I_3.
\tag{13.11}
\]

La reducción de primer orden es simétrica hiperbólica, y sus características son el cono de luz. El potencial sólo introduce términos de orden inferior. Por localidad y la estimación de energía en conos, los datos externos al cono pasado no afectan la solución: la velocidad de frente es \(c\), independientemente de una velocidad de grupo menor o de una dispersión anómala local.

Para el portal electromagnético sin operadores de derivadas superiores, \(B>0\) conserva el signo cinético y, tras fijar calibre, el mismo cono principal. Una métrica material conforme con \(A>0\) comparte el cono nulo. No se ha demostrado aquí la hiperbolicidad de una teoría material arbitraria, una completación de derivadas superiores o una teoría gravitatoria no mínima. El laboratorio de estos cálculos fija \(\xi=0\) y métrica plana.

## 13.7. Obstrucción estática y alcance de la geometría

Para campos estrictamente independientes del tiempo, localizados y con vacío en el infinito, defínase \(\Phi_L(\mathbf x)=\Phi(\mathbf x/L)\), \(\chi_L(\mathbf x)=\chi(\mathbf x/L)\). Si \(T\) es la energía de gradientes y \(U\) la de potencial,

\[
E(L)=LT+L^3U,\qquad E'(1)=T+3U>0
\tag{13.12}
\]

para toda configuración no nula. Una solución estática de energía finita debe ser crítica frente a esta variación; por tanto no existe una solución estática no trivial en ese sector. Ésta es la aplicación directa del argumento de escala de Derrick. La ecuación y sus hipótesis bastan para comprobarla.

**No se aplica a un estado cargado en rotación interna.** A carga fija,

\[
E_Q[f,\chi]=\frac{Q^2}{4I}+T+U,\qquad I=\int f^2d^3x,
\]

\[
E_Q(L)=L^{-3}\frac{Q^2}{4I}+LT+L^3U.
\tag{13.13}
\]

El término \(L^{-3}\) permite un mínimo: ése es el mecanismo de la solución cargada resuelta en el capítulo 14. Ni este mínimo ni su simetría radial fijan por sí mismos un recorrido con bifurcaciones y curvas.

Un trazo puede especificar una región deseada o datos iniciales. Para ser confinamiento debe aparecer como un perfil material calculado, una fuente, una condición física de frontera o un estado autosostenido que satisfaga las ecuaciones. Las tres posibilidades cambian el problema que se resuelve. No existe un término «reconocer P-04» en (13.4).

## 13.8. Preparación y simetría de carga

Con los portales \(A(s),B(s)\), toda ecuación clásica de \(\Phi\) sigue siendo homogénea en \(\Phi\) y \(\Phi^*\). Para campos externos regulares, \(\Phi=\dot\Phi=0\) es una solución; por unicidad, un estado exactamente nulo no abandona esa solución por una modulación multiplicativa. Una masa efectiva negativa puede amplificar una perturbación, pero no crea una perturbación clásica desde cero.

La simetría U(1) tampoco cambia con un bombeo que sólo dependa de \(s\). En un sistema cerrado \(Q(t)=Q(0)\), aunque el bombeo aporte energía. Partir de \(Q=0\) no permite acabar con una única carga positiva y nada más: hace falta una carga compensatoria, un flujo por terminales o una modificación explícita de la simetría. Pares de cargas opuestas y producción cuántica no están excluidos.

Un estado cuántico de vacío tiene fluctuaciones; no se identifica con datos clásicos exactamente nulos. Calcular su crecimiento, selección espacial y saturación exige el estado inicial, las correlaciones y el acoplamiento de la fuente. El ensayo Floquet anterior sólo verificaba el crecimiento lineal de una perturbación ya disponible. No es un protocolo completo de P-01.
