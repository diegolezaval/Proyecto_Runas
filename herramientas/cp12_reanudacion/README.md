# Reanudar CP12/P3

El comando coordina la retoma híbrida de CP12/P3 desde una frontera cerrada o un
transporte exacto con su asignación publicada. El tramo de referencia es τ28,8 → τ32.

## Uso

Prepara el checkout con Python, Git y las dependencias registradas en
`requirements.txt`.

```bash
git fetch origin administracion/cp12-reanudacion
git switch --track origin/administracion/cp12-reanudacion
```

Usa la sección de inventario automático para ejecutar desde una sesión de Work.

- **`verificar`** consulta el HEAD científico y sus recibos, compara las identidades
  persistentes, recupera los archivos necesarios, comprueba el entorno y ejecuta
  los auditores originales y `--solo-auditar`. Hace cero pasos de M2. Con
  `--historial SHA` puede comprobar un expediente publicado de sólo lectura.
- **`retomar`** usa el mismo directorio privado y persistente. Coordina una
  asignación publicada, con intención exclusiva en Git antes de arrancar el
  trabajador. Recupera la capacidad propia, la reserva y la activación en orden.
  Entrega los bytes de la activación al proceso dueño de ambos locks y registra el
  primer paso físico aceptado. El ejecutor original continúa el tramo hasta su puerta.
- Las escrituras operativas de `retomar` necesitan Git autenticado para la rama
  científica. La publicación nueva de un control público preparado por el comando
  exige aprobación del SHA256 exacto, con `--aprobar-publicacion SHA256` y
  `gh` autenticado. Otra vía es publicar el archivo autorizado externamente y
  repetir el comando para que recupere el adjunto exacto. Se comprueban nombre,
  destino, tamaño, huella e identidad del adjunto. Una subida incierta exige
  reconciliación antes de otra escritura.

El directorio `--helpers` contiene `library_file_transfer.py`,
`library_hosted_apps.py` y `library_upload.py` con las huellas del
`REGISTRO.json` de la asignación. La capacidad nativa necesita acceso de
escritura y recuperación desde el proceso que ejecuta el tramo. En un entorno con
acceso de lectura a Biblioteca, el comando materializa el origen por sus dos IDs.
Si el acceso de lectura requiere intervención, admite el ZIP exacto ya recuperado
con `--archivo /ruta/al/archivo.zip`.

El compilador registrado se reutiliza si coinciden su versión y SHA256. Si hace
falta, se descarga el adjunto público registrado y se ejecuta el restaurador
original en un prefijo privado. Los auditores conservan sus comprobaciones de
Python, SciPy, BLAS, configuración, fuentes y estado.

### Inventario automático en ChatGPT Work

`inventario_work.js` ejecuta el reanudador con
`--comando-inventario herramientas/inventario_cp12.py`. Cada consulta pide a
Biblioteca su listado activo y sigue los cursores hasta terminar. Entrega sólo
las identidades de CP12/P3. Una página incompleta, un cursor repetido o una
identidad ambigua cierran la puerta de inventario. La siguiente consulta
vuelve a listar desde el origen.

En una sesión de Work con acceso a la Biblioteca del proyecto, ejecuta el
siguiente bloque en el runtime de herramientas desde un checkout de esta rama.
Usa la ruta absoluta del repositorio y el directorio de trabajo persistente.
Para una retoma autorizada, cambia `verificar` por `retomar`.

```javascript
const repositorio = "/ruta/absoluta/Proyecto_Runas";
const programa = await tools.exec_command({
    cmd: "cat herramientas/cp12_reanudacion/inventario_work.js",
    workdir: repositorio,
    max_output_tokens: 5000,
});
if (programa.exit_code !== 0) throw new Error("Falta el proveedor de inventario");
const ejecutar = eval(programa.output);
const recibo = await ejecutar({
    repositorio,
    argumentos: ["verificar", "--trabajo", "../cp12-operacion", "--helpers", "../cp12-ayudantes"],
});
text(recibo);
```

El programa de la sesión sirve el listado a través de un canal local privado.
El código de salida, el resumen de retoma y los conteos de páginas y segundos
quedan en el resultado de la sesión. El recibo habitual de la retoma se guarda
en `--trabajo`.

### Otros proveedores e instantáneas de Biblioteca

`--inventario` acepta una instantánea de los archivos activos de Biblioteca,
recursiva y paginada hasta el final, desde `2026-11-06T00:00:00Z`. Se requiere una
captura de los últimos cinco minutos para verificar y del último minuto antes de
escribir o activar. Puede filtrarse localmente al prefijo
`CP12_CANDIDATO_P3_128492e27d6d44798f2ef9336fc1b2e7_`. El siguiente JSON muestra
el formato.

```json
{
  "captured_at": "fecha ISO 8601 de la consulta",
  "created_after": "2026-11-06T00:00:00Z",
  "complete": true,
  "items": [
    {"name": "nombre.zip", "library_file_id": "libfile_…", "file_id": "file_…", "size_bytes": 1}
  ]
}
```

