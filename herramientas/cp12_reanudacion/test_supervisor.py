"""Procesos y Git reales de prueba, con almacenamiento fuera de cada intento."""

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import uuid4

from . import supervisor, trabajador
from .flujo import Flow
from .infra import Git, Stop, Timings, now, record


def example_claim(label):
    return dict(schema=supervisor.WORKER_SCHEMA, allocation_id='prueba_supervision_' + label,
                worker_id=uuid4().hex, session_id=uuid4().hex, registry_sha256='1' * 64,
                source_archive_sha256='2' * 64, at=now())


class ExitSupervisorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.remote = self.root / 'persistente.git'
        self.origin = self.root / 'checkout_a'
        self.origin.mkdir()
        subprocess.run(['git', 'init', '--bare', '-q', str(self.remote)], check=True)
        git = Git(self.origin)
        git.run('init', '-q')
        git.run('config', 'user.name', 'Prueba CP12')
        git.run('config', 'user.email', 'cp12@example.invalid')
        git.run('commit', '--allow-empty', '-qm', 'Inicio de prueba')
        git.run('remote', 'add', 'origin', str(self.remote))
        git.run('push', '-q', 'origin', f'HEAD:{supervisor.EXIT_REF}')
        self.git = git
        self.job = self.root / 'entorno_temporal'
        self.job.mkdir()

    def fresh_checkout(self):
        fresh = self.root / 'checkout_b'
        subprocess.run(['git', 'clone', '-q', '--branch', supervisor.EXIT_BRANCH,
                        str(self.remote), str(fresh)], check=True)
        return Git(fresh)

    def test_new_session_recovers_confirmed_exit_after_original_is_removed(self):
        claim = example_claim('codigo')
        supervisor.check_destination(self.git)
        result = supervisor.supervise(self.git, self.job, claim, [sys.executable, '-c', 'raise SystemExit(17)'])
        self.assertEqual(result, 0)
        shutil.rmtree(self.job)
        shutil.rmtree(self.origin)
        fresh = self.fresh_checkout()
        receipt = supervisor.recover(fresh, claim)['receipt']
        self.assertEqual(receipt['exit_code'], 17)
        self.assertIsNone(receipt['signal'])
        self.assertEqual(receipt['session_id'], claim['session_id'])
        self.assertEqual(receipt['allocation_id'], claim['allocation_id'])
        self.assertEqual(supervisor.publish(fresh, claim, receipt)['commit'], fresh.head(supervisor.EXIT_REF))
        self.assertEqual(supervisor.recover(fresh, dict(claim, session_id=uuid4().hex)), None)
        with self.assertRaisesRegex(ValueError, 'otra sesión'):
            supervisor.recover(fresh, dict(claim, registry_sha256='3' * 64))
        flow = Flow(fresh, None, fresh.root, None, Timings(), dict(stages=[]))
        flow.job, flow.worker_id = fresh.root / 'nuevo_trabajo', None
        plan = SimpleNamespace(claim=claim, state={}, allocation=claim['allocation_id'],
                               registry_sha=claim['registry_sha256'],
                               origin={'sha256': claim['source_archive_sha256']})
        flow.observe(plan)
        self.assertEqual(flow.report['worker']['status'], 'SALIDA_CONFIRMADA')
        with self.assertRaises(Stop) as stopped:
            flow.stop_for_exit_evidence()
        self.assertEqual(stopped.exception.detail['code'], 'TRABAJADOR_TERMINADO')

    def test_signal_is_recorded_from_wait_and_not_as_an_exit_code(self):
        claim = example_claim('senal')
        command = [sys.executable, '-c', 'import os,signal;os.kill(os.getpid(),signal.SIGKILL)']
        self.assertEqual(supervisor.supervise(self.git, self.job, claim, command), 0)
        value = supervisor.recover(self.git, claim)['receipt']
        self.assertEqual(value['signal'], signal.SIGKILL)
        self.assertIsNone(value['exit_code'])
        self.assertTrue(value['exit_observed'])

    def test_destination_failure_keeps_receipt_for_retry(self):
        claim = example_claim('reintento')
        with patch.object(supervisor, 'publish', side_effect=RuntimeError('prueba de transporte')):
            result = supervisor.supervise(self.git, self.job, claim, [sys.executable, '-c', 'pass'])
        self.assertEqual(result, 2)
        local = json.loads((self.job / 'SALIDA_OBSERVADA.json').read_bytes())
        self.assertEqual(supervisor.evidence(self.git, claim, local)['status'], 'SALIDA_LOCAL_PENDIENTE')
        self.assertEqual(supervisor.evidence(self.git, claim)['status'], 'CONTACTO_PERDIDO_SIN_SALIDA')
        self.assertEqual(supervisor.evidence(self.git, claim, local, retry=True)['status'], 'SALIDA_CONFIRMADA')

    def test_lost_supervisor_leaves_no_confirmed_exit(self):
        claim = example_claim('contacto')
        ready = self.job / 'listo'
        worker = 'import pathlib,sys,time;pathlib.Path(sys.argv[1]).touch();time.sleep(30)'
        launch = (
            'import json,sys;from pathlib import Path;'
            'from cp12_reanudacion.infra import Git;from cp12_reanudacion.supervisor import supervise;'
            'raise SystemExit(supervise(Git(Path(sys.argv[1])),Path(sys.argv[2]),json.loads(sys.argv[3]),'
            '[sys.executable,"-c",sys.argv[4],sys.argv[5]]))'
        )
        process = subprocess.Popen([sys.executable, '-c', launch, str(self.origin), str(self.job),
                                    json.dumps(claim), worker, str(ready)], start_new_session=True)
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(.025)
            self.assertTrue(ready.is_file(), 'El hijo de prueba debe haber empezado')
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=5)
        shutil.rmtree(self.job)
        shutil.rmtree(self.origin)
        value = supervisor.evidence(self.fresh_checkout(), claim)
        self.assertEqual(value['status'], 'CONTACTO_PERDIDO_SIN_SALIDA')
        self.assertEqual(value['exit_lookup'], 'SIN_RECIBO')
        self.assertFalse(value['exit_observed'])

    def test_supervisor_can_publish_if_worker_directory_disappears_before_exit(self):
        claim = example_claim('sin_directorio')
        command = [sys.executable, '-c', 'import shutil,sys;shutil.rmtree(sys.argv[1]);sys.exit(23)', str(self.job)]
        self.assertEqual(supervisor.supervise(self.git, self.job, claim, command), 0)
        self.assertFalse(self.job.exists())
        self.assertEqual(supervisor.recover(self.fresh_checkout(), claim)['receipt']['exit_code'], 23)

    def test_child_reaped_without_wait_status_is_not_an_exit_receipt(self):
        claim = example_claim('sin_estado_terminal')
        previous = signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        try:
            result = supervisor.supervise(self.git, self.job, claim, [sys.executable, '-c', 'pass'])
        finally:
            signal.signal(signal.SIGCHLD, previous)
        self.assertEqual(result, 2)
        self.assertFalse((self.job / 'SALIDA_OBSERVADA.json').exists())
        self.assertIsNone(supervisor.recover(self.git, claim))

    def test_worker_locks_are_insufficient_without_its_supervisor(self):
        claim = example_claim('sin_supervisor')
        flow = Flow(self.git, None, self.root, None, Timings(), dict(stages=[]))
        flow.job, flow.output = self.job, self.job / 'resultado'
        flow.worker_id = {'worker_id': claim['worker_id']}
        plan = SimpleNamespace(claim=claim, state={}, allocation=claim['allocation_id'],
                               registry_sha=claim['registry_sha256'],
                               origin={'sha256': claim['source_archive_sha256']})
        with patch.object(trabajador, 'live', return_value=True):
            self.assertFalse(flow.alive(plan, locks=True))
            flow.observe(plan)
            self.assertEqual(flow.report['worker']['status'], 'TRABAJADOR_SIN_SUPERVISION')
            with self.assertRaises(Stop) as stopped:
                flow.stop_for_exit_evidence()
            self.assertEqual(stopped.exception.detail['code'], 'SUPERVISION_PERDIDA')
            record(self.job / 'SUPERVISION_INICIADA.json',
                   dict(**supervisor.binding(claim), identity=trabajador.identity(os.getpid())))
            self.assertTrue(flow.alive(plan, locks=True))


if __name__ == '__main__':
    unittest.main()
