"""Evaluate model configurations against complete, evidenced task runs."""

from datetime import datetime, timedelta, timezone
import math


class ValidationError(ValueError):
    """Input is malformed or inconsistent with the candidate catalog."""


def _object(value, name):
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be an object")
    return value


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")
    return value


def _bool(value, name):
    if type(value) is not bool:
        raise ValidationError(f"{name} must be a boolean")
    return value


def _number(value, name, *, nullable=False):
    if value is None and nullable:
        return None
    try:
        valid = type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        valid = False
    if not valid:
        raise ValidationError(f"{name} must be a finite non-negative number")
    return value


def _date(value, name):
    _text(value, name)
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValidationError(f"{name} must be an ISO UTC date") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValidationError(f"{name} must include the UTC timezone")
    return parsed.astimezone(timezone.utc)


def validate_catalog(catalog):
    """Validate the candidate catalog, policy, and fallback reference."""
    _object(catalog, 'catalog')
    if type(catalog.get('schema_version')) is not int or catalog['schema_version'] != 1:
        raise ValidationError('catalog.schema_version must be 1')
    _bool(catalog.get('synthetic'), 'catalog.synthetic')
    candidates = catalog.get('candidates')
    if not isinstance(candidates, list) or not candidates:
        raise ValidationError('catalog.candidates must be a non-empty array')
    ids = set()
    for candidate in candidates:
        _object(candidate, 'candidate')
        for key in ('id', 'model', 'effort', 'harness'):
            _text(candidate.get(key), f'candidate.{key}')
        if candidate['id'] in ids:
            raise ValidationError(f"duplicate candidate id: {candidate['id']}")
        ids.add(candidate['id'])
    if not isinstance(catalog.get('fallback'), str) or catalog['fallback'] not in ids:
        raise ValidationError('catalog.fallback must name a candidate')
    policy = _object(catalog.get('policy'), 'catalog.policy')
    if type(policy.get('min_cases')) is not int or policy['min_cases'] < 1:
        raise ValidationError('policy.min_cases must be a positive integer')
    rate = _number(policy.get('min_pass_rate'), 'policy.min_pass_rate')
    if rate > 1:
        raise ValidationError('policy.min_pass_rate must be at most 1')
    _number(policy.get('max_age_days'), 'policy.max_age_days')
    return catalog


def validate_task(task):
    """Validate task classification, matching fields, and optional limits."""
    _object(task, 'task')
    for key in ('id', 'family', 'harness', 'rubric'):
        _text(task.get(key), f'task.{key}')
    if task.get('risk') not in ('low', 'medium', 'high'):
        raise ValidationError('task.risk must be low, medium, or high')
    _bool(task.get('classification_confirmed'), 'task.classification_confirmed')
    for key in ('max_mean_cost_usd', 'max_mean_duration_seconds'):
        if key in task:
            _number(task[key], f'task.{key}')
    return task


def _validate_runs(runs, candidates, now):
    if not isinstance(runs, list):
        raise ValidationError('runs must be an array')
    seen = set()
    for index, run in enumerate(runs):
        prefix = f'runs[{index}]'
        _object(run, prefix)
        for key in ('id', 'case_id', 'family', 'harness', 'rubric', 'candidate_id',
                    'model', 'effort', 'evidence'):
            _text(run.get(key), f'{prefix}.{key}')
        if run['id'] in seen:
            raise ValidationError(f"duplicate run id: {run['id']}")
        seen.add(run['id'])
        if run.get('risk') not in ('low', 'medium', 'high'):
            raise ValidationError(f'{prefix}.risk is invalid')
        _bool(run.get('passed'), f'{prefix}.passed')
        for key in ('total_cost_usd', 'total_duration_seconds'):
            if key not in run:
                raise ValidationError(f'{prefix}.{key} is required (null if unknown)')
            _number(run[key], f'{prefix}.{key}', nullable=True)
        timestamp = _date(run.get('completed_at'), f'{prefix}.completed_at')
        if timestamp > now:
            raise ValidationError(f'{prefix}.completed_at is in the future')
        if run.get('source') not in ('observed', 'synthetic'):
            raise ValidationError(f'{prefix}.source is invalid')
        candidate = candidates.get(run['candidate_id'])
        if candidate is None:
            raise ValidationError(f'{prefix} references an unknown candidate')
        if any(run[key] != candidate[key] for key in ('model', 'effort', 'harness')):
            raise ValidationError(f'{prefix} does not match its candidate configuration')


def _mean(values):
    return math.fsum(v / len(values) for v in values) if values and all(v is not None for v in values) else None


