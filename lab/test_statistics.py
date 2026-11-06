import unittest


class StatisticsTests(unittest.TestCase):
    def test_stably_wrong_is_consistent_but_not_in_agreement(self):
        from lab.aggregate import summarize
        votes = {str(i): ['PASS'] * 5 for i in range(12)}
        s = summarize(votes, {str(i): 'FAIL' for i in range(12)}, {str(i): i >= 8 for i in range(12)})
        self.assertEqual(s['self_consistency']['count'], [12, 12])
        self.assertEqual(s['agreement']['count'], [0, 12])
        self.assertEqual(s['disputed']['count'], [0, 4])
        self.assertEqual(s['false_accept'], 12)
        self.assertLess(s['self_consistency']['wilson'][0], 1)

    def test_wilson_and_mixed_majority_and_invalid_votes(self):
        from lab.aggregate import summarize, wilson
        p, lo, hi, h = wilson(6, 12)
        self.assertAlmostEqual(p, .5)
        self.assertAlmostEqual(lo, .2537781703934222)
        self.assertAlmostEqual(hi, .7462218296065778)
        self.assertAlmostEqual(h, .2462218296065778)
        s = summarize({'x': ['PASS', 'FAIL', 'FAIL', 'PASS', 'FAIL']}, {'x': 'FAIL'}, {'x': True})
        self.assertEqual(s['agreement']['count'], [1, 1])
        self.assertEqual(s['self_consistency']['count'], [0, 1])
        with self.assertRaises(ValueError):
            summarize({'x': ['PASS', 'INVALID']}, {'x': 'FAIL'}, {'x': True})

    def test_fabricated_quote_is_flagged_without_changing_vote(self):
        from lab.aggregate import quote_valid
        self.assertTrue(quote_valid('Answer €10', '€10'))
        self.assertTrue(quote_valid('Answer €10', ''))
        self.assertFalse(quote_valid('Answer €10', '€11'))
