# Continuidad recuperada, entorno y capacidad de P3

Entrega del 4 de noviembre de 2026. **CP11 aceptado; CP12 abierto; P3 sin
validar.** Frontera completa positiva τ8, transporte íntegro τ11,2 y siguiente
frontera τ16. Esta entrega no ejecuta pasos nuevos de M2.

## Pregunta y protocolo previo

¿Puede recuperarse la preparación interrumpida y conservar el estado exacto
desde el ejecutor que continuará hacia τ16, antes de activarlo?
Rigen el [prerregistro original](../checkpoints/CP12/p3_20261018/PRERREGISTRO_PILOTO.md)
y el [registro del ejecutor](../checkpoints/CP12/p3_20261018/continuidad_20261030/ejecutor/REGISTRO.json),
publicado antes de esta ejecución. No se repite τ9,6→11,2, F0…F5, CP04 ni
ninguna trayectoria cerrada. Las fuentes científicas, puertas y observadores
originales mantienen su autoridad.

## Recuperación de la preparación y árbol global

Al retomar, el espacio temporal anterior ya no estaba disponible. La causa
no está determinada. Los heads seguían en `4a88af2` para P3, `4aa5562` para
la preparación y `90e8fcf` para main; la Release conservaba ocho adjuntos.
No había evidencia publicada de una frontera posterior a τ11,2.

