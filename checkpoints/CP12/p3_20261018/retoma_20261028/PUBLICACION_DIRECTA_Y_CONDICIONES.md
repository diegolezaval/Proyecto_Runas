# Publicación directa y condiciones antes de otro intento

**No autoriza M2 ni otra repetición.** La excepción única τ9,6→τ11,2 ya se consumió. El [incidente](INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json) y los resultados anteriores permanecen conservados. La entrada anterior del lanzador se bloqueó para que una carpeta temporal nueva no permita reutilizar la reserva.

## Cambio concreto preparado

`publicar_desde_proceso.py` utiliza GitHub CLI para subir la cápsula desde el proceso que conserva los resultados y llama inmediatamente al adaptador registrado `conservar_release.py aceptar`. El ciclo completo no necesita que otro turno del chat seleccione un archivo en el navegador:

1. Verificar archivo local contra su solicitud, repositorio exacto y Release experimental.
2. Publicar el adjunto sin `--clobber`. Un nombre existente con otros bytes se rechaza; un adjunto idéntico puede reutilizarse.
3. Comprobar tamaño y SHA-256 informados por GitHub, además de que el ZIP fuente siga idéntico.
4. Descargar públicamente en otra carpeta, verificar cada miembro, extraer y ejecutar los auditores originales sin pasos.
5. Emitir `ACEPTACION_DIRECTA.json` sólo si todas las comprobaciones pasan. Esta aceptación es de conservación, no de aceptación científica ni permiso de repetición.

La implementación y sus [ocho controles](CONTROLES_PUBLICACION_DIRECTA.json) están preparados. Los controles usan datos sintéticos, sin red ni M2: no sustituyen la prueba real de subida y recuperación autenticada, que sigue pendiente. El [preflight real](PREFLIGHT_PUBLICACION_DIRECTA.json) confirma GitHub CLI instalado y autenticación aún ausente.

## Acceso y prueba real pendientes

El acceso existente mediante la integración del chat no acredita autenticación del proceso independiente. Antes de usar este método hay que configurar su acceso por un flujo seguro y verificarlo. El programa no extrae ni registra tokens. Las credenciales y la configuración de GitHub CLI deben permanecer fuera de la raíz científica, sus inventarios y los ZIP.

La documentación oficial de [autenticación](https://cli.github.com/manual/gh_auth_login) describe el flujo web y el uso de credenciales de automatización. Un acceso limitado a `diegolezaval/Proyecto_Runas`, con escritura de contenidos necesaria para adjuntos Release y duración limitada, es preferible cuando pueda configurarse. La autorización web estándar de GitHub CLI solicita los permisos de su aplicación; no se ha iniciado ni concedido aquí. No se deben ampliar permisos ni crear credenciales sin la intervención requerida del usuario.

Después de autenticar, la prueba real debe conservar una cápsula τ9,6 con tamaño superior a 229848115 bytes mediante **este publicador directo**, descargarla y auditarla sin pasos. Se conservarán solicitud, metadatos, hashes y aceptación. El preflight de autenticación por sí solo no habilita ninguna evolución.

## Condiciones para solicitar una nueva excepción

- Buscar y recuperar primero cualquier copia íntegra nueva τ11,2 que aparezca. Sus metadatos conservados no reconstruyen el estado.
- Completar la prueba real de publicación directa sin M2.
- Obtener una excepción explícita adicional para repetir exclusivamente τ9,6→τ11,2; la autorización anterior era de una sola vez.
- Registrar un nuevo identificador de intento y una asignación durable antes de M2. Si se pierde el ejecutor, no usar la ausencia de un marcador local como permiso de repetición.
- Mantener intactos fuentes científicas, entorno, puertas, memoria DOP853 y datos de Cauchy. Usar el intervalo original con límite interno τ16 y detener el reloj observador en τ11,2.
- El nuevo proceso deberá invocar la publicación y verificación directamente al alcanzar la parada. No declararlo terminado o reanudable por una aceptación local o por la sola presencia del adjunto.

La prueba de capacidad anterior sigue siendo válida para su alcance. El incidente mostró una limitación operacional adicional: entre producir un archivo local y la siguiente acción del chat podía interrumpirse la conservación. El nuevo código busca eliminar esa dependencia; la supervivencia ante una pérdida completa del ejecutor no se presume sin prueba.

## Comandos de comprobación

Desde esta carpeta, con una instalación autorizada de GitHub CLI disponible:

```bash
python publicar_desde_proceso.py --preflight
python publicar_desde_proceso.py --solicitud /ruta/SOLICITUD.json --salida /ruta/nueva/recuperacion
```

La formación de cápsula y sus auditorías locales se hacen con el adaptador registrado. El publicador verifica también el hash de ese adaptador antes de aceptarlo. Los comandos de esta sección conservan archivos; no inician física.

Referencias de implementación: [subida de adjuntos](https://cli.github.com/manual/gh_release_upload), [autenticación](https://cli.github.com/manual/gh_auth_login). El archivo GitHub CLI se obtuvo de la publicación oficial y sus checksums se comprobaron; se conserva el [comprobante de instalación](GITHUB_CLI_VERIFICADO.json).
