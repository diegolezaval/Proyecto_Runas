# Diagnóstico exterior a entrada fija

Base: ca4751d7b88e50a089f36b3671973b5080e99008. Reproducir completo el resultado anterior y extraer los presupuestos X y E de la última fila rechazada en s=22,875 sin modificar el cálculo. Cotejar las cinco cotas, el estado entrante y los cinco radios. Localizar máximo de la envolvente de mínimos por celda y forma activa en ambas bandas.

En mismas condiciones contrastar (a) la extensión dos unidades de la banda 60–160; (b) una escalera más densa de λ y extensión de ocho unidades; (c) la combinación no negativa con la energía ponderada de la banda vecina. Mantener λ solo en la banda para la cual se tiene el presupuesto X. Conservar el piso publicado y la pared física. Omitir las caras de corte artificial por completo. La energía de cada forma se acota con la suma de sus presupuestos cuadrados con exactamente los mismos factores, nunca con cotas de fuerza. Contrastar la factorización en celdas de borde e interiores con una resolución dispersa independiente. Mantener la envolvente previa por intersección.

No propagar una nueva trayectoria si la fila fija sigue fuera del tubo. No modificar la atribución previa de la corona ni inferir transferencia al receptor. El diagnóstico es de error numérico, no de lanzamiento del piloto.
