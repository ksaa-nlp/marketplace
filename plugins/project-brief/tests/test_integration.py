"""Integration tests: the packaged CLI driven from temporary consuming projects (no network, no credentials).

Fixtures exercise the tool, not a live Claude session or human usability.
"""
import ast
import contextlib
import importlib.util
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
CLI = PLUGIN / "skills" / "project-brief" / "scripts" / "brief.py"
spec = importlib.util.spec_from_file_location("brief", CLI)
brief = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brief)


def offline_env():
    # Drop credentials and Python overrides; any proxy-honouring network call would fail fast.
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith(("ANTHROPIC", "OPENAI", "CLAUDE", "PYTHON", "GIT_"))
           and k.upper() not in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY")}
    env.update(HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", ALL_PROXY="http://127.0.0.1:9")
    return env


def symlink(test, link, target, directory=False):
    try:
        os.symlink(str(target), str(link), target_is_directory=directory)
    except (OSError, NotImplementedError) as error:
        test.skipTest("symlinks unavailable: " + str(error))


class Project:
    """A consuming project whose path contains spaces and Arabic, outside any Git repository it owns."""

    def __init__(self, test, name="client project"):
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.root = self.base / "مشروع تجريبي" / name
        self.root.mkdir(parents=True)

    def write(self, name, text, newline="\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.replace("\n", newline).encode("utf-8"))
        return path

    def manifest(self, data=None, name="project-brief.json"):
        if data is not None:
            self.write(name, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return json.loads((self.root / name).read_text(encoding="utf-8"))

    def run(self, *args, root=None, cwd=None):
        # -I -S: no user or site packages, so only the standard library can be imported.
        command = [sys.executable, "-I", "-S", str(CLI)] + list(args) + ["--root", str(root or self.root)]
        done = subprocess.run(command, cwd=str(cwd or self.base), capture_output=True, env=offline_env(), timeout=60)
        return done.returncode, done.stdout.decode("utf-8"), done.stderr.decode("utf-8")

    def review(self, topic, language):
        code, out, err = self.run("review", "--topic", topic, "--language", language, "--acknowledge-reviewed")
        assert code == 0, err
        return out

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}


def topic(variants, visibility="public", evidence=(), claims=None):
    entry = {"visibility": visibility, "variants": variants, "evidence": [{"ref": r} for r in evidence]}
    if claims is not None:
        entry["claims"] = claims
    return entry


def variant(path, direction, block=None):
    v = {"path": path, "direction": direction}
    if block:
        v["block"] = block
    return v


class SetupTests(unittest.TestCase):
    def test_non_software_project_without_git_end_to_end(self):
        p = Project(self, "reading circle")
        self.assertFalse(any((d / ".git").exists() for d in [p.root] + list(p.root.parents)))
        code, out, err = p.run("init", "--language", "en", "--project", "Neighbourhood reading circle")
        self.assertEqual(code, 0, err)
        self.assertIn("created: brief.md", out)
        self.assertIn("created: project-brief.json", out)
        self.assertIn("direction=ltr", out)
        code, out, _ = p.run("check")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)[0]["needs_review"][0], "not-reviewed")
        code, _, err = p.run("export", "--recipe", "introduction")
        self.assertEqual(code, 2)
        self.assertIn("Review required", err)
        p.write("brief.md", "# Reading circle\n\nWeekly volunteer-led reading for children. "
                            "Three pilot sessions ran in September (locally tested); no permanent venue is agreed (unknown).\n")
        self.assertIn("not independent verification", p.review("purpose", "en"))
        self.assertEqual(p.run("check")[0], 0)
        code, out, err = p.run("export", "--recipe", "introduction")
        self.assertEqual(code, 0, err)
        self.assertIn("# Neighbourhood reading circle", out)
        self.assertIn("no permanent venue is agreed (unknown)", out)
        self.assertIn("<!-- Project Brief snapshot:", out)
        self.assertNotIn("REVIEW REQUIRED", out)

    def test_setup_is_idempotent_and_never_overwrites(self):
        p = Project(self)
        self.assertEqual(p.run("init", "--language", "en")[0], 0)
        first = p.snapshot()
        code, out, _ = p.run("init", "--language", "ar", "--content", "other.md")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "unchanged: project-brief.json")
        self.assertEqual(p.snapshot(), first)
        data = p.manifest()
        data["extensions"] = {"authoring": {"owner": "Programme team"}}
        p.manifest(data)
        edited = p.snapshot()
        self.assertEqual(p.run("init")[0], 0)
        self.assertEqual(p.snapshot(), edited)

    def test_setup_adopts_existing_content_unchanged(self):
        p = Project(self)
        original = "# Overview\n\nExisting explanation written by the team.\r\n"
        p.write("docs/overview.md", original, newline="\n")
        code, out, err = p.run("init", "--language", "en", "--content", "docs/overview.md")
        self.assertEqual(code, 0, err)
        self.assertIn("adopted: docs/overview.md", out)
        self.assertFalse((p.root / "brief.md").exists())
        self.assertEqual((p.root / "docs/overview.md").read_bytes(), original.encode("utf-8"))
        self.assertEqual(p.manifest()["topics"]["purpose"]["variants"]["en"]["path"], "docs/overview.md")

    def test_setup_refuses_invalid_or_unsafe_targets_without_writing(self):
        p = Project(self)
        p.write("project-brief.json", '{"version": 2}\n')
        before = p.snapshot()
        code, _, err = p.run("init")
        self.assertEqual(code, 2)
        self.assertIn("Unsupported manifest version", err)
        self.assertEqual(p.snapshot(), before)
        q = Project(self)
        for args in (["--config", "../escape.json"], ["--content", "../escape.md"],
                     ["--content", "project-brief.json"], ["--language", "e n"]):
            code, _, err = q.run("init", *args)
            self.assertEqual(code, 2, args)
        self.assertEqual(q.snapshot(), {})
        self.assertEqual(sorted(x.name for x in q.root.parent.iterdir()), ["client project"])
        q.write("empty.md", "  \n")
        self.assertEqual(q.run("init", "--content", "empty.md")[0], 2)
        self.assertFalse((q.root / "project-brief.json").exists())

    def test_plugin_directory_is_not_the_project(self):
        p = Project(self)
        before = sorted(str(x) for x in PLUGIN.rglob("*") if "__pycache__" not in x.parts)
        code, _, err = p.run("init", "--language", "en", cwd=CLI.parent)
        self.assertEqual(code, 0, err)
        self.assertTrue((p.root / "project-brief.json").is_file())
        self.assertEqual(sorted(str(x) for x in PLUGIN.rglob("*") if "__pycache__" not in x.parts), before)

    def test_init_infers_explicit_direction(self):
        for language, expected in (("ar", "rtl"), ("fa", "rtl"), ("he", "rtl"), ("ur-PK", "rtl"),
                                   ("fr", "ltr"), ("en-GB", "ltr"), ("zh-Hans", "ltr")):
            p = Project(self)
            self.assertEqual(p.run("init", "--language", language)[0], 0)
            v = p.manifest()["topics"]["purpose"]["variants"][language]
            self.assertEqual(v["direction"], expected, language)
        p = Project(self)
        p.run("init", "--language", "ar", "--direction", "ltr")
        self.assertEqual(p.manifest()["topics"]["purpose"]["variants"]["ar"]["direction"], "ltr")
        self.assertIn("تعريف بالمشروع", (p.root / "brief.md").read_text(encoding="utf-8"))


