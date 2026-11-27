# Referencia radial aislada del contacto, s = 0…40

**Decisión.** La referencia tangente conserva precisión empírica en cuatro inventarios diferenciales de las donantes aisladas. La estimación de estabilidad disponible deja indeterminado su error en el volumen de contacto. Sigue pendiente la predicción de la salida conjunta y no se habilita el piloto.

El [protocolo](PROTOCOLO.md) se publicó antes del cálculo en `4cf83ee4c6bc550ee1b1fc40834f7eedb7b980b5`. La [auditoría de cobertura](../cobertura_contacto_variable_20261126/README.md) explica por qué hacen falta perfiles interiores y qué observan las sondas. Se usan el perfil CP03 de ω=0,900, los cuatro estados de τ300 de la cargada y la gemela (dos preparaciones), los pesos de volúmenes finitos del paso 2 y las sondas e inventarios principales sin paquete del ensayo archivado. El programa coteja los SHA de estados y series con sus manifiestos y registra la huella del perfil.

## Método

Con Φ=exp[i(α+ωs)](f+a+ib) y χ=z+y, se alineó α con el campo central de cada preparación. Se reconstruyeron los seis campos y velocidades iniciales. Se usó el perfil de equilibrio interpolado por Hermite en la malla de preparación R256, dr=0,025. El operador incluye el defecto discreto de estacionariedad del perfil, cuyo máximo en Φ y χ es 4,10×10⁻⁶ y 8,20×10⁻⁷. Con A igual al laplaciano radial negativo y K=m²+2λf²+gz+hz²/2, la aceleración de u=a+ib incluye −Au+(ω²−K)u−4λf²a−(g+hz)fy−2iωu̇ y el defecto del fondo. La de y incluye −Ay−(mχ²+hf²)y−2(g+hz)fa y el defecto de χ. Se integró este sistema afín por composición simétrica, con rotación giroscópica exacta en cada subpaso. La aceleración no lineal publicada se evaluó únicamente para contrastar el residuo en tres instantes.

R256 tiene regularidad en el origen y pared exterior. Las sondas primarias y sus inventarios proceden de la caja R512, con igual espaciado. El contraste se limita a las regiones interiores y al horizonte corto estipulados. Se registraron ocho trayectorias con pasos 0,005 y 0,0025, estados de preparación dt0005/dt001 y muestras cada 0,25. La comparación con el archivo emplea su preparación dt0005. Las cuatro sondas complejas se sitúan a ambos lados de r40 y r60.

## Resultados

Cada fila compara la pérdida de inventario de la cargada menos la de la gemela desde s=0. La mayor discrepancia entre la referencia fina y el archivo ocurrió en s=40 en los cuatro canales. Las sensibilidades son máximos sobre los 41 tiempos enteros al cambiar solo uno de los pasos.

| Canal | Referencia en 40 | Archivo en 40 | Error máximo | % del umbral de misión | Cambio de paso tangente | Cambio de preparación |
|---|---:|---:|---:|---:|---:|---:|
| E(r40) | 7,29488e−7 | 7,16589e−7 | 1,28989e−8 | 0,7751 | 2,80e−9 | 1,36e−9 |
| Q(r40) | 7,15992e−7 | 7,01632e−7 | 1,43600e−8 | 0,7772 | 3,11e−9 | 1,34e−9 |
| E(r60) | 3,54513e−6 | 3,53318e−6 | 1,19494e−8 | 0,7181 | 2,80e−9 | 6,25e−10 |
| Q(r60) | 3,36956e−6 | 3,35589e−6 | 1,36670e−8 | 0,7397 | 3,11e−9 | 6,80e−10 |

El denominador es 1,66414371e−6 para E y 1,84762579e−6 para Q. Estas son pérdidas de estados aislados. Para la misión se necesita separar el transporte causado por el contacto, la fuga espontánea, el inventario exterior inicial y el trabajo de preparación, y verificar los balances por núcleo y la receptora. El error máximo en las sondas complejas a paso fino es 1,01e−8 en la cargada y 6,00e−11 en la gemela (redondeados hacia arriba).

## Residuo y estabilidad

En el marco rotante el residuo R es aceleración lineal menos aceleración M2, con δK=2λ(2fa+|u|²)+(g+hz)y+hy²/2. Se obtiene RΦ=f(2λ|u|²+hy²/2)+δK u y Rχ=(g+hz)|u|²+h(2fa+|u|²)y. Se contrasta por sustracción directa en s=0,20,40. En las muestras de la referencia fina principal, la norma dinámica L² radial de R con pesos canónicos (2,1) alcanza 9,30e−3 en la cargada y 3,10e−6 en la gemela (cotas redondeadas); limitada a r≤160, 3,21e−3 y 3,10e−6.

La fuente de carga de la trayectoria aproximada es 2 Im(Φ* RΦ) y la de energía es 2 Re(Φ̇* RΦ)+χ̇Rχ, con ambas magnitudes complejas en el mismo marco y velocidad física. Al integrar la diferencia cargada menos gemela por trapecios en el tiempo se obtienen −1,3260e−8 y −1,3261e−8 en E(r40,r60), y −1,4734e−8 en ambos cortes de Q. El signo predice un aumento de la pérdida aparente y la escala concuerda con la discrepancia observada. Esta comprobación por muestras deja pendiente acotar el residuo entre ellas y la diferencia de flujos.

Para la ecuación tangente homogénea en variables canónicas inerciales, sea M la diagonal positiva de masas y D el hessiano del potencial menos M². La rotación del fondo preserva la norma de DM⁻¹. La derivada de la energía de vacío satisface |Ė₀|≤L E₀ por Cauchy y 2ab≤a²+b², con L=maxᵣ‖DM⁻¹‖₂=1500,03348. Así la amplitud energética lleva exp(Ls/2), con log₁₀ del factor igual a 13029,13 a s=40. Esta cota superior carece de resolución para la misión. Tampoco certifica el resto no lineal sobre la solución verdadera. Las sondas y los inventarios aislados no determinan χ, S, H ni la retroacción sobre Φ en el volumen de solapamiento.

## Siguiente decisión

Evaluar si la segunda variación discreta de E−ωQ controla el propagador radial al separar el modo de fase y llevar explícitamente la perturbación de carga de cada donante. Comprobar el signo del menor modo en el espacio restringido, el defecto de la simetría por interpolación y la estabilidad frente a malla antes de usarla para un residuo forzado. Una constante útil todavía requeriría un recinto del defecto entre muestras, estabilidad no lineal y balances de contacto. Siguen vigentes los controles y umbrales anteriores.

## Reproducción

Desde este directorio, ejecutar `OPENBLAS_NUM_THREADS=1 python3 medir.py` y `OPENBLAS_NUM_THREADS=1 python3 verificar.py` con NumPy, SciPy y un compilador C. [Resultados](resultado.json) · [1.288 muestras en CSV comprimido](series.csv.gz) · [Control con exponencial matricial y series primarias](verificar.py). El verificador compara la propagación con una exponencial afín independiente, comprueba reversibilidad y recalcula 164 diferencias a partir de los dos archivos primarios.
