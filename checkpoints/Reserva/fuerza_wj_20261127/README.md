# Trabajo directo de la fuerza en 10 ≤ r < 40

**El horizonte acreditado de la donante cargada en todo el volumen pasa de s=14,625 a s=14,875.** El primer rechazo está en s=15, solo en r<10. La aceptación exige un único candidato que contenga la entrada y las cinco envolventes. No se integró el contacto.

| Ensayo en s=14,75 | Cota de la fuerza no lineal en D | Cota del desplazamiento en el núcleo |
|---|---:|---:|
| Control del conmutador reproducido | 3,01322e−5 | 1,11872e−4 |
| WJ por celda, misma entrada | 6,34166e−6 | 1,05034e−4 |
| Cajas y X de toda la banda, misma entrada | 4,39976e−6 | 1,04476e−4 |
| Cajas y X desde s=13,5, con historia completa | 3,18056e−6 | 8,34452e−5 |

Los mayorantes tabulados se redondearon hacia arriba. En la última pasada del ensayo dual a entrada fija, X=2,40491e−4. En esa misma caja los techos directos en 10–40 valen 2,97876e−5 por el control previo, 4,76142e−6 por el máximo de WJ y 5,66466e−6 por las cajas solas. Su intersección por el dual da 1,44945e−6. El cambio de caja entre pasadas explica la leve diferencia con el ensayo que usa exclusivamente WJ.

Con la entrada del control y todas las otras tasas y restituciones fijas, poner a cero la fuerza no lineal de la última fila aún deja la cota interior en 1,03266e−4. Ese contraste motivó la reconstrucción causal. Las diez filas desde 13,5 hasta 14,75 cerraron y se probaron las dos siguientes conforme al protocolo. En s=14,875 el máximo es 9,88386e−5. En s=15 el del núcleo alcanza 1,18688e−4; las otras cuatro bandas quedan por debajo de 3,36740e−5. El rechazo de la comparación no determina el desplazamiento real en esa fila.

## Método

Se conservaron la caja física, las cinco bandas, las fuentes entre muestras y los radios de la [marcha del conmutador FV](../conmutador_fv_20261127/README.md). En cada pasada de la comparación se vuelven a formar el jacobiano mayorante componente a componente Uᵢ y el vector de techos pᵢ en coordenadas canónicas, con la raíz de la masa FV. La cota de desplazamiento de la banda es X. Para la norma del producto se usa bᵢ = Wᵢ √(‖Uᵢ‖₁ ‖Uᵢ‖∞). La caja proporciona el segundo techo aᵢ = Wᵢ ‖Uᵢ pᵢ‖₂.

Si tᵢ es el desplazamiento canónico cuadrático de una celda, su fuerza cuadrática es a lo sumo min(aᵢ²,bᵢ²tᵢ) y Σtᵢ ≤ X². Para λ ≥ 0, al restar λtᵢ y maximizar en tᵢ ≥ 0 queda aᵢ² max(0,1−λ/bᵢ²). Las celdas con bᵢ=0 aportan cero. Se suma λX² y se minimiza la expresión convexa por tramos. Se ordenan los bᵢ² de mayor a menor y se acumula aᵢ²/bᵢ² hasta agotar X². La ganancia marginal selecciona el mínimo entre los puntos de quiebre; si caben todas las celdas, se usa λ=0. Se evalúa la expresión dual mediante sumandos positivos y se toma la raíz al final.

El cálculo amplía las ganancias y los techos un factor 1+1e−11 y usa precisión extendida para evaluar el dual con otra holgura de 1e−11. Se conserva el mínimo con los costes ya admitidos. Se contrastan dos presupuestos de ganancia uniforme, dos celdas de ganancias distintas con saturación parcial y un caso de ganancia nula, tanto contra el óptimo analítico como por enumeración de los puntos de quiebre. La proyección en q̇ se calcula con su estimación independiente. Se conservan κq̇, fase y trabajo de caras.

El control se reconstruye desde cero y exige igualdad exacta con las filas publicadas. Los dos ensayos a entrada fija comparten los estados, historias y radios del control en el primer intervalo rechazado. El ensayo sobre diez filas conserva las primeras 108 filas y todos los historiales internos antes de aplicar la cota nueva. El descenso en la fuerza y en el punto interior a entrada fija determina si se justifica esta última prueba.

Reproducción desde este directorio con `OPENBLAS_NUM_THREADS=1 python3 medir_wj.py`. [Protocolo](PROTOCOLO.md) · [Resultados numéricos](resultado.json) · [Recibo](RECUPERACION.json)


## Continuación del mismo contacto

En la primera fila rechazada el coste de caras llega a 4,90653e−5 y el trabajo de κq̇ a 1,29423e−5, frente a 6,84057e−6 de κq̇ en la fila anterior. El siguiente contraste barato es descomponer q̇ por banda a idéntica entrada en s=15. Para la fuerza imaginaria de 10–40, intersectar la proyección anterior con la suma de los techos locales ponderados por |uᵢ| y con Cauchy aplicado a la fila imaginaria de WU y el presupuesto X. Comparar con la proyección directa publicada, conservando por separado el conmutador proyectado, los defectos y la fase. Medir el efecto sobre κq̇ y sobre el punto antes de decidir si merece otra marcha.

El resultado acredita el tubo radial aislado en el prefijo indicado. La historia parcial de la corona hasta 40 conserva sus cortes previos. Siguen pendientes la salida conjunta atribuible en r60 y la entrega útil, con mínimos de misión 1,66414371e−6 en energía y 1,84762579e−6 en carga.
