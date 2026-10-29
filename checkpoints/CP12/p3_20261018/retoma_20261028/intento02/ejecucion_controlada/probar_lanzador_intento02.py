"""Puertas de capacidad y permiso de un solo uso: fixtures, sin M2 ni red."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import retomar_intento02_con_transito as subject


def run():
    tests={}
    capacity=dict(schema='CP12_P3_TEMPORARY_TRANSIT_AND_GITHUB_CAPACITY_ACCEPTANCE_V1',passed=True,
                  capacity_probe=True,native_full_cycle_performed_in_this_invocation=True,
                  github_final_publication_verified=True,independently_extracted_zero_step_audits_passed=True,
                  source_archive_and_payload_unchanged=True,observer_clock=9.6,bytes=230000000,
                  transport_state_sha256=subject.SOURCE_TRANSPORT,M2_steps_executed=0)
    subject.capacity_gates(capacity);tests['complete_combined_capacity_gate_accepted']=True
    cases={'manual_only_recovery_rejected':{'schema':'CP12_GITHUB_RELEASE_TRANSPORT_ACCEPTANCE_V1'},
           'read_only_reconciliation_cannot_replace_full_native_cycle':{'native_full_cycle_performed_in_this_invocation':False},
           'missing_final_github_copy_rejected':{'github_final_publication_verified':False},
           'insufficient_capacity_rejected':{'bytes':229848115},
           'physical_steps_in_capacity_control_rejected':{'M2_steps_executed':1}}
    for name,change in cases.items():
        value=dict(capacity,**change)
        try:subject.capacity_gates(value)
        except ValueError:tests[name]=True
        else:tests[name]=False
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary);ticket=root/'execution.token';ticket.write_bytes(b'synthetic single-use fixture')
        allocation={'ticket_basename':ticket.name,'one_use_ticket_sha256':subject.sha(ticket)}
        subject.consume_ticket(ticket,allocation)
        tests['execution_permission_consumed_once']=not ticket.exists() and (root/'execution.token.consumido').is_file()
        ticket.write_bytes(b'synthetic single-use fixture')
        try:subject.consume_ticket(ticket,allocation)
        except FileExistsError:tests['recreated_private_ticket_cannot_run_same_allocation_twice']=ticket.exists()
        else:tests['recreated_private_ticket_cannot_run_same_allocation_twice']=False
        wrong=root/'wrong.token';wrong.write_bytes(b'different fixture')
        try:subject.consume_ticket(wrong,allocation)
        except ValueError:tests['wrong_ticket_identity_stops_before_consumption']=wrong.is_file()
        else:tests['wrong_ticket_identity_stops_before_consumption']=False
        linkroot=root/'links';linkroot.mkdir();link=linkroot/'execution.token';link.symlink_to(ticket)
        try:subject.consume_ticket(link,allocation)
        except ValueError:tests['symlink_cannot_reuse_execution_permission']=link.is_symlink()
        else:tests['symlink_cannot_reuse_execution_permission']=False
    report=dict(schema='CP12_P3_ADDITIONAL_BOUNDED_REPLAY_GUARDS_V1',passed=all(tests.values()),tests=tests,
                runner_sha256=subject.sha(Path(subject.__file__)),M2_steps_executed=0,
                real_network_or_credentials_used=False,scientific_data_used=False)
    print(json.dumps(report),flush=True)
    if not report['passed']:raise AssertionError('Bounded replay guard failure')


if __name__=='__main__':run()
