"""Lectura de destinos, recibos atómicos y publicación Git con lectura posterior."""

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import quote
from urllib.request import Request, urlopen


REPO = 'diegolezaval/Proyecto_Runas'
BRANCH = 'ciencia/cp12-residuo-p3-20261018'
REF = 'refs/heads/' + BRANCH
TAG = 'respaldo-cp12-p3-20261027'
RELEASE = 426273098
UID = '128492e27d6d44798f2ef9336fc1b2e7'
PREFIX = f'CP12_CANDIDATO_P3_{UID}_'
ROOT = 'checkpoints/CP12/p3_20261018'
STATE = ROOT + '/ESTADO_REANUDACION.json'
CLAIM = ROOT + '/REANUDADOR_ACTUAL.json'
HYBRID = ROOT + '/conservacion_hibrida_20261106/ejecutor'
AUDITOR = ROOT + '/retoma_20261028/auditar_recuperacion.py'
COMPARE = 'herramientas/comparar_control_publico_p3.py'
LIBRARY_SINCE = '2026-11-06T00:00:00Z'


class Stop(Exception):
    def __init__(self, code, reason, action, *, file=None, destination=None, chat=True):
        super().__init__(reason)
        self.detail = dict(code=code, reason=reason, action=action, file=file,
                           destination=destination, chat=chat)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_bytes())


