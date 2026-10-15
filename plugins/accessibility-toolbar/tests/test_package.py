import hashlib
import json
import pathlib
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "accessibility-toolbar"
ZIP = ROOT / "downloads" / "accessibility-toolbar-v5.zip"


class AccessibilityToolbarPackageTests(unittest.TestCase):
    def test_plugin_manifest(self):
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "accessibility-toolbar")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["license"], "MIT")
        self.assertIn("haithamnaddaf", manifest["repository"])

    def test_skill_and_license_are_present(self):
        self.assertTrue((SKILL / "SKILL.md").is_file())
        self.assertTrue((SKILL / "LICENSE").is_file())
        self.assertTrue((ROOT / "LICENSE").is_file())

    def test_archive_hash_matches_manifest(self):
        expected = json.loads((ROOT / "downloads" / "manifest.json").read_text())["sha256"]
        actual = hashlib.sha256(ZIP.read_bytes()).hexdigest()
        self.assertEqual(actual, expected)

    def test_archive_has_exactly_twelve_source_files(self):
        with zipfile.ZipFile(ZIP) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
        self.assertEqual(len(names), 12)
        self.assertTrue(all(name.startswith("accessibility-toolbar/") for name in names))
        self.assertIn("accessibility-toolbar/SKILL.md", names)
        self.assertIn("accessibility-toolbar/assets/AccessibilityToolbar.tsx", names)

    def test_manifest_is_valid_json(self):
        data = json.loads((ROOT / "downloads" / "manifest.json").read_text())
        self.assertEqual(data["fileCount"], 12)
        self.assertEqual(data["source"]["license"], "MIT")

    def test_documentation_preserves_scope_limits(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertIn("React", text)
        self.assertIn("WCAG", text)
        self.assertIn("اختبار", text)

    def test_no_v2_archive_is_registered(self):
        manifest = (ROOT / "downloads" / "manifest.json").read_text()
        self.assertNotIn("v2", manifest.lower())


if __name__ == "__main__":
    unittest.main()
