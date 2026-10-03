# Código CP10 antes de observar hilos

Se conserva el comparador preparado con el protocolo antes de su primera ejecución. Se incorpora después un contexto explícito threadpool_limits(1), la observación del límite en el JSON y una comprobación de igualdad de todos los umbrales frente al protocolo original (incluido el cambio de nombre amplification_max). No se cambian fórmulas, métricas, puertas, parámetros físicos ni trabajadores de evolución. El código efectivo quedará capturado antes de ejecutar la comparación.
