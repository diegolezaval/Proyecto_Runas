# Traza adjunta de la cargada en r=39,9875

[Protocolo](PROTOCOLO.md) · [Seis semillas y presupuesto por banda](adjunta.py) · [Contraste directo en la malla completa](pulsos.py) · [Valores reproducibles](resultado.json) · [Presupuesto anterior de la interfaz](../interfaz_cargada_20261127/README.md)

## Qué se calcula

Se estima la parte lineal del error de la referencia aislada de la cargada que alcanza la celda inmediatamente interior a r40. Los insumos son la malla radial FV de R256, dr=0,025, la pared a media celda, el equilibrio y las fuentes canónicas ajustadas con cobertura entre muestras en los 320 intervalos de la primera referencia corregida. No se evoluciona M2. Para potencial y laplaciano se usan los mismos bloques del Hessiano rotante libre. En la malla completa el núcleo y la corona intercambian por la cara interior sin imponer una traza artificial allí.

Para G(x,v)=(v,−Kx+Ωv), el adjunto euclídeo canónico cumple pₓ′=−Kpᵥ y pᵥ′=pₓ−Ωpᵥ. Con w=pᵥ se tiene w″=−Kw−Ωw′ y pₓ=w′+Ωw. La involución R cambia el signo imaginario. RKR=K y RΩR=−Ω se verifican entrada por entrada. Así (Rw,Rw′) se propaga con el generador directo. Para las tres filas de posición, (w,w′) parte de (0,e); para las tres de velocidad parte de (e,−Ωe). Cada vector e selecciona la celda y divide por la raíz de su volumen 4πwᵢ. El resultado es una traza de (√2 Re Φ,√2 Im Φ,χ) en unidades físicas del campo. El defecto cinemático entra por pₓ en todo el historial y directamente en z′ en el instante observado.

## Cotas en la malla y entre muestras

Se evalúa el polinomio de Taylor de orden 48 cada 1/32. Para cada grupo de tres salidas se suman, banda por banda, las normas de Frobenius de sus coeficientes multiplicados por la potencia máxima del tiempo local. Esto cubre todas las fases de muestreo sin presuponer cancelación. En cada par de intervalos de fuente y observación se usa el máximo sobre ambos intervalos posibles de retardo. Los valores de z terminal publicados acotan también el último intervalo. La fuerza lejana se mantiene en el presupuesto aunque su soporte quede fuera del cálculo restringido.

Para limitar el coste se aplica el bloque principal de K hasta r=104, conservando su diagonal FV. Extender por cero solo introduce una fuerza en la primera celda omitida, de norma acotada por el coeficiente canónico de la cara por la norma del último w. Se incluye su integral con crecimiento en **toda** la malla. En la norma de energía desplazada N²=‖v‖²+⟨w,(K+I)w⟩, la curvatura local publicada asegura K+I≥0,590 I. La derivada de N²/2 para la ecuación homogénea es ⟨v,w⟩. Así N(t)≤exp(μt)N(0), μ=1/(2√0,590). La norma del generador se acota por √(1+‖K‖∞)+1/√0,590+2ω, separando el generador de onda para K+I del desplazamiento y de la giroscopia.

Con b igual a esa cota y h=1/32, el resto relativo de un paso es a≤exp(bh)(bh)^49/49!. La energía de los estados numéricos ideales queda por debajo de N(0)(exp(μh)+a)^1280. Se acumula el error de los pasos con exp(40μ), se añade el resto dentro de cada paso y se carga también su efecto sobre la cara omitida. La estimación de pₓ usa el factor 1+2ω/√0,590 y la de pᵥ usa 1/√0,590. Son cotas de truncación en aritmética exacta, evaluadas en doble precisión. No se certificó el redondeo flotante. La exponencial dispersa usa el generador adjunto original en la malla completa; los pulsos largos usan el avance directo original y dos pasos temporales, sin fuente afín. El pulso de r≥160 comprueba que una respuesta lejana muy pequeña es compatible con los controles; no mide transporte físico.

## Presupuesto y alcance


El primer control formal aplicó el crecimiento máximo de 40 unidades tanto al estado que genera cada defecto como al tiempo posterior a ese defecto. Dio 0,04838 de resto energético y 1,109e−4 para la integral simple de |z′|. Se conserva como contraste. Se afinó únicamente esa desigualdad: para un defecto generado en t se multiplican el crecimiento hasta t y el crecimiento desde t al extremo. El producto de ambos tiene una sola ventana de 40 unidades. Si A=N(0)(exp(μh)+a)^1282, un mayorante uniforme del error de los nodos, incluida la interpolación local y ya transportado al extremo, es 1281aA. Para la cara truncada se añade este término multiplicado por 40|Kₙ,ₙ₋₁|/√0,590 y la envolvente medida en la última celda multiplicada por 40 exp(40μ)|Kₙ,ₙ₋₁|. Esta afinación conserva el mismo orden, el mismo paso y todas las fuentes.

