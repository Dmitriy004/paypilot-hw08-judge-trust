import json
import os
import tempfile
import io
import urllib.error
import unittest
from pathlib import Path
from unittest.mock import patch


class ProviderTests(unittest.TestCase):
    def test_outer_json_and_http_errors_retain_body_before_next_success(self):
        from lab import provider
        class Response(io.BytesIO):
            status = 200
        with tempfile.TemporaryDirectory() as d:
            error = urllib.error.HTTPError('https://openrouter.ai/api/v1/chat/completions', 502, 'bad gateway', {}, io.BytesIO(b'upstream unavailable'))
            results = [Response(b'broken JSON secret-test'), error,
                       Response(b'{"choices":[{"message":{"content":"ok"}}],"usage":{"cost":0.001}}')]
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'secret-test', 'LAB_AUDIT_DIR': d}), patch('urllib.request.OpenerDirector.open', side_effect=results):
                with self.assertRaises((ValueError, RuntimeError)):
                    provider.complete('s', 'p', 'm', .7)
                with self.assertRaises(RuntimeError):
                    provider.complete('s', 'p', 'm', .7)
                self.assertEqual(provider.complete('s', 'p', 'm', .7), 'ok')
            rows = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(Path(d).glob('*.json'))]
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]['response']['http_status'], 200)
            self.assertEqual(rows[0]['response']['raw_body'], 'broken JSON [REDACTED]')
            self.assertEqual(rows[1]['response']['raw_body'], 'upstream unavailable')
            self.assertEqual(rows[1]['response']['http_status'], 502)
            self.assertEqual(rows[2]['cost_usd'], .001)

    def test_versioned_clarification_appends_without_editing_criterion(self):
        import judge
        from lab import provider
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'rubric.txt'
            path.write_text('Contact time is not resolution time.', encoding='utf-8')
            seen = []
            def send(body, key):
                seen.append(body['messages'][1]['content'])
                return {'choices': [{'message': {'content': '{"verdict":"PASS","trigger":"c","evidence_turn":1,"quote":"a"}'}}],
                        'usage': {'cost': .001}}
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-secret', 'LAB_AUDIT_DIR': d,
                                         'JUDGE_RUBRIC_APPEND': str(path)}), patch.object(provider, '_send', send):
                judge.judge('q', 'a', 'Original criterion.', 'openrouter:google/gemini-2.5-flash', .7)
            self.assertIn('RUBRIC:\nOriginal criterion.\n\nContact time is not resolution time.\n\nJSON:', seen[0])

    def test_transport_preserves_prompt_and_saves_paid_malformed_output(self):
        import judge
        from lab import provider
        with tempfile.TemporaryDirectory() as d:
            captured = []
            def send(body, key):
                captured.append(body)
                return {'id': 'gen-test', 'model': 'google/gemini-2.5-flash',
                        'choices': [{'message': {'content': 'not JSON'}}],
                        'usage': {'prompt_tokens': 100, 'completion_tokens': 3, 'cost': .001}}
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'secret-test', 'LAB_AUDIT_DIR': d,
                                         'LAB_PHASE': 'test'}), patch.object(provider, '_send', send):
                with self.assertRaises(ValueError):
                    judge.judge('q <untrusted>', 'a €', 'literal criterion',
                                'openrouter:google/gemini-2.5-flash', .7)
            self.assertEqual(captured[0]['model'], 'google/gemini-2.5-flash')
            self.assertEqual(captured[0]['max_tokens'], 400)
            self.assertEqual(captured[0]['reasoning'], {'effort': 'none'})
            self.assertEqual(captured[0]['temperature'], .7)
            self.assertEqual(captured[0]['messages'][1]['content'],
                             'CUSTOMER QUESTION:\nq <untrusted>\n\nAGENT ANSWER:\na €\n\nRUBRIC:\nliteral criterion\n\nJSON:')
            saved = list(Path(d).glob('*.json'))
            self.assertEqual(len(saved), 1)
            text = saved[0].read_text(encoding='utf-8')
            self.assertNotIn('secret-test', text)
            self.assertIn('not JSON', text)
