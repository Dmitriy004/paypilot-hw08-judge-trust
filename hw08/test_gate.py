import io
import copy
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


class GateTests(unittest.TestCase):
    def test_offline_gate_recomputes_majority_and_fails_on_mismatch(self):
        from hw08.replay import verdict_exit
        report = json.loads(Path('reports/calibration-hw08-after-audited.json').read_text(encoding='utf-8'))
        self.assertEqual(verdict_exit(report), 1)
        for row in report['cases']:
            row.update(verdicts=[row['label']] * 5, agree=False)
        self.assertEqual(verdict_exit(report), 0)
        row = next(r for r in report['cases'] if r['label'] == 'FAIL')
        row.update(verdicts=['PASS'] * 5, agree=True)
        self.assertEqual(verdict_exit(report), 1)
        row['verdicts'] = ['PASS']
        self.assertEqual(verdict_exit(report), 2)

    def test_offline_gate_rejects_dropped_duplicate_extra_or_relabelled_cases(self):
        from hw08.replay import verdict_exit
        source = json.loads(Path('reports/calibration-hw08-after-audited.json').read_text(encoding='utf-8'))
        dropped = copy.deepcopy(source)
        dropped['cases'] = [r for r in dropped['cases'] if r['id'] not in ('PL-01', 'PL-05', 'PL-16')]
        duplicated = copy.deepcopy(source)
        passing = next(r for r in source['cases'] if r['id'] == 'PL-02')
        duplicated['cases'] = [copy.deepcopy(passing) for _ in range(30)]
        extra = copy.deepcopy(source)
        extra['cases'][-1]['id'] = 'FOREIGN-CASE'
        relabelled = copy.deepcopy(source)
        relabelled['cases'][0]['label'] = 'FAIL'
        wrong_hash = copy.deepcopy(source)
        wrong_hash['set_hash'] = 'changed'
        wrong_core = copy.deepcopy(source)
        wrong_core['core_hash'] = 'changed'
        for name, report in [('dropped', dropped), ('duplicate', duplicated), ('extra', extra),
                             ('relabelled', relabelled), ('hash', wrong_hash), ('core', wrong_core)]:
            with self.subTest(name=name):
                self.assertEqual(verdict_exit(report), 2)

    def test_stock_runner_does_not_treat_all_skipped_as_pass(self):
        import runner
        case = {'id': 'SKIP-CONTROL', 'input': 'q', 'expected_output': 'see criterion', 'context': {},
                'additional_metadata': {'layer': 'judge', 'oracle': 'human', 'assertion': 'judge',
                 'rubric': 'criterion', 'severity': 'high', 'source': 'control', 'gate': 'release', 'runs': 1}}
        result = {'answer': 'a', 'trace': {}, 'usage': {}, 'latency_ms': 0, 'turns': []}
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'GATE': '', 'CASE': '', 'TRACES': ''}), \
             patch.object(runner, 'REPORTS_DIR', Path(d)), patch.object(runner, 'HERE', Path(d) / 'evals'), patch.object(runner, 'JUDGE_MODEL', 'not-used'), \
             patch.object(runner, 'load', return_value=[case]), patch.object(runner, 'set_hash', return_value='testhash'), \
             patch.object(runner, '_one_run', return_value=result), \
             patch.object(runner.stand, 'wait_until_ready'), patch.object(runner.stand, 'profile', return_value={'profile': 'clean'}), \
             patch.object(runner.stand, 'prompt_version', return_value='base.v1'), redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(), 1)

    def test_cli_returns_invalid_exit_for_malformed_report_shapes(self):
        from hw08.replay import main
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'invalid.json'
            for body in ('not json', '[]', '{"cases":5}', '{"cases":{}}'):
                with self.subTest(body=body):
                    path.write_text(body, encoding='utf-8')
                    with patch('sys.argv', ['hw08.replay', str(path)]), redirect_stdout(io.StringIO()):
                        self.assertEqual(main(), 2)

    def test_environment_spend_cap_is_enforced(self):
        from lab.audit import Audit
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'LAB_SPEND_CAP_USD': '.03'}):
            a = Audit(d)
            a.record('judge', {}, {'usage': {'cost': .02}})
            with self.assertRaises(RuntimeError):
                a.ensure_room(.02)

    def test_live_judge_uses_explicit_temperature_environment(self):
        from lab import provider
        with tempfile.TemporaryDirectory() as d:
            seen = []
            def send(body, key):
                seen.append(body)
                return {'choices': [{'message': {'content': 'ok'}}], 'usage': {'cost': .001}}
            with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-key', 'TEMP': '.7', 'LAB_AUDIT_DIR': d}), patch.object(provider, '_send', send):
                provider.complete('s', 'p', 'm', None)
            self.assertEqual(seen[0]['temperature'], .7)
