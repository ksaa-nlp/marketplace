# المكونات والقوالب — كود المنصات

المصدر: https://design.dga.gov.sa/guidelines/components/ ، والحزمة `@platformscode/core@0.0.52` (مكونات ويب مبنية بـ Stencil) وغلافها `platformscode-new-react@0.1.45`.

**القاعدة الحاكمة (قائمة التحقق 12–36):** المكوّن الرسمي يُستعمل **كما هو** في الشكل والحواف واللون والمسافات، وحالاته كاملة. إن توفرت الحزمة في المشروع فاستعمل المكوّن نفسه ولا تعِد بناءه. وإن تعذّر ذلك (موقع ثابت أو قالب خادم بلا JavaScript) فأعد إنتاج مظهره وحالاته من الرموز، بالمواصفات أدناه.

## الفهرس

1. خريطة العناصر العامة إلى مكونات DGA
2. مواصفات موثقة من الحزمة (للبناء اليدوي)
3. هيكل الواجهة: الرأس والتذييل
4. القوالب
5. الحصول على الخصائص الدقيقة لمكوّن

---

## 1. خريطة العناصر العامة إلى مكونات DGA

| العنصر في المشروع | React (`platformscode-new-react`) | وسم الويب (`@platformscode/core`) | صفحة الإرشاد |
|---|---|---|---|
| زر | `DgaButton` | `dga-button` | components/actions/buttons |
| زر عائم | — (لا غلاف React) | `floating-button` (وسم بلا بادئة dga في الإصدار 0.0.52) | components/actions/floating-Button |
| قائمة منسدلة / select | `DgaDropdown` | `dga-dropdown` | components/actions/dropdown |
| رابط | `DgaLink` | `dga-link` | components/actions/link |
| شريحة تفاعلية (chip) | `DgaChip` | `dga-chip` | components/actions/chip |
| حقل نص | `DgaTextInput` | `dga-text-input` | components/forms-and-inputs/input |
| منطقة نص | `DgaTextarea` | `dga-textarea` | components/forms-and-inputs/textarea |
| رقم | `DgaNumberInput` | `dga-number-input` | components/forms-and-inputs/number-input |
| مربع اختيار | `DgaCheckbox` | `dga-checkbox` | components/forms-and-inputs/checkbox |
| زر اختيار | `DgaRadioButton` | `dga-radio-button` | components/forms-and-inputs/radio |
| مفتاح تبديل | `DgaSwitch` | `dga-switch` | components/forms-and-inputs/switch |
| منتقي تاريخ | `DgaDatepicker` / `DgaDateField` | `dga-datepicker` / `dga-date-field` | components/forms-and-inputs/DatePicker |
| منزلق | `DgaSlider` | `dga-slider` | components/forms-and-inputs/slider |
| رفع ملفات | `DgaFileUpload` | `dga-file-upload` | components/forms-and-inputs/file-uploader |
| خطوات نموذج | `DgaProgressIndicator` | `dga-progress-indicator` | components/forms-and-inputs/Steps |
| تسمية ونص مساعد | `DgaLabel`, `DgaHelperText` | `dga-label`, `dga-helper-text` | — |
| تبويبات | `DgaTabs` | `dga-tabs` | components/navigational/tabs |
| قائمة (menu) | `DgaMenu` | `dga-menu` | components/navigational/menu |
| ترقيم صفحات | `DgaPagination` | `dga-pagination` | components/navigational/pagination |
| مسار التصفح | `DgaBreadcrumbs` | `dga-breadcrumbs` | components/navigational/breadcrumbs |
| قائمة جانبية منزلقة | `DgaSlideoutMenu` | `dga-slideout-menu` | components/navigational/slide-out |
| شريط التنقل العلوي | `DgaNavHeader` (+ `DgaNavHeaderMain` و`Logos` و`Menu` و`Link` و`SubMenu` و`Actions`) أو `DgaHeader` | `dga-nav-header` … / `dga-header` | components/ui-shell/navigation-header |
| شريط تنقل ثانوي | `DgaSecondNavHeader` | `dga-second-nav-header` | components/ui-shell/second-nav-header |
| درج التنقل | `DgaDrawer` | `dga-drawer` | components/ui-shell/navigation-drawer |
| جدول المحتويات | `DgaTableOfContent` | `dga-table-of-content` | components/ui-shell/table-of-content |
| التذييل | `DgaFooter` | `dga-footer` | components/ui-shell/footer |
| بطاقة | `DgaCard` (+ `DgaCardTitle` و`Content` و`Image` و`Actions`) | `dga-card` | components/content-display/card |
| أكورديون | `DgaAccordion` | `dga-accordion` | components/content-display/accordion |
| قائمة تعداد | `DgaList` / `DgaListV2` | `dga-list` | components/content-display/list |
| اقتباس | `DgaQuote` | `dga-quote` | components/content-display/quote |
| فاصل | `DgaDivider` | `dga-divider` | components/content-display/divider |
| مقتطف كود | `DgaCodesnippet` | `dga-codesnippet` | components/content-display/code-snippet |
| جدول | `DgaDataTable` / `DgaTable` | `dga-data-table` / `dga-table` | components/data-display/table |
| مبدّل المحتوى | `DgaContentSwitcher` | `dga-content-switcher` | components/data-display/content-switcher |
| صورة رمزية | `DgaAvatar`, `DgaAvatarGroup` | `dga-avatar` | components/data-display/avatar |
| مؤشر رقمي | `DgaMetric` | `dga-metric` | — |
| رسم بياني | `DgaChart` / `DgaApexChart` | `dga-chart` | — |
| علامة (tag) | `DgaTag`, `DgaStatusTag` | `dga-tag`, `dga-status-tag` | components/search-and-filters/tags |
| مربع بحث | `DgaSearchBox` | `dga-search-box` | — |
| تصفية | `DgaFilteration` | `dga-filteration` | — |
| إشعار أعلى الصفحة | `DgaNotification` | `dga-notification` | components/feedback/notification |
| إشعار منبثق مؤقت | `DgaNotificationToast` | `dga-notification-toast` | components/feedback/notification |
| تنبيه مدمج دائم | `DgaInlineAlert` | `dga-inline-alert` | components/feedback/notification |
| نافذة منبثقة | `DgaModal` | `dga-modal` | components/feedback/modal |
| تلميح | `DgaTooltip` | `dga-tooltip` | components/feedback/tooltip |
| تقييم بالنجوم | `DgaRating` | `dga-rating` | components/feedback/rating |
| تحميل | `DgaLoading` | `dga-loading` | components/loading-and-status/loading |
| شريط تقدم | `DgaLinearProgressBar`, `DgaCircularProgressBar` | `dga-linear-progress-bar` | components/loading-and-status/progress-bar |
| خطوات دائرية | `DgaRadialStepper` | `dga-radial-stepper` | components/loading-and-status/radial-stepper |
| هيكل تحميل | `DgaSkeletonComponent` وأشكاله | `dga-skeleton-component` | components/loading-and-status/skeleton |
| أيقونة | `DgaIcon` | `dga-icon` | foundations/iconography |
| أيقونة مميزة (أكبر من 24px) | `DgaFeaturedIcon` | `dga-featured-icon` | foundations/iconography |
| شبكة | `DgaGridContainer`, `DgaGridItem` | `dga-grid-container` | foundations/layout-and-spacing |
| توقيع رقمي | `DgaDigitalSignature` | `dga-digital-signature` | — |

