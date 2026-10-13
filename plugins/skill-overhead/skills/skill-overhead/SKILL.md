---
name: skill-overhead
description: يفحص مهارات Claude المثبّتة ويقيس ما تضيفه كل واحدة إلى نافذة السياق (الوصف المحمّل دائمًا مقابل المتن المحمّل عند الاستدعاء)، ويعرض النتيجة جدولًا بالعربية. استعمله عند السؤال عن حجم السياق الذي تأخذه المهارات، أو أثقلها، أو طلب جدول بالعبء. Scan installed Claude skills and report the context-window overhead of each one as a table, in Arabic.
argument-hint: "[مجلدات مهارات إضافية...]"
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/scan.py *)
---

# Skill context overhead report (Arabic output)

Use this when the user asks how much context their installed skills take, which skills are the heaviest, or wants an overhead table.

**Language rule:** write everything the user sees in Arabic: the table, the summary, and any notes. Keep skill names, file paths, and terms like SKILL.md, /clear and ANTHROPIC_API_KEY exactly as they are, untranslated.

## What is measured

- **محمّل دائمًا (always loaded)**: the skill's name + description. It sits in the system prompt every turn, so this is the real baseline cost.
- **عند الاستدعاء (on invoke)**: the SKILL.md body. It loads only when the skill is used, then stays in the conversation until /clear, a new session, or compaction.
- **الملفات المرفقة (bundled files)**: scripts and references in the skill folder. They cost nothing until Claude opens them.

## Steps

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/scan.py [extra dirs...]`. By default it scans `~/.claude/skills`, `~/.claude/plugins` and `./.claude/skills`. Pass any other skill folders the user mentions as extra arguments. The script already prints its headers and labels in Arabic.
2. If `ANTHROPIC_API_KEY` is set, it uses the Anthropic token counting API for exact counts. Otherwise it estimates with characters ÷ 3.5 (about ±15%). The first line of output states which method was used. Keep that line.
3. Show the table it prints. Then add a short summary **in Arabic**: the always-loaded total, the 3 heaviest descriptions, and that per-skill cost depends on description length, not skill size. Also mention that built-in and claude.ai-hosted skills without local files are not included.
4. If the table is long, save it to a Markdown file and point to it instead of pasting it all.