def evaluate(catalog, runs, task, *, allow_synthetic=False, now=None):
    """Compare common cases; empirical thresholds do not guarantee future quality."""
    validate_catalog(catalog)
    validate_task(task)
    _bool(allow_synthetic, 'allow_synthetic')
    if catalog['synthetic'] and not allow_synthetic:
        raise ValidationError('synthetic catalog is for simulation only; explicitly allow synthetic evidence')
    if now is None:
        now = datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() != timedelta(0):
        raise ValidationError('now must be a timezone-aware UTC datetime')
    now = now.astimezone(timezone.utc)
    candidates = {c['id']: c for c in catalog['candidates']}
    _validate_runs(runs, candidates, now)
    try:
        cutoff = now - timedelta(days=catalog['policy']['max_age_days'])
    except OverflowError:
        cutoff = datetime.min.replace(tzinfo=timezone.utc)
    grouped = {cid: {} for cid in candidates}
    for run in runs:
        if (any(run[k] != task[k] for k in ('family', 'risk', 'harness', 'rubric'))
                or _date(run['completed_at'], 'completed_at') < cutoff
                or (run['source'] == 'synthetic' and not allow_synthetic)):
            continue
        grouped[run['candidate_id']].setdefault(run['case_id'], []).append(run)
    covered = [cid for cid, cases in grouped.items() if cases]
    common = sorted(set.intersection(*(set(grouped[cid]) for cid in covered))) if covered else []
    results = []
    policy = catalog['policy']
    for cid, candidate in candidates.items():
        cases = grouped[cid]
        selected_cases = [cases[case] for case in common] if cases else []
        n = len(selected_cases)
        pass_rate = (sum(all(r['passed'] for r in case) for case in selected_cases) / n) if n else None
        cost = _mean([_mean([r['total_cost_usd'] for r in case]) for case in selected_cases])
        duration = _mean([_mean([r['total_duration_seconds'] for r in case]) for case in selected_cases])
        reasons = []
        if candidate['harness'] != task['harness']:
            reasons.append('harness_mismatch')
        if not cases:
            reasons.append('no_matching_evidence')
        if n < policy['min_cases']:
            reasons.append('insufficient_common_cases')
        if pass_rate is None or pass_rate < policy['min_pass_rate']:
            reasons.append('pass_rate_below_threshold')
        if cost is None:
            reasons.append('unknown_cost')
        if 'max_mean_cost_usd' in task and (cost is None or cost > task['max_mean_cost_usd']):
            reasons.append('cost_limit_unproven_or_exceeded')
        if 'max_mean_duration_seconds' in task and (duration is None or duration > task['max_mean_duration_seconds']):
            reasons.append('duration_limit_unproven_or_exceeded')
        results.append({'candidate_id': cid, 'n': n, 'pass_rate': pass_rate,
                        'mean_total_cost_usd': cost, 'mean_total_duration_seconds': duration,
                        'reasons': reasons})
    eligible = [r for r in results if not r['reasons']]
    limitations = ['Thresholds are empirical and do not guarantee future quality.',
                   'Costs and durations cover recorded complete task runs only.']
    if len(covered) == 1:
        limitations.append('Only one candidate has matching evidence; no comparative advantage is established.')
    if allow_synthetic:
        limitations.append('Synthetic evidence is allowed; this result is a simulation.')
    fallback = candidates[catalog['fallback']]
    fallback_result = next(r for r in results if r['candidate_id'] == fallback['id'])
    limits = ('max_mean_cost_usd' in task or 'max_mean_duration_seconds' in task)
    if task['risk'] == 'high' or not task['classification_confirmed']:
        status, selected, reason = 'review_required', None, 'risk_or_classification_requires_review'
    elif eligible:
        winner = min(eligible, key=lambda r: (r['mean_total_cost_usd'],
                                               r['mean_total_duration_seconds'] if r['mean_total_duration_seconds'] is not None else math.inf,
                                               r['candidate_id']))
        status, selected, reason = 'selected', candidates[winner['candidate_id']], 'lowest_eligible_mean_cost'
    elif fallback['harness'] != task['harness']:
        status, selected, reason = 'review_required', None, 'fallback_harness_mismatch'
    elif limits and fallback_result['reasons']:
        status, selected, reason = 'review_required', None, 'fallback_limits_or_quality_unproven'
    else:
        status, selected, reason = 'fallback', fallback, 'no_eligible_candidate'
    return {'status': status, 'selected': selected, 'reason': reason, 'candidates': results,
            'common_cases': common, 'limitations': limitations, 'simulation': allow_synthetic}
