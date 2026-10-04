"""Control aislado del cierre y reutilización de un recibo externo; sin ciencia."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def check():
    with tempfile.TemporaryDirectory(prefix='runas_recibo_externo_') as temporary:
        work = Path(temporary)
        root = work / 'Proyecto_Runas'
        for name in ['herramientas', 'datos', 'validacion/P06/no_radial']:
            (root / name).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'herramientas/ejecutar_con_procedencia.py', root / 'herramientas/ejecutar_con_procedencia.py')
        (root / 'datos/theta_comun.json').write_text('{}')
        (root / 'datos/origen.json').write_text('{"scope":"CONTROL_NO_M2"}')
        (root / 'herramientas/control.py').write_text('from pathlib import Path\nimport argparse\np=argparse.ArgumentParser();p.add_argument("--config");p.add_argument("--output-dir",type=Path);a=p.parse_args();(a.output_dir/"control.json").write_text("{}")\n')
        protocol = dict(model='CONTROL_NO_M2', initial_state='datos/origen.json', cases={'control':dict(entrypoint='herramientas/control.py', inputs=['datos/origen.json'], configuration={})})
        (root / 'datos/protocolo.json').write_text(json.dumps(protocol))
        launcher = ('import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);'
                    'import ejecutar_con_procedencia as p;p.CAMPAIGN=Path(sys.argv[2]);'
                    'p.execute(p.ROOT/"datos/protocolo.json","control");'
                    'receipt=next(p.CAMPAIGN.glob("*/procedencia.json"));'
                    'assert p.verify_receipt(receipt)["passed"];print("INTEGRIDAD_OK")')
        command = [sys.executable, '-c', launcher, str(root / 'herramientas'), str(work / 'recibos_externos')]
        env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE'] = '1'
        first = subprocess.run(command, text=True, capture_output=True, env=env, timeout=20)
        paths = list((work / 'recibos_externos').glob('*/procedencia.json'))
        assert first.returncode == 0 and len(paths) == 1, first.stdout + first.stderr
        before = paths[0].read_bytes()
        second = subprocess.run(command, text=True, capture_output=True, env=env, timeout=20)
        tests = dict(external_close_exits_zero=first.returncode == 0 and 'COMPLETADA' in first.stdout,
                     external_completed_receipt_reused=second.returncode == 0 and 'REUTILIZADO' in second.stdout,
                     receipt_integrity_verified='INTEGRIDAD_OK' in first.stdout and 'INTEGRIDAD_OK' in second.stdout,
                     reused_receipt_byte_identical=paths[0].read_bytes() == before,
                     external_path_reported=str(work / 'recibos_externos') in first.stdout,
                     synthetic_control_only=True)
        return dict(passed=all(tests.values()), tests=tests, new_M2_evolution_steps=0,
                    scope='Control aislado de publicación, no cálculo ni aceptación científica.')


if __name__ == '__main__':
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)
