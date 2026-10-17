"""Synthetic administrative ordering controls; no imports of M2."""
import json
from supervisar_fronteras import sequence


def test():
    positive, negative, exception = [], [], []
    def evolve(log):
        return lambda target: log.append(('evolve_preserve_audit', target))
    def check(log, failing=None):
        def run(target):
            log.append(('prefix', target))
            return target != failing
        return run
    assert sequence([48, 56, 160], evolve(positive), check(positive)) is None
    assert positive == [('evolve_preserve_audit', 48), ('prefix', 48),
                        ('evolve_preserve_audit', 56), ('prefix', 56), ('evolve_preserve_audit', 160)]
    assert sequence([48, 56, 64], evolve(negative), check(negative, 56)) == 56
    assert negative == [('evolve_preserve_audit', 48), ('prefix', 48),
                        ('evolve_preserve_audit', 56), ('prefix', 56)]
    def fail(target):
        exception.append(('prefix_failed', target))
        raise RuntimeError('Synthetic administrative failure')
    try:
        sequence([48, 56], evolve(exception), fail)
        raise AssertionError('Exception swallowed')
    except RuntimeError:
        pass
    assert exception == [('evolve_preserve_audit', 48), ('prefix_failed', 48)]
    return dict(passed=True, positive_sequence=True, scientific_negative_blocks_next=True,
                administrative_failure_blocks_next=True, no_prefix_at_final160=True, M2_steps_executed=0)


if __name__ == '__main__':
    print(json.dumps(test()))
