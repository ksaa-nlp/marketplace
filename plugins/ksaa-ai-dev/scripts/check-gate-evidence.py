#!/usr/bin/env python3
"""يفحص اتساق سجل الأدلة المعلن فقط؛ لا يصادق على صحتها أو يمنح صلاحية."""
import argparse
import datetime as dt
import json
from pathlib import Path

GATES = {'lint', 'unit', 'integration', 'sast', 'dependency', 'secrets', 'human-review', 'ci-cd'}
STATUSES = {'passed', 'failed', 'not-run', 'blocked', 'skipped', 'exception'}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be string')
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timezone required')
    return parsed


def nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and not value.strip().startswith('[')


def check(report, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    errors = []
    if not isinstance(report, dict):
        return ['report must be an object']
    if type(report.get('schema-version')) is not int or report.get('schema-version') != 1:
        errors.append('unsupported schema-version')
    revision = report.get('revision')
    if not nonempty(revision):
        errors.append('revision required')
    gates = report.get('gates')
    if not isinstance(gates, list) or any(not isinstance(g, dict) for g in gates):
        return errors + ['gates must be objects in an array']
    ids = [g.get('id') for g in gates]
    if any(not isinstance(i, str) for i in ids) or len(ids) != len(set(str(i) for i in ids)) or set(str(i) for i in ids) != GATES:
        errors.append('all eight distinct gate IDs required')
    for gate in gates:
        name = str(gate.get('id', 'unknown'))
        status = gate.get('status')
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(name + ': invalid status')
            continue
        if status not in {'passed', 'exception'}:
            errors.append(name + ': blocking status ' + status)
            continue
        evidence = gate.get('evidence')
        if not isinstance(evidence, dict):
            errors.append(name + ': evidence required')
            continue
        for field in ('method', 'environment', 'executed-at', 'artifact', 'result', 'revision'):
            if not nonempty(evidence.get(field)):
                errors.append(name + ': evidence.' + field + ' required')
        if evidence.get('revision') != revision:
            errors.append(name + ': evidence revision mismatch')
        try:
            if timestamp(evidence.get('executed-at')) > now:
                errors.append(name + ': evidence is in the future')
        except (ValueError, TypeError):
            errors.append(name + ': evidence timestamp invalid')
        if status == 'passed' and evidence.get('result') != 'passed':
            errors.append(name + ': passed status contradicts result')
        if name == 'human-review':
            approval = gate.get('human-decision', {})
            if not isinstance(approval, dict) or approval.get('decision') != 'accepted' or not all(nonempty(approval.get(f)) for f in ('reviewer', 'artifact')):
                errors.append(name + ': declared human acceptance and source required')
        if name == 'ci-cd':
            if not nonempty(gate.get('enforcement-evidence')):
                errors.append(name + ': declared required-check/protection evidence required')
        if status == 'exception':
            if evidence.get('result') != 'failed':
                errors.append(name + ': exception must preserve original failed result')
            ex = gate.get('exception', {})
            if name != 'sast':
                errors.append(name + ': only scoped SAST exception supported by this conservative checker')
            if not isinstance(ex, dict):
                errors.append(name + ': exception must be an object')
                continue
            for field in ('policy', 'approved-by', 'security-reviewer', 'approval-artifact', 'reason', 'mitigation', 'scope', 'expires-at'):
                if not nonempty(ex.get(field)):
                    errors.append(name + ': exception.' + field + ' required')
            if ex.get('revision') != revision:
                errors.append(name + ': exception revision mismatch')
            try:
                if timestamp(ex.get('expires-at')) <= now:
                    errors.append(name + ': exception expired')
            except (ValueError, TypeError):
                errors.append(name + ': exception expiry invalid')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        errors = check(json.loads(args.report.read_text(encoding='utf-8')))
    except (OSError, ValueError) as exc:
        errors = ['invalid report: ' + str(exc)]
    for error in errors:
        print('BLOCKED:', error)
    if not errors:
        print('CONSISTENT: declared evidence only; verify sources, human authority and live controls separately. No merge/deploy permission granted.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
