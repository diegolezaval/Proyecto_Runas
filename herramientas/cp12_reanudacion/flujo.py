"""Orquestación P3 hasta la evidencia del primer avance físico."""

from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import zipfile

from . import trabajador
from .evidencia import checked_audits, first_step, historical_chain, resolve, unpublished, zero
from .infra import (BRANCH, CLAIM, COMPARE, HYBRID, PREFIX, REPO, STATE, TAG, Stop,
                    digest, encoded, find_asset, install, library_item, now, optional, record, require, sha)
from .preparacion import audit_archive, environment, log_command, payloads, restore_exact, runner, snapshots, worker_args


def pending_public(destinations, assets, request, journal, approval=None):
    """Encontrar primero una subida ya hecha. Una intención incierta no se repite."""
    archive = Path(request['archive_path'])
    label = f'https://github.com/{REPO}/releases/tag/{TAG}'
    found = find_asset(assets, request)
    if found:
        return found
    if journal.exists():
        raise Stop('SUBIDA_INCIERTA', 'Hay intención previa y todavía no se recupera el adjunto exacto',
                   'Reconciliar la subida en la Release y volver a ejecutar retomar',
                   file=str(archive), destination=label)
    if approval != request['sha256']:
        raise Stop('APROBACION_PUBLICA', 'El control exacto requiere aprobación explícita',
                   f'Autorizar y volver a ejecutar retomar --aprobar-publicacion {request["sha256"]}, '
                   'o subir el archivo exacto y volver a ejecutar retomar',
                   file=str(archive), destination=label)
    destinations.check(archive, request)
    record(journal, dict(at=now(), archive=str(archive), sha256=request['sha256'], destination=label), once=True)
    try:
        destinations.upload(archive)
    except (OSError, subprocess.TimeoutExpired):
        pass  # Buscar el adjunto antes de decidir que no hubo escritura.
    found = find_asset(destinations.assets(), request)
    if found:
        return found
    raise Stop('SUBIDA_NO_ACREDITADA', 'GitHub no confirmó la subida exacta',
               'Comprobar la aprobación y la credencial de GitHub, reconciliar el adjunto y repetir retomar',
               file=str(archive), destination=label)


