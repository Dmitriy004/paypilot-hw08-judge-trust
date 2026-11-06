"""One durable record per response, saved before decoding and enriched atomically."""
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def clean(value):
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()
                if k.lower() not in {'authorization', 'api_key', 'x-api-key'}}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, str):
        value = re.sub(r'("user_id"\s*:\s*")[^"]*"', r'\1[REDACTED]"', value)
        for name in ('OPENROUTER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY'):
            secret = os.environ.get(name)
            if secret:
                value = value.replace(secret, '[REDACTED]')
    return value


class Audit:
    def __init__(self, directory=None, cap=1.0):
        self.directory = Path(directory or os.environ.get('LAB_AUDIT_DIR', 'lab/evidence/audit'))
        self.directory.mkdir(parents=True, exist_ok=True)
        self.cap = min(cap, float(os.environ.get('LAB_SPEND_CAP_USD', cap)))
        if not math.isfinite(self.cap) or self.cap <= 0:
            raise ValueError('Positive finite spend cap required')

    def total(self):
        total = 0.0
        for p in self.directory.glob('*.json'):
            cost = json.loads(p.read_text(encoding='utf-8'))['guard_cost_usd']
            if cost is None:
                raise RuntimeError('Unknown spend; reconcile before another paid request')
            total += cost
        return total

    def ensure_room(self, reserve_usd):
        if not math.isfinite(reserve_usd) or reserve_usd <= 0:
            raise ValueError('Positive finite reservation required')
        if self.total() + reserve_usd > self.cap:
            raise RuntimeError('Experiment budget guard: stop before paid request')

    def record(self, kind, request, response, error=None, reserve=None):
        usage = (response or {}).get('usage') or {}
        cost = usage.get('cost', usage.get('provider_cost_usd'))
        if cost is not None and (not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0):
            cost = None
        now = datetime.now(timezone.utc).isoformat()
        row = clean({'at_utc': now, 'phase': os.environ.get('LAB_PHASE', 'unspecified'),
                     'rubric_version': os.environ.get('RUBRIC_VERSION', 'rubric.v1'),
                     'kind': kind, 'request': request, 'response': response, 'error': str(error) if error else None,
                     'cost_usd': cost, 'guard_cost_usd': cost if cost is not None else reserve,
                     'cost_basis': 'actual' if cost is not None else ('reserved-upper-bound' if reserve else 'unknown')})
        p = self.directory / (now.replace(':', '').replace('+', '_') + '-' + uuid.uuid4().hex[:8] + '.json')
        with p.open('x', encoding='utf-8', newline='\n') as f:
            json.dump(row, f, ensure_ascii=False, indent=2)
            f.write('\n')
        return p

    def enrich(self, path, response):
        """Keep the saved raw envelope even if parsing/enrichment later fails."""
        row = json.loads(path.read_text(encoding='utf-8'))
        row['response'] = clean({**row['response'], **response})
        usage = response.get('usage') or {}
        cost = usage.get('cost', usage.get('provider_cost_usd'))
        if isinstance(cost, (int, float)) and math.isfinite(cost) and cost >= 0:
            row.update(cost_usd=cost, guard_cost_usd=cost, cost_basis='actual')
        temporary = path.with_suffix('.tmp')
        with temporary.open('x', encoding='utf-8', newline='\n') as f:
            json.dump(row, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(temporary, path)
