# Conversión exterior conjunta a la misma entrada

En s=22,875 se recuperó exactamente el cálculo anterior. Se mantuvieron la entrada, las cinco cajas y los presupuestos originales. Dos bandas superaban el tubo de 10⁻⁴. En 60–160 basta extender la forma dos unidades a ambos lados. Para r≥160, extender la forma hasta ocho unidades y densificar λ no basta. Añadir la energía ponderada ya acotada de 60–160 sí da margen, sin reducir el presupuesto de error ni añadir energía en la frontera.

| Banda | X | E | Cota de origen (r) | Forma ensayada | Nueva cota |
|---|---:|---:|---|---|---:|
| 60–160 | 0,02001577 | 0,01443536 | 1,005689e−4 (60,0125) | Extensión 2, λ=0 | 8,65534e−5 |
| ≥160 | 0,06543651 | 0,04722482 | 1,068574e−4 (160,0125) | Extensión 8, escalera densa, sin mezcla | 1,034540e−4 |
| ≥160 | 0,06543651 | 0,04722482 | idem | Extensión 8, con mezcla | 8,61127e−5 |

Los presupuestos de la tabla se muestran redondeados hacia arriba. Se conserva el término λ X² solo en la banda observada. En el exterior se incorpora α veces la forma de 60–160, con α no negativo, y α veces el cuadrado de su presupuesto. La forma física suma potencial inferior y términos FV no negativos. La pared mantiene la distancia física; no hay términos de borde artificial. Se comprueba el margen de cada factorización LDL por fila, la recurrencia inversa con holgura y cinco nodos con resolución dispersa independiente. Se evalúa el mínimo de formas válidas por celda antes de maximizar sobre la banda. No se usan estas mejoras como disminuciones de E ni como prueba de transferencia.

[Protocolo](PROTOCOLO.md) · [Presupuestos de la fila reproducida](entrada.json) · [Cribado y márgenes](evaluacion.json)

Reproducción desde este directorio:

```sh
export OPENBLAS_NUM_THREADS=1
python3 diagnostico.py
python3 formas.py
python3 reproducir.py
```

## Marcha causal

Se verificó el ensayo fijo con una selección de 3 formas para 60–160 y 16 para el exterior. La prueba desde cero reproduce exactamente las 182 filas aceptadas anteriores. La nueva conversión se activa solo a partir del intervalo que terminaba en el rechazo, sin alterar la historia previa. Solo se propaga una fila si sus cinco cotas y el extremo entrante caben en sus radios.

| s | Núcleo | 60–160 | ≥160 | Decisión |
|---|---:|---:|---:|---|
| 22,875 | 4,45178e−5 | 8,65534e−5 | 8,61027e−5 | Acreditado con idéntica entrada y radios |
| 23,000 | 4,93164e−5 | 9,70434e−5 | 9,60212e−5 | Acreditado |
| 23,125 | 5,46914e−5 | 1,086425e−4 | 1,070182e−4 | No acreditado |

Resultado: cobertura de las cinco bandas hasta **s=23 de 40**, dos intervalos adicionales. Los dos experimentos se reprodujeron byte por byte en un segundo clon limpio de la misma base. [Marcha](marcha.json) · [Recibo](RECUPERACION.json)

## Continuación del mismo contacto

Las dos bandas exteriores siguen limitando en s=23,125. La conversión ya eliminó la mayor holgura de borde hallada en s=22,875. Antes de densificar más formas, desglosar E y X en la fila de rechazo a misma entrada y radios. Separar trabajo de la fuerza prescrita, realimentación, desplazamiento positivo y defectos numéricos, con su peso, retardo y saltos de métrica. Reconciliar la suma con la cota y contrastar cuánto podría ahorrar el término dominante antes de intentar otra marcha. La falta de garantía no es un error físico medido. No se extienden los cortes de corona independientes. El piloto sigue en espera del cruce atribuible conjunto de energía y carga por r60 y de la entrega útil a la receptora.