class SoftwareProjectTests(unittest.TestCase):
    def setUp(self):
        # A Rust service with the explanation in a block of an existing README and a dated test report as evidence.
        self.p = p = Project(self, "rust service")
        p.write("Cargo.toml", '[package]\nname = "queue"\n')
        p.write("src/main.rs", "fn main() {}\n")
        p.write("docs/api-contract.md", "POST /tasks returns 202.\n")
        p.write("docs/test-reports/claim-task-2026-10-20.md", "Pass 12 · Fail 0 · Not run 3 (database unavailable)\n")
        p.write("README.md", "# queue\n\nBuild with cargo.\n\n<!-- project-brief:start id=purpose lang=en -->\n"
                             "Volunteers claim tasks; results return asynchronously. Implemented and locally tested; "
                             "3 scenarios not run.\n<!-- project-brief:end id=purpose lang=en -->\n\nLicense notes.\n")
        p.manifest({"version": 1, "project": "Queue", "primary_language": "en",
                    "topics": {"purpose": topic({"en": variant("README.md", "ltr", "purpose")},
                                                evidence=["docs/api-contract.md", "docs/test-reports/claim-task-2026-10-20.md"],
                                                claims={"implemented": True, "locally_tested": "partial", "external_operation": "none"})},
                    "recipes": {"brief": {"topics": ["purpose"], "visibility": "public"}}})
        p.review("purpose", "en")

    def test_unrelated_changes_need_no_review(self):
        p = self.p
        p.write("src/main.rs", "fn main() { println!(\"hi\"); }\n")
        p.write("src/lib.rs", "pub fn x() {}\n")
        readme = (p.root / "README.md").read_text(encoding="utf-8")
        p.write("README.md", readme.replace("Build with cargo.", "Build with cargo build --release."))
        code, out, _ = p.run("check")
        self.assertEqual(code, 0, out)
        code, out, _ = p.run("export", "--recipe", "brief")
        self.assertEqual(code, 0)
        self.assertNotIn("cargo", out)
        self.assertNotIn("License notes", out)

    def test_changed_evidence_requires_review_and_blocks_public_export(self):
        p = self.p
        p.write("docs/test-reports/claim-task-2026-10-20.md", "Pass 11 · Fail 1 · Not run 3\n")
        code, out, _ = p.run("check")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)[0]["needs_review"], ["evidence-changed"])
        code, _, err = p.run("export", "--recipe", "brief", "--allow-stale")
        self.assertEqual(code, 2)
        self.assertIn("evidence-changed", err)

    def test_changed_claims_require_review(self):
        p = self.p
        data = p.manifest()
        data["topics"]["purpose"]["claims"]["external_operation"] = "pilot partner"
        p.manifest(data)
        self.assertEqual(json.loads(p.run("check")[1])[0]["needs_review"], ["claims-changed"])


