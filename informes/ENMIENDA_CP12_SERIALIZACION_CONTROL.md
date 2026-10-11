# CP12 · Corrección de escritura del control previo

Antes de cualquier paso nuevo de M2, el intento `control_instrumentacion__1f74508bd2a56bfb797b94cd607a68f3d1896199cb52441eb35be4261c67f83b` terminó FALLIDA al escribir `resultados.json`: el comparador de epsilon devolvía un booleano de NumPy, no serializable por el JSON estricto. El recibo, código capturado, protocolo original y log del intento permanecen íntegros en su carpeta.

Se convierten explícitamente a `bool` de Python los valores del diccionario de pruebas antes de escribir. No se interpreta el intento sin resultados guardados como control superado. Se repite únicamente el control sin evolución, bajo una identidad nueva. No cambia ninguna fórmula, hipótesis, configuración, tolerancia, puerta, ni criterio causal. Las dos evoluciones siguen bloqueadas hasta un control reproducible positivo.

Esta es una enmienda de implementación y procedencia; no es un resultado negativo sobre M2 o el operador radial.
