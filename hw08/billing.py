"""Private account snapshots; only experiment delta is published."""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def main():
    name = sys.argv[1]
    if name not in ('before', 'after'):
        raise SystemExit('Expected before or after')
    req = urllib.request.Request('https://openrouter.ai/api/v1/key',
        headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY']})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)['data']
    private = Path('hw08/private')
    private.mkdir(parents=True, exist_ok=True)
    snapshot = {'at_utc': datetime.now(timezone.utc).isoformat(), 'usage': data['usage']}
    p = private / (name + '.json')
    if name == 'before' and p.exists():
        raise SystemExit('Refusing to overwrite baseline')
    p.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')
    if name == 'before':
        print('Private usage baseline saved; no account total displayed.')
        with urllib.request.urlopen('https://openrouter.ai/api/v1/models', timeout=60) as r:
            models = json.load(r)['data']
        prices = {m['id']: m['pricing'] for m in models if m['id'] in
                  ('anthropic/claude-haiku-5.5', 'google/gemini-2.5-flash')}
        Path('hw08/prices.json').write_text(json.dumps({'at_utc': snapshot['at_utc'], 'models': prices}, indent=2), encoding='utf-8')
        print('Selected-model public prices saved.')
    else:
        before = json.loads((private / 'before.json').read_text(encoding='utf-8'))
        delta = {'from_utc': before['at_utc'], 'to_utc': snapshot['at_utc'],
                 'provider_usage_delta_usd': data['usage'] - before['usage'],
                 'scope': 'API-key usage delta; assumes no concurrent use of this key.'}
        Path('hw08/provider-reconciliation.json').write_text(json.dumps(delta, indent=2), encoding='utf-8')
        print(json.dumps(delta))


if __name__ == '__main__':
    main()
