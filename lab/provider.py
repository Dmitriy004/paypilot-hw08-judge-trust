"""OpenRouter transport only; official judge parser and majority are unchanged."""
import json
import os
import urllib.error
import urllib.request
from lab.audit import Audit, clean


def _send(body, key):
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',
                                 data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=180) as r:
            return r.status, r.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')


def complete(system, prompt, model, temperature):
    if temperature is None and os.environ.get('TEMP'):
        temperature = float(os.environ['TEMP'])
    key = os.environ.get('OPENROUTER_API_KEY')
    if not key:
        raise RuntimeError('OPENROUTER_API_KEY is not set')
    body = {'model': model.removeprefix('openrouter:'), 'max_tokens': 400,
            'reasoning': {'effort': 'none'},
            'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]}
    if body['model'].startswith('openai/gpt-4.1'):
        body.pop('reasoning')
    if temperature is not None:
        body['temperature'] = temperature
    if os.environ.get('LAB_PROVIDER_ROUTE'):
        body['provider'] = {'only': [os.environ['LAB_PROVIDER_ROUTE']],
                            'allow_fallbacks': False, 'require_parameters': True}
    audit = Audit()
    audit.ensure_room(.01)
    try:
        received = _send(body, key)
    except Exception as e:
        audit.record('judge', body, None, error=e, reserve=.01)
        raise RuntimeError(clean(str(e))) from None
    # Dict support keeps the narrow injected transport used by offline tests.
    status, raw = (200, json.dumps(received)) if isinstance(received, dict) else received
    path = audit.record('judge', body, {'http_status': status, 'raw_body': raw}, reserve=.01)
    if status >= 400:
        raise RuntimeError(f'OpenRouter HTTP {status}; sanitized body retained in {path.name}')
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError('OpenRouter response must be an object; raw response retained')
    audit.enrich(path, data)
    return data['choices'][0]['message']['content']
