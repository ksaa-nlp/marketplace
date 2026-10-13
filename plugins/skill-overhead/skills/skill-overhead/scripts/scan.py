import glob, json, os, re, sys, urllib.request
roots = [os.path.expanduser("~/.claude/skills"), os.path.expanduser("~/.claude/plugins"), ".claude/skills"] + sys.argv[1:]
seen, rows = set(), []
for root in roots:
    for p in glob.glob(os.path.join(root, "**", "SKILL.md"), recursive=True):
        rp = os.path.realpath(p)
        if rp in seen: continue
        seen.add(rp)
        text = open(p, encoding="utf-8", errors="replace").read()
        m = re.match(r"---\s*\n(.*?)\n---\s*\n?(.*)", text, re.S)
        fm, body = (m.group(1), m.group(2)) if m else ("", text)
        name = re.search(r"^name:\s*(.*)$", fm, re.M)
        desc = re.search(r"^description:\s*(.*?)(?=^[\w-]+:|\Z)", fm, re.M | re.S)
        name = name.group(1).strip().strip("'\"") if name else os.path.basename(os.path.dirname(p))
        desc = re.sub(r"\s+", " ", desc.group(1)).strip().strip("'\"|>") if desc else ""
        d = os.path.dirname(p)
        extra = sum(os.path.getsize(f) for f in glob.glob(d + "/**/*", recursive=True) if os.path.isfile(f)) - os.path.getsize(p)
        src = "إضافة" if "/plugins/" in p else ("المشروع" if not p.startswith(os.path.expanduser("~")) else "المستخدم")
        rows.append({"name": name, "source": src, "listing": f"- {name}: {desc}", "body": body, "extra_kb": extra // 1024})
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
method = "واجهة Anthropic لعدّ الرموز (دقيق)" if key else "تقدير (عدد الأحرف ÷ 3.5، بهامش خطأ ±15% تقريبًا)"
for r in rows: r["always"], r["invoke"] = count(r["listing"]), count(r["body"])
rows.sort(key=lambda r: -r["always"])
print(f"طريقة العدّ: {method}\n")
print("| المهارة | المصدر | محمّل دائمًا | عند الاستدعاء | الملفات المرفقة |\n|---|---|---:|---:|---:|")
for r in rows: print(f"| {r['name']} | {r['source']} | {r['always']:,} | {r['invoke']:,} | {r['extra_kb']:,} ك.ب |")
print(f"| **الإجمالي ({len(rows)} مهارة)** | | **{sum(r['always'] for r in rows):,}** | {sum(r['invoke'] for r in rows):,} | |")
