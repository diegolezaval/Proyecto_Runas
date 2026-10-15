# Copias temporales verificadas

Los internos completos de DOP853 producen respaldos grandes. El supervisor externo `limpiar_copias_temporales.py` mantiene las dos recuperaciones temporales más recientes de cada clase (transporte y frontera científica), además de τ0, todos los negativos, comprobantes y fuentes. Sólo retira duplicados de trabajo después de que el archivo completo haya sido guardado permanentemente, recuperado, verificado y auditado independientemente. Comprueba nombres, raíces, tamaños y SHA256 antes de retirar las copias locales.

No elimina archivos conservados permanentemente ni su historial. No toca estados de producción, integradores, observadores, criterios o código en ejecución. Cualquier archivo desconocido queda intacto. Cada retirada deja un registro local con el identificador del archivo íntegro y su SHA256 para recuperarlo. Esto limita el uso temporal de disco sin perder evidencia científica.
