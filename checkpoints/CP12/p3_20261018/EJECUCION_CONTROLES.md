# Reproducción de los controles nuevos P3

Propuesta registrada en `538ef767aee6134cdaa4ab3673d183b63bce80bb`. Estos archivos implementan el candidato y sus controles **después** del registro. `REGISTRO_CODIGO.json` fija sus hashes antes de ejecutarlos. Las fuentes P2 y las 14 fuentes científicas históricas no se editan. Sólo se ha analizado la sintaxis; no se ha ejecutado aún F0…F4 ni M2.

Recuperar primero la cápsula diagnóstica histórica, autenticar ZIP/manifiesto/cargas y extraer su manifiesto original sin modificarlo. Los argumentos siguientes apuntan a esa extracción y a ese manifiesto externo. Cada salida debe ser un directorio nuevo. Ejecutar secuencialmente F0_structure, F1_action, F2_defect, F3_matrix, F4_frozen; detener al primer código distinto de cero. Cada lector verifica entradas y fuentes, bloquea DOP853 y escribe RESULTADO.json incluso si encuentra una excepción. Conservar también stdout y stderr.

```bash
python3 checkpoints/CP12/p3_20261018/control_F0_structure.py \
  --inputs /ruta/a/extraccion \
  --manifest /ruta/a/MANIFIESTO_DIAGNOSTICO_NEGATIVO_ORIGINAL.json \
  --output /ruta/nueva/a/F0
```

Las otras cuatro fases usan los mismos tres argumentos. No reutilizar directorios de salida ni sobrescribir un negativo. Los archivos de control adaptan los métodos de paso complejo, referencia polinómica extendida y referencias congeladas originales al **operador nuevo**, con semilla distinta fijada y el tercer fondo mixto80. El conjunto positivo debe conservarse, recuperarse y certificarse antes de preparar un nuevo piloto. No cambia ninguna puerta ni autoriza todavía pasos físicos.
