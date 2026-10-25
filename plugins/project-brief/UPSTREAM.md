# مصدر نواة Project Brief وسياسة مزامنتها

## المصدر المستورد

- المستودع: https://github.com/ksaa-nlp/awn-arabia
- الالتزام: `a4d95ccca1a265ea71f3611ec394cd8cdd95f7c9` بتاريخ 2026-10-25، بعنوان «Add portable Project Brief kit and adapt Awn presentation content». كان رأس `main` عند الاستيراد في 2026-10-25، فلا تغييرات أحدث منه.
- ملفات تجربة عون قُرئت للفهم وفحص التوافق فقط، ولم يُنسخ منها شيء: `docs/showcase/project-brief.json` و`docs/showcase/README.md` و`docs/executive-demo.md`.
- الاستيراد على التزامين: الأول ينسخ الملفات حرفيًا، والثاني يضيف تعديلات التوافق أدناه. لرؤية التعديلات وحدها: `git diff <الالتزام الأول> -- plugins/project-brief/skills/project-brief/scripts/brief.py`.

## الملفات

البصمات SHA-256 لنص بنهايات أسطر LF، لأن بعض النسخ المحلية تحوّلها إلى CRLF. احسبها بـ `tr -d '\r' < <الملف> | sha256sum`.

| في المصدر | هنا | بصمة المصدر | البصمة الحالية | الحالة |
|---|---|---|---|---|
| `tools/project-brief/brief.py` | `skills/project-brief/scripts/brief.py` | `fe7dde753b8b83182bbb3a88139beb81a1055b68b1a28bccb9f47a3496151c3c` | `263d9303494b69b2705c5ef179f883ebd8ddd08124bb56bf116f1aa9ce81f220` | معدّل (القسم التالي) |
| `tools/project-brief/test_brief.py` | `tests/test_brief.py` | `d98842528cdcdc4be8f42d52e872f6accfb0398c9eb0b83d765757c4180999a3` | `e5f5e35063d0b4b9c3a21b9b5b4e87022057c2f31bef08b598709c31cbe29451` | معدّل بأقل قدر، والتأكيدات كما هي |
| `tools/project-brief/example.json` | `skills/project-brief/assets/starter/project-brief.json` | `c9763a2a9fb6c2660797e95d42bd0212b7adf527216626bcc1696dfdae5f2ee7` | نفسها | كما هو |
| `tools/project-brief/example.md` | `skills/project-brief/assets/starter/brief.md` | `c2d810dc7a6812fccf42451d994f92418ec1146adb01a2a50e4fa82a0a027b40` | نفسها | كما هو |
| `tools/project-brief/README.md` | `skills/project-brief/references/contract.md` و`contract.en.md` | `99c3415cfd4029a486acc49ce416ac7c9f4875a18e0d2c36080515c20d1c11db` | — | قُسم على ملفين بلغة واحدة لكل منهما، وحُذفت منه إشارات عون، وأُضيف ما يلي |

جديد هنا بلا مقابل في المصدر: `SKILL.md` و`references/authoring.md` و`assets/starter/brief.ar.md` و`tests/test_integration.py` و`tests/test_package.py`.

## تعديلات التوافق في الإصدار 0.1.0

في `brief.py`:

1. **Python 3.8.** كان `local()` يستعمل `Path.is_relative_to` (من 3.9)، ففشلت الاختبارات الـ15 كلها على 3.8.10 بخطأ `AttributeError`. حلّت محله دالة `inside()` تستعمل `relative_to` بالفحص نفسه.
2. **جذر غير محلول.** كان `local()` يقارن مسارًا محلولًا بجذر غير محلول، ففشلت الاختبارات الـ15 كلها على Windows لأن مجلد temp يُعطى باسم 8.3 المختصر (`MALABD~1`). ويُتوقع الفشل نفسه على macOS حيث `/var` رابط إلى `/private/var`، ولم يُختبر ذلك هنا. أداة سطر الأوامر كانت تحل الجذر بنفسها، فلم يظهر الخلل إلا لمن يستدعي الدوال مباشرة. صار الطرفان محلولين، وبقي رفض الخروج من الجذر والروابط الرمزية كما هو، ومختبَرًا على Linux.
3. **مخرج UTF-8.** على Windows بترميز النظام `cp1256` فشل تصدير عربي موجَّه إلى ملف (`'charmap' codec can't encode`، الرمز 2). صار المخرج المعتاد ومخرج الأخطاء UTF-8 على كل الأنظمة.
4. **نهايات أسطر ملف الإعداد.** كان `review` يكتب بالوضع النصي للنظام، فيحوّل ملف LF إلى CRLF على Windows ويغيّر كل أسطره. صار يحافظ على نهايات الملف القائمة.
5. **ملف إعداد ليس كائن JSON.** كان يرمي `AttributeError` غير ملتقط فيخرج بالرمز 1، وهو رمز «يحتاج مراجعة» في `check`. صار خطأ مدخلات واضحًا بالرمز 2.
6. **`export` بلا `--recipe`.** كانت رسالته `can only concatenate str`. صارت «Export requires --recipe».
7. **أمر `init` جديد** مع `--content` و`--direction` و`--project`: ينشئ الناقص فقط بإنشاء حصري، ويتحقق من ملف الإعداد القائم ويتركه، ويعتمد ملف المحتوى القائم دون تعديله.
8. سطرا مصدر في رأس الملف.

