# Contacto interno entre dos estados cargados

**Decisión del 26 de noviembre.** El contacto por solapamiento introduce una corriente impar en la fase relativa. Aparece ya al superponer dos estados en el instante inicial, sin actuador ni paquete. La aproximación de perfiles rígidos falla la continuidad de carga en el volumen de la receptora. Por tanto, el cribado descarta usar esa aproximación para pronosticar entrega. El contacto en M2 queda indeterminado y el piloto sigue sin habilitarse. [Protocolo anterior al cálculo](PROTOCOLO.md)

## Observable y derivación

El centro donante está a distancia d del centro receptor. La superficie de lectura es la esfera de radio 40 de la receptora, con normal **hacia dentro**. Es una superficie cerrada: su flujo neto incluye todas las entradas y salidas. Sea Φ = D + exp(iθ)R en la instantánea inicial, y sean Vd,Vr las velocidades complejas publicadas, rotadas junto con su estado para alinear su fase central. Con la convención de M2, la densidad es 2 Im(Φ* Φ̇), la corriente de carga es −2 Im(Φ* ∇Φ) y el flujo energético es −2 Re(Φ̇* ∇Φ) − χ̇ ∇χ. La inversión de fase deja intacto el término del mediador real. Para una normal n, escribimos Dn y Rn para las derivadas normales y definimos, integrando sobre la superficie,

- Cq = ∫(D* Rn − R Dn*) dS.
- Ce = ∫(Vd* Rn + Vr Dn*) dS.

Los términos cruzados son −2 Im(Cq exp(iθ)) y −2 Re(Ce exp(iθ)). La semidiferencia entre fases +φ y −φ vale −2 Re(Cq) sin φ para la carga y +2 Im(Ce) sin φ para la energía. Las contribuciones de cada estado aislado se cancelan en esta operación. La tabla de datos conserva también el término cruzado a fase cero, que puede ser distinto de cero para un estado preparado complejo. En las tablas el segundo contraste resta la gemela a la cargada.

Para proyectar en el tiempo se fija θ(t)=θ(0)+(ωR−ωD)t y se sustituyen las velocidades por iωD D e iωR R. La integral temporal de exp(iΔωt) es T exp(iΔωT/2) sinc(ΔωT/2), con sinc(x)=sin(x)/x. Esto muestra por separado cómo entra la ventana y cómo la separación modifica las integrales espaciales. Los perfiles vecinos varían simultáneamente su forma y su frecuencia. La rotación rígida es una hipótesis adicional en las preparaciones de τ300.

**Prueba independiente del flujo.** La carga cruzada de la rotación rígida en el volumen receptor es Re[B exp(iθ)], con B=2(ωD+ωR)∫ D* R dV. Se calcula su cambio desde t=0 para las mismas fases y se compara con el flujo impar integrado. Una solución de M2 exige igualdad en esta esfera, incluso con inventario inicial de interferencia. Para frecuencias iguales, el inventario rígido permanece constante: todo flujo integrado distinto de cero revela directamente un defecto del modelo. La identidad prueba el balance local, sin asignar procedencia a cada contribución exterior.

## Resultados

En la receptora preparada y T=240 se obtiene el siguiente contraste cargada menos gemela. Las cifras están en millonésimas M2 y la fase positiva es +π/2.

| Separación | Flujo impar integrado Q | Flujo impar integrado E | Cambio de inventario impar Q |
|---:|---:|---:|---:|
| 80 | +0,0419 | +0,0377 | 0 |
| 100 | +0,0179 | +0,0161 | 0 |
| 120 | −1,3417 | −1,2075 | 0 |

El mayor cociente muestreado entre la cola de un estado dentro del núcleo opuesto y el pico propio fue 0,0000696. Los resultados se limitan a las tres geometrías de colas débiles; los estados preparados incluyen estructura exterior. El signo y la magnitud no siguen una ley monótona en la separación.

En el caso d=120, ωR=0,895 y T=240, invertir el signo de la fase daría en el modelo rígido magnitudes de flujo de 2,04449 × 10⁻⁶ en Q y 1,82977 × 10⁻⁶ en E. Ambas superarían ligeramente las referencias de la misión. Sin embargo, la discrepancia entre flujo e inventario de carga alcanza **7,64086 × 10⁻⁵**, unas 37 veces la magnitud del propio flujo. A T=40 y 80 ya vale 1,26189 × 10⁻⁵ y 2,59955 × 10⁻⁵. El cambio de cuadratura del defecto a T=240 es 3,12 × 10⁻¹³ y el cambio de preparación temporal 5,82 × 10⁻¹¹, redondeados hacia arriba. El fallo de continuidad supera ampliamente ambas sensibilidades. Sustituir la velocidad guardada por la rígida también cambia la corriente energética inicial: T veces esa diferencia en el contraste alcanza 3,435 × 10⁻⁷ en el mismo caso. Esta última lectura es una sensibilidad instantánea escalada; queda sin determinar la integral de ese error durante una evolución.

## Alcance y condición para continuar

El defecto es una violación medible de la identidad necesaria. Por sí solo no proporciona una cota superior del error dinámico en energía y carga. La puerta conjunta falla ya por carga. La corriente de la superficie receptora tampoco mide el cruce por r60 de la donante. La preparación conjunta requiere cuantificar por separado el término cruzado inicial de energía, el inventario del exterior de ambos núcleos y el trabajo de montaje. Superponer perfiles y declarar trabajo cero durante la ventana deja abierto ese coste inicial.

El siguiente cálculo defendible **dentro del mismo contacto** es evaluar, sin evolución, si una reducción con poblaciones y fases variables puede satisfacer las identidades de ambos núcleos simultáneamente. Antes de ajustar coeficientes, comprobar el rango y el condicionamiento de las derivadas de los inventarios respecto a las variables colectivas, la conservación global y el residuo de las ecuaciones de M2 fuera del espacio proyectado. Usar los mismos datos y geometrías. Una reducción que solo imponga continuidad por construcción sigue necesitando una predicción independiente de los flujos y una cota física verificable. Un piloto posterior exigiría un contrato de dos núcleos con cotas inferiores por encima de los umbrales, preparaciones cargada/gemela con y sin contacto, fases opuestas, receptor aislado, control exterior y trabajo de montaje. La captura y la recarga siguen pendientes.

## Reproducción

Ejecutar desde esta carpeta con Python 3.12, NumPy y SciPy:

```sh
OPENBLAS_NUM_THREADS=1 python3 medir.py
```

Las instantáneas de τ300 y la receptora se cotejan con sus manifiestos originales. Se guardan huellas de los ocho perfiles. Los 288 registros incluyen dos resoluciones de preparación, dos donantes, cuatro receptoras, tres separaciones, dos cuadraturas y tres ventanas. El resumen contiene los 36 contrastes con sensibilidad por refinamiento y defecto de carga. [Método](medir.py) · [Mediciones](medidas.csv) · [Contrastes y huellas](resultado.json)
