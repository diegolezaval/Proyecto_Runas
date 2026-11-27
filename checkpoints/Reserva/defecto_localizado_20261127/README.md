# Localización radial del defecto en el contacto de Reserva

En la donante cargada, la mayor contribución temporal se encuentra fuera de r=60. La envolvente de Taylor está dominada por χ en el exterior lejano. Se pudieron separar la fuente local y la propagación exterior en la ecuación lineal. El error entrante desde el núcleo y la realimentación no lineal siguen abiertos. El piloto de descarga permanece sin habilitarse.

[Protocolo inicial](PROTOCOLO.md) · [Protocolo del control ponderado](PROTOCOLO_PESO.md) · [Bandas, campos y escalera completa](bandas.csv) · [Operador, flujos y controles](resultado.json) · [Método](localizar.py) · [Verificación independiente](verificar.py)

## Prefijo y ventana completa

Se partió de los dos estados primarios de τ300 y de la receptora preparada del paso 2, con comprobación de huellas. En la malla R256 de dr=0,025 solo se avanzó la referencia tangente de paso interno 0,0025. En cada intervalo se formaron los cuatro coeficientes de Bernstein del mismo puente de Hermite de la entrega anterior. Se acumularon las normas de sus defectos por radio y campo antes de descartar el intervalo. Las normas de Φ incluyen ambas componentes en la métrica canónica. El valor conjunto usa la norma en producto antes del máximo temporal; las filas de distintas regiones son mayorantes y no son porcentajes aditivos.

| Intervalo del puente | Temporal, cargada en s=0…1 | Taylor, cargada en s=0…1 |
|---:|---:|---:|
| 0,2500 | 0,10418 | 0,0096601 |
| 0,1250 | 0,05355 | 0,0093795 |
| 0,0500 | 0,01872 | 0,0092980 |
| 0,0250 | 0,00648 | 0,0092815 |
| 0,0100 | 0,00259 | 0,0092730 |
| 0,0050 | 0,00467 | 0,0092702 |
| 0,0025 | 0,00929 | 0,0092688 |

El defecto temporal de este puente vuelve a crecer en los dos últimos intervalos. El paso interno del integrador se mantuvo fijo. La tabla caracteriza una reconstrucción entre nodos y no establece convergencia del integrador ni un paso óptimo para s=0…40.

| Radio | Temporal Φ | Temporal χ | Taylor Φ | Taylor χ |
|---|---:|---:|---:|---:|
| 0–40 | 1,848e−5 | 3,829e−4 | 3,618e−5 | 1,302e−4 |
| 40–60 | 3,065e−5 | 5,523e−4 | 2,373e−10 | 1,300e−4 |
| 60–160 | 2,232e−2 | 1,718 | 9,408e−7 | 1,099e−2 |
| 160–256 | 0,2743 | 1,087 | 6,621e−6 | 0,3372 |

Esta segunda tabla usa la cargada y el intervalo 0,125 medido durante las 40 unidades. Los dos totales globales, 2,02365 y 0,33825, reproducen la [entrega anterior](../error_forzado_contacto_20261127/README.md); la gemela también reproduce ambos totales. En la gemela domina el núcleo en ambas fuentes. Se verificó la aceleración M2 directa en puntos interiores de cada combinación de escalera y región, sin evolucionar M2.

## Telescopaje radial y términos de H

Para celdas centradas en rᵢ, sean wᵢ el volumen sin 4π, aᵢ el radio de la cara derecha, ℓᵢ la distancia al siguiente centro y cᵢ=aᵢ²/ℓᵢ. En la última celda se toma el valor exterior cero y ℓ=dr/2. Al telescopar r²|F|² hasta la pared se puede descartar el término de signo negativo debido al aumento de r. Se obtiene rⱼ²|Fⱼ|² ≤ Σᵢ≥ⱼ rᵢ² |ΔFᵢ| (|Fᵢ|+|Fᵢ₊₁|). Por Cauchy y la desigualdad del cuadrado de una suma, el lado derecho se acota por √(C V G), con V=Σwᵢ|Fᵢ|², G=Σcᵢ|ΔFᵢ|², ambas restringidas desde la primera celda exterior, y C=max 2(tᵢ+tᵢ₋₁)/wᵢ, tᵢ=rᵢ⁴/cᵢ. Se omite el t anterior al corte. Se midió C=3,999219. Para cada coeficiente temporal del campo se evaluó la desigualdad y luego se aplicó convexidad al campo para cubrir el puente completo. El verificador contrasta el telescopaje y la forma de gradiente contra el operador FV, también con un estado soportado solo en la última celda.

Las envolventes exteriores de |Φ| desde r=40 fueron 2,244e−3 (cargada), 1,750e−7 (gemela) y 1,688e−7 (receptora), redondeadas hacia arriba. El máximo global de cada referencia fue inferior a 0,747. Para d≥80, en cada punto al menos una de las dos distancias alcanza 40. Si solo D es exterior, se usa su cota de cola y el máximo global de R; si solo R es exterior se invierten los papeles. El cálculo concierne a valores FV por celda y puentes temporales, sin suponer exactitud para un interpolante espacial arbitrario.

En H=−Δ+M²+hₘ|D|²+hₘ|R|²+2hₘ Re(D*R), M²=10000 y el término de gradiente actúa sobre el mediador. En el par cargada–receptora, donde D es exterior, los tres términos variables quedan acotados en valor absoluto por 5,034e−4, 55,655 y 0,335. Donde R es exterior dan 55,655, 2,848e−12 y 2,518e−5. El término propio del núcleo interior permanece incluso si la interferencia es pequeña. Estas cotas describen H de las referencias; acotar su error exige también los errores de ambos campos, incluidas sus contribuciones cuadráticas.

