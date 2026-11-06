"""Frozen semantic identity, deliberately independent of rubric wording."""
import hashlib
import json


def core_hash(cases):
    core = []
    for row in sorted(cases, key=lambda r: r['id']):
        m = row['additional_metadata']
        core.append([row['id'], row['input'], row['answer_under_test'],
                     m['criterion'], m['label'], bool(m.get('disputed'))])
    return hashlib.sha256(json.dumps(core, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
