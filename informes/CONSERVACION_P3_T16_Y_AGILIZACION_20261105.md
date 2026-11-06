# P3: frontera τ16 conservada, positiva y guardado sin pérdidas

Entrega del 5 de noviembre de 2026, hora de Lima; publicación GitHub fechada el 6 de noviembre UTC. **CP11 aceptado; CP12 abierto; P3 sin validar.** La última frontera completa positiva recuperada pasa de τ8 a **τ16**. No se repitió14,4→16 ni se ejecutaron pasos nuevos durante esta revisión.

## Pregunta y resultado

Se recuperó la cápsula de16 que había producido la asignación `p3_144_a16_20261105`, se publicó sin modificar un byte y se comprobó desde una descarga pública independiente. Sus324 cargas pasaron cobertura exacta y SHA256 antes/después, los30 controles originales de frontera y la lectura original de las cinco métricas espaciales y diez controles físicos de ambas mallas. Todos fueron positivos. La recuperación nativa independiente también pasó los30 controles. Las auditorías registran cero construcciones o pasos DOP853 y la lectura registra cero pasos M2.

La sesión anterior81225 ya no era accesible; no se observó su salida. No se la reactivó, no se reconstruyó su archivo privado de publicación y no se atribuye al proceso nuevo la prueba de capacidad de un proceso anterior. La [reconciliación](../checkpoints/CP12/p3_20261018/recuperacion_t16_20261105/RECONCILIACION.json) delimita lo observado.

## Artefacto recuperado

| Campo | Identidad |
| --- | --- |
| Cápsula | CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_FRONTERA_0016_P3_144_A16_20261105.zip |
| Adjunto GitHub | 715405768 |
| Bytes | 230213899 |
| SHA256 | 9627950c47e52280df00b5aab8e75358f653d4807c85db32e1b1cedcafabca12 |
| Identidad nativa existente | libfile_bb187e2e145c81918cf7b7b1e20cac45 |
| Estado de frontera | ac249962765a990e75fc25817f5c3d7ce9c0061430e3142719ccd97964e5c1ed |
| Configuración original | 76408ed2afc60006641dc3954b0c8709b4be32fa8ab6e1fcfbaa49a37edf8fed |
| Recibo de procedencia | 4fe1495f9dc6b6e25ba97574918e9735fb7603e2d64cd392fbc50c680cd389ca |

[Release experimental](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027) · [identidad](../checkpoints/CP12/p3_20261018/recuperacion_t16_20261105/ORIGEN.json) · [recuperación nativa](../checkpoints/CP12/p3_20261018/recuperacion_t16_20261105/RECUPERACION_NATIVA.json) · [recuperación pública](../checkpoints/CP12/p3_20261018/recuperacion_t16_20261105/RECUPERACION_PUBLICA.json) · [certificado](../checkpoints/CP12/p3_20261018/recuperacion_t16_20261105/CERTIFICADO_FRONTERA.json).

El transporte interno que permanece dentro de esta cápsula es antecedente forense. La reanudación usa el estado cerrado de16, con ambos solvers ausentes, conforme al restaurador original. No se interpreta el transporte interno antiguo como estado de16.

## Puertas originales

Valores sin redondear en [METRICAS_ORIGINALES.json](../checkpoints/CP12/p3_20261018/recuperacion_t16_20261105/METRICAS_ORIGINALES.json). El umbral de cada fila es0,02.

| Métrica | Valor original | Puerta |
| --- | ---: | --- |
| Supremo relativo de la norma | 0.00005123020515315443 | Superada |
| Campo complejo no radial final | 0.00029962342842862445 | Superada |
| Φ en espacio de fases final | 0.00045296081570267216 | Superada |
| χ no radial final | 0.000249545229481547 | Superada |
| χ en espacio de fases final | 0.0002544239796291026 | Superada |