## Interfaces y cola discreta

Se integraron los flujos firmados de energía y carga de cada referencia aislada en las caras 40, 60 y 160. Con la mitad de la energía de cada cara asignada a cada celda, el flujo de energía hacia fuera es −4πa²[2 Re(promedio Φ̇* ΔΦ)+promedio χ̇ Δχ]/dr y el de carga es −8πa² Im(promedio Φ* ΔΦ)/dr. La rotación común se cancela; la cuadratura de Gauss de cuatro puntos integra los polinomios de grado hasta seis. El verificador reproduce la identidad de energía en cada cara con campos manufacturados. En la cargada, en r60 se obtienen +3,53221e−6 y +3,35520e−6. Son flujos de preparación aislada. El flujo de **error** en las mismas caras depende de los errores de campo, gradiente y velocidad.

Primero se controló la cola del propagador lineal FV completo por la serie de la exponencial. De r≥160 a r<60 se necesitan al menos 4000 saltos de malla. La norma infinita del generador sobre (x,p/200) es a lo sumo 200. La serie desde el primer salto permitido da log₁₀ de la cota menor que −3469 a s=1; a s=40 la estimación general exp(8000) pierde resolución. Se conservaron los términos no locales sin imponer velocidad de propagación estricta.

La segunda comprobación separa el núcleo del exterior. En r≥40, la energía rotante del error lineal usa el potencial FV local, energía cinética y diferencias por cara. Se toma kᵢ=exp[−0,2 max(rᵢ−60,0)] para los términos por celda y el promedio de ambos pesos por cara. El operador exterior tiene una conexión a valor cero en el centro de la celda interior contigua; su valor real entra aparte como fuerza loᵢ xᵢ₋₁ en la primera celda exterior. Para esta energía Eₖ, el término giroscópico es antisimétrico. La derivada por cara interna es proporcional a cᵢ(kᵢ−kᵢ₊₁)Δx·(vᵢ+vᵢ₊₁)/2. Cauchy da (√(2Eₖ))′ ≤ B√(2Eₖ)/2 + ‖F‖ₖ, donde B² es el máximo por celda de la suma de cᵢ(Δk)²/(kᵢ+kᵢ₊₁) sobre sus caras internas, dividida por wᵢkᵢ. Los dos extremos usan el peso de la celda en la cara con dato cero. La positividad del potencial exterior se comprueba en ambos bloques canónicos, aparte del núcleo.

Se aplicó esta desigualdad a las envolventes de la fuente prescrita por banda en todos los intervalos de la ventana. La salida es una cota de amplitud energética exterior, con datos iniciales de error cero. Para un balance completo se debe sumar la entrada desde el núcleo y la fuerza no lineal dependiente del error. El acoplamiento al núcleo no se descarta al estimar la cola exterior.

El mínimo del potencial exterior es 0,1900 (a cuatro decimales) y B=0,20000019. La contribución de una fuente lineal soportada en r≥160 a la amplitud en 40≤r<60 adquiere un factor máximo exp(40B/2−10)=0,00247877, redondeado hacia arriba, respecto a la integral de su norma global. No se trata de una fracción de carga transportada. Para la cargada, las contribuciones ponderadas (temporal, Taylor) al extremo s=40 fueron (0,007397; 0,002091) en 40–60, (0,06802; 0,001098) en 60–160 y (0,0004294; 0,00008087) en 160–256, redondeadas hacia arriba. La cota temporal en la banda intermedia domina este presupuesto de fuentes. El coeficiente de entrada desde la celda interior en la norma de fuerza es 35860,74 por unidad de error de campo canónico sin peso radial; su amplitud temporal aún no está acotada con precisión. Las fuentes/cotas de energía del error están en unidades distintas de un flujo de misión.

**Siguiente iteración del diagnóstico localizado.** Probar una sola energía ponderada en la malla entera con peso plano en el núcleo y en 40–60, conservando la carga tangente, el modo de fase y el rango uno del Hessiano. Así se podrá comprobar algebraicamente si las caras de r40 se cancelan al sumar las dos regiones y medir los conmutadores del peso con las proyecciones, antes de intentar cerrar la realimentación no lineal. La reducción homogénea anterior solo justifica este ensayo. Mantener las puertas E=1,66414371e−6 y Q=1,84762579e−6, la atribución en r60 y la entrega útil a la receptora. No avanzar al piloto.

**Resumen listo para el Dot principal.** Diego, el defecto de la donante cargada se concentra fuera de r60 en la referencia de 40 unidades. La cota ponderada atenúa la contribución lineal de fuentes más allá de r160 a la corona 40–60 por un factor de hasta 0,002479. La entrada desde el núcleo y el error no lineal siguen sin cerrar. El piloto permanece suspendido. La siguiente iteración comprobará si una energía conjunta puede incorporar la interfaz y conservar la carga y la fase. [Informe en la rama científica](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/defecto_localizado_20261127)

Reproducir en este directorio con NumPy, SciPy y un compilador C: ejecutar `OPENBLAS_NUM_THREADS=1 python3 localizar.py` y `OPENBLAS_NUM_THREADS=1 python3 verificar.py`. Los controles numéricos usan doble precisión.
