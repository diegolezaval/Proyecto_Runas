"""Exporta cambios UTF-8 preparados; los blobs grandes se reconstruyen desde su base Git."""
import argparse
import json
from pathlib import Path
import re
import subprocess


def git(*args):
    return subprocess.check_output(['git', *args])


def lines(text):
    parts = text.split('\n')
    return [p + '\n' for p in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def export(base):
    files = []
    for raw in git('diff', '--cached', '--name-only', '-z', base).split(b'\0'):
        if not raw:
            continue
        name = raw.decode('utf8')
        oid = git('rev-parse', ':' + name).decode().strip()
        target = git('cat-file', 'blob', oid).decode('utf8')
        item = dict(path=name, sha=oid, characters=len(target))
        previous = subprocess.run(['git', 'rev-parse', '--verify', base + ':' + name], capture_output=True, text=True)
        if previous.returncode or len(target) < 12000:
            item['content'] = target
        else:
            old_oid = previous.stdout.strip()
            old = git('cat-file', 'blob', old_oid).decode('utf8')
            old_lines, new_lines = lines(old), lines(target)
            offsets = [0]
            for line in old_lines:
                offsets.append(offsets[-1] + len(line))
            diff = git('diff', '--cached', '--no-ext-diff', '--no-color', '--no-renames', '--unified=0', base, '--', name).decode('utf8')
            operations = []
            for match in re.finditer(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', diff, re.MULTILINE):
                start, count, new_start, new_count = [int(v) if v is not None else 1 for v in match.groups()]
                a = start - 1 if count else start
                b = new_start - 1 if new_count else new_start
                operations.append([offsets[a], offsets[a + count], ''.join(new_lines[b:b + new_count])])
            pieces, cursor = [], 0
            for a, b, replacement in operations:
                if a < cursor:
                    raise ValueError('Hunks solapados: ' + name)
                pieces.extend([old[cursor:a], replacement])
                cursor = b
            pieces.append(old[cursor:])
            if ''.join(pieces) != target:
                raise ValueError('Delta no reproduce exactamente el blob: ' + name)
            item.update(base_sha=old_oid, operations=operations)
        files.append(item)
    return dict(parent=base, base_tree=git('rev-parse', base + '^{tree}').decode().strip(),
        expected_tree=git('write-tree').decode().strip(), files=files,
        all_deltas_reconstruct_exact_git_blobs=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    data = export(args.base)
    args.salida.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps(dict(paths=len(data['files']), bytes=args.salida.stat().st_size,
        expected_tree=data['expected_tree'], local_reconstruction_passed=True)))
