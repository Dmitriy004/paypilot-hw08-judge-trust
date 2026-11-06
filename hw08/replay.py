"""Offline agreement gate: replay retained votes, never calls a model or stand."""
import json
import hashlib
import sys
from collections import Counter
from pathlib import Path

from lab.reference import core_hash
from loader import load


def verdict_exit(report):
    try:
        manifest = json.loads(Path('hw08/manifest.json').read_text(encoding='utf-8'))
        canonical = Path(manifest['canonical']).read_bytes()
        runtime = Path(manifest['runtime_alias'])
        if canonical != runtime.read_bytes() or hashlib.sha256(canonical).hexdigest() != manifest['set_sha256']:
            return 2
        reference = load(runtime)
        expected = {c['id']: c['additional_metadata'] for c in reference}
        if len(reference) != manifest['cases'] or len(expected) != len(reference) or core_hash(reference) != manifest['core_hash']:
            return 2
        if report.get('set_hash') != manifest['set_sha256'][:12] or report.get('runs') != 5:
            return 2
        if report.get('core_hash', manifest['core_hash']) != manifest['core_hash']:
            return 2
        cases = report.get('cases') or []
        ids = [r['id'] for r in cases]
        if len(ids) != len(expected) or len(set(ids)) != len(ids) or set(ids) != set(expected):
            return 2
        failed = False
        for row in cases:
            label = expected[row['id']]['label']
            votes = row.get('verdicts') or []
            if row.get('label') != label or row.get('disputed') != expected[row['id']]['disputed']:
                return 2
            if len(votes) != 5 or any(v not in ('PASS', 'FAIL') for v in votes):
                return 2
            failed |= Counter(votes).most_common(1)[0][0] != label
        return 1 if failed else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return 2


def main():
    if len(sys.argv) != 2:
        print('Usage: python -m hw08.replay reports/calibration-file.json')
        return 2
    try:
        report = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        print('Invalid/unreadable report')
        return 2
    code = verdict_exit(report)
    rows = report.get('cases') if isinstance(report, dict) else None
    count = len(rows) if isinstance(rows, list) else 0
    print(json.dumps({'report': sys.argv[1], 'cases': count, 'gate_exit': code,
                      'meaning': 'all reference agreements' if code == 0 else ('reference mismatch' if code == 1 else 'invalid/incomplete report')}))
    return code


if __name__ == '__main__':
    sys.exit(main())
