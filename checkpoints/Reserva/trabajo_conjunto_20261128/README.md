# Trabajo directo por soportes radiales disjuntos

La cota de desplazamiento en todo el volumen de la donante cargada cumple el techo de 10⁻⁴ hasta **s=22,75**, frente a 22,375. El ensayo a igual entrada en s=22,5 cierra las cinco bandas. Se acreditan tres intervalos adicionales de 0,125. En el primero no acreditado, s=22,875, limitan 60≤r<160 y r≥160; el núcleo queda dentro.

| Comparación | s | Núcleo | 60–160 | r≥160 | Decisión |
|---|---:|---:|---:|---:|---|
| Control, sin el nuevo ajuste | 22,5 | 1,04839e−4 | 9,51019e−5 | 7,77199e−5 | No acreditado |
| Fase dual archivada, misma entrada | 22,5 | 1,00787e−4 | 9,51019e−5 | 7,77199e−5 | No acreditado |
| Trabajo agrupado y fase dual, misma entrada | 22,5 | 9,96329e−5 | 9,51019e−5 | 7,77199e−5 | Acreditado |
| Marcha con ajuste desde cero | 22,75 | 4,02394e−5 | 9,20080e−5 | 9,51394e−5 | Acreditado |
| Marcha con ajuste desde cero | 22,875 | 4,45178e−5 | 1,00569e−4 | 1,06858e−4 | No acreditado |

En la prueba fija, las cuatro cotas externas, el estado entrante y los cinco radios se conservan. Los mayorantes tabulados se redondearon hacia arriba. Una cota que no acredita el tubo no demuestra que el error físico lo supere.

## Método y controles

Las filas no nulas del conmutador [T,W] se encuentran entre r=11,9875 y 38,0125: todas pertenecen a 10–40. La fuerza WJ se acota directamente en sus dos bandas con los componentes y la norma de volumen ya disponibles; W es nulo a partir de 38. No se obtiene la norma de transición por resta de cuadrados de cotas. Si A es la cota de la fuerza interior, B la de transición y C la de caras, el trabajo conjunto se acota por hypot(A,B+C) antes de la proyección ortogonal contractiva. El código calcula en precisión extendida con holgura relativa de 2e−11 y conserva el menor mayorante previo válido. Se comprueban los casos sin caras y sin fuerza interior.

La revisión se aplica después de fijar las cotas externas, de desplazamiento auxiliar y de realimentación de cada candidato. El segundo cálculo del núcleo usa los mismos insumos de cada intervalo y conserva por separado la proyección de carga, el trabajo de κq̇, los defectos y la fase. Para la fase común se reutiliza el coeficiente dual verificado, con la historia refinada previa en el ensayo de entrada fija. El cálculo puntual intersecta el mayorante anterior con la restauración ortogonal de carga y fase. En la marcha desde cero solo una fila aceptada aporta su estado e historia al paso siguiente. La prueba desactivada reproduce todas las filas del archivo anterior a igualdad exacta.

Reproducción: `OPENBLAS_NUM_THREADS=1 python3 medir.py`. [Protocolo](PROTOCOLO.md) · [Resultados y controles](resultado.json) · [Recibo](RECUPERACION.json)

## Siguiente comprobación del mismo contacto

En s=22,875, recuperar a igual entrada y radios los presupuestos X y E y la celda y forma que maximizan la cota de cada una de las dos bandas que limitan. Separar exceso de presupuesto de energía de holgura en la evaluación puntual. Con la forma FV acreditada, cribar primero si cerrar ambos excesos sería posible afinando peso, soporte o la combinación con X sin inventar energía en una frontera artificial. Si la mejora potencial en evaluación es insuficiente, desglosar los dos historiales por fuente y retardo con sus saltos antes de otra marcha. Conservar el control en las cinco bandas. No se modifican los cortes del cálculo de la corona hasta 40. El piloto sigue pendiente del cruce atribuible conjunto de energía y carga por r60 y de la entrega útil a la receptora.
