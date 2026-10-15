# CP12 · Frontera τ96 conservada y verificada

La cápsula completa τ96 se conservó, recuperó y auditó antes de iniciar 96→104. Una segunda recuperación independiente del respaldo permanente verificó tamaño y SHA256 del ZIP, cobertura exacta y los 243 hashes de carga. Pasaron los 33 controles originales con cero pasos M2 en las auditorías.

- ZIP: 38 397 584 bytes; SHA256 `38184f857b0195255f70ce4e02a0fca4b584c31f8d6c5a8f565123eea85f3452`.
- Estado: SHA256 `4bdb57d4e06516367f19a1c90955835b4924bbf40ef219eebd2ecb41b64c1ece`.
- Configuración original: SHA256 `148dfb982ce59ff5e9e7696749f58c77584c96c2833ca5fb4bd03122af5e5541`.
- 241 observaciones por malla, prefijos CP10 `array_equal`.
- Malla .125: 17 258 pasos, 208 380 evaluaciones; malla .0625: 17 291 pasos, 208 776 evaluaciones.
- Derivas máximas de energía inferiores a 2.614e-10 y de carga inferiores a 2.665e-15.
- Cierre escalar máximo 2.925e-6; acoplado 2.773e-6, ambos inferiores a la puerta original 1e-3. Pasan controles de orden, Parseval, simetría, identidades y observadores.

Los contadores intermedios se conservan con su contabilidad original; la igualdad final completa de pasos, evaluaciones, campos, velocidades, observaciones y balances con CP10 se exigirá en τ160. El comprobante legible está en `checkpoints/CP12/continuacion_20261014/tau0096/AUDITORIA_FRONTERA_GUARDADA.json`. La cápsula completa permanece privada; la recuperación numérica pública completa sigue en τ80. Este comprobante no afirma haber publicado un NPZ τ96 reconstruible desde JSON.

Se observó el inicio de 96→104 después de la conservación positiva. La actividad no certifica τ104. No se duplicó M2 ni se modificó código bajo el trabajador activo. El generador original actualiza la vista de continuidad desde el estado canónico; las 33 etapas y todos los negativos se conservan.

CP12 permanece abierto: faltan τ160 y la interpretación de las tres ventanas, con integrales, cancelaciones y realimentación. Estos cierres numéricos parciales no prueban una causa dominante ni una corrección eficaz. M2, Θ, solver, tolerancias, observadores, ambas trayectorias y la puerta del 2 % permanecen originales. Main sigue CP11 y PR #2 abierto/borrador, sin merge, tag ni Release.
