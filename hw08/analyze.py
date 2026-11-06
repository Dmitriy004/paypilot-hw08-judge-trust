"""Independent raw-evidence audit; preserves failures and rejects incomplete samples."""
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import judge
import stand
from lab.aggregate import quote_valid, summarize
from lab.reference import core_hash
from loader import load


def audit_phase(records, cases, clarification=''):
    prompts = {}
    for c in cases:
        rubric = c['additional_metadata']['rubric'] + ('\n\n' + clarification.strip() if clarification else '')
        prompt = f"CUSTOMER QUESTION:\n{c['input']}\n\nAGENT ANSWER:\n{c['answer_under_test']}\n\nRUBRIC:\n{rubric}\n\nJSON:"
        if prompt in prompts:
            raise ValueError('Duplicate semantic calibration input')
        prompts[prompt] = c
    votes, evidence = {c['id']: [] for c in cases}, []
    for r in records:
        body, response = r['request'], r['response']
        if (body.get('model'), body.get('temperature'), body.get('max_tokens'), body.get('reasoning')) != \
                ('google/gemini-2.5-flash', .7, 400, {'effort': 'none'}):
            raise ValueError('Experimental model/settings changed')
        if body['messages'][0] != {'role': 'system', 'content': judge.SYSTEM}:
            raise ValueError('SYSTEM changed')
        c = prompts.get(body['messages'][1]['content'])
        if c is None:
            raise ValueError('Raw prompt is not an unchanged frozen input/answer/criterion')
        if response.get('model') != 'google/gemini-2.5-flash' or r['cost_usd'] is None:
            raise ValueError('Unknown model or actual cost')
        parsed = judge._parse(response['choices'][0]['message']['content'])
        votes[c['id']].append(parsed['verdict'])
        evidence.append({'id': c['id'], 'file': r['file'], **parsed,
                         'quote_valid': quote_valid(c['answer_under_test'], parsed['quote'])})
    out = summarize(votes, {c['id']: c['additional_metadata']['label'] for c in cases},
                    {c['id']: bool(c['additional_metadata']['disputed']) for c in cases})
    versions = {r['rubric_version'] for r in records}
    if len(versions) != 1:
        raise ValueError('Mixed rubric versions in one phase')
    out.update(rubric_version=versions.pop(), judge_model='openrouter:google/gemini-2.5-flash',
               evidence=evidence, invalid_quotes=[e for e in evidence if not e['quote_valid']],
               cost_usd=sum(r['cost_usd'] for r in records),
               input_tokens=sum(r['response']['usage']['prompt_tokens'] for r in records),
               output_tokens=sum(r['response']['usage']['completion_tokens'] for r in records))
    out['matrix'] = {reference: {prediction: sum(r['label'] == reference and r['majority'] == prediction for r in out['cases'])
                                for prediction in ('PASS', 'FAIL')} for reference in ('PASS', 'FAIL')}
    return out


def exact_cost(records, traces):
    agents = [r for r in records if r['kind'] == 'agent']
    traced = {t['trace']['request_id']: t['trace'] for t in traces}
    ids = [r['response']['request_id'] for r in agents if r['response']]
    if len(ids) != len(agents) or len(set(ids)) != len(ids) or any(rid not in traced for rid in ids):
        raise ValueError('Exact reconciliation blocked: unmatched paid agent responses')
    if set(traced) != set(ids):
        raise ValueError('Orphan or foreign trace')
    if any(r['cost_usd'] is None for r in records):
        raise ValueError('Unknown actual cost; no zero substitution')
    llm = [a for rid in ids for a in stand.llm_calls(traced[rid])]
    if any(a.get('provider.cost_usd') is None for a in llm):
        raise ValueError('Unknown span cost')
    agent_cost = sum(a['provider.cost_usd'] for a in llm)
    judge_cost = sum(r['cost_usd'] for r in records if r['kind'] == 'judge')
    return {'boundary_records': len(records), 'agent_turns': len(agents), 'agent_llm_calls': len(llm),
            'judge_llm_calls': sum(r['kind'] == 'judge' for r in records),
            'provider_llm_calls': len(llm) + sum(r['kind'] == 'judge' for r in records),
            'agent_trace_usd': agent_cost, 'judge_response_usd': judge_cost,
            'actual_usd': agent_cost + judge_cost,
            'response_reported_rounded_usd': sum(r['cost_usd'] for r in records)}