`--comando-inventario /ruta/al/proveedor` también admite otros proveedores.
Recibe en stdin un JSON con `execution_uuid` y `created_after` y devuelve en
stdout una captura completa con el mismo formato.

### Recibos y recuperación de interrupciones

- `ULTIMO.json` indica el recibo de la invocación. En `recibos/` quedan las
  etapas, el HEAD comprobado, el respaldo, la actividad observada, la acción
  exacta pendiente y los tiempos separados de descarga, auditoría, espera y
  consultas. Las peticiones al chat se cuentan al abrir cada bloqueo. Volver a
  encontrar el mismo bloqueo abierto mantiene el conteo. La espera externa
  acumulada se registra por separado.
- Los recibos locales se reutilizan con la misma cápsula, inventario, registro,
  entorno y versiones. Al repetir se verifican otra vez los hashes de archivo y
  las cargas extraídas. Antes de una escritura o activación se vuelve a comprobar
  la rama, el origen y, cuando corresponda, los destinos y locks.
- El proceso lanzado conserva sus propios archivos y recibos en
  `asignaciones/`. Si aparece el adjunto exacto después de un corte se recupera
  desde Releases. Las reservas y activaciones ya publicadas se releen de Git,
  y la entrega local conserva una intención y un archivo atómico. Los archivos de
  capacidad están vinculados al mismo trabajador y registro.
- Una sesión externa o perdida se informa con su evidencia de actividad y de
  salida por separado. Se requiere una sesión original accesible o un aislamiento
  acreditado y una nueva asignación. La intención exclusiva de un intento
  anterior se reemplaza sólo con evidencia de salida o con aislamiento que
  documente ambos locks libres y prohíba reactivar el intento. Cada asignación
  nueva realiza su propia capacidad. Los rescates protegidos quedan fuera de la
  rotación.
- Un latido y el primer paso aceptado son evidencia de actividad. El reloj de
  respaldo del registro sigue apuntando a la última cápsula recuperada. La
  frontera siguiente conserva todas las puertas originales y la ruta híbrida
  para transportes, frontera y negativos.
- El código de salida `0` indica plan o inicio acreditado. El código `2` indica
  espera o bloqueo. Una espera del trabajador puede continuarse con el mismo comando y
  el mismo directorio. `--espera` acota la espera por invocación.

### Recibos de salida del supervisor

Cada lanzamiento nuevo registra un `session_id` en `REANUDADOR_ACTUAL.json`.
El supervisor es padre del ejecutor y espera su estado terminal. El recibo
vincula la sesión, el trabajador, la asignación y los SHA256 del registro y del
respaldo. Distingue un código de salida de una terminación por señal.

El destino persistente es la [rama de recibos](https://github.com/diegolezaval/Proyecto_Runas/tree/administracion/cp12-recibos-salida),
bajo `checkpoints/CP12/p3_20261018/recibos_salida/<asignacion>/<session_id>.json`.
Antes de lanzar, `retomar` comprueba acceso Git al destino. Después de observar
la salida, el supervisor publica el recibo y comprueba los bytes desde el remoto.
La publicación usa la autenticación Git del supervisor. Los identificadores
de asignación que comienzan por `prueba_` corresponden a procesos de prueba.
La entrega de activación exige que el supervisor de esa sesión siga accesible.

En otro entorno, `verificar` busca el recibo de la sesión registrada.
`SALIDA_CONFIRMADA` incluye su commit y ruta. `CONTACTO_PERDIDO_SIN_SALIDA`
indica que falta evidencia terminal. Si Git falla después de la observación,
`SALIDA_LOCAL_PENDIENTE` conserva la evidencia local y `retomar` reintenta
publicarla desde el mismo `--trabajo`. La pérdida del supervisor antes de
observar la salida deja la sesión en comprobación.

El aislamiento posterior identifica la misma asignación y `session_id`.
Cuando el aislamiento se acredita por salida, el reanudador comprueba el
recibo remoto. La comprobación de ambos locks originales sigue disponible
como otra evidencia de aislamiento.

## Comprobaciones

```bash
PYTHONPATH=herramientas python3 -m unittest -v cp12_reanudacion.test_reanudacion cp12_reanudacion.test_supervisor
node --test herramientas/cp12_reanudacion/test_inventario_work.js

python3 herramientas/reanudar_cp12.py verificar \
  --historial 2434e69871f4c20314aafceb04c0eda754c927c5 \
  --trabajo ../cp12-operacion --helpers ../cp12-ayudantes --inventario ../cp12-inventario.json
```

El [recibo de pruebas](../../informes/REANUDADOR_CP12_PRUEBAS_20261107.json)
distingue las auditorías de cápsulas reales, la lectura del inicio histórico y
las interrupciones simuladas en un remoto Git local.

El [recibo del inventario automático](../../informes/REANUDADOR_CP12_INVENTARIO_BIBLIOTECA_20261107.json)
registra la prueba contra Biblioteca y el estado de la retoma desde τ30,0.

El [recibo de pruebas del supervisor](../../informes/REANUDADOR_CP12_SUPERVISION_20261107.json)
registra las terminaciones de prueba y su recuperación desde GitHub.
