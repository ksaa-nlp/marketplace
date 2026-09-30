# تعليمات العمل في هذا المستودع

تعليمات لكل عميل برمجي يعمل هنا. ملف `CLAUDE.md` يستورد هذا الملف؛ **عدّل هنا فقط**.

## ما هذا

سوق إضافات Claude Code لفريق ksaa-nlp (اسم السوق: `ksaa-nlp`). كل إضافة مجلد مستقل تحت `plugins/` ومسجّلة في `.claude-plugin/marketplace.json`.

## اللغة

- الأوصاف (`description` في السوق والإضافات والمهارات) والتوثيق ورسائل الـcommit **بالعربية**.
- أسماء الإضافات والمهارات والأوامر والملفات **بالإنجليزية** (kebab-case).

## الأوامر

```bash
claude plugin validate .      # فحص marketplace.json وكل إضافة مسجّلة
```

## الخريطة

- `.claude-plugin/marketplace.json` ← فهرس السوق: الاسم والمالك وقائمة الإضافات.
- `plugins/<name>/.claude-plugin/plugin.json` ← بيان الإضافة.
- `plugins/<name>/{skills,commands,agents,hooks}/`، `.mcp.json` ← مكوّنات الإضافة.
- `README.md` ← دليل التثبيت وجدول الإضافات.

## قواعد ثابتة

- كل إضافة جديدة تُسجَّل في `marketplace.json` وتُضاف إلى جدول `README.md` في الـcommit نفسه.
- ارفع `version` في `plugin.json` عند كل تغيير سلوك حتى تصل التحديثات إلى الفريق.
- لا أسرار في الإضافات؛ خوادم MCP تقرأ مفاتيحها من متغيرات البيئة.

## قبل أن تُنهي

شغّل `claude plugin validate .` وأدرج نتيجته.
