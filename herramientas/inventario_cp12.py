#!/usr/bin/env python3
"""Canal privado entre --comando-inventario y el listado de Biblioteca de la sesión."""

import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from uuid import uuid4

from cp12_reanudacion.infra import LIBRARY_SINCE, UID, optional, read, record, require


CHANNEL_ENV = 'RUNICA_CP12_BUZON_BIBLIOTECA'
REQUEST = {'execution_uuid': UID, 'created_after': LIBRARY_SINCE}


def channel(value):
    require(value, 'Falta el canal de Biblioteca de la sesión')
    path = Path(value).absolute()
    info = path.lstat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and not info.st_mode & 0o077,
            'El canal de Biblioteca debe ser un directorio privado del operador')
    return path


def wait_for(read_ready, seconds):
    limit = time.monotonic() + seconds
    while True:
        result = read_ready()
        if result is not None or time.monotonic() >= limit:
            return result
        time.sleep(0.15)


def reply_path(path, key):
    require(isinstance(key, str) and re.fullmatch('[0-9a-f]{32}', key), 'Solicitud de inventario inválida')
    require((path / (key + '.solicitud.json')).is_file(), 'Solicitud de inventario desconocida')
    return path / (key + '.respuesta.json')


def inventory(path, request):
    require(request == REQUEST, 'Consulta fuera del inventario CP12 autorizado')
    key = uuid4().hex
    record(path / (key + '.solicitud.json'), request, once=True)
    response = reply_path(path, key)
    result = wait_for(lambda: optional(response), 105)
    require(result is not None, 'La sesión no respondió a la consulta de Biblioteca')
    if 'error' in result:
        raise ValueError(result['error'])
    return result['inventory']


def event(path):
    def next_event():
        status = optional(path / 'finalizado.json')
        if status is not None:
            return status
        for item in sorted(path.glob('*.solicitud.json')):
            key = item.name.removesuffix('.solicitud.json')
            if not reply_path(path, key).exists():
                return dict(key=key, request=read(item))
        return None
    return wait_for(next_event, 10) or {}


def start(path, args):
    require(args and args[0] in ('verificar', 'retomar'), 'Falta verificar o retomar')
    require(all(arg.partition('=')[0] not in ('--inventario', '--comando-inventario') for arg in args),
            'El canal de sesión ya fija el proveedor de inventario')
    script = Path(__file__).resolve()
    command = [sys.executable, str(script.with_name('reanudar_cp12.py')), *args,
               '--comando-inventario', str(script)]
    code = 2
    try:
        code = subprocess.run(command, env=dict(os.environ, **{CHANNEL_ENV: str(path)})).returncode
        return code
    finally:
        record(path / 'finalizado.json', dict(exit_code=code), once=True)


def main():
    args = sys.argv[1:]
    try:
        if not args:
            value = inventory(channel(os.environ.get(CHANNEL_ENV)), json.load(sys.stdin))
        elif len(args) >= 2:
            operation, location, *rest = args
            path = channel(location)
            if operation == 'iniciar':
                return start(path, rest)
            require(not rest, 'Argumentos adicionales en el canal de inventario')
            if operation == 'esperar':
                value = event(path)
            elif operation == 'responder':
                response = json.load(sys.stdin)
                key = response.pop('key')
                record(reply_path(path, key), response, once=True)
                return 0
            else:
                raise ValueError('Operación de inventario inválida')
        else:
            raise ValueError('Falta la ruta del canal de inventario')
        print(json.dumps(value, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'Inventario Biblioteca · {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
