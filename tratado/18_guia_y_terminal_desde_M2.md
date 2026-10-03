# Prueba directa de la guía autosostenida y del terminal

## 18.1. Resultado de la prueba

**M2 produce una solución tubular autosostenida de dos campos, pero esa solución es longitudinalmente inestable. No proporciona la guía operacional estable exigida para Canal.** El extremo tampoco queda descrito automáticamente por el terminal Neumann usado en el grafo: el exterior de vacío impone una respuesta dependiente de frecuencia, y falta la solución del extremo que la acople a los modos internos.

Este resultado ya no depende de atribuir al trazo una ecuación de guía. Se han resuelto las ecuaciones completas de M2 para un tubo recto sin paredes materiales, con los mismos parámetros de la Q-ball. Se han calculado los modos longitudinales crecientes, su convergencia y un argumento analítico que explica la inestabilidad. La prueba rechaza esta realización autosostenida concreta; no excluye todas las guías que pudieran sostenerse con materia, corrientes, topología adicional o control activo.

![Perfil y banda de inestabilidad calculados](../graficos/M2_guia_inestable.svg)

## 18.2. Geometría mínima y ecuaciones transversales

En coordenadas cilíndricas \((\rho,\varphi,z)\), se busca

\[
\Phi=f(\rho)e^{i\omega t},\qquad \chi=z_s(\rho),
\quad \partial_z f=\partial_z z_s=0.
\tag{18.1}
\]

\(z_s\) nombra al mediador para no confundirlo con la coordenada axial. El tubo tiene energía finita **por unidad de longitud**; un tubo infinito no es un objeto de energía total finita. No hay paredes, potencial de atrapamiento externo ni parámetros fundamentales específicos de Canal.

Con las unidades comunes,

\[
f''+\rho^{-1}f'=
(1-\omega^2+198f^2+\hat g z_s+50z_s^2)f,
\]

\[
z_s''+\rho^{-1}z_s'=10000z_s+\hat g f^2+100z_sf^2.
\tag{18.2}
\]

Se exige regularidad \(f'(0)=z_s'(0)=0\), positividad de \(f\) y decaimiento al vacío. El potencial reducido se utiliza únicamente para construir una aproximación inicial de Newton; el resultado final satisface ambas ecuaciones completas y conserva el gradiente del mediador. Cambiar un inicializador no cambia \(\Theta_s\).

Defínanse

\[
I_\perp=2\pi\int_0^\infty\rho f^2d\rho,\quad
T_\perp=2\pi\int_0^\infty\rho[(f')^2+\tfrac12(z_s')^2]d\rho,
\]

\[
U_\perp=2\pi\int_0^\infty\rho V(f,z_s)d\rho,
\quad q=2\omega I_\perp,\quad
\varepsilon=\omega^2I_\perp+T_\perp+U_\perp.
\tag{18.3}
\]

La identidad virial transversal es \(U_\perp=\omega^2I_\perp\). Para \(\omega=0.9\):

| Radio de caja | Nodos adaptados | Energía por longitud \(\hat\varepsilon\) | Carga por longitud \(\hat q\) | Residuo virial relativo |
|---:|---:|---:|---:|---:|
| 30 | 700 | 51.6294936874 | 55.0393671660 | \(3.08\times10^{-10}\) |
| 40 | 1349 | 51.6294938485 | 55.0393673482 | \(4.84\times10^{-12}\) |
| 50 | 2277 | 51.6294938554 | 55.0393673559 | \(3.57\times10^{-13}\) |

Se obtiene \(f(0)=0.72314289818\), \(z_s(0)=-0.07356896013\). El radio donde \(f^2\) cae a la mitad de su valor central es \(\rho_{1/2}=3.91602354\). Los cambios entre las dos últimas energías son del orden de \(10^{-10}\) relativamente. Esto demuestra convergencia numérica del perfil; no implica su estabilidad.

