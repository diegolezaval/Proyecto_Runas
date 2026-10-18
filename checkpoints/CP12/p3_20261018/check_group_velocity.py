"""Exact additional interior-symbol identity, not a repeated F0 or M2 run."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json


def multiply(a, b):
    result = [F(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            result[i+j] += u*v
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    p = [F(0), F(1), F(1, 12), F(1, 90)]
    derivative = [i*p[i] for i in range(1, len(p))]
    rhs = multiply([F(1), F(-1, 4)], multiply(derivative, derivative))
    difference = [(p[i+1] if i+1 < len(p) else F(0))-rhs[i]
                  for i in range(len(rhs))]
    expected = [F(0), F(0), F(0), F(1, 80), F(1, 600), F(1, 3600)]
    at_four = sum(value*4**i for i, value in enumerate(p))
    tests = dict(exact_identity=difference == expected,
                 nonnegative_coefficients=all(x >= 0 for x in difference),
                 positive_symbol_for_positive_x=all(x > 0 for x in p[1:]),
                 exact_nyquist_symbol=at_four == F(272, 45))
    result = dict(schema='CP12_P3_ADDITIONAL_EXACT_INTERIOR_GROUP_VELOCITY',
                  tests=tests, passed=all(tests.values()),
                  difference_coefficients=[str(x) for x in difference],
                  nyquist_symbol=str(at_four),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Homogeneous infinite flat linear operator, constant nonnegative mass squared',
                  radial_box_or_nonlinear_causality_proved=False,
                  M2_steps_executed=0, DOP853_constructions_or_steps=0,
                  F0_F5_repeated=False, candidate_changed=False, CP12_closed=False)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
