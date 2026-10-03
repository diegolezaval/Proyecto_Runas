# Entrega 07 · Acceso lineal y continuidad parcial

Se retomaron los estados pendientes de CP06, que continúa CP04. E00, E01 y C0 no se repitieron. La auditoría de lectura confirma que sus estados y 154 archivos protegidos conservan los hashes de CP04. Se preservan los fallos numéricos anteriores, incluidos los intentos que no admiten continuación física fiable.

## Resultados completados

**Acceso lineal a Reserva.** Sobre el perfil ya guardado de ω=0.9 se derivó y resolvió la dispersión de los dos campos, con dos bandas cargadas y el mediador como canal cerrado dinámico. No se recalculó el fondo. Se completaron 46 soluciones de malla, ocho controles y tres verificaciones independientes por colocación de la ODE continua. Se auditó la linealización contra la fuerza no lineal y los flujos contra la corriente y el tensor de M2.

La incidencia de carga negativa se convierte parcialmente a una banda de mayor frecuencia. En las nueve frecuencias probadas la mayor ganancia de flujo energético es **0,157 %**, en Ω=2.3. La contabilidad da ΔE=ωΔQ. La onda incidente aporta energía positiva y carga negativa; el fondo debe ceder el incremento exterior a segundo orden. Esa retroacción no se ha evolucionado en este cálculo infinitesimal.

El último cambio de malla en probabilidad de conversión es como máximo 1,60 %. El contraste independiente difiere como máximo 0,239 %. El defecto de unitariedad es menor de 1,1×10⁻¹³ en la campaña discreta. Se conserva el primer intento de colocación complejo que no convergió; la reformulación real/imaginaria con Jacobiano de frontera explícito pasó sin relajar las tolerancias finales. La puerta acepta esta subpregunta y mantiene RES0 PARCIAL y RES2 BLOQUEADA.

**Fase estacionaria de C7.** Se demuestra mediante conservación de corriente, truncamiento de fase y corte espacial que un estado monofrecuencial C²∩H¹ sin ceros en R³ tiene fase espacial constante. No se presupone fase acotada. Aplicar el resultado de CP05 excluye que una fase suave salve una cadena estacionaria localizada sin nodos, bajo las otras hipótesis del capítulo 27. No se repite su prueba ni se declaran resueltas las alternativas nodales o dinámicas. C7 sigue PARCIAL. La prueba es propia y explícita, sin certificación formal ni revisión externa atribuida.

## Continuación no radial: puerta aún no superada

Se terminó el control `split4c` fino desde su último estado válido, τ=136, hasta 160. Su deriva energética máxima es 1,733×10⁻⁵. El esquema grueso falla a tiempos largos: 2,354 % en h=0.5 y 1,072 % en h=0.25 al interrumpirse en τ=112. Los pilotos `split4b` no mejoraron la fase y se conservaron sin prolongarlos. Estos son fallos numéricos; no se presentan como una inestabilidad física del depósito.

Se pasó a DOP853 sobre las fuerzas completas de M2, sin cambiar su acción. Los dos pilotos a τ=8 pasaron y se continuaron desde allí. Tres evoluciones adaptativas completaron τ=160; el control espacial h=0.25 se reanudó desde τ=120 tras perderse su sesión. No se reiniciaron los casos terminados. La conservación se vigiló en cada paso aceptado.

| Control adaptativo | Φ: diferencia final de campo | χ: diferencia final de campo | χ: diferencia con velocidades | Puerta |
|---|---:|---:|---:|---|
| Tolerancias 10⁻⁸→10⁻⁹, h=0.5 | 0,0000152 % | 0,00191 % | 0,00272 % | Superada |
| Mallas h=0.5→0.25, tolerancia 10⁻⁹ | 1,123 % | 4,034 % | 5,009 % | Falla el límite de 2 % |

Las diferencias se normalizan por la perturbación inicial no radial en el núcleo r<40; se elimina sólo la fase global de Φ. El diagnóstico que incluye velocidades usa ‖(δq,δv/masa)‖. La buena conservación y el pequeño error temporal no eliminan el error espacial de χ. Los ocho casos Verlet de CP06 y el fallo angular L2→L4 permanecen íntegros y no se repiten.

**Siguiente prueba prerregistrada:** h=0.125, DOP853 con rtol=10⁻⁹, atol=10⁻¹¹, paso máximo 0.02, L=4, R=220, ε=0.02 y τ=160. Esta nueva malla toma los campos guardados de CP04; si tiene un reinicio propio, continúa desde su tiempo explícito. Se conserva el umbral de 2 %. En CP07 todavía no está completada.

## Estado y reanudación

Checkpoint: **CP07_ACCESO_LINEAL_PARCIAL**. E02/E03/E04/RES0/RES1/C7 siguen PARCIALES. RES2 y las etapas funcionales dependientes siguen BLOQUEADAS. No se declara estabilidad orbital, ciclo de Reserva, dispositivo completo ni M3.

Los capítulos 28–30 contienen método, derivaciones y límites. Las puertas están en `validacion/P06/no_radial/intento_08_mediador_radial_h025.json`, `validacion/P06/acceso_lineal/puerta_decision.json` y `validacion/P04/C7/puerta_fase_sin_nodos.json`. `datos/registro_calculos.json` distingue los cálculos completados de los parciales y de la nueva malla pendiente.

Para continuar únicamente el refinamiento pendiente:

```bash
OPENBLAS_NUM_THREADS=1 python herramientas/continuar_no_radial_adaptativo.py --rtol 1e-9 --atol 1e-11 --dx .125
python herramientas/verificar_no_radial_m2.py
```

El primer comando reutiliza su estado si existe y no vuelve a la gaussiana original. El segundo lee resultados guardados. Aplicar la puerta, registrar cualquier nuevo fallo y emitir el siguiente checkpoint antes de atribuir cierre al subensayo. No ejecutar reproducción histórica como sustituto de esa continuación.
