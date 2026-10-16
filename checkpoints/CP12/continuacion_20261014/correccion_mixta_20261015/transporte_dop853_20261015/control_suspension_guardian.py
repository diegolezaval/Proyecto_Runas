"""Bounded synthetic copy of a guardian with a child in a new session; no M2."""
from pathlib import Path
import argparse
import datetime
import json
import subprocess
import sys
import time


def write(home, name, value):
    value.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(), synthetic_only=True, M2_steps_executed=0)
    (home / name).write_text(json.dumps(value, indent=2) + '\n')


def child(home, duration):
    write(home, 'child_started.json', dict(duration=duration))
    end = time.monotonic() + duration
    count = 0
    try:
        while time.monotonic() < end:
            count += 1
            write(home, 'child_heartbeat.json', dict(count=count))
            time.sleep(.25)
        write(home, 'child_natural_end.json', dict(count=count))
    except BaseException as error:
        write(home, 'child_interruption_checkpoint.json', dict(exception=type(error).__name__, count=count))
        raise
    finally:
        write(home, 'child_finally.json', dict(count=count))


def parent(home, duration):
    home.mkdir(parents=True, exist_ok=False)
    with (home / 'child.log').open('xb') as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--home', str(home),
                                    '--duration', str(duration), '--child'], cwd=home,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        write(home, 'parent_observed_start.json', dict(scope='Only own synthetic child', child_pid_in_parent_namespace=process.pid))
        try:
            result = process.wait()
            write(home, 'parent_observed_exit.json', dict(returncode=result))
            raise SystemExit(result if result >= 0 else 1)
        except BaseException as error:
            write(home, 'parent_interruption.json', dict(exception=type(error).__name__))
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--duration', type=float, default=18)
    parser.add_argument('--child', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.duration <= 20
    (child if args.child else parent)(args.home.resolve(), args.duration)
