"""Guarda y recupera una cápsula temporal en Biblioteca desde el propio proceso.

No ejecuta M2 ni publica en GitHub. Sólo acredita tránsito durable después de
descarga independiente, manifiesto completo y auditorías originales sin pasos.
La aceptación definitiva en GitHub se registra por separado antes de más física.
"""
import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPOSITORY = 'diegolezaval/Proyecto_Runas'
REGISTERED_ADAPTER = 'f4382caecef573f089c44b8871ab3307767da6be90835acbe0e109b4119ca41b'
REGISTERED_AUDITOR = '5ec8064cb2ef130b6796a296940a564d5c290e6f1000c4ca3ba2b0705f76aae0'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())


def unpack(value):
    for _ in range(12):
        if not isinstance(value, dict):
            break
        if isinstance(value.get('structuredContent'), dict):
            value = value['structuredContent']; continue
        if 'transfers' in value or 'results' in value:
            return value
        if isinstance(value.get('result'), dict):
            value = value['result']; continue
        content = value.get('content')
        if isinstance(content, list):
            content = '\n'.join(c['text'] for c in content if c.get('type') == 'text')
        if isinstance(content, str):
            try:
                value = json.loads(content); continue
            except json.JSONDecodeError:
                pass
        break
    return value


def helper(directory, name, arguments, payload, private):
    process = subprocess.run([sys.executable, str(directory / name), *arguments],
                             input=json.dumps(payload, ensure_ascii=False),
                             capture_output=True, text=True)
    (private / (name + '.stdout.txt')).write_text(process.stdout)
    (private / (name + '.stderr.txt')).write_text(process.stderr)
    if process.returncode:
        raise RuntimeError('El ayudante de transferencia no terminó; no se reintenta automáticamente')
    # La transferencia documentada puede responder texto; su código de salida,
    # los bytes descargados y las auditorías siguientes determinan la aceptación.
    if name != 'library_upload.py':
        return None
    raw = process.stdout
    if '\n{"results"' in raw:
        raw = raw[raw.rfind('\n{"results"'):].strip()
    return json.loads(raw) if raw.strip() else None


def validate_request(request_path):
    request = read(request_path)
    if request.get('schema') != 'CP12_GITHUB_RELEASE_ATTACHMENT_REQUEST_V1' or request.get('repository') != REPOSITORY:
        raise ValueError('Solicitud fuera del protocolo')
    if request.get('release_tag') != 'respaldo-cp12-p3-20261027':
        raise ValueError('Release distinta de la registrada')
    if request.get('observer_clock') not in (9.6, 11.2):
        raise ValueError('Fuera del tramo acotado autorizado')
    archive = Path(request['archive_path']).resolve()
    if archive.name != request['file_name'] or archive.stat().st_size != request['bytes'] or sha(archive) != request['sha256']:
        raise ValueError('Los bytes de origen no coinciden con su solicitud')
    adapter = Path(__file__).with_name('conservar_release.py')
    auditor = Path(__file__).with_name('auditar_recuperacion.py')
    if sha(adapter) != REGISTERED_ADAPTER or request['conservation_driver_sha256'] != REGISTERED_ADAPTER or sha(auditor) != REGISTERED_AUDITOR:
        raise ValueError('Adaptador o auditor distinto de los bytes registrados')
    return request, archive, auditor


