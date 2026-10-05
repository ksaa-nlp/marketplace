# ابدأ من هنا — حزمة تحويل موقع قائم إلى كود المنصات الموحد

هذه الحزمة مخصصة لمشاركة جميع ملفات العمل اللازمة مع الفريق لتحويل واجهة موجودة تدريجيًا إلى كود المنصات الموحد، دون إعادة بناء المشروع أو تغيير منطق الأعمال بلا ضرورة.

## ما الذي يجب نسخه إلى المشروع؟

انسخ العناصر التالية إلى **جذر المشروع القائم** مع المحافظة على أسمائها ومساراتها:

```text
AGENTS.md
UDS_EXISTING_PROJECT_MIGRATION_INSTRUCTIONS_AR.md
UDS_FILES_USAGE_GUIDE_AR.md
.design-system/
tools/uds-compliance/
```

العناصر التالية مرجعية واختيارية ولا يلزم نسخها إلى المنتج النهائي:

```text
uds-validation-demo/
official-resources/
```

- `uds-validation-demo/`: مثال عملي يمكن تشغيله ومقارنته بالمشروع.
- `official-resources/`: أدلة وأصول المصدر العام التي استند إليها التدقيق.

## ترتيب الاستخدام

1. افتح المشروع من جذره في Codex.
2. تأكد أن `AGENTS.md` و`.design-system/` موجودان في الجذر.
3. افتح `UDS_EXISTING_PROJECT_MIGRATION_INSTRUCTIONS_AR.md`.
4. انسخ الطلب الموجود تحت «الطلب الجاهز للاستخدام مع Codex» إلى مهمة جديدة.
5. اجعل المرحلة الأولى فحصًا وجردًا قبل تعديل الواجهة.
6. راجع `UDS_MIGRATION_PLAN.md` الذي سينشئه Codex.
7. نفّذ الترحيل تدريجيًا: tokens ثم الخطوط ثم المكونات المشتركة ثم الصفحات.
8. شغّل اختبارات المشروع ومدقق UDS بعد كل دفعة.
9. أكمل المراجعات اليدوية في `.design-system/UDS_DEFINITION_OF_DONE.md`.

## اختبار سلامة الحزمة بعد النسخ

من جذر المشروع:

```bash
python3 tools/uds-compliance/build_rules.py
python3 tools/uds-compliance/build_catalogs.py
python3 tools/uds-compliance/test_uds_compliance.py
```

النتيجة المرجعية المتوقعة:

```text
169 rules
50 components
19 templates
5 tests passed
```

## فحص المشروع القائم

استبدل `src` بمسار الواجهة الفعلي:

```bash
python3 tools/uds-compliance/uds_compliance.py src \
  --strict \
  --json-out reports/uds-compliance.json \
  --text-out reports/uds-compliance.txt
```

لا تعتبر التحويل مكتملًا مع وجود `FAIL`. راجع كل `WARNING`، وأكمل بنود `MANUAL REVIEW` يدويًا لأنها ليست نجاحًا أو فشلًا تلقائيًا.

## الملفات التي يبدأ بها كل دور

| الدور | ابدأ بهذه الملفات |
|---|---|
| قائد المشروع | `UDS_EXISTING_PROJECT_MIGRATION_INSTRUCTIONS_AR.md` ثم تقرير التغطية |
| المطور | `AGENTS.md` ثم سجلات JSON و`uds-tokens.css` |
| المصمم | الدليل الرئيسي ثم سجلي المكونات والقوالب |
| المدقق | القواعد المدققة وDefinition of Done وتقارير المدقق |
| وكيل الذكاء الاصطناعي | `AGENTS.md` ثم الملفات التي يحيل إليها تلقائيًا |

## تنبيهات

- لا تعدّل `uds-rules.json` منفردًا؛ حدّث مصدر القواعد ثم شغّل `build_rules.py`.
- لا تعدّل `uds-components.json` أو `uds-templates.json` منفردين؛ حدّث `build_catalogs.py` ثم أعد التوليد.
- لا تنسب أي حقل يحمل `NOT PUBLISHED BY OFFICIAL SOURCE` إلى النظام الرسمي.
- لا تنسخ العرض التجريبي بوصفه منتجًا نهائيًا؛ استخدمه كمرجع وفحص فقط.
- النجاح الآلي لا يغني عن لوحة المفاتيح وقارئ الشاشة وRTL والاستجابة والتباين والاختبار البصري.

## مرجع سريع

- تعليمات التحويل: `UDS_EXISTING_PROJECT_MIGRATION_INSTRUCTIONS_AR.md`
- دليل الملفات: `UDS_FILES_USAGE_GUIDE_AR.md`
- تعليمات الوكيل: `AGENTS.md`
- المرجع الشامل: `.design-system/Saudi_Unified_Platform_Code_Master_Guide.md`
- تعريف الإنجاز: `.design-system/UDS_DEFINITION_OF_DONE.md`
- دليل المدقق: `tools/uds-compliance/README.md`

تاريخ إعداد الحزمة: **28 سبتمبر 2026**.
