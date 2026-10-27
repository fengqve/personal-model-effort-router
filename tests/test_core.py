import copy
import math
import unittest
from datetime import datetime, timezone

from fitmytask.core import ValidationError, evaluate, validate_catalog

NOW = datetime(2026, 10, 27, tzinfo=timezone.utc)


def catalog():
    return {'schema_version': 1, 'synthetic': False,
            'candidates': [{'id': 'a', 'model': 'm1', 'effort': 'low', 'harness': 'h'},
                           {'id': 'b', 'model': 'm2', 'effort': 'high', 'harness': 'h'}],
            'fallback': 'b', 'policy': {'min_cases': 2, 'min_pass_rate': 1.0, 'max_age_days': 30}}


def task(**kwargs):
    result = {'id': 't', 'family': 'f', 'risk': 'low', 'harness': 'h', 'rubric': 'r',
              'classification_confirmed': True}
    result.update(kwargs)
    return result


def run(candidate, case, cost=1, passed=True, **kwargs):
    c = next(x for x in catalog()['candidates'] if x['id'] == candidate)
    result = {'id': f'{candidate}-{case}', 'case_id': case, 'family': 'f', 'risk': 'low',
              'harness': 'h', 'rubric': 'r', 'candidate_id': candidate, 'model': c['model'],
              'effort': c['effort'], 'passed': passed, 'total_cost_usd': cost,
              'total_duration_seconds': 2, 'completed_at': '2026-10-26T00:00:00Z',
              'source': 'observed', 'evidence': 'local artifact'}
    result.update(kwargs)
    return result


def assess(runs, t=None, **kwargs):
    return evaluate(catalog(), runs, t or task(), now=NOW, **kwargs)


def metrics(result, candidate):
    return next(x for x in result['candidates'] if x['candidate_id'] == candidate)


class CoreTests(unittest.TestCase):
    def test_failure_cost_and_duplicates_are_included(self):
        runs = [run('a', '1', 1), run('a', '1', 9, False, id='retry'), run('a', '2', 1),
                run('b', '1', 4), run('b', '2', 4)]
        result = assess(runs)
        a = metrics(result, 'a')
        self.assertEqual((a['n'], a['pass_rate'], a['mean_total_cost_usd']), (2, .5, 3))
        self.assertEqual(result['selected']['id'], 'b')

    def test_common_cases_prevent_unfair_comparison(self):
        runs = [run('a', '1', 8), run('a', '2', 1), run('a', '3', 1),
                run('b', '1', 4), run('b', '2', 4)]
        result = assess(runs)
        self.assertEqual(result['common_cases'], ['1', '2'])
        self.assertEqual(metrics(result, 'a')['mean_total_cost_usd'], 4.5)
        self.assertEqual(result['selected']['id'], 'b')

    def test_disjoint_cases_and_duplicate_cases_do_not_meet_threshold(self):
        result = assess([run('a', '1'), run('a', '1', id='retry'), run('b', '2')])
        self.assertEqual(result['common_cases'], [])
        self.assertEqual(result['status'], 'fallback')
        result = assess([run('a', '1'), run('a', '1', id='retry')])
        self.assertEqual(metrics(result, 'a')['n'], 1)
        self.assertEqual(result['status'], 'fallback')

    def test_expired_and_synthetic_excluded(self):
        runs = [run('a', '1'), run('a', '2', completed_at='2026-09-01T00:00:00Z'),
                run('a', '3', source='synthetic')]
        result = assess(runs)
        self.assertEqual(metrics(result, 'a')['n'], 1)
        self.assertFalse(result['simulation'])
        result = assess(runs, allow_synthetic=True)
        self.assertEqual(metrics(result, 'a')['n'], 2)
        self.assertTrue(result['simulation'])
        self.assertEqual(result['status'], 'selected')

    def test_synthetic_catalog_requires_explicit_simulation(self):
        c = catalog()
        c['synthetic'] = True
        with self.assertRaises(ValidationError):
            evaluate(c, [], task(), now=NOW)
        self.assertTrue(evaluate(c, [], task(), now=NOW, allow_synthetic=True)['simulation'])

    def test_high_risk_and_unconfirmed_require_review(self):
        for t in (task(risk='high'), task(classification_confirmed=False)):
            result = assess([], t)
            self.assertEqual(result['status'], 'review_required')
            self.assertIsNone(result['selected'])

    def test_fallback_cannot_bypass_budget(self):
        self.assertEqual(assess([], task(max_mean_cost_usd=5))['status'], 'review_required')
        self.assertEqual(assess([], task(max_mean_duration_seconds=5))['status'], 'review_required')
        self.assertEqual(assess([], task(harness='different'))['status'], 'review_required')

    def test_missing_cost_cannot_win(self):
        result = assess([run('a', '1', None), run('a', '2', None),
                         run('b', '1', 4), run('b', '2', 4)])
        self.assertIsNone(metrics(result, 'a')['mean_total_cost_usd'])
        self.assertIn('unknown_cost', metrics(result, 'a')['reasons'])
        self.assertEqual(result['selected']['id'], 'b')

    def test_missing_duration_fails_duration_limit(self):
        result = assess([run('a', '1', total_duration_seconds=None),
                         run('a', '2', total_duration_seconds=None)], task(max_mean_duration_seconds=5))
        self.assertEqual(result['status'], 'review_required')

    def test_bad_catalog_numbers(self):
        for field, value in [('min_pass_rate', math.nan), ('max_age_days', math.inf),
                             ('min_cases', True), ('min_pass_rate', True)]:
            c = catalog()
            c['policy'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                validate_catalog(c)

    def test_bad_runs_fail_even_if_not_matching(self):
        base = run('a', '1', family='other')
        for field, value in [('passed', 1), ('total_cost_usd', math.nan),
                             ('total_duration_seconds', -1), ('evidence', ''),
                             ('candidate_id', 'unknown'), ('model', 'wrong'),
                             ('completed_at', '2026-10-28T00:00:00Z')]:
            bad = copy.deepcopy(base)
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValidationError):
                assess([bad])
        with self.assertRaises(ValidationError):
            assess([base, copy.deepcopy(base)])

    def test_single_candidate_no_comparative_claim(self):
        result = assess([run('a', '1'), run('a', '2')])
        self.assertEqual(result['selected']['id'], 'a')
        self.assertIn('no comparative advantage', ' '.join(result['limitations']))
        self.assertIn('no_matching_evidence', metrics(result, 'b')['reasons'])


if __name__ == '__main__':
    unittest.main()
