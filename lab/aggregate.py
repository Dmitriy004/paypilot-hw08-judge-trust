"""Independent audit of official majority results; counts cases, not votes."""
import hashlib
import json
from collections import Counter
from math import sqrt
from pathlib import Path
from lab.reference import core_hash


def wilson(k, n):
    if not 0 <= k <= n or n <= 0:
        raise ValueError('Expected 0 <= k <= n and n > 0')
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0, c - h), min(1, c + h), h


def metric(k, n):
    p, lo, hi, h = wilson(k, n)
    return {'count': [k, n], 'rate': p, 'wilson': [lo, hi], 'half_width': h}


def summarize(votes, labels, disputed):
    if set(votes) != set(labels) or set(disputed) != set(labels):
        raise ValueError('All reference IDs must be present')
    rows = []
    for case_id, vs in votes.items():
        if len(vs) != 5 or any(v not in ('PASS', 'FAIL') for v in vs):
            raise ValueError('Exactly five valid votes required; never drop invalid results')
        majority = Counter(vs).most_common(1)[0][0]
        rows.append({'id': case_id, 'label': labels[case_id], 'votes': vs, 'majority': majority,
                     'stable': len(set(vs)) == 1, 'agree': majority == labels[case_id],
                     'disputed': disputed[case_id]})
    out = {'agreement': metric(sum(r['agree'] for r in rows), len(rows)),
           'self_consistency': metric(sum(r['stable'] for r in rows), len(rows)),
           'false_accept': sum(r['majority'] == 'PASS' and r['label'] == 'FAIL' for r in rows),
           'false_reject': sum(r['majority'] == 'FAIL' and r['label'] == 'PASS' for r in rows),
           'mismatch_ids': [r['id'] for r in rows if not r['agree']], 'cases': rows}
    for name, group in (('obvious', [r for r in rows if not r['disputed']]),
                        ('disputed', [r for r in rows if r['disputed']]),
                        ('obvious_PASS', [r for r in rows if not r['disputed'] and r['label'] == 'PASS']),
                        ('obvious_FAIL', [r for r in rows if not r['disputed'] and r['label'] == 'FAIL'])):
        if group:
            out[name] = metric(sum(r['agree'] for r in group), len(group))
    return out


def quote_valid(answer, quote):
    return isinstance(quote, str) and quote in answer


def load_set(name):
    return [json.loads(s) for s in Path('sets', name + '.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
