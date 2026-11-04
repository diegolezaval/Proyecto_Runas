"""Controles administrativos adversos; sin importar kernels ni ejecutar M2."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import zipfile
import preservar as p
import continuar as runner


def rejects(call):
    try:call()
    except (ValueError,RuntimeError,FileExistsError):return True
    return False


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--auditor',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args();tests={}
    with tempfile.TemporaryDirectory() as directory:
        r=Path(directory);home=r/'home';(home/'outputs').mkdir(parents=True);(home/'transport').mkdir()
        for name,value in [('outputs/MIXTO_par_estado.npz',b'closed'),('outputs/procedencia.json',b'receipt'),('configuration.json',b'configuration'),('transport/current.npz',b'transport')]:
            (home/name).write_bytes(value)
        reg=dict(schema='CP12_P3_FORWARD_SEGMENT_V2',registered_before_M2=True,replay96_to112_authorized=False,
            kind='transport',closed_boundary=8,target=16,clock=11.2,closed_state_sha256=p.sha(home/'outputs/MIXTO_par_estado.npz'),
            receipt_sha256=p.sha(home/'outputs/procedencia.json'),configuration_sha256=p.sha(home/'configuration.json'),
            transport_sha256=p.sha(home/'transport/current.npz'),administrative_sources={},helper_sha256={},original_auditor_sha256=p.sha(args.auditor))
        runner.validate(reg,home,r,args.auditor)
        tests['consumed_replay_cannot_be_authorized']=rejects(lambda:runner.validate(dict(reg,replay96_to112_authorized=True),home,r,args.auditor))
        tests['earlier_clock_refused']=rejects(lambda:runner.validate(dict(reg,clock=9.6),home,r,args.auditor))
        tests['boundary_skip_refused']=rejects(lambda:runner.validate(dict(reg,target=24),home,r,args.auditor))
        tests['wrong_transport_refused']=rejects(lambda:runner.validate(dict(reg,transport_sha256='different'),home,r,args.auditor))
        tests['wrong_configuration_refused']=rejects(lambda:runner.validate(dict(reg,configuration_sha256='different'),home,r,args.auditor))
        tests['changed_administrative_source_refused']=rejects(lambda:runner.validate(dict(reg,administrative_sources={'continuar.py':'different'}),home,r,args.auditor))
        activation=r/'activation.json';p.write(activation,dict(schema='CP12_P3_FORWARD_ACTIVATION_V2',registry_sha256='expected',
            capacity_acceptance_sha256='wrong',single_worker_reserved=True,registered_commit='commit'))
        tests['unrelated_capacity_cannot_activate_physics']=rejects(lambda:runner.activate(activation,'expected','right'))
        tests['existing_receipt_not_overwritten']=rejects(lambda:p.write(activation,{}))
        request=dict(file_name='x.zip',bytes=1,sha256='a');metadata=dict(name='x.zip',size=2,digest='sha256:a',browser_download_url='wrong')
        tests['wrong_public_asset_rejected_before_download']=rejects(lambda:p.public(request,metadata,r/'public',args.auditor))
        source=r/'source';source.mkdir();(source/'x').write_bytes(b'original');archive=r/'archive.zip';archive.write_bytes(b'unchanged')
        req=dict(archive_path=str(archive),sha256=p.sha(archive),source_home=str(source),source_inventory={'x':dict(bytes=8,sha256=p.sha(source/'x'))})
        (source/'x').write_bytes(b'changed!');tests['source_mutation_detected']=rejects(lambda:p.unchanged(req))
        spec=importlib.util.spec_from_file_location('original_unpack_guards',args.auditor);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        unsafe=r/'unsafe.zip'
        with zipfile.ZipFile(unsafe,'w') as z:z.writestr('../outside',b'bad');z.writestr('MANIFIESTO_NEGATIVO.json',json.dumps(dict(files={})))
        tests['original_unpack_rejects_unsafe_paths']=rejects(lambda:m.unpack(unsafe,r/'fresh',p.sha(unsafe),unsafe.stat().st_size))
        tests['unsafe_payload_not_written']=not (r/'outside').exists()
    result=dict(schema='CP12_P3_FORWARD_ADVERSARIAL_ADMIN_TESTS_V2',passed=all(tests.values()),tests=tests,
        M2_steps_executed=0,DOP853_constructed=False,scope='Rechazo administrativo; no acredita conservación real ni valida P3.')
    p.write(args.salida,result);print(json.dumps(result,ensure_ascii=False));return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
