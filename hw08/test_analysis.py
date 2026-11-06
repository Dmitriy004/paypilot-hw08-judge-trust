import copy
import unittest


class AnalysisTests(unittest.TestCase):
    def test_transport_errors_remain_pending_until_provider_delta_reconciles(self):
        from hw08.analyze import accounting
        known = {'kind': 'judge', 'response': {'choices': [{}]}, 'cost_usd': .002, 'file': 'known.json'}
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
        judge = {'kind': 'judge', 'response': {}, 'cost_usd': .002}
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
        result = audit_phase([record] * 5, [case])
        self.assertEqual(result['agreement']['count'], [1, 1])
        self.assertEqual(len(result['invalid_quotes']), 5)
        for votes in ([record] * 4, [record] * 6):
            with self.assertRaises(ValueError):
                audit_phase(votes, [case])
        changed = copy.deepcopy(record)
        changed['request']['messages'][1]['content'] = 'altered answer'
        with self.assertRaises(ValueError):
            audit_phase([changed] * 5, [case])
