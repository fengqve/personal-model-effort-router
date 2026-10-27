import copy
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/route-model-effort/scripts'))
from model_effort_router.core import evaluate, validate_catalog, validate_task, ValidationError

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)


def fixtures():
    candidates = [dict(id=i, model=i, effort='high', harness='h') for i in ('cheap', 'fast', 'best', 'new')]
    catalog = dict(schema_version=1, synthetic=False, candidates=candidates, fallback='cheap',
                   policy=dict(min_cases=2, min_pass_rate=0.5, max_age_days=30))
    task = dict(id='t', family='f', harness='h', rubric='r', risk='low', classification_confirmed=True)
    runs = []
    for c, cost, duration, passes in [('cheap', 1, 30, (True, False)),
                                      ('fast', 2, 10, (True, False)),
                                      ('best', 3, 20, (True, True))]:
        for index, passed in enumerate(passes):
            runs.append(dict(id=f'{c}-{index}', case_id=f'case-{index}', family='f', harness='h',
                             rubric='r', risk='low', candidate_id=c, model=c, effort='high',
                             evidence='verified', passed=passed, total_cost_usd=cost,
                             total_duration_seconds=duration, completed_at='2026-10-26T00:00:00Z',
                             source='observed', configuration_confirmed=True))
    return catalog, runs, task


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.catalog, self.runs, self.task = fixtures()

    def route(self):
        return evaluate(self.catalog, self.runs, self.task, now=NOW)

    def test_objectives_and_precedence(self):
        self.assertEqual(self.route()['selected']['id'], 'cheap')
        self.catalog['policy']['objective'] = 'quality'
        self.assertEqual(self.route()['selected']['id'], 'best')
        self.task['objective'] = 'latency'
        result = self.route()
        self.assertEqual((result['objective'], result['selected']['id']), ('latency', 'fast'))
        fast = next(c for c in result['candidates'] if c['candidate_id'] == 'fast')
        self.assertEqual(fast['evidence_run_ids'], ['fast-0', 'fast-1'])

    def test_unknown_cost_and_limits(self):
        for run in self.runs:
            if run['candidate_id'] == 'best':
                run['total_cost_usd'] = None
                run['total_duration_seconds'] = 1
        for objective in ('latency', 'quality'):
            self.task['objective'] = objective
            self.assertEqual(self.route()['selected']['id'], 'best')
            self.task['max_mean_cost_usd'] = 5
            self.assertNotEqual(self.route()['selected']['id'], 'best')
            del self.task['max_mean_cost_usd']
        self.task['objective'] = 'cost'
        result = self.route()
        self.assertNotEqual(result['selected']['id'], 'best')
        self.assertIn('unknown_cost', next(c for c in result['candidates'] if c['candidate_id'] == 'best')['reasons'])

    def test_allowed_intersection_and_fallback(self):
        extra = copy.deepcopy(self.runs[0])
        extra.update(id='new-0', candidate_id='new', model='new')
        self.runs.append(extra)
        self.task.update(objective='quality', allowed_candidates=['cheap', 'fast', 'best'])
        result = self.route()
        self.assertEqual(result['common_cases'], ['case-0', 'case-1'])
        self.assertEqual(result['selected']['id'], 'best')
        excluded = next(c for c in result['candidates'] if c['candidate_id'] == 'new')
        self.assertIn('not_available_or_allowed', excluded['reasons'])
        self.assertEqual(excluded['evidence_run_ids'], [])
        self.task['allowed_candidates'] = []
        result = self.route()
        self.assertEqual((result['status'], result['reason']), ('review_required', 'fallback_not_available_or_allowed'))
        self.task['allowed_candidates'] = ['new']
        self.assertEqual(self.route()['status'], 'review_required')
        self.task['allowed_candidates'] = ['cheap', 'new']
        self.assertEqual(self.route()['status'], 'fallback')

    def test_invalid_inputs(self):
        for value in ('bad', None, [], 1):
            with self.subTest(objective=value), self.assertRaises(ValidationError):
                validate_task(dict(self.task, objective=value))
            with self.assertRaises(ValidationError):
                validate_catalog(dict(self.catalog, policy=dict(self.catalog['policy'], objective=value)))
        for value in (None, 'cheap', ['cheap', 'cheap'], ['missing'], [1]):
            with self.subTest(allowed=value), self.assertRaises(ValidationError):
                evaluate(self.catalog, self.runs, dict(self.task, allowed_candidates=value), now=NOW)

    def test_unconfirmed_configuration_is_not_performance_evidence(self):
        for run in self.runs:
            run.pop('configuration_confirmed')
        result = self.route()
        self.assertEqual(result['status'], 'fallback')
        self.assertEqual(result['common_cases'], [])


if __name__ == '__main__':
    unittest.main()
