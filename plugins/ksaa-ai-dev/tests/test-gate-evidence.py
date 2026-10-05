"""اختبارات اتساق أدلة اصطناعية؛ ليست موافقات أو نتائج CI حقيقية."""
import copy
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gate_checker', PLUGIN / 'scripts/check-gate-evidence.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
NOW = dt.datetime(2030, 1, 1, tzinfo=dt.timezone.utc)


def sample():
    report = {'schema-version': 1, 'revision': 'synthetic-revision', 'gates': []}
    for name in sorted(checker.GATES):
        gate = {'id': name, 'status': 'passed', 'evidence': {
            'method': 'synthetic fixture only', 'environment': 'isolated-fixture',
            'executed-at': '2029-12-31T10:00:00Z', 'artifact': 'fixture://report',
            'result': 'passed', 'revision': report['revision']}}
        if name == 'human-review':
            gate['human-decision'] = {'decision': 'accepted', 'reviewer': 'synthetic-reviewer', 'artifact': 'fixture://decision'}
        if name == 'ci-cd': gate['enforcement-evidence'] = 'fixture://required-checks'
        report['gates'].append(gate)
    return report


def select(report, gate_id):
    return next(g for g in report['gates'] if g['id'] == gate_id)


def add_exception(report):
    gate = select(report, 'sast')
    gate['status'] = 'exception'; gate['evidence']['result'] = 'failed'
    gate['exception'] = {'policy': 'fixture://policy', 'approved-by': 'synthetic-owner',
                         'security-reviewer': 'synthetic-security-reviewer',
                         'approval-artifact': 'fixture://approval', 'reason': 'synthetic case',
                         'mitigation': 'isolated fixture', 'scope': 'fixture only',
                         'expires-at': '2030-01-02T00:00:00Z', 'revision': report['revision']}


class EvidenceTests(unittest.TestCase):
    def test_complete_declared_evidence_consistent(self):
        self.assertEqual(checker.check(sample(), NOW), [])

    def test_incomplete_template_blocked(self):
        import json
        data = json.loads((PLUGIN / 'templates/gate-evidence.json').read_text())
        self.assertTrue(checker.check(data, NOW))

    def test_failed_notrun_skipped_blocked_remain_blocking(self):
        for status in ('failed', 'not-run', 'blocked', 'skipped'):
            with self.subTest(status=status):
                data = sample(); select(data, 'unit')['status'] = status
                self.assertTrue(any('blocking status' in e for e in checker.check(data, NOW)))

    def test_missing_gate_blocked(self):
        data = sample(); data['gates'].pop()
        self.assertTrue(checker.check(data, NOW))

    def test_duplicate_gate_blocked(self):
        data = sample(); data['gates'].append(copy.deepcopy(data['gates'][0]))
        self.assertTrue(checker.check(data, NOW))

    def test_pass_without_evidence_blocked(self):
        data = sample(); del select(data, 'unit')['evidence']
        self.assertTrue(checker.check(data, NOW))

    def test_old_revision_blocked(self):
        data = sample(); select(data, 'ci-cd')['evidence']['revision'] = 'other-revision'
        self.assertTrue(any('revision mismatch' in e for e in checker.check(data, NOW)))

    def test_future_execution_blocked(self):
        data = sample(); select(data, 'unit')['evidence']['executed-at'] = '2031-01-01T00:00:00Z'
        self.assertTrue(checker.check(data, NOW))

    def test_timestamp_without_timezone_blocked(self):
        data = sample(); select(data, 'unit')['evidence']['executed-at'] = '2029-12-31T10:00:00'
        self.assertTrue(checker.check(data, NOW))

    def test_result_contradiction_blocked(self):
        data = sample(); select(data, 'unit')['evidence']['result'] = 'failed'
        self.assertTrue(checker.check(data, NOW))

    def test_missing_human_decision_blocked(self):
        data = sample(); del select(data, 'human-review')['human-decision']
        self.assertTrue(checker.check(data, NOW))

    def test_conditional_acceptance_not_merge_ready(self):
        data = sample(); select(data, 'human-review')['human-decision']['decision'] = 'conditional'
        self.assertTrue(checker.check(data, NOW))

    def test_unverified_protection_blocked(self):
        data = sample(); del select(data, 'ci-cd')['enforcement-evidence']
        self.assertTrue(checker.check(data, NOW))

    def test_documented_scoped_sast_exception_consistent(self):
        data = sample(); add_exception(data)
        self.assertEqual(checker.check(data, NOW), [])

    def test_exception_requires_policy_security_and_human_source(self):
        for field in ('policy', 'approved-by', 'security-reviewer', 'approval-artifact'):
            data = sample(); add_exception(data)
            del select(data, 'sast')['exception'][field]
            self.assertTrue(checker.check(data, NOW))

    def test_expired_exception_blocked(self):
        data = sample(); add_exception(data)
        select(data, 'sast')['exception']['expires-at'] = '2029-12-31T00:00:00Z'
        self.assertTrue(any('expired' in e for e in checker.check(data, NOW)))

    def test_exception_does_not_make_failed_result_pass(self):
        data = sample(); add_exception(data)
        select(data, 'sast')['evidence']['result'] = 'passed'
        self.assertTrue(checker.check(data, NOW))

    def test_non_sast_exception_blocked(self):
        data = sample(); add_exception(data)
        select(data, 'unit')['exception'] = copy.deepcopy(select(data, 'sast')['exception'])
        select(data, 'unit')['status'] = 'exception'; select(data, 'unit')['evidence']['result'] = 'failed'
        self.assertTrue(any('only scoped SAST' in e for e in checker.check(data, NOW)))

    def test_malformed_json_types_fail_closed(self):
        for report in ([], None, {'schema-version': True}, {'schema-version': 1, 'gates': [None]},
                       {'schema-version': 1, 'gates': [{'id': [], 'status': []}]},
                       {'schema-version': 1, 'gates': [{'id': 'unit', 'status': 'passed', 'evidence': []}]}):
            self.assertTrue(checker.check(report, NOW))


if __name__ == '__main__':
    unittest.main()
