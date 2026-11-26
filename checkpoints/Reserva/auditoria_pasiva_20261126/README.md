# Hasta dónde llega la fuga espontánea del núcleo

**La fuga positiva de energía y carga queda resuelta. La pérdida del núcleo queda por debajo del objetivo conjunto del 1 % en s = 400…480.** La tabla expresa la media del flujo acumulado cargada menos gemela, sin paquete, como porcentaje del exceso histórico almacenado en r40 en τ300. Los intervalos son sensibilidades numéricas ±3U. La resolución espacial domina en las cuatro lecturas de cara. [Orden previa](PROTOCOLO.md) · [Resultados por réplica y componentes de U](resultado.json)

| Región y saldo | Energía, media [intervalo] | Carga, media [intervalo] |
|---|---:|---:|
| Núcleo, salida en r40 | 0,658 % [0,6407–0,6744] | 0,582 % [0,5672–0,5967] |
| Corona, salida menos entrada | 3,237 % [3,1846–3,2891] | 2,789 % [2,7456–2,8324] |
| Interior de r60, salida en r60 | 3,894 % [3,8254–3,9634] | 3,371 % [3,3128–3,4290] |

Al inicio, la corona de la cargada contenía 5,43497 × 10⁻⁶ M2 de energía y 5,20126 × 10⁻⁶ M2 de carga adicionales respecto de la gemela. Los respectivos inventarios diferenciales medios en la ventana fueron 4,83880 × 10⁻⁸ y 4,82760 × 10⁻⁸. La reducción de ese inventario explica en el balance el 83,12 % de la salida diferencial de energía en r60 y el 82,74 % de la de carga. La identificación de la procedencia de cada componente requeriría otra medición.

**Decisión de la misión.** Se cierra esta vía pasiva para la preparación y ventana fijadas. Las cotas superiores en r40 quedan bajo ambos umbrales. El plan mantiene pendientes la descarga controlada, la captura por una receptora y la recarga. Un mecanismo distinto necesita una hipótesis física que permita predecir y distinguir una salida controlada de la fuga espontánea ya medida.

## Reproducción

Desde la raíz del repositorio, ejecutar `python3 checkpoints/Reserva/auditoria_pasiva_20261126/auditar.py` con Python 3 y NumPy 2. El lector verifica las ocho huellas de las trayectorias de lectura completa, las dos del solapamiento hasta s = 300, el reloj, el trabajo, los retornos y los cierres frente al recibo histórico. Reconstruye las tres medias por canal, cara, rama y réplica. En la corona el flujo tabulado es F60−F40, positivo al vaciarse. Los valores diferenciales se obtienen restando ambas ramas después de calcular los cambios de cada inventario respecto de su estado inicial.

El programa genera resultado.json y series_auditadas.csv. El CSV contiene las dos medidas y su residuo en las 481 muestras de cada una de las 72 combinaciones de réplica, rama, canal y región. La huella del CSV figura en resultado.json. El origen de cada muestra se conserva en las [series primarias](../mision_paquete_negativo_20261125/datos).
