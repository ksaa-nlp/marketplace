"""Package tests: manifest, marketplace registration, packaged paths, provenance and documentation parity."""
import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
SKILL = PLUGIN / "skills" / "project-brief"
CLI = SKILL / "scripts" / "brief.py"
SOURCE_COMMIT = "a4d95ccca1a265ea71f3611ec394cd8cdd95f7c9"
SOURCE_BRIEF_SHA256 = "fe7dde753b8b83182bbb3a88139beb81a1055b68b1a28bccb9f47a3496151c3c"
ARABIC = re.compile(r"[؀-ۿ]")

spec = importlib.util.spec_from_file_location("brief", CLI)
brief = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brief)


def text(path):
    return path.read_text(encoding="utf-8")


def lf_sha256(path):
    # Checkouts may convert line endings, so hashes are recorded for LF text.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.plugin = json.loads(text(PLUGIN / ".claude-plugin" / "plugin.json"))
        match = re.match(r"---\n(.*?)\n---\n(.*)", text(SKILL / "SKILL.md"), re.S)
        self.frontmatter, self.body = match.groups()

    def test_plugin_manifest(self):
        self.assertEqual(self.plugin["name"], "project-brief")
        self.assertRegex(self.plugin["version"], r"^\d+\.\d+\.\d+$")
        self.assertRegex(self.plugin["description"], ARABIC)
        self.assertNotIn("license", self.plugin, "The source declares no license; record the owners' decision in UPSTREAM.md first")

    def test_marketplace_registration_readme_and_map(self):
        market = json.loads(text(REPO / ".claude-plugin" / "marketplace.json"))
        entries = [p for p in market["plugins"] if p["name"] == "project-brief"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], "./plugins/project-brief")
        self.assertEqual(entries[0]["version"], self.plugin["version"])
        self.assertRegex(entries[0]["description"], ARABIC)
        readme = text(REPO / "README.md")
        self.assertIn("[`project-brief`](plugins/project-brief/)", readme)
        self.assertIn("/project-brief:project-brief", readme)
        self.assertIn("plugins/project-brief", text(REPO / "AGENTS.md"))

    def test_skill_is_small_and_its_paths_exist(self):
        self.assertRegex(self.frontmatter, r"(?m)^name: project-brief$")
        description = re.search(r"(?m)^description: (.*)$", self.frontmatter).group(1)
        self.assertLess(len(description), 400, "the description is loaded in every turn")
        for ref in set(re.findall(r"`((?:references|scripts|assets)/[^`*<>\s]+)`", self.body)):
            self.assertTrue((SKILL / ref).exists(), ref)

    def test_only_read_only_commands_are_pre_approved(self):
        rules = re.findall(r"- 'Bash\((.*)\)'", self.frontmatter)
        self.assertEqual(len(rules), 4)
        for rule in rules:
            self.assertRegex(rule, r'^python3? "\$\{CLAUDE_SKILL_DIR\}/scripts/brief\.py" (check|export) \*$')
        # Command text in the body must use the same quoting as the rules, or the rules never match.
        self.assertIn('`python3 "${CLAUDE_SKILL_DIR}/scripts/brief.py" <', self.body)
        self.assertIn('`python3 "${CLAUDE_SKILL_DIR}/scripts/brief.py" export --root "R"', self.body)

    def test_starter_assets_match_init(self):
        for language, asset in (("en", "brief.md"), ("ar", "brief.ar.md")):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                brief.init(root, "project-brief.json", "brief.md", language, project="Example project")
                self.assertEqual(text(root / "brief.md"), text(SKILL / "assets" / "starter" / asset))
                if language == "en":
                    self.assertEqual(json.loads(text(root / "project-brief.json")),
                                     json.loads(text(SKILL / "assets" / "starter" / "project-brief.json")))

    def test_provenance_records_source_and_current_core(self):
        upstream = text(PLUGIN / "UPSTREAM.md")
        self.assertIn(SOURCE_COMMIT, upstream)
        self.assertIn(SOURCE_BRIEF_SHA256, upstream)
        self.assertIn(lf_sha256(CLI), upstream,
                      "brief.py changed: record the change and its LF SHA-256 in UPSTREAM.md, "
                      "bump the plugin version, and follow the Awn sync steps there")

    def test_contract_docs_cover_the_cli_in_both_languages(self):
        source = text(CLI)
        options = re.findall(r"add_argument\('(--[a-z-]+)'", source)
        commands = re.findall(r"'(\w+)'", re.search(r"choices=\[('check'[^\]]*)\]", source).group(1))
        issues = ["not-reviewed", "content-changed", "primary-changed", "evidence-changed", "claims-changed"]
        fields = ["primary_language", "visibility", "variants", "direction", "block", "evidence", "reviewed_reference",
                  "claims", "max_chars", "audience", "perspective", "priorities", "delivery", "extensions",
                  "with-primary", "on-request", "project-brief:start", "project-brief:end"]
        self.assertEqual(len(options), 11)
        for doc in ("contract.md", "contract.en.md"):
            body = text(SKILL / "references" / doc)
            for token in options + commands + issues + fields:
                self.assertIn(token, body, doc + ": " + token)


if __name__ == "__main__":
    unittest.main()
