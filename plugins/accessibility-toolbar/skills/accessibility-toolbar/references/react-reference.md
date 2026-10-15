# دمج المرجع المختبر: React V5

استخدم هذا المسار فقط عندما يناسب تقنية المشروع. لا تفرضه على مشروع بإطار أو CSS مختلفين. تفاصيل الموقع الحالي واختبار الدمج تبقى ضرورية.

## الاعتماديات

المراجعة المسجلة: React وReactDOM 18.3.1، Tailwind 3.4.17، Lucide React 0.468.0. أدوات الوحدة: Vitest 2.1.8 وjsdom 24.1.3 وTypeScript 5.7.2. لا توجد node_modules داخل ZIP.

## الدمج

1. انسخ assets/AccessibilityToolbar.tsx وassets/accessibility.css إلى مجلدات مشروعك، وثبّت lucide-react إن لم يكن موجودًا.
2. استورد CSS من نقطة الدخول أو التنسيق العام، واعرض <AccessibilityToolbar /> مرة واحدة. حافظ على "use client" في Next.js.
3. أضف مسار المكوّن إلى content في Tailwind، ووفّر الأسماء الدلالية background وforeground وcard وpopover وmuted وmuted-foreground وborder وprimary وprimary-foreground وring. mapping الموقع يجب أن يناسب صيغة توكناته.
4. عند ترقية V3/V4 استبدل المكوّن وكتلة CSS معًا؛ لا تُبقِ فلاتر body/html السابقة إلى جانب V5.
5. portal ينشأ مباشرة تحت body بعد التركيب. لا تنقله داخل حاوية محوّلة أو مفلترة. افحص عناصر fixed في محتوى الموقع عند تطبيق فلاتر عليه.

```tsx
import { AccessibilityToolbar } from './components/AccessibilityToolbar';
import './styles/accessibility.css';

export function App() {
  return <><main>{/* محتوى الموقع */}</main><AccessibilityToolbar /></>;
}
```

توكنات HSL المجزأة مثل --primary: 221 83% 40% تحتاج mapping مثل hsl(var(--primary) / <alpha-value>)؛ اللون الكامل مثل #1d4ed8 يحتاج mapping لون كامل، لا تغليفه مرة أخرى في hsl. قواعد المكوّن المساعدة تدعم الصيغتين، وmapping Tailwind للموقع مسؤولية تهيئته، بما في ذلك فئات الشفافية.

دليل الدمج العام وأمثلة Tailwind في [المستودع](https://github.com/haithamnaddaf/arabic-accessibility-toolbar/blob/main/docs/INSTALLATION.md). [نتائج المرجع وحدودها](validation-v5.html). هذه النتائج لا تثبت نجاح تكييف لإطار آخر.