بعض المكونات لها نسختان (`DgaButton`/`DgaButtonV2`، `DgaCard`/`DgaCardV2`، `DgaModal`/`DgaModalV2` …). لا تخمّن: اتبع مثال الكود في صفحة إرشاد المكوّن أو Storybook، وإن لم يتضح فاسأل.

---

## 2. مواصفات موثقة من الحزمة (للبناء اليدوي)

استعملها حين تعيد إنتاج مكوّن من الرموز. القيم مأخوذة من `core.css` في الحزمة.

### الزر

- الأحجام: **lg: ارتفاع 40px** وحشوة أفقية 16px (خط `text-md-medium`) · **md: ‏32px** و12px (`text-sm-medium`) · **sm: ‏24px** و8px (`text-xs-medium`). المسافة بين الأيقونة والنص 4px.
- الحواف `--radius-sm` (4px). التركيز: `outline: 2px solid var(--border-black)` في `:focus-visible`.
- الأنماط (`variant`): `primary-brand` (أخضر) · `primary-neutral` (أسود) · `secondary` · `secondary-outline` · `subtle` · `transparent`، وللأفعال الخطرة `des-primary` و`des-secondary` و`des-secondary-outline` و`des-subtle` و`des-transparent`. ولكل منها نسخة `--on-color` للخلفيات الملونة.
- ألوان الحالات بالرموز: `--button-background-primary-{default,hovered,pressed,selected,focused}` = sa-flag ‏600 / 700 / 900 / 800 / 600، ونظيرها للمحايد والخطر والأسود.
- الأيقونة سابقة أو لاحقة. السابقة تلفت الانتباه إلى الفعل، واللاحقة مكمّلة للنص. أي نمط يصلح زرَّ أيقونة فقط (`iconOnly`).
- مثال React موثق من أنواع الحزمة: `<DgaButton variant="primary-brand" size="lg" label="إرسال" type="submit" />`

### حقل الإدخال