def optional(path):
    return read(path) if path.is_file() else None


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def install(path, data, *, once=False):
    """Publicar un archivo completo y duradero, incluso si dos lectores coinciden."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        tmp = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        if once:
            try:
                os.link(tmp, path)
            except FileExistsError:
                require(path.read_bytes() == data, f'Recibo existente distinto: {path.name}')
        else:
            os.replace(tmp, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    finally:
        tmp.unlink(missing_ok=True)


def record(path, value, *, once=False):
    install(path, encoded(value), once=once)
    return value


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def age(timestamp):
    return (datetime.now(timezone.utc) - datetime.fromisoformat(timestamp)).total_seconds()


class Timings:
    def __init__(self):
        self.events = []

    @contextmanager
    def measure(self, category, name):
        start = time.monotonic()
        try:
            yield
        finally:
            self.events.append(dict(category=category, name=name,
                                    seconds=round(time.monotonic() - start, 3)))

    def totals(self):
        return {key: round(sum(x['seconds'] for x in self.events if x['category'] == key), 3)
                for key in ('descarga', 'auditoria', 'espera', 'consulta')}


class Git:
    def __init__(self, root):
        self.root = root

    def run(self, *args, data=None, env=None, check=True):
        result = subprocess.run(['git', *args], cwd=self.root, env=env, input=data,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
        if check and result.returncode:
            raise RuntimeError(f'Git {args[0]} terminó con código {result.returncode}')
        return result

    def pin(self, commit):
        require(re.fullmatch('[0-9a-f]{40}', commit), 'Commit Git inválido')
        if self.run('cat-file', '-e', commit + '^{commit}', check=False).returncode:
            self.run('fetch', '--no-tags', 'origin', commit)
        self.run('cat-file', '-e', commit + '^{commit}')
        return commit

    def head(self):
        line = self.run('ls-remote', '--exit-code', 'origin', REF).stdout.decode().split()
        require(len(line) == 2 and line[1] == REF, 'No se pudo fijar la rama científica')
        return self.pin(line[0])

    def get(self, commit, path, *, missing=False):
        posix = Path(path)
        require(not posix.is_absolute() and '..' not in posix.parts and '\\' not in path,
                'Ruta Git inválida')
        result = self.run('show', f'{commit}:{path}', check=not missing)
        return None if result.returncode else result.stdout

    def json(self, commit, path, *, missing=False):
        data = self.get(commit, path, missing=missing)
        return json.loads(data) if data is not None else None

    def publish(self, parent, files, message):
        """Sólo se publica un descendiente directo del HEAD que se comprobó."""
        def matches(head):
            return all(self.get(head, path, missing=True) == data for path, data in files.items())

        head = self.head()
        if matches(head):
            return head
        if head != parent:
            raise Stop('RAMA_CAMBIO', 'Cambió el registro antes de escribir',
                       'Reejecutar retomar para reconciliar la rama', chat=False)
        with tempfile.TemporaryDirectory() as temp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
            self.run('read-tree', parent, env=env)
            for path, data in files.items():
                blob = self.run('hash-object', '-w', '--stdin', data=data).stdout.decode().strip()
                self.run('update-index', '--add', '--cacheinfo', f'100644,{blob},{path}', env=env)
            tree = self.run('write-tree', env=env).stdout.decode().strip()
        commit = self.run('commit-tree', tree, '-p', parent, '-m', message).stdout.decode().strip()
        try:
            self.run('push', f'--force-with-lease={REF}:{parent}', 'origin', f'{commit}:{REF}',
                     env=dict(os.environ, GIT_TERMINAL_PROMPT='0'), check=False)
        except subprocess.TimeoutExpired:
            pass  # La respuesta puede haberse perdido después de la escritura.
        head = self.head()
        if not matches(head):
            raise Stop('GIT_PUBLICACION_PENDIENTE', 'Git no confirmó los bytes tras el push',
                       f'Comprobar credenciales y rama, y recuperar o publicar el commit {commit}',
                       file=', '.join(files), destination=BRANCH)
        require(not self.run('merge-base', '--is-ancestor', commit, head, check=False).returncode,
                'Git contiene los bytes pero otro commit los publicó; reconciliar antes de seguir')
        return commit

    def version(self, head, path):
        """Commit público que introdujo el archivo inmutable de esta asignación."""
        commit = self.run('log', '-1', '--format=%H', head, '--', path).stdout.decode().strip()
        require(commit and self.get(commit, path) == self.get(head, path),
                f'Historial incompleto de {path}; recuperar los commits de la asignación')
        return commit


def asset_url(name):
    return f'https://github.com/{REPO}/releases/download/{TAG}/{quote(name)}'


def asset_identity(item, spec):
    require(item['name'] == spec['file_name'] and item['size'] == spec['bytes'] and
            item.get('digest') == 'sha256:' + spec['sha256'] and
            item['browser_download_url'] == asset_url(spec['file_name']) and
            item['state'] == 'uploaded' and item['id'] > 0, 'Identidad del adjunto público distinta')
    return item


def request(url):
    return urlopen(Request(url, headers={'User-Agent': 'Runica-CP12-reanudar/1'}), timeout=90)


class Destinations:
    def __init__(self, work, helpers, timings, files=(), inventory=None, inventory_command=None):
        self.work, self.helpers, self.timings = work, helpers, timings
        self.files = {file.name: file for file in files}
        require(len(self.files) == len(files), 'Hay dos archivos aportados con el mismo nombre')
        self.inventory_file, self.inventory_command = inventory, inventory_command

    def assets(self):
        with self.timings.measure('consulta', 'GitHub Releases'):
            items = []
            for page in range(1, 51):
                url = f'https://api.github.com/repos/{REPO}/releases/{RELEASE}/assets?per_page=100&page={page}'
                with request(url) as stream:
                    batch = json.load(stream)
                require(isinstance(batch, list), 'Listado GitHub inválido')
                items.extend(batch)
                if len(batch) < 100:
                    return items
            raise ValueError('Listado GitHub incompleto')

    def library(self, *, max_age=300):
        with self.timings.measure('consulta', 'Inventario Biblioteca'):
            if self.inventory_command:
                result = subprocess.run([self.inventory_command], input=encoded(
                    dict(execution_uuid=UID, created_after=LIBRARY_SINCE)),
                    capture_output=True, check=True, timeout=120)
                inventory = json.loads(result.stdout)
            elif self.inventory_file and self.inventory_file.is_file():
                inventory = read(self.inventory_file)
            else:
                inventory = {}
            if (inventory.get('complete') is not True or
                    inventory.get('created_after', '9999') > LIBRARY_SINCE or
                    not -30 <= age(inventory['captured_at']) <= max_age):
                raise Stop('INVENTARIO_BIBLIOTECA',
                           f'Falta un inventario completo de Biblioteca de los últimos {max_age} segundos',
                           'Listar los archivos activos desde ' + LIBRARY_SINCE +
                           ' y entregar el inventario con --inventario o --comando-inventario',
                           file=str(self.inventory_file or 'inventario.json'), destination='Biblioteca')
            require(isinstance(inventory['items'], list), 'Inventario de Biblioteca inválido')
            return [item for item in inventory['items'] if item.get('name', '').startswith(PREFIX)]

    def upload(self, archive):
        with self.timings.measure('espera', 'Subida GitHub'):
            result = subprocess.run(['gh', 'release', 'upload', TAG, str(archive), '-R', REPO],
                                    capture_output=True, timeout=900)
        return result.returncode

    def archive(self, spec, *, public=None):
        name = spec['file_name']
        require(re.fullmatch(r'[A-Za-z0-9_.~+-]+\.zip', name) and
                re.fullmatch('[0-9a-f]{64}', spec['sha256']) and spec['bytes'] > 0,
                'Identidad de archivo inválida')
        path = self.files.get(name) or self.work / 'archivos' / spec['sha256'] / name
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=path.parent) as directory:
                private = Path(directory)
                temp = private / name
                with self.timings.measure('descarga', name):
                    if public is not None:
                        asset_identity(public, spec)
                        with request(public['browser_download_url']) as source, temp.open('xb') as target:
                            shutil.copyfileobj(source, target, 1024 * 1024)
                    else:
                        self.materialize(spec, temp)
                self.check(temp, spec)
                os.replace(temp, path)
        else:
            self.check(path, spec)
        return path

    def check(self, path, spec):
        with self.timings.measure('auditoria', 'SHA256 ' + path.name):
            require(path.is_file() and path.stat().st_size == spec['bytes'] and sha(path) == spec['sha256'],
                    f'Tamaño o SHA256 incorrecto: {path.name}')

    def materialize(self, spec, path):
        try:
            helper = module(self.helpers / 'library_hosted_apps.py', '_cp12_hosted_apps')
            item = {key: spec[key] for key in ('library_file_id', 'file_id', 'file_name')}
            with (path.parent / 'transfer.log').open('w') as log, redirect_stdout(log), redirect_stderr(log):
                response = helper.HostedAppsClient().call_tool(
                    'connector_openai_library', 'prepare_materialize',
                    dict(items=[item], destination=dict(directory=str(path.parent))))
                for _ in range(5):
                    if 'transfers' in response:
                        break
                    if 'content' in response and 'structuredContent' not in response and 'result' not in response:
                        response = json.loads(''.join(x['text'] for x in response['content'] if x['type'] == 'text'))
                    else:
                        response = response.get('structuredContent', response.get('result', {}))
                require(len(response['transfers']) == 1 and not response.get('unavailable_items'),
                        'Transferencia de Biblioteca incompleta')
                transfer = response['transfers'][0]
                workspace = transfer.get('workspace_path')
                if workspace:
                    require(Path(workspace).resolve() == path.resolve(), 'Ruta de Biblioteca distinta')
                command = ['apply-xattrs' if workspace else 'materialize', str(path)]
                subprocess.run([sys.executable, str(self.helpers / 'library_file_transfer.py'), *command],
                               input=encoded(transfer), stdout=log, stderr=log, check=True, timeout=300)
        except Exception as error:
            raise Stop('DESCARGA_BIBLIOTECA', f'Materialización no disponible ({type(error).__name__})',
                       f'Recuperar {spec["library_file_id"]} / {spec["file_id"]} y pasar --archivo',
                       file=path.name, destination='Biblioteca') from error


def find_asset(assets, spec):
    matches = [item for item in assets if item['name'] == spec['file_name']]
    require(len(matches) <= 1, 'Más de un adjunto con el nombre exacto')
    return asset_identity(matches[0], spec) if matches else None


def library_item(items, spec):
    matches = [x for x in items if x['library_file_id'] == spec['library_file_id']]
    if len(matches) != 1:
        raise Stop('IDENTIDAD_BIBLIOTECA', 'Identidad de Biblioteca ausente o ambigua',
                   f'Recuperar o conciliar {spec["library_file_id"]} en un inventario actual y repetir',
                   file=spec['file_name'], destination='Biblioteca')
    item = matches[0]
    require(item['file_id'] == spec['file_id'] and item['name'] == spec['file_name'] and
            item['size_bytes'] == spec['bytes'], f'Versión de Biblioteca distinta: {spec["file_name"]}')
    return item
