import copy
import unittest


class AnalysisTests(unittest.TestCase):
    def test_resumed_trace_copies_do_not_duplicate_actual_agent_turns(self):
        from hw08.analyze import unique_traces
        a = {'case': 'X', 'run': 1, 'answer': 'a', 'trace': {'request_id': 'r1'}, 'file': 'old.json'}
        b = {**a, 'file': 'resumed.json'}
        unique, copies = unique_traces([a, b])
        self.assertEqual(len(unique), 1)
        self.assertEqual(copies, ['resumed.json'])
        with self.assertRaises(ValueError):
            unique_traces([a, {**b, 'answer': 'different'}])

    def test_transport_errors_remain_pending_until_provider_delta_reconciles(self):
        from hw08.analyze import accounting
        known = {'kind': 'judge', 'response': {'id': 'gen-known', 'choices': [{}]}, 'cost_usd': .002, 'file': 'known.json'}
        error = {'kind': 'judge', 'response': {'http_status': 429}, 'cost_usd': None, 'file': '429.json'}
        pending = accounting([known, error], [])
        self.assertIsNone(pending['actual_usd'])
        self.assertEqual(pending['unresolved_transport_attempts'], ['429.json'])
        done = accounting([known, error], [], {'provider_usage_delta_usd': .002})
        self.assertEqual(done['actual_usd'], .002)
        self.assertEqual(done['rejected_transport_cost_residual_usd'], 0)
        self.assertEqual(done['provider_llm_calls'], 1)
        with self.assertRaises(ValueError):
            accounting([known, error], [], {'provider_usage_delta_usd': .003})

    def test_missing_paid_agent_trace_blocks_exact_cost_and_later_responses_remain(self):
        from hw08.analyze import exact_cost
        rows = [{'kind': 'agent', 'response': {'request_id': rid}, 'cost_usd': .01} for rid in ('r1', 'r2')]
        with self.assertRaisesRegex(ValueError, 'unmatched paid'):
            exact_cost(rows, [{'trace': {'request_id': 'r2', 'children': []}}])
        self.assertEqual(len(rows), 2)

    def test_unknown_cost_not_zero_and_exact_span_cost_not_rounded_turn_cost(self):
        from hw08.analyze import exact_cost
        agent = {'kind': 'agent', 'response': {'request_id': 'r1'}, 'cost_usd': .01}
        judge = {'kind': 'judge', 'response': {'id': 'gen-judge'}, 'cost_usd': .002}
        traces = [{'trace': {'request_id': 'r1', 'children': [{'name': 'llm.call', 'attributes': {'provider.cost_usd': .0099994}}]}}]
        s = exact_cost([agent, judge], traces)
        self.assertEqual(s['provider_llm_calls'], 2)
        self.assertAlmostEqual(s['actual_usd'], .0119994)
        judge['cost_usd'] = None
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            exact_cost([agent, judge], traces)

    def test_phase_rejects_extra_missing_and_altered_prompts(self):
        from hw08.analyze import audit_phase
        from judge import SYSTEM
        case = {'id': 'X', 'input': 'q', 'answer_under_test': 'a', 'additional_metadata': {'criterion': 'c', 'rubric': 'r', 'label': 'PASS', 'disputed': True}}
        request = {'model': 'google/gemini-2.5-flash', 'temperature': .7, 'max_tokens': 400,
                   'reasoning': {'effort': 'none'}, 'messages': [{'role': 'system', 'content': SYSTEM},
                   {'role': 'user', 'content': 'CUSTOMER QUESTION:\nq\n\nAGENT ANSWER:\na\n\nRUBRIC:\nr\n\nJSON:'}]}
        record = {'request': request, 'rubric_version': 'rubric.v1', 'cost_usd': .001,
                  'response': {'model': 'google/gemini-2.5-flash', 'choices': [{'message': {'content': '{"verdict":"PASS","trigger":"r","quote":"invented","evidence_turn":1}'}}],
                               'usage': {'prompt_tokens': 10, 'completion_tokens': 5}}, 'file': 'fake.json'}
        records = [copy.deepcopy(record) for _ in range(5)]
        for i, r in enumerate(records):
            r['response']['id'] = f'gen-{i}'
            r['file'] = f'vote-{i}.json'
        result = audit_phase(records, [case])
        self.assertEqual(result['agreement']['count'], [1, 1])
        self.assertEqual(len(result['invalid_quotes']), 5)
        for votes in (records[:4], records + [record]):
            with self.assertRaises(ValueError):
                audit_phase(votes, [case])
        changed = copy.deepcopy(record)
        changed['request']['messages'][1]['content'] = 'altered answer'
        with self.assertRaises(ValueError):
            audit_phase([changed] * 5, [case])

    def test_duplicate_generation_cannot_replace_a_vote_or_double_count_spend(self):
        import json
        from pathlib import Path
        from hw08.analyze import audit_phase, exact_cost
        from loader import load
        rows = [json.loads(p.read_text(encoding='utf-8')) | {'file': str(p)}
                for p in sorted(Path('hw08/evidence/audit').glob('*.json'))]
        rows = [r for r in rows if r['phase'] == 'baseline' and r['kind'] == 'judge']
        cases = load(Path('sets/l09_labels.jsonl'))
        route = {'only': ['openai'], 'allow_fallbacks': False, 'require_parameters': True}
        self.assertEqual(audit_phase(rows, cases, provider_preferences=route,
                                    model_name='openai/gpt-4.1-mini')['agreement']['count'], [27, 30])
        duplicate = copy.deepcopy(rows)
        duplicate[1] = copy.deepcopy(duplicate[0])
        duplicate[1]['file'] = 'copy-in-another-file.json'
        with self.assertRaisesRegex(ValueError, 'generation'):
            audit_phase(duplicate, cases, provider_preferences=route, model_name='openai/gpt-4.1-mini')
        missing = copy.deepcopy(rows)
        missing[0]['response'].pop('id')
        with self.assertRaisesRegex(ValueError, 'generation'):
            audit_phase(missing, cases, provider_preferences=route, model_name='openai/gpt-4.1-mini')
        cross_archive = copy.deepcopy(rows[0])
        cross_archive.update(phase='after', file='pilot-copy.json')
        with self.assertRaisesRegex(ValueError, 'generation'):
            exact_cost([rows[0], cross_archive], [])
