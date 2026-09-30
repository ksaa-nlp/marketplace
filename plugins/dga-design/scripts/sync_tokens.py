#!/usr/bin/env python3
"""Regenerate skills/dga-design/assets/dga-tokens.css from the official
@platformscode/core package (MIT) published by the DGA Platforms Code team.

Usage:
    python3 scripts/sync_tokens.py            # latest version on npm
    python3 scripts/sync_tokens.py 0.0.52     # pin a version

Needs `npm` on PATH (uses `npm pack`, no install). Standard library only.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

PKG = "@platformscode/core"
OUT = Path(__file__).resolve().parent.parent / "skills/dga-design/assets/dga-tokens.css"
TOKEN_SELECTORS = (":root", "[data-theme=dark]")
# Typography utility classes shipped by the package (Display / Text scale x weight).
TYPO_RE = re.compile(r"^\.(display-(2xl|xl|lg|md|sm|xs)|text-(xl|lg|md|sm|xs|2xs))-(regular|medium|semibold|bold)$")


def fetch_css(version: str) -> tuple[str, str]:
    spec = f"{PKG}@{version}" if version else PKG
    with tempfile.TemporaryDirectory() as tmp:
        name = subprocess.run(
            ["npm", "pack", spec, "--silent"], cwd=tmp, check=True, capture_output=True, text=True
        ).stdout.strip().splitlines()[-1]
        with tarfile.open(Path(tmp) / name) as tar:
            css = tar.extractfile("package/dist/core/core.css").read().decode("utf-8")
            meta = tar.extractfile("package/package.json").read().decode("utf-8")
    resolved = re.search(r'"version"\s*:\s*"([^"]+)"', meta).group(1)
    return css, resolved


def walk_rules(css: str):
    """Yield (parents, selector, body) for every innermost rule."""
    stack, last = [], 0
    for m in re.finditer(r"[{}]", css):
        if m.group() == "{":
            selector = css[last:m.start()].split("}")[-1].strip()
            stack.append((selector, m.end()))
        else:
            selector, start = stack.pop()
            body = css[start:m.start()]
            if "{" not in body:
                yield [s for s, _ in stack], selector, body
        last = m.end()


def fmt_block(selector: str, body: str, indent: str = "") -> str:
    decls = [d.strip() for d in body.split(";") if d.strip()]
    inner = "".join(f"{indent}  {d};\n" for d in decls)
    return f"{indent}{selector} {{\n{inner}{indent}}}\n"


def build(css: str, version: str) -> str:
    parts = [
        "/*\n"
        f" * DGA Platforms Code design tokens — generated from {PKG}@{version}\n"
        " * Source: https://www.npmjs.com/package/@platformscode/core (MIT License)\n"
        " * Guidelines: https://design.dga.gov.sa/\n"
        " * Do not edit by hand: regenerate with plugins/dga-design/scripts/sync_tokens.py\n"
        " *\n"
        " * Font: IBM Plex Sans Arabic (weights 400/500/600/700) must be loaded separately.\n"
        " * Dark theme: set data-theme=\"dark\" on <html>.\n"
        " */\n"
    ]
    typo = {}
    for parents, selector, body in walk_rules(css):
        if selector in TOKEN_SELECTORS and "--" in body:
            if parents:
                parts.append(f"{parents[-1]} {{\n{fmt_block(selector, body, '  ')}}}\n")
            else:
                parts.append(fmt_block(selector, body))
        elif not parents:
            # The package groups some utilities with component selectors
            # (e.g. ".text-md-medium,.dga-btn--lg"); keep only the utility.
            for cls in (s.strip() for s in selector.split(",")):
                if TYPO_RE.match(cls) and cls not in typo:
                    typo[cls] = fmt_block(cls, body)
    parts.append("\n/* Typography scale utilities (Display / Text) */\n")
    parts.extend(typo[c] for c in sorted(typo))
    return "\n".join(parts)


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else ""
    css, resolved = fetch_css(version)
    out = build(css, resolved)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT} from {PKG}@{resolved} ({out.count('--')} custom-property refs)")


if __name__ == "__main__":
    main()
