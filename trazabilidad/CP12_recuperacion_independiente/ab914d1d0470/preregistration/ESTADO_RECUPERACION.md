# CP12: recuperación independiente ab914d1d0470

La rama de esta ejecución es `ciencia/cp12-recuperacion-aislada-20261012-ab914d1d0470`, separada de main y PR #2. Ambos se conservan en CP11/CP12 abierto, respectivamente; no se integran ni se sobrescriben evidencias anteriores.

Última frontera independiente guardada, recuperada y auditada: **τ32**. El tramo **32→40** está en curso con sus dos trayectorias originales, sin cambios de M2, Θ, solver, tolerancias, observadores o puerta del 2 %. Los latidos no son certificados de reinicio.

Identidad nueva: `3f7a6b3251ed7f27696fc6d1015449b502a8513aa2c30cf15422e0e0361551ed`. Estado τ32 SHA256: `929f956875a1fa14fda9e7aeaf1505d11cdc7d2e0be3fc72b7d7e7a5e300aa58`. Cápsula independiente SHA256: `f3d156eabf887e1fe7b71c3d23596a44b3a627c4e56c6f9e6bb1177d8808e58f`. La configuración conserva SHA256 `148dfb982ce59ff5e9e7696749f58c77584c96c2833ca5fb4bd03122af5e5541`; pasan los controles, prefijo CP10 exacto y recarga original sin avance.

El ejecutor original y el intento anterior se consideran no autoritativos y potencialmente activos, con rutas y resultados separados. No se les consulta ni controla. Sólo este espacio publica resultados de esta identidad.

Los diagnósticos pasivos de regularidad y dispersión se conservan en `trazabilidad/CP12_recuperacion_independiente/ab914d1d0470/analysis/`. La sustitución angular ingenua falla para ℓ=1; ambas discretizaciones espectrales probadas conservan orden dos y el contraste regular tiene errores mayores en los tres modos ℓ=2 examinados. La referencia de dispersión de ondas cortas no identifica por sí sola el error de χ.

Siguen pendientes τ160, reproducción final CP10 exacta, interpretación de Duhamel y pruebas suficientes de una corrección. CP12 permanece abierto.

La frontera τ32 conserva 81 observaciones CP10 exactas. Contadores por malla: [5892, 5890] pasos aceptados y [71396, 71372] evaluaciones. El máximo error de los observadores es 5.80276454e-07, frente al límite original 1e−3. Estos contadores incluyen la ascendencia τ0→24; sólo 24→32 se ejecutó en esta identidad. El campo de origen de segmentos nuevos vale cero en el registro inicial; el historial de segmentos documenta los avances posteriores.
