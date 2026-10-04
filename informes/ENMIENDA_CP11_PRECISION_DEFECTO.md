# Enmienda de implementación · CP11 · Referencia aritmética del defecto

El recibo `respuesta_forzada__9360199db9cdc238ab2e4c8d75512db5f81d85a225088ad27f8ab8e67d9b0817`
permanece FALLIDA e íntegro. El residuo relativo de la identidad inicial
fue 1.31e−9, frente a la tolerancia prerregistrada de 2e−12. No se
promueven sus decisiones parciales como evidencia aceptada.

La identidad contiene diferencias de fuerzas que son casi cancelaciones
entre términos M²χ y gρ. Evaluar por separado esos términos en doble
precisión introduce redondeo antes de restar diferencias pequeñas. Éste
es un defecto de la implementación del CONTROL, no de la fuerza ni una
inestabilidad de M2. Se contrasta con una referencia aritmética extendida.

Antes de ejecutarla se fija:

- mismas ecuaciones, coeficientes almacenados, estados y spline cúbico;
- matriz del spline calculada una vez: I permanece un operador lineal fijo;
- evaluación de flujo, término centrífugo y potencial en `numpy.longdouble`;
- comprobación de equivalencia del mapa I con el spline anterior;
- la misma tolerancia algebraica 2e−12 y de cierre 2e−11;
- mismos momentos de Duhamel, normalización y puerta física original 2 %;
- recibo nuevo, sin sustituir el intento previo ni reanudarlo;
- si tampoco pasa, detener la inferencia y conservar la limitación.

Se exige que longdouble tenga mayor precisión que float64; su precisión
real se registra. No se incorpora una dependencia ni un parámetro físico.
El contrato nuevo es `datos/ensayo_respuesta_forzada_precisa_CP11.json` y el
trabajador es `herramientas/respuesta_forzada_chi_CP11_precisa.py`.
La corrección tiene una justificación aritmética independiente; no es
otra variante física o de fase escogida para aprobar el ensayo.