Con un único horizonte de crecimiento, el resto formal en la energía de los seis núcleos es ≤3,128e−10. La exponencial dispersa de Gᵀ en s=0,125 coincide con las seis semillas con error relativo inferior a 8,0e−15. En s=32 se comparó además el producto adjunto contra la exponencial directa de G sobre tres pulsos compactos de velocidad, uno por banda, en toda la malla. La discrepancia absoluta máxima fue 7,73e−16. El pulso intermedio sí llega con respuesta resoluble, de hasta 6,32e−4. El pulso lejano dio cero a la precisión del contraste; la cota retiene su resto positivo.

Se conserva un contraste desfavorable. Con el avance directo de patadas y derivas publicado, los pasos 0,005 y 0,0025 dieron errores máximos 1,32e−3 y 6,39e−4 para el pulso interior a s=32. La diferencia dominante a paso fino fue en velocidad de χ. Esos pasos no justifican usar ese avance como referencia precisa de los seis canales. La comprobación con exponencial directa empleó los mismos pulsos y otra representación del generador, escalando la velocidad por 100 para calcular la exponencial.

| Contribución al último intervalo | Cota de posición | Cota de velocidad integrada por Duhamel |
|---|---:|---:|
| Fuerza ajustada r<60 | 1,313e−10 | 1,057e−8 |
| Fuerza ajustada 60≤r<160 | 7,212e−9 | 1,728e−7 |
| Fuerza ajustada r≥160 | 4,557e−14 | 4,557e−14 |
| Defecto cinemático en el historial | 1,882e−19 | 2,174e−17 |
| Defecto de velocidad en el historial | 2,364e−19 | 1,882e−17 |

El error lineal parte de cero. La traza terminal satisface |z(40)|≤7,343e−9. La cota para la integral de |z′| es **1,891e−6**, incluido el defecto cinemático directo (≤6,34e−21). Al propagarla hasta el extremo con exp(0,051(40−s)) sube a **2,783e−6**. Ambas caben en el cribado provisional de 3,96e−6. La ruta directa con Bz cuesta ≤0,004800 de amplitud energética. La levantada cuesta ≤0,002488, incluida la restitución terminal ≤6,548e−6. La estimación anterior de la ruta levantada era 0,1389. Las cotas de cada fila se redondearon hacia arriba.

**Decisión.** El cribado de la entrada lineal por r40 permite pasar a la realimentación de la cargada dentro de este diagnóstico. Las fuentes exteriores prescritas, la realimentación y las puertas conjuntas siguen teniendo presupuestos separados. Esta prueba usa la referencia aislada. Para fijar H variable en el contacto aún se requieren control de volumen y de los factores de solapamiento, inventarios y balances locales. El piloto continúa pendiente; se mantienen E≥1,66414371e−6, Q≥1,84762579e−6, atribución en r60 y entrega útil a la receptora.

**Siguiente cálculo.** Recuperar para la cargada las envolventes por celda de la primera corrección y formar el mayorante por banda del jacobiano no lineal en el tubo 1e−4. Probar primero, por intervalos desde cero, una comparación acoplada de núcleo, corona y exterior que alimente las dos trazas con esa fuerza por banda. La realimentación requiere cotas del desplazamiento en cada banda; una traza aislada en r40 no las proporciona. Mantener carga tangente y fase común, las fuentes cercanas y la contribución exterior directa. Contrastar anulando solo la realimentación para recuperar esta entrega. Registrar el primer intervalo sin cierre si la comparación pierde resolución, sin extrapolar el prefijo.

**Resumen para el Dot principal.** Diego, la cota lineal propagada de la integral de |z′| en la interfaz de la cargada baja a 2,783e−6, dentro del cribado provisional. El coste del levantamiento baja de 0,1389 a 0,002488. Queda abierta la realimentación antes de evaluar el contacto. [Resultado y controles](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/adjunta_cargada_20261127)

Reproducción desde la raíz con NumPy, SciPy y un compilador C: ejecutar `OPENBLAS_NUM_THREADS=1 python3 checkpoints/Reserva/adjunta_cargada_20261127/adjunta.py` y comparar resultado.json con el blob de la rama.
