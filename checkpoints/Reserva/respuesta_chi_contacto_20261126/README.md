# La deformación estática de χ reduce la fuerza de contacto en Φ

Al permitir que el mediador χ se deforme con los dos núcleos presentes, la norma de la aceleración adicional en Φ baja al **0,483–0,530 % de su valor original** en los 36 casos de la malla fina. La disminución se mide en la ecuación del campo cargado, independiente de la ecuación elíptica usada para ajustar χ. Esta es una mejora de la descripción del contacto en la instantánea de τ300. La energía y la carga entregadas a una receptora durante la ventana siguen indeterminadas. El piloto continúa sin habilitarse. [Protocolo anterior al cálculo](PROTOCOLO.md)

## Qué se resolvió

D y R son los dos perfiles cargados con la fase relativa ya aplicada; z e y son sus mediadores aislados. Escribimos sD=|D|², sR=|R|², I=2 Re(D*R), s=sD+sR+I y χ₀=z+y. En esta notación g designa el acoplamiento trilineal, h el mixto y M la masa del mediador en unidades de M2. Al restar de la aceleración conjunta de χ las aceleraciones de los dos estados aislados, queda la fuente de contacto

    S = −g I − h [sD y + sR z + I χ₀].

La corrección que cancela esta fuente, manteniendo Φ fijo, satisface H w=S con H=−Δ+M²+h s. Se usaron volúmenes finitos cilíndricos y el producto escalar de volumen anular. La positividad del operador proporciona el control ||w|| ≤ ||S||/M². Para un núcleo aislado, la expresión de S se anula. La corrección a la aceleración en Φ se evaluó directamente como −[(g+hχ₀)w+h w²/2](D+R), sumada a la fuerza de contacto original. Es un múltiplo real del campo. Por ello, al cambiar solo χ, permanece intacta la corriente instantánea de carga y también se anula la contribución de esta corrección a 2 Im(Φ* Φ̈). Para modificar el flujo de carga durante una ventana es necesaria la respuesta temporal de Φ.

## Qué cambia en las preparaciones

La tabla mantiene la donante cargada, el paso de preparación 0,0005 y la fase +π/2. Los rangos del párrafo inicial incluyen las dos donantes, ambas preparaciones y las tres fases.

| Separación | Norma residual en Φ / norma original | Norma de ẅ / norma de S | Energía cuadrática de deformación, M2 | Cambio total de energía al imponer el seguimiento, M2 |
|---:|---:|---:|---:|---:|
| 80 | 0,5264 % | 0,01663 % | 3,9344 × 10⁻⁷ | −3,9062 × 10⁻⁷ |
| 100 | 0,5195 % | 0,04458 % | 4,9407 × 10⁻⁷ | −4,9395 × 10⁻⁷ |
| 120 | 0,5260 % | 0,05337 % | 2,1133 × 10⁻⁶ | −2,1163 × 10⁻⁶ |

La energía cuadrática C=⟨w,Hw⟩/2 es positiva y se cotejó por dos vías, el trabajo de la fuente ⟨w,S⟩/2 y la suma de gradientes por caras y términos de masa. La diferencia de energía física entre el montaje corregido y el montaje por superposición incluye además el término lineal ⟨Hχ₀+g s,w⟩. Si se impone la velocidad de seguimiento, se añade ⟨χ̇₀,ẇ⟩+||ẇ||²/2. El signo negativo en la tabla indica menor energía de la preparación corregida a igualdad de Φ y Φ̇. Realizar esa preparación requeriría contabilizar el destino de la energía retirada y el trabajo del mecanismo de montaje. El coste de generar las donantes y de la superposición inicial es común a esta comparación incremental.

Tomando primero la semidiferencia de fases opuestas y luego cargada menos gemela, los cambios totales de energía de montaje son +2,8041 × 10⁻⁹, −7,2849 × 10⁻¹¹ y −4,1173 × 10⁻⁹ M2 a separaciones 80, 100 y 120. Son diferencias de preparación. El término cuadrático bruto a d=120 supera numéricamente el umbral energético de misión de 1,66414371 × 10⁻⁶; ese dato por sí solo carece de información sobre la entrega a través de una cara o sobre el umbral de carga de 1,84762579 × 10⁻⁶.

## Qué se sabe del error dinámico

En las trayectorias aisladas de referencia, las dos derivadas de la forma cuasiestática se obtienen en un instante por H ẇ=Ṡ−Ḣw y H ẅ=S̈−2Ḣẇ−Ḧw. Se usaron velocidades publicadas, aceleraciones de las ecuaciones M2 y derivadas radiales de los interpolantes. Al sustituir ese seguimiento en la ecuación de ondas del mediador queda el defecto ẅ. En la malla fina, ||ẅ||/||S|| va de 1,30 × 10⁻⁵ a 5,34 × 10⁻⁴. Esta medida corresponde a τ300 y a las trayectorias aisladas empleadas para diferenciar. Los datos de superposición originales parten de w=0 y velocidad añadida cero. Incluso con una fuente constante, alcanzar el estado estático exigiría estudiar la oscilación libre asociada a ese desajuste inicial. Para una ventana finita faltan además la variación de la fuente y la retroacción en Φ. El defecto instantáneo no constituye una cota uniforme.

## Controles, alcance y continuación

Se midieron 108 configuraciones de malla, caja, preparación y fase. El residuo elíptico relativo máximo de las tres resoluciones por caso (w, ẇ y ẅ) en la malla fina fue inferior a 7,2 × 10⁻¹³. El mayor desacuerdo relativo de la norma de fuerza sin corrección frente a la cuadratura independiente del estudio anterior fue 0,02382 %. Para el cociente de fuerzas en Φ, los máximos cambios absolutos entre mallas, cajas y pasos de preparación fueron 2,19 × 10⁻⁶, 1,74 × 10⁻¹⁸ y 3,02 × 10⁻⁵. En la energía incremental de montaje fueron 3,61 × 10⁻⁸, 5,30 × 10⁻²² y 1,22 × 10⁻¹¹ M2. Las cifras del cuadro son valores en malla fina. Los controles de caja y refinamiento caracterizan estas discretizaciones. El control manufacturado independiente usa una solución analítica, condiciones de borde homogéneas y tres resoluciones; el error relativo decrece en los dos refinamientos.

**Siguiente cálculo del mismo contacto.** Evaluar el transitorio debido al desajuste de montaje sobre el operador positivo H congelado, con datos iniciales −w y −ẇ respecto del seguimiento. El presupuesto de energía inicial de ese transitorio es C+||ẇ||²/2. Usar conservación de la energía de la ecuación homogénea y el hueco M² para acotar la amplitud de χ y contrastar su efecto sobre la fuerza en Φ. Separar la cota sin cancelación de cualquier predicción que dependa de cancelación de fase y declarar qué exigiría extenderla a una fuente variable. El objetivo es determinar si despreciar el transitorio es defendible antes de usar una reducción temporal; los balances de los dos núcleos y la recepción siguen pendientes. No se ha evolucionado M2 ni modificado Θ.

Para reproducir desde esta carpeta con Python 3.12, NumPy 2.3.5 y SciPy 1.17.0:

```sh
OPENBLAS_NUM_THREADS=1 python3 respuesta.py
OPENBLAS_NUM_THREADS=1 python3 verificar.py
```

[Método](respuesta.py) · [Controles independientes](verificar.py) · [Valores por preparación](medidas.csv) · [Contrastes impares y procedencia](resultado.json)
