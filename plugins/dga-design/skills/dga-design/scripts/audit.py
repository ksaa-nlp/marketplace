#!/usr/bin/env python3
"""Static audit of a front-end codebase against DGA Platforms Code foundations.

Reports hard-coded values that fall outside the official tokens: colours
(with the nearest palette token), font families, spacing / radius / font-size
px values, raw box-shadows, Tailwind arbitrary values, and <html lang/dir>.
It is a heuristic helper for the dga-design skill, not an official score.

Usage:
    python3 audit.py [PATH] [--json] [--limit N]

Standard library only; Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path

TOKENS = Path(__file__).resolve().parent.parent / "assets" / "dga-tokens.css"

EXTS = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jinja", ".j2", ".njk",
        ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro", ".py"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".output", "out",
             "coverage", "vendor", ".venv", "venv", "__pycache__", ".cache", ".angular",
             "site-packages", ".svelte-kit"}
SKIP_FILES = {"dga-tokens.css", "core.css"}

SPACING_PX = {0, 1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160}  # 1px: borders
RADIUS_PX = {0, 2, 4, 8, 16, 24, 9999}
FONT_PX = {10, 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72}
LINE_PX = {14, 18, 20, 24, 28, 30, 32, 38, 44, 60, 72, 90}
BLUR_PX = {0, 8, 16, 24, 40}
REM_PX = 16  # root font size assumed by the DGA tables ("Size (16px base)")

HEX_RE = re.compile(r"(?<![\w&])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB_RE = re.compile(r"\brgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})[^)]*\)")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}{\n]+)", re.I)
SPACING_RE = re.compile(r"\b(margin|padding|gap|row-gap|column-gap|inset|top|right|bottom|left)"
                        r"(?:-[a-z-]+)?\s*:\s*([^;}{\n\"']+)", re.I)
RADIUS_RE = re.compile(r"border(?:-[a-z]+)*-radius\s*:\s*([^;}{\n\"']+)", re.I)
FSIZE_RE = re.compile(r"font-size\s*:\s*([^;}{\n\"']+)", re.I)
LHEIGHT_RE = re.compile(r"line-height\s*:\s*([^;}{\n\"']+)", re.I)
SHADOW_RE = re.compile(r"box-shadow\s*:\s*([^;}{\"']+)", re.I)  # may span lines
BACKDROP_RE = re.compile(r"backdrop-filter\s*:\s*([^;}{\"']+)", re.I)
LENGTH_RE = re.compile(r"(-?\d*\.?\d+)(px|rem)\b")
BLUR_RE = re.compile(r"blur\(\s*(-?\d*\.?\d+)(px|rem)\s*\)")
FLUID_RE = re.compile(r"clamp\(|\d(?:vw|vh|vmin|vmax)\b")
TW_ARBITRARY_RE = re.compile(r"(?<![\w-])(?:[a-z]+:)*-?(?:p[trblxyse]?|m[trblxyse]?|gap(?:-[xy])?|"
                             r"text|bg|border(?:-[trblxy])?|rounded(?:-[a-z]+)?|shadow|w|h|"
                             r"min-w|max-w|min-h|max-h|top|left|right|bottom|inset|leading|"
                             r"tracking|space-[xy]|font|fill|stroke|ring|outline)-\[[^\]\s]+\]")
HTML_TAG_RE = re.compile(r"<html\b[^>]*>", re.I)


def load_palette() -> dict[str, str]:
    """hex (lowercase, 6 digits) -> token name, from the generated token file."""
    palette: dict[str, str] = {}
    text = TOKENS.read_text(encoding="utf-8")
    # only the light :root palette block (first definition wins)
    for name, value in re.findall(r"(--colors-[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\b", text):
        palette.setdefault(value.lower(), name)
    return palette


def norm_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h[:6]


def rgb(h: str) -> tuple[int, int, int]:
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def nearest(hexv: str, palette: dict[str, str]) -> tuple[str, str, float]:
    r, g, b = rgb(hexv)
    best = min(palette, key=lambda p: sum((x - y) ** 2 for x, y in zip((r, g, b), rgb(p))))
    dist = sum((x - y) ** 2 for x, y in zip((r, g, b), rgb(best))) ** 0.5
    return best, palette[best], dist


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS and p.name not in SKIP_FILES \
                and not any(part in SKIP_DIRS for part in p.parts) and not p.name.endswith(".min.js"):
            yield p


def to_px(num: str, unit: str) -> float:
    return float(num) * (REM_PX if unit == "rem" else 1)


def fmt_len(num: str, unit: str) -> str:
    return f"{num}{unit}" if unit == "px" else f"{num}rem ({to_px(num, unit):g}px)"


def off_scale(value: str, allowed: set, fluid_is_off: bool = False) -> list:
    """Lengths in `value` (px or rem) that are not on the given px scale."""
    if "var(" in value:
        return []
    bad = ["clamp()/vw"] if fluid_is_off and FLUID_RE.search(value) else []
    for num, unit in LENGTH_RE.findall(value):
        if abs(to_px(num, unit)) not in allowed:
            bad.append(fmt_len(num, unit))
    return bad


def audit(root: Path) -> dict:
    palette = load_palette()
    findings: dict[str, list[dict]] = defaultdict(list)
    stats = {"files": 0, "uses_dga_tokens": False, "uses_dga_package": False}

    for pkg in [root / "package.json"] if root.is_dir() else []:
        if pkg.exists() and re.search(r'"(platformscode-new-react|@platformscode/core)"', pkg.read_text("utf-8", "ignore")):
            stats["uses_dga_package"] = True

    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        stats["files"] += 1
        if "--colors-primary-sa-flag" in text or "--background-primary" in text:
            stats["uses_dga_tokens"] = True
        rel = str(path.relative_to(root)) if root.is_dir() else path.name
        if path.suffix == ".py":
            # Python: keep only lines that look like embedded CSS/HTML
            text = "\n".join(l if re.search(r"[{};]|<\w", l) else "" for l in text.split("\n"))
        starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]

        def loc(m, _rel=rel, _starts=starts) -> str:
            return f"{_rel}:{bisect_right(_starts, m.start())}"

        for m in HEX_RE.finditer(text):
            h = norm_hex(m.group(1))
            if h in palette:
                findings["color_hardcoded_palette"].append({"loc": loc(m), "value": m.group(0), "token": palette[h]})
            else:
                near, tok, dist = nearest(h, palette)
                findings["color_off_palette"].append({"loc": loc(m), "value": m.group(0), "nearest": tok,
                                                      "nearest_hex": near, "distance": round(dist, 1)})
        for m in RGB_RE.finditer(text):
            h = "#%02x%02x%02x" % tuple(min(255, int(x)) for x in m.groups())
            if h not in palette and h not in ("#101828",):  # shadow base colour
                near, tok, dist = nearest(h, palette)
                findings["color_off_palette"].append({"loc": loc(m), "value": m.group(0), "nearest": tok,
                                                      "nearest_hex": near, "distance": round(dist, 1)})
        for m in FONT_RE.finditer(text):
            v = m.group(1).strip()
            if "IBM Plex Sans Arabic" not in v and "var(" not in v and "inherit" not in v and "monospace" not in v:
                findings["font_family"].append({"loc": loc(m), "value": v[:80]})
        for regex, key, allowed, fluid in ((SPACING_RE, "spacing_off_scale", SPACING_PX, False),
                                           (RADIUS_RE, "radius_off_scale", RADIUS_PX, False),
                                           (FSIZE_RE, "font_size_off_scale", FONT_PX, True),
                                           (LHEIGHT_RE, "line_height_off_scale", LINE_PX, False)):
            for m in regex.finditer(text):
                bad = off_scale(m.groups()[-1], allowed, fluid)
                if bad:
                    findings[key].append({"loc": loc(m), "value": m.group(0).strip()[:80], "off": bad})
        for m in SHADOW_RE.finditer(text):
            v = " ".join(m.group(1).split())
            if "var(--shadow" not in v and v.lower() not in ("none", "inherit", "initial", "unset"):
                findings["shadow_custom"].append({"loc": loc(m), "value": v[:80]})
        for m in BACKDROP_RE.finditer(text):
            bad = [fmt_len(n, u) for n, u in BLUR_RE.findall(m.group(1)) if abs(to_px(n, u)) not in BLUR_PX]
            if bad:
                findings["blur_off_scale"].append({"loc": loc(m), "value": " ".join(m.group(0).split())[:80],
                                                   "off": bad})
        for m in TW_ARBITRARY_RE.finditer(text):
            findings["tailwind_arbitrary"].append({"loc": loc(m), "value": m.group(0)})
        for m in HTML_TAG_RE.finditer(text):
            tag = m.group(0)
            if ('lang="ar"' not in tag and "lang='ar'" not in tag) or "dir=" not in tag:
                findings["html_lang_dir"].append({"loc": loc(m), "value": tag[:120]})
    return {"root": str(root), "stats": stats, "findings": findings}


TITLES = {
    "color_off_palette": "ألوان خارج لوحة DGA (مع أقرب رمز)",
    "color_hardcoded_palette": "ألوان من اللوحة مكتوبة قيمًا ثابتة (استبدلها بالرمز)",
    "font_family": "خطوط غير IBM Plex Sans Arabic",
    "spacing_off_scale": "مسافات خارج سلّم DGA",
    "radius_off_scale": "حواف خارج قيم DGA",
    "font_size_off_scale": "أحجام خط خارج سلّم Display/Text (والأحجام المائعة clamp/vw)",
    "line_height_off_scale": "ارتفاعات سطر خارج السلّم",
    "shadow_custom": "ظلال مخصصة (استعمل --shadow-*)",
    "blur_off_scale": "تمويه خلفية خارج القيم 8/16/24/40",
    "tailwind_arbitrary": "قيم Tailwind اعتباطية",
    "html_lang_dir": "وسم <html> بلا lang=\"ar\" و dir",
}


def render(report: dict, limit: int) -> str:
    st, fd = report["stats"], report["findings"]
    out = [f"# تدقيق DGA: {report['root']}", "",
           f"- الملفات المفحوصة: {st['files']}",
           f"- حزمة DGA في package.json: {'نعم' if st['uses_dga_package'] else 'لا'}",
           f"- رموز DGA مستعملة في الكود: {'نعم' if st['uses_dga_tokens'] else 'لا'}", ""]
    for key, title in TITLES.items():
        items = fd.get(key, [])
        out.append(f"## {title}: {len(items)}")
        if key.startswith("color"):
            by_val: dict[str, list[dict]] = defaultdict(list)
            for it in items:
                by_val[it["value"].lower()].append(it)
            for val, its in sorted(by_val.items(), key=lambda kv: -len(kv[1]))[:limit]:
                hint = its[0].get("token") or f"الأقرب {its[0]['nearest']} ({its[0]['nearest_hex']}، مسافة {its[0]['distance']})"
                locs = ", ".join(i["loc"] for i in its[:3]) + (" …" if len(its) > 3 else "")
                out.append(f"- `{val}` ×{len(its)} → {hint} — {locs}")
        else:
            for it in items[:limit]:
                extra = f" (خارج السلّم: {', '.join(it['off'])})" if "off" in it else ""
                out.append(f"- {it['loc']}: `{it['value']}`{extra}")
            if len(items) > limit:
                out.append(f"- … و{len(items) - limit} غيرها")
        out.append("")
    out.append("> تدقيق آلي تقريبي: يكشف القيم الثابتة ولا يحكم على المكونات والقوالب وتجربة الاستخدام. "
               "راجع البنود الباقية يدويًا مقابل references/checklist.md.")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--limit", type=int, default=15, help="items shown per category")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    if not root.exists():
        sys.exit(f"not found: {root}")
    report = audit(root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report, args.limit))


if __name__ == "__main__":
    main()