def preserve(request_path, output, directory):
    request_path, output, directory = request_path.resolve(), output.resolve(), directory.resolve()
    request, archive, auditor = validate_request(request_path)
    output.mkdir(parents=True, exist_ok=False)
    private = output / 'privado'; private.mkdir(mode=0o700)
    report = dict(schema='CP12_P3_TEMPORARY_LIBRARY_TRANSIT_RECEIPT_V1',
                  started_at_utc=datetime.now(timezone.utc).isoformat(),
                  passed=False, uploaded=False, upload_outcome='not_started', independent_recovery_verified=False,
                  observer_clock=request['observer_clock'], file_name=archive.name,
                  bytes=request['bytes'], sha256=request['sha256'],
                  request_sha256=sha(request_path), transit_driver_sha256=sha(Path(__file__)),
                  temporary_transit_only=True, github_publication_verified=False,
                  further_physics_authorized=False, M2_steps_executed=0, CP12_closed=False,
                  correction_validated=False)
    stage = 'initial_validation'
    try:
        names = ['library_upload.py', 'library_hosted_apps.py', 'library_file_transfer.py']
        report['current_helper_sha256'] = {name:sha(directory / name) for name in names}
        stage = 'native_upload'
        report['upload_outcome'] = 'attempted_outcome_pending'
        uploaded = helper(directory, 'library_upload.py', [], {'uploads':[{
            'local_path':str(archive), 'purpose':'create_library_file',
            'library_artifact_type':'other'}]}, private)
        items = uploaded.get('results', [])
        if len(items) != 1 or items[0].get('status') != 'succeeded':
            raise RuntimeError('La escritura no fue acreditada; revisar el resultado sin repetirla')
        item = items[0]
        if item['file_name'] != archive.name or not item['library_file_id'] or not item['file_id']:
            raise ValueError('Identidad de la escritura inconsistente')
        report.update(uploaded=True, upload_outcome='confirmed', library_file_id=item['library_file_id'],
                      file_id=item['file_id'], library_file_name=item['file_name'])
        write_new(output / 'GUARDADO_DURABLE_PENDIENTE_AUDITORIA.json', report)
        print(json.dumps(dict(stage='uploaded', library_file_id=item['library_file_id'],
                             observer_clock=request['observer_clock'], further_physics_authorized=False)), flush=True)
        stage = 'independent_materialization'
        sys.path.insert(0, str(directory))
        from library_hosted_apps import HostedAppsClient
        destination = output / 'descarga_independiente'
        destination.mkdir()
        with (private / 'prepare_materialize.log').open('w') as log:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                response = HostedAppsClient().call_tool('connector_openai_library', 'prepare_materialize', {
                    'items':[{'file_id':item['file_id'], 'library_file_id':item['library_file_id'],
                              'file_name':item['file_name']}],
                    'destination':{'directory':str(destination)}})
        transfers = unpack(response)
        write_new(private / 'prepare_materialize.json', transfers)
        if len(transfers.get('transfers', [])) != 1 or transfers.get('unavailable_items'):
            raise ValueError('No se acreditó una descarga independiente única')
        transfer = transfers['transfers'][0]
        if transfer.get('workspace_path'):
            downloaded = Path(transfer['workspace_path']).resolve()
            if not downloaded.is_relative_to(destination) or downloaded == archive:
                raise ValueError('La recuperación debe estar en una raíz nueva independiente')
            helper(directory, 'library_file_transfer.py', ['apply-xattrs', str(downloaded)], transfer, private)
        else:
            downloaded = destination / archive.name
            helper(directory, 'library_file_transfer.py', ['materialize', str(downloaded)], transfer, private)
        if downloaded.stat().st_size != request['bytes'] or sha(downloaded) != request['sha256']:
            raise ValueError('La descarga no coincide con el archivo guardado')
        stage = 'original_zero_step_audits'
        process = subprocess.run([sys.executable, str(auditor), '--archivo', str(downloaded),
                                  '--sha256', request['sha256'], '--bytes', str(request['bytes']),
                                  '--home', str(output / 'extraido'), '--salida', str(output / 'auditoria')],
                                 capture_output=True, text=True)
        (output / 'auditor_stdout.txt').write_text(process.stdout)
        (output / 'auditor_stderr.txt').write_text(process.stderr)
        if process.returncode:
            raise RuntimeError('La recuperación no pasó los auditores originales')
        audit = read(output / 'auditoria/RESULTADO.json')
        transport = audit['audits']['transport']['audit']
        if not audit['passed'] or transport['state_sha256'] != request['transport_state_sha256'] or transport['observer_clock'] != request['observer_clock']:
            raise ValueError('El transporte recuperado no es el solicitado')
        source = Path(request['source_home'])
        for name, metadata in request['source_inventory'].items():
            if name == request['synthetic_ancestor_member']:
                continue
            path = source / name
            if path.stat().st_size != metadata['bytes'] or sha(path) != metadata['sha256']:
                raise ValueError('La fuente cambió durante la conservación')
        if sha(archive) != request['sha256']:
            raise ValueError('El ZIP de origen cambió')
        report.update(passed=True, independent_recovery_verified=True,
                      transport_state_sha256=transport['state_sha256'],
                      source_archive_and_payload_unchanged=True,
                      all_original_zero_step_audits_passed=True,
                      audit_receipt_sha256=sha(output / 'auditoria/RESULTADO.json'))
    except BaseException as error:
        if stage == 'native_upload' and not report['uploaded']:
            report['upload_outcome'] = 'unknown_requires_reconciliation'
        report.update(failed_stage=stage, error_type=type(error).__name__,
                      automatic_retry_permitted=False, further_physics_authorized=False)
        raise
    finally:
        report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        write_new(output / 'RESULTADO_TRANSITO.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solicitud', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--helpers', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = preserve(args.solicitud, args.salida, args.helpers)
    except BaseException as error:
        print(json.dumps(dict(passed=False, error_type=type(error).__name__,
                             automatic_retry_permitted=False, further_physics_authorized=False)), flush=True)
        return 1
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
