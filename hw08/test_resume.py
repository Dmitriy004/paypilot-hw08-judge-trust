import os
import unittest
from unittest.mock import patch


class ResumeTests(unittest.TestCase):
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
        with self.assertRaises(ValueError):
            Resume(cached, live, interval=0)('s', 'changed', 'openrouter:google/gemini-2.5-flash', .7)

    def test_provider_account_identifier_is_redacted_in_nested_raw_error(self):
        from lab.audit import clean
        self.assertEqual(clean({'raw_body': '{"user_id":"user_private123456789","error":"429"}'}),
                         {'raw_body': '{"user_id":"[REDACTED]","error":"429"}'})
