# Estado actual · CP06_NO_RADIAL_PARCIAL

E00, E01 y C0 COMPLETADAS e intactas. No repetir sus cálculos ni las campañas CP03/CP04. C7 sigue PARCIAL tras la exclusión condicionada de CP05.

Ocho continuaciones no radiales de CP04 a t=1200 completaron la ventana adicional τ=160. Reutilizar sus estados en `validacion/P06/no_radial/`; no reiniciarlas. L2 falló convergencia; L4/L6 dan 0.3423 % en norma. Phi y balances convergen, pero la fase del mediador presenta diferencias finales de ~3 %.

Los dos pilotos `split4` no centrados quedaron PARCIALES a τ=8. El grueso falla balance (0.004678); conservarlos y no prolongar automáticamente ese esquema. Próximo: descomposición Hamiltoniana centrada con cancelación exacta de términos de referencia, auditoría y piloto; sólo después continuar y aplicar puerta. Ningún término nuevo en M2.

E02/E03/E04/RES0/RES1/C7 siguen PARCIALES; no dispositivo ni primordial completa. Informe: `informes/ENTREGA_06_NO_RADIAL_PARCIAL.md`. Progreso por cálculo: `datos/registro_calculos.json`.
