# Coste de caras con cajas por celda para Sx

En el historial fijo de la donante cargada, la cota del coste de caras a s=15 baja un **61,64 %** al aplicar el desplazamiento positivo S por celda. Se conservan la realimentación, la norma de banda y los defectos del cálculo previo. El resultado justifica incorporar esta estimación a una comparación causal. La última fila con certificación en todo el volumen sigue siendo s=14,875.

| Extremo | Contribución previa de S a la amplitud de energía | Contribución con cajas y norma de banda | Coste de caras previo | Coste de caras al sustituir solo Sx |
|---|---:|---:|---:|---:|
| 14,875, aceptado | 2,78394e−4 | 5,53470e−5 | 4,06477e−5 | 1,50773e−5 |
| 15, candidato rechazado | 3,23617e−4 | 6,39611e−5 | 4,82899e−5 | 1,85226e−5 |

Mayorantes redondeados hacia arriba. Se usan los mismos 120 estados de comparación y se conservan los pesos de observación de la [auditoría causal](../historial_caras_20261127/README.md), incluidos los saltos de métrica y el propio intervalo. Para las dos bandas donde S tiene soporte se recupera X dividiendo la contribución original por la ganancia de banda. Para cada componente se reconstruye la cota de We con D, κq y uβ. Se divide por W solo en las celdas con W>0 y se intersecta con el radio del candidato en unidades canónicas. En W=0 se conserva ese radio. Se añade la masa antes de aplicar la matriz de magnitudes de S.

La fuerza por celda se limita por el menor entre el techo de la caja y la ganancia espectral multiplicada por el desplazamiento local. El dual cuadrático de WJ impone el mismo X al conjunto de celdas de cada banda. Se comprueban el espectro local, el soporte de S, las contribuciones originales por emisión y el coste de caras previo. Se usan holguras relativas de 1e−11 y el mínimo con los mayorantes anteriores. [Protocolo](PROTOCOLO.md) · [Cálculo](cribar.py) · [Series y extremos](resultado.json) · [Recibo](RECUPERACION.json)

En s=15 los restantes términos de amplitud ya suman 9,76079e−5 antes de la conversión a caras. La reducción obtenida solo afecta a la contribución ensayada. La siguiente comparación debe partir de las cajas del candidato original ya acotado, refinar la fuerza con esas cajas y efectuar pasadas descendentes de las cinco energías con sus propios pesos, sin iniciar a cero el error. Comprobar primero la fila de s=15 a igual entrada y después el historial desde s=13,5 si mejora. Validar el control al desactivar solo el refinamiento. Conservar el conmutador proyectado, q̇ y las puertas de misión. El cruce de energía y carga en r60 y la entrega útil a la receptora siguen pendientes.

Reproducir con `OPENBLAS_NUM_THREADS=1 python3 cribar.py` en este directorio.
