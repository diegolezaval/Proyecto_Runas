#!/usr/bin/env python3
"""Consultar o retomar CP12/P3 desde el último respaldo acreditado."""

import argparse
import fcntl
from pathlib import Path
import sys
import traceback
import uuid

from cp12_reanudacion.flujo import Flow
from cp12_reanudacion.infra import (REPO, Destinations, Git, Stop, Timings, age, now, optional,
                                    record, require)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('modo', choices=('verificar', 'retomar'))
    parser.add_argument('--trabajo', type=Path, required=True, help='Directorio privado y persistente fuera del repositorio')
    parser.add_argument('--helpers', type=Path, required=True, help='Ayudantes de Biblioteca fijados por la asignación')
    inventory = parser.add_mutually_exclusive_group()
    inventory.add_argument('--inventario', type=Path, help='Instantánea completa y reciente de Biblioteca')
    inventory.add_argument('--comando-inventario', type=Path, help='Proveedor ejecutable de inventario JSON')
    parser.add_argument('--archivo', type=Path, action='append', default=[],
                        help='Copia ya recuperada del destino registrado. Repetible')
    parser.add_argument('--historial', help='Commit histórico de sólo lectura')
    parser.add_argument('--aprobar-publicacion', metavar='SHA256', help='Autorizar un control público exacto')
    parser.add_argument('--espera', type=int, default=60, metavar='SEGUNDOS',
                        help='Espera máxima en el trabajador durante esta invocación')
    args = parser.parse_args()
    if (args.modo == 'retomar' and args.historial) or (args.modo == 'verificar' and args.aprobar_publicacion):
        parser.error('El historial es de sólo lectura. La aprobación sólo aplica a retomar')
    if args.historial and (len(args.historial) != 40 or any(c not in '0123456789abcdef' for c in args.historial)):
        parser.error('--historial requiere el SHA completo de un commit')
    if not 0 <= args.espera <= 3600:
        parser.error('--espera debe estar entre 0 y 3600 segundos')
    return args


def summary(report, receipt):
    origin = report.get('origin', {})
    block = report.get('block')
    clock = origin.get('observer_clock')
    print(f"Estado · {report['status']} | intervenciones del chat {report['chat_interventions_total']}")
    if clock is None:
        print('Origen · pendiente')
    else:
        kind = {'transport': 'transporte', 'boundary': 'frontera'}[origin['kind']]
        clock_label = f'{clock:g}'.replace('.', ',')
        print(f'Origen · τ{clock_label} ({kind})')
    print(f"Última etapa · {report['last_stage']}")
    if block:
        target = ' → '.join(x for x in (block['file'], block['destination']) if x)
        print(f"Bloqueo · {block['reason']}" + (f' | {target}' if target else ''))
    else:
        print('Bloqueo · ninguno')
    print(f"Siguiente · {report['next_action']} | recibo {receipt}")


def interventions(path, report, locked):
    ledger = optional(path) or {}
    allocation = report.get('allocation', 'sin-asignacion')
    entries = ledger.setdefault(allocation, [])
    if isinstance(entries, dict):
        entries = ledger[allocation] = [dict(value, key=key) for key, value in entries.items()]
    block = report.get('block')
    report['chat_interventions_this_run'] = 0
    if locked:
        active = next((entry for entry in reversed(entries) if 'until' not in entry), None)
        key = block['code'] + '|' + str(block['file'] or '') if block and block['chat'] else None
        if active and active['key'] != key:
            active['until'] = now()
            active['seconds'] = round(max(0, age(active['since'])), 3)
            active = None
        if key and not active:
            active = dict(since=now(), block=block, key=key)
            entries.append(active)
            report['chat_interventions_this_run'] = 1
        if entries:
            record(path, ledger)
    report['chat_interventions_total'] = len(entries)
    report['external_wait_seconds'] = round(sum(entry.get('seconds', max(0, age(entry['since'])))
                                                for entry in entries), 3)


def main():
    args = arguments()
    root = Path(__file__).resolve().parents[1]
    work = args.trabajo.resolve()
    require(not work.is_relative_to(root), '--trabajo debe quedar fuera del repositorio')
    work.mkdir(mode=0o700, parents=True, exist_ok=True)
    helpers = args.helpers.resolve()
    timings = Timings()
    git = Git(root)
    sources = (f'https://github.com/{REPO}', f'https://github.com/{REPO}.git',
               f'git@github.com:{REPO}.git', f'ssh://git@github.com/{REPO}.git')
    destinations = Destinations(work, helpers, timings, files=[p.resolve() for p in args.archivo],
                                inventory=args.inventario, inventory_command=args.comando_inventario.resolve()
                                if args.comando_inventario else None)
    report = dict(schema='CP12_REANUDADOR_RECEIPT_V1', mode=args.modo, historical=args.historial,
                  started_at=now(), stages=[], last_stage='CONSULTA', status='BLOQUEADO')
    receipt = work / 'recibos' / (uuid.uuid4().hex + '.json')
    scope = 'historial-' + args.historial if args.historial else 'vigente'
    ledger_path = work / 'intervenciones' / (scope + '.json')
    flow = Flow(git, destinations, work, helpers, timings, report,
                seconds=args.espera, approval=args.aprobar_publicacion)
    with (work / 'REANUDADOR.lock').open('a+') as lock:
        locked = False
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
            origin = git.run('remote', 'get-url', 'origin').stdout.decode().strip()
            push_origin = git.run('remote', 'get-url', '--push', 'origin').stdout.decode().strip()
            require(origin in sources and push_origin in sources, 'El remoto origin no corresponde a Proyecto_Runas')
            report['status'] = flow.run(args.modo, historical=args.historial)
        except BlockingIOError:
            report['block'] = Stop('COORDINADOR_ACTIVO', 'Hay otra invocación en el mismo directorio',
                                   'Esperar su recibo y repetir', chat=False).detail
        except Stop as stop:
            report['block'] = stop.detail
            if not stop.detail['chat']:
                report['status'] = 'EN_ESPERA'
        except Exception as error:
            report['block'] = Stop('COMPROBACION_FALLIDA', f'{type(error).__name__}: {error}',
                                   'Consultar el recibo y corregir la comprobación antes de repetir').detail
            report['diagnostic'] = traceback.format_exc()

        block = report.get('block')
        if block:
            report['next_action'] = block['action']
        interventions(ledger_path, report, locked)
        report['finished_at'] = now()
        report['timings_seconds'] = timings.totals()
        report['timing_events'] = timings.events
        if hasattr(flow, 'job'):
            report['worker_timing'] = optional(flow.job / 'TIEMPOS_TRABAJADOR.json')
        record(receipt, report, once=True)
        if locked:
            record(work / 'ULTIMO.json', dict(receipt=str(receipt), status=report['status']))
    summary(report, receipt)
    return 2 if block else 0


if __name__ == '__main__':
    sys.exit(main())
