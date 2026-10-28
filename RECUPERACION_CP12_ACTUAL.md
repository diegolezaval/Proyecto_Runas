# CP12: recuperación vigente

**Detenido por infraestructura. La repetición adicional τ9,6→τ11,2 está autorizada y sigue sin utilizarse.** No se ha iniciado un nuevo cálculo. La autorización y las puertas están en el [intento02](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/PRERREGISTRO.md).

| Referencia | Estado comprobado |
| --- | --- |
| Checkpoint aceptado | CP11 |
| Investigación CP12 / P3 | Abierta / sin validar |
| Última frontera completa aprobada del ensayo | τ8 |
| Último transporte permanente recuperable | τ9,6 |
| Recuperación canónica nueva | 30 controles de τ8 + 14 de τ9,6; cero construcciones o pasos DOP853 |
| Repetición adicional autorizada | Sin asignar; cero pasos nuevos |

## Qué impide continuar

- **Publicación local desde el proceso:** el usuario informó que completó la activación oficial de GitHub CLI; la conexión no quedó guardada y la sesión de ejecución devolvió un bloqueo de red del entorno hacia `api.github.com`. No se infiere que GitHub rechazara al usuario. [Observación](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/infraestructura/CONEXION_LOCAL.json).
- **Ejecutor probado en GitHub Actions:** el único diagnóstico nuevo observó Haswell; el proyecto exige SkylakeX sin forzar el dispatch. Se detuvo antes de usar M2. Se recuperó el artefacto original y se verificó su SHA-256. [Resultado original](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/infraestructura/DISPATCH_REMOTO_ORIGINAL.json) · [Comprobación de descarga](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/infraestructura/RECUPERACION_ARTEFACTO_REMOTO.json) · [Ejecución](https://github.com/diegolezaval/Proyecto_Runas/actions/runs/40765474986).

La [auditoría canónica](checkpoints/CP12/p3_20261018/retoma_20261028/intento02/auditoria_canonica/RESULTADO.json) confirma otra vez el ZIP original, sus 283 cargas y la rehidratación sin pasos, usando los bytes exactos del auditor registrado. La cápsula local nueva de capacidad es un prototipo administrativo sin publicar; deberá reconstruirse con los adaptadores de identidad exacta antes de la prueba directa. No acredita todavía conservación automática.

## Siguiente puerta

Hace falta un ejecutor que mantenga el entorno original y disponga de publicación operativa desde el mismo proceso. Después debe pasar la prueba completa de cápsula, subida, descarga, hashes y rehidratación independiente sin pasos. Sólo entonces se registrarán el nuevo lanzador acotado y su asignación exclusiva, antes de usar la autorización adicional existente. El diagnóstico de infraestructura no autoriza reasignaciones repetidas ni cambios de arquitectura o umbrales.

## Historia que se conserva

La primera repetición excepcional terminó y dejó [resultados y auditorías](checkpoints/CP12/p3_20261018/retoma_20261028/repeticion96_112/RESULTADO.json) en GitHub. Sus bytes nuevos desaparecieron antes de una publicación observada. El [incidente](checkpoints/CP12/p3_20261018/retoma_20261028/INCIDENTE_SEGUNDA_PERDIDA_LOCAL.json) distingue lo observado de las causas no identificadas. Su excepción sigue consumida y su lanzador bloqueado.

Los [tres ZIP originales y la prueba anterior de capacidad](https://github.com/diegolezaval/Proyecto_Runas/releases/tag/respaldo-cp12-p3-20261027) permanecen íntegros. P2 no se reanuda; no repetir CP10, CP12 original, F0…F5 ni P3 τ0→τ9,6. La transferencia histórica 116/308 permanece incompleta.

[Registro de reanudación](checkpoints/CP12/p3_20261018/ESTADO_REANUDACION.json) · [Expediente](checkpoints/CP12/p3_20261018/retoma_20261028/README.md).