class Flow:
    def __init__(self, git, destinations, work, helpers, timings, report, *, seconds=60, approval=None):
        self.git, self.destinations, self.work, self.helpers = git, destinations, work, helpers
        self.report, self.timings, self.seconds, self.approval = report, timings, seconds, approval
        self.deadline = time.monotonic()

    def stage(self, name, **detail):
        self.report['last_stage'] = name
        self.report['stages'].append(dict(name=name, at=now(), **detail))

    def wait(self, condition, name):
        with self.timings.measure('espera', name):
            while True:
                try:
                    value = condition()
                except json.JSONDecodeError:
                    # Los recibos de los ejecutores históricos pueden estar escribiéndose.
                    value = None
                if value or time.monotonic() >= self.deadline:
                    return value
                time.sleep(.25)

    def fresh(self, plan, *, inventory=False):
        with self.timings.measure('consulta', 'HEAD científico'):
            require(self.git.head() == plan.head, 'La rama científica cambió durante la operación')
        if not inventory:
            return None
        assets, library = self.destinations.assets(), self.destinations.library(max_age=60)
        self.destinations_present(plan, assets, library)
        self.pending_origin(plan, assets, library)
        return assets, library

    @staticmethod
    def destinations_present(plan, assets, library):
        public = find_asset(assets, plan.frontier)
        require(public and public['id'] == plan.frontier['github_asset_id'], 'Adjunto de frontera ausente o distinto')
        if plan.origin['kind'] == 'transport':
            library_item(library, plan.origin)
        return public

    def pending_origin(self, plan, assets, library):
        pending = unpublished(plan, assets, library)
        if pending:
            self.report['pending_origin'] = pending
            raise Stop('ORIGEN_PENDIENTE', 'Hay un respaldo o incidente más reciente sin recibo conciliado',
                       'Recuperar y auditar este objeto, registrar su identidad exacta en la rama y repetir',
                       file=pending['file'], destination=pending['destination'])

    def run(self, mode, historical=None):
        with self.timings.measure('consulta', 'HEAD científico'):
            head = self.git.pin(historical) if historical else self.git.head()
        plan = resolve(self.git, head)
        self.report.update(head=head, allocation=plan.allocation, origin=plan.origin, frontier=plan.frontier,
                           next_action=plan.state['next_recovery'])
        self.stage('ORIGEN_RESUELTO', recovery_proof=plan.origin.get('recovery_receipt', plan.frontier['certificate']))
        self.job = self.work / 'asignaciones' / (plan.allocation + '-' + plan.registry_sha)
        self.output = self.job / 'resultado'
        self.worker_id = optional(self.job / 'INTENCION.json')
        self.observe(plan)
        assets, library = self.destinations.assets(), self.destinations.library()
        asset = self.destinations_present(plan, assets, library)
        if not historical:
            self.pending_origin(plan, assets, library)

        if not plan.assignment_matches():
            raise Stop('ASIGNACION_DESFASADA', 'El mejor respaldo carece de asignación correspondiente',
                       'Registrar una asignación nueva desde el origen acreditado',
                       file=plan.registry_path, destination=BRANCH)

        self.code = snapshots(self.git, plan, self.work, self.helpers, historical=bool(historical))
        self.env, self.fingerprint = environment(self.git, plan, self.destinations, assets, self.work)
        self.report['environment'] = self.fingerprint
        self.reference = self.destinations.archive(plan.frontier, public=asset)
        self.home, public_audit = self.audit(plan.frontier, self.reference)
        self.stage('FRONTERA_AUDITADA', receipt=public_audit)
        origin_audit = public_audit
        if plan.origin['kind'] == 'transport':
            origin_archive = self.destinations.archive(plan.origin)
            self.home, origin_audit = self.audit(plan.origin, origin_archive)
            self.stage('TRANSPORTE_AUDITADO', receipt=origin_audit)
        else:
            origin_archive = self.reference
        self.origin_archive = origin_archive
        exact = restore_exact(plan, self.home, self.reference, self.code, self.helpers, self.work, self.env,
                              self.fingerprint, self.timings)
        self.stage('RESTAURACION_EXACTA', frontier_audit=public_audit, origin_audit=origin_audit, restore=exact)
        if historical:
            chain = historical_chain(self.git, plan)
            if chain:
                self.stage('INICIO_HISTORICO_ACREDITADO', receipts=chain)
            self.report['next_action'] = 'Usar el HEAD vigente para una retoma real'
            return 'VERIFICADO_HISTORICO'
        if plan.blocked:
            self.prior_block(plan, assets, library)
        if self.report['worker']['status'] in ('TRABAJADOR_AJENO_ACTIVO', 'SESION_INACCESIBLE_SIN_SALIDA'):
            raise Stop('TRABAJADOR_EXISTENTE', 'Hay un trabajador registrado ajeno a este directorio de operación',
                       'Verificar la sesión y ambos locks. Si se perdió, acreditar su aislamiento y registrar '
                       'una asignación nueva desde el respaldo recuperable',
                       file=plan.registry_path, destination=BRANCH)
        if plan.state.get('own_observed_start'):
            self.stage('INICIO_FISICO_ACREDITADO', receipts=historical_chain(self.git, plan))
            return 'INICIO_ACREDITADO'
        if mode == 'verificar':
            self.report['next_action'] = 'Ejecutar retomar con el mismo directorio de trabajo'
            return ('TRABAJADOR_ACTIVO' if self.report['worker']['status'] == 'TRABAJADOR_PROPIO_ACTIVO'
                    else 'PLAN_LISTO')

        self.deadline = time.monotonic() + self.seconds
        return self.resume(plan, assets, library)

    def audit(self, spec, archive, *, capacity=False):
        return audit_archive(spec, archive, self.code, self.work, self.env, self.fingerprint,
                             self.timings, capacity=capacity)

    def observe(self, plan):
        guardian = plan.state.get('own_guardian_tool_session_id')
        worker = dict(status='SIN_TRABAJADOR_REGISTRADO', session=guardian,
                      exit_observed=plan.state.get('own_exit_observed') is True,
                      heartbeat_is_restart=False)
        claim = plan.claim
        if claim and claim['allocation_id'] != plan.allocation:
            isolation_path = plan.registry.get('isolation')
            isolated = self.git.json(plan.head, isolation_path) if isolation_path else {}
            require(isolated.get('allocation_id', isolated.get('previous_allocation')) == claim['allocation_id'] and
                    (isolated.get('process_exit_observed') is True or
                     isolated.get('local_worker_locks_observed_free') is True and
                     isolated.get('prior_assignment_reactivation_prohibited') is True),
                    'La intención anterior sigue vigente y requiere aislamiento o salida acreditada')
            previous = self.work / 'asignaciones' / (claim['allocation_id'] + '-' + claim['registry_sha256'])
            require(not trabajador.live(previous, claim['worker_id'], claim['registry_sha256']),
                    'El trabajador anterior sigue activo pese al recibo de aislamiento')
        if claim and claim['allocation_id'] == plan.allocation:
            require(claim['registry_sha256'] == plan.registry_sha and
                    claim['source_archive_sha256'] == plan.origin['sha256'],
                    'La intención registrada corresponde a otro origen o versión de la asignación')
            if not self.worker_id or claim['worker_id'] != self.worker_id['worker_id']:
                worker['status'] = 'SESION_INACCESIBLE_SIN_SALIDA'
            else:
                live = self.alive(plan)
                exited = optional(self.job / 'SALIDA_OBSERVADA.json')
                worker.update(status='TRABAJADOR_PROPIO_ACTIVO' if live else (
                    'SALIDA_OBSERVADA' if exited else 'INTENCION_PROPIA_SIN_SALIDA'),
                    exit_observed=bool(exited), exit=exited,
                    heartbeat=optional(self.output / 'HEARTBEAT.json'))
        elif guardian is not None and not worker['exit_observed']:
            home = plan.state.get('own_attempt_home')
            active = home and trabajador.lock_owner(Path(home) / 'runtime/worker.lock')
            worker['status'] = 'TRABAJADOR_AJENO_ACTIVO' if active else 'SESION_INACCESIBLE_SIN_SALIDA'
        self.report['worker'] = worker

    def prior_block(self, plan, assets, library):
        block = plan.blocked
        spec = dict(file_name=block['exact_requested_file_name'], bytes=block['bytes'], sha256=block['sha256'])
        found = find_asset(assets, spec)
        self.report['pending_publication'] = dict(spec, asset_id=found['id'] if found else None,
                                                  prior_block=plan.state['active_publication_block'])
        native_path = block['independent_native_capacity']
        self.check_native(plan, self.git.json(plan.head, native_path), library)
        self.stage('CAPACIDAD_NATIVA_REGISTRADA', receipt=native_path)
        if found:
            self.recover_public(plan, spec, found)
        action = ('Verificar la sesión y entregar al mismo proceso el adjunto exacto ya existente para su '
                  'recuperación independiente, o aislar la asignación si la sesión se perdió') if found else (
                  'Comprobar si la sesión sigue accesible. Si sigue, obtener aprobación explícita '
                  'para el adjunto exacto. Si se perdió, registrar su aislamiento y una asignación nueva')
        raise Stop('PUBLICACION_PREVIA', block['auto_review_reason'], action, file=spec['file_name'],
                   destination=f'https://github.com/{REPO}/releases/tag/{TAG}')

    def alive(self, plan, *, locks=False):
        return trabajador.live(self.job, self.worker_id['worker_id'], plan.registry_sha, locks=locks)

    def publish(self, plan, files, message):
        # publish comprueba el padre y relee cada byte desde el ref remoto.
        with self.timings.measure('consulta', message):
            return self.git.publish(plan.head, files, message)

    def published_plan(self, previous, commit):
        head = self.git.head()
        if head != commit:
            raise Stop('RAMA_CAMBIO', 'Se publicó el recibo y la rama volvió a avanzar',
                       'Reejecutar retomar para comprobar el nuevo HEAD', chat=False)
        plan = resolve(self.git, head)
        require(plan.registry_sha == previous.registry_sha and plan.origin == previous.origin,
                'Cambió la identidad del origen o de la asignación')
        return plan

    def launch(self, plan):
        worker_id = self.worker_id
        claim = plan.claim
        if not worker_id:
            worker_id = self.worker_id = record(self.job / 'INTENCION.json',
                                                dict(worker_id=uuid.uuid4().hex, at=now(), head=plan.head), once=True)
        worker = dict(schema='CP12_REANUDADOR_WORKER_V1', allocation_id=plan.allocation,
                      worker_id=worker_id['worker_id'], registry_sha256=plan.registry_sha,
                      source_archive_sha256=plan.origin['sha256'], at=worker_id['at'])
        _, library = self.fresh(plan, inventory=True)
        label = ('CONTROL_NATIVO_' if plan.registry['kind'] == 'transport' else 'CONTROL_') + plan.allocation.upper()
        name = PREFIX + label + '.zip'
        if any(item['name'] == name for item in library):
            raise Stop('CONTROL_NATIVO_PREEXISTENTE', 'La asignación ya tiene un control nativo en Biblioteca',
                       'Reconciliar su proceso y recibos. Si se perdió, aislarlo y registrar otra asignación',
                       file=name, destination='Biblioteca')
        if not claim or claim['allocation_id'] != plan.allocation:
            # Es una intención exclusiva de preparar el proceso. La reserva va después de la capacidad.
            commit = self.publish(plan, {CLAIM: encoded(worker)}, 'CP12/P3: fijar intención exclusiva de trabajador')
            plan = self.published_plan(plan, commit)
        require(plan.claim == worker, 'La intención Git pertenece a otro trabajador')
        require(not (self.job / 'PROCESO.json').exists() and not self.output.exists(),
                'El directorio ya contiene un trabajador o sus resultados')
        if not (self.job / 'home').exists():
            temp = self.job / ('home-preparar-' + uuid.uuid4().hex)
            with zipfile.ZipFile(self.origin_archive) as zipped:
                manifest = json.loads(zipped.read('MANIFIESTO_NEGATIVO.json'))
            for name in (*manifest['files'], 'MANIFIESTO_NEGATIVO.json'):
                target = temp / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.home / name, target)
            payloads(temp, manifest)
            temp.rename(self.job / 'home')
        self.fresh(plan)
        registry = self.job / 'REGISTRO.json'
        install(registry, plan.registry_bytes, once=True)
        flags = worker_args(self.job / 'home', registry, self.helpers, self.code, self.output,
                            self.reference, plan.registry)
        command = [str(runner(self.code, plan.registry)), *flags]
        with (self.job / 'trabajador.log').open('ab', buffering=0) as log:
            record(self.job / 'LANZAMIENTO.json', dict(worker_id=worker_id['worker_id'],
                   registry_sha256=plan.registry_sha, command=command, environment=self.fingerprint,
                   helpers=str(self.helpers)), once=True)
            subprocess.Popen([sys.executable, '-m', 'cp12_reanudacion.trabajador', str(self.job)],
                             cwd=Path(__file__).resolve().parents[1], env=self.env,
                             stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        return plan

    def resume(self, plan, assets, library):
        if not (self.job / 'LANZAMIENTO.json').is_file():
            plan = self.launch(plan)
        require(read_json(self.job / 'LANZAMIENTO.json')['environment'] == self.fingerprint,
                'Cambió el entorno desde que se lanzó el proceso')
        acceptance = self.output / 'control/ACEPTACION_COMBINADA.json'
        if (self.output / 'ACTIVACION.json').is_file() and (self.output / 'INICIO_FISICO.json').is_file():
            combined = read_json(acceptance)
            self.validate_capacity(plan, combined, assets=None, library=library)
            return self.activate(plan, acceptance, combined)
        self.wait(lambda: self.alive(plan, locks=True) or (self.job / 'SALIDA_OBSERVADA.json').exists(),
                  'Identidad y exclusividad del trabajador')
        if not self.alive(plan, locks=True):
            if self.alive(plan):
                raise Stop('ESPERANDO_LOCKS', 'El proceso todavía no acredita ambos locks',
                           'Volver a ejecutar retomar con el mismo --trabajo', chat=False)
            self.unavailable(plan, library)
        self.stage('TRABAJADOR_EXCLUSIVO', worker_id=self.worker_id['worker_id'])
        if not acceptance.is_file():
            self.capacity(plan, assets, library)
        combined = self.wait(lambda: optional(acceptance) or not self.alive(plan), 'Capacidad independiente')
        if not isinstance(combined, dict):
            if not self.alive(plan):
                self.unavailable(plan, self.destinations.library())
            raise Stop('ESPERANDO_CAPACIDAD', 'El trabajador sigue auditando la recuperación',
                       'Volver a ejecutar retomar con el mismo --trabajo', chat=False)
        self.validate_capacity(plan, combined, assets=None, library=self.destinations.library())
        self.stage('CAPACIDAD_ACREDITADA', receipt=str(acceptance), sha256=sha(acceptance))
        return self.activate(plan, acceptance, combined)

    def capacity(self, plan, assets, library):
        control = self.output / 'control'
        split = plan.registry['kind'] == 'transport'
        public_dir = control / 'publico' if split else control
        native_dir = control / 'nativo' if split else control
        request_path = public_dir / 'SOLICITUD.json'
        native_path = native_dir / 'transito/RESULTADO_TRANSITO.json'
        ready = self.wait(lambda: (optional(request_path) and optional(native_path)) or not self.alive(plan),
                          'Preparación y recuperación nativa')
        if not self.alive(plan):
            self.unavailable(plan, self.destinations.library())
        if not ready:
            raise Stop('ESPERANDO_CAPACIDAD_NATIVA', 'El trabajador aún prepara o recupera el control',
                       'Volver a ejecutar retomar con el mismo --trabajo', chat=False)
        request, native = read_json(request_path), read_json(native_path)
        self.check_native_request(plan, native)
        self.check_native(plan, native, self.destinations.library())
        self.stage('CAPACIDAD_NATIVA_ACREDITADA', receipt=str(native_path))
        require(request['kind'] == 'boundary' and request['capacity_probe'] is True and request['release_tag'] == TAG and
                request['repository'] == REPO and request['observer_clock'] == plan.frontier['observer_clock'],
                'Solicitud pública distinta de la capacidad registrada')
        self.compare_public(plan, request)
        handoff = public_dir / 'ASSET_GITHUB.json'
        self.report['pending_publication'] = {k: request[k] for k in ('archive_path', 'file_name', 'bytes', 'sha256')}
        assets, _ = self.fresh(plan, inventory=True)
        require(self.alive(plan, locks=True), 'El trabajador perdió exclusividad antes de la publicación')
        if handoff.exists():
            selected = find_asset(assets, request)
            require(selected and selected['id'] == read_json(handoff)['id'], 'El adjunto entregado cambió')
        else:
            self.fresh(plan)
            selected = pending_public(self.destinations, assets, request,
                                      self.job / 'INTENCION_PUBLICA.json', self.approval)
            self.fresh(plan)
            require(selected['id'] != plan.frontier['github_asset_id'] and self.alive(plan, locks=True),
                    'El adjunto o el proceso ya no son los de capacidad')
            record(handoff, selected, once=True)
        self.stage('ADJUNTO_PUBLICO_RECUPERADO', asset_id=selected['id'], file=request['file_name'],
                   independent_audit_pending=True)

    def compare_public(self, plan, request):
        result = self.job / 'CONTENIDO_PUBLICO_VERIFICADO.json'
        source = Path(request['archive_path'])
        self.destinations.check(source, request)
        cached = optional(result)
        if (cached and cached['passed'] is True and cached['control_sha256'] == request['sha256'] and
                cached['public_frontier_sha256'] == plan.frontier['sha256'] and
                cached['registry_sha256'] == plan.registry_sha and
                cached['comparator_sha256'] == sha(self.code / COMPARE)):
            return
        with self.timings.measure('auditoria', 'Comparar contenido permitido del control público'):
            temp = self.job / ('comparar-' + uuid.uuid4().hex + '.json')
            cmd = [sys.executable, str(self.code / COMPARE), '--control', str(source), '--publico',
                   str(self.reference), '--repositorio', str(self.git.root), '--salida', str(temp),
                   '--sha-control', request['sha256'], '--sha-publico', plan.frontier['sha256'],
                   '--commit-publico', plan.head, '--registro-publico', plan.registry_path,
                   '--ejecutor-publico', HYBRID, '--publico-asset-id', str(plan.frontier['github_asset_id'])]
            log_command(cmd, temp, self.env)
            comparison = read_json(temp)
            require(comparison['passed'] is True and comparison['unclassified_entries'] == 0,
                    'Comparación pública no acreditada')
            record(result, dict(comparison, registry_sha256=plan.registry_sha, comparator_sha256=sha(self.code / COMPARE)))

    @staticmethod
    def check_native(plan, native, library):
        library_item(library, native)
        audit = native['recovery']
        require(native['passed'] is True and native['upload_outcome'] == 'confirmed' and
                native['observer_clock'] == plan.origin['observer_clock'] and audit['passed'] is True and
                audit['exact_manifest_coverage'] is True and audit['all_payload_hashes_verified_before_and_after'] is True,
                'Recuperación nativa incompleta o de otro reloj')
        checked_audits(audit['original_audits'], plan.origin)

    def check_native_request(self, plan, native):
        split = plan.registry['kind'] == 'transport'
        directory = self.output / ('control/nativo' if split else 'control')
        request = read_json(directory / 'SOLICITUD.json')
        label = 'CONTROL_NATIVO_' if split else 'CONTROL_'
        require(request['file_name'] == PREFIX + label + plan.allocation.upper() + '.zip' and
                request['capacity_probe'] is True and request['kind'] == plan.origin['kind'] and
                all(request[key] == native[key] for key in ('file_name', 'bytes', 'sha256', 'observer_clock')),
                'El control nativo no pertenece a esta solicitud y asignación')

    def validate_capacity(self, plan, combined, assets, library):
        require(combined['passed'] is True and combined['capacity_probe'] is True and
                combined['M2_steps_executed_during_preservation'] == 0 and
                combined['observer_clock'] == plan.registry['clock'] and
                (plan.registry['kind'] != 'transport' or combined['registry_sha256'] == plan.registry_sha),
                'Capacidad de otro proceso, registro o reloj')
        self.check_native_request(plan, combined['native'])
        self.check_native(plan, combined['native'], library)
        public = combined['github']
        audit = public['recovery']
        require(public['passed'] is True and audit['passed'] is True and audit['exact_manifest_coverage'] is True and
                audit['all_payload_hashes_verified_before_and_after'] is True and
                public['github_asset_id'] != plan.frontier['github_asset_id'], 'Capacidad pública incompleta')
        checked_audits(audit['original_audits'], plan.frontier)
        directory = self.output / ('control/publico' if plan.registry['kind'] == 'transport' else 'control')
        request = read_json(directory / 'SOLICITUD.json')
        handoff = read_json(directory / 'ASSET_GITHUB.json')
        require(all(public[key] == request[key] for key in ('bytes', 'sha256')) and
                public['github_asset_id'] == handoff['id'], 'Recuperación pública de otro adjunto')
        self.compare_public(plan, request)
        if assets is not None:
            item = find_asset(assets, request)
            require(item and item['id'] == public['github_asset_id'], 'El control público ya no está disponible')

    def unavailable(self, plan, library):
        pending_native = None
        for directory in (self.output / 'control/nativo', self.output / 'control'):
            request = optional(directory / 'SOLICITUD.json')
            if not request:
                continue
            found = [item for item in library if item['name'] == request['file_name']]
            require(len(found) <= 1, 'Control nativo de resultado ambiguo')
            if found:
                spec = dict(plan.origin, **{k: request[k] for k in ('file_name', 'bytes', 'sha256')},
                            library_file_id=found[0]['library_file_id'], file_id=found[0]['file_id'],
                            payload_files=len(request['archive_inventory']))
                library_item(library, spec)
                original = optional(directory / 'transito/RESULTADO_TRANSITO.json')
                if original and original['passed']:
                    self.check_native(plan, original, library)
                    receipt = original
                else:
                    archive = self.destinations.archive(spec)
                    _, receipt = self.audit(spec, archive, capacity=True)
                record(self.job / 'RECUPERACION_NATIVA_RECONCILIADA.json', dict(spec=spec, recovery=receipt))
                self.stage('SUBIDA_NATIVA_RECONCILIADA', file=spec['file_name'])
                break
            transit = optional(directory / 'transito/RESULTADO_TRANSITO.json') or {}
            pending_native = (request, transit.get('upload_outcome', 'resultado sin recibo'))
        public_dir = self.output / ('control/publico' if plan.registry['kind'] == 'transport' else 'control')
        request = optional(public_dir / 'SOLICITUD.json')
        found = None
        if request:
            found = find_asset(self.destinations.assets(), request)
            if found:
                self.recover_public(plan, request, found)
        exited = optional(self.job / 'SALIDA_OBSERVADA.json')
        reason = 'Salida del trabajador observada' if exited else 'Sesión inaccesible o lanzamiento incierto, salida sin observar'
        self.report['worker'].update(status='SALIDA_OBSERVADA' if exited else 'SESION_INACCESIBLE_SIN_SALIDA',
                                     exit_observed=bool(exited), exit=exited)
        if pending_native:
            native, outcome = pending_native
            raise Stop('SUBIDA_NATIVA_INCIERTA', f'{reason}. Capacidad nativa pendiente ({outcome})',
                       'Conciliar la identidad exacta en Biblioteca antes de aislar la asignación o volver a retomar',
                       file=native['archive_path'], destination='Biblioteca')
        if request and not found:
            raise Stop('PUBLICACION_PROCESO_INACCESIBLE', f'{reason}. Falta el adjunto exacto',
                       'Conciliar la subida y acreditar el estado del proceso antes de registrar otra asignación',
                       file=request['archive_path'], destination=f'https://github.com/{REPO}/releases/tag/{TAG}')
        raise Stop('TRABAJADOR_NO_DISPONIBLE', reason,
                   'Reconciliar el intento y registrar su aislamiento y una asignación nueva si procede',
                   file=str(self.job / 'LANZAMIENTO.json'), destination=BRANCH)

    def recover_public(self, plan, request, found):
        spec = dict(plan.frontier, **{key: request[key] for key in ('file_name', 'bytes', 'sha256')})
        spec['github_asset_id'] = found['id']
        spec['payload_files'] = plan.frontier['payload_files'] + 3 if 'archive_inventory' not in request else len(
            request['archive_inventory'])
        archive = self.destinations.archive(spec, public=found)
        self.compare_public(plan, dict(request, archive_path=str(archive)))
        _, receipt = self.audit(spec, archive, capacity=True)
        self.stage('SUBIDA_PUBLICA_RECONCILIADA', asset_id=found['id'], recovery=receipt)

    def activate(self, plan, acceptance, combined):
        base = self.worker_id
        worker_id = base['worker_id']
        capacity_sha = sha(acceptance)
        delivery_path = self.output / 'ACTIVACION.json'
        receipt_path = self.job / 'ENTREGA_INTENCION.json'
        # La entrega puede haberse realizado antes de caer el coordinador.
        if not delivery_path.exists():
            assets, library = self.fresh(plan, inventory=True)
            self.validate_capacity(plan, combined, assets, library)
        folder = plan.directory
        reservation_path = f'{folder}/ASIGNACION_REANUDADOR.json'
        acceptance_path = f'{folder}/capacidad/ACEPTACION_COMBINADA.json'
        reservation = dict(schema='CP12_P3_FORWARD_RESERVATION_V2', at_utc=base['at'],
                           allocation_id=plan.allocation, worker_id=worker_id, tool_session_id=None,
                           registry_sha256=plan.registry_sha, registration=plan.registry_path,
                           source_registration_commit=base['head'], capacity_acceptance_sha256=capacity_sha,
                           capacity_acceptance=acceptance_path, source_archive_sha256=plan.origin['sha256'],
                           source_observer_clock=plan.registry['clock'], target=plan.registry['target'],
                           single_worker_reserved=True, both_locks_held=dict(registration=True, instance=True),
                           new_M2_steps_executed_at_reservation=0, CP12_closed=False)
        reserved = self.git.get(plan.head, reservation_path, missing=True)
        if reserved is None:
            require(not delivery_path.exists() and self.alive(plan, locks=True),
                    'No se puede reservar un proceso sin exclusividad o que ya recibió activación')
            reserved = encoded(reservation)
            reservation_commit = self.publish(plan, {reservation_path: reserved, acceptance_path: acceptance.read_bytes()},
                                              'CP12/P3: reservar proceso tras capacidad propia')
            plan = self.published_plan(plan, reservation_commit)
        else:
            require(reserved == encoded(reservation) and self.git.get(plan.head, acceptance_path) == acceptance.read_bytes(),
                    'Reserva o capacidad pública distintas')
            reservation_commit = self.git.version(plan.head, reservation_path)
        require(self.git.get(reservation_commit, reservation_path) == reserved and
                self.git.get(reservation_commit, acceptance_path) == acceptance.read_bytes(),
                'La reserva no se recuperó del commit publicado')
        self.stage('RESERVA_RECUPERADA', commit=reservation_commit)
        readback = dict(schema='CP12_P3_RESERVATION_READBACK_V2', registered_commit=reservation_commit,
                        public_path=reservation_path, reservation_sha256=digest(reserved), exact_bytes_recovered=True,
                        M2_steps_executed_at_readback=0)
        activation = dict(schema='CP12_P3_FORWARD_ACTIVATION_V2', at_utc=base['at'], allocation_id=plan.allocation,
                          worker_id=worker_id, tool_session_id=None, registered_commit=reservation_commit,
                          registry_sha256=plan.registry_sha, capacity_acceptance_sha256=capacity_sha,
                          single_worker_reserved=True, recovered_reservation_sha256=digest(reserved),
                          source_clock=plan.registry['clock'], target=plan.registry['target'], CP12_closed=False)
        published_path = f'{folder}/ACTIVACION.json'
        published = self.git.get(plan.head, published_path, missing=True)
        if published is None:
            require(not delivery_path.exists() and self.alive(plan, locks=True), 'Proceso sin exclusividad para activar')
            published = encoded(activation)
            activation_commit = self.publish(plan, {published_path: published,
                                              f'{folder}/RESERVA_RECUPERADA.json': encoded(readback)},
                                              'CP12/P3: registrar activación tras recuperar la reserva')
            plan = self.published_plan(plan, activation_commit)
        else:
            require(published == encoded(activation) and plan.files(self.git, 'RESERVA_RECUPERADA.json') == readback,
                    'Activación o comprobante de reserva distintos')
            activation_commit = self.git.version(plan.head, published_path)
        require(self.git.get(activation_commit, published_path) == published, 'No se recuperó la activación de GitHub')
        self.stage('ACTIVACION_RECUPERADA', commit=activation_commit)
        intent = optional(receipt_path)
        if not delivery_path.exists():
            assets, library = self.fresh(plan, inventory=True)
            self.validate_capacity(plan, combined, assets, library)
            require(self.alive(plan, locks=True) and plan.claim['worker_id'] == worker_id,
                    'El proceso perdió exclusividad antes de entregar la activación')
            if intent is None:
                intent = record(receipt_path, dict(worker_id=worker_id, at=now(), activation_commit=activation_commit,
                                activation_sha256=digest(published), both_locks_held=True), once=True)
            self.fresh(plan)
            require(self.alive(plan, locks=True), 'El proceso perdió los locks antes de la entrega')
            install(delivery_path, published, once=True)
        require(intent and intent['worker_id'] == worker_id and intent['activation_commit'] == activation_commit and
                intent['activation_sha256'] == digest(published) and intent['both_locks_held'] is True and
                delivery_path.read_bytes() == published, 'Activación entregada sin comprobantes del mismo proceso')
        self.stage('ACTIVACION_ENTREGADA', receipt=str(receipt_path))
        first = self.wait(lambda: optional(self.output / 'INICIO_FISICO.json') or not self.alive(plan),
                          'Primer paso físico aceptado')
        if not isinstance(first, dict):
            if not self.alive(plan):
                self.unavailable(plan, self.destinations.library())
            raise Stop('ESPERANDO_INICIO', 'La entrega está comprobada. Aún falta un paso físico aceptado',
                       'Volver a ejecutar retomar con el mismo --trabajo', chat=False)
        first_step(first, plan.registry)
        require(datetime.fromisoformat(first['at']) >= datetime.fromisoformat(intent['at']),
                'El primer paso registrado precede a la entrega')
        delivery = dict(schema='CP12_P3_FORWARD_ACTIVATION_DELIVERY_V2', at_utc=intent['at'],
                        activation_commit=activation_commit, activation_sha256=digest(published),
                        registry_sha256=plan.registry_sha, capacity_acceptance_sha256=capacity_sha,
                        worker_id=worker_id, tool_session_id=None, exact_public_bytes_recovered=True,
                        both_worker_locks_held=True, delivered_atomically=True,
                        activity_not_inferred_from_delivery=True, CP12_closed=False)
        observed = dict(schema='CP12_P3_FORWARD_OBSERVED_ACTIVATION_RECEIPT_V2',
                        activation_commit=activation_commit, worker_id=worker_id, tool_session_id=None,
                        starting_observer_clock=plan.registry['clock'], physical_start_observed=True,
                        first_observed=first, activation_delivery=f'{folder}/ACTIVACION_RECUPERADA_Y_ENTREGADA.json',
                        no_predecessor_intervals_repeated=True, activity_is_restart_certificate=False, CP12_closed=False)
        next_action = f'Conservar los transportes previstos y comprobar la frontera τ{plan.registry["target"]} con las puertas originales'
        state = dict(plan.state, updated_at=first['at'], last_public_commit=activation_commit,
                     current_own_worker_status='INICIO_FISICO_ACREDITADO', own_observed_start=first,
                     own_guardian_tool_session_id=None, own_worker_id=worker_id,
                     own_exit_observed=(self.job / 'SALIDA_OBSERVADA.json').is_file(), own_attempt_home=None,
                     capacity_public_asset_id=combined['github']['github_asset_id'], next_recovery=next_action,
                     latest_recoverable_observer_clock=plan.origin['observer_clock'],
                     latest_recoverable_kind=plan.origin['kind'], active_publication_block=None)
        self.publish(plan, {STATE: encoded(state), f'{folder}/INICIO_FISICO.json': encoded(first),
                     f'{folder}/ACTIVACION_RECUPERADA_Y_ENTREGADA.json': encoded(delivery),
                     f'{folder}/RECEPCION_ACREDITADA_POR_INICIO.json': encoded(observed)},
                     'CP12/P3: acreditar el primer paso físico y actualizar el registro vigente')
        self.report['next_action'] = next_action
        self.stage('INICIO_FISICO_ACREDITADO', first=first)
        return 'INICIO_ACREDITADO'


def read_json(path):
    return json.loads(path.read_bytes())
