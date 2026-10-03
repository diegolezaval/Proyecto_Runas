# Instantánea de entrada de la auditoría CP09

Conserva los bytes exactos de los quince archivos originales de CP08 que se sustituyeron o editaron en esta auditoría, incluido su manifiesto. No es una carpeta de trabajo independiente ni contiene por sí sola todos los datos.

El inventario completo de los 786 archivos originales y hashes está en trazabilidad/arquitectura/archivos_CP08.json. Para reconstruir CP08, tomar cada archivo actual con el mismo hash, o su copia de esta instantánea si cambió. La regresión estructural realiza esa reconstrucción en una copia temporal y verifica el manifiesto original.

Los documentos copiados conservan el contexto de sus rutas originales. La función de resolución está declarada en datos/arquitectura.json. Los scripts copiados son antecedentes y no deben ejecutarse como herramientas vigentes.