Las dos mallas conservan: energía original≤2e-4, energía coherente P3≤2e-4, carga≤1e-9, carga de núcleo según el criterio original y amplificación de ventana≤3 veces la inicial. Máximos registrados: energía original3,4873062215723394e-9; energía P3 7,069400620451916e-11; carga1,1102230246251565e-15. Las puertas originales de identidades/simetría, Parseval, observadores, memoria pasiva, datos iniciales y configuración pasaron en el auditor fijado. No se usó la rotación descriptiva deχ para aceptación.

Se restauró otra vez el compilador real Ubuntu13.3.0 con el restaurador registrado; hash6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234. No se forzó arquitectura BLAS ni se modificaron auditores. Se conservan M2,Θ,CP04,h=.125/.0625,R220,L4,ε=.02,DOP853 y sus tolerancias y todos los observadores originales.

## Agilización comprobada

Los cinco NPZ ya comprimidos ocupaban229496073 bytes. La segunda compresión sólo ahorraba5522 bytes. La nueva versión administrativa conserva directamente sus bytes mediante ZIP_STORED; los demás archivos mantienen DEFLATE nivel6. El AST permite exclusivamente ese cambio en una llamada de serialización. `continuar.py` y `probar.py` son copias exactas de sus versiones registradas. El código antiguo permanece intacto.

| Medida | Compresión anterior | NPZ almacenado |
| --- | ---: | ---: |
| Mediana de dos empaquetados | 9.910477623500014 s | 0.3119931690000044 s |
| Tamaño | 230213899 bytes | 230219421 bytes |
| Sobrecoste | — | 5522 bytes;0,0023986388415275783% |

El empaquetado fue31,765046828637054 veces más rápido en esta medición. Se alternó el orden de las dos parejas de ejecuciones. En las cuatro variantes se verificaron nombres, orden y bytes de las325 entradas y el desempaquetador original; la variante rápida pasó además los30 controles originales. Los12 controles administrativos adversos siguen positivos. El archivo autoritativo publicado de16 conserva su hash original; los ZIP del benchmark son diagnósticos.

Este resultado mide empaquetado, no evolución ni duración total de la conservación. No elimina auditorías, hash, recuperación independiente, guardado nativo, descarga pública, reserva o activación. No serializa nuevamente matrices ni reduce precisión. [Registro](../checkpoints/CP12/p3_20261018/conservacion_rapida_20261105/REGISTRO.json) · [mediciones](../checkpoints/CP12/p3_20261018/conservacion_rapida_20261105/COMPARACION_EMPAQUETADO.json) · [controles adversos](../checkpoints/CP12/p3_20261018/conservacion_rapida_20261105/CONTROLES_ADMINISTRATIVOS.json) · [método](../checkpoints/CP12/p3_20261018/conservacion_rapida_20261105/README.md).

## Alcance y siguiente acción

La pareja en16 es positiva; no demuestra la aceptación final en160, orden radial global seis ni estabilidad general. Siguen pendientes las tres ventanas causales, reducción original≥50% del canal operadorχ acoplado, tercera malla/orden observado justificados, referencia independiente, interpolación, angular/caja, estabilidad temporal y robustez. P2 conserva su negativo80 y sigue suspendido. No se reabren campañas cerradas.

El head de entrada verificado fue `0e647ac1870aa21243ff1960cd4f0c982134bb0b`; main conserva CP11 en `90e8fcffbba65629a1628f435d3c3240832fe9c4`. El commit que contiene este informe identifica la entrega; los recibos posteriores identifican sus respaldos sin autorreferencias de hash.

Se preparó el [registro16→24](../checkpoints/CP12/p3_20261018/reanudacion_t16_20261105/REGISTRO.json) con el código administrativo rápido y las fuentes científicas originales. Antes de física necesita restauración exacta, capacidad nativa y pública del proceso real, reserva publicada y activación coincidente. Conservar cada1,6 y aplicar nuevamente todas las puertas en24; un negativo se conserva y suspende. Los recibos posteriores de esa asignación actualizan su preparación sin convertir un latido en certificado de reinicio.
