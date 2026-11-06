"""Offline agreement gate: replay retained votes, never calls a model or stand."""
import json
import sys
from collections import Counter
from pathlib import Path


def verdict_exit(report):
    cases = report.get('cases') or []
    if not cases:
        return 2
    failed = False
    for row in cases:
        votes = row.get('verdicts') or []
        if len(votes) != 5 or any(v not in ('PASS', 'FAIL') for v in votes) or row.get('label') not in ('PASS', 'FAIL'):
            return 2
        failed |= Counter(votes).most_common(1)[0][0] != row['label']
    return 1 if failed else 0


def main():
    if len(sys.argv) != 2:
        print('Usage: python -m hw08.replay reports/calibration-file.json')
        return 2
    report = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    code = verdict_exit(report)
    print(json.dumps({'report': sys.argv[1], 'cases': len(report.get('cases', [])), 'gate_exit': code,
                      'meaning': 'all reference agreements' if code == 0 else ('reference mismatch' if code == 1 else 'invalid/incomplete report')}))
    return code


if __name__ == '__main__':
    sys.exit(main())
