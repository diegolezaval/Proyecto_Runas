"""Recover published CP12 bytes and run the unchanged original auditor, zero M2 steps."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, sys, tempfile

os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def recover(boundary, work):
    source = BASE / f'tau{boundary:04d}'
    manifest = json.loads((source / 'MANIFIESTO_PUBLICO.json').read_text())
    assert manifest['time'] == boundary
    assert not work.exists(), 'Use a new, isolated destination'
    work.mkdir(parents=True)
    state = work / 'CP12_par_estado.npz'
    readable = source / 'numerical_text' / 'MANIFIESTO_TEXTUAL.json'
    if readable.exists():
        sys.path.insert(0, str(BASE))
        from recuperar_texto_numerico import recover as recover_readable
        recovery = recover_readable(readable.parent, ROOT, state)
        assert recovery['passed'] and recovery['exact_original_npz_bytes']
    else:
        with state.open('xb') as output:
            for chunk in manifest['state_chunks']:
                p = source / chunk['path']
                assert p.stat().st_size == chunk['bytes'] and sha(p) == chunk['sha256']
                output.write(p.read_bytes())
    assert state.stat().st_size == manifest['state_bytes']
    assert sha(state) == manifest['state_sha256']
    for name, record in manifest['companion_files'].items():
        p = source / name
        assert p.stat().st_size == record['bytes'] and sha(p) == record['sha256']
        shutil.copyfile(p, work / name)
    sys.path.insert(0, str(ROOT / 'herramientas'))
    import gestionar_respaldo_CP12 as original
    import ejecutar_con_procedencia as provenance
    _, case, identity, scientific_id = original.original_identity()
    assert identity == json.loads((BASE / 'IDENTIDAD_CIENTIFICA_ORIGINAL.json').read_text())
    assert len(identity['code_hashes']) == 14
    # This is a newly registered public recovery receipt, never a recreated
    # historical executor receipt. Only administrative provenance differs.
    receipt = dict(schema_version='1.0.0', run_id=scientific_id,
                   case='recuperacion_publica_sin_avance', identity=identity,
                   created_at=provenance.now(), status='PAUSADA_REANUDABLE',
                   segments=[], source_snapshots={},
                   configuration_sha256=sha(work / 'configuration.json'),
                   output_hashes={p.name: sha(p) for p in work.iterdir() if p.is_file()},
                   execution_origin=dict(kind='NEW_PUBLIC_SCIENTIFIC_RECOVERY',
                       original_lost_receipt_recreated=False,
                       historical_private_receipt_not_recreated=True,
                       physical_steps_executed=0,
                       original_protocol_unchanged=True))
    provenance.write(work / 'procedencia.json', receipt)
    # The original auditor enumerates controls beside RUN, so stage independent
    # copies of the six already published controls without changing their bytes.
    controls = sorted((ROOT / case['configuration']['control_directory']).glob('control_instrumentacion__*'))
    assert len(controls) == 6
    for control in controls:
        target = work.parent / control.name
        assert not target.exists()
        shutil.copytree(control, target)
    original.RUN = work
    report = original.audit(boundary)
    if not report['passed'] or not all(report['tests'].values()):
        raise ValueError(json.dumps(report, ensure_ascii=False))
    assert report['M2_steps_executed'] == 0
    assert report['state_sha256'] == manifest['state_sha256']
    report['public_recovery_receipt_is_new'] = True
    report['private_historical_receipt_reproduced'] = False
    report['CP12_closed'] = False
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--boundary', type=int, required=True)
    p.add_argument('--work-dir', type=Path)
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    if a.work_dir:
        result = recover(a.boundary, a.work_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='cp12_public_audit_') as d:
            result = recover(a.boundary, Path(d) / 'scientific_state')
    if a.report:
        assert not a.report.exists(), 'Never overwrite evidence'
        a.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