## 18.3. Perturbaciones que el modelo de grafo no contenía

Se perturban los tres campos reales con dependencia axial \(e^{\sigma t+ikz}\). En el sector axisimétrico, los operadores son los del capítulo 14 con laplaciano transversal \(\partial_\rho^2+\rho^{-1}\partial_\rho\), y cada diagonal recibe \(+k^2\):

\[
(\sigma^2+L_u+k^2)u-2\omega\sigma v+C\zeta=0,
\]

\[
(\sigma^2+L_v+k^2)v+2\omega\sigma u=0,
\]

\[
(\sigma^2+L_\chi+k^2)\zeta+Cu=0.
\tag{18.4}
\]

Una raíz real \(\sigma>0\) amplifica la perturbación. Basta **un** sector inestable para rechazar estabilidad espectral completa; no hace falta suponer que los demás sectores también lo sean.

Se discretiza el laplaciano por volúmenes finitos cilíndricos. La transformación con la raíz del peso de cada celda produce matrices simétricas de los Hessianos, conservando la regularidad en el eje. No se reemplaza el mediador por su mínimo algebraico en el espectro.

| Radio, celdas | Mínimo del Hessiano de amplitud \(H_0\) | \(\sigma(k=0.075)\) | \(\sigma(k=0.15)\) |
|---|---:|---:|---:|
| 30, 400 | −0.0513554135 | 0.0105724010 | 0.0164651525 |
| 30, 800 | −0.0513343980 | 0.0105729820 | 0.0164599559 |
| 30, 1600 | −0.0513291458 | 0.0105731270 | 0.0164586567 |
| 40, 2133 | −0.0513291463 | 0.0105731269 | 0.0164586568 |

El autovalor negativo del Hessiano converge con segundo orden. La tasa positiva persiste al refinar y ampliar el dominio. No es el pequeño error de simetría que tendía a cero en la traslación de la Q-ball.

## 18.4. Demostración de la inestabilidad de tubos de esta clase

La razón no depende de un ajuste de pérdida ni de atribuir un signo a una curva. Sean \(y=(\sqrt2f,z_s)\) y

\[
\mathcal S_\omega[y]=\int_{\mathbb R^2}
\left[\tfrac12|\nabla_\perp y|^2+W_\omega(y)\right]d^2x,
\quad W_\omega=V-\omega^2f^2.
\tag{18.5}
\]

Un perfil exacto es un punto crítico de \(\mathcal S_\omega\). Al dilatar transversalmente \(y_L(x)=y(x/L)\),

\[
\mathcal S_\omega[y_L]=T_\perp+L^2(U_\perp-\omega^2I_\perp).
\]

El virial hace nulo el segundo término. Para \(w=\partial_Ly_L|_{L=1}=-x\cdot\nabla y\), la segunda variación cumple

\[
\langle w,H_0w\rangle=0,\qquad H_0w=2\Delta_\perp y\ne0.
\tag{18.6}
\]

La última desigualdad se sigue de que un perfil armónico regular, localizado y no nulo no puede decaer al vacío. Si \(H_0\) fuese no negativo, \(\langle w,H_0w\rangle=0\) implicaría \(H_0w=0\), contradicción. **Todo perfil no trivial de esta clase tiene una dirección negativa de amplitud a frecuencia fija.** Se supone la regularidad y el decaimiento necesarios para las integraciones y para que \(w\) pertenezca al dominio de la forma cuadrática.

En un perfil sin nodos, \(L_v f=0\) y la transformación de estado fundamental da \(L_v\ge0\). También \(L_\chi\ge M^2>0\). Sea \(-\mu^2<0\) el autovalor más bajo de \(H_0\). Para \(0<k<\mu\), \(H_0+k^2I\) sigue teniendo una dirección negativa.

Eliminando \(v\) y \(\zeta\) de (18.4), para \(\sigma\) real se obtiene el operador autoadjunto

