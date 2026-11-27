# Realimentación de la cargada en el volumen radial

**Resultado.** La comparación FV de la referencia aislada y corregida de la cargada mantiene el tubo puntual de 1e−4 hasta **s=7,25** en toda la malla. En el intervalo siguiente, hasta **s=7,375**, la cota en 60≤r<160 asciende a **1,0800e−4**. Esta pérdida de garantía determina dónde se detuvo el cálculo. El valor real del error en ese intervalo sigue indeterminado. El piloto permanece pendiente.

[Protocolo causal](PROTOCOLO.md) · [Contraste registrado con peso fijo por banda](PROTOCOLO_PESO.md) · [Método](causal.py) · [Núcleos de interfaz](nucleos.py) · [Datos de cada intervalo y primer fallo](resultado.json) · [Referencia lineal reproducida](../adjunta_cargada_20261127/README.md)

## Qué se mantuvo

Malla FV R256, dr=0,025, intervalo h=0,125, pared a media celda, datos coincidentes en s=0 y la primera referencia corregida de gota_a010. En cada intervalo ensayado se reconstruyeron el puente de Hermite y las dos correcciones con los programas publicados. Se cotejaron las tres normas de fuerza ajustada, el máximo del jacobiano en el tubo y los defectos cinemático y de velocidad con bandas.csv.gz. La cobertura del puente incluye el interior del intervalo. Cada prueba empieza con error cero y lleva todas sus fuentes anteriores. Las cinco bandas son [0,10), [10,40), [40,60), [60,160) y [160,256]. Se trabaja en coordenadas de volumen canónicas. Los resultados son comparaciones numéricas en doble precisión, con el alcance del control de truncación publicado; no se certificó el redondeo.

## Contribución causal del propio intervalo

Sea N la raíz de dos veces la energía con potencial desplazado V+I. Se usa el mínimo V+I≥0,590 I y μ=1/(2√0,590). Para un impulso unitario de aceleración, el desplazamiento inicial es cero, y la velocidad en tiempo τ tiene norma a lo sumo exp(μτ). Integrar primero la velocidad y luego el historial de la fuente da

    D(τ) = expm1(μτ)/μ
    K₀ = [expm1(μh)/μ − h]/μ = 0,00802877751446.

El producto con 0,465 vale 0,003733381545. La suma de filas del sistema acoplado se comprobó aparte. Para una fuente de j intervalos de antigüedad, la ganancia de energía es exp(μjh)expm1(μh)/μ. Restando h y dividiendo por μ se obtiene la ganancia de desplazamiento. Estas integrales hasta el extremo derecho cubren también las observaciones intermedias porque los mayorantes usados son positivos y no decrecientes.

Con peso por celda k y media aritmética en las caras se usa la tasa μ+B/2. B² es el máximo sobre celdas de la suma por caras incidentes de c(Δk)²/(kᵢ+kⱼ), dividida por wᵢkᵢ. Resulta de Cauchy aplicada al trabajo de cara de la energía FV. Se incluyen todas las caras interiores; la pared homogénea cancela su trabajo con la energía de su conexión. El término giroscópico es antisimétrico celda a celda. Las fuerzas de truncación de posición y velocidad se transportan en energía; para la primera se usa una cota de la raíz del operador desplazado, para la segunda su norma de volumen. Ambas aparecen asimismo en el presupuesto de carga.

## Dos formas de transportar el historial

1. **Bandas disjuntas.** Para cada par de bandas se toma el menor de los dos núcleos válidos, sin peso y con k=exp(0,5 distancia a la banda fuente), dividiendo por el mínimo de √k en el destino. El término presente satisface X≤b+K₀ diag(J)X. La suma máxima de filas observada fue 0,010101 redondeada hacia arriba. La serie de Neumann garantiza la inversa positiva; se comprobaron también sus entradas y el residuo del sistema en cada paso. El jacobiano por banda J incluye toda la desviación admitida dentro del tubo. Esta comparación mantiene la garantía hasta s=5,0. En s=5,125 el mayorante de r<10 llega a 1,05613e−4. Con la realimentación anulada, el mayorante puntual de ese núcleo en el mismo intervalo es 5,555e−9 redondeado hacia arriba.
2. **Un peso conservado por cada banda observada.** Se toma k=exp(−0,5 distancia a esa banda) sobre toda la malla. La fuerza prescrita se pesa por celda; el peso acompaña cada aportación hasta la observación. La inversa diagonal inicial usa la fuerza de realimentación ≤max(J)‖x‖ₖ. La mayor fila observada es 0,003777 redondeada hacia arriba. Para afinar se combina esa cota con la suma en cuadratura de los cinco productos Jᵦ Xᵦ maxᵦ√k. Cada Xᵦ ponderado domina la norma de la banda donde su peso vale uno. Tres iteraciones descendentes desde la primera cota preservan el mayorante por positividad sin exigir que la iteración converja. Cada término aceptado se guarda con su propio retardo.