في `test_brief.py`: يجد `brief.py` بجانبه أولًا ثم في تخطيط الإضافة، ويكتب ملف العربية بـ`encoding='utf-8'` (كان يُكتب بترميز النظام ثم يُقرأ UTF-8)، ويتخطى اختبار الروابط الرمزية حين يمنعها النظام (Windows دون وضع المطوّر).

## التوافق مع عقد الإصدار 1

لا تغيير في صيغة ملف الإعداد ولا في الأوامر والخيارات القائمة، فلا يلزم ترحيل لأي ملف إعداد. الإضافات كلها اختيارية.

فُحص ملف عون التجريبي كما هو عند `a4d95cc` بالأداة المعدّلة. على Python 3.12.3 جاء ناتج `check` مطابقًا لناتج الأداة الأصلية حرفيًا (28 نسخة لغوية، لا شيء يحتاج مراجعة، الرمز 0). وجاءت التصديرات العشرون (5 وصفات × لغتان × صيغتان) مطابقة لها، باستثناء ساعة الإنشاء. وعلى Python 3.8.10 نجح `check` بالنتيجة نفسها، ولم تمكن المقارنة لأن الأداة الأصلية لا تعمل على 3.8.

## الترخيص (غير محسوم)

- مستودع awn-arabia عند `a4d95cc` بلا ملف `LICENSE` في جذره، وبلا حقل `license` في `package.json`، وبلا نص ترخيص لـ`tools/project-brief`. ملفات الترخيص الموجودة فيه تخص أصولًا من أطراف أخرى فقط: خطوط Noto في `runtime/fonts` و`scripts/art/fonts`، وأيقونات LobeHub (MIT) في `scripts/art/providers`، وأيقونات Lucide (ISC/MIT) في `assets/vendor`.
- لذلك لا يحمل `plugin.json` حقل `license`، ولا ينطبق عليه ترخيص MIT المذكور في إضافات السوق الأخرى.
- المطلوب: أن يقرر مالكو awn-arabia في ksaa-nlp ترخيصًا. بعده يُضاف `LICENSE` إلى الإضافة، وحقل `license` إلى `plugin.json`، ويُحدَّث `tests/test_package.py`.

## الملكية وسياسة التحديث

- **النسخة المرجعية للنواة العامة هنا**، في `plugins/project-brief`: `brief.py` واختباراته وملفات البدء ووثيقة الصيغة.
- **عون يملك محتواه فقط**: `docs/showcase/project-brief.json` و`docs/executive-demo.md` و`docs/showcase/README.md`. لا يدخل محتوى عون في النواة ولا في ملفات البدء.
- كل تعديل على النواة يبدأ هنا: عدّل، وأضف اختبارًا، وحدّث جدول الملفات أعلاه بالبصمة الجديدة، وارفع `version` في `plugin.json` و`marketplace.json`. يفشل `tests/test_package.py` إن تغيّر `brief.py` دون تحديث هذا الملف، فلا يحدث تفرّع صامت.
- التغيير الذي يكسر عقد الإصدار 1 يحتاج `version: 2` في الصيغة، مع بقاء قراءة الإصدار 1 أو أداة ترحيل، وتعليمات ترحيل هنا.
- النسخ في المشاريع الأخرى، ومنها عون، لقطات من إصدار منشور هنا. تُحدَّث بنسخ الملفات كما هي، لا بتعديلها في مكانها، وتُطابَق بالبصمة.

## ترحيل عون (خطوات لاحقة، لم تُنفَّذ في هذه المهمة)

تُنفَّذ في طلب دمج مستقل في awn-arabia:

1. انسخ `skills/project-brief/scripts/brief.py` من الإصدار 0.1.0 هنا فوق `tools/project-brief/brief.py`، و`tests/test_brief.py` فوق `tools/project-brief/test_brief.py`، كما هما. يجد ملف الاختبار `brief.py` بجانبه.
2. تحقق من البصمتين: `tr -d '\r' < tools/project-brief/brief.py | sha256sum` يساوي `263d9303…f220` في الجدول أعلاه، والأمر نفسه للاختبار يساوي `e5f5e350…9451`.
3. أبقِ `example.json` و`example.md` كما هما؛ محتواهما مطابق لملفات البدء هنا.
4. حدّث `tools/project-brief/README.md`: «Python 3.10+» إلى «Python 3.8+» (السطران 22 و92)، ووثّق `init` وخياراته، وأضف سطر مصدر يذكر `ksaa-nlp/marketplace` والإصدار والبصمة. وحدّث ذكر 3.10 في `docs/progress.md` (السطران 20 و188). أما `build.py` فيخص موقع عون وليس من النواة.
5. لا تغيّر `docs/showcase/` ولا `docs/executive-demo.md`؛ التوافق مختبَر أعلاه.
6. شغّل في عون: `python -m unittest discover -s tools/project-brief -p 'test_*.py' -v`، ثم `python tools/project-brief/brief.py check --config docs/showcase/project-brief.json` ويُتوقع الرمز 0 إن لم يتغير المحتوى.
7. اختياري: من يستعمل Claude Code في عون يثبّت الإضافة ويستدعي `/project-brief:project-brief check --config docs/showcase/project-brief.json`. تقرأ المهارة ملف الإعداد نفسه، فلا يلزم شيء تحت `.claude/`.
