# Capacidad separada al recuperar un transporte nativo

La asignación nueva restaura el transporte desde la Biblioteca y ejecuta su propia prueba de escritura y recuperación nativas con el estado interno exacto. Esa cápsula queda en el mismo destino. No entra en la rotación de transportes periódicos.

El mismo proceso prueba la publicación con una cápsula de tamaño real derivada de la última frontera completa ya pública. El registro fija el adjunto, nombre, tamaño y SHA256 de la referencia. La cápsula de prueba contiene exclusivamente sus cargas byte a byte, su inventario anterior, el inventario derivado y el relleno determinista de capacidad. El comparador verifica esas categorías antes de la subida. La descarga independiente desde el adjunto nuevo usa el auditor original de frontera con cero evolución.

La aceptación conjunta vincula el registro, el transporte nativo y la prueba pública. Ambos ciclos son nuevos y preceden a la reserva y a la activación. Si cualquiera falla, los transportes verificados previos se conservan y la asignación queda sin activar. La referencia pública acredita capacidad de conservación. La frontera científica y el reloj de reinicio se acreditan en sus propios recibos.

La adaptación se aplica sólo a nuevas asignaciones desde un transporte híbrido. Las fuentes del ejecutor histórico se conservan con sus hashes. El adaptador reutiliza restauración, activación, métricas, preservador y auditores. La evolución y las puertas desde la activación son idénticas. Se mantienen el diario de rotación, las frecuencias y todas las suspensiones. [Enmienda híbrida](ENMIENDA.md) · [Prueba acotada](CONTROLES_CAPACIDAD_SEPARADA.json).
