# CP12 · Prueba pasiva factorial de P4

**P4 pasa la prueba pasiva registrada.** El criterio en τ160 exigía que la combinación redujera la potencia de χ y χ̇/μ para ℓ=2 y ℓ=4, dentro de r<40 y en k de referencia >8. La señal se mantuvo con los dos órdenes pasivos y las dos interpolaciones de sensibilidad.

## Efectos en el corte tardío

Cada porcentaje es el cambio de potencia respecto a la respuesta P3 con el conmutador P3, en el mismo modo, ventana e interpolación. Un valor negativo indica reducción.

| Cúbica original y GL7 | Cambiar el conmutador | Cambiar el propagador | Cambiar ambos |
|---|---:|---:|---:|
| ℓ=2 | −0,6040 % | −9,9844 % | −11,7365 % |
| ℓ=4 | −2,7820 % | −8,6924 % | −12,4398 % |

| Interpolación, GL7 | Combinado ℓ=2 | Combinado ℓ=4 |
|---|---:|---:|
| Cúbica original | −11,7365 % | −12,4398 % |
| Cúbica con paridad en el origen | −11,7365 % | −12,4398 % |
| Cúbica fina→gruesa | −82,8072 % | −79,5620 % |

El propagador aporta la mayor reducción aislada en la comparación original. En la inversa, donde cambia la malla de destino, el conmutador explica la mayor reducción y el propagador aislado aumenta ligeramente la potencia (+0,0749 % y +0,0869 %). Esta sensibilidad afecta la atribución y la magnitud. La señal factorial combinada satisface la puerta en ambos sentidos.

En τ112, con cúbica original y GL7, el combinado dio −11,7411 % y −12,4478 % en los mismos modos y banda. En τ160, el contraste geométrico regular k≤4/8 quedó por debajo de 1,46×10⁻⁷ de la magnitud del efecto combinado en la banda de decisión. Esa estimación cubre la contribución de la proyección regular. Los JSON incluyen las dos componentes de fases, sus signos y las ventanas radialmente separadas, incluida 40≤r<220.

## Controles y reproducción

- Los adjuntos 750322957 y 750993142, el CMS de τ160 y las 621 y 747 cargas de ambos respaldos satisfacen las huellas registradas. Se reutilizaron las auditorías originales exactas de recuperación.
- El error relativo máximo GL7/GL6 fue 1,663×10⁻¹¹, frente al umbral 10⁻³. Los controles fabricados del resolvente y de la proyección geométrica dieron 1,279×10⁻¹¹ y 2,227×10⁻¹³. Pasaron Parseval, la identidad firmada de cambio de potencia y el cierre de linealidad.
- Se integró cada brazo durante Δτ=.4 con Jacobiano y fuente congelados, desde respuesta homogénea nula. Los contadores físicos registran **cero pasos nuevos de M2**. Esta puerta decide si procede evaluar un piloto físico independiente desde τ0. El límite oficial del 2 % se aplica a ese piloto.
- El intento inicial se detuvo por desajuste entre las bases angulares al preparar la geometría. Se registró la corrección antes de repetir, con las mismas entradas y los mismos criterios. [Enmienda](../checkpoints/CP12/p4_20261115/prueba_pasiva/ENMIENDA_EJECUCION.md)

El recibo identifica las huellas del código, de los resultados completos por corte y de los vectores pasivos. En el entorno fijado, ejecutar el lector con los ZIP locales `frontera112.zip` y `frontera160.zip` y el CMS autenticado de τ160. La salida debe ser un directorio nuevo fuera del repositorio.

```bash
python3 -B checkpoints/CP12/p4_20261115/prueba_pasiva/prueba_pasiva.py \
  --archivos /ruta/respaldos --cifrado /ruta/frontera160.cms --salida /ruta/prueba-p4
```

[Prerregistro](../checkpoints/CP12/p4_20261115/prueba_pasiva/PRERREGISTRO.md) · [Código](../checkpoints/CP12/p4_20261115/prueba_pasiva/prueba_pasiva.py) · [Resultados agregados](../checkpoints/CP12/p4_20261115/prueba_pasiva/RESULTADOS_AGREGADOS.json) · [Recibo](../checkpoints/CP12/p4_20261115/prueba_pasiva/RECIBO.json)
