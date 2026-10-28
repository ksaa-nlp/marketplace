"""Package checks for ksaa-jisr — no network, Python standard library only (3.8+).

Pins what the plugin promises: one keyless remote MCP server; three model-invoked
skills whose descriptions stay short (they load on every turn) and whose tool
references are real; a user-only `setup`; and its registration in the marketplace.
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
ARABIC = re.compile(r"[؀-ۿ]")

MODEL_SKILLS = ["arabic-word", "arabic-usage", "ksaa-resources"]
USER_SKILLS = ["setup"]

# The server's tools (https://mcp.arai.center). A skill naming anything else
# would send Claude searching for a tool that does not exist.
KNOWN_TOOLS = {
    "siwar_list_lexicons", "siwar_resolve_lemma", "siwar_get_word_meaning",
    "siwar_get_word_examples", "siwar_get_word_translations", "siwar_get_word_root",
    "siwar_get_word_pattern", "siwar_get_word_pos", "siwar_get_word_forms",
    "siwar_get_synonyms", "siwar_get_antonyms", "siwar_get_sense_relations",
    "siwar_search_by_root", "siwar_get_derivatives", "siwar_get_full_entry",
    "siwar_compare_words", "siwar_get_word_audio",
    "falak_list_corpora", "falak_get_corpus", "falak_concordance", "falak_collocations",
    "falak_ngrams", "falak_most_frequent", "falak_frequency_lists",
    "falak_corpus_statistics", "falak_search_sentences", "falak_stop_words",
    "balsam_leaderboard", "balsam_list_categories", "balsam_list_models", "balsam_list_tasks",
    "marsad_overview", "marsad_get_chapter", "marsad_search_report",
    "games_list_games", "games_get_game", "games_list_leagues",
    "library_search", "library_get_item", "library_journals", "library_contacts",
    "almustashar_search_bank", "almustashar_get_consultation",
    "almustashar_consultants", "almustashar_overview",
    "acronymer_search_registry", "acronymer_expand", "acronymer_guide",
    "list_platforms", "describe_platform", "search_platform_help",
}
TOOL_REF = re.compile(
    r"\b((?:siwar|falak|balsam|marsad|games|library|almustashar|acronymer)_[a-z_]+"
    r"|list_platforms|describe_platform|search_platform_help)\b"
)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "{} has no frontmatter".format(path)
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields, text[match.end():]


def skill_files(name):
    root = PLUGIN / "skills" / name
    return [root / "SKILL.md"] + sorted((root / "references").glob("*.md"))


class Manifest(unittest.TestCase):
    def test_plugin_json(self):
        data = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "ksaa-jisr")
        self.assertRegex(data["version"], r"^\d+\.\d+\.\d+$")
        self.assertRegex(data["description"], ARABIC)
        self.assertEqual(data["license"], "MIT")
        self.assertTrue((PLUGIN / "LICENSE").exists())

    def test_mcp_server_is_one_keyless_https_endpoint(self):
        servers = json.loads((PLUGIN / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(list(servers), ["ksaa"])
        server = servers["ksaa"]
        self.assertEqual(server["type"], "http")
        # The exact URL of the public connector, so Claude de-duplicates the two.
        self.assertEqual(server["url"], "https://mcp.arai.center/mcp")
        self.assertFalse({"headers", "headersHelper", "env"} & set(server), "no credentials in the plugin")


class Skills(unittest.TestCase):
    def test_model_invoked_skills(self):
        for name in MODEL_SKILLS:
            fields, _ = frontmatter(PLUGIN / "skills" / name / "SKILL.md")
            self.assertEqual(fields["name"], name)
            self.assertRegex(fields["description"], ARABIC)
            # Loaded on every turn: keep it short.
            self.assertLess(len(fields["description"]), 400, name)
            self.assertNotIn("disable-model-invocation", fields, name)

    def test_setup_costs_nothing_until_run(self):
        for name in USER_SKILLS:
            fields, _ = frontmatter(PLUGIN / "skills" / name / "SKILL.md")
            self.assertEqual(fields["name"], name)
            self.assertEqual(fields.get("disable-model-invocation"), "true")

    def test_referenced_files_exist(self):
        for name in MODEL_SKILLS + USER_SKILLS:
            root = PLUGIN / "skills" / name
            _, body = frontmatter(root / "SKILL.md")
            for ref in re.findall(r"`(references/[^`]+)`", body):
                self.assertTrue((root / ref).exists(), "{}: {}".format(name, ref))

    def test_tools_named_by_bare_name_and_real(self):
        for name in MODEL_SKILLS + USER_SKILLS:
            for path in skill_files(name):
                text = path.read_text(encoding="utf-8")
                # A server prefix differs between the plugin and a claude.ai connector.
                self.assertNotIn("mcp__", text, str(path))
                for tool in TOOL_REF.findall(text):
                    self.assertIn(tool, KNOWN_TOOLS, "{}: {}".format(path.name, tool))


@unittest.skipUnless(MARKETPLACE.exists(), "outside the marketplace repository")
class Registration(unittest.TestCase):
    def test_marketplace_entry(self):
        plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        entries = [p for p in json.loads(MARKETPLACE.read_text(encoding="utf-8"))["plugins"]
                   if p["name"] == "ksaa-jisr"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], "./plugins/ksaa-jisr")
        self.assertEqual(entries[0]["version"], plugin["version"])
        self.assertRegex(entries[0]["description"], ARABIC)

    def test_readme_and_agents(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`ksaa-jisr`](plugins/ksaa-jisr/)", readme)
        self.assertIn("/ksaa-jisr:", readme)
        self.assertIn("plugins/ksaa-jisr", (REPO / "AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
