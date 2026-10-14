# Recuperación pública τ80 certificada

En el clon limpio del commit `1d36903d7029c72528b7be6b566eb3f587fd7c0b`, las 145 partes JSON reconstruyen los 29 335 404 bytes del NPZ original, SHA-256 `645a2d701fd9395b3f1d6f77b95a784fc1e99106af2ce92b475cc906c4b78d01`. Pasan las 33 pruebas del auditor original, con 201 observaciones CP10 exactas por malla y cero pasos M2. Las catorce fuentes científicas y la puerta del 2 % permanecen originales.

El primer destino local sufrió un cambio de integridad posterior a su reconstrucción correcta. Su causa no está identificada y el resultado negativo se conserva. En dos destinos nuevos pasan todas las comprobaciones, incluido que el archivo auditado no cambie; la última prueba usa el adaptador original sin instrumentación. La certificación se refiere a estas recuperaciones completas verificadas, y no convierte el primer resultado en positivo.

El recibo de recuperación pública es nuevo; no reconstruye el recibo privado histórico. CP12 continúa abierto. Main permanece en CP11 y el PR #2 abierto y en borrador. No hay frontera τ88 certificada en esta recuperación.
