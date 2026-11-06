"""Explicit resume of the stock calibrator: replay saved prefix, then new calls.

Transport errors are retained separately and never turned into binary votes.
There is no automatic retry: a new provider error stops this invocation.
"""
import hashlib
import json
import os
import runpy
import sys
import time
from pathlib import Path


class Resume:
    def __init__(self, cached, live, interval=1.5):
        self.cached, self.live, self.interval = cached, live, interval
        self.index, self.last = 0, 0.0

    def __call__(self, system, prompt, model, temperature):
        if temperature is None and os.environ.get('TEMP'):
            temperature = float(os.environ['TEMP'])
        if self.index < len(self.cached):
            row = self.cached[self.index]
            want = {'model': model.removeprefix('openrouter:'), 'max_tokens': 400,
                    'reasoning': {'effort': 'none'}, 'messages': [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': prompt}], 'temperature': temperature}
            if want['model'].startswith('openai/gpt-4.1'):
                want.pop('reasoning')
            if os.environ.get('LAB_PROVIDER_ROUTE'):
                want['provider'] = {'only': [os.environ['LAB_PROVIDER_ROUTE']],
                                    'allow_fallbacks': False, 'require_parameters': True}
            if row['request'] != want:
                raise RuntimeError('Resume prefix differs from current frozen prompt/settings')
            self.index += 1
            return row['response']['choices'][0]['message']['content']
        remaining = self.interval - (time.monotonic() - self.last)
        if remaining > 0:
            time.sleep(remaining)
        self.last = time.monotonic()
        return self.live(system, prompt, model, temperature)


def main():
    from lab import provider
    manifest = json.loads(Path('hw08/manifest.json').read_text(encoding='utf-8'))
    path = Path('sets/l09_labels.jsonl')
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['set_sha256'] or path.read_bytes() != Path(manifest['canonical']).read_bytes():
        raise ValueError('Frozen dataset/alias changed')
    phase = os.environ['LAB_PHASE']
    directory = Path(os.environ.get('LAB_AUDIT_DIR', 'hw08/evidence/audit'))
    rows = sorted((json.loads(p.read_text(encoding='utf-8')) for p in directory.glob('*.json')), key=lambda r: r['at_utc'])
    cached = [r for r in rows if r['phase'] == phase and r['response'] and r['response'].get('choices')]
    errors = [r for r in rows if r['phase'] == phase and not (r['response'] or {}).get('choices')]
    print(f'Explicit resume: {len(cached)} previously paid responses replayed; {len(errors)} retained transport errors.', flush=True)
    provider.complete = Resume(cached, provider.complete, float(os.environ.get('LAB_MIN_INTERVAL', '1.5')))
    name = sys.argv[1] if len(sys.argv) > 1 else 'l09_labels'
    sys.argv = ['tools/calibrate_run.py', name]
    runpy.run_path('tools/calibrate_run.py', run_name='__main__')


if __name__ == '__main__':
    main()