\[
\mathcal A(\sigma)=L_u+k^2+\sigma^2
-C(L_\chi+k^2+\sigma^2)^{-1}C
+4\omega^2\sigma^2(L_v+k^2+\sigma^2)^{-1}.
\tag{18.7}
\]

En \(\sigma=0\), es el complemento de Schur de \(H_0+k^2I\); tiene un autovalor negativo. Para \(\sigma\) suficientemente grande, el término \(\sigma^2\) domina y todos los términos restantes están acotados inferiormente, por lo que es positivo. Los inversos son regulares para \(k>0\), y el espectro esencial permanece separado de cero en este problema localizado. Por continuidad, un autovalor de \(\mathcal A\) cruza cero para algún \(\sigma>0\). Al reconstruir \(v,\zeta\), se obtiene un modo longitudinal creciente de las ecuaciones completas.

La perturbación puede tener promedio axial cero en una longitud periódica; entonces no cambia la carga total a primer orden. La conservación de \(Q\) no la elimina. El argumento cubre los tubos rectos localizados, sin nodos, con rotación temporal uniforme, cinética canónica y sin soportes externos de este modelo. No se transfiere sin análisis a corrientes axiales, vórtices, paredes materiales, gravedad o realimentación.

## 18.5. Umbral y tiempo de crecimiento

Del espectro transversal,

\[
k_c=\sqrt{-\lambda_{min}(H_0)}\simeq0.22656,
\quad 0<k<k_c\ \Longrightarrow\ \text{inestabilidad},
\]

\[
\lambda_{axial}>\lambda_c=2\pi/k_c\simeq27.7331\,\ell_0.
\tag{18.8}
\]

En un segmento ideal de longitud \(L\) que admita perturbaciones de Neumann \(\cos(n\pi z/L)\), existe al menos un modo de esta banda si \(L>\pi/k_c\simeq13.8665\ell_0\). Es una observación importante: incluso **imponer** terminales Neumann no estabiliza por sí solo una guía suficientemente larga. Para periodicidad axial, el umbral de longitud del primer modo es \(2\pi/k_c\).

La mayor tasa entre los 31 puntos muestreados es \(\sigma=0.0165338\), cerca de \(k=0.158748\). Se denomina máximo muestreado, no máximo continuo certificado. El tiempo de un factor \(e\) es \(t_e\simeq60.4823t_0\). En la escala común ilustrativa de 1 eV, \(t_e=3.9810\times10^{-14}\) s y \(\lambda_c=5.47248\) μm. Una estimación lineal entre amplitudes \(\delta_0\) y \(\delta_1\) sería \(t\simeq\sigma^{-1}\ln(\delta_1/\delta_0)\); no demuestra la forma ni el tiempo final de fragmentación no lineal.

Como comprobación independiente de la pendiente a larga longitud de onda, la carga lineal de la familia da

\[
\frac{c_L^2}{c^2}=\frac{q}{\omega\,dq/d\omega}\simeq-0.0226604.
\tag{18.9}
\]

Se obtiene al reducir lentamente la fase axial: \(\mathcal L_{linea}(\omega)\) tiene derivada \(q\), y la ecuación de fase linealizada es \((dq/d\omega)\ddot\theta-(q/\omega)\theta''=0\). Por tanto \(\sigma/k\to\sqrt{-c_L^2/c^2}\simeq0.15053\) cuando \(k\to0\). Ésta es la compresibilidad de la **línea completa con su superficie**, distinta de la velocidad acústica positiva del volumen homogéneo del capítulo 15. No hay contradicción entre ambos resultados.

## 18.6. El exterior del terminal desde las ecuaciones

Un extremo de una guía no puede definirse añadiendo \(\partial_z q=0\) sin resolver la transición o justificar esa condición. En el exterior donde el fondo se aproxima al vacío, las perturbaciones complejas tienen bandas laterales de frecuencia \(\omega+\Omega\) y \(\omega-\Omega\); el mediador tiene frecuencia \(\Omega\).

