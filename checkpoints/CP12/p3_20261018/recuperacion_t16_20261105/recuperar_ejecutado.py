"""Reconcile an existing frontier; original byte, zero-step and metric readers only."""
from pathlib import Path
import importlib.util
import json
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / 'Proyecto_Runas'
OUT = ROOT / 'cierre16'
sys.path.insert(0, str(REPO / 'checkpoints/CP12/p3_20261018/continuidad_20261030/ejecutor'))
import preservar as p
import continuar as c

def load(name, file):
    spec=importlib.util.spec_from_file_location(name,file)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    if sys.flags.optimize or os.environ.get('OPENBLAS_CORETYPE'):
        raise ValueError('Disabled assertions or forced BLAS architecture')
    auditor=REPO/'checkpoints/CP12/p3_20261018/retoma_20261028/auditar_recuperacion.py'
    if p.sha(auditor)!='5ec8064cb2ef130b6796a296940a564d5c290e6f1000c4ca3ba2b0705f76aae0':
        raise ValueError('Original unpacker changed')
    unpacker=load('pinned_unpacker',auditor)
    asset=p.read(OUT/'ASSET_GITHUB.json')
    archive=ROOT/'native16'/asset['name']
    expected='9627950c47e52280df00b5aab8e75358f653d4807c85db32e1b1cedcafabca12'
    home=OUT/'nativo_extraido'
    manifest=unpacker.unpack(archive,home,expected,230213899)
    if manifest['kind']!='boundary' or manifest['closed_boundary']!=16 or manifest['observer_clock']!=16:
        raise ValueError('Not the recorded frontier')
    print(json.dumps({'stage':'native_unpacked','payloads':len(manifest['files'])}),flush=True)
    audits=p.audit(home,'boundary',16,OUT/'auditoria_nativa')
    request=dict(schema='CP12_P3_EXISTING_FRONTIER_RECONCILIATION_V1',repository=p.REPO,release_tag=p.TAG,
        kind='boundary',observer_clock=16,closed_boundary=16,capacity_probe=False,
        source_home=str(home),archive_path=str(archive),file_name=archive.name,
        bytes=230213899,sha256=expected,source_inventory=manifest['files'],
        archive_inventory=manifest['files'],local_audits=audits,
        M2_steps_executed_during_preservation=0,CP12_closed=False)
    p.unchanged(request)
    p.write(OUT/'RECUPERACION_NATIVA.json',dict(passed=True,library_file_id='libfile_bb187e2e145c81918cf7b7b1e20cac45',
        file_id='file_00000000973881f98409c1f7634034e5',sha256=expected,bytes=230213899,
        independently_materialized_in_current_process=True,payload_files=len(manifest['files']),
        all_payload_hashes_verified_before_and_after=True,original_audits=audits,
        original_worker_native_full_cycle_not_reconstructed=True,M2_steps_executed=0,CP12_closed=False))
    p.write(OUT/'SOLICITUD_RECONCILIADA.json',request)
    print(json.dumps({'stage':'native_audited','tests':len(audits['boundary']['tests'])}),flush=True)
    public=p.public(request,asset,OUT/'github',auditor)
    print(json.dumps({'stage':'public_audited','asset':public['github_asset_id']}),flush=True)
    decision=c.metrics({'github':public},OUT,16)
    p.unchanged(request)
    for name,meta in manifest['files'].items():
        file=Path(public['recovery']['recovered_home'])/name
        if file.stat().st_size!=meta['bytes'] or p.sha(file)!=meta['sha256']:
            raise ValueError('Public payload changed during metrics: '+name)
    positive=decision['prefix_pair_limits_met'] and decision['prefix_physical_controls_met']
    p.write(OUT/'RESULTADO.json',dict(schema='CP12_P3_EXISTING_FRONTIER_RECONCILED',passed=positive,
        time=16,comparison=decision['comparison'],all_original_prefix_gates_passed=positive,
        public_capsule_asset=public['github_asset_id'],all_payload_hashes_verified_after_metrics=True,
        current_process_M2_steps_executed=0,prior_worker_exit_observed=False,
        prior_worker_reactivated=False,prior_private_publication_file_recreated=False,
        next_physical_interval_executed=False,CP12_closed=False,correction_validated=False))
    if not positive:
        p.write(OUT/'SUSPENSION.json',dict(time=16,scientific_gate_failed=True,
            automatic_new_candidate_authorized=False,next_physical_interval_authorized=False,CP12_closed=False))
    print(json.dumps({'stage':'frontier_decision','passed':positive,'comparison':decision['comparison']}),flush=True)
    return 0 if positive else 2

if __name__=='__main__':
    raise SystemExit(main())
