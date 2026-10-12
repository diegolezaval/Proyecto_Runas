# CP12: recuperación independiente ab914d1d0470

La rama de esta ejecución es `ciencia/cp12-recuperacion-aislada-20261012-ab914d1d0470`, separada de main y PR #2. Ambos se conservan en CP11/CP12 abierto, respectivamente; no se integran ni se sobrescriben evidencias anteriores.

Última frontera independiente guardada, recuperada y auditada: **τ40**. El tramo **40→48** está en curso con sus dos trayectorias originales, sin cambios de M2, Θ, solver, tolerancias, observadores o puerta del 2 %. Los latidos no son certificados de reinicio.

Identidad nueva: `3f7a6b3251ed7f27696fc6d1015449b502a8513aa2c30cf15422e0e0361551ed`. Estado τ40 SHA256: `d20716451e62e8974e305391d36188354bf42fed2c5ba7595b0c56703f3d2ec0`. Cápsula independiente SHA256: `249873eb73ab81fe1ad709096e5422c759edcf77b322e4694a1f7f834bb1540a`. La configuración conserva SHA256 `148dfb982ce59ff5e9e7696749f58c77584c96c2833ca5fb4bd03122af5e5541`; pasan los controles, prefijo CP10 exacto y recarga original sin avance.

El ejecutor original y el intento anterior se consideran no autoritativos y potencialmente activos, con rutas y resultados separados. No se les consulta ni controla. Sólo este espacio publica resultados de esta identidad.

Los diagnósticos pasivos de regularidad y dispersión se conservan en `trazabilidad/CP12_recuperacion_independiente/ab914d1d0470/analysis/`. La sustitución angular ingenua falla para ℓ=1; ambas discretizaciones espectrales probadas conservan orden dos y el contraste regular tiene errores mayores en los tres modos ℓ=2 examinados. La referencia de dispersión de ondas cortas no identifica por sí sola el error de χ.

Siguen pendientes τ160, reproducción final CP10 exacta, interpretación de Duhamel y pruebas suficientes de una corrección. CP12 permanece abierto.

La frontera τ40 conserva 101 observaciones CP10 exactas. Todas las pruebas del auditor original pasan, incluida recarga sin avance. Los contadores científicos incluyen la ascendencia τ0→24 y los dos segmentos nuevos 24→32→40; el campo de origen con cero segmentos describe el registro inicial. La contabilidad nfev reproduce la definición original CP10, no el coste total de instrumentación.

La lectura provisional τ40 cierra χ en toda la caja con residuos relativos [3.9397212297032346e-07, 5.154441557243219e-07]. El error de fases del núcleo es .0166620532; no es una decisión final de aceptación. El operador χ y el grupo de operadores cumplen las tres ventanas a ese tiempo provisional. La referencia estacionaria a Φ no explica el defecto y su retirada lo empeora; el residuo no estacionario domina la descripción. El Jacobiano local muestra una rama alta con participación χ próxima a uno y una firma de signo compatible, sin predicción de la historia global.

Un candidato matemático de operador conserva la masa, potencial y carga originales, respeta todos los momentos regulares ensayados y pasa variación y carga. No tiene backend de observadores ni trayectoria física validada; sus errores espectrales globales siguen siendo de orden dos y algunos modos empeoran. No se declara corrección ni cierre.
