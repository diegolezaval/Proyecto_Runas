# Entrega CP08

Descargar los dos archivos complementarios:

- `Proyecto_Runas_M2_4_2_CP08_PROYECTO.zip`: código, informes, tratado, resultados, trazabilidad, estados de preparación y evolución no radial.
- `Proyecto_Runas_M2_4_2_CP08_ESTADOS_ACCESO.zip`: estados completos NPZ de acceso lineal y colocación, incluidos los intentos fallidos.

Extraer ambos en **la misma carpeta**. Los dos contienen la raíz `Proyecto_Runas/`; sus archivos se complementan sin sobrescribir nombres. La división sólo facilita la entrega, no elimina estados ni resultados.

Leer primero [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md) y el [informe CP08](informes/ENTREGA_08_REFINAMIENTO_NO_RADIAL.md). No hay simulaciones en curso en este checkpoint.

Con Python disponible, comprobar la unión completa sin ejecutar física:

```bash
cd Proyecto_Runas
python herramientas/checkpoint.py --verificar
```

`MANIFIESTO_SHA256.json` cubre la unión de ambos ZIP. Se excluyen únicamente cachés de ejecución, bloqueos y bytecode; las fuentes de la aceleración opcional en C están incluidas. El integrador también admite fuerza NumPy sin compilador. No ejecutar la reproducción histórica para continuar la hoja de ruta.
