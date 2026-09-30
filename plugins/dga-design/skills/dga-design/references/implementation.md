# التطبيق حسب نوع المشروع

المصدر: صفحة التطوير https://design.dga.gov.sa/developing (الحزمة الرسمية المعلنة فيها لـ React: `platformscode-new-react`)، والحزمة الأساسية `@platformscode/core`.

**قبل أي تثبيت:** إضافة اعتمادية أو إطار قرار معماري. إن كان المشروع يوثّق مكدسه في `AGENTS.md` أو المواصفة، أو كانت الإضافة تغيّر طريقة البناء، فاعرض الخيار واسأل قبل التنفيذ.

## الفهرس

1. اختيار المسار
2. React / Next.js
3. Angular / Vue / Svelte / JavaScript بمجمِّع
4. HTML ثابت وقوالب الخادم (بلا مجمِّع)
5. الرموز فقط (بلا مكونات)
6. Tailwind
7. تنبيهات مشتركة

---

## 1. اختيار المسار

| المشروع | المسار | السبب |
|---|---|---|
| React أو Next.js | القسم 2 (`platformscode-new-react`) | الحزمة الرسمية المعلنة |
| Angular أو Vue أو Svelte أو Vite بلا إطار | القسم 3 (مكونات الويب من `@platformscode/core`) | مكونات Stencil تعمل في أي إطار |
| HTML ثابت، Jinja/Django/Flask، مولّد مواقع | القسم 4، أو القسم 5 إن كان المشروع بلا JavaScript أصلًا | لا مجمِّع |
| تقرير أو صفحة مولَّدة من سكربت (مثل Python يكتب HTML) | القسم 5 | لا حاجة لمكونات تفاعلية |

غلاف Angular المنشور على npm باسم `platformscode-new-angular` مستودعٌ شخصي، وثابت على `@platformscode/core@0.0.17`، ولا يذكره موقع DGA. لا تعتمد عليه، واستعمل مكونات الويب مباشرة (القسم 3).

---

## 2. React / Next.js

```bash
npm install platformscode-new-react@latest
```

```tsx
import { DgaButton, DgaTextInput } from 'platformscode-new-react';
// ملف الحزمة الرئيس يستورد '@platformscode/core/dist/core/core.css' تلقائيًا.

<DgaTextInput label="الاسم الكامل" name="fullName" required />
<DgaButton variant="primary-brand" size="lg" label="إرسال" type="submit" />
```

- اضبط `<html lang="ar" dir="rtl">` في الجذر (`app/layout.tsx` في Next.js).
- المكونات مكونات ويب مغلَّفة. في Next.js (App Router) إن ظهر خطأ تصيير على الخادم فضعها داخل مكوّن عميل (`'use client'`). جرّب البناء والتشغيل قبل أن تحكم.

---

## 3. Angular / Vue / Svelte / JavaScript بمجمِّع

```bash
npm install @platformscode/core
```

في ملف الدخول (`main.ts`):

```ts
import '@platformscode/core/dist/core/core.css';
import { defineCustomElements } from '@platformscode/core/loader';

defineCustomElements();
```

- **Angular:** أضف `CUSTOM_ELEMENTS_SCHEMA` إلى `schemas` في المكوّن المستقل أو الوحدة التي تستعمل وسوم `dga-*`.
- **Vue 3 (Vite):** في `vite.config` داخل إعداد `vue()`:
  `template: { compilerOptions: { isCustomElement: (tag) => tag.startsWith('dga-') } }`
- **الخصائص:** البسيطة تُمرَّر سماتٍ بصيغة kebab-case (`<dga-button variant="primary-brand" size="lg" label="إرسال">`). والمعقدة (كائنات ومصفوفات، مثل `config` في `dga-header`) تُسنَد خاصيةً في JavaScript (`el.config = {...}`) أو بربط الخاصية في الإطار (`[config]="..."` في Angular، و`.config` أو `:config` في Vue).
- **الأحداث:** اقرأ أسماءها من `components.d.ts` (انظر components.md، القسم 5).

---

## 4. HTML ثابت وقوالب الخادم (بلا مجمِّع)

1. ثبّت الحزمة للحصول على ملفاتها (`npm install @platformscode/core`)، ثم انسخ المجلد `node_modules/@platformscode/core/dist/core/` إلى مجلد الملفات الثابتة (مثل `static/dga/`). فيه `core.esm.js` و`core.css` والخطوط في `assets/fonts/`.
2. في القالب الأساسي:

```html
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="/static/dga/core.css">
  <script type="module" src="/static/dga/core.esm.js"></script>
</head>
<body>
  <dga-button variant="primary-brand" size="lg" label="إرسال"></dga-button>
</body>
</html>
```

3. هذه طريقة Stencil القياسية لمخرَج `dist` (أداة البناء المستعملة في الحزمة). تحقق بالتشغيل الفعلي أن المكونات تُسجَّل وتظهر.
4. لا تحمّل الحزمة من شبكة توزيع خارجية (CDN) في الإنتاج دون موافقة صاحب المشروع. الاستضافة الذاتية أولى.

