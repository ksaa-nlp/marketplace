"""اختبارات بنيوية سلبية؛ لا تشغّل Claude أو مشاريع المستخدم."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / 'plugins/ksaa-ai-dev'
spec = importlib.util.spec_from_file_location('validate_plugin', PLUGIN / 'scripts/validate-plugin.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'marketplace'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        self.plugin = self.root / 'plugins/ksaa-ai-dev'

    def test_real_package_passes(self):
        self.assertEqual(validator.validate(self.root), [])

    def test_original_unquoted_colon_regression(self):
        for name in ('ksaa-govern', 'ksaa-measure'):
            text = '---\nname: %s\ndescription: وصف عربي: سياق غير مقتبس\n---\n\nمحتوى\n' % name
            self.assertTrue(any('JSON-quoted' in e for e in validator.frontmatter(text, name)))

    def test_quoted_colon_is_valid(self):
        text = '---\nname: ksaa-govern\ndescription: "وصف عربي: سياق مقتبس"\n---\n\nمحتوى\n'
        self.assertEqual(validator.frontmatter(text, 'ksaa-govern'), [])

    def test_duplicate_frontmatter_rejected(self):
        text = '---\nname: ksaa-govern\nname: ksaa-govern\ndescription: "عربي"\n---\nمحتوى'
        self.assertTrue(validator.frontmatter(text, 'ksaa-govern'))

    def test_nonstring_description_rejected(self):
        text = '---\nname: ksaa-govern\ndescription: ["عربي"]\n---\nمحتوى'
        self.assertTrue(validator.frontmatter(text, 'ksaa-govern'))

    def test_version_mismatch_rejected(self):
        path = self.plugin / '.claude-plugin/plugin.json'
        data = json.loads(path.read_text())
        data['version'] = '9.9.9'
        path.write_text(json.dumps(data))
        self.assertTrue(any('version mismatch' in e for e in validator.validate(self.root)))

    def test_invalid_name_even_in_both_manifests(self):
        p = self.plugin / '.claude-plugin/plugin.json'
        data = json.loads(p.read_text()); data['name'] = 'Bad Plugin'
        p.write_text(json.dumps(data))
        p = self.root / '.claude-plugin/marketplace.json'
        data = json.loads(p.read_text())
        for entry in data['plugins']:
            if entry['name'] == 'ksaa-ai-dev': entry['name'] = 'Bad Plugin'
        p.write_text(json.dumps(data))
        self.assertTrue(any('invalid' in e and 'name' in e for e in validator.validate(self.root)))

    def test_missing_linked_template_rejected(self):
        (self.plugin / 'templates/architecture-context.md').unlink()
        self.assertTrue(any('broken local link' in e for e in validator.validate(self.root)))

    def test_orphan_reference_rejected(self):
        (self.plugin / 'references/orphan.md').write_text('وثيقة غير قابلة للاكتشاف')
        self.assertTrue(any('undiscoverable' in e for e in validator.validate(self.root)))

    def test_escape_link_rejected(self):
        path = self.plugin / 'README.md'
        path.write_text(path.read_text() + '\n[مرجع خارجي محلي](../../AGENTS.md)\n')
        self.assertTrue(any('escapes plugin' in e for e in validator.validate(self.root)))

    def test_symlink_rejected(self):
        (self.plugin / 'references/linked.md').symlink_to(self.root / 'AGENTS.md')
        self.assertTrue(any('symlink' in e for e in validator.validate(self.root)))

    def test_private_repository_link_signal(self):
        path = self.plugin / 'README.md'
        path.write_text(path.read_text() + '\nhttps://github.com/ksaa-nlp/private-example/blob/main/config\n')
        self.assertTrue(any('public-safety' in e for e in validator.validate(self.root)))

    def test_internal_hostname_signal(self):
        path = self.plugin / 'README.md'
        path.write_text(path.read_text() + '\nhttps://example.internal/settings\n')
        self.assertTrue(any('public-safety' in e for e in validator.validate(self.root)))

    def test_baseline_deletion_rejected(self):
        baseline = Path(self.temp.name) / 'baseline'
        shutil.copytree(self.root, baseline)
        (self.root / 'plugins/dga-design/README.md').unlink()
        self.assertTrue(any('baseline file missing' in e for e in validator.check_baseline(self.root, baseline)))

    def test_baseline_instruction_edit_rejected(self):
        baseline = Path(self.temp.name) / 'baseline'
        shutil.copytree(self.root, baseline)
        (self.root / 'AGENTS.md').write_text('تعليمات بديلة')
        self.assertTrue(any('baseline file changed' in e for e in validator.check_baseline(self.root, baseline)))

    def test_baseline_readme_rewrite_rejected(self):
        baseline = Path(self.temp.name) / 'baseline'
        shutil.copytree(self.root, baseline)
        (self.root / 'README.md').write_text('دليل بديل')
        self.assertTrue(any('README' in e for e in validator.check_baseline(self.root, baseline)))


if __name__ == '__main__':
    unittest.main()