class LanguageTests(unittest.TestCase):
    def test_arabic_first_with_english_added_later(self):
        p = Project(self)
        p.write("brief.ar.md", "# عون\n\nمهام صغيرة للمتطوعين. اختُبر المسار الآلي بالمحاكاة فقط، ولا يوجد ربط حي مع جهة خارجية.\n")
        p.manifest({"version": 1, "project": "عون", "primary_language": "ar",
                    "topics": {"summary": topic({"ar": variant("brief.ar.md", "rtl")})},
                    "recipes": {"brief": {"topics": ["summary"], "visibility": "public", "audience": "الإدارة"}}})
        p.review("summary", "ar")
        code, out, err = p.run("export", "--recipe", "brief", "--language", "ar", "--format", "json")
        self.assertEqual(code, 0, err)
        pack = json.loads(out)
        self.assertEqual(pack["topics"][0]["direction"], "rtl")
        self.assertIn("بالمحاكاة فقط", pack["topics"][0]["text"])
        self.assertEqual(pack["brief"]["audience"], "الإدارة")
        code, _, err = p.run("export", "--recipe", "brief", "--language", "en")
        self.assertEqual(code, 2)
        self.assertIn("Requested translation is unavailable: en", err)
        p.write("brief.en.md", "# Awn\n\nSmall volunteer tasks. The automated path was tested in simulation only; "
                               "there is no live external integration.\n")
        data = p.manifest()
        data["topics"]["summary"]["variants"]["en"] = variant("brief.en.md", "ltr")
        p.manifest(data)
        self.assertEqual(json.loads(p.run("check")[1])[1], {"topic": "summary", "language": "en", "needs_review": ["not-reviewed", "content-changed", "primary-changed", "evidence-changed", "claims-changed"]})
        p.review("summary", "en")
        self.assertEqual(p.run("check")[0], 0)
        p.write("brief.ar.md", "# عون\n\nمهام صغيرة للمتطوعين. اختُبر المسار الآلي بالمحاكاة وبدأت تجربة محدودة.\n")
        results = {r["language"]: r["needs_review"] for r in json.loads(p.run("check")[1])}
        self.assertEqual(results, {"ar": ["content-changed", "primary-changed"], "en": ["primary-changed"]})
        code, _, err = p.run("export", "--recipe", "brief", "--language", "en", "--allow-stale")
        self.assertEqual(code, 2)
        self.assertIn("primary-changed", err)

    def test_other_language_first_with_arabic_added_later(self):
        p = Project(self)
        self.assertEqual(p.run("init", "--language", "fr", "--project", "Jardin partagé")[0], 0)
        p.write("brief.md", "# Jardin partagé\n\nProposition, non réalisée.\n")
        p.review("purpose", "fr")
        self.assertEqual(p.run("export", "--recipe", "introduction", "--language", "fr")[0], 0)
        self.assertEqual(p.run("export", "--recipe", "introduction", "--language", "ar")[0], 2)
        p.write("brief.ar.md", "# حديقة مشتركة\n\nمقترح لم يُنفّذ بعد.\n")
        data = p.manifest()
        data["topics"]["purpose"]["variants"]["ar"] = variant("brief.ar.md", "rtl")
        p.manifest(data)
        self.assertEqual(p.run("export", "--recipe", "introduction", "--language", "ar")[0], 2)
        p.review("purpose", "ar")
        code, out, err = p.run("export", "--recipe", "introduction", "--language", "ar")
        self.assertEqual(code, 0, err)
        self.assertIn("مقترح لم يُنفّذ بعد", out)

    def test_line_endings_do_not_change_fingerprints(self):
        p = Project(self)
        p.run("init", "--language", "en")
        p.write("brief.md", "# Title\n\nLine one.\nLine two.\n", newline="\r\n")
        p.review("purpose", "en")
        p.write("brief.md", "# Title\n\nLine one.\nLine two.\n", newline="\n")
        self.assertEqual(p.run("check")[0], 0)


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.p = p = Project(self)
        p.write("facts.md", "Three pilot stops; 41 loans recorded by hand (locally tested).\n")
        p.write("residents.md", "For residents: books within walking distance, every Thursday.\n")
        p.write("funders.md", "For funders: a three-month trial using only the maintenance budget.\n")
        p.manifest({"version": 1, "project": "Mobile library", "primary_language": "en",
                    "topics": {"facts": topic({"en": variant("facts.md", "ltr")}),
                               "residents": topic({"en": variant("residents.md", "ltr")}),
                               "funders": topic({"en": variant("funders.md", "ltr")})},
                    "recipes": {
                        "meeting": {"topics": ["residents", "facts"], "visibility": "public", "audience": "Residents",
                                    "perspective": "Volunteer organisers", "priorities": ["Access", "Children"],
                                    "delivery": "Community meeting script"},
                        "meeting-relabelled": {"topics": ["residents", "facts"], "visibility": "public",
                                               "audience": "Council", "perspective": "Independent evaluator",
                                               "priorities": ["Cost"], "delivery": "Audio briefing"},
                        "funding": {"topics": ["funders", "facts"], "visibility": "public", "audience": "Funders",
                                    "delivery": "Two-page report", "max_chars": 200}}})
        for t in ("facts", "residents", "funders"):
            p.review(t, "en")

    def export(self, recipe):
        code, out, err = self.p.run("export", "--recipe", recipe, "--format", "json")
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_recipes_carry_their_own_perspective_order_and_delivery(self):
        meeting, funding = self.export("meeting"), self.export("funding")
        self.assertEqual([t["id"] for t in meeting["topics"]], ["residents", "facts"])
        self.assertEqual([t["id"] for t in funding["topics"]], ["funders", "facts"])
        self.assertEqual(meeting["brief"], {"audience": "Residents", "perspective": "Volunteer organisers",
                                            "priorities": ["Access", "Children"], "delivery": "Community meeting script"})
        self.assertEqual(funding["brief"]["delivery"], "Two-page report")

    def test_relabelling_a_recipe_does_not_rewrite_the_narrative(self):
        a, b = self.export("meeting"), self.export("meeting-relabelled")
        self.assertEqual([(t["text"], t["fingerprint"]) for t in a["topics"]],
                         [(t["text"], t["fingerprint"]) for t in b["topics"]])
        self.assertNotEqual(a["content_fingerprint"], b["content_fingerprint"])

    def test_snapshot_fingerprint_is_reproducible(self):
        first, second = self.export("meeting"), self.export("meeting")
        self.assertEqual(first["content_fingerprint"], second["content_fingerprint"])

    def test_budget_fails_instead_of_truncating(self):
        p = self.p
        p.write("funders.md", "For funders: a three-month trial using only the maintenance budget. " * 4)
        p.review("funders", "en")
        code, out, err = p.run("export", "--recipe", "funding")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("character budget", err)


