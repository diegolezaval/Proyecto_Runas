"""Keep unmaterialized ancestral cleanup receipts outside the live queue."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(home):
    own_start = json.loads((home/'runtime/worker_observed_start.json').read_text())['at']
    started = datetime.datetime.fromisoformat(own_start).timestamp()
    source = home/'preregistration/administracion_transferencias/limpiar_transferencias.py'
    before = {str(p.relative_to(home)): sha(p) for p in [source, home/'configuration.json']}
    selected = []
    for path in (home/'preregistration/limpieza_transferencias').glob('*.json'):
        record = json.loads(path.read_text())
        pending = [e for e in record['entries'] if e['status'] == 'QUARANTINED']
        if not pending or all((home/'runtime/transfer_cleanup_quarantine'/e['quarantine_name']).is_file() for e in pending):
            continue
        assert record['at_seconds'] < started, 'Current-session missing file: do not reinterpret'
        assert all(not (home/'runtime/transfer_cleanup_quarantine'/e['quarantine_name']).exists() for e in pending)
        assert record['scope'] == 'Only old invalid ZIP transfer copies; no canonical file, negative or valid NPZ selected'
        assert record['M2_steps_executed'] == 0
        selected.append((path, sha(path), path.stat().st_size))
    assert selected, 'No ancestral-only mismatch identified'
    target = home/'ancestor/limpieza_transferencias_no_materializadas_recuperacion70p4'
    target.mkdir(exist_ok=False)
    destination = home/'preregistration/recuperacion_tau70p4/SEPARACION_REGISTROS_CUARENTENA.json'
    record = dict(schema='CP12_ANCESTRAL_DISPOSABLE_TRANSFER_RECEIPTS_RETAINED_OUTSIDE_LIVE_SESSION_QUEUE',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), own_started_at=own_start,
        preexisting_missing_disposable_copy_records_detected_before_cleaner_start=True,
        source_cleanup_helper_sha256=before[str(source.relative_to(home))],
        selection='Only pre-session quarantine receipts whose disposable runtime copies were not materialized',
        scientific_gate_failed=False, science_or_canonical_state_mutated=False,
        administrative_procedure_M2_steps=0, physical_worker_continues_independently=True,
        older_executor_termination_assumed=False, CP12_closed=False, moves=[])
    destination.write_text(json.dumps(record,indent=2)+'\n')
    for path, digest, size in selected:
        archived = target/path.name
        assert sha(path) == digest and path.stat().st_size == size
        path.rename(archived)
        assert sha(archived) == digest and archived.stat().st_size == size
        record['moves'].append(dict(original=str(path.relative_to(home)),
            preserved_as=str(archived.relative_to(home)),sha256=digest,bytes=size,bytes_identical=True))
        destination.write_text(json.dumps(record,indent=2)+'\n')
    assert before == {name:sha(home/name) for name in before}
    record['cleanup_source_and_configuration_unchanged'] = True
    destination.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--home',type=Path,required=True)
    run(parser.parse_args().home.resolve())
