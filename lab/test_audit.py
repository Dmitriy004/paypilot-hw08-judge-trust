import json
import tempfile
import unittest
from pathlib import Path


class AuditTests(unittest.TestCase):
    def test_actual_and_unknown_costs_guard_following_requests(self):
        from lab.audit import Audit
        with tempfile.TemporaryDirectory() as d:
            a = Audit(d, cap=0.1)
            a.record('judge', {'prompt': 'literal'}, {'usage': {'cost': .07}})
            a.ensure_room(.02)
            with self.assertRaises(RuntimeError):
                a.ensure_room(.04)
            a.record('judge', {}, {'usage': {}}, reserve=.02)
            self.assertAlmostEqual(a.total(), .09)
            rows = [json.loads(p.read_text(encoding='utf-8')) for p in Path(d).glob('*.json')]
            self.assertEqual(sorted(r['cost_basis'] for r in rows), ['actual', 'reserved-upper-bound'])

    def test_unknown_cost_without_reserve_blocks_not_zero(self):
        from lab.audit import Audit
        with tempfile.TemporaryDirectory() as d:
            a = Audit(d)
            a.record('agent', {}, {'answer': 'paid response', 'request_id': 'r'})
            with self.assertRaises(RuntimeError):
                a.ensure_room(.01)

    def test_agent_response_survives_trace_failure(self):
        from lab.live import capture_call
        from lab.audit import Audit
        with tempfile.TemporaryDirectory() as d:
            a = Audit(d)
            response = {'request_id': 'r1', 'answer': 'paid', 'usage': {'provider_cost_usd': .001}}
            def call(method, path, payload=None, **kw):
                if path == '/chat':
                    return response
                raise RuntimeError('trace unavailable')
            wrapped = capture_call(call, a)
            self.assertEqual(wrapped('POST', '/chat', {'message': 'q'}), response)
            with self.assertRaises(RuntimeError):
                wrapped('GET', '/api/_test/traces/r1')
            rows = [json.loads(p.read_text(encoding='utf-8')) for p in Path(d).glob('*.json')]
            self.assertEqual(rows[0]['response']['answer'], 'paid')