class VisibilityTests(unittest.TestCase):
    def setUp(self):
        self.p = p = Project(self)
        p.write("public.md", "Public summary. Externally operating: none yet.\n")
        p.write("demo.md", "Presenter notes: open the staging dashboard first.\n")
        p.write("notes/internal-evidence.md", "Staging host details.\n")
        p.manifest({"version": 1, "project": "Demo", "primary_language": "en",
                    "topics": {"summary": topic({"en": variant("public.md", "ltr")}, evidence=["notes/internal-evidence.md"],
                                                claims={"external_operation": "none"}),
                               "demo": topic({"en": variant("demo.md", "ltr")}, visibility="internal")},
                    "recipes": {"public": {"topics": ["summary"], "visibility": "public"},
                                "leaky": {"topics": ["summary", "demo"], "visibility": "public"},
                                "rehearsal": {"topics": ["demo", "summary"], "visibility": "internal"}}})
        p.review("summary", "en")
        p.review("demo", "en")

    def test_public_recipe_rejects_internal_topic(self):
        code, out, err = self.p.run("export", "--recipe", "leaky")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("Public recipe selects internal content: demo", err)

    def test_public_export_omits_internal_metadata(self):
        code, out, _ = self.p.run("export", "--recipe", "public", "--format", "json")
        self.assertEqual(code, 0)
        self.assertNotIn("internal-evidence", out)
        topic_keys = set(json.loads(out)["topics"][0])
        self.assertFalse(topic_keys & {"evidence", "claims"})
        code, out, _ = self.p.run("export", "--recipe", "rehearsal", "--format", "json")
        self.assertIn("notes/internal-evidence.md", out)
        self.assertEqual(json.loads(out)["topics"][1]["claims"], {"external_operation": "none"})

    def test_stale_internal_draft_is_visibly_marked_and_public_is_refused(self):
        p = self.p
        p.write("public.md", "Public summary, edited but not yet reviewed.\n")
        self.assertEqual(p.run("export", "--recipe", "rehearsal")[0], 2)
        code, out, err = p.run("export", "--recipe", "rehearsal", "--allow-stale")
        self.assertEqual(code, 0, err)
        self.assertIn("> REVIEW REQUIRED: content-changed, primary-changed", out)
        code, out, _ = p.run("export", "--recipe", "rehearsal", "--allow-stale", "--format", "json")
        self.assertEqual(json.loads(out)["topics"][1]["needs_review"], ["content-changed", "primary-changed"])
        self.assertEqual(p.run("export", "--recipe", "public", "--allow-stale")[0], 2)


