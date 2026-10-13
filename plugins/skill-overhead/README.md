# skill-overhead

مهارة تفحص المهارات المثبّتة على الجهاز لـ Claude وCodex وAntigravity وتقيس ما تضيفه كل واحدة إلى نافذة السياق، ثم تعرض النتيجة جدولًا بالعربية مرتبًا من الأثقل إلى الأخف.

## الاستعمال

بعد تثبيت الإضافة (`/plugin install skill-overhead@ksaa-nlp`):

```
/skill-overhead:skill-overhead                    ← يفحص المجلدات الافتراضية
/skill-overhead:skill-overhead ~/dev/my-skills    ← ويضيف مجلدات أخرى
/skill-overhead:skill-overhead --tools codex      ← أداة واحدة فقط
```

ويستدعيها Claude تلقائيًا إذا سألت كم تأخذ مهاراتك من السياق أو أيّها أثقل.

## ما تقيسه

- **محمّل دائمًا**: اسم المهارة ووصفها. يبقى في موجّه النظام في كل دور، فهو العبء الحقيقي الثابت.
- **عند الاستدعاء**: متن `SKILL.md`. لا يُحمَّل إلا عند استعمال المهارة، ثم يبقى في المحادثة حتى `/clear` أو جلسة جديدة أو الضغط.
- **الملفات المرفقة**: السكربتات والمراجع في مجلد المهارة. لا تكلّف شيئًا حتى يفتحها Claude.

## المجلدات المفحوصة

| الأداة | مجلدات المستخدم | مجلدات المشروع |
|---|---|---|
| Claude | `~/.claude/skills`، والإضافات المثبّتة فقط | `.claude/skills` |
| Codex | `~/.codex/skills`، `~/.agents/skills` | `.agents/skills`، `.codex/skills` |
| Antigravity | `~/.gemini/antigravity/skills`، `~/.gemini/antigravity-cli/skills`، `~/.gemini/config/skills`، `~/.gemini/config/plugins` | `.agent/skills`، `.agents/skills` |

إضافات Claude تُقرأ من `~/.claude/plugins/installed_plugins.json`: لا تُعدّ الإضافات الموجودة في نسخ الأسواق دون تثبيت، ولا المعطّلة في `enabledPlugins`، ولا المثبّتة لمشروع آخر.

المجلد المشترك بين أداتين (مثل `.agents/skills`) يظهر مرة واحدة باسم الأداتين، ولكل أداة سطر إجمالي خاص بها لأن كل أداة لا تحمّل إلا مهاراتها.

إن وُجد `ANTHROPIC_API_KEY` فالعدّ عبر واجهة عدّ الرموز: دقيق لـ Claude وتقريبي لـ Codex وAntigravity لاختلاف المُرمِّز، وإلا فتقدير (عدد الأحرف ÷ 3.5، بهامش ±15% تقريبًا). المهارات المدمجة والمستضافة على claude.ai بلا ملفات محلية لا تدخل في الجدول.

## التثبيت في Codex وAntigravity

المهارة نفسها تعمل في الأداتين: انسخ مجلد `skills/skill-overhead/` إلى `~/.codex/skills/` (Codex) أو `~/.gemini/antigravity/skills/` (Antigravity).

## الملفات

- `skills/skill-overhead/SKILL.md` ← سير العمل.
- `skills/skill-overhead/scripts/scan.py` ← سكربت الفحص والعدّ (مكتبة Python القياسية فقط).
