# Regímenes de validez y derivación de coeficientes

## 15.1. Cuatro afirmaciones que no son equivalentes

La existencia global de una solución de las ecuaciones clásicas, la precisión de una aproximación, la precisión de un cálculo numérico y la adecuación física a materia real son problemas distintos. M2 puede ser matemáticamente definido a cualquier amplitud finita y, aun así, su truncación efectiva puede fallar a cierta escala. La validez de R1 requiere resolver las cuatro cuestiones para el dispositivo concreto.

No existe actualmente una tabla justificada que garantice todas las funciones entre determinados voltajes, temperaturas, energías y tiempos SI. Se pueden dar dominios explícitos para las aproximaciones identificadas, y éstos son los que siguen. Donde falta un corte físico o un error demostrado, se declara indeterminado: no se sustituye por el corte de 1 MeV usado antes en un ejemplo M1.

## 15.2. Amplitud y reducción del mediador

Se usa \(\sigma=\lambda|\Phi|^2/m^2\). El potencial racional exacto y el sextico difieren en

\[
\hat U_{ef}-\hat U_6=-\frac{\sigma^4}{100(1+\sigma/100)},
\quad\hat U_6=\sigma-\sigma^2+\sigma^3.
\tag{15.1}
\]

Respecto del **término sextico** \(\sigma^3\), el error es \(\sigma/(100+\sigma)\). El criterio de 1 % exige \(\sigma\le100/99=1.010101\), o \(|f|\le1.005038\). No garantiza 1 % en la fuerza, presión, autovalores o una diferencia pequeña entre grandes contribuciones que se cancelan.

Eliminar \(\chi\) también induce el término de gradientes

