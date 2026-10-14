# CP12: recuperación científica y continuación desde τ80

La frontera τ80 conserva exactamente los estados de h=0.125 y h=0.0625, observadores, presupuestos causales y 201 observaciones CP10. El ZIP de entrada tiene SHA-256 `709cbb21e338b78597e6b4708a3d89dd0a60997c5d7f7cc085e2e65da5a7584c`; el NPZ científico, `645a2d701fd9395b3f1d6f77b95a784fc1e99106af2ce92b475cc906c4b78d01`.

El respaldo privado completo se guardó, recuperó y auditó de forma independiente. La publicación pública omite metadatos privados del ejecutor y sus recibos operativos. No altera ningún array científico, configuración, fuente original o criterio. El recibo público se registra como una recuperación nueva: no reconstruye ni suplanta el recibo histórico privado.

`COMPROBACION_CONTENIDO_PUBLICO.json` enumera todos los miembros del NPZ, tipos, formas, límites numéricos y hashes de sus partes. Sólo contiene arrays NumPy científicos y JSON del protocolo, contadores y presupuestos; no contiene objetos pickle, credenciales, rutas del ejecutor ni sus identificadores privados.

Para recuperar y auditar desde un clon limpio, con las dependencias de `requirements.txt`:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 checkpoints/CP12/continuacion_20261014/auditar_frontera.py --boundary 80
```

El adaptador reensambla bytes sin pérdidas, verifica cada hash, registra explícitamente el recibo nuevo y ejecuta el auditor original sin pasos M2. El auditor científico original y sus catorce fuentes conservan sus bytes. Main y PR #2 permanecen intactos; el PR sigue abierto y en borrador. Los resultados negativos anteriores se conservan. Alcanzar τ160 no cerrará CP12: exige las puertas causales y la validación física original del 2 %.
