---
name: skill-overhead
description: يفحص المهارات المثبّتة لـ Claude وCodex وAntigravity ويقيس ما تضيفه كل واحدة إلى نافذة السياق (الوصف المحمّل دائمًا مقابل المتن المحمّل عند الاستدعاء)، ويعرض النتيجة جدولًا بالعربية. استعمله عند السؤال عن حجم السياق الذي تأخذه المهارات، أو أثقلها، أو طلب جدول بالعبء. Scan installed Claude, Codex and Antigravity skills and report the context-window overhead of each one as a table, in Arabic.
argument-hint: "[--tools claude,codex,antigravity] [مجلدات مهارات إضافية...]"
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/scan.py *)
---

# Skill context overhead report (Arabic output)

Use this when the user asks how much context their installed skills take, which skills are the heaviest, or wants an overhead table. It covers Claude, Codex and Antigravity, and works when this skill itself is installed in any of the three.

**Language rule:** write everything the user sees in Arabic: the table, the summary, and any notes. Keep skill names, file paths, and terms like SKILL.md, /clear and ANTHROPIC_API_KEY exactly as they are, untranslated.

## What is measured

- **محمّل دائمًا (always loaded)**: the skill's name + description. It sits in the system prompt every turn, so this is the real baseline cost.
- **عند الاستدعاء (on invoke)**: the SKILL.md body. It loads only when the skill is used, then stays in the conversation until /clear, a new session, or compaction.
- **الملفات المرفقة (bundled files)**: scripts and references in the skill folder. They cost nothing until Claude opens them.

## Steps

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/scan.py [--tools ...] [extra dirs...]`. Outside Claude Code, `${CLAUDE_SKILL_DIR}` is not set: use the folder that contains this SKILL.md instead. By default it scans every tool's folders:
   - **Claude**: `~/.claude/skills`, `./.claude/skills`, and installed plugins only (from `~/.claude/plugins/installed_plugins.json`, skipping plugins disabled in `enabledPlugins` or installed for another project), plus the skills and plugins the Claude desktop app syncs from claude.ai (source «claude.ai»)
   - **Codex**: `~/.codex/skills`, `~/.agents/skills`, `./.agents/skills`, `./.codex/skills`
   - **Antigravity**: `~/.gemini/antigravity/skills`, `~/.gemini/antigravity-cli/skills`, `~/.gemini/config/skills`, `~/.gemini/config/plugins`, `./.agent/skills`, `./.agents/skills`

   If the user asks about one tool, pass `--tools codex` (comma-separated for several). Pass any other skill folders the user mentions as extra arguments; they appear under the tool «مخصص». The script already prints its headers and labels in Arabic.
2. If `ANTHROPIC_API_KEY` is set, it uses the Anthropic token counting API: exact for Claude, close but approximate for Codex and Antigravity, whose models use other tokenizers. Otherwise it estimates with characters ÷ 3.5 (about ±15%). The first line of output states which method was used. Keep that line.
3. Show the table it prints. A skill folder shared by several tools (such as `./.agents/skills`) is listed once with all of them, and each tool has its own total row, because each tool pays only for the skills it loads. Then add a short summary **in Arabic**: the always-loaded total for each tool, the 3 heaviest descriptions, and that per-skill cost depends on description length, not skill size. Also mention that skills built into the tool itself (such as Claude Code's bundled skills like code-review, simplify or claude-api) have no files on disk and are not included, so the real total is somewhat higher.
4. If the table is long, save it to a Markdown file and point to it instead of pasting it all.
