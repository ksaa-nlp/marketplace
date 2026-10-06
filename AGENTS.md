# تعليمات العمل في هذا المستودع

تعليمات لكل عميل برمجي يعمل هنا. ملف `CLAUDE.md` يستورد هذا الملف؛ **عدّل هنا فقط**.

## ما هذا

سوق إضافات Claude Code لفريق ksaa-nlp (اسم السوق: `ksaa-nlp`). كل إضافة مجلد مستقل تحت `plugins/` ومسجّلة في `.claude-plugin/marketplace.json`.

## اللغة

- الأوصاف (`description` في السوق والإضافات والمهارات) والتوثيق ورسائل الـcommit **بالعربية**.
- أسماء الإضافات والمهارات والأوامر والملفات **بالإنجليزية** (kebab-case).

## الأوامر

```bash
claude plugin validate .                                          # فحص marketplace.json وكل إضافة مسجّلة
python3 -m unittest discover -s plugins/dga-design/tests          # اختبارات سكربتات dga-design، بلا شبكة
python3 plugins/dga-design/scripts/sync_tokens.py [version]       # إعادة توليد رموز DGA من @platformscode/core (يحتاج npm وشبكة)
```

السكربتات بمكتبة Python القياسية فقط، وتعمل على 3.8+.

## الخريطة

- `.claude-plugin/marketplace.json` ← فهرس السوق: الاسم والمالك وقائمة الإضافات. مسار كل إضافة صريح (`./plugins/<name>`)، بلا `pluginRoot`.
- `plugins/<name>/.claude-plugin/plugin.json` ← بيان الإضافة.
- `plugins/<name>/{skills,commands,agents,hooks}/`، `.mcp.json` ← مكوّنات الإضافة.
- `README.md` ← دليل التثبيت وجدول الإضافات.

### `plugins/dga-design` (مطابقة كود المنصات من DGA)

- `skills/dga-design/SKILL.md` ← سير العمل: فهم، ثم تدقيق، ثم خطة، ثم تطبيق، ثم تحقق، ثم تقرير. يُستدعى `/dga-design:dga-design`.
- `skills/dga-design/references/` ← `foundations.md` (الرموز والأساسات) · `components.md` (المكونات والقوالب) · `checklist.md` (البنود الـ56 الرسمية) · `implementation.md` (المسار حسب المكدس).
- `skills/dga-design/assets/dga-tokens.css` ← **مولَّد** من `@platformscode/core` (MIT). لا يُعدَّل يدويًا؛ أعد توليده بـ `sync_tokens.py`.
- `skills/dga-design/scripts/audit.py` ← التدقيق الآلي للقيم الثابتة.
- `scripts/sync_tokens.py` ← أداة صيانة لتوليد ملف الرموز (خارج المهارة؛ لا يحتاجها المستخدم).
- `tests/` ← اختبارات السكربتين.
- مرجعية المحتوى: موقع design.dga.gov.sa وقائمة التحقق الرسمية والحزمة. إن تعارض نص الموقع مع الحزمة فالحزمة هي المرجع، والتعارضات موثقة في آخر `foundations.md`.

### `plugins/feature-test-report` (سيناريوهات الاختبار وتقريرها)

- `skills/feature-test-report/SKILL.md` ← سير العمل: تعرّف على المشروع، ثم متطلبات، ثم سيناريوهات، ثم مطابقة الكود، ثم أدلة، ثم تشغيل، ثم تقرير. يُستدعى `/feature-test-report:feature-test-report`.
- `skills/feature-test-report/report-template.md` ← قالب التقرير.
- `skills/feature-test-report/project-config-example.md` ← قالب الإعدادات الاختيارية التي يضعها كل مشروع في `.claude/feature-test-report.md`.
- المهارة عامة لكل المشاريع: لا تكتب فيها مسارًا أو أمرًا أو اسم إطار خاصًّا بمشروع بعينه؛ مكان ذلك ملف إعدادات المشروع.

## قواعد ثابتة

- كل إضافة جديدة تُسجَّل في `marketplace.json` وتُضاف إلى جدول `README.md` في الـcommit نفسه.
- ارفع `version` في `plugin.json` عند كل تغيير سلوك حتى تصل التحديثات إلى الفريق.
- لا أسرار في الإضافات؛ خوادم MCP تقرأ مفاتيحها من متغيرات البيئة.

## قبل أن تُنهي

شغّل `claude plugin validate .` واختبارات الإضافات المعدَّلة، وأدرج نتيجتها.