La comprobación puntual se hace después de resolver el volumen. Además de dividir por la menor raíz de volumen de cada banda, se usa que hay en ella una celda con norma física a lo sumo X/√(Σ4πw). Desde esa celda se telescopa hasta cualquier otra de la misma banda. El precio es la norma de gradiente acotada por N, multiplicada por √(Σ1/(4πc)) sobre las caras internas de esa banda. Se toma el menor de ambos mayorantes válidos. Esto comprueba por continuidad el tubo en cada intervalo aceptado. La contracción del término presente se mantuvo incluso en el primer intervalo rechazado de ambas pruebas.

| Banda radial | Cota puntual en s≤7,25, último intervalo | Cota condicional en (7,25; 7,375] |
|---|---:|---:|
| r<10 | 4,884e−7 | 5,737e−7 |
| 10–40 | 2,295e−8 | 2,711e−8 |
| 40–60 | 3,911e−9 | 4,620e−9 |
| 60–160 | 9,142e−5 | 1,0800e−4 |
| 160–256 | 7,269e−5 | 8,588e−5 |

## Carga, fase e interfaz

La ecuación de volumen incluye los bloques físicos completos. Se registra aparte la proyección de la fuerza en q̇, el término del defecto de fase Pu, las dos truncaciones y la contribución por banda de JX. La carga tangente se comprueba también por proyección directa del desplazamiento y la velocidad; la fase común, por proyección del desplazamiento. En el último intervalo aceptado de la segunda prueba se obtiene |q|≤7,891e−8, |q̇|≤9,504e−8 y |β|≤2,218e−7. Estas proyecciones del error no miden carga entregada.

Se regeneraron los núcleos de retardo de las seis semillas, incluido el resto entre muestras y la comprobación de la cara truncada. Al anular solo la realimentación se recuperan a s=40 la traza terminal lineal 7,34294e−9, la integral simple de |z′| de 1,89073e−6 y la integral propagada de 2,78259e−6 (valores redondeados hacia arriba). En el prefijo **s=0…7,25**, la cota de la integral simple total es **1,078e−7**, de los cuales hasta 1,060e−7 corresponden al término adicional de realimentación. El aporte total de ese prefijo con el peso temporal referido a 40 es ≤5,980e−7. Queda sin cerrar la continuación desde 7,25 hasta 40. La cota previa de la ruta levantada de la cargada a s=40 sigue teniendo alcance lineal.

**Siguiente comprobación del mismo contacto.** La banda limitante está fuera del núcleo, donde el potencial rotante ya es positivo. Evaluar una energía que añada el desplazamiento positivo solo en las celdas donde haga falta. Medir el mínimo local en los tres campos y acotar por separado el trabajo de ese desplazamiento, concentrado en el núcleo, mediante las cotas locales. Mantener las caras FV, la proyección de fase y carga, la integral causal del término propio, la comparación sin realimentación y el primer fallo. Antes de otra trayectoria comprobar si este cambio reduce el crecimiento conservador del historial exterior.

El piloto requiere una predicción conjunta por encima del error y atribución en r60 o un contrato separado validable. Los mínimos de misión siguen en E=1,66414371e−6 y Q=1,84762579e−6; la recarga requiere entrega útil a la receptora.

**Resumen para el Dot principal.** Diego, la cargada mantiene el tubo del error de 1e−4 en todo el volumen hasta s=7,25 con realimentación incluida. La cota falla primero en 60–160 al llegar a s=7,375. La contribución del intervalo propio sí es contractiva y el control sin realimentación recupera el resultado lineal hasta s=40. Sigue pendiente cerrar el historial exterior. [Informe y datos](https://github.com/diegolezaval/Proyecto_Runas/tree/ciencia/cp12-p4-validacion/checkpoints/Reserva/realimentacion_cargada_20261127)

Desde la raíz, ejecutar `OPENBLAS_NUM_THREADS=1 python3 checkpoints/Reserva/realimentacion_cargada_20261127/causal.py` y comparar resultado.json.