def build():
    manifest = json.loads(Path('hw08/manifest.json').read_text(encoding='utf-8'))
    canonical, runtime = Path(manifest['canonical']), Path(manifest['runtime_alias'])
    if canonical.read_bytes() != runtime.read_bytes() or hashlib.sha256(runtime.read_bytes()).hexdigest() != manifest['set_sha256']:
        raise ValueError('Frozen set bytes/alias changed')
    cases = load(runtime)
    if core_hash(cases) != manifest['core_hash']:
        raise ValueError('Frozen semantic reference changed')
    records = sorted((json.loads(p.read_text(encoding='utf-8')) | {'file': p.as_posix()}
                      for p in Path('hw08/evidence/audit').glob('*.json')), key=lambda r: r['at_utc'])
    traces = [json.loads(p.read_text(encoding='utf-8')) | {'file': p.as_posix()}
              for p in sorted(Path('reports/traces').rglob('*.json'))]
    out = {'set_hash': manifest['set_sha256'][:12], 'core_hash': manifest['core_hash'], 'phases': {},
           'cost': exact_cost(records, traces), 'agent_runs': []}
    for phase in ('baseline', 'after'):
        selected = [r for r in records if r['phase'] == phase]
        if not selected:
            continue
        clarification = Path('rubric/v2.md').read_text(encoding='utf-8').strip() if phase == 'after' else ''
        s = audit_phase(selected, cases, clarification)
        candidates = []
        last_call = datetime.fromisoformat(selected[-1]['at_utc'])
        for p in Path('reports').glob('calibration-l09_labels-*.json'):
            report = json.loads(p.read_text(encoding='utf-8'))
            if report['set_hash'] != out['set_hash'] or report['judge_model'] != s['judge_model']:
                continue
            by_id = {r['id']: r for r in report['cases']}
            if set(by_id) != {c['id'] for c in cases}:
                continue
            if all(by_id[r['id']]['verdicts'] == r['votes'] and by_id[r['id']]['label'] == r['label'] for r in s['cases']):
                delay = (datetime.fromisoformat(report['ran_at']) - last_call).total_seconds()
                if delay >= 0:
                    candidates.append((delay, p, report))
        if not candidates:
            raise ValueError('Official calibration summary does not match all raw votes')
        _, source, official = min(candidates, key=lambda item: item[0])
        enriched = {**official, 'rubric_version': s['rubric_version'], 'phase': phase,
                    'source_report': source.as_posix(), 'core_hash': out['core_hash'],
                    'self_consistency_wilson': s['self_consistency']['wilson'],
                    'metadata_note': 'Rubric version and independent intervals added from validated raw audit; official votes unchanged.'}
        target = Path('reports', f'calibration-hw08-{phase}-audited.json')
        target.write_text(json.dumps(enriched, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        s.update(source_report=source.as_posix(), audited_report=target.as_posix(),
                 first_call_utc=selected[0]['at_utc'], last_call_utc=selected[-1]['at_utc'])
        out['phases'][phase] = s
    agent_by_id = {r['response']['request_id']: r for r in records if r['kind'] == 'agent'}
    for t in traces:
        tree = t['trace']
        attrs = tree['attributes']
        raw = agent_by_id[tree['request_id']]
        calls = stand.tool_calls(tree)
        out['agent_runs'].append({'case': t['case'], 'run': t['run'], 'request_id': tree['request_id'],
            'phase': raw['phase'], 'trace_file': t['file'], 'answer': t['answer'], 'tool_calls': calls,
            'customer_id': attrs.get('session.customer_id'), 'model': attrs.get('run.model'),
            'profile': attrs.get('run.profile'), 'prompt_version': attrs.get('prompt.version'),
            'escalated': any(c['name'] == 'escalate_to_human' for c in calls)})
    Path('hw08/summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'phases': {p: {k: s[k] for k in ('agreement', 'self_consistency', 'mismatch_ids', 'matrix', 'cost_usd')}
                                 for p, s in out['phases'].items()}, 'cost': out['cost']}, indent=2))


if __name__ == '__main__':
    build()
