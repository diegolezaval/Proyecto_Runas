# Cargada · error que entra en la corona por r40

**Resultado del paso 3.** Para la parte lineal prescrita de la referencia corregida, el levantamiento estático reduce de 8,949 a 0,1389 la cota de amplitud energética atribuida a la entrada por r40 en s=40 (valores redondeados hacia arriba). Incluye 0,007597 de restitución al extremo. Ambas estimaciones pierden precisión al convertir la energía de toda la malla en una traza interior. Sigue abierta la contribución no lineal. El diagnóstico no acredita una predicción conjunta de salida en r60. El piloto, la captura y la recarga siguen pendientes.

[Protocolo previo](PROTOCOLO.md) · [Protocolo de trazas](PROTOCOLO_TRAZA.md) · [Cálculo reproducible](interfaz.py) · [Valores numéricos](resultado.json) · [Datos por intervalo y controles de carga](../energia_fisica_corregida_20261127/README.md)

## Dato que entra desde el núcleo

En la cara r40 la primera celda exterior tiene centro 40,0125 y su vecina interior está en 39,9875. En ésta, z es el **error de campo** en las coordenadas físicas (√2 Re Φ, √2 Im Φ, χ) del marco rotante. En las celdas exteriores x lleva además el factor √(4πw). El corte conserva la diagonal del laplaciano y la pared exterior a media celda. El mínimo del potencial rotante exterior es 0,1900. La fuerza del centro vecino es Bz, con B diagonal por campo en la primera celda y coeficiente 35860,73672.

Sea K el Hessiano exterior, L la solución de KL=B y G la giroscopia antisimétrica. Al poner y=x−Lz y conservar v como velocidad original, las ecuaciones son y′=v+rₓ−Lz′ y v′=−Ky+Gv+F. El trabajo de la traza en la energía sin peso es −⟨K y,Lz′⟩. La norma de K½L vale 891,64691 y la de L en desplazamiento vale 150,99282. Con los datos iniciales coincidentes, x(0)=v(0)=z(0)=0. En otro arranque se requiere la energía inicial de (x(0)−Lz(0),v(0)). Al extremo se reconstruye x=y+Lz. Con pesos positivos ≤1, el potencial exterior positivo y la media por cara dan Kₖ≤K como formas, también en la celda de borde. Esto permite usar la misma cota para la fuente cinemática y la restitución. La prueba independiente de la matriz LᵀKL suma todas las caras, las dos conexiones a cero y el potencial. El residuo de KL=B y las pruebas de ecuaciones y trabajo con z y z′ distintos quedan por debajo de 3e−15 en error relativo.

## Peso móvil y defecto en la transición

Para s en [0,40], kᵢ=exp(−α max(rᵢ−100+s,0)), α=0,2. La energía Eₖ usa kᵢ en cinética y potencial, y (kᵢ+kⱼ)/2 en los saltos. Los dos bordes toman el peso de su centro. En la corona 40–60 el peso por celda vale uno; las caras internas de la corona también tienen peso uno. La afirmación cubre estas porciones positivas de energía; no atribuye a la corona la cara compartida con la celda situada más allá de 60.

Sea dᵢ=−kᵢ′, igual a 0 o αkᵢ salvo en los instantes de paso por un centro. Al derivar Eₖ, el trabajo espacial por cara es c(kᵢ−kⱼ)Δx·(vᵢ+vⱼ)/2 en campos físicos, omitiendo el factor común 4π. El término temporal resta energía cinética, potencial y de gradiente. Para Eₖ′≤γEₖ basta que en cada celda se cumpla

    Σⱼ cᵢⱼ(kᵢ−kⱼ)² / (dᵢ+dⱼ+γ(kᵢ+kⱼ)) ≤ wᵢ(dᵢ+γkᵢ).

Se obtiene completando el cuadrado de cada salto y usando |vᵢ+vⱼ|²≤2(|vᵢ|²+|vⱼ|²). Las caras con k constante no generan trabajo. En los bordes las fuerzas homogéneas se cancelan con el gradiente de su conexión a cero. La giroscopia hace trabajo nulo en cada celda.

Para un control uniforme, sea C el máximo c/w de ambos extremos de las caras afectadas, multiplicado por exp(αdr)(exp(αdr)−1)². En unidades de wᵢkᵢ, cada cara mixta cuesta a lo sumo m=C/(α+2γ), y cada cara de cola cuesta t=C/(2α+2γ), pues la razón entre pesos vecinos está entre exp(−αdr) y exp(αdr). Basta comprobar γ≥m, α+γ≥m+t y α+γ≥2t. Con γ=0,102 los tres márgenes superan 0,00195. La desigualdad integrada atraviesa los cambios de centro por continuidad. Un estado de prueba a s=20 concentra velocidad en el último centro plano y desplazamiento de fase en el siguiente. Produce Eₖ′/Eₖ=+0,00790544. Por tanto, suponer compensación exacta en la transición infravaloraría el error.

