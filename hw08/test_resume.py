import os
import unittest
from unittest.mock import patch


class ResumeTests(unittest.TestCase):
    def test_live_prefix_uses_effective_environment_temperature(self):
        from hw08.calibrate import Resume
        body = {'model': 'openai/gpt-4.1-mini', 'max_tokens': 400, 'temperature': .7,
                'provider': {'only': ['openai'], 'allow_fallbacks': False, 'require_parameters': True},
                'messages': [{'role': 'system', 'content': 's'}, {'role': 'user', 'content': 'p'}]}
        cached = [{'request': body, 'response': {'choices': [{'message': {'content': 'saved'}}]}}]
        with patch.dict(os.environ, {'TEMP': '.7', 'LAB_PROVIDER_ROUTE': 'openai'}):
            self.assertEqual(Resume(cached, lambda *a: self.fail('must not charge'))('s', 'p', 'openrouter:openai/gpt-4.1-mini', None), 'saved')

    def test_nonreasoning_gpt41_omits_unsupported_reasoning_parameter(self):
        import tempfile
        from lab import provider
        with tempfile.TemporaryDirectory() as d:
            seen = []
            def send(body, key):
                seen.append(body)
                return {'choices': [{'message': {'content': 'ok'}}], 'usage': {'cost': .001}}
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key', 'LAB_AUDIT_DIR': d,
                                         'LAB_PROVIDER_ROUTE': 'openai'}), patch.object(provider, '_send', send):
                provider.complete('s', 'p', 'openrouter:openai/gpt-4.1-mini', .7)
            self.assertNotIn('reasoning', seen[0])
            self.assertEqual(seen[0]['temperature'], .7)
            self.assertEqual(seen[0]['max_tokens'], 400)

    def test_priority_route_is_explicit_and_does_not_change_model(self):
        import tempfile
        from lab import provider
        with tempfile.TemporaryDirectory() as d:
            seen = []
            def send(body, key):
                seen.append(body)
                return {'choices': [{'message': {'content': 'ok'}}], 'usage': {'cost': .001}}
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key', 'LAB_AUDIT_DIR': d,
                                         'LAB_PROVIDER_ROUTE': 'google-ai-studio/priority'}), patch.object(provider, '_send', send):
                provider.complete('s', 'p', 'openrouter:google/gemini-2.5-flash', .7)
            self.assertEqual(seen[0]['model'], 'google/gemini-2.5-flash')
            self.assertEqual(seen[0]['provider'], {'only': ['google-ai-studio/priority'], 'allow_fallbacks': False, 'require_parameters': True})

    def test_successful_prefix_is_replayed_once_then_only_new_calls_are_paid(self):
        from hw08.calibrate import Resume
        body = {'model': 'google/gemini-2.5-flash', 'max_tokens': 400, 'temperature': .7,
                'reasoning': {'effort': 'none'}, 'messages': [{'role': 'system', 'content': 's'}, {'role': 'user', 'content': 'p'}]}
        cached = [{'request': body, 'response': {'choices': [{'message': {'content': 'saved'}}]}}]
        paid = []
        def live(*args):
            paid.append(args)
            return 'fresh'
        resume = Resume(cached, live, interval=0)
        self.assertEqual(resume('s', 'p', 'openrouter:google/gemini-2.5-flash', .7), 'saved')
        self.assertFalse(paid)
        self.assertEqual(resume('s', 'p2', 'openrouter:google/gemini-2.5-flash', .7), 'fresh')
        self.assertEqual(len(paid), 1)
        with self.assertRaises(RuntimeError):
            Resume(cached, live, interval=0)('s', 'changed', 'openrouter:google/gemini-2.5-flash', .7)

    def test_provider_account_identifier_is_redacted_in_nested_raw_error(self):
        from lab.audit import clean
        self.assertEqual(clean({'raw_body': '{"user_id":"user_private123456789","error":"429"}'}),
                         {'raw_body': '{"user_id":"[REDACTED]","error":"429"}'})
