# سوق إضافات ksaa-nlp

سوق إضافات (Plugin Marketplace) لـ Claude Code خاص بفريق ksaa-nlp. يجمع في مكان واحد المهارات والأوامر والعملاء وخوادم MCP التي يحتاجها الفريق في مشاريع حوسبة اللغة العربية، فيثبّتها كل عضو بأمر واحد ويحصل على التحديثات تلقائيًا، بدل نسخها يدويًا بين المستودعات.

## التثبيت

من داخل Claude Code:

```
/plugin marketplace add ksaa-nlp/marketplace
/plugin install <اسم-الإضافة>@ksaa-nlp
```

للتجربة محليًا قبل رفع المستودع:

```
/plugin marketplace add ~/dev/ksaa-nlp/marketplace
```

ولتفعيله لكل من يعمل في مستودع معيّن، أضف إلى `.claude/settings.json` في ذلك المستودع:

```json
{
  "extraKnownMarketplaces": {
    "ksaa-nlp": { "source": { "source": "github", "repo": "ksaa-nlp/marketplace" } }
  }
}
```

## الإضافات

| الإضافة | الوصف | الاستدعاء |
|---|---|---|
| [`dga-design`](plugins/dga-design/) | مطابقة تصميم المشروع لكود المنصات، نظام التصميم الوطني الموحد من هيئة الحكومة الرقمية: تدقيق آلي، ثم خطة، ثم تطبيق، ثم تقرير بأرقام بنود قائمة التحقق الرسمية | `/dga-design:dga-design [audit\|apply] [نطاق]` |
| [`ksaa-ai-dev`](plugins/ksaa-ai-dev/) | حوكمة التطوير واكتشاف السياق والمواصفات والاختبار والأمان، مع أمثلة عربية لغوية وألعاب تعليمية | `/ksaa-ai-dev:ksaa-context` ثم المهارة المناسبة |

## إضافة إضافة جديدة

1. أنشئ مجلدًا في `plugins/<اسم-الإضافة>/` (الاسم بالإنجليزية، kebab-case).
2. ضع فيه `.claude-plugin/plugin.json` بالاسم والوصف (بالعربية) والإصدار.
3. أضف مكوّناتها في مجلداتها المعتادة: `skills/<name>/SKILL.md`، `commands/`، `agents/`، `hooks/hooks.json`، `.mcp.json`.
4. سجّلها في مصفوفة `plugins` في [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json):

   ```json
   { "name": "<اسم-الإضافة>", "source": "./plugins/<اسم-الإضافة>", "description": "وصف عربي موجز" }
   ```

5. حدّث جدول الإضافات أعلاه، وشغّل `claude plugin validate .` قبل الالتزام.

## استخدام مهارات حوكمة التطوير

تُثبت إضافة `ksaa-ai-dev` مستقلة عن الإضافات السابقة، وتبقى `dga-design` متاحة كما هي:

```text
/plugin install ksaa-ai-dev@ksaa-nlp
/ksaa-ai-dev:ksaa-context افحص المستودع الحالي وحدد المواصفة والأوامر وحدود المهمة
```

راجع [الدليل العربي العملي للإضافة](plugins/ksaa-ai-dev/README.md) لاختيار المهارة، وأمثلة الاستدعاء، وحدود الصلاحيات، وتشغيل الفحوص المحلية.

### توضيح التحديثات

التحديث التلقائي ليس مضمونًا بمجرد إضافة سوق مخصص؛ إعداداته الافتراضية قد تكون معطلة. راجع `/plugin` ثم `Marketplaces` لتفعيل تحديث هذا السوق إذا رغبت. للتحديث اليدوي حدّث فهرس السوق ثم الإضافة:

```text
/plugin marketplace update ksaa-nlp
```

ومن الطرفية:

```bash
claude plugin update ksaa-ai-dev@ksaa-nlp
```

راجع [توثيق تحديث الإضافات الرسمي](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated) للسلوك المدعوم في إصدار Claude Code لديك.
## الحزم المرجعية

- [حزمة ترحيل واجهة موقع قائم](kits/uds-existing-site-migration/): المرفقات الأصلية، ودليل الجرد والترحيل التدريجي، ونتائج التحقق وحدوده. حزمة مساندة لا تُثبّت كإضافة ولا تضيف قواعد تصميم تلقائية. استخدم `dga-design` لتدقيق الواجهة وتطبيق التصميم، وارجع إلى الحزمة عند الحاجة لخطة ترحيل موقع قائم.