class ContainmentTests(unittest.TestCase):
    def setUp(self):
        self.p = p = Project(self)
        (p.root.parent / "outside.md").write_text("Outside the project.\n", encoding="utf-8")
        p.write("brief.md", "Inside.\n")

    def manifest_with(self, path="brief.md", evidence=()):
        self.p.manifest({"version": 1, "primary_language": "en",
                         "topics": {"purpose": topic({"en": variant(path, "ltr")}, evidence=evidence)},
                         "recipes": {"r": {"topics": ["purpose"], "visibility": "internal"}}})

    def assert_escape(self, *args):
        code, _, err = self.p.run(*args)
        self.assertEqual(code, 2, err)
        self.assertIn("Path escapes project root", err)

    def test_relative_absolute_and_config_escapes_are_rejected(self):
        self.manifest_with("../outside.md")
        self.assert_escape("check")
        self.manifest_with(evidence=[str(self.p.root.parent / "outside.md")])
        self.assert_escape("check")
        self.manifest_with()
        self.assert_escape("check", "--config", "../outside.md")

    def test_symlinks_out_of_the_project_are_rejected(self):
        symlink(self, self.p.root / "link.md", self.p.root.parent / "outside.md")
        self.manifest_with("link.md")
        self.assert_escape("check")
        symlink(self, self.p.root / "shared", self.p.root.parent, directory=True)
        self.manifest_with("shared/outside.md")
        self.assert_escape("check")

    def test_root_reached_through_a_symlink_still_works(self):
        alias = self.p.base / "alias"
        symlink(self, alias, self.p.root, directory=True)
        self.manifest_with()
        self.assertEqual(self.p.run("check", root=alias)[0], 1)
        code, out, err = self.p.run("review", "--topic", "purpose", "--language", "en", "--acknowledge-reviewed", root=alias)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.p.run("check")[0], 0)

    def test_review_does_not_follow_a_planted_staging_symlink(self):
        self.manifest_with()
        before = self.p.snapshot()
        symlink(self, self.p.root / "project-brief.json.tmp", self.p.root.parent / "outside.md")
        code, _, _ = self.p.run("review", "--topic", "purpose", "--language", "en", "--acknowledge-reviewed")
        self.assertEqual(code, 2)
        self.assertEqual((self.p.root.parent / "outside.md").read_text(encoding="utf-8"), "Outside the project.\n")
        self.assertEqual((self.p.root / "project-brief.json").read_bytes(), before["project-brief.json"])


