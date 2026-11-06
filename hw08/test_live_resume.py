import unittest
from unittest.mock import patch


class LiveResumeTests(unittest.TestCase):
    def test_invalid_judge_output_is_failure_and_next_case_can_be_evaluated(self):
        import runner
        with patch.object(runner, 'JUDGE_MODEL', 'openrouter:openai/gpt-4.1-mini'), \
             patch('judge.verdict', side_effect=[ValueError('malformed JSON'), (True, 'valid next output')]):
            ok, why = runner._judge('q', 'a', 'r')
            self.assertFalse(ok)
            self.assertIn('invalid_judge_output', why)
            self.assertTrue(runner._judge('q2', 'a2', 'r')[0])

    def test_saved_agent_prefix_and_traces_are_replayed_without_http_or_duplicate_records(self):
        from hw08.live_resume import resume_calls
        row = {'request': {'payload': {'message': 'q', 'session_id': None, 'customer_id': 'CUS-X'}},
               'response': {'request_id': 'r1', 'answer': 'saved'}}
        tree = {'request_id': 'r1', 'children': []}
        real = []
        def live(method, path, payload=None, **kw):
            real.append(path)
            return {'request_id': 'r2', 'answer': 'fresh'}
        wrapped = resume_calls(live, [row], {'r1': tree})
        self.assertEqual(wrapped('POST', '/chat', row['request']['payload']), row['response'])
        self.assertEqual(wrapped('GET', '/api/_test/traces/r1'), tree)
        self.assertFalse(real)
        self.assertEqual(wrapped('POST', '/chat', {'message': 'new'})['request_id'], 'r2')
        self.assertEqual(real, ['/chat'])
        with self.assertRaises(ValueError):
            resume_calls(live, [row], {'r1': tree})('POST', '/chat', {'message': 'wrong'})