Sí seguía disponible el árbol Git completo `bdff910e327b57a08f692cdb9fde93d9be4a2fe6`,
contrastado el 30 de octubre. Se ancló sin reconstruir sus archivos en el
commit [`4f58c46`](https://github.com/diegolezaval/Proyecto_Runas/commit/4f58c467ff886834a7141eee64ce52bcba4a4a7b).
Tras recuperarlo por Git se verificó su manifiesto, se regeneró el ZIP y se
extrajeron sus **2593 archivos** por separado: todos coinciden con los blobs
de ese commit. P3 avanzó a ese commit administrativo; main conserva CP11.

El paquete regenerado tiene exactamente **305122086 bytes** y SHA256
`4f189892b4e4502e73700f6b76fe0f35178298ee1b6ca82a82113638f154ca45`,
idénticos a los observados el 30 de octubre. Esta identidad sí está
comprobada; no se atribuye al ZIP perdido del 29 de octubre.
[Recuperación independiente](../trazabilidad/continuidad_20261104/RECUPERACION_GLOBAL_LOCAL.json).
No se ha acreditado todavía su recuperación desde un adjunto Release.
La entrega posterior con este informe genera su propio manifiesto y paquete.

## Rechazo del entorno y recuperación del compilador

La primera ejecución del auditor original se detuvo en la comparación exacta
del entorno, antes de DOP853. El compilador disponible era Debian14.2;
el registro exige `cc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0`.
Se conservan el [rechazo](../trazabilidad/continuidad_20261104/fallo_entorno/RESULTADO.json)+y la [diferencia completa](../trazabilidad/continuidad_20261104/DIFERENCIA_ENTORNO.json).
Es un bloqueo administrativo de compatibilidad, sin negativo científico nuevo.

Se localizaron los binarios oficiales de la versión exacta en Launchpad,
se contrastaron tamaños y SHA256 con los registros de publicación y el
archivo `.changes`, y se extrajeron en un prefijo privado. Se usa el
ejecutable real, sin sustituir la respuesta de versión ni modificar el
auditor. El compilador del sistema no se reemplaza.
[Identidad recuperada](../trazabilidad/continuidad_20261104/RESTAURACION_COMPILADOR.json).

El [recuperador reproducible](../herramientas/restaurar_compilador_p3.py)
reconstruye ese prefijo y verifica los tres paquetes y el ejecutable;
su [recibo](../trazabilidad/continuidad_20261104/REPRODUCCION_COMPILADOR.json)
no certifica por sí solo la física. El host actual sigue siendo Debian13:
se ha recuperado la huella numérica exigida por el protocolo, no una imagen
idéntica de todo el sistema operativo anterior.

En una extracción nueva del adjunto original **688783601**, el auditor
original sin modificar pasó **30 controles de frontera τ8 y 14 de transporte
τ11,2**, con cero construcciones o pasos DOP853. Las 293 cargas originales
se verificaron antes y después; ZIP, configuración, recibo y NPZ permanecen
idénticos. [Auditoría](../trazabilidad/continuidad_20261104/auditoria_compatible/RESULTADO.json).

## Conservación desde el proceso real

El ejecutor publicado restauró toda la memoria interna y pasiva, con el
límite interno original16. [Restauración exacta](../checkpoints/CP12/p3_20261018/continuidad_20261104/RESTAURACION_EXACTA.json).
Se observó una única sesión propia y ambos bloqueos de instancia/registro
retenidos. Los PID de llamadas de herramienta distintas pertenecen a
espacios de procesos distintos; la observación usa la sesión y los bloqueos,
sin inferir terminación de ejecutores históricos inaccesibles.
[Actividad observada](../checkpoints/CP12/p3_20261018/continuidad_20261104/ACTIVIDAD.json).

Desde ese mismo proceso se guardó y recuperó la cápsula de capacidad:

| Campo | Resultado |
| --- | --- |
| Nombre | `CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_CONTROL_P3_112_A16_20261030.zip` |
| Tamaño | 230966017 bytes, mayor que la cápsula original |
| SHA256 | `a480ddb695f861274d8eb6d3e6199324cd10ca8eb72c418467ac56af38956308` |
| Cargas | 303 más manifiesto, cobertura exacta |
| Recuperación nativa independiente | Positiva; hashes antes/después y 44 controles originales |
| Identidad durable | `libfile_14734b00b48c81918ac7f0587217daf2` |
| Nuevos pasos M2 | 0 |
| Publicación/recuperación de esta capacidad en GitHub | Pendiente |

El nombre conserva la asignación registrada el 30 de octubre; la operación
real ocurrió el 4 de noviembre. Las diez cargas adicionales son administrativas
y de capacidad; no son estados físicos nuevos. Los identificadores se
guardaron inmediatamente después de confirmar la escritura.
[Solicitud](../checkpoints/CP12/p3_20261018/continuidad_20261104/capacidad/SOLICITUD.json)+y [recibo de recuperación](../checkpoints/CP12/p3_20261018/continuidad_20261104/capacidad/RESULTADO_TRANSITO.json).

## Puerta pendiente y siguiente acción

La capacidad combinada aún no está aceptada. La sesión del navegador muestra
el inicio de sesión de GitHub al abrir la edición de la Release. Las
herramientas conectadas permiten publicar árboles, commits y referencias,
pero no adjuntos binarios de Releases. Se requiere autenticación en esa
sesión para adjuntar los paquetes ya preparados.

El trabajador permanece en espera administrativa del adjunto, sin archivo de
activación ni recibo de inicio físico. Su espera tiene un límite de una hora.
Después de autenticar: comprobar adjuntos existentes para evitar duplicados,
subir los bytes exactos, descargarlos por separado y aplicar otra vez los
auditores originales. Sólo tras publicar el recibo combinado y la reserva
del único trabajador se puede escribir la activación ligada por hash y
continuar desde τ11,2 hacia16.

Si la sesión de ejecución expiró, comprobarlo y reconciliar los recibos antes
de preparar otro proceso. La escritura nativa de esta capacidad está
confirmada: no debe repetirse por incertidumbre. No se reconstruye el permiso
consumido τ9,6→11,2. El control de capacidad permite conservar; no demuestra
convergencia ni cierra CP12. En16 siguen pendientes la recuperación y las cinco
métricas originales, ambos balances energéticos y todas las demás puertas.

Los negativos P2τ80 y CP12 original permanecen; el histórico116/308 sigue
incompleto. Las33 etapas y las exclusiones de Canal mantienen sus registros;
ningún dispositivo completo se acepta y M3 no se activa. Tras las puertas
realmente habilitadas de P3, la finalidad sigue siendo estabilidad,
preparación, acceso finito, retroacción, receptor, retención y ciclo.

## Verificación administrativa de la entrega

La [regresión estructural actual](../trazabilidad/continuidad_20261104/REGRESION_FINAL.json)
pasó sus16 controles y23 comandos sobre datos guardados, sin campañas ni
cambios en los CSV/NPZ o en el corpus de entrada. La verificación editorial
también pasó. Las33 etapas y el registro de dispositivos coinciden exactamente
con el commit de entrada. Se corrigió un campo administrativo `report` ausente
en la nueva entrada del historial antes de regenerar las vistas; no afectó
a fuentes, resultados ni procesos científicos.

Los recibos de ZIP y del commit posterior identifican el cierre de conservación
de esta entrega; no se insertan hashes autorreferentes dentro del paquete.
