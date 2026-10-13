import json, os, re, sys, urllib.request
H = os.path.expanduser("~")
# Where each tool loads skills from: user-level folders, then project folders (relative to the current directory).
TOOLS = {
    "Claude": [H + "/.claude/skills", H + "/.claude/plugins", ".claude/skills"],
    "Codex": [H + "/.codex/skills", H + "/.agents/skills", ".agents/skills", ".codex/skills"],
    "Antigravity": [H + "/.gemini/antigravity/skills", H + "/.gemini/antigravity-cli/skills", H + "/.gemini/config/skills",
                    H + "/.gemini/config/plugins", ".agent/skills", ".agents/skills"],
}
args, want = sys.argv[1:], None
if "--tools" in args:
    i = args.index("--tools")
    want = {t.strip().lower() for t in args[i + 1].split(",")}
    args = args[:i] + args[i + 2:]
roots = [(t, r) for t, rs in TOOLS.items() if want is None or t.lower() in want for r in rs] + [("مخصص", a) for a in args]

def skill_files(root):
    # os.walk rather than glob: glob skips hidden folders such as ~/.codex/skills/.system
    seen_dirs = set()
    for d, dirs, files in os.walk(root, followlinks=True):
        rd = os.path.realpath(d)
        if rd in seen_dirs: dirs[:] = []; continue
        seen_dirs.add(rd)
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules")]
        if "SKILL.md" in files: yield os.path.join(d, "SKILL.md")

found = {}
for tool, root in roots:
    for p in skill_files(root):
        rp = os.path.realpath(p)
        if rp in found:
            if tool not in found[rp]["tools"]: found[rp]["tools"].append(tool)
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        m = re.match(r"---\s*\n(.*?)\n---\s*\n?(.*)", text, re.S)
        fm, body = (m.group(1), m.group(2)) if m else ("", text)
        name = re.search(r"^name:\s*(.*)$", fm, re.M)
        desc = re.search(r"^description:\s*(.*?)(?=^[\w-]+:|\Z)", fm, re.M | re.S)
        name = name.group(1).strip().strip("'\"") if name else os.path.basename(os.path.dirname(p))
        desc = re.sub(r"\s+", " ", desc.group(1)).strip().strip("'\"|>") if desc else ""
        d = os.path.dirname(p)
        extra = sum(os.path.getsize(os.path.join(a, f)) for a, _, fs in os.walk(d) for f in fs) - os.path.getsize(p)
        src = "إضافة" if "/plugins/" in p else ("المشروع" if not os.path.abspath(p).startswith(H) else "المستخدم")
        found[rp] = {"name": name, "tools": [tool], "source": src, "listing": f"- {name}: {desc}", "body": body, "extra_kb": extra // 1024}
rows = list(found.values())
key = os.environ.get("ANTHROPIC_API_KEY")
def count(t):
    if key and t.strip():
        try:
            req = urllib.request.Request("https://api.anthropic.com/v1/messages/count_tokens",
                data=json.dumps({"model": "claude-sonnet-5-5", "messages": [{"role": "user", "content": t}]}).encode(),
                headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
            return json.load(urllib.request.urlopen(req))["input_tokens"] - 7  # minus message overhead
        except Exception: pass
    return round(len(t) / 3.5)
method = "واجهة Anthropic لعدّ الرموز (دقيق لـ Claude، وتقريبي لـ Codex وAntigravity لاختلاف المُرمِّز)" if key else "تقدير (عدد الأحرف ÷ 3.5، بهامش خطأ ±15% تقريبًا)"
for r in rows: r["always"], r["invoke"] = count(r["listing"]), count(r["body"])
rows.sort(key=lambda r: -r["always"])
print(f"طريقة العدّ: {method}\n")
print("| المهارة | الأداة | المصدر | محمّل دائمًا | عند الاستدعاء | الملفات المرفقة |\n|---|---|---|---:|---:|---:|")
for r in rows: print(f"| {r['name']} | {'، '.join(r['tools'])} | {r['source']} | {r['always']:,} | {r['invoke']:,} | {r['extra_kb']:,} ك.ب |")
# Each tool pays only for the skills it loads, so totals are per tool; a skill shared by two tools counts in both.
for t in list(TOOLS) + ["مخصص"]:
    rs = [r for r in rows if t in r["tools"]]
    if rs: print(f"| **إجمالي {t} ({len(rs)} مهارة)** | | | **{sum(r['always'] for r in rs):,}** | {sum(r['invoke'] for r in rs):,} | |")
