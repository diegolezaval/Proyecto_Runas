# Primera descarga de la Reserva

La primera descarga **cierra esta misión en el paso 3**. En las tres discretizaciones, el núcleo de la receptora perdió más energía y carga con la donante cargada que con cada control. Ninguno de los cuatro contrastes alcanzó la ganancia positiva exigida. El resultado se refiere a la señal calibrada, la separación de 120 y la lectura entre 200 y 240 unidades de tiempo después del disparo. [Diseño de la descarga](DISENO_DESCARGA.md) · [Prerregistro del ciclo](PRERREGISTRO.md)

## Qué cambió en la receptora

La tabla da el cambio medio de inventario del núcleo de radio 40 respecto a su propio valor inicial, en la malla principal con paso espacial interior 0,30 y paso temporal 0,005. Todas las cifras de las dos tablas están en millonésimas de las unidades normalizadas de M2.

| Montaje | Cambio de energía | Cambio de carga |
|---|---:|---:|
| Donante cargada y señal encendida | −749,434 | −492,200 |
| Donante gemela sin carga adicional y misma señal | −576,422 | −439,722 |
| Señal directa sin donante | −582,635 | −444,149 |

Para calcular la entrega adicional se restó el cambio de cada control al de la donante cargada. La incertidumbre numérica U es la mayor variación observada al cambiar el paso espacial, el paso temporal o la mitad de la ventana de lectura. El criterio exige D > 3U y D > 0 en los cuatro contrastes.

| Control de referencia | Magnitud | Diferencia D | Incertidumbre U | D/U |
|---|---|---:|---:|---:|
| Gemela sin carga adicional | Energía | −173,012 | 3,593 | −48,16 |
| Gemela sin carga adicional | Carga | −52,478 | 0,189 | −278,00 |
| Transmisión directa | Energía | −166,799 | 17,157 | −9,72 |
| Transmisión directa | Carga | −48,052 | 10,430 | −4,61 |

El cambio de malla espacial fijó U en los cuatro casos. Incluso el contraste más próximo a cero, la carga frente a transmisión directa, mantiene el signo negativo al sumar 3U. La prueba fija el saldo de inventario en esa ventana. La atribución causal al disparo requería superar primero los cuatro contrastes. [Medias, ventanas y variaciones sin redondear](RESULTADO_DESCARGA.json)

## Preparación y balances

Se recuperaron los seis campos radiales de la donante y de su gemela en τ300, y los de la receptora preparada en el paso 2. La retención fina previamente medida fue de 96,90 % en energía adicional y 97,41 % en carga adicional. Se conservó la amplitud calibrada A = 0,0035912196276076985. Las nueve trayectorias tienen 241 muestras cada una y guardan los tres campos y sus tres velocidades en s = 240. Al volver a medir esos estados, los ocho inventarios finales coincidieron con el último renglón de cada serie. [Retención](RETENCION.json) · [Calibración](calibracion/CALIBRACION.json) · [Tamaños y SHA-256](MANIFIESTO_DESCARGA.json)

En la malla principal, el trabajo neto de la señal fue 1,79269 × 10⁻⁵ en la donante cargada, 1,79255 × 10⁻⁵ en la gemela y 2,80 × 10⁻¹⁸ en transmisión directa. Los máximos residuos globales entre las tres trayectorias finas fueron 1,33 × 10⁻⁶ en energía, redondeado hacia arriba tras descontar el trabajo, y 1,13 × 10⁻¹⁰ en carga.

Al proyectar la receptora aislada de la malla radial a la cilíndrica fina, el inventario inicial de su núcleo cambió en +0,280701 de energía y +0,388191 de carga. Además, las colas de la donante cargada ya aportaban al inventario inicial de la receptora, respecto al montaje con gemela, +0,000198087 de energía y +0,000077933 de carga. Las restas de la primera tabla parten del inventario propio de cada montaje en s = 0. Los residuos y el cambio inicial de malla se informan por separado de U. [Inventarios iniciales, proyecciones aisladas y residuos](RESULTADO_DESCARGA.json)

## Decisión y recuperación

El protocolo detiene aquí esta misión. El control con señal apagada, la recarga, la segunda descarga y el ensayo de interrupción quedan sin habilitar. La retención demostrada hasta τ300 se conserva como resultado de la fase anterior.

Para recuperar los campos finales, descarga el [ZIP con los nueve estados en s = 240](https://github.com/diegolezaval/Proyecto_Runas/releases/download/reserva-primera-descarga-s240-20261121/Reserva_primera_descarga_9_estados_s240.zip) y extráelo en este directorio. Cada archivo quedará junto a su `serie.csv` en `primera_descarga/<malla>/<rama>/`. El [recibo de verificación](RECIBO_GUARDADO_DESCARGA.json) recoge los tamaños y los SHA-256 comprobados al descargar el ZIP desde GitHub.

Desde este directorio se pueden reconstruir las tablas, comprobar los campos finales y medir de nuevo la proyección sin pasos de integración M2. Se requiere Python con NumPy 2, SciPy y un compilador C.

```sh
OPENBLAS_NUM_THREADS=1 python balances_descarga.py primera_descarga /tmp/resultado_descarga.json
```
