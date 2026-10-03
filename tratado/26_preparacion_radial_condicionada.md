# 26 · Asentamiento radial desde un paquete cargado

## 26.1. Resultado y puerta

**SIMULADO, condicionado y finito:** una gaussiana cargada de anchura 7.2 evoluciona hacia un perfil cercano a una Q-ball en el ensayo radial a t=1200. Las dos mallas conservan aproximadamente el 90.13 % de la carga dentro de r=40 y muestran una desviación de perfil de alrededor del 1.12 % frente al equilibrio de igual carga media. No demuestra una preparación primordial, estabilidad 3D, retención indefinida ni una Reserva funcional. E04 y RES1 permanecen **PARCIALES**; sus dependencias generales tampoco están cerradas.

El protocolo y sus criterios quedaron fijados en `datos/ensayo_preparacion_4_2.json` antes del ensayo base. La prolongación se decidió tras el fallo de asentamiento a t=240. Se conservan ambas ventanas, todos los intentos y todos los resultados negativos. La duración mayor no convierte el resultado corto en un éxito retroactivo.

## 26.2. Datos iniciales y contabilidad

Se toma Φ(0,r)=A exp[−r²/(2b²)], ∂tΦ(0,r)=i0.9Φ(0,r), con A elegido para Q=2745.7739207. El mediador inicial resuelve su ecuación elíptica para ese paquete y ∂tχ=0. Su energía está incluida. No se inicializa el perfil final de una Q-ball ni se introduce amortiguamiento.

El paquete ya tiene carga y energía. Su origen físico es un recurso pendiente; llamarlo dato inicial no lo produce desde el vacío. El ensayo sólo examina la evolución posterior. El mediador preparado constituye también parte de ese dato inicial, no una pared gratuita.

Se evolucionan los dos campos completos por volúmenes finitos radiales y Verlet. Los pesos son Δ(r³)/3; los flujos usan las caras r². La energía de gradiente se obtiene de esa misma acción discreta. Se cuentan E,Q del dominio entero y del núcleo r<40, incluyendo media energía de la cara que lo separa del exterior. E exterior=E total−E núcleo y Q exterior=Q total−Q núcleo son inventarios, no una medición de entrega a un receptor.

Las cajas son 260 hasta t=240 y 1300 hasta t=1200. El radio grande y las colas comprobadas impiden atribuir el asentamiento a una reflexión que regrese al núcleo durante la ventana. Los estados completos se guardan periódicamente en NPZ; el mismo comando puede continuar desde el último paso válido. Si ya existe el resultado final, se reutiliza.

## 26.3. Criterios y resultados negativos

Se exigieron deriva energética muestreada <2×10⁻⁴, deriva de carga <10⁻⁹, discrepancia de observables medios del núcleo <2 % entre refinamientos, desviación tardía de perfil <5 % y carga tardía retenida ≥90 %. Los dos últimos definen asentamiento en este ensayo; no sustituyen la puerta original de RES1.

| Anchura | Tiempo final | Malla | Carga tardía retenida | Máxima desviación tardía del perfil | Decisión de asentamiento |
|---|---:|---:|---:|---:|---|
| 7.2 | 240 | 0.2 | 92.780 % | 10.900 % | No supera |
| 7.2 | 240 | 0.1 | 92.783 % | 10.886 % | No supera |
| 8.0 | 240 | 0.2 | 88.141 % | 19.785 % | No supera |
| 8.0 | 240 | 0.1 | 88.141 % | 19.764 % | No supera |
| 8.8 | 240 | 0.2 | 85.530 % | 30.693 % | No supera |
| 7.2 | 1200 | 0.2 | 90.124 % | 1.120 % | Supera el ensayo radial |
| 7.2 | 1200 | 0.1 | 90.132 % | 1.124 % | Supera el ensayo radial |

