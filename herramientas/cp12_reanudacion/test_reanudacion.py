"""Pruebas administrativas aisladas. Ningún caso arranca M2 ni publica fuera de /tmp."""

from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from inventario_cp12 import CHANNEL_ENV, REQUEST, event, reply_path

from . import trabajador
from .evidencia import first_step, historical_chain, resolve, unpublished
from .flujo import Flow, pending_public
from .infra import (BRANCH, CLAIM, PREFIX, STATE, Destinations, Git, Stop, Timings, asset_url,
                    encoded, now, record, sha)


REFERENCE = '2434e69871f4c20314aafceb04c0eda754c927c5'
BOUNDARY = 'e13e7dc80dc0bb6ad0dbe609d5da8f96545e3dad'
CURRENT = '6153caeaa8bee7c80b87897693fe97ff2dd34126'
REPOSITORY = Path(__file__).resolve().parents[2]


def asset(request, identity=10):
    return dict(id=identity, name=request['file_name'], size=request['bytes'], state='uploaded',
                digest='sha256:' + request['sha256'], browser_download_url=asset_url(request['file_name']))


class LibraryProviderTests(unittest.TestCase):
    def test_provider_requests_a_fresh_inventory_each_time(self):
        provider = REPOSITORY / 'herramientas/inventario_cp12.py'
        with tempfile.TemporaryDirectory() as temp, ThreadPoolExecutor() as thread:
            work = Path(temp)
            with patch.dict(os.environ, {CHANNEL_ENV: temp}):
                destinations = Destinations(work, work, Timings(), inventory_command=provider)
                keys = set()
                for size in (8, 9):
                    waiting = thread.submit(destinations.library, max_age=60)
                    request = event(work)
                    self.assertEqual(request['request'], REQUEST)
                    self.assertNotIn(request['key'], keys)
                    keys.add(request['key'])
                    item = dict(name=PREFIX + 'test.zip', library_file_id='biblioteca', file_id='f', size_bytes=size)
                    record(reply_path(work, request['key']), dict(inventory=dict(
                        captured_at=now(), created_after=REQUEST['created_after'], complete=True, items=[item])))
                    self.assertEqual(waiting.result(timeout=5), [item])

    def test_unavailable_provider_keeps_the_library_gate_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            destinations = Destinations(work, work, Timings(), inventory_command=work / 'proveedor-ausente')
            with self.assertRaises(Stop) as caught:
                destinations.library()
            self.assertEqual(caught.exception.detail['code'], 'INVENTARIO_BIBLIOTECA')


class PublicCapacityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.work = Path(tmp.name)
        self.archive = self.work / 'control.zip'
        self.archive.write_bytes(b'control de capacidad simulado')
        self.request = dict(file_name=self.archive.name, archive_path=str(self.archive),
                            bytes=self.archive.stat().st_size, sha256=sha(self.archive))
        self.intent = self.work / 'INTENCION.json'
        self.remote = Mock(wraps=Destinations(self.work, self.work, Timings()))
        self.remote.assets = Mock(return_value=[])
        self.remote.upload = Mock(return_value=0)

    def test_unregistered_publication_is_reused(self):
        self.intent.write_text('{}')
        uploaded = asset(self.request)
        for _ in range(2):
            self.assertEqual(pending_public(self.remote, [uploaded], self.request, self.intent), uploaded)
        self.remote.upload.assert_not_called()

    def test_conflicting_exact_name_is_rejected(self):
        uploaded = asset(dict(self.request, sha256='f' * 64))
        with self.assertRaisesRegex(ValueError, 'Identidad del adjunto'):
            pending_public(self.remote, [uploaded], self.request, self.intent)
        self.remote.upload.assert_not_called()

    def test_hash_of_local_control_is_checked_before_upload(self):
        self.archive.write_bytes(b'x' * self.request['bytes'])
        with self.assertRaisesRegex(ValueError, 'SHA256 incorrecto'):
            pending_public(self.remote, [], self.request, self.intent, self.request['sha256'])
        self.remote.upload.assert_not_called()
        self.assertFalse(self.intent.exists())

    def test_approval_binds_to_exact_hash_and_unknown_result_does_not_retry(self):
        with self.assertRaisesRegex(Stop, 'aprobación explícita'):
            pending_public(self.remote, [], self.request, self.intent, 'f' * 64)
        self.remote.upload.side_effect = subprocess.TimeoutExpired(['gh'], 1)
        with self.assertRaisesRegex(Stop, 'no confirmó'):
            pending_public(self.remote, [], self.request, self.intent, self.request['sha256'])
        with self.assertRaisesRegex(Stop, 'intención previa'):
            pending_public(self.remote, [], self.request, self.intent, self.request['sha256'])
        self.remote.upload.assert_called_once_with(self.archive)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.git = Git(REPOSITORY)

    def test_historical_evidence_and_worker_heartbeat(self):
        self.git.pin(REFERENCE)
        plan = resolve(self.git, REFERENCE)
        chain = historical_chain(self.git, plan)
        self.assertEqual(plan.origin['observer_clock'], 28.8)
        self.assertEqual(chain['first']['clock'], 28.81)
        self.assertEqual(chain['first']['accepted_steps_since_restore'], [1, 1])
        with self.assertRaises(ValueError):
            first_step(dict(chain['first'], accepted_steps_since_restore=[0, 0]), plan.registry)
        self.git.pin(CURRENT)
        current = resolve(self.git, CURRENT)
        self.assertEqual(current.origin['observer_clock'], 30)
        self.assertEqual(current.frontier['observer_clock'], 24)
        self.git.pin(BOUNDARY)
        boundary = resolve(self.git, BOUNDARY)
        self.assertTrue(boundary.assignment_matches())
        self.assertEqual(historical_chain(self.git, boundary)['first']['clock'], 24.01)

    def test_new_archive_is_pending_but_capacity_is_never_an_origin(self):
        self.git.pin(CURRENT)
        plan = resolve(self.git, CURRENT)
        name = PREFIX + 'TRANSPORTE_000304_P3_30_A32.zip'
        pending = unpublished(plan, [], [dict(id='x', name=name)])
        self.assertEqual(pending['observer_clock'], 30.4)
        self.assertIsNone(unpublished(plan, [dict(name=PREFIX + 'CONTROL_PUBLICO_P3_30_A32.zip')], []))

    def test_actual_live_worker_locks_and_missing_pid(self):
        with tempfile.TemporaryDirectory() as temp:
            job = Path(temp)
            a, b = job / 'P3_WORKER.lock', job / 'home/runtime/worker.lock'
            b.parent.mkdir(parents=True)
            child = subprocess.Popen([sys.executable, '-c',
                'import fcntl,sys; a,b=(open(p,"a+") for p in sys.argv[1:]);'
                'fcntl.flock(a,2);fcntl.flock(b,2);print("listo",flush=True);sys.stdin.read()',
                str(a), str(b)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            try:
                self.assertEqual(child.stdout.readline(), b'listo\n')
                record(job / 'PROCESO.json', dict(worker_id='proceso', registry_sha256='registro',
                                                 identity=trabajador.identity(child.pid)))
                record(b.parent / 'worker_started.json', dict(pid=child.pid, registry_sha256='registro'))
                self.assertTrue(trabajador.live(job, 'proceso', 'registro', locks=True))
                self.assertFalse(trabajador.lock_owner(b, os.getpid()))
                with self.assertRaisesRegex(ValueError, 'otra asignación'):
                    trabajador.live(job, 'otro', 'registro', locks=True)
            finally:
                child.communicate(timeout=5)
            self.assertFalse(trabajador.live(job, 'proceso', 'registro', locks=True))
            self.assertIsNone(trabajador.optional(job / 'SALIDA_OBSERVADA.json'))

    def test_registered_inaccessible_session_is_not_an_exit(self):
        self.git.pin(CURRENT)
        plan = resolve(self.git, CURRENT)
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            report = {}
            flow = Flow(self.git, Mock(), work, work, Timings(), report)
            flow.job = work
            flow.worker_id = None
            with patch.object(trabajador, 'lock_owner', return_value=False):
                flow.observe(plan)
            self.assertEqual(report['worker']['status'], 'SESION_INACCESIBLE_SIN_SALIDA')
            self.assertFalse(report['worker']['exit_observed'])
            with patch.object(trabajador, 'lock_owner', return_value=True):
                flow.observe(plan)
            self.assertEqual(report['worker']['status'], 'TRABAJADOR_AJENO_ACTIVO')

    def test_uploaded_native_control_is_reconciled_without_restarting_worker(self):
        self.git.pin(REFERENCE)
        plan = resolve(self.git, REFERENCE)
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            destinations = Mock()
            report = dict(stages=[], worker={})
            flow = Flow(self.git, destinations, work, work, Timings(), report)
            flow.job, flow.output = work, work / 'resultado'
            flow.audit = Mock(return_value=(work, {'passed': True}))
            file_name = PREFIX + 'CONTROL_NATIVO_P3_288_A32_HIBRIDO_20261107.zip'
            request = dict(file_name=file_name, bytes=123, sha256='1' * 64, archive_inventory={},
                           archive_path=str(work / file_name))
            record(flow.output / 'control/nativo/SOLICITUD.json', request)
            with self.assertRaisesRegex(Stop, 'salida sin observar'):
                flow.unavailable(plan, [dict(name=file_name, library_file_id='nativo', file_id='v1', size_bytes=123)])
            self.assertEqual(report['last_stage'], 'SUBIDA_NATIVA_RECONCILIADA')
            self.assertTrue((work / 'RECUPERACION_NATIVA_RECONCILIADA.json').is_file())
            flow.audit.assert_called_once()
            destinations.upload.assert_not_called()


class GitFlowTests(unittest.TestCase):
    """Git real contra un remoto local. Los comprobantes del trabajador se simulan."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        remote = self.root / 'remoto.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        local = self.root / 'clon'
        local.mkdir()
        self.git = Git(local)
        self.git.run('init', '-q', '-b', BRANCH)
        self.git.run('config', 'user.name', 'Prueba CP12')
        self.git.run('config', 'user.email', 'prueba-cp12@example.invalid')
        self.git.run('remote', 'add', 'origin', str(remote))

        source = Git(REPOSITORY)
        source.pin(REFERENCE)
        plan = resolve(source, REFERENCE)
        state = dict(plan.state, own_observed_start=None, own_guardian_tool_session_id=None, own_attempt_home=None)
        paths = [plan.registry_path, plan.origin['recovery_receipt'], plan.frontier['certificate'],
                 plan.frontier['original_spatial_and_physical_metrics']]
        paths.append(str(Path(plan.frontier['certificate']).with_name('RECUPERACION_PUBLICA.json')))
        for name in paths:
            file = local / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(source.get(REFERENCE, name))
        (local / STATE).write_bytes(encoded(state))
        self.acceptance = source.get(REFERENCE, f'{plan.directory}/capacidad/ACEPTACION_COMBINADA.json')
        self.git.run('add', '.')
        self.git.run('commit', '-qm', 'Preparación de prueba sin física')
        self.git.run('push', '-q', 'origin', BRANCH)
        self.head = self.git.head()
        self.plan = resolve(self.git, self.head)

    def test_publish_recovers_lost_push_response_and_rejects_concurrent_head(self):
        real = self.git.run

        def lose_reply(*args, **kwargs):
            result = real(*args, **kwargs)
            if args[0] == 'push':
                raise subprocess.TimeoutExpired(args, 1)
            return result

        with patch.object(self.git, 'run', side_effect=lose_reply):
            commit = self.git.publish(self.head, {'recibo.json': b'{}\n'}, 'Subida simulada')
        self.assertEqual(self.git.get(commit, 'recibo.json'), b'{}\n')
        self.assertEqual(self.git.publish(self.head, {'recibo.json': b'{}\n'}, 'Repetición'), commit)
        with self.assertRaisesRegex(Stop, 'Cambió el registro'):
            self.git.publish(self.head, {'otro.json': b'{}\n'}, 'Base obsoleta')

    def test_resume_after_reservation_activation_and_delivery_without_duplication(self):
        report = dict(stages=[], worker={})
        worker = dict(worker_id='ejecutor-simulado', at=now(), head=self.head)
        claim = dict(allocation_id=self.plan.allocation, worker_id=worker['worker_id'])
        self.git.publish(self.head, {CLAIM: encoded(claim)}, 'Intención de prueba')
        flow = Flow(self.git, Mock(), self.root, self.root, Timings(), report)
        flow.worker_id = worker
        flow.job = self.root / 'asignacion'
        flow.output = flow.job / 'resultado'
        flow.alive = Mock(return_value=True)
        flow.fresh = Mock(return_value=([], []))
        flow.validate_capacity = Mock()
        acceptance = flow.output / 'control/ACEPTACION_COMBINADA.json'
        acceptance.parent.mkdir(parents=True)
        acceptance.write_bytes(self.acceptance)
        combined = json.loads(self.acceptance)
        original_publish = flow.publish

        def interrupted(plan, files, message):
            original_publish(plan, files, message)
            raise RuntimeError('Interrupción simulada después del commit')

        for file in ('ASIGNACION_REANUDADOR.json', 'ACTIVACION.json'):
            plan = resolve(self.git, self.git.head())
            with patch.object(flow, 'publish', side_effect=interrupted):
                with self.assertRaisesRegex(RuntimeError, 'Interrupción simulada'):
                    flow.activate(plan, acceptance, combined)
            self.assertIsNotNone(self.git.get(self.git.head(), f'{plan.directory}/{file}'))
        plan = resolve(self.git, self.git.head())
        with self.assertRaisesRegex(Stop, 'paso físico aceptado'):
            flow.activate(plan, acceptance, combined)
        delivered = (flow.output / 'ACTIVACION.json').read_bytes()
        self.assertEqual(delivered, self.git.get(plan.head, f'{plan.directory}/ACTIVACION.json'))
        first = dict(at=(datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat(), clock=28.81,
                     accepted_steps_since_restore=[1, 1], replay96_to112_executed=False, CP12_closed=False)
        record(flow.output / 'INICIO_FISICO.json', first)
        flow.alive.return_value = False  # El recibo sobrevive al proceso y a la invocación.
        self.assertEqual(flow.activate(plan, acceptance, combined), 'INICIO_ACREDITADO')
        committed = resolve(self.git, self.git.head())
        self.assertEqual(historical_chain(self.git, committed)['first'], first)
        self.assertEqual(committed.origin['observer_clock'], 28.8)
        self.assertEqual(flow.activate(committed, acceptance, combined), 'INICIO_ACREDITADO')
        self.assertEqual(self.git.head(), committed.head)


if __name__ == '__main__':
    unittest.main()
