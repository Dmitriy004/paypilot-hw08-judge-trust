"""Explicitly replay completed independent working turns; new turns stay live."""
import json
import os
import sys
from pathlib import Path


def resume_calls(live, cached, traces):
    index = 0
    def call(method, path, payload=None, **kwargs):
        nonlocal index
        if method == 'POST' and path == '/chat' and index < len(cached):
            row = cached[index]
            if row['request']['payload'] != payload:
                raise RuntimeError('Live resume prefix differs from saved question/customer/session')
            index += 1
            return row['response']
        if method == 'GET' and path.startswith('/api/_test/traces/'):
            rid = path.rsplit('/', 1)[1]
            if rid in traces:
                return traces[rid]
        return live(method, path, payload, **kwargs)
    return call


def main():
    import cli
    import stand
    from lab import provider
    from lab.audit import Audit
    from lab.live import capture_call
    from hw08.calibrate import Resume
    phase = os.environ['LAB_PHASE']
    directory = Path(os.environ.get('LAB_AUDIT_DIR', 'hw08/evidence/audit'))
    records = sorted((json.loads(p.read_text(encoding='utf-8')) for p in directory.glob('*.json')), key=lambda r: r['at_utc'])
    cached = [r for r in records if r['phase'] == phase and r['kind'] == 'agent']
    ids = {r['response']['request_id'] for r in cached if r['response']}
    if len(ids) != len(cached):
        raise ValueError('Cannot replay unsuccessful or duplicate agent responses')
    traces = {}
    for p in Path('reports/traces').rglob('*.json'):
        tree = json.loads(p.read_text(encoding='utf-8'))['trace']
        if tree['request_id'] in ids:
            traces[tree['request_id']] = tree
    if set(traces) != ids:
        raise ValueError('Saved paid agent prefix has missing traces')
    judges = [r for r in records if r['phase'] == phase and r['kind'] == 'judge' and (r['response'] or {}).get('choices')]
    stand._call = resume_calls(capture_call(stand._call, Audit()), cached, traces)
    provider.complete = Resume(judges, provider.complete)
    print(f'Explicit live resume: {len(cached)} saved independent turns and {len(judges)} saved judge outputs (including invalid ones); no paid repeats.', flush=True)
    return cli.main(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
