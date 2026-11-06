"""Controles acotados de rutas y rotación; no carga kernels ni evoluciona M2."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import preservar as p


def refused(call):
    try:
        call()
    except (ValueError, RuntimeError, FileExistsError):
        return True
    return False


def item(clock):
    return dict(execution_uuid=p.UID, kind='transport', protected=False, verified=True,
                observer_clock=clock, library_file_id='SYNTHETIC_' + str(clock),
                file_id='SYNTHETIC_FILE_' + str(clock), sha256='SYNTHETIC', bytes=1)


def receipt(clock):
    audit = lambda n: dict(passed=True, tests={str(i): True for i in range(n)},
                           M2_steps_executed=0, DOP853_construction_or_step_attempts=0)
    transport = dict(audit(14), observer_clock=clock)
    return dict(passed=True, observer_clock=clock, library_file_id='SYNTHETIC_' + str(clock),
        file_id='SYNTHETIC_FILE_' + str(clock), file_name='SYNTHETIC.zip', sha256='SYNTHETIC', bytes=1,
        recovery=dict(passed=True, exact_manifest_coverage=True,
            all_payload_hashes_verified_before_and_after=True,
            original_audits=dict(boundary=audit(30), transport=transport)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    tests = {}
    here = Path(__file__).resolve().parent
    tests['preserver_base_exact_original_bytes'] = (
        p.sha(here / 'base_preservar.py') == p.sha(args.original / 'preservar.py') ==
        '3aafd0b8157d2f6f9f4140db35f95163e385dda962762cdc8aeaa09fbd98b0fe')
    for name in ('prepare', 'audit', 'native', 'recover', 'public', 'unchanged'):
        tests['original_' + name + '_function_reused'] = getattr(p, name) is getattr(p.original, name)
    old = ast.parse((args.original / 'continuar.py').read_text())
    new = ast.parse((here / 'continuar.py').read_text())
    class RemoveAdministrativeCalls(ast.NodeTransformer):
        def visit_Expr(self, node):
            call = node.value
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and
                    isinstance(call.func.value, ast.Name) and call.func.value.id == 'p' and
                    call.func.attr in ('validate_hybrid_registry', 'initialize_rotation', 'retire_at_boundary')):
                return None
            return self.generic_visit(node)
    tests['runner_only_three_registered_administrative_calls_added'] = (
        ast.dump(old) == ast.dump(RemoveAdministrativeCalls().visit(new)))
    names = ('restore', 'activate', 'metrics')
    for name in names:
        select = lambda tree: next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == name)
        tests['exact_original_' + name + '_body'] = ast.dump(select(old)) == ast.dump(select(new))
    reg = dict(closed_boundary=24, clock=24, hybrid_policy_sha256=p.sha(here / 'POLITICA.json'))
    p.validate_hybrid_registry(reg)
    tests['old_segment_refused'] = refused(lambda: p.validate_hybrid_registry(dict(reg, closed_boundary=16)))
    tests['unregistered_policy_refused'] = refused(lambda: p.validate_hybrid_registry(dict(reg, hybrid_policy_sha256='wrong')))
    prior = [item(25.6), item(27.2)]
    tests['last_two_retained'] = p.rotation_plan(prior) == []
    tests['only_oldest_of_three_selected'] = p.rotation_plan(prior + [item(28.8)]) == prior[:1]
    tests['protected_negative_refused'] = refused(lambda: p.rotation_plan([dict(item(25.6), kind='negative')]))
    tests['foreign_execution_refused'] = refused(lambda: p.rotation_plan([dict(item(25.6), execution_uuid='OTHER')]))
    tests['duplicate_identity_refused'] = refused(lambda: p.rotation_plan([item(25.6), item(25.6)]))
    for field in ('passed', 'exact_manifest_coverage', 'all_payload_hashes_verified_before_and_after'):
        r = receipt(28.8)
        r['recovery'][field] = False
        tests['failed_' + field + '_refused_before_rotation'] = refused(lambda: p.validate_native(r, 28.8))
    r = receipt(28.8)
    r['recovery']['original_audits']['transport']['DOP853_construction_or_step_attempts'] = 1
    tests['evolving_audit_refused'] = refused(lambda: p.validate_native(r, 28.8))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        home = root / 'home'
        (home / 'runtime').mkdir(parents=True)
        (home / 'administracion_continuacion_20261030').mkdir()
        ring_path = home / 'runtime/HIBRIDO_ROTACION.json'
        ring = dict(schema=p.POLICY, execution_uuid=p.UID, retained=copy.deepcopy(prior), retirements=[])
        p.atomic_record(ring_path, ring)
        before = ring_path.read_bytes()
        with patch.object(p, 'prepare', return_value={}), patch.object(p, 'native', side_effect=RuntimeError('synthetic save failure')), patch.object(p, 'record_transport') as rotation:
            tests['failed_save_keeps_previous_backups_and_never_rotates'] = (
                refused(lambda: p.preserve(home, root / 'failed', 'SYNTHETIC', 'transport', 28.8, 24, root, root)) and
                ring_path.read_bytes() == before and not rotation.called)
        with patch.object(p, 'prepare', return_value={}), patch.object(p, 'native', return_value=receipt(28.8)), patch.object(p, 'record_transport', return_value={'retained': prior}) as rotation, patch.object(p.original, 'preserve') as public_route:
            output = root / 'native_only'
            output.mkdir()
            saved = p.preserve(home, output, 'SYNTHETIC', 'transport', 28.8, 24, root, root)
            tests['intermediate_transport_uses_native_recovery_only'] = (
                saved['passed'] and saved['github_required'] is False and rotation.called and not public_route.called)
        for kind, capacity in [('boundary', False), ('negative', False), ('transport', True)]:
            with patch.object(p.original, 'preserve', return_value='DUAL') as dual:
                tests[kind + ('_capacity' if capacity else '') + '_keeps_public_recovery'] = (
                    p.preserve(home, root / kind, 'SYNTHETIC', kind, 32, 24, root, root, capacity) == 'DUAL' and dual.called)
        removed = []
        class Client:
            def call_tool(self, app, name, value):
                latest = p.read(ring_path)
                assert latest['retained'][-2:] == [item(27.2), dict(item(28.8), file_name='SYNTHETIC.zip')]
                assert latest['retirements'][-1]['status'] == 'pending_no_automatic_retry'
                removed.extend(value['operations'])
                return {'structuredContent': {'results': [{'status': 'succeeded'}]}}
        after = p.record_transport(home, receipt(28.8), root, Client)
        tests['rotation_after_verified_new_save_keeps_two_and_records_replacement'] = (
            len(after['retained']) == 2 and len(removed) == 1 and
            removed[0]['target']['library_file_id'] == prior[0]['library_file_id'] and
            after['retirements'][-1]['status'] == 'trashed' and
            after['retirements'][-1]['replacement']['identities'] == [x['library_file_id'] for x in after['retained']])
        tests['negative_boundary_cannot_trigger_cleanup'] = refused(lambda: p.retire_at_boundary(
            home, {}, dict(prefix_pair_limits_met=False, prefix_physical_controls_met=True), root))
    result = dict(schema='CP12_P3_HYBRID_BOUNDED_ADMIN_TESTS_V1', passed=all(tests.values()), tests=tests,
        test_count=len(tests), synthetic=True, remote_mutations_executed=0, M2_steps_executed=0,
        DOP853_construction_or_step_attempts=0, CP12_closed=False,
        scope='Rutas, identidad del código numérico, fallo de guardado y rotación;no sustituye capacidad del proceso real.')
    p.write(args.salida, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
