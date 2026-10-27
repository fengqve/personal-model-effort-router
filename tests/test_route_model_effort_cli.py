"""Offline CLI integration tests using local mock adapters, never model calls."""

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / 'skills/route-model-effort/scripts/route.py'


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.catalog = {'schema_version': 1, 'synthetic': False,
                        'candidates': [{'id': 'a', 'model': 'mock-model', 'effort': 'low', 'harness': 'h'}],
                        'fallback': 'a', 'policy': {'min_cases': 1, 'min_pass_rate': 1.0, 'max_age_days': 30}}
        self.task = {'id': '中文任务', 'family': '中文类别', 'risk': 'low', 'harness': 'h',
                     'rubric': 'r', 'classification_confirmed': True, 'prompt': '请处理中文'}
        self.runs = [{'id': 'run-1', 'case_id': 'case-1', 'family': '中文类别', 'risk': 'low',
                      'harness': 'h', 'rubric': 'r', 'candidate_id': 'a', 'model': 'mock-model',
                      'effort': 'low', 'passed': True, 'total_cost_usd': 1,
                      'total_duration_seconds': 2, 'completed_at': datetime.now(timezone.utc).isoformat(),
                      'source': 'observed', 'evidence': '模拟适配器测试证据', 'configuration_confirmed': True}]
        self.record = self.dir / 'record.json'
        self.marker = self.dir / 'adapter-calls.jsonl'
        self.adapter = self.dir / 'mock adapter.py'
        self.adapter.write_text('''import json, pathlib, sys\nrequest = json.load(sys.stdin)\nmarker = pathlib.Path(sys.argv[1])\nwith marker.open("a", encoding="utf-8") as f:\n    f.write(json.dumps({"argv": sys.argv[2:], "request": request}, ensure_ascii=False) + "\\n")\nmode = sys.argv[2]\nif mode == "failure":\n    sys.exit(7)\nif mode == "invalid":\n    print("not-json")\n    sys.exit(0)\nif mode == "invalid-fields":\n    print(json.dumps({"passed": True}))\n    sys.exit(0)\napplied = {key: request["selected"][key] for key in ("model", "effort", "harness")}
if mode == "mismatch":
    applied["model"] = "wrong-model"
config = {} if mode == "missing-config" else {"applied_config": applied}
print(json.dumps({**config, "passed": mode != "failed-task", "total_cost_usd": 1.25,\n                  "total_duration_seconds": 3, "evidence": "模拟证据",\n                  "output": "中文结果"}, ensure_ascii=False))\n''', encoding='utf-8')

    def files(self):
        for name, data in (('catalog.json', self.catalog), ('task.json', self.task)):
            (self.dir / name).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        (self.dir / 'runs.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in self.runs), encoding='utf-8')
        return ['--catalog', str(self.dir / 'catalog.json'), '--runs', str(self.dir / 'runs.jsonl'),
                '--task', str(self.dir / 'task.json')]

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', str(ROUTE), *args], cwd=ROOT, text=True,
                              capture_output=True, timeout=10, check=False)

    def dispatch(self, mode='success', *extra, options=()):
        return self.cli('dispatch', *self.files(), *options, '--record-to', str(self.record),
                        '--adapter', sys.executable, '-B', str(self.adapter), str(self.marker), mode, *extra)

    def test_demo_is_explicitly_simulation(self):
        result = self.cli('demo')
        self.assertEqual(result.returncode, 0, result.stderr)
        decision = json.loads(result.stdout)
        self.assertTrue(decision['simulation'])
        self.assertIn('simulation', ' '.join(decision['limitations']).lower())
        self.assertFalse(self.marker.exists())

    def test_route_high_risk_requires_review(self):
        self.task['risk'] = 'high'
        result = self.cli('route', *self.files())
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'review_required')
        self.assertFalse(self.marker.exists())

    def test_dispatch_rejects_simulation_before_adapter(self):
        self.catalog['synthetic'] = True
        self.runs[0]['source'] = 'synthetic'
        result = self.dispatch(options=('--allow-synthetic',))
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.marker.exists())
        self.assertFalse(self.record.exists())

    def test_existing_record_prevents_execution_and_overwrite(self):
        self.record.write_text('existing', encoding='utf-8')
        result = self.dispatch()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.record.read_text(encoding='utf-8'), 'existing')
        self.assertFalse(self.marker.exists())

    def test_success_records_observed_and_preserves_chinese_and_argv(self):
        injection = '$(touch ' + str(self.dir / 'should-not-exist') + ')'
        result = self.dispatch('success', injection)
        self.assertEqual(result.returncode, 0, result.stderr)
        answer = json.loads(result.stdout)
        self.assertEqual(answer['output'], '中文结果')
        record = json.loads(self.record.read_text(encoding='utf-8'))
        self.assertEqual((record['source'], record['passed'], record['evidence']), ('observed', True, '模拟证据'))
        self.assertEqual(record['case_id'], '中文任务')
        self.assertTrue(record['configuration_confirmed'])
        calls = self.marker.read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(calls), 1)
        request = json.loads(calls[0])
        self.assertEqual(request['argv'], ['success', injection])
        self.assertEqual(request['request']['task']['prompt'], '请处理中文')
        self.assertFalse((self.dir / 'should-not-exist').exists())

    def test_failed_task_records_observed_and_exits_three(self):
        result = self.dispatch('failed-task')
        self.assertEqual(result.returncode, 3, result.stderr)
        record = json.loads(self.record.read_text(encoding='utf-8'))
        self.assertFalse(record['passed'])
        self.assertEqual(record['source'], 'observed')
        self.assertEqual(len(self.marker.read_text().splitlines()), 1)

    def test_dispatch_record_feeds_next_routing_decision(self):
        result = self.dispatch()
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.files()
        args.insert(args.index('--task'), str(self.record))
        result = self.cli('route', *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['candidates'][0]['n'], 2)

    def test_fallback_requires_explicit_opt_in(self):
        self.runs = []
        result = self.dispatch()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(self.marker.exists())
        result = self.dispatch(options=('--allow-fallback',))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_timeout_leaves_recovery_marker(self):
        self.adapter.write_text('import time; time.sleep(5)', encoding='utf-8')
        result = self.dispatch(options=('--timeout', '0.02'))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(self.record.read_text())['status'], 'execution_unverified')

    def test_adapter_failures_preserve_unverified_record_and_no_retry(self):
        for mode in ('failure', 'invalid', 'invalid-fields'):
            with self.subTest(mode=mode):
                self.record.unlink(missing_ok=True)
                self.marker.unlink(missing_ok=True)
                result = self.dispatch(mode)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(json.loads(self.record.read_text(encoding='utf-8'))['status'], 'execution_unverified')
                self.assertEqual(len(self.marker.read_text(encoding='utf-8').splitlines()), 1)


    def test_missing_applied_config_is_unconfirmed_and_not_calibration_evidence(self):
        result = self.dispatch('missing-config')
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(self.record.read_text(encoding='utf-8'))
        self.assertFalse(record['configuration_confirmed'])
        args = self.files()
        args.insert(args.index('--task'), str(self.record))
        result = self.cli('route', *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['candidates'][0]['n'], 1)

    def test_mismatched_applied_config_is_unverified(self):
        result = self.dispatch('mismatch')
        self.assertEqual(result.returncode, 1, result.stderr)
        record = json.loads(self.record.read_text(encoding='utf-8'))
        self.assertEqual(record['status'], 'execution_unverified')
        self.assertNotIn('candidate_id', record)
        self.assertNotIn('configuration_confirmed', record)
        self.assertEqual(len(self.marker.read_text(encoding='utf-8').splitlines()), 1)

if __name__ == '__main__':
    unittest.main()
