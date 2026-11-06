# Relevo breve del ejecutor Rúnica

Leer primero [RECUPERACION_CP12_ACTUAL.md](RECUPERACION_CP12_ACTUAL.md) y [el registro canónico](checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json). Consultar head,Release y Biblioteca posteriores antes de ejecutar. No inferir actividad de una sesión histórica.

CP11 aceptado;CP12 abierto;P3 sin validar. Última frontera completa positiva16;último transporte recuperado22,4 con límite24. El adjunto718197317 y libfile_142d2f9ee5388191a13da1520ed45dc8 conservan230372773 bytes,SHA256287581812d0c2c3fc0dd7bef2731b2eaf08aa20fa19a60e0421c9a85f5c1de00;350 cargas y30+14 controles originales,cero evolución en auditorías. [Recuperación22,4](checkpoints/CP12/p3_20261018/recuperacion_t224_20261106/ORIGEN.json).

La sesión77606 y su directorio son inaccesibles;salida no observada,no reactivar p3_16_a24_20261106 ni recrear su archivo privado de publicación. La asignación nueva p3_224_a24_20261106,proceso44909,restauró toda la memoria interna a22,4 y completó capacidad propia nativa/pública. [Reserva y recibos](checkpoints/CP12/p3_20261018/reanudacion_t224_20261106/ASIGNACION_224_A24.json). Comprobar activación y recepción posteriores:su publicación sola no acredita evolución.

## Acción y conservación

Continuar sólo22,4→24 con el ejecutor rápido anterior íntegro. No repetir intervalos hasta22,4. Cada0,4 guarda estado interno;cada1,6 y frontera exige la ruta anterior hasta cerrar24. En24:recuperación pública independiente,cinco métricas espaciales originales y todos los controles físicos antes de otro tramo.

La [enmienda híbrida](checkpoints/CP12/p3_20261018/conservacion_hibrida_20261106/ENMIENDA.md) se registra antes de usarla y sólo en una asignación nueva desde24 o posterior. Ruta:local exacto0,4;Biblioteca persistente y recuperación original cada1,6;dos últimos transportes verificados;fronteras8 completas en Releases con descarga independiente y todas las puertas. Capacidad,reserva y activación son propias del proceso real. Negativos/incidentes se conservan inmediatamente. No modificar trabajadores activos.

Rotación:conservar anterior hasta guardar,recuperar y auditar nuevo;retirar sólo identidades inscritas de esta ejecución y registrar reemplazo. Tras frontera pública positiva puede retirarse lo sustituido. Excluir migración,archivos ajenos,evidencia única,negativos e incidentes. Ante pérdida durante retirada,reconciliar diario e identidades persistentes antes de reintentar. No hacer limpieza histórica general.

## Invariantes y fuentes

Aplicar DIRECTRICES_DESARROLLO.md y DIRECTRICES_EJECUCION.txt;ARQUITECTURA.md orienta la estructura. Consultar protocolos y fuentes afectados. El panorama20261029 es histórico y se contrasta con evidencias posteriores;no reconstruir campañas cerradas para retomar.

P3 mantiene Φ-FV y χ=A2+h²A2²/12+h⁴A2³/90,M2,Θ,CP04 original sin suavizar,h=.125/.0625,R220,L4,ε=.02,DOP853 rtol1e-10/atol1e-12/max_step.02,observadores y contadores originales. No afirmar orden radial global seis. Restaurar solver,memoria densa,pasiva y contadores;no reconstruir continuación exacta desde matrices observadas. El compilador exacto13.3.0 está recuperado;no forzar BLAS ni cambiar auditores.

Fuentes científicas:[prerregistro](checkpoints/CP12/p3_20261018/PRERREGISTRO_PILOTO.md),DERIVACION.md,REGULARIDAD_Y_ORDEN.md,DISPERSION_Y_ALCANCE.md y CERTIFICADO_F0_F5.json en P3. Mantener separadas energías consistente yFV≤2e-4,carga≤1e-9,cinco métricas espaciales≤.02,identidades/simetría≤2e-12,Parseval≤2e-11,observadores≤1e-3 y controles de núcleo/amplificación aplicables. Auditorías:cero construcciones/pasos DOP853 y cero evolución M2.

Negativo científico:conservar,recuperar y suspender esa versión;no lanzar candidato automático. P2 conserva su negativo80 y no se reanuda;no repetir CP10,CP12 original,CP04 ni F0…F5. τ160 no cierra P3/CP12:quedan tres ventanas causales,reducción original≥50% del canal operadorχ acoplado,tercera malla/orden justificados,referencia independiente,interpolación,angular/caja,estabilidad temporal y robustez.

Trabajar autónomamente por entregas recuperables. Git conserva código,decisiones y registros pequeños;Releases las cápsulas científicas. No empaquetar otra vez todo el repositorio por cada transporte. Informar avance físico,transporte recuperable y frontera científica por separado. El historial de este relevo permanece en Git.