Para un semiespacio de vacío lineal, transformado en las coordenadas tangenciales de momento \(p\), el mapa de Dirichlet a Neumann es

\[
\partial_n\eta_\pm=-\kappa_\pm\eta_\pm,\quad
\kappa_\pm^2=p^2+1-(\omega\pm\Omega)^2,
\]

\[
\partial_n\zeta=-\kappa_\chi\zeta,\quad
\kappa_\chi^2=p^2+10000-\Omega^2.
\tag{18.10}
\]

Se elige decaimiento cuando \(\kappa^2>0\) y la rama saliente retardada cuando hay propagación. El resultado es exacto para el exterior lineal de vacío; aplicarlo a una superficie dentro de la cola del fondo introduce el error de haber despreciado esa cola. En una superficie curva el mapa es un operador espacial no local, no un escalar constante.

En \(p=0\), \(\omega=0.9\), \(\Omega=0.05\),

\[
\kappa_+=0.31224990,\quad
\kappa_-=0.52678269,\quad
\kappa_\chi=\sqrt{9999.9975}.
\tag{18.11}
\]

Ninguno es cero. En \(\Omega=0.1\), sólo la primera banda toca su umbral; las otras siguen siendo evanescentes. Por encima, esa banda puede radiar. Así, el exterior no proporciona una condición Neumann común y constante para todos los componentes sobre una banda.

Para un solo canal y una transición abrupta ideal de demostración, empalmar \(e^{ikz}+r e^{-ikz}\) a un exterior evanescente da

\[
r(\Omega)=\frac{ik+\kappa(\Omega)}{ik-\kappa(\Omega)},
\qquad |r|=1.
\tag{18.12}
\]

La reflexión puede ser total con fase diferente de cero. Neumann correspondería a \(r=+1\); una barrera evanescente finita no se identifica automáticamente con ese valor. Una región de transición resonante podría producir una fase efectiva equivalente en frecuencias seleccionadas: para demostrarlo hay que calcular esa región. La fórmula escalar (18.12) ilustra el empalme; **no es** el coeficiente de reflexión del extremo completo del Q-tubo, que mezcla modos y necesita su fondo axial.

## 18.7. Decisión física

La cadena directa conseguida es

\[
\Theta_s\ \longrightarrow\ \text{ecuaciones de un tubo recto libre}
\ \longrightarrow\ \text{perfil convergente}
\ \longrightarrow\ \text{banda longitudinal creciente}
\ \longrightarrow\ \text{rechazo como guía operacional estable}.
\]

Además se deriva la condición del exterior de vacío y se demuestra por qué no equivale al terminal ideal supuesto anteriormente. No se ha resuelto un extremo estable completo ni el trazado de P-04 con sus curvas y bifurcación, y no se presenta la fórmula de un semiespacio como si lo fuera.

Por tanto, **no puede sostenerse que se haya demostrado la guía y el terminal físicos requeridos**. La realización libre ensayada falla el criterio de estabilidad por una razón estructural, no por falta de precisión del dibujo ni por un parámetro de pérdida mal ajustado. La petición de una demostración positiva no cambia el signo de ese resultado.

## 18.8. Relación con resultados publicados

Q. Chen, [Hydrodynamic and Rayleigh-Plateau instabilities of Q-strings](https://arxiv.org/abs/2412.09815), estudia la inestabilidad longitudinal de cuerdas Q en un modelo de un campo complejo. Es un antecedente pertinente, no una verificación del M2 de dos campos de este proyecto. Aquí se conserva explícitamente el mediador y se calculan sus operadores acoplados. Las cifras, la demostración adaptada y el código de este capítulo pertenecen al análisis del proyecto.

Los datos completos están en `validacion/guia_m2.json` y `validacion/m2_guia_perfil.csv`; se reproducen con `herramientas/guia_m2.py`.