---

## 5. الرموز فقط (بلا مكونات)

للمواقع التي لا تريد JavaScript أو مكونات ويب:

1. انسخ `assets/dga-tokens.css` من هذه المهارة إلى المشروع (لا تعدّله يدويًا؛ هو مولَّد من الحزمة الرسمية).
2. حمّل الخط استضافةً ذاتية من ملفات الحزمة (`dist/core/assets/fonts/IBM-Plex-Sans-Arabic/*.woff2` بالأوزان 400 و500 و600 و700)، أو من Google Fonts بموافقة صاحب المشروع:
   `https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap`
3. أساس مقترح (يعتمد على رموز الملف وحدها):

```css
html { font-family: "IBM Plex Sans Arabic", "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", "Noto Sans Arabic", sans-serif; }
body { background: var(--background-body); color: var(--text-primary-paragraph); font-size: 16px; line-height: 24px; }
h1, h2, h3 { color: var(--text-display); }
.container { max-width: var(--spacing-320); margin-inline: auto; padding-inline: var(--spacing-4); }
@media (min-width: 960px) { .container { padding-inline: var(--spacing-8); } } /* 960 = بداية Large في جدول نقاط التحول */
p { max-width: var(--maxwidth-paragraph-max-width); }
a { color: var(--link-primary); }
a:hover { color: var(--link-primary-hovered); }
a:active { color: var(--link-primary-pressed); }
a:visited { color: var(--link-primary-visited); }
:focus-visible { outline: 2px solid var(--border-black); outline-offset: 2px; }
```

4. أعد إنتاج المكونات المستعملة (الأزرار والحقول والبطاقات والتنبيهات) بمواصفات components.md القسم 2، مع **كل** حالاتها في قائمة التحقق.
5. قبل استعمال أي رمز غير مذكور هنا تحقق أنه معرَّف في `dga-tokens.css` (مثلًا: `--link-primary-hovered` موجود، و`--link-primary-default` غير موجود)، ولا تفترض اسمًا.

---

## 6. Tailwind

المبدأ: اربط سمة Tailwind برموز DGA، وامنع ما يخرج عنها.

- **الألوان:** استبدل لوحة Tailwind بلوحات DGA (`primary` ← `--colors-primary-sa-flag-*`، `neutral` ← `--colors-neutral-*`، `gold`، `lavender`، `red`، `yellow`، `green`، `blue`)، وأضف الرموز الدلالية (`--background-*` و`--text-*` و`--border-*`).
  - v4: داخل `@theme inline { --color-*: initial; --color-primary-600: var(--colors-primary-sa-flag-600-primary); … }` بعد استيراد `dga-tokens.css`.
  - v3: `theme.colors` (لا `extend`) بقيم `var(--…)`.
- **المسافات:** سلّم DGA الرقمي (`--spacing-N` = ‏N × 4px) يطابق مضاعفات Tailwind الافتراضية (`p-4` = ‏16px). اقتصر على الخطوات الموجودة في DGA: ‏0 و0.5 و1 و1.5 و2 و3 و4 و5 و6 و8 و10 و12 و16 و20 و24 و32 و40. لا `p-7`، ولا `p-[13px]`.
- **الحواف والظلال:** عرّف `rounded-{none,xs,sm,md,lg,xl,full}` بقيم DGA (0 و2 و4 و8 و16 و24 و9999px) و`shadow-{xs..3xl}` بـ `var(--shadow-*)`. قيم Tailwind الافتراضية لـ md وlg والظلال **تختلف** عنها.
- **الخط:** `fontFamily.sans` بسلسلة IBM Plex Sans Arabic، وأحجام الخط من سلّم foundations.md (Display وText).
- **القيم الاعتباطية** (`text-[#…]` و`p-[…px]` و`rounded-[…]`) مخالفة لبند «رموز التصميم دون تعديل». ابحث عنها واستبدلها.

---

## 7. تنبيهات مشتركة

- `core.css` في الحزمة يبدأ **بتصفير عام** (reset): يصفّر الهوامش، ويجعل `body { line-height: 1 }`، ويلغي حدود التركيز العامة `:focus { outline: 0 }`، ويزيل تنسيق القوائم. استيراده في مشروع قائم يغيّر مظهر صفحات لم تُحوَّل بعد. فحوّل الصفحات كلها معًا، أو أعد ضبط الأساس بعده (ارتفاع السطر 1.5 للنص، ومؤشر تركيز ظاهر لكل عنصر تفاعلي).
- كل مكونات الحزمة تعكس اتجاهها حسب `html[dir=rtl]` أو `html[lang=ar]`. اضبطهما في الجذر لا على عنصر داخلي.
- الحزمة في الإصدار 0.x، فثبّت الإصدار في ملف القفل، واقرأ سجل التغييرات https://design.dga.gov.sa/updates/change-log قبل الترقية.
- النمط الداكن: `data-theme="dark"` على `<html>` يبدّل الرموز الدلالية. لا تُضفه إلا إن طُلب.
