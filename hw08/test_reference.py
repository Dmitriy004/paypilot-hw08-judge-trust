import json
import unittest
from collections import Counter
from pathlib import Path

from loader import load

ROOT = Path(__file__).resolve().parents[1]


class ReferenceTests(unittest.TestCase):
    def test_blind_reference_has_required_strata_aliases_and_rationales(self):
        canonical = ROOT / 'evals/sets/l09_labels.jsonl'
        runtime = ROOT / 'sets/l09_labels.jsonl'
        self.assertTrue(canonical.exists(), 'new blind homework reference missing')
        self.assertEqual(canonical.read_bytes(), runtime.read_bytes())
        rows = load(runtime)
        self.assertEqual(len(rows), 30)
        self.assertEqual(Counter('disputed' if r['additional_metadata']['disputed'] else r['additional_metadata']['label'] for r in rows),
                         {'PASS': 10, 'FAIL': 10, 'disputed': 10})
        pool = {r['id']: r for r in load(ROOT / 'sets/l09_lab_pool.jsonl')}
        for r in rows:
            m = r['additional_metadata']
            self.assertIn(m['label'], ('PASS', 'FAIL'))
            self.assertEqual((m['runs'], m['gate']), (5, 'release'))
            self.assertTrue(m['labeled_on'])
            self.assertTrue(m['why_disputed'] if m['disputed'] else m['ground_truth_from'])
            self.assertNotRegex(m['criterion'], r'\d')
            if r['id'] in pool:
                for key in ('input', 'answer_under_test'):
                    self.assertEqual(r[key], pool[r['id']][key])
                self.assertEqual(m['criterion'], pool[r['id']]['additional_metadata']['criterion'])

    def test_working_threshold_and_judge_gates_are_separate(self):
        rows = load(ROOT / 'sets/l09_escalation.jsonl')
        judges = [r for r in rows if r['additional_metadata']['assertion'] == 'judge']
        self.assertGreaterEqual(len(judges), 5)
        self.assertTrue(all(r['additional_metadata']['runs'] == 5 and r['additional_metadata']['gate'] == 'release' for r in judges))
        threshold = next(r for r in rows if r['id'] == 'ESC-001')
        m = threshold['additional_metadata']
        self.assertEqual((m['assertion'], m['runs'], m['gate']), ('tool_sequence', 1, 'daily'))
        self.assertIn('escalate_to_human', m['must_include'])
        self.assertEqual(threshold['context']['customer_id'], 'CUS-0007')
