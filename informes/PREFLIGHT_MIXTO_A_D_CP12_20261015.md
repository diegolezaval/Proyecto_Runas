# CP12 · Controles previos mixtos A–D positivos; no validación física

Se completó el contraste congelado registrado antes del cálculo en `05f61efebed643e3a7435ced96af2635ba206a6e`, reutilizando sin repetir los resultados A, B y C. Las cuatro combinaciones de malla/fondo y ambos órdenes pasan: se propagaron cinco respuestas lineales durante τ=.1, en diez ventanas .01, no una historia física M2.

| Comprobación | Máximo observado | Límite registrado |
|---|---:|---:|
| Contraste de las tres referencias | 3.413e-15 | 1e-8 |
| Error en espacio de fases congelado | 5.885e-12 | 1e-3 |
| Deriva de energía cuadrática congelada | 3.891e-13 | 2e-4 |
| Iteraciones de etapa | 6 | 12 |
| Residuo de iteración | 4.416e-13 | 1e-12 |

La referencia compara una exponencial dispersa con Taylor de grado 32 en 16 y 32 subintervalos, fijados antes del cálculo, más la cota analítica del resto. La cota de frecuencia por sumas de filas/columnas queda en los resultados. Es un contraste numérico controlado; no se presenta como aritmética de intervalos. Los fondos incluyen el Jacobiano inicial y el promedio entre estados CP10 inicial/final de cada malla, con pesos cinéticos y la base D2 inicial originales. No se cambiaron pasos, órdenes o umbrales tras ver resultados.

Los datos completos están en `checkpoints/CP12/continuacion_20261014/mixto_chi_prefLight_20261015/fase_D/RESULTADO.json`. `checkpoints/CP12/continuacion_20261014/mixto_chi_prefLight_20261015/CERTIFICADO_PREFLIGHT_A_D.json` enlaza hashes y registros de las cuatro fases, cuyos recuentos por caso son 32, 52, 16 y 36. No son pruebas estadísticamente independientes ni evidencia de aceptación física. Las entradas originales, los prototipos K4 y la fase A permanecieron íntegros; no se repitió la evolución original τ160 ni el piloto K4 fallido.

## Puerta de continuidad

El conjunto previo registrado es positivo: enrutado y acción, gradiente/carga/trabajo, equivalencia C/NumPy, defecto/Jacobiano, matriz independiente, resolventes y propagación congelada. Esto permite **preparar** un nuevo prerregistro ejecutable del piloto Φ-FV/χ-K4. Todavía faltan ese registro, la captura del coordinador e instrumentación física mixta y la conservación/recuperación/auditoría íntegra de τ0 antes de cualquier paso M2. Los controles no certifican que la energía FV original se conservará sobre la nueva trayectoria ni que χ convergerá.

La futura prueba conservará los mismos datos de Cauchy originales, ambas mallas, M2, Θ, R220, L4, DOP853, tolerancias, observadores y spline; exigirá ambas puertas energéticas 2e-4, carga 1e-9 y aceptación espacial 2 %. La eliminación del mecanismo, convergencia, conservación, estabilidad y robustez con las resoluciones necesarias deben demostrarse mediante evoluciones autoconsistentes. No se acepta una respuesta offline retirada como una corrección.

No se inicia M2 en esta revisión. K4 de tres campos sigue fallido y conservado. Las 33 etapas y todos los negativos, la reproducción CP10 exacta y las tres ventanas originales siguen intactos. Main permanece en CP11 y PR #2 abierto/borrador; no hay merge, tag, Release ni cierre CP12.