- ارتفاع 40px، وحشوة أفقية 8px، وحواف 4px، وحد 1px بلون `--form-field-border-default`، وخلفية `--form-field-background-default`.
- عند الضغط أو التركيز يظهر خط سفلي بسماكة 2px بلون `--form-field-border-pressed`، يتمدد من المنتصف (transition ‏0.2s).
- الأنماط: `default` و`lighter` و`darker`. والحالات: error وreadonly وdisabled، مع أيقونة تغذية راجعة (success أو error أو warning) ونص مساعد.
- مثال: `<DgaTextInput label="البريد الإلكتروني" name="email" required helperText="…" />`

### البطاقة

- الحواف 16px (`--components-card-radius`). المؤثر (`effect`): `with-shadow` أو `no-shadow` أو `stroke`. النوع: `default` أو `expanded` أو `selectable`.
- الحشوة والفاصل متجاوبان: `--card-md-padding` ‏32 / 24 / 16px، و`--card-md-gap` ‏24 / 20 / 12px.
- لا يُعدَّل فيها إلا المحاذاة الداخلية والمسافات الداخلية. والبطاقة القابلة للنقر فيها زر إجراء.

### الرابط

- المتغيرات: `primary` و`neutral` و`on-color`. الأحجام: `sm` و`md` و`lg`. خاصية `external` تضيف أيقونة الرابط الخارجي، وهي إلزامية للروابط الخارجية.

### الإشعارات

- `DgaNotification` (أعلى الصفحة، دائم عالي الأولوية): `variant` = `critical` أو `warning` أو `success` أو `info` أو `neutral`، و`dismissable`.
- `DgaInlineAlert` (مدمج دائم): `type` = `neutral` أو `info` أو `error` أو `success` أو `warning`.
- `DgaNotificationToast` للمؤقت.

---

## 3. هيكل الواجهة: الرأس والتذييل

- **الرأس (Navigation header):** شعار الجهة، وروابط رئيسة بقوائم فرعية، وإجراءات (بحث، ولغة، ودخول). متجاوب يتحول إلى قائمة جوال. الحالات: Default وHovered وPressed وFocused وDisabled، والسياقية Selected. والروابط الخارجية بأيقونة External link.
- **التذييل (Footer):** إلزامي أن يحوي الروابط الرسمية، وشعارات الجهة، ومعلومات التواصل، وسياسة الخصوصية. والروابط في مجموعات معنونة (مثل «روابط مهمة» و«الدعم والمساعدة»). يدعم `DgaFooter` خلفية `DarkGreen` أو `Light`، وروابط وسائل التواصل، وروابط إمكانية الوصول.
- ⚠️ **لا تضع** شعار هيئة الحكومة الرقمية، ولا شعار الدولة، ولا شعارات منصات حكومية، ولا رقم شهادة الختم الرقمي، ما لم يزوّدك بها صاحب المشروع. ضع مكانها عنصرًا نائبًا ظاهرًا واذكره في التقرير.

---

## 4. القوالب

القوالب تصاميم صفحات كاملة (ملفات Figma في مجتمع Figma لحساب DGA: https://www.figma.com/@sdga). طبّقها حين تطابق الصفحة غرضها:

| القالب | الصفحة |
|---|---|
| الصفحة الرئيسية | templates/home-page |
| صفحة الخدمة | templates/service-page |
| النموذج | templates/form-page |
| تواصل معنا | templates/contact-us-page |
| مركز المساعدة | templates/help-page |
| الأسئلة الشائعة | templates/faqs-page |
| خريطة الموقع | templates/sitemap-page |
| الصفحة غير موجودة (404) | templates/page-not-found |
| شريط ملفات الارتباط (Cookies) | templates/cookies-banner |
| البحث | templates/search-page |
| عن الجهة | templates/about-page |
| المشاركة الإلكترونية | templates/e-participation-page |
| صفحة محتوى | templates/content-page |
| روبوت المحادثة | templates/chatbot |
| قسم التقييم | templates/rating-section |
| قسم التغذية الراجعة | templates/feedback-section |

كل المسارات تحت https://design.dga.gov.sa/guidelines/ . القوالب ملفات Figma لا كود. فإن احتجت تفاصيل تخطيط قالب فاطلب من المستخدم لقطة أو رابط الإطار، ولا تتخيل محتواه.

---

## 5. الحصول على الخصائص الدقيقة لمكوّن

الحزمة في الإصدار 0.x وواجهتها تتغير بين الإصدارات. قبل استعمال مكوّن اقرأ تعريفه من المصدر المثبت:

- `node_modules/@platformscode/core/dist/types/components.d.ts` (الواجهة `Components.<Name>` والأحداث).
- `node_modules/platformscode-new-react/dist/types/components/stencil-generated/components.d.ts`
- صفحة الإرشاد (تبويب «الكود») وStorybook المشار إليه منها.
