# Entrega 06 · Continuación no radial parcial

Se continuó el estado fino de CP04 a t=1200. No se repitieron E00, E01, C0 ni la preparación cerrada. CP05 y todos los fallos anteriores permanecen íntegros.

Ocho evoluciones nuevas de los dos campos completaron τ=160: todos los armónicos reales hasta L=2,4,6, con sus m, dos pasos radiales, dos temporales, dos amplitudes, control sin perturbación y comparación de cajas. La deformación inicial es un cuadrupolo triaxial localizado. No se afirma haber probado todas las perturbaciones tridimensionales.

La máxima deriva relativa de energía es 3.34×10⁻⁶ y de carga 1.12×10⁻¹⁴. La norma no radial no supera su valor inicial en estos ensayos. La carga del núcleo cambia menos de 1.07×10⁻⁴ relativos. Las unidades son las del benchmark; no se extrapola a retención macroscópica.

| Control | Diferencia de normas | Decisión |
|---|---:|---|
| L=2 → 4 | 34.16 % | Falla; resultado conservado |
| L=4 → 6 | 0.3423 % | Pasa el límite angular de 5 % |
| h=0.5 → 0.25, L=4 | 0.5883 % | Pasa el límite de 2 % para esta norma |
| Δt=0.004 → 0.002, L=4 | 0.01198 % | Pasa el límite de 2 % para esta norma |
| R=220 → 260 | Cambios del núcleo <7×10⁻¹⁵ | Sin efecto resoluble en la ventana |

Las diferencias finales de campos complejos, descontando sólo la fase global, son 1.68 % angular, 1.13 % espacial y 0.0168 % temporal. Pero el mediador presenta diferencias de 3.49 % espacial y 2.87 % temporal respecto de su perturbación inicial: el control completo de sus oscilaciones rápidas queda pendiente. La buena conservación no cierra ese error de fase.

Se probó un integrador alternativo con flujo de masa exacto y composición simétrica de cuarto orden. Su auditor de orden converge con factores 15.74 y 15.93, pero el piloto M2 no centrado a τ=8 falla el balance en Δt=0.004 (deriva 0.004678). El piloto Δt=0.002 tiene deriva 1.423×10⁻⁵. Ambos estados se conservan como PARCIALES; no se prolonga automáticamente el esquema que falló. La siguiente investigación centrará la descomposición alrededor de datos guardados, con términos que se cancelan en la acción total, antes de verificarla otra vez.

La transferencia publica el inventario exterior omitido, la interpolación y la perturbación añadida. La caja original de R=1300 y sus campos a t=1200 siguen intactos. No se confunde el ensayo local con la evolución de todo ese exterior.

Se enlaza la identidad angular histórica de 14.4 con la monotonía demostrada en CP05. Es una consecuencia condicionada para soluciones estacionarias exactas; no una nueva campaña espectral ni estabilidad orbital no lineal demostrada.

**Puerta:** los observables de Φ superan los controles declarados tras refinar L, pero la campaña completa sigue EN_PROGRESO por el mediador y el integrador alternativo fallido. E02/E03/E04/RES0/RES1/C7 permanecen PARCIALES. No se habilita un ciclo de Reserva, un dispositivo ni M3.

**Estado reanudable:** `datos/registro_calculos.json` distingue las ocho evoluciones terminadas de los pilotos parciales a τ=8. No repetir las primeras. Continuar la verificación numérica pendiente; el checkpoint siguiente deberá conservar todos estos resultados.
