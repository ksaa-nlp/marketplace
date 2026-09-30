"""Tests for scripts/sync_tokens.py build logic (no network, no npm)."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts/sync_tokens.py"
spec = importlib.util.spec_from_file_location("sync_tokens", SCRIPT)
sync_tokens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_tokens)

FIXTURE = (
    "html,body{margin:0}"
    ":root{--spacing-4:16px;--radius-sm:4px}"
    "@media only screen and (max-width: 767px){:root{--card-md-padding:var(--spacing-4)}}"
    ".dga-btn{height:40px}"
    ".text-md-medium,.dga-btn--lg{font:500 16px/24px \"IBM Plex Sans Arabic\"}"
    ".display-xs-bold{font:700 24px/32px \"IBM Plex Sans Arabic\"}"
    "[data-theme=dark]{--background-white:#0c111b}"
)


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.out = sync_tokens.build(FIXTURE, "9.9.9")

    def test_header_names_source_and_version(self):
        self.assertIn("@platformscode/core@9.9.9", self.out)
        self.assertIn("MIT", self.out)

    def test_token_blocks_kept_with_media_context(self):
        self.assertIn("--spacing-4:16px;", self.out)
        self.assertIn("@media only screen and (max-width: 767px) {", self.out)
        self.assertIn("[data-theme=dark] {", self.out)

    def test_only_typography_utilities_extracted(self):
        self.assertIn(".text-md-medium {", self.out)
        self.assertIn(".display-xs-bold {", self.out)
        self.assertNotIn("dga-btn", self.out)
        self.assertNotIn("margin:0", self.out)

    def test_bundled_asset_is_complete(self):
        asset = (SCRIPT.parent.parent / "skills/dga-design/assets/dga-tokens.css").read_text(encoding="utf-8")
        import re
        defined = set(re.findall(r"(--[\w-]+)\s*:", asset))
        used = set(re.findall(r"var\((--[\w-]+)", asset))
        self.assertEqual(used - defined, set())
        self.assertEqual(len(re.findall(r"^\.(?:display|text)-[a-z0-9]+-[a-z]+ \{", asset, re.M)), 48)


if __name__ == "__main__":
    unittest.main()
