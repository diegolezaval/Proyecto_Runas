"""Nuevas resoluciones; usa intactas las ecuaciones y el integrador CP09."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from threadpoolctl import threadpool_limits
import continuar_no_radial_m2 as base
import continuar_no_radial_adaptativo as adaptive
import acelerar_fuerza_m2 as accelerated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--stop-at', type=float)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())['case']['configuration']
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    base.OUT = output
    adaptive.OUT = output
    with threadpool_limits(limits=1):
        audit_path = output / 'auditoria_fuerza_fusionada.json'
        if not audit_path.exists():
            sim = base.Evolution(config['dx'], config['radius'], config['L'])
            q, _, _ = base.seed(sim, config['eps'])
            standard = sim.force
            meta = accelerated.install(sim)  # shared disposable cache, source included
            rng = np.random.default_rng(20261002)
            errors = []
            for number in range(5):
                trial = q if number == 0 else q + rng.normal(size=q.shape) * 1e-5
                reference, tested = standard(trial), sim.force(trial)
                errors.append(float(np.max(abs(reference-tested)) / max(1., float(np.max(abs(reference))))))
            audit = dict(**meta, configuration=config, random_seed=20261002, errors=errors,
                         passed=max(errors) < 2e-12, scope='Equivalencia de implementación en la nueva malla; no certifica convergencia física.')
            base.save_json(audit_path, audit)
            if not audit['passed']:
                raise RuntimeError('Auditoría C/NumPy fallida')
        audit = json.loads(audit_path.read_text())
        if audit['source_sha256'] != hashlib.sha256(accelerated.SOURCE.read_bytes()).hexdigest():
            raise RuntimeError('Fuente C cambió')
        adaptive.run(**config, stop_at=args.stop_at, fused=True)


if __name__ == '__main__':
    main()