\[
-\tfrac12[\chi_*'(s)]^2(\partial s)^2.
\]

En la coordenada de amplitud \(f\), la corrección del coeficiente cinético es

\[
\delta Z(\sigma)=2\sigma\left[
\frac{\hat g\hat M^2}{(\hat M^2+\hat h\sigma)^2}\right]^2.
\tag{15.2}
\]

En la rama próxima al vacío, exigir \(\delta Z\le0.01\) da \(\sigma\le0.25253493\). En el centro de la solución radial, \(\sigma=0.55654465\) y \(\delta Z=0.0217730\). Por tanto la reducción que conserva sólo el potencial y elimina también la cinética inducida **no alcanza 1 % en ese coeficiente** para el estado ensayado. M2 de dos campos no incurre en esta omisión. A amplitudes enormes, \(\delta Z\) vuelve a disminuir; eso no restaura la expansión sextica, que ya ha fallado.

Alrededor de un fondo homogéneo, la respuesta lineal exacta del mediador es

\[
\delta\chi(\Omega,k)=-
\frac{g+h\chi_0}{M^2+hs_0+k^2-\Omega^2}\,\delta s.
\tag{15.3}
\]

La aproximación algebraica sustituye el denominador por \(D=M^2+hs_0\). Fuera del polo, el error relativo a la respuesta exacta es \(|k^2-\Omega^2|/D\). Una condición suficiente de 1 % es

\[
\Omega^2+k^2\le0.01(M^2+hs_0).
\tag{15.4}
\]

En el vacío del benchmark, \(\hat\Omega^2+\hat k^2\le100\). Si sólo hay variación espacial, \(L_{grad}=1/k\ge0.1\ell_0\); si sólo hay variación temporal, \(|\hat\Omega|\le10\). La frecuencia ordinaria es \(\nu=\hat\Omega/(2\pi t_0)\). Estas condiciones se refieren a la **respuesta incremental de \(\chi\)**, no a la validez de una guía, ni a campos inhomogéneos arbitrarios. Cerca de \(\Omega^2=k^2+M^2+hs_0\), la eliminación algebraica fracasa y se debe mantener el mediador dinámico.

## 15.3. Modos homogéneos, estabilidad y velocidad

Para \(\Phi=\sqrt{s_0}e^{i\omega t}\), \(\chi=\chi_*(s_0)\), se exige \(\omega^2=U_{ef}'(s_0)\). El fondo tiene

\[
p=s_0U_{ef}'-U_{ef},\qquad
\rho=s_0U_{ef}'+U_{ef},\qquad
\frac{c_s^2}{c^2}=\frac{s_0U_{ef}''}{s_0U_{ef}''+2U_{ef}'}.
\tag{15.5}
\]

Se deriva la última expresión del determinante completo de tres perturbaciones, no de una velocidad asignada. En unidades adimensionales, con \(x=\Omega^2\),

\[
\{(a-x)(k^2-x)-4\omega^2x\}(b-x)-C^2(k^2-x)=0,
\]

\[
a=k^2+396\sigma,\quad b=k^2+10000+100\sigma,
\quad C^2=2\sigma(\hat g+100z_0)^2.
\tag{15.6}
\]

El archivo de resultados conserva las tres ramas. El límite de la raíz sin brecha cuando \(k\to0\) da (15.5); a altas frecuencias, el sistema completo conserva el cono causal de (13.11).

| Estado | \(\sigma\) | \(\hat\omega\) | \(p/\rho\) | \(c_s\) |
|---|---:|---:|---:|---:|
| Presión nula | 0.503781526 | 0.865298869 | 0 | \(1.49990238\times10^8\) m/s |
| Ajuste sólo de la velocidad R1 | 0.336317264 | 0.815584530 | −0.0771611225 | \(1.00000000\times10^7\) m/s |

La frontera de inestabilidad compresional de esta rama homogénea es \(U_{ef}''=0\), en \(\sigma=0.335572985\). Justo por encima, la velocidad acústica es pequeña, pero la presión es negativa: el medio precisa tracción/confinamiento para mantener esa configuración uniforme. En la región donde (15.5) es negativa hay modos largos exponencialmente crecientes. No se reemplaza ese diagnóstico por una velocidad imaginaria de uso operacional.

La presión nula es una referencia de volumen homogéneo; una gota finita tiene contribuciones de superficie. El estado homogéneo no representa las paredes y curvas de Canal. Tampoco es un sólido: una fase escalar isotrópica no proporciona por sí sola el módulo de corte estático ni el módulo de Young adoptado en R1.

## 15.4. Linealización y amplitudes de señal

No existe una cota universal «perturbación menor de 1 %» que garantice error de 1 % en cualquier observable. Una norma relativa puede hacerse singular en los modos de fase, traslación o cerca de un umbral.

Se incluye un test explícito y reproducible. En el estado homogéneo de presión nula se usan coordenadas canónicas \(y=(\sqrt2f,z)\). Se toma el autovector unitario \(v_{min}\) del Hessiano de amplitud de menor autovalor y se perturba en línea recta \(\delta y=\epsilon\sqrt2f_0v_{min}\). Se compara la fuerza no lineal del marco rotante con su Jacobiano:

\[
\eta_F(\epsilon)=
\frac{\|F(y_0+\delta y)-F(y_0)-DF(y_0)\delta y\|}
{\|DF(y_0)\delta y\|}.
\tag{15.7}
\]

Para este sentido y esta norma, \(\eta_F=0.01\) a \(\epsilon=1.4296\times10^{-5}\). La dirección lineal sale de un valle curvo con un mediador rígido; de ahí que el error relativo de fuerza pueda crecer antes que la perturbación geométrica parezca grande. No es un umbral de destrucción ni la amplitud máxima de una primordial. Una reducción no lineal que siga el valle y conserve su cinética tiene otros errores.

## 15.5. Tiempo, energía, ruido y corte físico

| Nivel de descripción | Dominio establecido | Dónde no se debe extrapolar |
|---|---|---|
| M2 escalar clásico exacto | Datos de energía finita; solución global en la clase del capítulo 13 | No demuestra materia real ni completación cuántica |
| Solución numérica estacionaria | Rama \(\hat\omega=0.9\), radios 40–60 y tolerancias declaradas | No demuestra toda la familia ni una red 3D |
| Espectro calculado | Hessianos de \(\ell=0,1,2,3\), generador próximo a cero en \(\ell=0,1,2\) | No certifica por intervalos el continuo |
| Identidades angulares | Todo \(\ell\) para un fondo exacto positivo, monótono y regular | No se transfieren a nodos, vórtices o geometrías arbitrarias |
| Transitorio no lineal | Perturbación radial prescrita \(10^{-3}\), \(0\le\tau\le24\) | No valida segundos, fatiga, escritura ni envejecimiento |
| Sextico y mediador algebraico | Cotas (15.1)–(15.4), según el observable | Falla cerca del polo pesado, gradientes rápidos o grandes amplitudes |
| EFT completa con materia | Corte y errores sin identificar | No hay intervalo SI global defendible para R1 |

Una frecuencia aproximada \(\Omega+\delta\Omega\) acumula error de fase \(|\delta\varphi|\simeq|\delta\Omega|t\). Para una tolerancia \(\varphi_{max}\), se requiere \(t\le\varphi_{max}/|\delta\Omega|\), además del control de deriva del estado y del ruido. Una aproximación precisa en un instante no implica retención arbitrariamente larga.

En la escala SI común ilustrativa, la Q-ball tiene \(E=4.04655\times10^{-13}\) J y \(Q=2.74577\times10^6\). La densidad homogénea de presión nula es \(1.57310\times10^4\) J/m³, no los \(10^9\) J/m³ de determinadas metas R1. Cambiar \(m,\lambda\) para alcanzar una meta alteraría simultáneamente todas las escalas y todos los dispositivos; tendría que ser un nuevo benchmark global, no un ajuste oculto de Reserva.

Para usar M2 como EFT cuántica haría falta controlar cocientes \(\hbar\Omega/\Lambda_{EFT}\), \(\hbar ck/\Lambda_{EFT}\), los invariantes de fondo y los términos omitidos, además de ocupaciones que justifiquen una aproximación clásica. El mediador de 100 eV está resuelto en M2 y **no es automáticamente su corte UV**. El carácter polinómico del potencial tampoco demuestra estabilidad radiativa de todos sus coeficientes ni determina los portales no polinómicos.

## 15.6. Cómo deben salir los coeficientes de un dispositivo

Una geometría física \(\mathcal G_d\) y su configuración \(\mathcal C_d\) deben definir el dominio, los materiales, las fuentes y terminales. Primero se resuelve \(X_0=(\Phi_0,\chi_0,A_\mu,\psi)\). Después se obtiene el operador de respuesta \(D_d(\Omega,k;X_0,\Theta)\). Para un modo simple,

\[
v_g=-\frac{\langle u_L,\partial_kD_d\,u_R\rangle}
{\langle u_L,\partial_\Omega D_d\,u_R\rangle}.
\tag{15.8}
\]

La normalización y el flujo de energía fijan su impedancia. Los solapamientos de las derivadas tercera y cuarta de la acción fijan las interacciones modales. No se infiere igualdad de impedancias porque tres líneas tengan el mismo grosor en SVG.

Separar modos observados \(P\) y grados de libertad eliminados \(Q\) produce, con condición retardada,

\[
D_{ef}^R=D_{PP}-D_{PQ}(D_{QQ}^R)^{-1}D_{QP}.
\tag{15.9}
\]

Su parte imaginaria describe escape o disipación cuando existen canales abiertos. En un modo débilmente amortiguado \(\Omega=\Omega_r-i\gamma\), la atenuación de potencia espacial es

\[
\alpha_P=2\gamma/v_g.
\tag{15.10}
\]

Las metas \(\alpha_P=10^{-4}\,\mathrm{m^{-1}}\), \(v_g=10^7\) m/s requieren \(\gamma=500\,\mathrm{s^{-1}}\). Es una condición inversa de diseño; M2 todavía no ha producido ese valor para P-04.

Para una coordenada con ecuación

\[
M_{ef}\ddot q+K_{ef}q+\int_{-\infty}^t\Gamma(t-t')\dot q(t')dt'
=F_{ext}+\xi,
\]

el espectro simetrizado bilateral de fuerza en equilibrio satisface, con esta convención,

\[
S_{\xi\xi}^{sym}(\Omega)=\hbar\Omega
\coth\!\left(\frac{\hbar\Omega}{2k_BT}\right)\Re\widetilde\Gamma(\Omega).
\tag{15.11}
\]

En el límite clásico da \(2k_BT\Re\widetilde\Gamma\). Este vínculo impide elegir pérdidas y ruido de equilibrio como parámetros independientes. Fuera del equilibrio se calculan las correlaciones del estado de los reservorios; no se aplica automáticamente una única temperatura. Una reducción markoviana necesita un tiempo de correlación de baño corto frente a los tiempos del sistema y acoplamiento suficientemente débil, condiciones todavía no cuantificadas para los terminales rúnicos.
