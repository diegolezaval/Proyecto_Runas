# Entrega 11 · Diagnóstico radial de χ

Esta unidad continúa el pendiente científico de CP10 en
`ciencia/cp11-diagnostico-chi`, desde `origin/main`/CP10
`47b5e56cf3fd9f90b865ad2ddcaa313c2b43fa81`. No repite evoluciones cerradas
ni prepara de nuevo CP04. El modelo M2, Θ y las puertas permanecen intactos.

## Resultado y decisión

La explicación basada en un cruce artificial del umbral por spline o
normalización queda descartada dentro de los controles declarados. El
operador coincide con la acción de volúmenes finitos, es simétrico en su
peso y tiene forma positiva. Su autobase muestra que la diferencia espacial
se concentra en las componentes cortas del mediador. La propagación libre
inicial y la corrección modal del residuo congelado no bastan como
explicaciones suficientes. El negativo de esa corrección conserva su
criterio y sus datos; no se ensayan fases ajustadas.

La respuesta forzada recuperada de los extremos domina la diferencia.
Separar dentro de ella el defecto radial y la fuente no lineal requiere
la historia temporal que no está en los estados existentes. Se cierra
esta unidad con diagnóstico causal limitado y se detiene antes de una
nueva campaña. No se convierte incertidumbre en agotamiento de M2 ni
un fallo numérico en inestabilidad física.

Las cifras, tablas, límites y recibos se generan desde las autoridades
numéricas en [RESUMEN_NUMERICO_CP11.md](RESUMEN_NUMERICO_CP11.md).
Las derivaciones están en [el capítulo 31](../tratado/31_diagnostico_radial_del_mediador.md).
La puerta original del 2 % conserva el resultado negativo CP10:
REFINAMIENTO_PENDIENTE. E03/E04/RES0/RES1 siguen PARCIALES.

## Ejecuciones y fallo conservado

Los análisis usan exclusivamente el sistema de procedencia CP10 y
prerregistros enlazados por [el registro](../datos/registro_calculos.json).
Los diagnósticos no crean estados M2 y no ejecutan pasos de integración.
Se capturan código, parámetros, configuraciones, entorno y hashes antes
de cada ejecución, con los pools BLAS observados de un hilo.

El primer control doble de la identidad de defecto FALLÓ por pérdida
de precisión al restar fuerzas iniciales casi iguales. Se conserva íntegro
con sus salidas, traceback, código y recibo; no se utiliza como resultado
aceptado. La [enmienda](ENMIENDA_CP11_PRECISION_DEFECTO.md) prerregistra una
referencia longdouble de las mismas ecuaciones y coeficientes. Pasa sin
cambiar las tolerancias ni la puerta científica. No se borra el intento.

## Conservación y migración

Los 938 archivos autoritativos CP10 se identifican por los hashes de
`trazabilidad/CP10_entrada/archivos_sha256.json`. Cada fuente o vista CP10
actualizada conserva su versión exacta en esa instantánea. Ningún estado,
resultado numérico anterior, fallo, figura histórica, capítulo anterior o
hoja de ruta original se mueve, renombra o elimina. El código de evolución
y la autoridad Θ mantienen sus hashes. No hay una reorganización general
ni LFS nuevo.

**Mapa de movimientos/renombrados:** vacío. Las adiciones de evidencia y
las actualizaciones compatibles de autoridades se registran en
`trazabilidad/CP11/cambios_y_conservacion.json`; el diff Git muestra cada
ruta. Las instantáneas no son nuevas fuentes de verdad científica.

## Verificar y reproducir

```bash
python herramientas/checkpoint.py --verificar
python herramientas/verificar_entorno.py --cp10
python herramientas/generar_continuidad.py --comprobar
python herramientas/generar_resumen_CP11.py --comprobar
python herramientas/verificar_CP10.py
python herramientas/verificar_CP11.py
python herramientas/regresion_estructural.py --salida ../regresion_CP11.json
```

El prerregistro de verificación permite reproducir los tres diagnósticos
válidos en temporales, conservando el fallo declarado y comprobando sus
hashes. El recibo se escribe antes de reproducir; ningún resultado fuente
se sobrescribe. La reproducción de publicación puede guardarse fuera del
clon mediante la opción explícita del verificador para mantener limpio el
payload del checkpoint. Consultar la entrada [LEEME.md](../LEEME.md).

El entorno de referencia de CP10 tiene OpenBLAS SkylakeX/AVX512 y un hilo;
sus controles exactos de datos iniciales pueden diferir a redondeo en otro
backend/CPU. CP11 no relaja esa comprobación ni publica un CI genérico
como si equivaliera al entorno de referencia. La referencia extendida
requiere longdouble más preciso que float64. Las bibliotecas permanecen
fijadas en requirements.txt.

## Entrega y siguiente condición

El checkpoint completo incluye los estados, negativos, historia,
prerregistros, recibos, autoridades y vistas. `main` se actualiza sólo
mediante PR verificado y conserva su protección. El tag/Release CP11 se
publica después de comprobar el clon; CP10 no se modifica.

La siguiente decisión científica es formular evidencia discriminante
para los dos términos de la identidad de defecto, con coste y cobertura
justificados y sin repetir las catorce evoluciones cerradas. No hay una
simulación siguiente autorizada por inercia. No se abre otro modelo ni
se inicia CP12 durante esta entrega.
