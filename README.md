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

لا توجد إضافات بعد.

| الإضافة | الوصف |
|---|---|
| — | — |

## إضافة إضافة جديدة

1. أنشئ مجلدًا في `plugins/<اسم-الإضافة>/` (الاسم بالإنجليزية، kebab-case).
2. ضع فيه `.claude-plugin/plugin.json` بالاسم والوصف (بالعربية) والإصدار.
3. أضف مكوّناتها في مجلداتها المعتادة: `skills/<name>/SKILL.md`، `commands/`، `agents/`، `hooks/hooks.json`، `.mcp.json`.
4. سجّلها في مصفوفة `plugins` في [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json):

   ```json
   { "name": "<اسم-الإضافة>", "source": "./plugins/<اسم-الإضافة>", "description": "وصف عربي موجز" }
   ```

5. حدّث جدول الإضافات أعلاه، وشغّل `claude plugin validate .` قبل الالتزام.
