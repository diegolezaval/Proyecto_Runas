# CP12/P4 · Prerregistro de la referencia Galerkin

16 de noviembre de 2026. Comparar P4 contra una discretización independiente del mismo M2 en $R=220$, $L=4$, con $\epsilon=0.02$. El insumo es el cierre de la tercera malla en `1dc926f3f9ee32ab9f7fc9ccf279113a88899738`. Se recuperan sus estados y los dos estados del piloto correspondientes al mismo reloj. La Cauchy CP04 de $\tau=1200$, los seis campos, la cúbica par y su derivada para la semilla cuadrupolar siguen la preparación registrada.

## Espacio y tiempo

Usar $u_\ell=rq_\ell$. Para cada componente, ensamblar $M_{ij}=\int B_iB_j$ y $K_{\ell,ij}=\int(B_i'B_j'+\ell(\ell+1)B_iB_j/r^2)$. La base conforme es de grado cinco en los elementos ordinarios. En el primer elemento los polinomios de $r^2$ llevan el factor $r^{\ell+1}$, con continuidad en su extremo derecho. El grado de libertad en $R$ se elimina por Dirichlet. Integrar con 12 nodos de Gauss por elemento ordinario y 24 en el del origen. Proyectar la Cauchy en masa. Registrar su defecto de proyección.

El término de masa es $m^2M$ para las dos componentes de Φ y $M_\chi^2M$ para χ. La carga no lineal débil integra $B_i r N(q)$ con $q=u/r$, las tres contribuciones de la acción común y la cuadratura angular original. Usar el subespacio D2 de dimensión seis inducido por la semilla dentro de $L=4$. Antes de integrar, contrastar la proyección y sus productos con los 25 armónicos originales.

Resolver en el tiempo por Gauss–Legendre de cuatro etapas y orden ocho. Resolver el bloque lineal de cada etapa por LU dispersa, con iteración precondicionada de la carga no lineal. La tolerancia es la del incremento de etapa, $\lvert Q_{\mathrm{nuevo}}-Q\rvert/(\mathrm{atol}+\mathrm{rtol}\max(\lvert Q_{\mathrm{nuevo}}\rvert,\lvert Q\rvert))\le1$. Cada paso alcanza el reloj indicado por el contador entero. Los dos brazos temporales cambian un parámetro de la configuración R2 a la vez.

| Caso | Ancho de elemento | Paso temporal | rtol, atol de etapas |
| --- | ---: | ---: | --- |
| R0 | 0,5 | 0,008 | $2\cdot10^{-11}$, $2\cdot10^{-13}$ |
| R1 | 0,25 | 0,008 | $2\cdot10^{-11}$, $2\cdot10^{-13}$ |
| R2, referencia de comparación | 0,125 | 0,008 | $2\cdot10^{-11}$, $2\cdot10^{-13}$ |
| T | 0,125 | 0,004 | $2\cdot10^{-11}$, $2\cdot10^{-13}$ |
| EPS | 0,125 | 0,008 | $2\cdot10^{-13}$, $2\cdot10^{-15}$ |

## Puertas antes de la campaña

Medir perfiles fabricados $u_\ell=(r/3)^{\ell+1}(1-r^2/R^2)e^{-(r/3)^2}\cos(kr)$ en $\ell=0,2,4$, con $k=0$ y $k=8$. Las diferencias relativas del operador reconstruido deben decrecer con el refinamiento o quedar en el piso $10^{-10}$. En R2 se exigen ≤ $10^{-3}$ para el caso liso y ≤ $10^{-2}$ para la banda. Comprobar finitud, traza Dirichlet, estructura de la base del origen y coincidencia de la Cauchy sin proyectar con el lector original en los tres retículos, a error absoluto ≤ $2\cdot10^{-13}$.

Verificar el gradiente de la acción y la identidad U(1) con paso complejo sobre la cuadratura angular completa. Exigir residuos ≤ $2\cdot10^{-12}$ de las identidades de energía y carga y de los controles de potencial, fuerza, proyección y simetría. Verificar la tabla de Gauss y ejecutar un prefijo de control hasta $\tau=0.08$ con las cinco configuraciones. Aplicar las puertas físicas originales al prefijo. Registrar pasos, tiempo de cálculo e iteraciones antes de activar las trayectorias desde τ0.

## Lectura de las trayectorias

Guardar el estado, observadores y recibos en τ0 y cada ocho unidades, con observaciones cada 0,4. Medir deriva de energía y carga en cada paso y aplicar los máximos $2\cdot10^{-4}$ y $10^{-9}$, cambio de carga en el núcleo ≤ 0,005 y amplificación ≤ 3. La comparación recupera las tres mallas P4 guardadas y las cinco trayectorias de referencia por hash. El comparador original evalúa las cinco métricas en $r<40$ sobre centros de paso 0,015625 y sólo parametriza la guarda del tiempo para prefijos. Alinear Φ como en el comparador y conservar χ sin giro. La lectura alternativa interpola $q_\ell/r^\ell$ y su velocidad por extensión par y reconstruye $r^\ell$. Publicar ambas lecturas y su diferencia para cada métrica.

Para cada métrica y reloj, medir $D_{01}$ y $D_{12}$ en la secuencia R0, R1, R2, $D_t$ entre R2 y T y $D_\epsilon$ entre R2 y EPS. Comprobar $D_{12}<D_{01}$ o que ambos sean ≤ $10^{-10}$. Usar $U=D_{12}+D_t+D_\epsilon$ como estimación empírica conservadora de la variación observada. Una discrepancia $D$ admite interpretación cuantitativa cuando $U\le0.0025$, $U<D/4$ y el control radial resulta positivo. Cuando quede al nivel de U o la sensibilidad de interpolación I sea material, informar la cota empírica conjunta $D+U+I$ y el margen del 2 %. Conservar el valor oficial y su puerta de 0,02. Señalar si dicho margen también es robusto a U e I. Estos contrastes acotan el caso registrado hasta τ160. Las pruebas de estabilidad temporal de P4 y robustez quedan pendientes para la decisión de CP12.

[Protocolo acordado](../tercera_malla_20261116/SIGUIENTE_CONTRASTE.md) · [Cierre de la tercera malla](../tercera_malla_20261116/RESULTADO.json)
