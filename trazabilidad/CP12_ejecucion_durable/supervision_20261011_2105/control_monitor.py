"""Synthetic activity regression only: no M2, backup certification or upload."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
EXPECTED_BASELINE = 'a81957a7f3a9a8888cef936d1c5a0811dec5da0a299e791cae6febc97e92060d'


def load(name, source):
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert hashlib.sha256(args.baseline.read_bytes()).hexdigest() == EXPECTED_BASELINE
    source = ROOT/'trazabilidad/CP12_reconstruccion/actividad_ejecutor.py'
    previous, current = load('baseline_monitor', args.baseline), load('current_monitor', source)
    boot = hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes()).hexdigest()
    other_boot = '0'*64 if boot != '0'*64 else '1'*64
    pid, ticks = 424242, '123456'
    results = {}
    with tempfile.TemporaryDirectory(prefix='cp12_synthetic_activity_') as temporary:
        fixture = Path(temporary)
        proof = fixture/'trazabilidad/CP12_reconstruccion/respaldos/tau0000.json'
        proof.parent.mkdir(parents=True)
        proof.write_text(json.dumps(dict(schema='SYNTHETIC_NOT_A_SCIENTIFIC_BACKUP',
            passed=True, time=-1, zip_sha256='SYNTHETIC', state_sha256='SYNTHETIC',
            download_verification=dict(passed=True))))
        log = fixture/'synthetic.log'
        log.write_text('')
        previous.ROOT = current.ROOT = fixture
        coordinator = dict(start_ticks=ticks, parent_pid=1,
            command=str(fixture/'trazabilidad/CP12_reconstruccion/continuacion_raiz_20261010.py'))
        with patch.object(previous, 'process_identity', return_value=None):
            old = previous.observe(pid, ticks, 'SYNTHETIC', log)
        results['baseline_without_boot_guard_falsely_reports_inactivity'] = (
            old['status'] == 'INACTIVE_OBSERVED_ON_ORIGINAL_EXECUTOR' and old['active'] is False)
        with patch.object(current, 'process_identity', return_value=None):
            wrong = current.observe(pid, ticks, 'SYNTHETIC', log, other_boot)
            same = current.observe(pid, ticks, 'SYNTHETIC', log, boot)
        results['different_boot_no_process_is_unknown'] = (
            wrong['status'] == 'UNKNOWN_ACTIVITY' and wrong['active'] is None and
            not wrong['activity_known'] and not wrong['original_executor_matches'])
        results['same_boot_complete_empty_query_can_observe_inactivity'] = (
            same['status'] == 'INACTIVE_OBSERVED_ON_ORIGINAL_EXECUTOR' and same['active'] is False)
        def with_coordinator(value):
            return coordinator if value == pid else None
        with patch.object(current, 'process_identity', side_effect=with_coordinator):
            reused = current.observe(pid, ticks, 'SYNTHETIC', log, other_boot)
            active = current.observe(pid, ticks, 'SYNTHETIC', log, boot)
        results['different_boot_reused_pid_is_unknown'] = (
            reused['status'] == 'UNKNOWN_ACTIVITY' and reused['active'] is None and
            not reused['coordinator_identity_matches'])
        results['same_boot_matching_coordinator_is_active'] = (
            active['status'] == 'ACTIVE' and active['active'] is True and
            active['coordinator_identity_matches'])
        local_pid = next(int(p.name) for p in Path('/proc').iterdir()
                         if p.name.isdecimal() and int(p.name) != pid)
        def forbidden(value):
            if value == local_pid:
                raise PermissionError('SYNTHETIC_PERMISSION_ERROR')
            return None
        with patch.object(current, 'process_identity', side_effect=forbidden):
            uncertain = current.observe(pid, ticks, 'SYNTHETIC', log, boot)
        results['same_boot_incomplete_query_is_unknown'] = (
            uncertain['status'] == 'UNKNOWN_ACTIVITY' and uncertain['active'] is None)
        orphan = dict(start_ticks='1', parent_pid=1,
            command=str(fixture/'trazabilidad/CP12_reconstruccion/orquestador_respaldos.py'))
        with patch.object(current, 'process_identity',
                          side_effect=lambda value: orphan if value == local_pid else None):
            pipeline = current.observe(pid, ticks, 'SYNTHETIC', log, boot)
        results['same_boot_orphan_pipeline_still_blocks_duplicates'] = (
            pipeline['status'] == 'ACTIVE' and pipeline['active'] is True and
            not pipeline['coordinator_identity_matches'] and bool(pipeline['pipeline_processes']))
    report = dict(schema='CP12_SYNTHETIC_ACTIVITY_REGRESSION_NOT_SCIENTIFIC_EVIDENCE',
        checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        baseline_commit='43b51cc419897783f3111586b16dfc76875f1c61',
        baseline_sha256=EXPECTED_BASELINE, passed=all(results.values()), tests=results,
        M2_steps_executed=0, physics_or_observer_changed=False,
        certifies_original_executor_inactivity=False, certifies_a_boundary=False)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