class ReviewTests(unittest.TestCase):
    def build(self, newline):
        p = Project(self)
        p.write("a.md", "Topic A.\n")
        p.write("b.md", "Topic B.\n")
        p.write("b.ar.md", "الموضوع ب.\n")
        data = {"version": 1, "project": "Kept", "primary_language": "en", "x-owner": {"team": "ops"},
                "extensions": {"authoring": {"owner": "Programme team", "translations": "on-request"}},
                "topics": {"a": dict(topic({"en": dict(variant("a.md", "ltr"), note="keep")}), custom=[1, 2]),
                           "b": topic({"en": variant("b.md", "ltr"), "ar": variant("b.ar.md", "rtl")})},
                "recipes": {"r": {"topics": ["a", "b"], "visibility": "internal", "x-theme": "dark"}}}
        p.write("project-brief.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n", newline=newline)
        return p, data

    def test_review_requires_explicit_acknowledgement_and_known_topic(self):
        p, _ = self.build("\n")
        before = p.snapshot()
        for args in (["--topic", "a"], ["--topic", "zz", "--acknowledge-reviewed"], ["--acknowledge-reviewed"],
                     ["--topic", "a", "--language", "de", "--acknowledge-reviewed"]):
            code, _, _ = p.run("review", *args)
            self.assertEqual(code, 2, args)
        self.assertEqual(p.snapshot(), before)

    def test_review_changes_only_the_acknowledged_variant(self):
        for newline in ("\n", "\r\n"):
            p, original = self.build(newline)
            p.review("b", "ar")
            raw = (p.root / "project-brief.json").read_bytes()
            stored = json.loads(raw.decode("utf-8"))
            review = stored["topics"]["b"]["variants"]["ar"].pop("review")
            self.assertEqual(set(review), {"content", "primary", "evidence", "claims", "at"})
            self.assertEqual(stored, original)
            self.assertEqual(raw.count(b"\r\n") == raw.count(b"\n"), newline == "\r\n")
            results = {(r["topic"], r["language"]): r["needs_review"] for r in json.loads(p.run("check")[1])}
            self.assertEqual(results[("b", "ar")], [])
            self.assertIn("not-reviewed", results[("a", "en")])


