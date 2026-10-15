"""Recover one mixed trial capsule and run its captured zero-step auditor.

No evolution entrypoint is called. Use a new destination for every recovery.
The expected archive/state digests must come from a separate published proof.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(args):
    archive = args.capsule.resolve()
    assert archive.stat().st_size == args.bytes, 'Archive size differs'
    assert digest(archive) == args.zip_sha256, 'Archive SHA256 differs'
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert len(names) == len(set(names)), 'Duplicate ZIP entries'
        for item in zipped.infolist():
            path = Path(item.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert path.parts and not stat.S_ISLNK(item.external_attr >> 16)
        manifests = [n for n in names if n.endswith('/MANIFIESTO_RECUPERACION_INDEPENDIENTE.json')]
        assert len(manifests) == 1
        root_name = Path(manifests[0]).parts[0]
        assert all(Path(n).parts[0] == root_name for n in names)
        manifest = json.loads(zipped.read(manifests[0]))
        assert manifest['time'] == args.time
        assert manifest['schema'] == 'CP12_MIXTO_TRIAL_FULL_CAPSULE_NOT_CORRECTION_VALIDATION'
        expected_names = {root_name + '/' + name for name in manifest['files']}
        assert set(names) == expected_names | {manifests[0]}, 'Manifest coverage differs'
        for name, item in manifest['files'].items():
            payload = zipped.read(root_name + '/' + name)
            assert len(payload) == item['bytes'], name
            assert hashlib.sha256(payload).hexdigest() == item['sha256'], name
        zipped.extractall(destination)
    restored = destination / root_name
    state = restored / 'outputs/MIXTO_par_estado.npz'
    assert digest(state) == args.state_sha256
    identity = json.loads((restored / 'preregistration/nueva_identidad.json').read_text())
    public_root = args.public_sources.resolve()
    repository = public_root.parents[3]
    mapping = {
        'coordinator.py': public_root / 'coordinator.py',
        'preservation.py': public_root / 'preservation.py',
        'guardian.py': public_root / 'guardian.py',
        'configuration.json': public_root / 'configuration.json',
        'candidate/operador.py': repository / 'trazabilidad/CP12_recuperacion_independiente/ab914d1d0470/analysis/candidato_operador/operador.py',
        'candidate/backend.py': repository / 'trazabilidad/CP12_recuperacion_independiente/2f01ea6e32b2/analysis/backend_candidato/backend.py',
        'candidate/mixed_backend.py': public_root.parent / 'mixto_chi_prefLight_20261015/fase_A/mixed_backend.py',
        'preregistration/PRERREGISTRO.md': public_root / 'PRERREGISTRO.md',
        'preregistration/REGISTRO.json': public_root / 'REGISTRO.json',
        'preregistration/preflight_certificate.json': public_root.parent / 'mixto_chi_prefLight_20261015/CERTIFICADO_PREFLIGHT_A_D.json',
    }
    assert set(identity['captured_sources']) == set(mapping), 'Unexpected captured source set'
    for name, expected in identity['captured_sources'].items():
        assert digest(restored / name) == expected, name
        assert digest(mapping[name]) == expected, 'Published source differs: ' + name
    certificate = json.loads(mapping['preregistration/preflight_certificate.json'].read_text())
    assert certificate['passed'] and certificate['all_registered_preflight_controls_passed']
    assert certificate['mixed_backend_sha256'] == identity['captured_sources']['candidate/mixed_backend.py']
    runtime = restored / 'runtime'
    (runtime / 'tmp').mkdir(parents=True)
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       PYTHONPYCACHEPREFIX=str(runtime / 'pycache'), TMPDIR=str(runtime / 'tmp'))
    assert not environment.get('OPENBLAS_CORETYPE'), 'Forced BLAS dispatch forbidden'
    command = [sys.executable, str(restored / 'coordinator.py'), '--home', str(restored), '--audit-only', str(args.time)]
    process = subprocess.run(command, env=environment, text=True, capture_output=True)
    (destination / 'audit_stdout.json').write_text(process.stdout)
    (destination / 'audit_stderr.txt').write_text(process.stderr)
    assert process.returncode == 0, 'Captured zero-step auditor failed; inspect retained stderr'
    audit = json.loads(process.stdout)
    assert audit['passed'] and audit['time'] == args.time and audit['M2_steps_executed'] == 0
    assert all(audit['tests'].values())
    assert digest(state) == args.state_sha256 == audit['state_sha256']
    public_audit = {key: value for key, value in audit.items() if key not in ('run_id', 'execution_uuid', 'receipt_sha256')}
    report = dict(schema='CP12_MIXED_ADDITIONAL_INDEPENDENT_RECOVERY', time=args.time,
                  passed=True, zip_sha256=args.zip_sha256, zip_bytes=args.bytes,
                  state_sha256=args.state_sha256, exact_manifest_coverage=True,
                  payload_hashes_verified=len(manifest['files']),
                  captured_sources_match_published_registration=True,
                  preflight_A_to_D_reused_without_reexecution=True,
                  independent_zero_step_audit=public_audit,
                  M2_steps_executed=0, correction_validated=False, CP12_closed=False)
    (destination / 'RECUPERACION_INDEPENDIENTE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capsule', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--public-sources', type=Path, required=True)
    parser.add_argument('--time', type=int, required=True)
    parser.add_argument('--bytes', type=int, required=True)
    parser.add_argument('--zip-sha256', required=True)
    parser.add_argument('--state-sha256', required=True)
    print(json.dumps(verify(parser.parse_args()), ensure_ascii=False))


if __name__ == '__main__':
    main()
