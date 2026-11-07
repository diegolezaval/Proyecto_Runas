# Relevo breve del ejecutor Rúnica

Leer primero [RECUPERACION_CP12_ACTUAL.md](RECUPERACION_CP12_ACTUAL.md) y [el registro canónico](checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json). Consultar head,Release y Biblioteca posteriores antes de ejecutar. No inferir actividad de una sesión histórica.

CP11 aceptado;CP12 abierto;P3 sin validar. Última frontera completa positiva24:358 cargas,30 controles originales,cinco métricas espaciales y diez controles físicos positivos. [Origen y recibos24](checkpoints/CP12/p3_20261018/frontera_t24_20261106/ORIGEN.json). Adjunto718257706:230562086 bytes,SHA25613660aae72467ccb2eda738d773103c8b14cb1950f4ed84a959cfb6f3f10fed6. Biblioteca:libfile_ddacdad0b1148191828315263c178493.

44909 terminó22,4→24 con salida0 observada. La carpeta temporal se perdió después;el estado24 se recuperó desde ambos destinos sin repetir física. Las cinco métricas coinciden exactamente.77606 permanece históricamente inaccesible,sin terminación presumida. No reactivar asignaciones anteriores ni recrear sus archivos privados de publicación.

## Acción y conservación

La asignación nueva `p3_288_a32_hibrido_20261107` está preparada desde τ28,8, recuperado con 381 cargas y 44 controles originales. La sesión 75320 está inaccesible y su salida queda sin observar. La nueva capacidad nativa conserva el estado exacto y la pública usa la frontera pública τ24. Recuperar la reserva y la activación antes de evolucionar. Consultar el [registro de la asignación](checkpoints/CP12/p3_20261018/reanudacion_hibrida_t288_20261107/REGISTRO.json) y el [aislamiento](checkpoints/CP12/p3_20261018/reanudacion_hibrida_t288_20261107/AISLAMIENTO.json). Evitar repetir intervalos hasta τ28,8.

La [enmienda híbrida](checkpoints/CP12/p3_20261018/conservacion_hibrida_20261106/ENMIENDA.md) pasó33 controles administrativos y debe estar publicada y recuperada antes de usarla. Local exacto0,4;Biblioteca persistente con recuperación original cada1,6;dos últimos transportes verificados;fronteras8 en Releases con descarga independiente y todas las puertas. Capacidad,reserva y activación propias del proceso real. No modificar trabajadores activos.

Rotación:conservar anterior hasta guardar,recuperar y auditar nuevo;retirar sólo identidades verificadas y registrar reemplazo. Tras frontera pública positiva puede retirarse lo sustituido. Excluir migración,archivos ajenos,evidencia única,negativos e incidentes. Ante pérdida durante retirada,reconciliar diario e identidades persistentes,sin reintento ciego. No hacer limpieza histórica general.

## Invariantes y fuentes

Aplicar DIRECTRICES_DESARROLLO.md y DIRECTRICES_EJECUCION.txt;ARQUITECTURA.md orienta la estructura. Consultar protocolos y fuentes afectados. El panorama20261029 es histórico y se contrasta con evidencias posteriores;no reconstruir campañas cerradas para retomar.

P3 mantiene Φ-FV y χ=A2+h²A2²/12+h⁴A2³/90,M2,Θ,CP04 original sin suavizar,h=.125/.0625,R220,L4,ε=.02,DOP853 rtol1e-10/atol1e-12/max_step.02,observadores y contadores originales. No afirmar orden radial global seis. Restaurar solver,memoria densa,pasiva y contadores;no reconstruir continuación exacta desde matrices observadas. El compilador exacto13.3.0 está recuperado;no forzar BLAS ni cambiar auditores.

Fuentes científicas:[prerregistro](checkpoints/CP12/p3_20261018/PRERREGISTRO_PILOTO.md),DERIVACION.md,REGULARIDAD_Y_ORDEN.md,DISPERSION_Y_ALCANCE.md y CERTIFICADO_F0_F5.json en P3. Mantener separadas energías consistente yFV≤2e-4,carga≤1e-9,cinco métricas espaciales≤.02,identidades/simetría≤2e-12,Parseval≤2e-11,observadores≤1e-3 y controles de núcleo/amplificación aplicables. Auditorías:cero construcciones/pasos DOP853 y cero evolución M2.

Negativo científico:conservar,recuperar y suspender esa versión;no lanzar candidato automático. P2 conserva su negativo80 y no se reanuda;no repetir CP10,CP12 original,CP04 ni F0…F5. τ160 no cierra P3/CP12:quedan tres ventanas causales,reducción original≥50% del canal operadorχ acoplado,tercera malla/orden justificados,referencia independiente,interpolación,angular/caja,estabilidad temporal y robustez.

Trabajar autónomamente por entregas recuperables. Git conserva código,decisiones y registros pequeños;Releases las cápsulas científicas. No empaquetar otra vez todo el repositorio por cada transporte. Informar avance físico,transporte recuperable y frontera científica por separado. El historial de este relevo permanece en Git.

Para comparar controles sin rehacer código,usar [la utilidad reutilizable](checkpoints/CP12/p3_20261018/conservacion_hibrida_20261106/COMPARADOR_REUTILIZABLE.md). Reutilizar recibos con entradas idénticas;no ejecutar otra campaña ni benchmark.
