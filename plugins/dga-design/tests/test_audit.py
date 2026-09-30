"""Tests for skills/dga-design/scripts/audit.py (no network)."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills/dga-design/scripts/audit.py"
spec = importlib.util.spec_from_file_location("audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTest(unittest.TestCase):
    def run_on(self, files: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, content in files.items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(content, encoding="utf-8")
            return audit.audit(root)

    def test_palette_loaded_from_tokens(self):
        palette = audit.load_palette()
        self.assertEqual(palette["#1b8354"], "--colors-primary-sa-flag-600-primary")
        self.assertIn("#161616", palette)

    def test_colors_classified(self):
        r = self.run_on({"a.css": ".x{color:#1B8354;background:#02a4ac}"})
        fd = r["findings"]
        self.assertEqual(fd["color_hardcoded_palette"][0]["token"], "--colors-primary-sa-flag-600-primary")
        self.assertEqual(len(fd["color_off_palette"]), 1)
        self.assertTrue(fd["color_off_palette"][0]["nearest"].startswith("--colors-"))

    def test_scales(self):
        css = (".a{padding:16px 13px;border-radius:8px}"
               ".b{border-radius:12px;font-size:15px;line-height:24px;margin:var(--spacing-4)}")
        fd = self.run_on({"a.css": css})["findings"]
        self.assertEqual(fd["spacing_off_scale"][0]["off"], ["13px"])
        self.assertEqual([f["off"] for f in fd["radius_off_scale"]], [["12px"]])
        self.assertEqual(fd["font_size_off_scale"][0]["off"], ["15px"])
        self.assertNotIn("line_height_off_scale", fd)

    def test_fonts_shadows_tailwind(self):
        fd = self.run_on({
            "a.css": 'body{font-family:"Noto Kufi Arabic"}h1{font-family:"IBM Plex Sans Arabic",sans-serif}'
                     ".c{box-shadow:0 1px 2px red}.d{box-shadow:var(--shadow-sm)}",
            "b.tsx": '<div className="p-[13px] text-[#123456] p-4" />',
        })["findings"]
        self.assertEqual(len(fd["font_family"]), 1)
        self.assertEqual(len(fd["shadow_custom"]), 1)
        self.assertEqual({f["value"] for f in fd["tailwind_arbitrary"]}, {"p-[13px]", "text-[#123456]"})

    def test_rem_fluid_blur_and_multiline(self):
        css = (".a{padding:0.7rem 1rem}\n"
               ".b{font-size:clamp(14px,2vw,18px)}\n"
               ".c{box-shadow:\n  0 1px 2px red,\n  0 2px 4px blue;\n}\n"
               ".d{backdrop-filter:blur(10px)}.e{backdrop-filter:blur(16px)}")
        fd = self.run_on({"a.css": css})["findings"]
        self.assertEqual(fd["spacing_off_scale"][0]["off"], ["0.7rem (11.2px)"])
        self.assertIn("clamp()/vw", fd["font_size_off_scale"][0]["off"])
        self.assertEqual(len(fd["shadow_custom"]), 1)
        self.assertEqual(fd["shadow_custom"][0]["loc"], "a.css:3")
        self.assertEqual([f["off"] for f in fd["blur_off_scale"]], [["10px"]])

    def test_line_numbers(self):
        fd = self.run_on({"a.css": "\n\n.x{color:#02a4ac}"})["findings"]
        self.assertEqual(fd["color_off_palette"][0]["loc"], "a.css:3")

    def test_html_lang_dir(self):
        fd = self.run_on({"ok.html": '<html lang="ar" dir="rtl">', "bad.html": '<html lang="en">'})["findings"]
        self.assertEqual([f["loc"] for f in fd["html_lang_dir"]], ["bad.html:1"])

    def test_skips_vendor_and_token_files(self):
        fd = self.run_on({
            "node_modules/x/a.css": ".x{color:#02a4ac}",
            "dga-tokens.css": ":root{--x:#02a4ac}",
        })["findings"]
        self.assertEqual(dict(fd), {})

    def test_render_is_arabic_markdown(self):
        out = audit.render(self.run_on({"a.css": ".x{color:#02a4ac}"}), limit=5)
        self.assertIn("# تدقيق DGA", out)
        self.assertIn("#02a4ac", out)


if __name__ == "__main__":
    unittest.main()
