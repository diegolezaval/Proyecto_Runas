# CP12: controles independientes de la hipótesis P3

P3 superó F0…F5 con cero pasos M2, cero intentos DOP853 y las472 cargas históricas idénticas antes/después. La propuesta se publicó en538ef76, el código en c7a61e6 y el contraste adicional F5 en967d0bf antes de ejecutarse. El nuevo término se limita aχ; no modifica Φ, masa, fuente ni potencial. El ensayo P2 conserva su negativo válidoτ80 y no se reanuda.

| Control | Casos conservados | Resultado |
|---|---:|---|
| F0, forma y símbolo |15 matrices,50 perfiles fabricados | Positividad, siete bandas y consistencia; orden radial≈2 |
| F1, acción/gradiente/carga/trabajo |6 estados, ambas mallas | Todos los residuos≤2e-12; fuerza C original equivalente |
| F2, identidad y Jacobiano |15 parejas estáticas | Defecto completo máximo 1.46617391939e-12; signos y cancelaciones conservados |
| F3, matriz/resolvente |6 fondos, GL7/6 | Acción, simetría y resolventes≤2e-12 |
| F4, referencia congelada |6 fondos, GL7/6 | Fases máximo 5.9070089537e-12, balance 4.5400117542e-13 |
| F5, incremento aislado |25 modos/mallas | Error energía 1.90216284102e-13; gradiente 2.69326312324e-13 |

La referencia independiente de F4 usa exponencial dispersa, Taylor32 con16/32 subpasos prefijados y una cota analítica de truncamiento. Su peor contraste/cota es 3.91117609769e-15, frente a1e-8. No es aritmética de intervalos. Ningún control de propagación congelada equivale a una trayectoria M2 autoconsistente.

F5 se añadió prospectivamente para aislar la energíaβ de la escala de la energía total. No se modificaron F0…F4 ni sus límites. Su texto registra el estado de observación pendiente de F4; la terminación efectiva de F4 quedó grabada a16:38:18,857UTC antes de recogerla. La prueba adicional se ejecutó sólo tras comprobar ese positivo. No hubo negativos de estos seis controles ni ajustes posteriores para aprobar.

La energía semidiscreta P3 es positiva en su parte espacial y su gradiente produce el mismo operador deχ. La energía FV original permanece una puerta independiente y todavía no se ha ensayado su deriva durante física nueva. Los perfiles centradosℓ2/4 dan últimos órdenes 1.999844295 y 1.998630413: añadir P3 no elimina el residuo geométricoh² ni justifica llamar al operador radial de orden seis. La exposición inicial adversa documentada en D2 se conserva.

Fuentes, resultados completos y certificado: `checkpoints/CP12/p3_20261018/`. La cápsula de controles fue guardada, recuperada y verificada por cada hash; SHA256 `661f374756bd01a1d7cba06de9fb09a067eecfd066e619433a5afda40086b134`, 232942913 bytes. La conservación acredita integridad, no una frontera física.

Estos resultados permiten preparar y registrar un piloto P3 nuevo desde los datos de Cauchy originales exactos. Antes de M2 faltan identidad propia yτ0 guardado/recuperado/auditado. Después deberán pasar las dos energías2e-4, carga1e-9, cinco métricas2% y todos los controles de observadores en cada frontera. CP12 sigue abierto; CP11 aceptado. Main y PR2 permanecen intactos. La causalidad final, tercera malla/orden, referencia, interpolación, angular/caja, estabilidad y robustez siguen pendientes. Son resultados numéricos, sin validación física experimental.