class OfflineTests(unittest.TestCase):
    def test_tool_imports_only_the_standard_library(self):
        tree = ast.parse(CLI.read_text(encoding="utf-8"))
        imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imported, {"argparse", "hashlib", "json", "pathlib", "re", "sys", "datetime"})

    def test_commands_run_with_networking_disabled(self):
        p = Project(self)
        p.write("brief.md", "Offline content.\n")
        p.manifest({"version": 1, "primary_language": "en",
                    "topics": {"purpose": dict(topic({"en": variant("brief.md", "ltr")}, visibility="internal"),
                                               evidence=[{"ref": "https://example.org/status", "reviewed_reference": "2026-10-01"},
                                                         {"ref": "http://example.org/unreviewed"}])},
                    "recipes": {"r": {"topics": ["purpose"], "visibility": "internal"}}})

        def refuse(*args, **kwargs):
            raise AssertionError("network access attempted")

        def main(*args):
            sys.argv = ["brief.py"] + list(args) + ["--root", str(p.root)]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = brief.main()
            return code, out.getvalue()

        saved = (socket.socket, socket.create_connection, socket.getaddrinfo, sys.argv)
        socket.socket = socket.create_connection = socket.getaddrinfo = refuse
        try:
            self.assertEqual(main("check")[0], 1)
            self.assertEqual(main("review", "--topic", "purpose", "--acknowledge-reviewed")[0], 0)
            code, out = main("export", "--recipe", "r", "--format", "json")
            self.assertEqual(code, 0)
        finally:
            socket.socket, socket.create_connection, socket.getaddrinfo, sys.argv = saved
        review = p.manifest()["topics"]["purpose"]["variants"]["en"]["review"]
        self.assertEqual(review["evidence"], {"https://example.org/status": "2026-10-01",
                                              "http://example.org/unreviewed": "unverified-external-reference"})

    def test_input_errors_exit_2_not_1(self):
        p = Project(self)
        self.assertEqual(p.run("check")[0], 2)
        p.write("project-brief.json", "[]\n")
        code, _, err = p.run("check")
        self.assertEqual(code, 2)
        self.assertIn("Manifest must be a JSON object", err)
        q = Project(self)
        q.run("init")
        code, _, err = q.run("export")
        self.assertEqual(code, 2)
        self.assertIn("Export requires --recipe", err)

    def test_arabic_output_is_utf8_through_a_pipe(self):
        p = Project(self)
        p.run("init", "--language", "ar")
        p.write("brief.md", "مرحبًا ٢٠٢٦ — نصّ عربي «مقتبس».\n")
        p.review("purpose", "ar")
        code, out, err = p.run("export", "--recipe", "introduction")
        self.assertEqual(code, 0, err)
        self.assertIn("مرحبًا ٢٠٢٦ — نصّ عربي «مقتبس».", out)


if __name__ == "__main__":
    unittest.main()