La octava ejecución es el control temporal a anchura 8, h=0.2 y Δt=0.002. En el caso base Δt=0.004; el caso fino usa h=0.1 y Δt=0.002. Reducir sólo Δt divide la deriva de energía por 4.00001. Las diferencias espaciales de los observables medios del núcleo son menores que 4.22×10⁻⁶ relativos a t=240. En la prolongación la diferencia combinada de espacio y tiempo queda por debajo de 9.79×10⁻⁵. No hay una tercera malla larga que certifique un orden asintótico para cada observable.

La mayor deriva energética muestreada entre las ocho ejecuciones es 1.92×10⁻⁷; la mayor deriva de carga es 7.00×10⁻¹⁵. El núcleo pierde carga de forma física mientras la carga total se conserva. La ventana tardía abarca el último 20 % del tiempo, y el error de perfil es una norma radial ponderada hasta r=30. No es una cota puntual ni una prueba fuera de la simetría radial.

## 26.4. Reanudación y fallo conservado

La primera guarda de transferencia, un anillo exterior de anchura 40, rechazó la ampliación porque contenía 1.37×10⁻⁹ de la energía frente al umbral 10⁻¹². El lanzador inició por error el comando siguiente desde t=0. Ese cálculo terminó y se conserva como control directo de caja grande; no se presenta como reanudado. El registro `intento_01_extension.json` documenta ambos hechos.

Se distinguió la energía de un pulso dentro de ese anillo de los valores efectivos en la frontera. El anillo de anchura 20 estaba vacío al nivel requerido y la modificación exacta de la energía discreta por sustituir la cara exterior era despreciable. El refinamiento fino sí se prolongó desde t=240: conserva los valores, velocidades y malla interior, añade el exterior nulo y no repite sus 120000 pasos previos. Su anillo exterior representa 2.93×10⁻²³ de la energía y el cambio de energía de cara es 4.57×10⁻⁴⁰ relativo. Los criterios de balance y asentamiento permanecieron iguales.

La auditoría final detectó además una marca antigua «diagnóstico pendiente» en el control grueso, aunque sus campos, resultado y diagnóstico estaban terminados. Se conservó la marca y la verificación fallida, se comprobaron paso final, configuración y finitud, y se sincronizó únicamente el estado de progreso. No se volvió a evolucionar ese caso. La recuperación está documentada en `recuperacion_marca_progreso.json`.

## 26.5. Equilibrio de igual carga y energía de excitación

La interpolación inicial de ω(Q) dejaba una discrepancia de carga del orden de 0.1 %. Se conserva como diagnóstico preliminar. El diagnóstico final resuelve la ecuación estacionaria a la carga media realmente retenida: la discrepancia es menor que 3×10⁻¹¹ relativa en los casos largos. Esto evita llamar excitación a la energía debida a comparar cargas diferentes.

Aun así, restar una energía de equilibrio continua a una energía de evolución discreta introducía un sesgo: los excesos eran 0.11932 y 0.14823 en las dos mallas. Para resolver esa diferencia se calculó también el equilibrio a carga fija de **la misma acción de volúmenes finitos**, con Newton sobre ambos campos y ω. Se publican residuos y el contraste de cajas 60 y 80, cuya diferencia energética es menor que 4.6×10⁻¹³.

El exceso medio del núcleo sobre ese equilibrio discreto es 0.15914 y 0.15818; la discrepancia relativa entre mallas es 0.611 %. El valor fino contrasta con E núcleo≈2281.78. Es una estimación de excitación radial por encima de una solución estacionaria, no una prueba de mínimo global ni de energía extraíble: no se ha resuelto receptor, descarga o ciclo. Tampoco se interpreta la radiación de carga expulsada como trabajo útil recuperado.

## 26.6. Pendientes que impiden el cierre

Faltan una región de datos iniciales que pase a largo plazo, la fuente y preparación de esos datos con sus recursos, perturbaciones no radiales, apagado y destinos finales, acceso y receptor. La anchura 7.2 ofrece un candidato condicional; no justifica extrapolar a las otras anchuras ni a toda una cuenca de atracción. Los estados finales y sus velocidades están disponibles para estudiar estos puntos sin reiniciar desde la gaussiana.

![Preparación radial](../graficos/CP04_preparacion_radial.svg)
