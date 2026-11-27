# Error forzado en el volumen, s = 0…40

**Decisión.** La respuesta estática a la carga se verifica en la malla FV. En cambio, el presupuesto de error en norma global no consigue garantizar que los campos permanezcan a distancia puntual 10⁻⁴ de la trayectoria de referencia. Ya falla la condición suficiente en el primer extremo de ambos muestreos. El piloto sigue sin habilitarse. El cálculo acota una diferencia entre trayectorias aisladas y no mide transporte físico.

[Protocolo anterior al cálculo](PROTOCOLO.md) · [Hessiano y huecos utilizados](../hessiano_contacto_20261127/README.md) · [Método ejecutable](medir.py) · [Resultados](resultado.json) · [Envolventes por intervalo](envolventes.csv.gz)

## Fuentes y resto temporal

La reconstrucción usa los dos estados τ300 primarios dt0005, cuya huella se contrasta con el manifiesto, el perfil CP03 a ω=0,900, las masas y fuerzas M2 y el integrador afín publicado. R=256, dr=0,025 y paso de integración tangente 0,0025. Para cada intervalo de longitud h, posición y velocidad coinciden en ambos extremos con las de la referencia. Las cotas se refieren a esta extensión continua explícita y a la solución M2 semidiscreta con el mismo dato inicial y borde radial. Los dos valores de h definen extensiones ligeramente distintas.

Los cuatro coeficientes de Bernstein de posición son x₀, x₀+h p₀/3, x₁−h p₁/3 y x₁. Diferencias sucesivas dan la velocidad y aceleración. Se elevan sus grados hasta tres para calcular el defecto de aceleración frente a la ecuación afín. Su norma se acota por la mayor norma de sus cuatro coeficientes. La convexidad por celda también acota |a+ib| y |y| en todo el intervalo. Esas dos envolventes se sustituyen en el polinomio de Taylor exacto de la [referencia radial](../referencia_radial_contacto_20261127/README.md). La parte imaginaria solo recibe δK b, lo que permite acotar la proyección de carga sin asignarle toda la fuerza. El defecto temporal incluye el error de la trayectoria numérica: se evalúa la ecuación en el puente, sin hipótesis de que los nodos sean la trayectoria tangente exacta.

| Donante | h | Integral superior del defecto temporal | Integral superior de Taylor | Integral superior de la proyección sobre carga |
|---|---:|---:|---:|---:|
| Cargada | 0,250 | 4,00977 | 0,348362 | 2,51549e−5 |
| Cargada | 0,125 | 2,02365 | 0,338253 | 1,89532e−5 |
| Gemela | 0,250 | 7,02911e−4 | 1,28858e−4 | 1,76836e−5 |
| Gemela | 0,125 | 3,55654e−4 | 1,28807e−4 | 1,59517e−5 |

Son integrales de mayorantes sin cancelación, en norma canónica radial con volumen 4πW; la carga usa la normalización tangente unitaria del Hessiano. La sustitución directa en la aceleración M2 en los 960 puntos medios dio siempre un cociente norma real/mayorante inferior a 0,453 y respetó la cota de proyección. El argumento entre muestras procede de los coeficientes del polinomio, además de este contraste independiente.

## Separación de la carga y la fase

En la notación del Hessiano, C=A+4ω²vvᵀ. Usando una resolución dispersa de A y su actualización de rango uno se obtiene Cκ=2ωv con residuo absoluto 3,37e−13. Se midieron ‖κ‖₂=0,79534000, ‖κ‖C=1,00693674 y γ=1−2ωvᵀκ=−0,01392160. El interpolante original conserva su defecto ε=‖Pu‖=3,59504e−6. Los valores proceden de la malla FV de la referencia.

Para el error en variables rotantes sean X=x−κq, b=B+uβ, B perpendicular a u y q=uᵀpᵦ+2ωvᵀx. Sea D la raíz de la suma de las formas XᵀCX, BᵀPB y las normas cuadradas de la velocidad de amplitud y de la velocidad de fase perpendicular. La corrección introduce −κq̇ en Ẋ. Por reconstrucción x=X+κq y β̇=γq−2ωvᵀX. Con el hueco conservador k=0,17, la norma del desplazamiento canónico completo está acotada por S=√(2/k)D+‖κ‖₂|q|+|β|.

Al derivar la energía las partes giroscópicas transversales se cancelan. Para fuerza total F quedan las desigualdades Ḋ≤‖F‖+‖κ‖C|q̇|+ε|β| y |q̇|≤|uᵀFᵦ|+ε(D/√k+|β|). Se usa |β̇|≤|γ||q|+2ωD/√k. Se propaga el sistema de comparación positivo por exponencial en cada intervalo, desde error inicial cero. El archivo de resultados separa la cota de la ecuación lineal forzada por el defecto prescrito de la prueba con realimentación no lineal. La reconstrucción del extremo incorpora κq y la fase común.

## No linealidad y límite de la estimación

Dentro del tubo puntual propuesto, el teorema del valor medio acota la fuerza adicional por L S. L es el supremo mayorado del jacobiano de la fuerza restante tras sustraer el Hessiano fijo. Si U e Y acotan los desplazamientos complejo y real respecto del equilibrio, ampliados por el radio del tubo, y d=2|f|U+U², los bloques diagonales canónicos se acotan por 6λd+|g+hₘz|Y+hₘY²/2 y hₘd. El acoplamiento se acota por √2[(|g+hₘz|+hₘY)U+hₘY|f|], donde hₘ es el coeficiente mixto M2. Se utiliza la máxima suma por fila de bloques. La misma contribución LS acota la proyección adicional de carga. El factor S/min√(4πW) convierte la cota global en una suficiente por celda. Al resultar demasiado grande ya en s=0,125 con la reconstrucción fina, no se prolonga el argumento condicional. Esto no demuestra que el error real saliera del tubo.

Para todo s de la ventana queda una cota no lineal independiente: completando el cuadrado en χ, el potencial reducido satisface Uef≥μ²|Φ|², μ²=0,74874213. La energía inicial M2 semidiscreta E₀ se conserva, así que ‖Φ‖≤√(E₀/μ²) y ‖χ‖≤√(2E₀)/M+|g|‖Φ‖/(2M√hₘ), usando el máximo de t/(M²+hₘt²). Sumando el máximo de la norma del interpolante por Bernstein, la cota para el error de campos en L² canónico es menor que 147,50 para las dos donantes. Su validez cubre el volumen y cada subvolumen por restricción. No controla con precisión la fuerza del contacto ni los flujos de energía y carga en r60. Las evaluaciones numéricas son en doble precisión; no se empleó aritmética de intervalos para certificar redondeos.

**Siguiente frente defendible del mismo contacto.** Localizar el defecto temporal y de Taylor por radio y componente en las trayectorias ya preparadas; medir qué parte corresponde a χ rápido y a la región exterior al solapamiento, y qué parte queda en las zonas que pesan en S y H. Antes de otra propagación, comprobar si un presupuesto espacial ponderado con su término de flujo entre regiones y con la cola del operador FV puede mejorar la cota. No suprimir la fuente exterior por un corte causal exacto en la malla. Si la fuerza relevante o el flujo de error siguen sin control, conservar la indeterminación. Se mantienen las puertas de energía 1,66414371e−6 y carga 1,84762579e−6 y los requisitos de atribución, captura y entrega a la receptora.

Reproducción desde este directorio: ejecutar `OPENBLAS_NUM_THREADS=1 python3 medir.py`, comparar resultado.json y contrastar el SHA-256 de envolventes.csv con el registrado; la versión publicada del CSV se distribuye comprimida sin pérdida.