## Fuentes de la referencia corregida

Se usaron los mismos 320 intervalos de 0,125 de gota_a010. En cada uno se aplica el peso máximo y el tiempo restante máximo al mayorante ajustado que ya cubre el interior del intervalo. La tabla muestra contribuciones individuales a √(2Eₖ) al final, redondeadas hacia arriba. Los costes próximos incluyen toda la fuente archivada de r<60 como mayorante para 40–60. Las cotas fijas conservan el tiempo de cada intervalo, por lo que son más finas que aplicar un único factor máximo a las 40 unidades.

| Procedencia | Peso fijo | Peso móvil |
|---|---:|---:|
| 40–60, usando todo r<60 | 5,958e−8 | 1,941e−8 |
| 60–160 | 6,019e−5 | 1,057e−5 |
| 160–256 | 4,063e−8 | 1,762e−7 |
| Defecto de posición en norma del Hessiano | 2,452e−16 | 5,985e−17 |
| Defecto de velocidad | 1,915e−16 | 4,675e−17 |

El peso móvil mejora la estimación de la banda cercana; el fijo atenúa más la fuente lejana al inicio. La norma del defecto de posición usa la raíz de la máxima suma absoluta por fila de K. La de velocidad entra en la norma de volumen. Se mantienen los límites numéricos del defecto formal y el redondeo en doble precisión de la fuente publicada.

## Dos presupuestos de la traza lineal

Para la solución forzada **lineal** en toda la malla se usan los extremos no decrecientes de D, |q| y |β| del sistema de comparación archivado. Para z se usa el telescopaje desde la pared, con la resistencia Rᵢ=Σⱼ≥ᵢ(4πcⱼ)⁻¹ y la cota del gradiente reducido (1+max(0,−Vmin)/0,17)D². Se restituyen los valores locales de κq y de uβ. Para la derivada, la norma de la velocidad transversal está acotada por D. La velocidad imaginaria paralela contiene u[(1−2ωvᵀκ)q−2ωvᵀX]. A ambas se aplica el factor de volumen del centro interior y se suma allí el defecto cinemático del intervalo. Esto conserva por separado la fuerza sobre q̇ y la fase del sistema físico de partida. En el exterior no se impone carga fija por separado a cada lado de la cara.

Si se reconstruyen carga y fase desde variables ponderadas con S=√k, el error del vector usado en la proyección tiene norma ‖(S⁻¹−I)u‖≤2,051e−11, y ‖(S′/S)u‖≤1,044e−11 a lo largo del movimiento. Se conserva el defecto de fase FV ‖Pu‖≈3,59504e−6. Las trazas de esta entrega usan las proyecciones físicas sin peso y los términos de carga, fase y truncación de la comparación publicada.

Las integrales simples de los mayorantes de |z| y |z′| valen 1,27055e−4 y 7,49476e−5. Al propagar con exp(0,102(40−s)/2) suben a 2,49525e−4 y 1,47192e−4. La segunda ruta paga además ‖K½L‖ |z(40)|, con |z(40)|≤8,51933e−6. La entrada lineal de toda la malla ya responde a las fuerzas del exterior; si se combina por desigualdad triangular con esas fuentes, puede haber sobreestimación. Estos números tienen unidades de amplitud del error. Las fuerzas no lineales dependientes del error requieren tanto su contribución exterior como su efecto sobre la traza del núcleo. Las dos rutas no dan una cota no lineal cerrada.

**Siguiente comprobación del mismo contacto.** Antes de otra corrección, medir cuánto de la pérdida de precisión de la traza procede de usar D de toda la malla. Una opción verificable es proyectar el propagador adjunto del generador lineal FV completo desde el centro 39,9875 sobre cada banda de fuente, para posición y velocidad por separado. Incluir el defecto cinemático directo en z′, el resto temporal entre muestras y un control de discretización independiente de cada núcleo de propagación. La reciprocidad con fuerzas de prueba ofrece un contraste. Conservar el presupuesto anterior si la propagación adjunta no mejora la traza. Para la realimentación siguen haciendo falta un tubo autoconsistente y los balances conjuntos de contacto. Los mínimos de misión permanecen en E≥1,66414371e−6 y Q≥1,84762579e−6.

**Resumen para el Dot principal.** Diego, al conservar por separado la traza en r40 y su derivada, el levantamiento baja su cota lineal de 8,949 a 0,1389. La banda 60–160 sigue pesando más que la fuente lejana con el peso móvil. Falta resolver mejor la traza de la cargada y cerrar la realimentación antes de evaluar una descarga. [Resultado y método](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/interfaz_cargada_20261127)

Para reproducir desde la raíz, ejecutar `OPENBLAS_NUM_THREADS=1 python3 checkpoints/Reserva/interfaz_cargada_20261127/interfaz.py` y comparar resultado.json con el blob publicado.
